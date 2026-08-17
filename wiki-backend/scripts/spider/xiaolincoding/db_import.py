"""将抓取结果写入 wiki 数据库（Tortoise ORM）。"""
from __future__ import annotations

import copy
import re
from datetime import datetime
from typing import Any, Optional

from tortoise import Tortoise
from tortoise.transactions import in_transaction

from app.enums import ArticleNodeType
from app.models.article import Article
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User
from config import TORTOISE_ORM

from markdown_quill import quill_delta_to_json


def build_tortoise_config(
    *,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> dict:
    cfg = copy.deepcopy(TORTOISE_ORM)
    cfg["connections"]["default"]["credentials"].update(
        {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }
    )
    return cfg


def _summary_from_markdown(markdown: str, max_len: int = 480) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", markdown)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[#>*`]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_len] if text else ""


async def _init_import_parent(
    knowledge_base_id: int,
    parent_id: int,
    section_parent: dict[str, int],
    child_sort: dict[int, int],
) -> None:
    """校验父节点，并预加载其下已有目录与子节点排序计数。"""
    parent_node = await Article.get_or_none(
        id=parent_id,
        knowledge_base_id=knowledge_base_id,
        status__gt=0,
    )
    if not parent_node:
        raise ValueError(f"父节点不存在或不属于该知识库: id={parent_id}")
    if parent_node.node_type != ArticleNodeType.DIRECTORY.value:
        raise ValueError(f"父节点必须是目录（node_type=2）: id={parent_id}")

    child_sort[parent_id] = await Article.filter(
        knowledge_base_id=knowledge_base_id,
        parent_id=parent_id,
        status__gt=0,
    ).count()

    existing_dirs = await Article.filter(
        knowledge_base_id=knowledge_base_id,
        parent_id=parent_id,
        node_type=ArticleNodeType.DIRECTORY.value,
        status__gt=0,
    )
    for directory in existing_dirs:
        section_parent[directory.title] = directory.id
        child_sort[directory.id] = await Article.filter(
            knowledge_base_id=knowledge_base_id,
            parent_id=directory.id,
            status__gt=0,
        ).count()


async def import_articles(
    articles: list[dict[str, Any]],
    *,
    knowledge_base_id: int,
    author_id: int,
    parent_id: Optional[int] = None,
    source_url_field: str = "url",
    skip_existing: bool = True,
) -> list[dict[str, Any]]:
    """
    按 section 创建目录节点，其下创建文章；content 为 Quill Delta JSON 字符串。

    parent_id：可选，各 section 目录的 parent_id 均为此值（平铺，互不嵌套）；未指定则挂在知识库根。
    返回每篇的导入结果摘要。
    """
    kb = await KnowledgeBase.get_or_none(id=knowledge_base_id, status=1)
    if not kb:
        raise ValueError(f"知识库不存在: id={knowledge_base_id}")
    author = await User.get_or_none(id=author_id)
    if not author:
        raise ValueError(f"用户不存在: id={author_id}")

    # 固定为 --parent-id，勿在循环内复用 parent_id 变量名
    root_parent_id: Optional[int] = parent_id
    section_parent: dict[str, int] = {}
    child_sort: dict[int, int] = {}
    if root_parent_id is not None:
        await _init_import_parent(
            knowledge_base_id, root_parent_id, section_parent, child_sort
        )

    results: list[dict[str, Any]] = []

    for art in articles:
        if art.get("error"):
            results.append({"title": art.get("title"), "ok": False, "error": art["error"]})
            continue

        section = (art.get("section") or "未分类").strip()
        title = (art.get("title") or art.get("sidebar_title") or "未命名").strip()[:200]
        quill = art.get("quill_delta")
        if not quill:
            results.append({"title": title, "ok": False, "error": "缺少 quill_delta"})
            continue

        content_json = (
            quill if isinstance(quill, str) else quill_delta_to_json(quill)
        )

        async with in_transaction():
            if section not in section_parent:
                if root_parent_id is not None:
                    section_dir_parent_id = root_parent_id
                    s_order = child_sort.get(section_dir_parent_id, 0)
                    child_sort[section_dir_parent_id] = s_order + 1
                else:
                    section_dir_parent_id = None
                    s_order = len(section_parent)
                dir_article = await Article.create(
                    knowledge_base_id=knowledge_base_id,
                    parent_id=section_dir_parent_id,
                    node_type=ArticleNodeType.DIRECTORY.value,
                    title=section[:200],
                    content=None,
                    summary=None,
                    author_id=author_id,
                    visibility=kb.visibility,
                    sort_order=s_order,
                    status=2,
                    is_original=False,
                    is_ai_generated=False,
                    published_at=datetime.utcnow(),
                )
                section_parent[section] = dir_article.id
                child_sort[dir_article.id] = child_sort.get(dir_article.id, 0)

            article_parent_id = section_parent[section]
            if skip_existing:
                exists = await Article.filter(
                    knowledge_base_id=knowledge_base_id,
                    parent_id=article_parent_id,
                    title=title,
                    status__gt=0,
                ).exists()
                if exists:
                    results.append(
                        {
                            "title": title,
                            "section": section,
                            "ok": True,
                            "skipped": True,
                            "reason": "同标题已存在",
                        }
                    )
                    continue

            order = child_sort.get(article_parent_id, 0)
            child_sort[article_parent_id] = order + 1
            markdown = art.get("markdown") or ""
            article = await Article.create(
                knowledge_base_id=knowledge_base_id,
                parent_id=article_parent_id,
                node_type=ArticleNodeType.ARTICLE.value,
                title=title,
                content=content_json,
                summary=_summary_from_markdown(markdown) or None,
                author_id=author_id,
                visibility=kb.visibility,
                sort_order=order,
                status=2,
                is_original=False,
                is_ai_generated=False,
                published_at=datetime.utcnow(),
            )

        results.append(
            {
                "title": title,
                "section": section,
                "ok": True,
                "article_id": article.id,
                "parent_id": article_parent_id,
                "section_parent_id": root_parent_id,
                "source_url": art.get(source_url_field),
            }
        )

    return results


async def init_db(db_config: dict) -> None:
    await Tortoise.init(config=db_config)


async def close_db() -> None:
    await Tortoise.close_connections()
