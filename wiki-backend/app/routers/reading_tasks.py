"""
阅读任务相关路由：主从表设计，针对文章为指定角色下的用户创建必读任务
"""
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from tortoise.transactions import in_transaction

from app.models.user import User
from app.models.article import Article
from app.models.knowledge_base import KnowledgeBase
from app.models.role import Role, UserRole
from app.models.reading_task import ReadingTaskBatch, ReadingTask
from app.models.notification import Notification
from app.core.dependencies import get_current_active_user
from app.core.response import success_response, error_response
from app.utils.permissions import require_permission

router = APIRouter()


class ReadingTaskAssignRequest(BaseModel):
    """下发阅读任务请求体"""
    article_id: int = Field(..., description="文章ID")
    knowledge_base_id: int = Field(..., description="所属知识库ID")
    required_seconds: int = Field(..., ge=1, description="要求最少阅读时长（秒）")
    deadline: Optional[datetime] = Field(None, description="阅读截止时间（ISO 时间，可空）")
    role_ids: List[int] = Field(..., min_length=1, description="对象列表：角色ID集合")


@router.post(
    "/assign",
    summary="为文章下发阅读任务",
    description="根据文章ID、所属知识库ID和角色ID列表，创建签读批次，并为每个角色下的用户创建阅读任务。",
)
async def assign_reading_tasks(
    body: ReadingTaskAssignRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    为指定文章下发阅读任务：
    1. 创建签读批次（主表）
    2. 根据 role_ids 查询所有有效用户
    3. 为每个用户创建一条任务明细（从表）
    """
    article = await Article.get_or_none(id=body.article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")

    if article.knowledge_base_id != body.knowledge_base_id:
        return error_response(400, "文章与知识库ID不匹配")

    kb = await KnowledgeBase.get_or_none(id=body.knowledge_base_id, status=1)
    if not kb:
        return error_response(404, "知识库不存在")

    await require_permission(current_user, 3, body.article_id, 2)

    if body.required_seconds <= 0:
        return error_response(400, "required_seconds 必须大于 0")

    role_ids = list(set(body.role_ids))
    roles = await Role.filter(id__in=role_ids, status=1).all()
    valid_role_ids = {r.id for r in roles}
    if len(valid_role_ids) != len(role_ids):
        invalid_ids = set(role_ids) - valid_role_ids
        return error_response(400, f"部分角色ID不存在或已被禁用：{list(invalid_ids)}")

    user_roles = await UserRole.filter(
        role_id__in=role_ids,
        status=1,
    ).values_list("user_id", "role_id")

    if not user_roles:
        return success_response(data={"batch_id": None, "created": 0, "skipped": 0}, message="角色下没有用户，无任务创建")

    user_to_roles = {}
    for uid, rid in user_roles:
        user_to_roles.setdefault(uid, set()).add(rid)

    user_ids = list(user_to_roles.keys())
    users = await User.filter(id__in=user_ids, status=1).values_list("id", flat=True)
    valid_user_ids = set(users)

    if not valid_user_ids:
        return success_response(data={"batch_id": None, "created": 0, "skipped": 0}, message="角色下用户均被禁用，无任务创建")

    created_count = 0
    skipped_count = 0

    async with in_transaction():
        batch = await ReadingTaskBatch.create(
            article_id=body.article_id,
            knowledge_base_id=body.knowledge_base_id,
            required_seconds=body.required_seconds,
            deadline=body.deadline,
            role_ids=role_ids,
            status=0,
            created_by=current_user,
            updated_by=current_user,
        )

        for uid in valid_user_ids:
            # existing = await ReadingTask.filter(
            #     batch__article_id=body.article_id,
            #     user_id=uid,
            #     status__in=[0, 1],
            # ).exists()
            # if existing:
            #     skipped_count += 1
            #     continue

            role_id = next(iter(user_to_roles.get(uid, [])), None)
            await ReadingTask.create(
                batch=batch,
                user_id=uid,
                role_id=role_id,
                status=0,
                updated_by=current_user,
            )
            created_count += 1

            # 创建站内消息通知
            await Notification.create(
                user_id=uid,
                type="reading_task_assigned",
                title="签读任务通知",
                content=f"您有新的签读任务，请及时阅读，可点击链接查看详情， 已读忽略",
                link=f"/articles/{body.knowledge_base_id}?articleId={body.article_id}",
                is_read=0,
            )

    return success_response(
        data={"batch_id": batch.id, "created": created_count, "skipped": skipped_count},
        message="阅读任务下发完成",
    )


@router.get(
    "",
    summary="获取所有签读任务批次",
    description="获取所有签读批次，按创建时间倒序，含文章、创建人、角色ID列表、任务数量。支持分页、按批次状态筛选。",
)
async def get_all_reading_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[int] = Query(None, description="批次状态筛选：0-有效，1-已取消（不传则全部）"),
    current_user: User = Depends(get_current_active_user),
):
    """获取所有签读任务批次"""
    query = ReadingTaskBatch.all().prefetch_related("article", "knowledge_base", "created_by")
    if status is not None:
        if status not in (0, 1):
            return error_response(400, "状态值无效")
        query = query.filter(status=status)

    total = await query.count()
    offset = (page - 1) * page_size
    batches = await query.order_by("-created_at").offset(offset).limit(page_size)

    items = []
    for batch in batches:
        article = await batch.article
        kb = await batch.knowledge_base
        creator = await batch.created_by
        task_count = await ReadingTask.filter(batch_id=batch.id).count()

        items.append({
            "batch_id": batch.id,
            "article_id": batch.article_id,
            "article_title": article.title if article else None,
            "knowledge_base_id": batch.knowledge_base_id,
            "knowledge_base_name": kb.name if kb else None,
            "required_seconds": batch.required_seconds,
            "deadline": batch.deadline.isoformat() if batch.deadline else None,
            "created_by_id": batch.created_by_id,
            "created_by_name": (creator.nickname or creator.username) if creator else None,
            "role_ids": batch.role_ids or [],
            "task_count": task_count,
            "status": batch.status,
            "created_at": batch.created_at.isoformat() if batch.created_at else None,
        })

    return success_response(
        data={"items": items, "total": total, "page": page, "page_size": page_size},
        message="获取成功",
    )


@router.get(
    "/check",
    summary="检查文章签读状态",
    description="根据文章ID判断当前用户是否需要签读此文章。优先返回第一个未完成任务；若无则返回最后一个已签读任务。",
)
async def check_article_sign_read(
    article_id: int = Query(..., description="文章ID"),
    current_user: User = Depends(get_current_active_user),
):
    """根据文章ID判断当前用户是否需要签读此文章。优先返回未完成任务，若无则返回最后一个已签读任务"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")

    task = await ReadingTask.filter(
        batch__article_id=article_id,
        batch__status=0,
        user_id=current_user.id,
    ).order_by("-created_at").prefetch_related("batch", "batch__created_by").first()

    if not task:
        return success_response(
            data={"need_sign_read": False, "article_id": article_id},
            message="无需签读",
        )

    batch = await task.batch
    

    now = datetime.now(timezone.utc)
    deadline = batch.deadline
    if deadline and task.status in [0, 1]:
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        else:
            deadline = deadline.astimezone(timezone.utc)
        if now > deadline:
            task.status = 3
            await task.save()
            return success_response(
                data={"need_sign_read": True, "article_id": article_id, "status": 3},
                message="已过期",
            )
    creator = await batch.created_by
    actual = task.actual_seconds or 0
    required = batch.required_seconds
    remaining = max(0, required - actual)
    return success_response(
        data={
            "need_sign_read": True,
            "article_id": article_id,
            "task_id": task.id,
            "batch_id": batch.id,
            "status": task.status,
            "actual_seconds": actual,
            "required_seconds": required,
            "remaining_seconds": remaining,
            "deadline": batch.deadline.isoformat() if batch.deadline else None,
            "created_by_id": batch.created_by_id,
            "created_by_name": (creator.nickname or creator.username) if creator else None,
            "created_at": batch.created_at.isoformat() if batch.created_at else None,
        },
        message="获取成功",
    )


