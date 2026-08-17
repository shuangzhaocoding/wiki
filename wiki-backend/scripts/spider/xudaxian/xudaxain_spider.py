#!/usr/bin/env python3
"""
语雀知识库爬虫 + Markdown / Quill Delta + 可选入库。

1. 从入口页 window.appData 解析 book.toc（扁平列表，靠 level 表示层级）
2. TITLE 为目录分组，DOC 为文档；section 由上级 TITLE 路径拼接
3. 通过语雀 API 拉取文档 Lake HTML，转 Markdown / Quill Delta
4. 可选写入 MySQL articles 表

  python scripts/spider/xudaxian/xudaxain_spider.py --toc-only
  python scripts/spider/xudaxian/xudaxain_spider.py --limit 3 -o out.json
"""
from __future__ import annotations

import argparse
import asyncio
import importlib
import json
import re
import sys
from dataclasses import dataclass, field
from html import escape as html_escape, unescape
from pathlib import Path
from typing import Any, Optional
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.outer_apis.huawei_obs_api import HuaweiOBSClient  # noqa: E402
from config import settings  # noqa: E402

_XIAOLIN_DIR = Path(__file__).resolve().parent.parent / "xiaolincoding"
if str(_XIAOLIN_DIR) not in sys.path:
    sys.path.insert(0, str(_XIAOLIN_DIR))

from db_import import build_tortoise_config, close_db, import_articles, init_db  # noqa: E402
from markdown_quill import (  # noqa: E402
    html_content_to_quill_delta,
    markdown_to_quill_delta,
    migrate_markdown_images,
    quill_delta_to_json,
)

DEFAULT_BOOK_URL = "https://www.yuque.com/fairy-era/yg511q/"
DEFAULT_IMAGE_OBS_PREFIX = "wiki/import/yuque"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
REFERER = "https://www.yuque.com/"

# 语雀代码块为 <card name="codeblock" value="data:{json}">，非 <pre>
_CODEBLOCK_CARD_RE = re.compile(
    r'<card\s[^>]*\bname="codeblock"[^>]*\bvalue="([^"]+)"[^>]*>\s*</card>',
    re.I | re.S,
)


@dataclass
class TocNode:
    title: str
    url: Optional[str] = None
    children: list["TocNode"] = field(default_factory=list)
    level: int = 0
    node_type: str = ""


def fetch_bytes(url: str, timeout: int = 30) -> bytes:
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Referer": REFERER,
            "Accept": "text/html,application/json,*/*",
        },
    )
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_html(url: str, timeout: int = 30) -> str:
    raw = fetch_bytes(url, timeout=timeout)
    charset = "utf-8"
    return raw.decode(charset, errors="replace")


def fetch_json(url: str, timeout: int = 30) -> Any:
    raw = fetch_bytes(url, timeout=timeout)
    return json.loads(raw.decode("utf-8", errors="replace"))


def parse_yuque_book_url(url: str) -> tuple[str, str, str]:
    """返回 (namespace_login, book_slug, book_base_url)。"""
    p = urlparse(url.strip())
    parts = [x for x in p.path.strip("/").split("/") if x]
    if len(parts) < 2:
        raise ValueError(f"无效的语雀知识库 URL: {url}")
    login, slug = parts[0], parts[1]
    base = f"{p.scheme or 'https'}://{p.netloc or 'www.yuque.com'}/{login}/{slug}"
    return login, slug, base.rstrip("/")


def extract_app_data(page_html: str) -> dict[str, Any]:
    m = re.search(
        r'window\.appData\s*=\s*JSON\.parse\(decodeURIComponent\("([^"]+)"\)\)',
        page_html,
        flags=re.S,
    )
    if not m:
        raise ValueError("页面中未找到 window.appData")
    return json.loads(unquote(m.group(1)))


