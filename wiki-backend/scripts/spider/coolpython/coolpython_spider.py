#!/usr/bin/env python3
"""
酷python 教程爬虫 + Markdown / Quill Delta + 可选入库。

1. 解析入口页左侧 #x-wiki-index 目录（按章分组）
2. 逐篇抓取右侧 markdown-body 正文，markdownify 转 Markdown
3. 图片上传 OBS，Markdown 直转 Quill Delta
4. 可选写入 MySQL articles 表

  python scripts/spider/coolpython/coolpython_spider.py --toc-only
  python scripts/spider/coolpython/coolpython_spider.py --limit 3 -o out.json
  python scripts/spider/coolpython/coolpython_spider.py --import-db \\
    --knowledge-base-id 1 --author-id 1 --parent-id 100
"""
from __future__ import annotations

import argparse
import asyncio
import importlib
import json
import re
import sys
from dataclasses import dataclass, field
from html import unescape
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urljoin, urlparse
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

DEFAULT_INDEX_URL = (
    "http://coolpython.net/python_senior/index.html"
)
DEFAULT_IMAGE_OBS_PREFIX = "wiki/import/coolpython"
USER_AGENT = "Mozilla/5.0 (compatible; coolpython-spider/1.0; +http://coolpython.net)"
REFERER = "http://coolpython.net/"


@dataclass
class TocNode:
    title: str
    url: Optional[str] = None
    children: list["TocNode"] = field(default_factory=list)


def fetch_html(url: str, timeout: int = 30) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def series_path_prefix(index_url: str) -> str:
    """如 /python_primary/python_primary_tutorial.html → /python_primary"""
    parts = [p for p in urlparse(index_url).path.strip("/").split("/") if p]
    return f"/{parts[0]}" if parts else ""


def extract_toc_html(page_html: str) -> str:
    m = re.search(
        r'<ul id="x-wiki-index"[^>]*>(.*)</ul>',
        page_html,
        flags=re.S | re.I,
    )
    if not m:
        raise ValueError("页面中未找到 #x-wiki-index 目录")
    return m.group(1)


def _is_html_url(url: Optional[str]) -> bool:
    if not url:
        return False
    return urlparse(url).path.lower().endswith(".html")


def _href_in_series(href: str, path_prefix: str) -> bool:
    """章节占位链接（#）不参与 path 过滤，由子链接判定是否属于当前系列。"""
    if not path_prefix:
        return True
    h = href.strip()
    if not h or h in {"#", "#!"} or h.startswith("javascript:"):
        return True
    return h.startswith(path_prefix)


def parse_coolpython_toc(
    toc_inner: str,
    index_url: str,
    *,
    path_prefix: str,
) -> list[TocNode]:
    """按 depth=0 分章，子链接为 depth=1 文章。"""
    base = f"{urlparse(index_url).scheme}://{urlparse(index_url).netloc}"
    groups: list[TocNode] = []
    blocks = re.split(r"(?=<div[^>]*\bdepth=\"0\"[^>]*>)", toc_inner)
    for block in blocks:
        if not block.strip() or 'depth="0"' not in block:
            continue
        links = re.findall(
            r'<a href="([^"]+)" class="x-wiki-index-item">([^<]+)</a>',
            block,
            flags=re.I,
        )
        if not links:
            continue
        chapter_href, chapter_title = links[0]
        chapter_title = unescape(re.sub(r"\s+", " ", chapter_title).strip())
        if path_prefix and not _href_in_series(chapter_href, path_prefix):
            continue
        children: list[TocNode] = []
        for href, title in links[1:]:
            if path_prefix and not href.startswith(path_prefix):
                continue
            if not _is_html_url(href):
                continue
            t = unescape(re.sub(r"\s+", " ", title).strip())
            children.append(TocNode(title=t, url=urljoin(base, href)))
        if children:
            groups.append(TocNode(title=chapter_title, children=children))
    if not groups:
        raise ValueError("未解析到章节目录，请检查页面结构或 path_prefix")
    return groups


