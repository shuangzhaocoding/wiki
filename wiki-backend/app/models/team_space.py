"""
团队空间模型
"""
from tortoise.models import Model
from tortoise import fields


class TeamSpace(Model):
    """团队空间表"""
    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=100, description="团队空间名称")
    description = fields.TextField(null=True, description="描述")
    owner_id = fields.BigIntField(description="创建者ID")
    visibility = fields.IntField(default=1, description="可见性：1-个人可见，2-团队成员可见，3-公开可见")
    cover_image = fields.CharField(max_length=255, null=True, description="封面图URL")
    status = fields.IntField(default=1, description="状态：0-已删除，1-正常")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "team_spaces"
        table_description = "团队空间表"

    def __str__(self):
        return self.name


class TeamMember(Model):
    """团队成员表"""
    id = fields.BigIntField(pk=True)
    team_space = fields.ForeignKeyField("models.TeamSpace", related_name="members", description="团队空间")
    user = fields.ForeignKeyField("models.User", related_name="team_memberships", description="用户")
    role = fields.IntField(default=0, description="角色：0-只读，1-编辑者，2-管理员")
    joined_at = fields.DatetimeField(auto_now_add=True, description="加入时间")
    status = fields.IntField(default=1, description="状态：0-已移除，1-正常")
    added_by = fields.ForeignKeyField("models.User", related_name="added_team_members", null=False, description="添加人")

    class Meta:
        table = "team_members"
        table_description = "团队成员表"
        unique_together = (("team_space", "user"),)

    def __str__(self):
        return f"{self.user.username} in {self.team_space.name}"
