"""
统一响应格式
"""
from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应格式"""
    code: int
    data: Optional[T] = None
    message: str = "请求成功"

    class Config:
        from_attributes = True


def success_response(data: Any = None, message: str = "请求成功") -> dict:
    """成功响应"""
    return {
        "code": 200,
        "data": data,
        "message": message
    }


def error_response(code: int, message: str, data: Any = None) -> dict:
    """错误响应"""
    return {
        "code": code,
        "data": data,
        "message": message
    }