def load_book_context(book_url: str) -> dict[str, Any]:
    login, slug, base = parse_yuque_book_url(book_url)
    index_url = base if book_url.rstrip("/").count("/") >= 4 else f"{base}/"
    html = fetch_html(index_url)
    app = extract_app_data(html)
    book = app.get("book")
    if not book:
        raise ValueError("appData 中未找到 book")
    toc = book.get("toc")
    if not toc:
        raise ValueError("book.toc 为空")
    return {
        "login": login,
        "slug": slug,
        "book_base": base,
        "book_id": book["id"],
        "book_name": book.get("name") or slug,
        "toc": toc,
    }


def _doc_page_url(book_base: str, doc_slug: str) -> str:
    return f"{book_base}/{doc_slug}"


def _section_from_stack(title_stack: list[str]) -> str:
    parts = [s for s in title_stack if s]
    return " / ".join(parts) if parts else "未分类"


def iter_toc_entries(
    flat_toc: list[dict[str, Any]],
    *,
    book_base: str,
) -> list[dict[str, Any]]:
    """扁平 toc → 抓取项；按 level 维护 TITLE 层级作为 section。"""
    title_stack: list[str] = []
    items: list[dict[str, Any]] = []

    for node in flat_toc:
        typ = (node.get("type") or "").upper()
        title = unescape(re.sub(r"\s+", " ", (node.get("title") or "").strip()))
        level = int(node.get("level") or 0)

        if typ == "TITLE":
            while len(title_stack) > level:
                title_stack.pop()
            while len(title_stack) < level:
                title_stack.append("")
            if len(title_stack) == level:
                title_stack.append(title)
            else:
                title_stack[level] = title
            continue

        if typ != "DOC":
            continue

        doc_slug = (node.get("url") or "").strip()
        doc_id = node.get("doc_id") or node.get("id")
        if not doc_slug or not doc_id:
            continue

        while len(title_stack) > level:
            title_stack.pop()

        items.append(
            {
                "section": _section_from_stack(title_stack),
                "title": title,
                "url": _doc_page_url(book_base, doc_slug),
                "doc_id": int(doc_id),
                "level": level,
            }
        )
    return items


def build_toc_tree(flat_toc: list[dict[str, Any]], *, book_base: str) -> list[TocNode]:
    """按 level 构建目录树（用于 --toc-only 展示）。"""
    roots: list[TocNode] = []
    stack: list[TocNode] = []

    for node in flat_toc:
        typ = (node.get("type") or "").upper()
        title = unescape(re.sub(r"\s+", " ", (node.get("title") or "").strip()))
        level = int(node.get("level") or 0)

        while len(stack) > level:
            stack.pop()

        if typ == "TITLE":
            n = TocNode(title=title, level=level, node_type="TITLE")
            if stack:
                stack[-1].children.append(n)
            else:
                roots.append(n)
            stack.append(n)
        elif typ == "DOC":
            slug = (node.get("url") or "").strip()
            if not slug:
                continue
            n = TocNode(
                title=title,
                url=_doc_page_url(book_base, slug),
                level=level,
                node_type="DOC",
            )
            if stack:
                stack[-1].children.append(n)
            else:
                roots.append(n)

    return roots


def fetch_doc_lake_html(doc_id: int, book_id: int) -> str:
    api = (
        f"https://www.yuque.com/api/docs/{doc_id}"
        f"?book_id={book_id}&merge_dynamic_data=false"
    )
    payload = fetch_json(api)
    content = (payload.get("data") or {}).get("content")
    if not content:
        raise ValueError(f"文档无 content: doc_id={doc_id}")
    return content


def lake_to_html(lake: str) -> str:
    html = re.sub(r"<!doctype lake>.*?(?=<)", "", lake, count=1, flags=re.S | re.I)
    html = re.sub(r"<meta[^>]*>\s*", "", html, flags=re.I)
    return html.strip()


def _codeblock_card_to_pre(match: re.Match[str]) -> str:
    """语雀 codeblock 卡片 → <pre><code class="language-xxx">。"""
    raw = match.group(1)
    payload = unquote(raw[5:]) if raw.startswith("data:") else unquote(raw)
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return ""
    mode = str(data.get("mode") or "plain").strip()
    code = str(data.get("code") or "")
    lang = re.sub(r"[^\w+#.-]", "", mode) or "plain"
    return (
        f'<pre><code class="language-{lang}">'
        f"{html_escape(code)}</code></pre>"
    )


