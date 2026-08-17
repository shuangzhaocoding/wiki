"""
权限相关路由
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from pydantic import BaseModel
from app.models.user import User
from app.models.permission import Permission
from app.models.team_space import TeamSpace, TeamMember
from app.models.knowledge_base import KnowledgeBase, KnowledgeBaseMember
from app.models.article import Article, ArticleMember
from app.core.dependencies import get_current_active_user
from app.core.response import success_response, error_response
from app.utils.permissions import require_permission

router = APIRouter()


class PermissionGrant(BaseModel):
    user_id: int
    resource_type: int  # 1-团队空间，2-知识库，3-文章
    resource_id: int
    permission_type: int  # 1-只读，2-可编辑，3-管理员
    expires_at: Optional[str] = None  # ISO格式日期字符串


class PermissionResponse(BaseModel):
    id: int
    user_id: int
    resource_type: int
    resource_id: int
    permission_type: int
    granted_by: Optional[int] = None
    granted_at: datetime
    expires_at: Optional[datetime] = None
    status: int

    class Config:
        from_attributes = True


@router.post("")
async def grant_permission(
    permission_data: PermissionGrant,
    current_user: User = Depends(get_current_active_user)
):
    """授予权限"""
    # 检查用户是否存在
    user = await User.get_or_none(id=permission_data.user_id, status=1)
    if not user:
        return error_response(404, "用户不存在")
    
    # 检查授权人是否有权限授予该资源的权限（需要管理员权限）
    await require_permission(current_user, permission_data.resource_type, permission_data.resource_id, 2)
    
    # 解析过期时间
    expires_at = None
    if permission_data.expires_at:
        try:
            expires_at = datetime.fromisoformat(permission_data.expires_at.replace('Z', '+00:00'))
        except:
            return error_response(400, "过期时间格式错误")
    
    # 检查是否已存在权限
    existing = await Permission.get_or_none(
        user_id=permission_data.user_id,
        resource_type=permission_data.resource_type,
        resource_id=permission_data.resource_id
    )
    
    if existing:
        # 更新现有权限
        existing.permission_type = permission_data.permission_type
        existing.granted_by = current_user
        existing.expires_at = expires_at
        existing.status = 1
        await existing.save()
        data = PermissionResponse.model_validate(existing).model_dump()
        return success_response(data=data, message="权限已更新")
    else:
        # 创建新权限
        permission = await Permission.create(
            user=user,
            resource_type=permission_data.resource_type,
            resource_id=permission_data.resource_id,
            permission_type=permission_data.permission_type,
            granted_by=current_user,
            expires_at=expires_at
        )
        data = PermissionResponse.model_validate(permission).model_dump()
        return success_response(data=data, message="权限已授予")


@router.get("")
async def get_permissions(
    resource_type: Optional[int] = Query(None, description="资源类型"),
    resource_id: Optional[int] = Query(None, description="资源ID"),
    user_id: Optional[int] = Query(None, description="用户ID"),
    current_user: User = Depends(get_current_active_user)
):
    """获取权限列表"""
    query = Permission.filter(status=1)
    
    if resource_type and resource_id:
        # 检查是否有权限查看该资源的权限列表
        await require_permission(current_user, resource_type, resource_id, 2)
        query = query.filter(resource_type=resource_type, resource_id=resource_id)
    elif user_id:
        # 只能查看自己的权限
        if user_id != current_user.id:
            return error_response(403, "只能查看自己的权限")
        query = query.filter(user_id=user_id)
    else:
        # 只返回自己的权限
        query = query.filter(user_id=current_user.id)
    
    permissions = await query.all()
    data = [PermissionResponse.model_validate(p).model_dump() for p in permissions]
    return success_response(data=data, message="获取成功")


@router.delete("/{permission_id}")
async def revoke_permission(
    permission_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """撤销权限"""
    permission = await Permission.get_or_none(id=permission_id, status=1)
    if not permission:
        return error_response(404, "权限不存在")
    
    # 检查是否有权限撤销该权限
    await require_permission(current_user, permission.resource_type, permission.resource_id, 2)
    
    permission.status = 0
    await permission.save()
    return success_response(message="权限已撤销")


@router.get("/check")
async def check_permission(
    resource_type: int = Query(..., description="资源类型"),
    resource_id: int = Query(..., description="资源ID"),
    required_permission: int = Query(1, description="所需权限类型"),
    current_user: User = Depends(get_current_active_user)
):
    """检查用户权限"""
    from app.utils.permissions import check_user_permission
    
    result = await check_user_permission(
        current_user,
        resource_type,
        resource_id,
        required_permission,
    )

    data = {
        "has_permission": result.allowed,
        "role": result.role,
        "user_id": current_user.id,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "required_permission": required_permission,
    }
    return success_response(data=data, message="检查完成")


@router.get(
    "/admins",
    summary="获取资源管理员列表",
    description="根据资源类型和资源ID，获取该资源下所有管理员信息（所有者/作者 + 角色为管理员的成员）。支持文章、知识库、团队空间。",
)
async def get_resource_admins(
    resource_type: int = Query(..., description="资源类型：1-团队空间，2-知识库，3-文章"),
    resource_id: int = Query(..., description="资源ID"),
    current_user: User = Depends(get_current_active_user),
):
    """获取资源下所有管理员：根据资源类型查询所有者/作者 + 角色为管理员(role=2)的成员。"""
    admin_user_ids = set()
    owner_id = None
    created_at = None
    member_admin_rows = []
    
    if resource_type == 1:  # 团队空间
        team_space = await TeamSpace.get_or_none(id=resource_id, status=1)
        if not team_space:
            return error_response(404, "团队空间不存在")
        owner_id = team_space.owner_id
        created_at = team_space.created_at
        admin_user_ids.add(owner_id)
        # 查询角色为管理员(role=2)的成员
        member_admin_rows = await TeamMember.filter(
            team_space_id=resource_id, status=1, role=2
        ).values_list("user_id", "joined_at")
        admin_user_ids.update([uid for uid, _ in member_admin_rows])
    
    elif resource_type == 2:  # 知识库
        kb = await KnowledgeBase.get_or_none(id=resource_id, status=1)
        if not kb:
            return error_response(404, "知识库不存在")
        owner_id = kb.owner_id
        created_at = kb.created_at
        admin_user_ids.add(owner_id)
        # 查询角色为管理员(role=2)的成员
        member_admin_rows = await KnowledgeBaseMember.filter(
            knowledge_base_id=resource_id, status=1, role=2
        ).values_list("user_id", "joined_at")
        admin_user_ids.update([uid for uid, _ in member_admin_rows])
    
    elif resource_type == 3:  # 文章
        article = await Article.get_or_none(id=resource_id, status__gt=0)
        if not article:
            return error_response(404, "文章不存在")
        owner_id = article.author_id
        created_at = article.created_at
        admin_user_ids.add(owner_id)
        # 查询角色为管理员(role=2)的成员
        member_admin_rows = await ArticleMember.filter(
            article_id=resource_id, status=1, role=2
        ).values_list("user_id", "joined_at")
        admin_user_ids.update([uid for uid, _ in member_admin_rows])
    
    else:
        return error_response(400, "资源类型无效")

    if not admin_user_ids:
        return success_response(data=[], message="获取成功")

    users = await User.filter(id__in=list(admin_user_ids), status=1).all()
    users_map = {u.id: u for u in users}

    items = []
    # 先返回所有者/作者
    owner = users_map.get(owner_id)
    if owner:
        items.append({
            "id": owner.id,
            "username": owner.username,
            "email": owner.email,
            "nickname": owner.nickname,
            "avatar": owner.avatar,
            "role_type": "owner" if resource_type in (1, 2) else "author",
            "joined_at": created_at.isoformat() if created_at else None,
        })
    
    # 再返回成员中的管理员（排除所有者/作者，避免重复）
    for uid, joined_at in member_admin_rows:
        if uid == owner_id:
            continue
        u = users_map.get(uid)
        if not u:
            continue
        items.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "nickname": u.nickname,
            "avatar": u.avatar,
            "role_type": "admin",
            "joined_at": joined_at.isoformat() if joined_at else None,
        })

    return success_response(data=items, message="获取成功")