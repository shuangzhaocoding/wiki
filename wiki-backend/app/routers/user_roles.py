"""
用户角色管理相关路由
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from tortoise.transactions import in_transaction

from app.models.user import User
from app.models.role import Role, UserRole
from app.models.system_permission import SystemPermission
from app.core.dependencies import get_current_active_user
from app.core.response import success_response, error_response

router = APIRouter()


async def get_permissions_detail(permission_ids: List[int]) -> List[dict]:
    """根据权限ID列表获取权限详细信息"""
    if not permission_ids:
        return []
    
    permissions = await SystemPermission.filter(id__in=permission_ids, status=1).all()
    return [
        {
            "id": perm.id,
            "name": perm.name,
            "code": perm.code,
            "description": perm.description,
            "category": perm.category
        }
        for perm in permissions
    ]


class UserRoleAssign(BaseModel):
    """分配用户角色请求"""
    user_id: int = Field(..., description="用户ID")
    role_ids: List[int] = Field(..., description="角色ID列表")


class UserRoleResponse(BaseModel):
    """用户角色响应"""
    id: int
    user_id: int
    role_id: int
    role_name: str
    role_code: str
    role_permissions: dict
    status: int
    assigned_by: Optional[int] = None
    assigned_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserWithRolesResponse(BaseModel):
    """用户及其角色列表响应"""
    user_id: int
    username: str
    email: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    user_status: int
    roles: List[dict]  # JSON列表展示角色信息


@router.post("/assign", summary="为用户分配角色", description="为用户分配一个或多个角色，会替换用户现有的所有角色")
async def assign_user_roles(
    assign_data: UserRoleAssign,
    current_user: User = Depends(get_current_active_user)
):
    """为用户分配角色"""
    # 检查用户是否存在
    user = await User.get_or_none(id=assign_data.user_id)
    if not user:
        return error_response(404, "用户不存在")
    
    # 检查角色是否存在且启用
    if not assign_data.role_ids:
        return error_response(400, "角色ID列表不能为空")
    
    roles = await Role.filter(id__in=assign_data.role_ids, status=1).all()
    if len(roles) != len(assign_data.role_ids):
        return error_response(400, "部分角色不存在或已被禁用")
    
    async with in_transaction():
        # 先移除用户现有的所有角色（软删除）
        existing_user_roles = await UserRole.filter(user_id=assign_data.user_id, status=1).all()
        for user_role in existing_user_roles:
            user_role.status = 0
            await user_role.save()
        
        # 分配新角色
        for role in roles:
            # 检查是否已存在（可能是之前被移除的）
            existing = await UserRole.get_or_none(user_id=assign_data.user_id, role_id=role.id)
            if existing:
                existing.status = 1
                existing.assigned_by = current_user
                existing.assigned_at = datetime.now()
                await existing.save()
            else:
                await UserRole.create(
                    user=user,
                    role=role,
                    assigned_by=current_user,
                    status=1
                )
    
    # 返回用户及其角色信息
    user_roles = await UserRole.filter(user_id=assign_data.user_id, status=1).prefetch_related("role").all()
    roles_data = []
    for ur in user_roles:
        role = await ur.role
        roles_data.append({
            "id": role.id,
            "name": role.name,
            "code": role.code,
            "permissions": role.permissions if role.permissions else [],  # 权限ID列表 [1, 2, 3]
            "assigned_at": ur.assigned_at.isoformat() if ur.assigned_at else None
        })
    
    data = {
        "user_id": user.id,
        "username": user.username,
        "roles": roles_data
    }
    return success_response(data=data, message="角色分配成功")


@router.post("/{user_id}/roles/{role_id}", summary="为用户添加单个角色", description="为用户添加一个角色（不替换现有角色）")
async def add_user_role(
    user_id: int,
    role_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """为用户添加单个角色"""
    # 检查用户是否存在
    user = await User.get_or_none(id=user_id)
    if not user:
        return error_response(404, "用户不存在")
    
    # 检查角色是否存在且启用
    role = await Role.get_or_none(id=role_id, status=1)
    if not role:
        return error_response(404, "角色不存在或已被禁用")
    
    # 检查是否已存在
    existing = await UserRole.get_or_none(user_id=user_id, role_id=role_id)
    if existing:
        if existing.status == 1:
            return error_response(400, "用户已拥有该角色")
        else:
            # 重新启用
            async with in_transaction():
                existing.status = 1
                existing.assigned_by = current_user
                existing.assigned_at = datetime.now()
                await existing.save()
            return success_response(message="角色已重新分配")
    
    async with in_transaction():
        await UserRole.create(
            user=user,
            role=role,
            assigned_by=current_user,
            status=1
        )
    
    return success_response(message="角色添加成功")


@router.delete("/{user_id}/roles/{role_id}", summary="移除用户的单个角色", description="移除用户的指定角色")
async def remove_user_role(
    user_id: int,
    role_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """移除用户的单个角色"""
    user_role = await UserRole.get_or_none(user_id=user_id, role_id=role_id, status=1)
    if not user_role:
        return error_response(404, "用户角色关联不存在")
    
    async with in_transaction():
        user_role.status = 0
        await user_role.save()
    
    return success_response(message="角色移除成功")


@router.get("/{user_id}/roles", summary="获取用户的角色列表", description="获取指定用户的所有角色（JSON列表）")
async def get_user_roles(
    user_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的角色列表"""
    # 检查用户是否存在
    user = await User.get_or_none(id=user_id)
    if not user:
        return error_response(404, "用户不存在")
    
    user_roles = await UserRole.filter(user_id=user_id, status=1).prefetch_related("role").all()
    
    roles_data = []
    for ur in user_roles:
        role = await ur.role
        # 获取权限详细信息
        permissions_detail = await get_permissions_detail(role.permissions if role.permissions else [])
        roles_data.append({
            "id": role.id,
            "name": role.name,
            "code": role.code,
            "permissions": permissions_detail,  # 权限详细信息列表
            "assigned_at": ur.assigned_at.isoformat() if ur.assigned_at else None,
            "assigned_by": ur.assigned_by_id
        })
    
    data = {
        "user_id": user.id,
        "username": user.username,
        "roles": roles_data
    }
    return success_response(data=data, message="获取成功")


