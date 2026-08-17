"""
权限模型
"""
from tortoise.models import Model
from tortoise import fields


class Permission(Model):
    """权限表"""
    id = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="permissions", description="用户")
    resource_type = fields.IntField(description="资源类型：1-团队空间，2-知识库，3-文章")
    resource_id = fields.BigIntField(description="资源ID")
    permission_type = fields.IntField(description="权限类型：1-只读，2-可编辑，3-管理员")
    granted_by = fields.ForeignKeyField("models.User", related_name="granted_permissions", null=True, description="授权人")
    granted_at = fields.DatetimeField(auto_now_add=True, description="授权时间")
    expires_at = fields.DatetimeField(null=True, description="过期时间")
    status = fields.IntField(default=1, description="状态：0-已撤销，1-有效")

    class Meta:
        table = "permissions"
        table_description = "权限表"
        unique_together = (("user", "resource_type", "resource_id"),)

    def __str__(self):
        return f"{self.user.username} - {self.resource_type}:{self.resource_id}"
