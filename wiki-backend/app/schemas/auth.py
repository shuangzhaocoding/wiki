"""
认证相关的Schema
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    password: str
    email: EmailStr
    email_code: str
    nickname: Optional[str] = None


class SendRegisterCodeRequest(BaseModel):
    """发送注册验证码请求"""
    email: EmailStr


class SendResetPasswordCodeRequest(BaseModel):
    """发送重置密码验证码请求"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    email: EmailStr
    email_code: str
    new_password: str


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    status: int

    class Config:
        from_attributes = True