def _expand_codeblock_cards(html: str) -> str:
    return _CODEBLOCK_CARD_RE.sub(_codeblock_card_to_pre, html)


_LAKE_SPACER_TAGS = frozenset({"p", "ne-p", "div"})


def _element_plain_text(el: Any) -> str:
    text = (el.text_content() or "").replace("\u00a0", " ").replace("\u200b", "")
    return re.sub(r"\s+", " ", text).strip()


def _is_empty_lake_paragraph(el: Any) -> bool:
    """语雀占位：<p><br></p>、仅空白 span、ne-p 空段落等。"""
    tag = (el.tag or "").lower()
    if tag not in _LAKE_SPACER_TAGS:
        return False
    if _element_plain_text(el):
        return False
    children = list(el)
    if not children:
        return True
    return all((c.tag or "").lower() in ("br", "span") for c in children)


def _normalize_ne_paragraph_tags(root: Any) -> None:
    """语雀新编辑器 ne-p 等自定义段落标签 → p。"""
    for el in root.iter():
        tag = (el.tag or "").lower()
        if tag in ("ne-p", "ne_p"):
            el.tag = "p"


def _remove_empty_paragraphs(root: Any) -> None:
    for el in root.xpath(".//p | .//ne-p | .//div"):
        if _is_empty_lake_paragraph(el):
            parent = el.getparent()
            if parent is not None:
                parent.remove(el)


def _remove_empty_headings(root: Any) -> None:
    for h in root.xpath("//h1|//h2|//h3|//h4|//h5|//h6"):
        if not _element_plain_text(h):
            parent = h.getparent()
            if parent is not None:
                parent.remove(h)


def _merge_fragmented_lists(container: Any) -> None:
    """语雀列表常为多个 <ul> 各包一个 <li>，合并相邻 <ul> 减少多余换行。"""
    children = list(container)
    i = 0
    while i < len(children):
        el = children[i]
        if (el.tag or "").lower() != "ul":
            i += 1
            continue
        j = i + 1
        while j < len(children):
            nxt = children[j]
            tag = (nxt.tag or "").lower()
            if tag == "ul":
                for li in list(nxt.findall("./li")):
                    el.append(li)
                container.remove(nxt)
                children = list(container)
                continue
            if _is_empty_lake_paragraph(nxt):
                container.remove(nxt)
                children = list(container)
                continue
            break
        i += 1
    for child in list(container):
        if hasattr(child, "tag"):
            _merge_fragmented_lists(child)


def _prepare_lake_tables(root: Any) -> None:
    """表格首行 td→th、扁平单元格；markdownify 与 Quill 均能正确识别。"""
    for table in root.findall(".//table"):
        for cg in table.findall("colgroup"):
            cg.getparent().remove(cg)
        rows = table.findall(".//tr")
        if rows:
            for td in rows[0].xpath("./td"):
                td.tag = "th"
        for cell in table.iter("td", "th"):
            text = re.sub(r"\s+", " ", cell.text_content()).strip()
            cell.attrib.clear()
            cell.text = text
            for child in list(cell):
                cell.remove(child)


def _serialize_lake_root(root: Any) -> str:
    from lxml import html as lxml_html

    parts: list[str] = []
    if root.text:
        parts.append(root.text)
    for child in root:
        parts.append(lxml_html.tostring(child, encoding="unicode", method="html"))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


def prepare_lake_html(html: str) -> str:
    """语雀 Lake HTML 预处理：代码块、表格、去空段落、合并列表。"""
    try:
        from lxml import html as lxml_html
    except ModuleNotFoundError as exc:
        raise RuntimeError("缺少依赖 lxml，请先执行: pip install lxml") from exc

    html = _expand_codeblock_cards(html)
    root = lxml_html.fromstring(f'<div class="lake-root">{html}</div>')
    _normalize_ne_paragraph_tags(root)
    _remove_empty_paragraphs(root)
    _remove_empty_headings(root)
    _merge_fragmented_lists(root)
    _remove_empty_paragraphs(root)
    _prepare_lake_tables(root)
    return _serialize_lake_root(root)


