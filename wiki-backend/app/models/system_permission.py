"""
系统权限定义模型
"""
from tortoise.models import Model
from tortoise import fields


class SystemPermission(Model):
    """系统权限定义表"""
    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=100, unique=True, description="权限名称")
    code = fields.CharField(max_length=100, unique=True, description="权限代码（唯一标识），如：create_user")
    description = fields.TextField(null=True, description="权限描述")
    category = fields.CharField(max_length=50, null=True, description="权限分类，如：user, article, team_space")
    status = fields.IntField(default=1, description="状态：0-禁用，1-启用")
    sort_order = fields.IntField(default=0, description="排序顺序")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "system_permissions"
        table_description = "系统权限定义表"

    def __str__(self):
        return self.name
