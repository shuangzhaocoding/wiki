"""
资源申请记录模型（用于站内消息通知审核人）
"""
import json
from tortoise.models import Model
from tortoise import fields


class ResourceApplication(Model):
    """资源申请表"""
    id = fields.BigIntField(pk=True)
    applicant = fields.ForeignKeyField(
        "models.User",
        related_name="resource_applications",
        description="申请人",
    )
    resource_type = fields.IntField(
        description="资源类型：1-团队空间，2-知识库，3-文章",
    )
    resource_id = fields.BigIntField(description="资源ID")
    applied_role = fields.IntField(
        default=1,
        description="申请的角色：0-只读，1-编辑者，2-管理员",
    )
    message = fields.TextField(null=True, description="申请说明/备注")
    reviewer_ids = fields.JSONField(
        null=True,
        description="审核人ID列表（JSON数组），用于站内消息通知",
    )
    status = fields.IntField(
        default=0,
        description="状态：0-待审核，1-已同意，2-已拒绝",
    )
    reply_message = fields.TextField(null=True, description="审核回复说明")
    replied_at = fields.DatetimeField(null=True, description="审核时间")
    replied_by_id = fields.BigIntField(null=True, description="审核人ID")
    created_at = fields.DatetimeField(auto_now_add=True, description="申请时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "resource_applications"
        table_description = "资源申请记录表"

    def __str__(self):
        return f"Application {self.id} ({self.resource_type}/{self.resource_id})"