def _nl_attrs(op: dict[str, Any]) -> dict[str, Any]:
    raw = op.get("attributes")
    return dict(raw) if isinstance(raw, dict) else {}


def _is_empty_paragraph_nl(attrs: dict[str, Any]) -> bool:
    """Quill 空段落：仅 text-indent、无正文。"""
    if not attrs:
        return True
    return set(attrs.keys()) <= {"text-indent"} and attrs.get("text-indent") == "0px"


def _is_structural_block_nl(attrs: dict[str, Any]) -> bool:
    if not attrs:
        return False
    if "header" in attrs or "list" in attrs or "blockquote" in attrs:
        return True
    if "code-block" in attrs:
        return True
    if "table-up-cell-inner" in attrs:
        return True
    return False


def _collapse_quill_newlines(delta: dict[str, Any]) -> dict[str, Any]:
    """去掉标题/列表/引用后的空段落换行，合并连续无用换行。"""
    ops = delta.get("ops") or []
    if not ops:
        return delta

    out: list[dict[str, Any]] = []
    for op in ops:
        ins = op.get("insert")
        if isinstance(ins, str) and ins != "\n" and not ins.strip():
            continue

        if ins != "\n":
            out.append(op)
            continue

        attrs = _nl_attrs(op)
        if out and out[-1].get("insert") == "\n":
            prev = _nl_attrs(out[-1])
            if _is_empty_paragraph_nl(attrs):
                if _is_structural_block_nl(prev) or _is_empty_paragraph_nl(prev):
                    continue
            if not attrs and (_is_structural_block_nl(prev) or _is_empty_paragraph_nl(prev)):
                continue
            if _is_empty_paragraph_nl(attrs) and _is_empty_paragraph_nl(prev):
                continue

        if not out and _is_empty_paragraph_nl(attrs):
            continue

        out.append(op)

    while out and out[-1].get("insert") == "\n" and _is_empty_paragraph_nl(_nl_attrs(out[-1])):
        out.pop()

    if not out:
        return {"ops": [{"insert": "\n"}]}
    if out[-1].get("insert") != "\n":
        out.append({"insert": "\n"})
    return {"ops": out}