def iter_article_items(toc: list[TocNode]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for group in toc:
        for link in group.children:
            if link.url and _is_html_url(link.url):
                items.append(
                    {
                        "section": group.title,
                        "title": link.title,
                        "url": link.url,
                    }
                )
    return items


def _element_inner_html(el: Any) -> str:
    from lxml import html as lxml_html

    parts: list[str] = []
    if el.text:
        parts.append(el.text)
    for child in el:
        parts.append(lxml_html.tostring(child, encoding="unicode", method="html"))
        if child.tail:
            parts.append(child.tail)
    html = "".join(parts).strip()
    if not html:
        raise ValueError("正文区域为空")
    return html


def _find_markdown_body_element(doc: Any) -> Any:
    wrap_list = doc.xpath('//*[@id="markdown-body-wrap"]')
    if wrap_list:
        return wrap_list[0]

    body_list = doc.xpath(
        '//*[contains(concat(" ", normalize-space(@class), " "), " markdown-body ")]'
    )
    if body_list:
        return body_list[0]

    raise ValueError("未找到正文区域 #markdown-body-wrap 或 .markdown-body")


def extract_article_content_html(page_html: str) -> str:
    try:
        from lxml import html as lxml_html
    except ModuleNotFoundError as exc:
        raise RuntimeError("缺少依赖 lxml，请先执行: pip install lxml") from exc

    doc = lxml_html.fromstring(page_html)
    body_el = _find_markdown_body_element(doc)
    return _element_inner_html(body_el)


def extract_title_from_content(content_html: str, fallback: str) -> str:
    m = re.search(r"<h1[^>]*>([^<]+)", content_html, flags=re.S | re.I)
    if m:
        return unescape(re.sub(r"\s+", " ", m.group(1)).strip())
    return fallback


def _page_base_url(page_url: str) -> str:
    p = urlparse(page_url)
    return f"{p.scheme}://{p.netloc}"


def _absolutize_html_urls(content_html: str, base_url: str) -> str:
    """将 img/a 的相对路径补全为绝对 URL（酷 python 图片多为 /pictures/...）。"""

    def _abs_url(raw: str) -> str:
        u = raw.strip()
        if not u or u.startswith(("http://", "https://", "data:", "mailto:", "#")):
            return u
        return urljoin(base_url, u)

    def repl_attr(m: re.Match[str]) -> str:
        attr, quote, val = m.group(1), m.group(2), m.group(3)
        return f'{attr}={quote}{_abs_url(val)}{quote}'

    content_html = re.sub(
        r'\b(src|href)=(["\'])([^"\']+)\2',
        repl_attr,
        content_html,
        flags=re.I,
    )
    return content_html


def _prepare_content_html(content_html: str, base_url: str) -> str:
    content_html = re.sub(
        r'<a[^>]*href="[^"]*taobao\.com[^"]*"[^>]*>.*?</a>',
        "",
        content_html,
        flags=re.S | re.I,
    )
    content_html = re.sub(
        r"<script[^>]*>.*?</script>",
        "",
        content_html,
        flags=re.S | re.I,
    )
    return _absolutize_html_urls(content_html, base_url)


def _absolutize_markdown_urls(markdown: str, base_url: str) -> str:
    """markdownify 后兜底：相对路径图片/链接补全。"""

    def repl(m: re.Match[str]) -> str:
        alt, url = m.group(1), m.group(2).strip()
        if url.startswith(("http://", "https://", "data:")):
            return m.group(0)
        return f"![{alt}]({urljoin(base_url, url)})"

    md = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", repl, markdown)
    md = re.sub(
        r"(?<!!)\[([^\]]+)\]\(([^)]+)\)",
        lambda m: (
            m.group(0)
            if m.group(2).strip().startswith(("http://", "https://", "mailto:", "#"))
            else f"[{m.group(1)}]({urljoin(base_url, m.group(2).strip())})"
        ),
        md,
    )
    return md


def _clean_markdown(md: str) -> str:
    md = re.sub(r"\n[ \t]+\n", "\n\n", md)
    md = re.sub(r"(#{1,6})\s{2,}", r"\1 ", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


def html_to_markdown(content_html: str, *, base_url: str) -> str:
    try:
        markdownify = importlib.import_module("markdownify")
    except ModuleNotFoundError as exc:
        raise RuntimeError("缺少依赖 markdownify，请先执行: pip install markdownify") from exc

    prepared = _prepare_content_html(content_html, base_url)
    md = markdownify.markdownify(
        prepared,
        heading_style="ATX",
        bullets="-",
        strip=["script", "style", "svg", "button", "iframe"],
    )
    md = _absolutize_markdown_urls(md, base_url)
    return _clean_markdown(md)


def scrape_article(item: dict[str, str]) -> dict[str, Any]:
    page_html = fetch_html(item["url"])
    content_html = extract_article_content_html(page_html)
    base_url = _page_base_url(item["url"])
    content_html = _absolutize_html_urls(content_html, base_url)
    title = extract_title_from_content(content_html, item["title"])
    markdown = html_to_markdown(content_html, base_url=base_url)
    return {
        "section": item["section"],
        "title": title,
        "sidebar_title": item["title"],
        "url": item["url"],
        "markdown": markdown,
        "content_html": content_html,
    }


def build_toc(index_url: str) -> list[TocNode]:
    html = fetch_html(index_url)
    toc_inner = extract_toc_html(html)
    prefix = series_path_prefix(index_url)
    return parse_coolpython_toc(toc_inner, index_url, path_prefix=prefix)


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
    delta_from_html: bool = False,
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
    if delta_from_html and article.get("content_html"):
        delta = html_content_to_quill_delta(article["content_html"])
    else:
        delta = markdown_to_quill_delta(md)
    article["quill_delta"] = delta
    article["content"] = quill_delta_to_json(delta)
    return article


async def enrich_all_articles(
    articles: list[dict[str, Any]],
    *,
    cache_dir: Path,
    migrate_images: bool,
    delta_from_html: bool = False,
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
                    delta_from_html=delta_from_html,
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
        print(f"{prefix}[{node.title}]")
        for child in node.children:
            print(f"{prefix}  - {child.title}")
            print(f"{prefix}    {child.url}")


async def _async_main(args: argparse.Namespace) -> int:
    print(f"正在请求目录: {args.url}", file=sys.stderr)
    toc = build_toc(args.url)
    items = iter_article_items(toc)
    if args.limit is not None:
        items = items[: args.limit]

    if args.toc_only:
        print(f"\n=== 目录（共 {len(toc)} 章 / {len(items)} 篇）===\n")
        print_toc(toc)
        return 0

    articles: list[dict[str, Any]] = []
    for i, item in enumerate(items, start=1):
        print(f"[抓取 {i}/{len(items)}] {item['url']}", file=sys.stderr)
        try:
            articles.append(scrape_article(item))
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
        delta_from_html=args.delta_from_html,
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
    parser = argparse.ArgumentParser(description="酷python 抓取 / OBS 图片 / Quill / 入库")
    parser.add_argument(
        "--url",
        default=DEFAULT_INDEX_URL,
        help="教程入口页（含 #x-wiki-index 左侧目录）",
    )
    parser.add_argument("--toc-only", action="store_true", help="仅打印目录")
    parser.add_argument("--limit", type=int, default=None, help="最多抓取篇数")
    parser.add_argument("--delay", type=float, default=0.5, help="抓取间隔秒数")
    parser.add_argument("-o", "--output", type=str, default=None, help="JSON 输出路径")
    parser.add_argument(
        "--image-cache-dir",
        default=str(_ROOT / ".cache" / "coolpython_images"),
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
        "--delta-from-html",
        action="store_true",
        help="Delta 从正文 HTML 解析（默认 Markdown 直转）",
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
