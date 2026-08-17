"""
角色模型
"""
from tortoise.models import Model
from tortoise import fields


class Role(Model):
    """角色表"""
    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description="角色名称")
    code = fields.CharField(max_length=50, unique=True, description="角色代码（唯一标识）")
    description = fields.TextField(null=True, description="角色描述")
    permissions = fields.JSONField(default=list, description="角色权限ID列表（JSON数组），如：[1, 2, 3]")
    status = fields.IntField(default=1, description="状态：0-禁用，1-启用")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "roles"
        table_description = "角色表"

    def __str__(self):
        return self.name


class UserRole(Model):
    """用户-角色关联表"""
    id = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="user_roles", description="用户")
    role = fields.ForeignKeyField("models.Role", related_name="user_roles", description="角色")
    status = fields.IntField(default=1, description="状态：0-已移除，1-有效")
    assigned_by = fields.ForeignKeyField("models.User", related_name="assigned_user_roles", null=True, description="分配人")
    assigned_at = fields.DatetimeField(auto_now_add=True, description="分配时间")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "user_roles"
        table_description = "用户-角色关联表"
        unique_together = (("user", "role"),)

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"
