#!/usr/bin/env python3
"""
小林 coding（VuePress）目录爬虫 + 文章抓取 + 入库。

1. 解析左侧 sidebar，仅保留 .html 链接
2. 逐篇请求正文，用 markdownify 转为 Markdown
3. 图片下载并上传 OBS，替换 Markdown 中的图片 URL
4. Markdown 直转 Quill Delta（mistune AST）；可选 --delta-from-html 从正文 HTML 转
5. 可选写入 MySQL articles 表

  python scripts/spider/xiaolincoding/xiaolincoding_spider.py --limit 2 -o out.json
  python scripts/spider/xiaolincoding/xiaolincoding_spider.py --import-db \\
    --knowledge-base-id 1 --author-id 1 --parent-id 100 \\
    --image-obs-prefix wiki/import/redis
"""
from __future__ import annotations

import argparse
import asyncio
import importlib
import json
import re
import sys
import time
from dataclasses import dataclass, field
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

# wiki-backend 项目根
_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.outer_apis.huawei_obs_api import HuaweiOBSClient  # noqa: E402
from config import settings  # noqa: E402

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from db_import import build_tortoise_config, close_db, import_articles, init_db  # noqa: E402
from markdown_quill import (  # noqa: E402
    html_content_to_quill_delta,
    markdown_to_quill_delta,
    migrate_markdown_images,
    quill_delta_to_json,
)

DEFAULT_URL = "https://www.xiaolincoding.com/redis/"
DEFAULT_IMAGE_OBS_PREFIX = "wiki/import/xiaolincoding"
USER_AGENT = (
    "Mozilla/5.0 (compatible; xiaolincoding-spider/1.0; +https://www.xiaolincoding.com)"
)


@dataclass
class TocNode:
    title: str
    url: Optional[str] = None
    children: list["TocNode"] = field(default_factory=list)


class _SidebarGroupParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.heading: str = ""
        self.links: list[TocNode] = []
        self._in_heading_p = False
        self._in_heading_span = False
        self._in_top_link = False
        self._in_sub_link = False
        self._inside_sub_headers = False
        self._current_parent: Optional[TocNode] = None
        self._buf: list[str] = []
        self._href: str = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        d = {k: v or "" for k, v in attrs}
        cls = d.get("class", "")
        if tag == "span" and self._in_heading_p:
            self._in_heading_span = True
            self._buf = []
        elif tag == "p" and "sidebar-heading" in cls:
            self._in_heading_p = True
        elif tag == "a" and "sidebar-link" in cls:
            self._href = d.get("href", "")
            if "sidebar-sub-header" in cls or self._inside_sub_headers:
                self._in_sub_link = True
            else:
                self._in_top_link = True
            self._buf = []
        elif tag == "ul" and "sidebar-sub-headers" in cls:
            self._inside_sub_headers = True
            self._current_parent = self.links[-1] if self.links else None

    def handle_endtag(self, tag: str) -> None:
        if tag == "span" and self._in_heading_span:
            self.heading = "".join(self._buf).strip()
            self._in_heading_span = False
            self._in_heading_p = False
        elif tag == "a":
            title = unescape("".join(self._buf).strip())
            title = re.sub(r"\s+", " ", title)
            if self._in_sub_link and self._current_parent is not None:
                self._current_parent.children.append(TocNode(title=title, url=self._href))
            elif self._in_top_link:
                self.links.append(TocNode(title=title, url=self._href))
            self._in_top_link = False
            self._in_sub_link = False
            self._buf = []
        elif tag == "ul" and self._inside_sub_headers:
            self._inside_sub_headers = False
            self._current_parent = None

    def handle_data(self, data: str) -> None:
        if self._in_heading_span or self._in_top_link or self._in_sub_link:
            self._buf.append(data)


def fetch_html(url: str, timeout: int = 30) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def extract_sidebar_html(page_html: str) -> str:
    m = re.search(
        r'<aside[^>]*class="[^"]*sidebar[^"]*"[^>]*>(.*)</aside>',
        page_html,
        flags=re.S | re.I,
    )
    if not m:
        raise ValueError("页面中未找到 sidebar 区域")
    return m.group(1)


def _is_html_url(url: Optional[str]) -> bool:
    if not url:
        return False
    return urlparse(url).path.lower().endswith(".html")


