"""
用户相关的Schema
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class UserCreate(BaseModel):
    """创建用户"""
    username: str
    password: str
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None


class UserCreateRequest(BaseModel):
    """创建用户请求（含角色分配）"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")
    email: EmailStr = Field(..., description="邮箱")
    role_ids: List[int] = Field(default_factory=list, description="分配的角色ID列表")


class UserUpdate(BaseModel):
    """更新用户"""
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    username: Optional[str] = None


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    status: int
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True