@router.put("/{user_id}/disable", summary="禁用用户", description="禁用用户（将用户状态设为0）")
async def disable_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """禁用用户"""
    # 不能禁用自己
    if user_id == current_user.id:
        return error_response(400, "不能禁用自己")
    
    user = await User.get_or_none(id=user_id)
    if not user:
        return error_response(404, "用户不存在")
    
    if user.status == 0:
        return error_response(400, "用户已被禁用")
    
    async with in_transaction():
        user.status = 0
        await user.save()
    
    data = {
        "user_id": user.id,
        "username": user.username,
        "status": user.status
    }
    return success_response(data=data, message="用户已禁用")


@router.put("/{user_id}/enable", summary="启用用户", description="启用用户（将用户状态设为1）")
async def enable_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """启用用户"""
    user = await User.get_or_none(id=user_id)
    if not user:
        return error_response(404, "用户不存在")
    
    if user.status == 1:
        return error_response(400, "用户已启用")
    
    async with in_transaction():
        user.status = 1
        await user.save()
    
    data = {
        "user_id": user.id,
        "username": user.username,
        "status": user.status
    }
    return success_response(data=data, message="用户已启用")


@router.get("/users/{user_id}", summary="获取用户及其角色信息", description="获取用户详细信息及其所有角色（JSON列表）")
async def get_user_with_roles(
    user_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """获取用户及其角色信息"""
    user = await User.get_or_none(id=user_id)
    if not user:
        return error_response(404, "用户不存在")
    
    user_roles = await UserRole.filter(user_id=user_id, status=1).prefetch_related("role").all()
    
    roles_data = []
    for ur in user_roles:
        role = await ur.role
        roles_data.append({
            "id": role.id,
            "name": role.name,
            "code": role.code,
            "permissions": role.permissions if role.permissions else [],  # 权限ID列表
            "assigned_at": ur.assigned_at.isoformat() if ur.assigned_at else None
        })
    
    data = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "user_status": user.status,
        "roles": roles_data
    }
    return success_response(data=data, message="获取成功")


@router.get("", summary="获取用户角色列表", description="分页获取所有用户及其角色信息")
async def get_users_with_roles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[int] = Query(None, description="用户状态筛选：0-禁用，1-启用"),
    keyword: Optional[str] = Query(None, description="关键词搜索（用户名、邮箱、昵称）"),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户角色列表"""
    query = User.all()
    
    # 状态筛选
    if status is not None:
        if status not in (0, 1):
            return error_response(400, "状态值无效")
        query = query.filter(status=status)
    
    # 关键词搜索
    if keyword:
        from tortoise.expressions import Q
        query = query.filter(
            Q(username__icontains=keyword) |
            Q(email__icontains=keyword) |
            Q(nickname__icontains=keyword)
        )
    
    total = await query.count()
    offset = (page - 1) * page_size
    users = await query.order_by("-created_at").offset(offset).limit(page_size).all()
    
    # 批量获取用户角色
    user_ids = [u.id for u in users]
    user_roles_map = {}
    if user_ids:
        user_roles = await UserRole.filter(user_id__in=user_ids, status=1).prefetch_related("role").all()
        for ur in user_roles:
            if ur.user_id not in user_roles_map:
                user_roles_map[ur.user_id] = []
            role = await ur.role
            user_roles_map[ur.user_id].append({
                "id": role.id,
                "name": role.name,
                "code": role.code,
                "permissions": role.permissions if role.permissions else [],  # 权限ID列表
                "assigned_at": ur.assigned_at.isoformat() if ur.assigned_at else None
            })
    
    items = []
    for user in users:
        items.append({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "user_status": user.status,
            "roles": user_roles_map.get(user.id, [])
        })
    
    data = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }
    return success_response(data=data, message="获取成功")
