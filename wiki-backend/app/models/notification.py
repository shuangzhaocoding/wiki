"""
站内消息通知模型
"""
from tortoise.models import Model
from tortoise import fields


class Notification(Model):
    """站内消息通知表"""
    id = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField(
        "models.User",
        related_name="notifications",
        description="接收人",
    )
    type = fields.CharField(
        max_length=50,
        description="通知类型，如：reading_task_assigned、reading_task_reminder",
    )
    title = fields.CharField(max_length=255, description="标题")
    content = fields.CharField(
        max_length=500,
        null=True,
        description="内容描述",
    )
    link = fields.CharField(
        max_length=500,
        null=True,
        description="跳转链接（前端点击后跳转的 URL）",
    )
    is_read = fields.IntField(
        default=0,
        description="是否已读：0-未读，1-已读",
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "notifications"
        table_description = "站内消息通知表"

    def __str__(self) -> str:
        return f"Notification {self.id} -> user {self.user_id} ({self.type})"