def _clean_markdown(md: str) -> str:
    md = re.sub(r"\n[ \t]+\n", "\n\n", md)
    md = re.sub(r"(#{1,6})\s{2,}", r"\1 ", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = re.sub(r"(#{1,6}[^\n]+)\n{3,}", r"\1\n\n", md)
    md = re.sub(r"(\n[-*+] .+)\n{2,}(?=[-*+] )", r"\1\n", md)
    md = re.sub(r"(\n\d+\. .+)\n{2,}(?=\n\d+\. )", r"\1\n", md)
    return md.strip() + "\n"


def lake_to_markdown(prepared_html: str) -> str:
    try:
        markdownify = importlib.import_module("markdownify")
    except ModuleNotFoundError as exc:
        raise RuntimeError("缺少依赖 markdownify，请先执行: pip install markdownify") from exc
    md = markdownify.markdownify(
        prepared_html,
        heading_style="ATX",
        bullets="-",
        strip=["script", "style", "svg", "button", "iframe"],
    )
    return _clean_markdown(md)


def scrape_article(item: dict[str, Any], *, book_id: int) -> dict[str, Any]:
    lake = fetch_doc_lake_html(item["doc_id"], book_id)
    content_html = prepare_lake_html(lake_to_html(lake))
    markdown = lake_to_markdown(content_html)
    title = item.get("title") or ""
    m = re.search(r"^#\s+(.+)$", markdown, re.M)
    if m:
        title = m.group(1).strip()
    return {
        "section": item["section"],
        "title": title,
        "sidebar_title": item.get("title") or title,
        "url": item["url"],
        "doc_id": item["doc_id"],
        "markdown": markdown,
        "content_html": content_html,
    }


async def _upload_to_obs(local_path: str, object_key: str) -> str:
    client = HuaweiOBSClient()
    result = await client.upload_file(object_key, local_path, public_read=True)
    if not result.get("success"):
        raise RuntimeError(result.get("error") or "OBS 上传失败")
    url = (result.get("data") or {}).get("url")
    if not url:
        raise RuntimeError("OBS 未返回访问 URL")
    return url


async def enrich_article(
    article: dict[str, Any],
    *,
    cache_dir: Path,
    migrate_images: bool,
    delta_from_markdown: bool = False,
    image_obs_prefix: str = DEFAULT_IMAGE_OBS_PREFIX,
) -> dict[str, Any]:
    md = article.get("markdown") or ""
    if migrate_images and md:
        md, image_map = await migrate_markdown_images(
            md,
            upload_fn=_upload_to_obs,
            cache_dir=cache_dir,
            user_agent=USER_AGENT,
            obs_key_prefix=image_obs_prefix,
            referer=REFERER,
        )
        article["image_map"] = image_map
        article["markdown"] = md
    # 默认 Lake HTML → Quill（表格 quill-table-up、代码块 code-block）
    if not delta_from_markdown and article.get("content_html"):
        delta = _collapse_quill_newlines(
            html_content_to_quill_delta(article["content_html"])
        )
    else:
        delta = _collapse_quill_newlines(markdown_to_quill_delta(md))
    article["quill_delta"] = delta
    article["content"] = quill_delta_to_json(delta)
    return article


async def enrich_all_articles(
    articles: list[dict[str, Any]],
    *,
    cache_dir: Path,
    migrate_images: bool,
    delta_from_markdown: bool = False,
    image_obs_prefix: str = DEFAULT_IMAGE_OBS_PREFIX,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, art in enumerate(articles, start=1):
        if art.get("error"):
            out.append(art)
            continue
        print(f"  处理图片/Quill [{i}/{len(articles)}] {art.get('title')}", file=sys.stderr)
        try:
            out.append(
                await enrich_article(
                    art,
                    cache_dir=cache_dir,
                    migrate_images=migrate_images,
                    delta_from_markdown=delta_from_markdown,
                    image_obs_prefix=image_obs_prefix,
                )
            )
        except Exception as exc:
            out.append({**art, "error": str(exc), "content": "", "quill_delta": None})
            print(f"    失败: {exc}", file=sys.stderr)
    return out


def print_toc(nodes: list[TocNode], indent: int = 0) -> None:
    prefix = "  " * indent
    for node in nodes:
        if node.node_type == "TITLE" or (not node.url and node.children):
            print(f"{prefix}[{node.title}]")
            if node.children:
                print_toc(node.children, indent + 1)
        else:
            print(f"{prefix}- {node.title}")
            if node.url:
                print(f"{prefix}  {node.url}")


def build_toc(book_url: str) -> tuple[list[TocNode], dict[str, Any]]:
    ctx = load_book_context(book_url)
    tree = build_toc_tree(ctx["toc"], book_base=ctx["book_base"])
    return tree, ctx


async def _async_main(args: argparse.Namespace) -> int:
    print(f"正在请求知识库: {args.url}", file=sys.stderr)
    toc_tree, ctx = build_toc(args.url)
    flat_items = iter_toc_entries(ctx["toc"], book_base=ctx["book_base"])
    book_id = ctx["book_id"]

    if args.toc_only:
        doc_count = sum(1 for x in flat_items)
        print(
            f"\n=== 目录《{ctx['book_name']}》（{len(toc_tree)} 个顶层节点 / {doc_count} 篇文档）===\n",
            file=sys.stderr,
        )
        print_toc(toc_tree)
        return 0

    items = flat_items
    if args.limit is not None:
        items = items[: args.limit]

    articles: list[dict[str, Any]] = []
    for i, item in enumerate(items, start=1):
        print(f"[抓取 {i}/{len(items)}] {item['url']}", file=sys.stderr)
        try:
            articles.append(scrape_article(item, book_id=book_id))
        except Exception as exc:
            articles.append({**item, "error": str(exc), "markdown": ""})
            print(f"  失败: {exc}", file=sys.stderr)
        if args.delay > 0 and i < len(items):
            await asyncio.sleep(args.delay)

    migrate_images = not args.no_migrate_images
    cache_dir = Path(args.image_cache_dir)
    if migrate_images:
        print(f"OBS 图片路径前缀: {args.image_obs_prefix}", file=sys.stderr)
    articles = await enrich_all_articles(
        articles,
        cache_dir=cache_dir,
        migrate_images=migrate_images,
        delta_from_markdown=args.delta_from_markdown,
        image_obs_prefix=args.image_obs_prefix,
    )

    import_results: list[dict[str, Any]] = []
    if args.import_db:
        if not args.knowledge_base_id or not args.author_id:
            print("入库需要 --knowledge-base-id 与 --author-id", file=sys.stderr)
            return 1
        db_config = build_tortoise_config(
            host=args.db_host,
            port=args.db_port,
            user=args.db_user,
            password=args.db_password,
            database=args.db_name,
        )
        if args.parent_id is not None:
            print(f"入库父节点: parent_id={args.parent_id}", file=sys.stderr)
        print("正在连接数据库并导入...", file=sys.stderr)
        await init_db(db_config)
        try:
            import_results = await import_articles(
                articles,
                knowledge_base_id=args.knowledge_base_id,
                author_id=args.author_id,
                parent_id=args.parent_id,
                skip_existing=not args.force_update,
            )
        finally:
            await close_db()
        ok = sum(1 for r in import_results if r.get("ok") and not r.get("skipped"))
        print(f"入库完成: 新增 {ok} 篇", file=sys.stderr)

    payload: dict[str, Any] = {
        "source": args.url,
        "book": ctx["book_name"],
        "count": len(articles),
        "articles": articles,
    }
    if import_results:
        payload["import_results"] = import_results

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"已写入 {args.output}", file=sys.stderr)
    elif not args.import_db:
        print(text)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="语雀知识库抓取 / OBS / Quill / 入库")
    parser.add_argument(
        "--url",
        default=DEFAULT_BOOK_URL,
        help="语雀知识库入口，如 https://www.yuque.com/fairy-era/yg511q/",
    )
    parser.add_argument("--toc-only", action="store_true", help="仅打印层级目录")
    parser.add_argument("--limit", type=int, default=None, help="最多抓取篇数")
    parser.add_argument("--delay", type=float, default=0.5, help="抓取间隔秒数")
    parser.add_argument("-o", "--output", type=str, default=None, help="JSON 输出路径")
    parser.add_argument(
        "--image-cache-dir",
        default=str(_ROOT / ".cache" / "yuque_images"),
        help="图片下载临时目录",
    )
    parser.add_argument(
        "--image-obs-prefix",
        default=DEFAULT_IMAGE_OBS_PREFIX,
        help="OBS object key 前缀",
    )
    parser.add_argument(
        "--no-migrate-images",
        action="store_true",
        help="不上传 OBS，仅做 Quill 转换",
    )
    parser.add_argument(
        "--delta-from-markdown",
        action="store_true",
        help="Quill 经 Markdown 转换（默认由预处理后的 Lake HTML 直转，表格/代码块更准确）",
    )
    parser.add_argument("--import-db", action="store_true", help="写入 MySQL articles 表")
    parser.add_argument("--knowledge-base-id", type=int, default=None, help="目标知识库 ID")
    parser.add_argument(
        "--parent-id",
        type=int,
        default=None,
        help="入库时 section 目录的父节点 ID",
    )
    parser.add_argument("--author-id", type=int, default=None, help="文章作者用户 ID")
    parser.add_argument("--force-update", action="store_true", help="不跳过同标题文章")
    parser.add_argument("--db-host", default=settings.DB_HOST)
    parser.add_argument("--db-port", type=int, default=settings.DB_PORT)
    parser.add_argument("--db-user", default=settings.DB_USER)
    parser.add_argument("--db-password", default=settings.DB_PASSWORD)
    parser.add_argument("--db-name", default=settings.DB_NAME)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(_async_main(args)))


if __name__ == "__main__":
    main()
