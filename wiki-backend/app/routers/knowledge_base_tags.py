"""
指定知识库下的标签：增删改查
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from tortoise.transactions import in_transaction

from app.core.dependencies import get_current_active_user, get_request_locale
from app.core.response import error_response, success_response
from app.i18n import t
from app.models.article import ArticleTag, Tag
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User
from app.schemas.tag import TagCreate, TagResponse, TagUpdate
from app.utils.permissions import require_permission

router = APIRouter()


@router.get("", summary="标签列表")
async def list_tags(
    kb_id: int,
    keyword: Optional[str] = Query(None, description="按名称模糊搜索"),
    current_user: User = Depends(get_current_active_user),
    locale: str = Depends(get_request_locale),
):
    kb = await KnowledgeBase.get_or_none(id=kb_id, status=1)
    if not kb:
        return error_response(404, t(locale, "kb.tag.kb_not_found"))

    await require_permission(current_user, 2, kb_id, 0)

    query = Tag.filter(knowledge_base_id=kb_id)
    if keyword and keyword.strip():
        query = query.filter(name__icontains=keyword.strip())
    tags = await query.order_by("name").all()
    items = [TagResponse.model_validate(x).model_dump() for x in tags]
    return success_response(data={"items": items}, message=t(locale, "kb.tag.list_success"))


@router.post("", summary="创建标签")
async def create_tag(
    kb_id: int,
    body: TagCreate,
    current_user: User = Depends(get_current_active_user),
    locale: str = Depends(get_request_locale),
):
    kb = await KnowledgeBase.get_or_none(id=kb_id, status=1)
    if not kb:
        return error_response(404, t(locale, "kb.tag.kb_not_found"))

    await require_permission(current_user, 2, kb_id, 1)

    name_stripped = body.name.strip()
    if not name_stripped:
        return error_response(400, t(locale, "kb.tag.name_empty"))

    dup = await Tag.get_or_none(knowledge_base_id=kb_id, name=name_stripped)
    if dup:
        return error_response(400, t(locale, "kb.tag.duplicate_name"))

    color_val = body.color.strip() if body.color else None
    if color_val == "":
        color_val = None

    async with in_transaction():
        tag = await Tag.create(
            knowledge_base=kb,
            name=name_stripped,
            color=color_val,
        )

    data = TagResponse.model_validate(tag).model_dump()
    return success_response(data=data, message=t(locale, "kb.tag.create_success"))


@router.get("/{tag_id}", summary="标签详情")
async def get_tag(
    kb_id: int,
    tag_id: int,
    current_user: User = Depends(get_current_active_user),
    locale: str = Depends(get_request_locale),
):
    kb = await KnowledgeBase.get_or_none(id=kb_id, status=1)
    if not kb:
        return error_response(404, t(locale, "kb.tag.kb_not_found"))

    await require_permission(current_user, 2, kb_id, 0)

    tag = await Tag.get_or_none(id=tag_id, knowledge_base_id=kb_id)
    if not tag:
        return error_response(404, t(locale, "kb.tag.tag_not_found"))

    data = TagResponse.model_validate(tag).model_dump()
    return success_response(data=data, message=t(locale, "kb.tag.get_success"))


@router.put("/{tag_id}", summary="更新标签")
async def update_tag(
    kb_id: int,
    tag_id: int,
    body: TagUpdate,
    current_user: User = Depends(get_current_active_user),
    locale: str = Depends(get_request_locale),
):
    kb = await KnowledgeBase.get_or_none(id=kb_id, status=1)
    if not kb:
        return error_response(404, t(locale, "kb.tag.kb_not_found"))

    await require_permission(current_user, 2, kb_id, 1)

    tag = await Tag.get_or_none(id=tag_id, knowledge_base_id=kb_id)
    if not tag:
        return error_response(404, t(locale, "kb.tag.tag_not_found"))

    payload = body.model_dump(exclude_unset=True)
    if not payload:
        return error_response(400, t(locale, "kb.tag.no_fields"))

    if "name" in payload and payload["name"] is not None:
        name_stripped = payload["name"].strip()
        if not name_stripped:
            return error_response(400, t(locale, "kb.tag.name_empty"))
        other = (
            await Tag.filter(knowledge_base_id=kb_id, name=name_stripped)
            .exclude(id=tag_id)
            .first()
        )
        if other:
            return error_response(400, t(locale, "kb.tag.duplicate_name"))
        tag.name = name_stripped

    if "color" in payload:
        c = payload["color"]
        if c is None:
            tag.color = None
        else:
            c = c.strip()
            tag.color = None if c == "" else c

    async with in_transaction():
        await tag.save()

    data = TagResponse.model_validate(tag).model_dump()
    return success_response(data=data, message=t(locale, "kb.tag.update_success"))


@router.delete("/{tag_id}", summary="删除标签")
async def delete_tag(
    kb_id: int,
    tag_id: int,
    current_user: User = Depends(get_current_active_user),
    locale: str = Depends(get_request_locale),
):
    kb = await KnowledgeBase.get_or_none(id=kb_id, status=1)
    if not kb:
        return error_response(404, t(locale, "kb.tag.kb_not_found"))

    await require_permission(current_user, 2, kb_id, 1)

    tag = await Tag.get_or_none(id=tag_id, knowledge_base_id=kb_id)
    if not tag:
        return error_response(404, t(locale, "kb.tag.tag_not_found"))

    async with in_transaction():
        await ArticleTag.filter(tag_id=tag.id).delete()
        await tag.delete()

    return success_response(message=t(locale, "kb.tag.delete_success"))
