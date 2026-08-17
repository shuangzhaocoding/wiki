"""
知识库标签 Schema
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    """创建标签"""

    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    color: Optional[str] = Field(None, max_length=20, description="标签颜色")


class TagUpdate(BaseModel):
    """更新标签"""

    name: Optional[str] = Field(None, min_length=1, max_length=50, description="标签名称")
    color: Optional[str] = Field(None, max_length=20, description="标签颜色；传空字符串可清空颜色")


class TagResponse(BaseModel):
    """标签响应"""

    id: int
    knowledge_base_id: int
    name: str
    color: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