@router.get(
    "/me",
    summary="获取当前用户的阅读任务列表",
    description="分页获取当前用户的阅读任务，支持按状态筛选，返回文章标题、知识库ID等信息。",
)
async def get_my_reading_tasks(
    status: Optional[int] = Query(
        None,
        description="状态筛选：0-未开始，1-进行中，2-已完成，3-已过期，4-已取消（不传则全部）",
    ),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
):
    """获取当前登录用户的阅读任务列表"""
    query = ReadingTask.filter(user_id=current_user.id)

    if status is not None:
        if status not in (0, 1, 2, 3, 4):
            return error_response(400, "状态值无效")
        query = query.filter(status=status)

    total = await query.count()
    offset = (page - 1) * page_size

    tasks = (
        await query.order_by("-created_at")
        .offset(offset)
        .limit(page_size)
        .prefetch_related("batch", "batch__article", "batch__knowledge_base")
    )

    items = []
    for t in tasks:
        batch = await t.batch
        article = await batch.article
        kb = await batch.knowledge_base
        items.append({
            "id": t.id,
            "batch_id": batch.id,
            "article_id": batch.article_id,
            "article_title": article.title if article else None,
            "knowledge_base_id": batch.knowledge_base_id,
            "knowledge_base_name": kb.name if kb else None,
            "required_seconds": batch.required_seconds,
            "deadline": batch.deadline.isoformat() if batch.deadline else None,
            "status": t.status,
            "started_at": t.started_at.isoformat() if t.started_at else None,
            "finished_at": t.finished_at.isoformat() if t.finished_at else None,
            "actual_seconds": t.actual_seconds,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        })

    return success_response(
        data={"items": items, "total": total, "page": page, "page_size": page_size},
        message="获取成功",
    )


