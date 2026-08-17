"""
用户模型
"""
from tortoise.models import Model
from tortoise import fields


class User(Model):
    """用户表"""
    id = fields.BigIntField(pk=True)
    username = fields.CharField(max_length=50, description="用户名")
    password = fields.CharField(max_length=255, description="密码（加密）")
    email = fields.CharField(max_length=100, unique=True, null=True, description="邮箱")
    nickname = fields.CharField(max_length=50, null=True, description="昵称")
    avatar = fields.CharField(max_length=255, null=True, description="头像URL")
    status = fields.IntField(default=1, description="状态：0-禁用，1-启用")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    last_login_at = fields.DatetimeField(null=True, description="最后登录时间")

    class Meta:
        table = "users"
        table_description = "用户表"

    def __str__(self):
        return self.username
