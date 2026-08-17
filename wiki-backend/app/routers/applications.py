"""
资源申请相关路由（申请记录与站内消息通知审核人）
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from pydantic import BaseModel
from tortoise.transactions import in_transaction

from app.models.user import User
from app.models.application import ResourceApplication
from app.models.team_space import TeamSpace, TeamMember
from app.models.knowledge_base import KnowledgeBase, KnowledgeBaseMember
from app.models.article import Article, ArticleMember
from app.models.notification import Notification
from app.core.dependencies import get_current_active_user
from app.core.response import success_response, error_response
from app.enums import ApplicationStatus, ResourceType

router = APIRouter()


class ApplicationCreate(BaseModel):
    """创建申请请求体"""
    resource_type: int  # 1-团队空间，2-知识库，3-文章
    resource_id: int
    applied_role: int = 1  # 0-只读，1-编辑者，2-管理员
    message: Optional[str] = None  # 申请说明/备注
    reviewer_ids: Optional[List[int]] = None  # 审核人ID列表，为空则查询所有管理员


class ApplicationReview(BaseModel):
    """审核请求体"""
    approved: bool  # True-同意，False-拒绝
    reply_message: Optional[str] = None  # 审核回复说明


async def _get_all_admin_ids(resource_type: int, resource_id: int) -> List[int]:
    """获取资源的所有管理员ID列表（包括所有者和角色为管理员的成员）。"""
    admin_ids = set()
    
    if resource_type == ResourceType.TEAM_SPACE:
        ts = await TeamSpace.get_or_none(id=resource_id, status=1)
        if not ts:
            return []
        # 添加所有者
        admin_ids.add(ts.owner_id)
        # 查询角色为管理员(role=2)的成员
        members = await TeamMember.filter(
            team_space_id=resource_id, status=1, role=2
        ).values_list("user_id", flat=True)
        admin_ids.update(members)
    
    elif resource_type == ResourceType.KNOWLEDGE_BASE:
        kb = await KnowledgeBase.get_or_none(id=resource_id, status=1)
        if not kb:
            return []
        # 添加所有者
        admin_ids.add(kb.owner_id)
        # 查询角色为管理员(role=2)的成员
        members = await KnowledgeBaseMember.filter(
            knowledge_base_id=resource_id, status=1, role=2
        ).values_list("user_id", flat=True)
        admin_ids.update(members)
    
    elif resource_type == ResourceType.ARTICLE:
        article = await Article.get_or_none(id=resource_id, status__gt=0)
        if not article:
            return []
        # 添加作者
        admin_ids.add(article.author_id)
        # 查询角色为管理员(role=2)的成员
        members = await ArticleMember.filter(
            article_id=resource_id, status=1, role=2
        ).values_list("user_id", flat=True)
        admin_ids.update(members)
    
    return list(admin_ids)


@router.post(
    "",
    summary="提交资源申请",
    description="申请人提交对某资源（团队空间/知识库/文章）的加入或角色申请，审核人可在消息通知界面查看。如果reviewer_ids为空，则查询所有管理员；否则使用前端提交的审核人ID。",
)
async def create_application(
    body: ApplicationCreate,
    current_user: User = Depends(get_current_active_user),
):
    """创建申请：申请人=当前用户。如果reviewer_ids为空，查询所有管理员；否则使用前端提交的审核人ID。只创建一条申请记录，多个审核人ID用JSON存储。"""
    if body.resource_type not in (ResourceType.TEAM_SPACE, ResourceType.KNOWLEDGE_BASE, ResourceType.ARTICLE):
        return error_response(400, "资源类型无效")
    if body.applied_role not in (0, 1, 2):
        return error_response(400, "申请角色无效")

    # 确定审核人ID列表
    if body.reviewer_ids is None or len(body.reviewer_ids) == 0:
        # 如果前端未提交或为空，查询所有管理员
        reviewer_ids = await _get_all_admin_ids(body.resource_type, body.resource_id)
        if not reviewer_ids:
            return error_response(404, "资源不存在或已删除，或该资源没有管理员")
    else:
        # 使用前端提交的审核人ID列表
        reviewer_ids = body.reviewer_ids
        # 验证资源是否存在
        if body.resource_type == ResourceType.TEAM_SPACE:
            ts = await TeamSpace.get_or_none(id=body.resource_id, status=1)
            if not ts:
                return error_response(404, "资源不存在或已删除")
        elif body.resource_type == ResourceType.KNOWLEDGE_BASE:
            kb = await KnowledgeBase.get_or_none(id=body.resource_id, status=1)
            if not kb:
                return error_response(404, "资源不存在或已删除")
        elif body.resource_type == ResourceType.ARTICLE:
            article = await Article.get_or_none(id=body.resource_id, status__gt=0)
            if not article:
                return error_response(404, "资源不存在或已删除")
        
        # 验证审核人ID是否有效（用户存在且启用）
        valid_user_ids = await User.filter(id__in=reviewer_ids, status=1).values_list("id", flat=True)
        valid_user_ids = list(valid_user_ids)
        if len(valid_user_ids) != len(reviewer_ids):
            return error_response(400, "部分审核人ID无效或用户已禁用")
        reviewer_ids = valid_user_ids

    # 排除申请人自己
    reviewer_ids = [rid for rid in reviewer_ids if rid != current_user.id]
    if not reviewer_ids:
        return error_response(400, "不能向自己申请")

    # 防止重复提交：检查是否存在待审核状态的申请
    # 同一申请人、同一资源类型、同一资源ID，且状态为待审核(0)
    existing_pending = await ResourceApplication.filter(
        applicant_id=current_user.id,
        resource_type=body.resource_type,
        resource_id=body.resource_id,
        status=ApplicationStatus.PENDING,  # 只检查待审核状态的申请
    ).first()
    
    if existing_pending:
        return error_response(400, "您已提交过该资源的申请，请等待审核结果")

    # 只创建一条申请记录，多个审核人ID用JSON存储，并为每位审核人创建站内通知
    async with in_transaction():
        app = await ResourceApplication.create(
            applicant=current_user,
            resource_type=body.resource_type,
            resource_id=body.resource_id,
            applied_role=body.applied_role,
            message=body.message,
            reviewer_ids=reviewer_ids,  # JSON数组
            status=ApplicationStatus.PENDING,
        )

        for reviewer_id in reviewer_ids:
            await Notification.create(
                user_id=reviewer_id,
                type="resource_application",
                title="资源申请待审核",
                content=f"您有新的资源申请待审核，请及时处理，可点击链接查看详情， 已读忽略",
                link="/knowledge/pending-review",
                is_read=0,
            )

    data = {
        "id": app.id,
        "resource_type": app.resource_type,
        "resource_id": app.resource_id,
        "applied_role": app.applied_role,
        "message": app.message,
        "reviewer_ids": app.reviewer_ids,
        "status": app.status,
        "created_at": app.created_at.isoformat() if app.created_at else None,
    }
    return success_response(
        data=data,
        message=f"申请已提交，已发送给{len(reviewer_ids)}位审核人，请等待审核",
    )


@router.get(
    "",
    summary="获取申请列表",
    description="审核人查看待我审核的申请(type=to_review)，或申请人查看我的申请(type=my)。支持按状态筛选、分页。",
)
async def list_applications(
    list_type: str = Query("to_review", description="to_review-待我审核，my-我的申请"),
    status: Optional[int] = Query(None, description="状态：0-待审核，1-已同意，2-已拒绝，不传则全部"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    current_user: User = Depends(get_current_active_user),
):
    """列表：审核人在消息通知界面查看待审核；申请人查看自己的申请。"""
    if list_type == "to_review":
        # 先获取所有记录，然后在Python中过滤JSON字段
        query = ResourceApplication.all()
        if status is not None:
            if status not in (0, 1, 2):
                return error_response(400, "状态值无效")
            query = query.filter(status=status)
        
        all_applications = await query.order_by("-created_at").all()
        # 过滤：reviewer_ids JSON数组中包含当前用户ID
        applications = [
            app for app in all_applications
            if app.reviewer_ids and current_user.id in app.reviewer_ids
        ]
        total = len(applications)
        # 手动分页
        offset = (page - 1) * page_size
        applications = applications[offset:offset + page_size]
    
    elif list_type == "my":
        query = ResourceApplication.filter(applicant_id=current_user.id)
        if status is not None:
            if status not in (0, 1, 2):
                return error_response(400, "状态值无效")
            query = query.filter(status=status)
        
        total = await query.count()
        offset = (page - 1) * page_size
        applications = await query.order_by("-created_at").offset(offset).limit(page_size).all()
    else:
        return error_response(400, "list_type 只能为 to_review 或 my")

    # 批量拉取申请人、审核人ID列表
    applicant_ids = list({a.applicant_id for a in applications})
    all_reviewer_ids = set()
    for a in applications:
        if a.reviewer_ids:
            all_reviewer_ids.update(a.reviewer_ids)
    user_ids = list(set(applicant_ids + list(all_reviewer_ids)))
    users = await User.filter(id__in=user_ids).all()
    users_map = {u.id: u for u in users}

    # 批量查询资源信息（团队空间、知识库、文章）
    team_space_ids = []
    knowledge_base_ids = []
    article_ids = []
    for a in applications:
        if a.resource_type == ResourceType.TEAM_SPACE:
            team_space_ids.append(a.resource_id)
        elif a.resource_type == ResourceType.KNOWLEDGE_BASE:
            knowledge_base_ids.append(a.resource_id)
        elif a.resource_type == ResourceType.ARTICLE:
            article_ids.append(a.resource_id)
    
    # 查询团队空间名称
    team_spaces_map = {}
    if team_space_ids:
        team_spaces = await TeamSpace.filter(id__in=team_space_ids).values_list("id", "name")
        team_spaces_map = {ts_id: ts_name for ts_id, ts_name in team_spaces}
    
    # 查询知识库名称
    knowledge_bases_map = {}
    if knowledge_base_ids:
        knowledge_bases = await KnowledgeBase.filter(id__in=knowledge_base_ids).values_list("id", "name")
        knowledge_bases_map = {kb_id: kb_name for kb_id, kb_name in knowledge_bases}
    
    # 查询文章名称和所属知识库ID
    articles_map = {}
    if article_ids:
        articles = await Article.filter(id__in=article_ids).values_list("id", "title", "knowledge_base_id")
        articles_map = {
            article_id: {
                "name": article_title,
                "knowledge_base_id": kb_id,
            }
            for article_id, article_title, kb_id in articles
        }

    items = []
    for a in applications:
        applicant = users_map.get(a.applicant_id)
        # 获取审核人列表信息
        reviewer_list = []
        if a.reviewer_ids:
            for rid in a.reviewer_ids:
                reviewer = users_map.get(rid)
                if reviewer:
                    reviewer_list.append({
                        "id": reviewer.id,
                        "name": reviewer.nickname or reviewer.username,
                    })
        
        replied_by = users_map.get(a.replied_by_id) if a.replied_by_id else None
        
        # 根据资源类型获取资源名称和相关信息
        resource_name = None
        knowledge_base_id = None
        
        if a.resource_type == ResourceType.TEAM_SPACE:
            resource_name = team_spaces_map.get(a.resource_id)
        elif a.resource_type == ResourceType.KNOWLEDGE_BASE:
            resource_name = knowledge_bases_map.get(a.resource_id)
        elif a.resource_type == ResourceType.ARTICLE:
            article_info = articles_map.get(a.resource_id)
            if article_info:
                resource_name = article_info["name"]
                knowledge_base_id = article_info["knowledge_base_id"]
        
        items.append({
            "id": a.id,
            "applicant_id": a.applicant_id,
            "applicant_name": (applicant.nickname or applicant.username) if applicant else None,
            "resource_type": a.resource_type,
            "resource_id": a.resource_id,
            "resource_name": resource_name,
            "knowledge_base_id": knowledge_base_id,  # 仅文章类型有此字段
            "applied_role": a.applied_role,
            "message": a.message,
            "reviewer_ids": a.reviewer_ids or [],
            "reviewers": reviewer_list,
            "status": a.status,
            "reply_message": a.reply_message,
            "replied_by_id": a.replied_by_id,
            "replied_by_name": (replied_by.nickname or replied_by.username) if replied_by else None,
            "replied_at": a.replied_at.isoformat() if a.replied_at else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "updated_at": a.updated_at.isoformat() if a.updated_at else None,
        })

    return success_response(
        data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        message="请求成功",
    )


@router.put(
    "/{application_id}/review",
    summary="审核申请",
    description="审核人同意或拒绝申请，填写可选回复说明。",
)
async def review_application(
    application_id: int,
    body: ApplicationReview,
    current_user: User = Depends(get_current_active_user),
):
    """审核人处理申请：同意或拒绝。如果同意，将申请人加入到相应的成员表中。"""
    app = await ResourceApplication.get_or_none(id=application_id)
    if not app:
        return error_response(404, "申请不存在")
    
    # 检查当前用户是否在审核人列表中
    if not app.reviewer_ids or current_user.id not in app.reviewer_ids:
        return error_response(403, "无权审核该申请")
    
    if app.status != ApplicationStatus.PENDING:
        return error_response(400, "该申请已处理，无法重复审核")

    now = datetime.now()
    async with in_transaction():
        app.status = ApplicationStatus.APPROVED if body.approved else ApplicationStatus.REJECTED
        app.reply_message = body.reply_message
        app.replied_at = now
        app.replied_by_id = current_user.id
        await app.save()
        
        # 如果审核通过，将申请人加入到相应的成员表中
        if body.approved:
            applicant = await app.applicant
            if not applicant:
                return error_response(404, "申请人不存在")
            
            if app.resource_type == ResourceType.TEAM_SPACE:
                # 加入团队空间成员表
                team_member = await TeamMember.get_or_none(
                    team_space_id=app.resource_id,
                    user_id=app.applicant_id,
                )
                if team_member:
                    # 如果已存在，更新角色和状态
                    team_member.role = app.applied_role
                    team_member.status = 1
                    team_member.added_by = current_user
                    await team_member.save()
                else:
                    # 如果不存在，创建新记录
                    await TeamMember.create(
                        team_space_id=app.resource_id,
                        user_id=app.applicant_id,
                        role=app.applied_role,
                        status=1,
                        added_by=current_user,
                    )
            
            elif app.resource_type == ResourceType.KNOWLEDGE_BASE:
                # 加入知识库成员表
                kb_member = await KnowledgeBaseMember.get_or_none(
                    knowledge_base_id=app.resource_id,
                    user_id=app.applicant_id,
                )
                if kb_member:
                    # 如果已存在，更新角色和状态
                    kb_member.role = app.applied_role
                    kb_member.status = 1
                    kb_member.added_by = current_user
                    await kb_member.save()
                else:
                    # 如果不存在，创建新记录
                    await KnowledgeBaseMember.create(
                        knowledge_base_id=app.resource_id,
                        user_id=app.applicant_id,
                        role=app.applied_role,
                        status=1,
                        added_by=current_user,
                    )
            
            elif app.resource_type == ResourceType.ARTICLE:
                # 加入文章成员表
                article_member = await ArticleMember.get_or_none(
                    article_id=app.resource_id,
                    user_id=app.applicant_id,
                )
                if article_member:
                    # 如果已存在，更新角色和状态
                    article_member.role = app.applied_role
                    article_member.status = 1
                    article_member.added_by = current_user
                    await article_member.save()
                else:
                    # 如果不存在，创建新记录
                    await ArticleMember.create(
                        article_id=app.resource_id,
                        user_id=app.applicant_id,
                        role=app.applied_role,
                        status=1,
                        added_by=current_user,
                    )

    data = {
        "id": app.id,
        "status": app.status,
        "reply_message": app.reply_message,
        "replied_by_id": app.replied_by_id,
        "replied_at": app.replied_at.isoformat() if app.replied_at else None,
    }
    return success_response(data=data, message="已同意" if body.approved else "已拒绝")
