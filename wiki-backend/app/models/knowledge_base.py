"""
知识库模型
"""
from tortoise.models import Model
from tortoise import fields


class KnowledgeBase(Model):
    """知识库表"""
    id = fields.BigIntField(pk=True)
    team_space = fields.ForeignKeyField("models.TeamSpace", related_name="knowledge_bases", description="所属团队空间")
    name = fields.CharField(max_length=100, description="知识库名称")
    description = fields.TextField(null=True, description="描述")
    owner = fields.ForeignKeyField("models.User", related_name="owned_knowledge_bases", description="创建者")
    visibility = fields.IntField(default=1, description="可见性：1-个人可见，2-团队成员可见，3-公开可见")
    icon = fields.CharField(max_length=50, null=True, description="图标")
    sort_order = fields.IntField(default=0, description="排序顺序")
    status = fields.IntField(default=1, description="状态：0-已删除，1-正常")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "knowledge_bases"
        table_description = "知识库表"

    def __str__(self):
        return self.name


class KnowledgeBaseMember(Model):
    """知识库成员表（记录知识库的成员可见性）"""
    id = fields.BigIntField(pk=True)
    knowledge_base = fields.ForeignKeyField("models.KnowledgeBase", related_name="members", description="知识库")
    user = fields.ForeignKeyField("models.User", related_name="knowledge_base_memberships", description="用户")
    role = fields.IntField(default=0, description="角色：0-只读，1-编辑者，2-管理员")
    joined_at = fields.DatetimeField(auto_now_add=True, description="加入时间")
    status = fields.IntField(default=1, description="状态：0-已移除，1-正常")
    added_by = fields.ForeignKeyField("models.User", related_name="added_kb_members", null=False, description="添加人")

    class Meta:
        table = "knowledge_base_members"
        table_description = "知识库成员表"
        unique_together = (("knowledge_base", "user"),)

    def __str__(self):
        return f"{self.user.username} in {self.knowledge_base.name}"
