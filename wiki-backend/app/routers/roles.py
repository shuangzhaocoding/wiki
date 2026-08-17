"""
角色管理相关路由
"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from tortoise.transactions import in_transaction

from app.models.user import User
from app.models.role import Role, UserRole
from app.models.system_permission import SystemPermission
from app.core.dependencies import get_current_active_user
from app.core.response import success_response, error_response

router = APIRouter()


class RoleCreate(BaseModel):
    """创建角色请求"""
    name: str = Field(..., description="角色名称", max_length=50)
    code: str = Field(..., description="角色代码（唯一标识）", max_length=50)
    description: Optional[str] = Field(None, description="角色描述")
    permissions: List[int] = Field(default_factory=list, description="角色权限ID列表，如：[1, 2, 3]")
    status: int = Field(default=1, description="状态：0-禁用，1-启用")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in (0, 1):
            raise ValueError("状态值必须是0或1")
        return v


class RoleUpdate(BaseModel):
    """更新角色请求"""
    name: Optional[str] = Field(None, description="角色名称", max_length=50)
    code: Optional[str] = Field(None, description="角色代码（唯一标识）", max_length=50)
    description: Optional[str] = Field(None, description="角色描述")
    permissions: Optional[List[int]] = Field(None, description="角色权限ID列表，如：[1, 2, 3]")
    status: Optional[int] = Field(None, description="状态：0-禁用，1-启用")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in (0, 1):
            raise ValueError("状态值必须是0或1")
        return v


class RoleResponse(BaseModel):
    """角色响应"""
    id: int
    name: str
    code: str
    description: Optional[str] = None
    permissions: List[int]  # 权限ID列表 [1, 2, 3]
    status: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RolePermissionUpdate(BaseModel):
    """更新角色权限请求"""
    permissions: List[int] = Field(..., description="角色权限ID列表，如：[1, 2, 3]")


@router.post("", summary="创建角色", description="创建新角色")
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_active_user)
):
    """创建角色"""
    existing_code = await Role.get_or_none(code=role_data.code, status__gte=0)
    if existing_code:
        return error_response(400, "角色代码已存在")

    existing_name = await Role.get_or_none(name=role_data.name, status__gte=0)
    if existing_name:
        return error_response(400, "角色名称已存在")

    if role_data.permissions:
        permission_ids = list(set(role_data.permissions))
        existing_permissions = await SystemPermission.filter(id__in=permission_ids, status=1).all()
        existing_permission_ids = [p.id for p in existing_permissions]
        if len(existing_permission_ids) != len(permission_ids):
            invalid_ids = set(permission_ids) - set(existing_permission_ids)
            return error_response(400, f"部分权限ID不存在或已被禁用：{list(invalid_ids)}")

    async with in_transaction():
        role = await Role.create(
            name=role_data.name,
            code=role_data.code,
            description=role_data.description,
            permissions=role_data.permissions,
            status=role_data.status
        )

    data = RoleResponse.model_validate(role).model_dump()
    return success_response(data=data, message="角色创建成功")


@router.get("", summary="获取角色列表", description="分页获取角色列表，默认返回所有角色（包括已禁用的），支持按状态筛选")
async def get_roles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[int] = Query(None, description="状态筛选：0-禁用，1-启用（不传则返回所有）"),
    keyword: Optional[str] = Query(None, description="关键词搜索（角色名称或代码）"),
    current_user: User = Depends(get_current_active_user)
):
    """获取角色列表"""
    query = Role.all()

    if status is not None:
        if status not in (0, 1):
            return error_response(400, "状态值无效")
        query = query.filter(status=status)

    if keyword:
        query = query.filter(name__icontains=keyword) | query.filter(code__icontains=keyword)

    total = await query.count()
    offset = (page - 1) * page_size
    roles = await query.order_by("-created_at").offset(offset).limit(page_size).all()

    data = {
        "items": [RoleResponse.model_validate(role).model_dump() for role in roles],
        "total": total,
        "page": page,
        "page_size": page_size
    }
    return success_response(data=data, message="获取成功")


@router.get("/{role_id}", summary="获取角色详情", description="根据ID获取角色详情")
async def get_role(
    role_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """获取角色详情"""
    role = await Role.get_or_none(id=role_id)
    if not role:
        return error_response(404, "角色不存在")

    data = RoleResponse.model_validate(role).model_dump()
    return success_response(data=data, message="获取成功")


@router.put("/{role_id}", summary="更新角色", description="更新角色信息")
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """更新角色"""
    role = await Role.get_or_none(id=role_id)
    if not role:
        return error_response(404, "角色不存在")

    if role_data.code and role_data.code != role.code:
        existing_code = await Role.get_or_none(code=role_data.code, status__gte=0)
        if existing_code:
            return error_response(400, "角色代码已存在")

    if role_data.name and role_data.name != role.name:
        existing_name = await Role.get_or_none(name=role_data.name, status__gte=0)
        if existing_name:
            return error_response(400, "角色名称已存在")

    if role_data.permissions is not None:
        permission_ids = list(set(role_data.permissions))
        existing_permissions = await SystemPermission.filter(id__in=permission_ids, status=1).all()
        existing_permission_ids = [p.id for p in existing_permissions]
        if len(existing_permission_ids) != len(permission_ids):
            invalid_ids = set(permission_ids) - set(existing_permission_ids)
            return error_response(400, f"部分权限ID不存在或已被禁用：{list(invalid_ids)}")

    async with in_transaction():
        update_data = role_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(role, key, value)
        await role.save()

    data = RoleResponse.model_validate(role).model_dump()
    return success_response(data=data, message="角色更新成功")


@router.put("/{role_id}/permissions", summary="更新角色权限", description="更新角色的权限配置")
async def update_role_permissions(
    role_id: int,
    permission_data: RolePermissionUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """更新角色权限"""
    role = await Role.get_or_none(id=role_id)
    if not role:
        return error_response(404, "角色不存在")

    if permission_data.permissions:
        permission_ids = list(set(permission_data.permissions))
        existing_permissions = await SystemPermission.filter(id__in=permission_ids, status=1).all()
        existing_permission_ids = [p.id for p in existing_permissions]
        if len(existing_permission_ids) != len(permission_ids):
            invalid_ids = set(permission_ids) - set(existing_permission_ids)
            return error_response(400, f"部分权限ID不存在或已被禁用：{list(invalid_ids)}")

    async with in_transaction():
        role.permissions = permission_data.permissions
        await role.save()

    data = RoleResponse.model_validate(role).model_dump()
    return success_response(data=data, message="角色权限更新成功")


@router.put("/{role_id}/enable", summary="启用角色", description="重新启用已禁用的角色（将状态设为1）")
async def enable_role(
    role_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """启用角色"""
    role = await Role.get_or_none(id=role_id)
    if not role:
        return error_response(404, "角色不存在")

    if role.status == 1:
        return error_response(400, "角色已启用")

    async with in_transaction():
        role.status = 1
        await role.save()

    data = RoleResponse.model_validate(role).model_dump()
    return success_response(data=data, message="角色已启用")


@router.put("/{role_id}/disable", summary="删除角色", description="删除角色（软删除，将状态设为0）")
async def delete_role(
    role_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """删除角色"""
    role = await Role.get_or_none(id=role_id)
    if not role:
        return error_response(404, "角色不存在")

    user_role_count = await UserRole.filter(role_id=role_id, status=1).count()
    if user_role_count > 0:
        return error_response(400, f"该角色正在被 {user_role_count} 个用户使用，无法删除")

    async with in_transaction():
        role.status = 0
        await role.save()

    return success_response(message="角色删除成功")