class ReadingTaskStatusUpdate(BaseModel):
    """阅读任务状态更新请求体"""
    status: int = Field(..., description="新状态：0-未开始，1-进行中，2-已完成，3-已过期，4-已取消")
    actual_seconds: Optional[int] = Field(None, ge=0, description="实际累计阅读时长（秒）")


class ReadingTaskBatchUpdateRequest(BaseModel):
    """批量修改签读任务请求体（修改批次）"""
    required_seconds: Optional[int] = Field(None, ge=1, description="要求最少阅读时长（秒）")
    deadline: Optional[datetime] = Field(None, description="阅读截止时间（ISO 时间，可空表示取消截止）")
    role_ids: Optional[List[int]] = Field(None, description="重新指定角色ID列表；新增角色则增加任务，移除的角色则取消其任务")


@router.put(
    "/{task_id}/status",
    summary="更新阅读任务状态",
    description="当前用户更新自己的阅读任务状态，可同时上报实际阅读时长。",
)
async def update_reading_task_status(
    task_id: int,
    body: ReadingTaskStatusUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """更新阅读任务状态"""
    if body.status not in (0, 1, 2, 3, 4):
        return error_response(400, "状态值无效")

    task = await ReadingTask.get_or_none(id=task_id).prefetch_related("batch")
    if not task:
        return error_response(404, "阅读任务不存在")

    if task.user_id != current_user.id:
        return error_response(403, "只能更新自己的阅读任务")

    now = datetime.utcnow()

    async with in_transaction():
        previous_status = task.status
        task.status = body.status

        if previous_status == 0 and body.status == 1 and not task.started_at:
            task.started_at = now

        if body.status == 2 and not task.finished_at:
            task.finished_at = now

        if body.actual_seconds is not None:
            task.actual_seconds = body.actual_seconds

        task.updated_by = current_user
        await task.save()

    batch = await task.batch
    data = {
        "id": task.id,
        "batch_id": batch.id,
        "article_id": batch.article_id,
        "status": task.status,
        "required_seconds": batch.required_seconds,
        "actual_seconds": task.actual_seconds,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "finished_at": task.finished_at.isoformat() if task.finished_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }
    return success_response(data=data, message="更新成功")


@router.put(
    "/{task_id}",
    summary="修改签读任务（修改所属批次）",
    description="修改任务所属批次的要求时长、截止时间。",
)
async def update_reading_task(
    task_id: int,
    body: ReadingTaskBatchUpdateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """修改签读任务：更新所属批次的 required_seconds、deadline"""
    task = await ReadingTask.get_or_none(id=task_id).prefetch_related("batch")
    if not task:
        return error_response(404, "阅读任务不存在")

    batch = await task.batch

    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        return error_response(400, "请提供要修改的字段")

    if "required_seconds" in update_data and update_data["required_seconds"] <= 0:
        return error_response(400, "required_seconds 必须大于 0")

    async with in_transaction():
        for key, value in update_data.items():
            setattr(batch, key, value)
        batch.updated_by = current_user
        await batch.save()

    data = {
        "id": task.id,
        "batch_id": batch.id,
        "article_id": batch.article_id,
        "required_seconds": batch.required_seconds,
        "deadline": batch.deadline.isoformat() if batch.deadline else None,
        "updated_at": batch.updated_at.isoformat() if batch.updated_at else None,
    }
    return success_response(data=data, message="修改成功")


@router.post(
    "/{task_id}/cancel",
    summary="取消签读任务",
    description="取消单个签读任务。",
)
async def cancel_reading_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """取消单个签读任务"""
    task = await ReadingTask.get_or_none(id=task_id).prefetch_related("batch")
    if not task:
        return error_response(404, "阅读任务不存在")

    if task.status == 4:
        return success_response(data={"id": task.id, "status": 4}, message="任务已处于取消状态")

    async with in_transaction():
        task.status = 4
        task.updated_by = current_user
        await task.save()

    return success_response(
        data={"id": task.id, "status": 4, "updated_at": task.updated_at.isoformat() if task.updated_at else None},
        message="取消成功",
    )


@router.put(
    "/batches/{batch_id}",
    summary="修改签读任务批次",
    description="修改批次的要求时长、截止时间、角色。重新指定角色时：新增角色则增加任务，移除的角色则取消其任务。",
)
async def update_reading_task_batch(
    batch_id: int,
    body: ReadingTaskBatchUpdateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """修改签读任务批次：可更新 required_seconds、deadline、role_ids。"""
    batch = await ReadingTaskBatch.get_or_none(id=batch_id)
    if not batch:
        return error_response(404, "签读批次不存在")

    if batch.status == 1:
        return error_response(400, "该批次已取消")

    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        return error_response(400, "请提供要修改的字段")

    if "required_seconds" in update_data and update_data["required_seconds"] <= 0:
        return error_response(400, "required_seconds 必须大于 0")

    role_ids_update = update_data.pop("role_ids", None)

    if role_ids_update is not None:
        new_role_ids = list(set(role_ids_update))
        roles = await Role.filter(id__in=new_role_ids, status=1).all()
        valid_role_ids = {r.id for r in roles}
        if len(valid_role_ids) != len(new_role_ids):
            invalid_ids = set(new_role_ids) - valid_role_ids
            return error_response(400, f"部分角色ID不存在或已被禁用：{list(invalid_ids)}")

    async with in_transaction():
        for key, value in update_data.items():
            setattr(batch, key, value)

        if role_ids_update is not None:
            new_role_ids = list(set(role_ids_update))
            new_role_ids_set = set(new_role_ids)
            old_role_ids = set(batch.role_ids or [])
            added_role_ids = new_role_ids_set - old_role_ids
            removed_role_ids = old_role_ids - new_role_ids_set

            # 移除的角色：取消其任务（任务 role_id 在移除列表中的）
            if removed_role_ids:
                to_cancel = await ReadingTask.filter(
                    batch_id=batch_id,
                    role_id__in=list(removed_role_ids),
                    status__in=[0, 1],
                ).all()
                for task in to_cancel:
                    task.status = 4
                    task.updated_by = current_user
                    await task.save()

            # 新增的角色：为角色下用户增加任务（已存在则跳过）
            if added_role_ids:
                user_roles = await UserRole.filter(
                    role_id__in=list(added_role_ids),
                    status=1,
                ).values_list("user_id", "role_id")
                user_to_roles = {}
                for uid, rid in user_roles:
                    user_to_roles.setdefault(uid, set()).add(rid)

                users = await User.filter(id__in=list(user_to_roles.keys()), status=1).values_list("id", flat=True)
                valid_user_ids = set(users)

                for uid in valid_user_ids:
                    existing = await ReadingTask.filter(
                        batch_id=batch_id,
                        user_id=uid,
                    ).exists()
                    if existing:
                        continue
                    role_id = next(iter(user_to_roles.get(uid, [])), None)
                    await ReadingTask.create(
                        batch=batch,
                        user_id=uid,
                        role_id=role_id,
                        status=0,
                        updated_by=current_user,
                    )
                    # 创建站内消息通知
                    await Notification.create(
                        user_id=uid,
                        type="reading_task_assigned",
                        title="您有新的签读任务",
                        link=f"/articles/{batch.knowledge_base_id}?articleId={batch.article_id}",
                        is_read=0,
                    )

            batch.role_ids = sorted(new_role_ids_set)

        batch.updated_by = current_user
        await batch.save()

    return success_response(
        data={
            "batch_id": batch.id,
            "required_seconds": batch.required_seconds,
            "deadline": batch.deadline.isoformat() if batch.deadline else None,
            "role_ids": batch.role_ids or [],
            "updated_at": batch.updated_at.isoformat() if batch.updated_at else None,
        },
        message="修改成功",
    )


@router.get(
    "/batches/{batch_id}/tasks",
    summary="获取批次下的所有任务",
    description="获取指定签读批次下的所有任务明细，含用户、角色、状态、阅读时长等。支持分页和状态筛选。",
)
async def get_batch_tasks(
    batch_id: int,
    status: Optional[int] = Query(
        None,
        description="任务状态筛选：0-未开始，1-进行中，2-已完成，3-已过期，4-已取消（不传则全部）",
    ),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
):
    """获取批次下的所有任务"""
    batch = await ReadingTaskBatch.get_or_none(id=batch_id)
    if not batch:
        return error_response(404, "签读批次不存在")

    query = ReadingTask.filter(batch_id=batch_id)

    if status is not None:
        if status not in (0, 1, 2, 3, 4):
            return error_response(400, "状态值无效")
        query = query.filter(status=status)

    total = await query.count()
    offset = (page - 1) * page_size

    tasks = (
        await query.order_by("-created_at")
        .offset(offset)
        .limit(page_size)
        .prefetch_related("user", "role")
    )

    items = []
    for t in tasks:
        user = await t.user
        role = await t.role
        items.append({
            "id": t.id,
            "user_id": t.user_id,
            "username": user.username if user else None,
            "nickname": user.nickname if user else None,
            "role_id": t.role_id,
            "role_name": role.name if role else None,
            "status": t.status,
            "required_seconds": batch.required_seconds,
            "actual_seconds": t.actual_seconds,
            "started_at": t.started_at.isoformat() if t.started_at else None,
            "finished_at": t.finished_at.isoformat() if t.finished_at else None,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        })

    return success_response(
        data={
            "batch_id": batch_id,
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        message="获取成功",
    )


@router.post(
    "/batches/{batch_id}/cancel",
    summary="批量取消签读任务",
    description="取消指定批次下的所有未完成任务。",
)
async def cancel_reading_task_batch(
    batch_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """批量取消签读任务批次"""
    batch = await ReadingTaskBatch.get_or_none(id=batch_id)
    if not batch:
        return error_response(404, "签读批次不存在")

    tasks = await ReadingTask.filter(
        batch_id=batch_id,
        status__in=[0, 1],
    ).all()

    if not tasks:
        return success_response(data={"cancelled_count": 0}, message="没有可取消的任务")

    async with in_transaction():
        for task in tasks:
            task.status = 4
            task.updated_by = current_user
            await task.save()
        batch.status = 1
        batch.updated_by = current_user
        await batch.save()

    return success_response(
        data={"batch_id": batch_id, "cancelled_count": len(tasks)},
        message=f"已取消 {len(tasks)} 个任务",
    )
