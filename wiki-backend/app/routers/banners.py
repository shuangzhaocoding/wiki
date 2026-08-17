"""
Banner 相关路由：用于管理首页或模块的 Banner（轮播图/横幅）
"""
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from tortoise.transactions import in_transaction

from app.models.user import User
from app.models.banner import Banner
from app.core.dependencies import get_current_active_user
from app.core.response import success_response, error_response

router = APIRouter()


class BannerCreate(BaseModel):
    title: Optional[str] = None
    image_url: str
    link_url: Optional[str] = None
    description: Optional[str] = None
    position: Optional[str] = "default"
    sort_order: Optional[int] = 0
    status: Optional[int] = 1  # 0-禁用，1-启用


class BannerUpdate(BaseModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    description: Optional[str] = None
    position: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[int] = None


@router.get(
    "",
    summary="获取 Banner 列表",
    description="按位置、状态获取 Banner 列表，默认只返回启用状态且按 sort_order 升序、created_at 倒序排序。",
)
async def list_banners(
    position: Optional[str] = Query(None, description="展示位置标识，如 home_top、kb_top"),
    status: Optional[int] = Query(None, description="状态：0-禁用，1-启用；默认只返回启用的 Banner"),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取 Banner 列表。
    """
    query = Banner.all()

    if position:
        query = query.filter(position=position)

    if status is not None:
        query = query.filter(status=status)

    banners = await query.order_by("sort_order", "-created_at").all()

    # 批量查询创建人、更新人的信息
    created_ids = {b.created_by_id for b in banners if getattr(b, "created_by_id", None)}
    updated_ids = {b.updated_by_id for b in banners if getattr(b, "updated_by_id", None)}
    user_ids = list(created_ids.union(updated_ids))
    users_map = {}
    if user_ids:
        users = await User.filter(id__in=user_ids).all()
        users_map = {u.id: u for u in users}

    items = []
    for b in banners:
        created_user = users_map.get(getattr(b, "created_by_id", None))
        updated_user = users_map.get(getattr(b, "updated_by_id", None))
        items.append(
            {
                "id": b.id,
                "title": b.title,
                "image_url": b.image_url,
                "link_url": b.link_url,
                "description": b.description,
                "position": b.position,
                "sort_order": b.sort_order,
                "status": b.status,
                "created_by_id": getattr(b, "created_by_id", None),
                "created_by_name": (created_user.nickname or created_user.username) if created_user else None,
                "created_by_email": created_user.email if created_user else None,
                "updated_by_id": getattr(b, "updated_by_id", None),
                "updated_by_name": (updated_user.nickname or updated_user.username) if updated_user else None,
                "updated_by_email": updated_user.email if updated_user else None,
                "created_at": b.created_at.isoformat() if b.created_at else None,
                "updated_at": b.updated_at.isoformat() if b.updated_at else None,
            }
        )

    return success_response(data=items, message="获取成功")


@router.post(
    "",
    summary="创建 Banner",
    description="创建新的 Banner 记录，用于配置首页或模块的轮播图/横幅。",
)
async def create_banner(
    banner_data: BannerCreate,
    current_user: User = Depends(get_current_active_user),
):
    """
    创建 Banner。
    """
    if not banner_data.image_url:
        return error_response(400, "image_url 不能为空")

    async with in_transaction():
        banner = await Banner.create(
            title=banner_data.title,
            image_url=banner_data.image_url,
            link_url=banner_data.link_url,
            description=banner_data.description,
            position=banner_data.position or "default",
            sort_order=banner_data.sort_order or 0,
            status=banner_data.status if banner_data.status is not None else 1,
            created_by=current_user,
            updated_by=current_user,
        )

    creator_name = current_user.nickname or current_user.username

    data = {
        "id": banner.id,
        "title": banner.title,
        "image_url": banner.image_url,
        "link_url": banner.link_url,
        "description": banner.description,
        "position": banner.position,
        "sort_order": banner.sort_order,
        "status": banner.status,
        "created_by_id": banner.created_by_id,
        "created_by_name": creator_name,
        "created_by_email": current_user.email,
        "updated_by_id": banner.updated_by_id,
        "updated_by_name": creator_name,
        "updated_by_email": current_user.email,
        "created_at": banner.created_at.isoformat() if banner.created_at else None,
        "updated_at": banner.updated_at.isoformat() if banner.updated_at else None,
    }
    return success_response(data=data, message="创建成功")


@router.put(
    "/{banner_id}",
    summary="更新 Banner",
    description="根据 Banner ID 更新其基础信息，如标题、图片链接、跳转链接、排序等。",
)
async def update_banner(
    banner_id: int,
    banner_data: BannerUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """
    更新 Banner。
    """
    banner = await Banner.get_or_none(id=banner_id)
    if not banner:
        return error_response(404, "Banner 不存在")

    update_dict = banner_data.model_dump(exclude_unset=True)

    if "status" in update_dict and update_dict["status"] not in (0, 1):
        return error_response(400, "status 只能为 0 或 1")

    async with in_transaction():
        for field, value in update_dict.items():
            setattr(banner, field, value)
        banner.updated_by = current_user
        await banner.save()

    # 获取创建人、更新人信息
    created_user = await banner.created_by
    updated_user = current_user

    data = {
        "id": banner.id,
        "title": banner.title,
        "image_url": banner.image_url,
        "link_url": banner.link_url,
        "description": banner.description,
        "position": banner.position,
        "sort_order": banner.sort_order,
        "status": banner.status,
        "created_by_id": getattr(banner, "created_by_id", None),
        "created_by_name": (created_user.nickname or created_user.username) if created_user else None,
        "created_by_email": created_user.email if created_user else None,
        "updated_by_id": getattr(banner, "updated_by_id", None),
        "updated_by_name": (updated_user.nickname or updated_user.username) if updated_user else None,
        "updated_by_email": updated_user.email,
        "created_at": banner.created_at.isoformat() if banner.created_at else None,
        "updated_at": banner.updated_at.isoformat() if banner.updated_at else None,
    }
    return success_response(data=data, message="更新成功")


@router.put(
    "/{banner_id}/status",
    summary="启用/禁用 Banner",
    description="通过修改 status 字段启用(1)或禁用(0)指定 Banner。",
)
async def update_banner_status(
    banner_id: int,
    status: int = Query(..., description="Banner 状态：0-禁用，1-启用"),
    current_user: User = Depends(get_current_active_user),
):
    """
    启用/禁用 Banner。
    """
    if status not in (0, 1):
        return error_response(400, "status 只能为 0 或 1")

    banner = await Banner.get_or_none(id=banner_id)
    if not banner:
        return error_response(404, "Banner 不存在")

    async with in_transaction():
        banner.status = status
        banner.updated_by = current_user
        await banner.save()

    updated_user = current_user
    created_user = await banner.created_by

    return success_response(
        data={
            "id": banner.id,
            "status": banner.status,
            "created_by_id": getattr(banner, "created_by_id", None),
            "created_by_name": (created_user.nickname or created_user.username) if created_user else None,
            "created_by_email": created_user.email if created_user else None,
            "updated_by_id": getattr(banner, "updated_by_id", None),
            "updated_by_name": (updated_user.nickname or updated_user.username) if updated_user else None,
            "updated_by_email": updated_user.email,
        },
        message="操作成功",
    )

