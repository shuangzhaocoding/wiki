"""
站内消息通知相关路由
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.models.user import User
from app.models.notification import Notification
from app.core.dependencies import get_current_active_user
from app.core.response import success_response, error_response

router = APIRouter()


@router.get(
    "/unread-count",
    summary="获取未读消息数量",
    description="获取当前用户的未读消息数量。",
)
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
):
    """获取未读消息数量"""
    count = await Notification.filter(user_id=current_user.id, is_read=0).count()
    return success_response(data={"count": count}, message="获取成功")


@router.get(
    "",
    summary="获取所有消息",
    description="分页获取当前用户的站内消息，支持按已读状态筛选。",
)
async def get_notifications(
    is_read: Optional[int] = Query(
        None,
        description="已读状态筛选：0-未读，1-已读（不传则全部）",
    ),
    type: Optional[str] = Query(
        None,
        description="消息类型筛选，例如：reading_task_assigned、reading_task_reminder（不传则全部）",
    ),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
):
    """获取当前用户的所有站内消息"""
    query = Notification.filter(user_id=current_user.id)

    if is_read is not None:
        if is_read not in (0, 1):
            return error_response(400, "状态值无效")
        query = query.filter(is_read=is_read)

    if type:
        query = query.filter(type=type)

    total = await query.count()
    offset = (page - 1) * page_size

    notifications = (
        await query.order_by("-created_at")
        .offset(offset)
        .limit(page_size)
    )

    items = [
        {
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "content": n.content,
            "link": n.link,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "updated_at": n.updated_at.isoformat() if n.updated_at else None,
        }
        for n in notifications
    ]

    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        message="获取成功",
    )


class NotificationStatusUpdate(BaseModel):
    """消息状态更新请求体"""
    is_read: int = Field(..., description="是否已读：0-未读，1-已读")


@router.put(
    "/{notification_id}",
    summary="更新消息状态",
    description="更新指定消息的已读状态。",
)
async def update_notification_status(
    notification_id: int,
    body: NotificationStatusUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """更新消息状态"""
    if body.is_read not in (0, 1):
        return error_response(400, "is_read 必须为 0 或 1")

    notification = await Notification.get_or_none(id=notification_id)
    if not notification:
        return error_response(404, "消息不存在")

    if notification.user_id != current_user.id:
        return error_response(403, "只能操作自己的消息")

    notification.is_read = body.is_read
    await notification.save()

    return success_response(
        data={
            "id": notification.id,
            "is_read": notification.is_read,
            "updated_at": notification.updated_at.isoformat() if notification.updated_at else None,
        },
        message="更新成功",
    )