def filter_html_only(nodes: list[TocNode]) -> list[TocNode]:
    result: list[TocNode] = []
    for node in nodes:
        if node.url is not None:
            if not _is_html_url(node.url):
                continue
            children = [
                TocNode(title=c.title, url=c.url)
                for c in node.children
                if c.url and _is_html_url(c.url)
            ]
            result.append(TocNode(title=node.title, url=node.url, children=children))
        else:
            children = filter_html_only(node.children)
            if children:
                result.append(TocNode(title=node.title, children=children))
    return result


def parse_sidebar_groups(sidebar_html: str, page_url: str, path_prefix: str) -> list[TocNode]:
    base = f"{urlparse(page_url).scheme}://{urlparse(page_url).netloc}"
    groups = re.findall(
        r'<section class="sidebar-group[^"]*">(.*?)</section>',
        sidebar_html,
        flags=re.S | re.I,
    )
    result: list[TocNode] = []
    for chunk in groups:
        if path_prefix not in chunk:
            continue
        parser = _SidebarGroupParser()
        parser.feed(chunk)
        if not parser.heading and not parser.links:
            continue
        group = TocNode(title=parser.heading or "(未命名分组)", children=[])
        for link in parser.links:
            if link.url:
                link.url = urljoin(base, link.url)
            group.children.append(link)
        result.append(group)
    if not result:
        raise ValueError("未解析到目录分组，请检查页面结构或 path_prefix")
    return result


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


def extract_article_content_html(page_html: str) -> str:
    m = re.search(
        r'class="theme-default-content content__default"[^>]*>(.*?)<footer class="page-edit"',
        page_html,
        flags=re.S | re.I,
    )
    if not m:
        m = re.search(
            r'class="content__default"[^>]*>(.*?)<footer',
            page_html,
            flags=re.S | re.I,
        )
    if not m:
        raise ValueError("未找到正文区域 theme-default-content")
    return m.group(1)


def extract_title_from_content(content_html: str, fallback: str) -> str:
    m = re.search(
        r"<h1[^>]*>(?:\s*<a[^>]*class=\"header-anchor\"[^>]*>.*?</a>\s*)?([^<]+)",
        content_html,
        flags=re.S | re.I,
    )
    if m:
        return unescape(re.sub(r"\s+", " ", m.group(1)).strip())
    m = re.search(r"<title>(.*?)</title>", content_html, re.S | re.I)
    if m:
        return re.sub(r"\s*[|｜].*$", "", unescape(m.group(1))).strip()
    return fallback


def _prepare_content_html(content_html: str) -> str:
    """去掉 VuePress 噪声节点，再交给 markdownify。"""
    content_html = re.sub(
        r'<span class="sr-only">.*?</span>',
        "",
        content_html,
        flags=re.S | re.I,
    )
    content_html = re.sub(
        r'<a[^>]*class="[^"]*header-anchor[^"]*"[^>]*>.*?</a>',
        "",
        content_html,
        flags=re.S | re.I,
    )
    content_html = re.sub(
        r'<motion-div[^>]*>.*',
        "",
        content_html,
        flags=re.S | re.I,
    )
    content_html = re.sub(
        r'<div class="page-nav">.*',
        "",
        content_html,
        flags=re.S | re.I,
    )
    return content_html


