"""
系统权限管理相关路由
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from tortoise.transactions import in_transaction

from app.models.user import User
from app.models.system_permission import SystemPermission
from app.core.dependencies import get_current_active_user
from app.core.response import success_response, error_response

router = APIRouter()


class SystemPermissionCreate(BaseModel):
    """创建权限请求"""
    name: str = Field(..., description="权限名称", max_length=100)
    code: str = Field(..., description="权限代码（唯一标识）", max_length=100)
    description: Optional[str] = Field(None, description="权限描述")
    category: Optional[str] = Field(None, description="权限分类", max_length=50)
    status: int = Field(default=1, description="状态：0-禁用，1-启用")
    sort_order: int = Field(default=0, description="排序顺序")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in (0, 1):
            raise ValueError("状态值必须是0或1")
        return v


class SystemPermissionUpdate(BaseModel):
    """更新权限请求"""
    name: Optional[str] = Field(None, description="权限名称", max_length=100)
    code: Optional[str] = Field(None, description="权限代码（唯一标识）", max_length=100)
    description: Optional[str] = Field(None, description="权限描述")
    category: Optional[str] = Field(None, description="权限分类", max_length=50)
    status: Optional[int] = Field(None, description="状态：0-禁用，1-启用")
    sort_order: Optional[int] = Field(None, description="排序顺序")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in (0, 1):
            raise ValueError("状态值必须是0或1")
        return v


class SystemPermissionResponse(BaseModel):
    """权限响应"""
    id: int
    name: str
    code: str
    description: Optional[str] = None
    category: Optional[str] = None
    status: int
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("", summary="创建权限", description="创建新的系统权限定义")
async def create_system_permission(
    permission_data: SystemPermissionCreate,
    current_user: User = Depends(get_current_active_user)
):
    """创建权限"""
    # 检查权限代码是否已存在
    existing_code = await SystemPermission.get_or_none(code=permission_data.code, status__gte=0)
    if existing_code:
        return error_response(400, "权限代码已存在")
    
    # 检查权限名称是否已存在
    existing_name = await SystemPermission.get_or_none(name=permission_data.name, status__gte=0)
    if existing_name:
        return error_response(400, "权限名称已存在")
    
    async with in_transaction():
        permission = await SystemPermission.create(
            name=permission_data.name,
            code=permission_data.code,
            description=permission_data.description,
            category=permission_data.category,
            status=permission_data.status,
            sort_order=permission_data.sort_order
        )
    
    data = SystemPermissionResponse.model_validate(permission).model_dump()
    return success_response(data=data, message="权限创建成功")


@router.get("", summary="获取权限列表", description="分页获取系统权限列表，默认返回所有权限（包括已禁用的），支持按状态和分类筛选")
async def get_system_permissions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[int] = Query(None, description="状态筛选：0-禁用，1-启用（不传则返回所有）"),
    category: Optional[str] = Query(None, description="权限分类筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索（权限名称或代码）"),
    current_user: User = Depends(get_current_active_user)
):
    """获取权限列表"""
    query = SystemPermission.all()
    
    # 状态筛选
    if status is not None:
        if status not in (0, 1):
            return error_response(400, "状态值无效")
        query = query.filter(status=status)
    
    # 分类筛选
    if category:
        query = query.filter(category=category)
    
    # 关键词搜索
    if keyword:
        from tortoise.expressions import Q
        query = query.filter(
            Q(name__icontains=keyword) |
            Q(code__icontains=keyword) |
            Q(description__icontains=keyword)
        )
    
    total = await query.count()
    offset = (page - 1) * page_size
    permissions = await query.order_by("sort_order", "-created_at").offset(offset).limit(page_size).all()
    
    data = {
        "items": [SystemPermissionResponse.model_validate(perm).model_dump() for perm in permissions],
        "total": total,
        "page": page,
        "page_size": page_size
    }
    return success_response(data=data, message="获取成功")


@router.get("/{permission_id}", summary="获取权限详情", description="根据ID获取权限详情")
async def get_system_permission(
    permission_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """获取权限详情"""
    permission = await SystemPermission.get_or_none(id=permission_id)
    if not permission:
        return error_response(404, "权限不存在")
    
    data = SystemPermissionResponse.model_validate(permission).model_dump()
    return success_response(data=data, message="获取成功")


@router.put("/{permission_id}", summary="更新权限", description="更新权限信息")
async def update_system_permission(
    permission_id: int,
    permission_data: SystemPermissionUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """更新权限"""
    permission = await SystemPermission.get_or_none(id=permission_id)
    if not permission:
        return error_response(404, "权限不存在")
    
    # 检查权限代码是否与其他权限冲突
    if permission_data.code and permission_data.code != permission.code:
        existing_code = await SystemPermission.get_or_none(code=permission_data.code, status__gte=0)
        if existing_code:
            return error_response(400, "权限代码已存在")
    
    # 检查权限名称是否与其他权限冲突
    if permission_data.name and permission_data.name != permission.name:
        existing_name = await SystemPermission.get_or_none(name=permission_data.name, status__gte=0)
        if existing_name:
            return error_response(400, "权限名称已存在")
    
    async with in_transaction():
        update_data = permission_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(permission, key, value)
        await permission.save()
    
    data = SystemPermissionResponse.model_validate(permission).model_dump()
    return success_response(data=data, message="权限更新成功")


@router.put("/{permission_id}/enable", summary="启用权限", description="重新启用已禁用的权限（将状态设为1）")
async def enable_system_permission(
    permission_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """启用权限"""
    permission = await SystemPermission.get_or_none(id=permission_id)
    if not permission:
        return error_response(404, "权限不存在")
    
    if permission.status == 1:
        return error_response(400, "权限已启用")
    
    async with in_transaction():
        permission.status = 1
        await permission.save()
    
    data = SystemPermissionResponse.model_validate(permission).model_dump()
    return success_response(data=data, message="权限已启用")


@router.put("/{permission_id}/disable", summary="禁用权限", description="禁用权限（将状态设为0）")
async def disable_system_permission(
    permission_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """禁用权限"""
    permission = await SystemPermission.get_or_none(id=permission_id)
    if not permission:
        return error_response(404, "权限不存在")
    
    if permission.status == 0:
        return error_response(400, "权限已禁用")
    
    async with in_transaction():
        permission.status = 0
        await permission.save()
    
    data = SystemPermissionResponse.model_validate(permission).model_dump()
    return success_response(data=data, message="权限已禁用")


@router.delete("/{permission_id}", summary="删除权限", description="删除权限（软删除，将状态设为0）")
async def delete_system_permission(
    permission_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """删除权限"""
    permission = await SystemPermission.get_or_none(id=permission_id)
    if not permission:
        return error_response(404, "权限不存在")
    
    async with in_transaction():
        permission.status = 0
        await permission.save()
    
    return success_response(message="权限删除成功")


@router.get("/categories/list", summary="获取权限分类列表", description="获取所有权限分类")
async def get_permission_categories(
    current_user: User = Depends(get_current_active_user)
):
    """获取权限分类列表"""
    # 查询所有非空的分类
    categories = await SystemPermission.filter(category__isnull=False).distinct().values_list("category", flat=True)
    
    data = {
        "categories": sorted(list(set(categories))) if categories else []
    }
    return success_response(data=data, message="获取成功")