def _clean_markdown(md: str) -> str:
    md = re.sub(r"\(opens new window\)", "", md, flags=re.I)
    md = re.sub(r"\*\*\s*\*\*", "", md)
    md = re.sub(r"\n[ \t]+\n", "\n\n", md)
    md = re.sub(r"(#{1,6})\s{2,}", r"\1 ", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


def html_to_markdown(content_html: str) -> str:
    try:
        markdownify = importlib.import_module("markdownify")
    except ModuleNotFoundError as exc:
        raise RuntimeError("缺少依赖 markdownify，请先执行: pip install markdownify") from exc

    prepared = _prepare_content_html(content_html)
    md = markdownify.markdownify(
        prepared,
        heading_style="ATX",
        bullets="-",
        strip=["script", "style", "svg", "button", "iframe"],
    )
    return _clean_markdown(md)


def scrape_article(item: dict[str, str]) -> dict[str, Any]:
    page_html = fetch_html(item["url"])
    content_html = extract_article_content_html(page_html)
    title = extract_title_from_content(content_html, item["title"])
    markdown = html_to_markdown(content_html)
    return {
        "section": item["section"],
        "title": title,
        "sidebar_title": item["title"],
        "url": item["url"],
        "markdown": markdown,
        "content_html": content_html,
    }


def build_toc(index_url: str) -> list[TocNode]:
    path_prefix = urlparse(index_url).path.rstrip("/") or "/"
    if not path_prefix.endswith("/"):
        path_prefix += "/"
    html = fetch_html(index_url)
    sidebar = extract_sidebar_html(html)
    return filter_html_only(parse_sidebar_groups(sidebar, index_url, path_prefix))


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
    """图片迁移 + Markdown/HTML → Quill Delta（默认 Markdown 直转 Delta）。"""
    md = article.get("markdown") or ""
    if migrate_images and md:
        md, image_map = await migrate_markdown_images(
            md,
            upload_fn=_upload_to_obs,
            cache_dir=cache_dir,
            user_agent=USER_AGENT,
            obs_key_prefix=image_obs_prefix,
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
        if node.url:
            print(f"{prefix}- {node.title}")
            print(f"{prefix}  {node.url}")
        else:
            print(f"{prefix}[{node.title}]")
        if node.children:
            print_toc(node.children, indent + 1)


async def _async_main(args: argparse.Namespace) -> int:
    print(f"正在请求目录: {args.url}", file=sys.stderr)
    toc = build_toc(args.url)
    items = iter_article_items(toc)
    if args.limit is not None:
        items = items[: args.limit]

    if args.toc_only:
        print(f"\n=== 目录（仅 .html，共 {len(toc)} 组 / {len(items)} 篇）===\n")
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
    """
    example:
        python scripts/spider/xiaolincoding/xiaolincoding_spider.py \
        --url https://www.xiaolincoding.com/redis/ \
        --import-db \
        --knowledge-base-id 35 \
        --parent-id 762 \
        --author-id 15 \
        --image-obs-prefix wiki/xiaolincoding/redis \
        -o redis_import.json
    """
    parser = argparse.ArgumentParser(description="小林 coding 抓取 / OBS 图片 / Quill / 入库")
    parser.add_argument("--url", default=DEFAULT_URL, help="系列入口页")
    parser.add_argument("--toc-only", action="store_true", help="仅打印目录")
    parser.add_argument("--limit", type=int, default=None, help="最多抓取篇数")
    parser.add_argument("--delay", type=float, default=0.5, help="抓取间隔秒数")
    parser.add_argument("-o", "--output", type=str, default=None, help="JSON 输出路径")
    parser.add_argument(
        "--image-cache-dir",
        default=str(_ROOT / ".cache" / "xiaolincoding_images"),
        help="图片下载临时目录",
    )
    parser.add_argument(
        "--image-obs-prefix",
        default=DEFAULT_IMAGE_OBS_PREFIX,
        help="上传 OBS 的 object key 前缀，文件名自动追加 uuid+扩展名，"
        "如 wiki/import/redis → wiki/import/redis/{uuid}.png",
    )
    parser.add_argument(
        "--no-migrate-images",
        action="store_true",
        help="不上传 OBS，仅做 Quill 转换",
    )
    parser.add_argument(
        "--delta-from-html",
        action="store_true",
        help="Delta 直接从正文 HTML 解析（默认 Markdown→HTML→Delta）",
    )
    parser.add_argument("--import-db", action="store_true", help="写入 MySQL articles 表")
    parser.add_argument("--knowledge-base-id", type=int, default=None, help="目标知识库 ID")
    parser.add_argument(
        "--parent-id",
        type=int,
        default=None,
        help="入库时 section 目录的父节点 ID（须为同知识库下的目录节点；不指定则挂在知识库根）",
    )
    parser.add_argument("--author-id", type=int, default=None, help="文章作者用户 ID")
    parser.add_argument("--force-update", action="store_true", help="不跳过同标题文章（仍新建）")
    parser.add_argument("--db-host", default=settings.DB_HOST)
    parser.add_argument("--db-port", type=int, default=settings.DB_PORT)
    parser.add_argument("--db-user", default=settings.DB_USER)
    parser.add_argument("--db-password", default=settings.DB_PASSWORD)
    parser.add_argument("--db-name", default=settings.DB_NAME)
    args = parser.parse_args()

    raise SystemExit(asyncio.run(_async_main(args)))
    
    

if __name__ == "__main__":
    main()
