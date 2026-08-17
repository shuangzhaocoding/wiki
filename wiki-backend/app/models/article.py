"""
文章模型
"""
from tortoise.models import Model
from tortoise import fields

from app.enums import ArticleNodeType


class Article(Model):
    """文章表"""
    id = fields.BigIntField(pk=True)
    knowledge_base = fields.ForeignKeyField("models.KnowledgeBase", related_name="articles", description="所属知识库")
    parent = fields.ForeignKeyField("models.Article", related_name="children", null=True, description="父文章")
    node_type = fields.IntField(
        default=ArticleNodeType.ARTICLE.value,
        description="节点类型：1-文章，2-目录",
    )
    title = fields.CharField(max_length=200, description="文章标题")
    content = fields.TextField(null=True, description="文章内容")
    summary = fields.CharField(max_length=500, null=True, description="摘要")
    author = fields.ForeignKeyField("models.User", related_name="articles", description="作者")
    visibility = fields.IntField(default=1, description="可见性：1-个人可见，2-团队成员可见，3-公开可见")
    sort_order = fields.IntField(default=0, description="排序顺序，在父级目录下的显示顺序")
    status = fields.IntField(default=1, description="状态：0-已删除，1-草稿，2-已发布")
    is_original = fields.BooleanField(default=False, description="是否原创")
    is_ai_generated = fields.BooleanField(default=False, description="是否AI生成")
    published_at = fields.DatetimeField(null=True, description="发布时间")
    updated_by = fields.ForeignKeyField("models.User", related_name="updated_articles", null=True, description="最后更新人")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "articles"
        table_description = "文章表"

    def __str__(self):
        return self.title


class ArticleVersion(Model):
    """文章版本历史表"""
    id = fields.BigIntField(pk=True)
    article = fields.ForeignKeyField("models.Article", related_name="versions", description="文章")
    version = fields.IntField(description="版本号")
    title = fields.CharField(max_length=200, description="标题")
    content = fields.TextField(null=True, description="内容")
    author = fields.ForeignKeyField("models.User", related_name="article_versions", description="编辑者")
    change_log = fields.TextField(null=True, description="变更说明")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "article_versions"
        table_description = "文章版本历史表"

    def __str__(self):
        return f"{self.article.title} v{self.version}"


class Tag(Model):
    """标签表"""
    id = fields.BigIntField(pk=True)
    knowledge_base = fields.ForeignKeyField(
        "models.KnowledgeBase",
        related_name="tags",
        description="所属知识库",
    )
    name = fields.CharField(max_length=50, description="标签名称")
    color = fields.CharField(max_length=20, null=True, description="标签颜色")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "tags"
        table_description = "标签表"
        unique_together = (("knowledge_base", "name"),)

    def __str__(self):
        return self.name


class ArticleTag(Model):
    """文章标签关联表"""
    id = fields.BigIntField(pk=True)
    article = fields.ForeignKeyField("models.Article", related_name="article_tags", description="文章")
    tag = fields.ForeignKeyField("models.Tag", related_name="article_tags", description="标签")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "article_tags"
        table_description = "文章标签关联表"
        unique_together = (("article", "tag"),)

    def __str__(self):
        return f"{self.article.title} - {self.tag.name}"


class ArticleInteraction(Model):
    """文章交互记录表（记录用户的点赞、收藏、浏览等行为）"""
    id = fields.BigIntField(pk=True)
    article = fields.ForeignKeyField("models.Article", related_name="interactions", description="文章")
    user = fields.ForeignKeyField("models.User", related_name="article_interactions", description="用户")
    action_type = fields.IntField(description="操作类型：1-点赞，2-取消点赞，3-收藏，4-取消收藏，5-浏览")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "article_interactions"
        table_description = "文章交互记录表"
        indexes = (("article", "user", "action_type"),)

    def __str__(self):
        action_map = {1: "点赞", 2: "取消点赞", 3: "收藏", 4: "取消收藏", 5: "浏览"}
        return f"{self.user_id} - {action_map.get(self.action_type, '未知')} - {self.article_id}"


class ArticleStats(Model):
    """文章统计表（记录文章的统计数据）"""
    id = fields.BigIntField(pk=True)
    article = fields.OneToOneField("models.Article", related_name="stats", description="文章")
    view_count = fields.IntField(default=0, description="浏览次数")
    like_count = fields.IntField(default=0, description="点赞数")
    collect_count = fields.IntField(default=0, description="收藏数")
    comment_count = fields.IntField(default=0, description="评论数")
    share_count = fields.IntField(default=0, description="分享数")
    feedback_count = fields.IntField(default=0, description="反馈数")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "article_stats"
        table_description = "文章统计表"

    def __str__(self):
        return f"Stats for article {self.article_id}"


class ArticleFeedback(Model):
    """文章反馈表"""
    id = fields.BigIntField(pk=True)
    article = fields.ForeignKeyField("models.Article", related_name="feedbacks", description="文章")
    user = fields.ForeignKeyField("models.User", related_name="article_feedbacks", description="反馈用户")
    feedback_type = fields.IntField(description="反馈类型：1-错误报告，2-内容建议，3-格式问题，4-其他")
    content = fields.TextField(description="反馈内容")
    status = fields.IntField(default=1, description="状态：0-已删除，1-待处理，2-处理中，3-已处理，4-已关闭")
    reply = fields.TextField(null=True, description="管理员回复")
    reply_by = fields.ForeignKeyField("models.User", related_name="replied_feedbacks", null=True, description="回复人")
    reply_at = fields.DatetimeField(null=True, description="回复时间")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "article_feedbacks"
        table_description = "文章反馈表"

    def __str__(self):
        feedback_type_map = {1: "错误报告", 2: "内容建议", 3: "格式问题", 4: "其他"}
        return f"{self.user_id} - {feedback_type_map.get(self.feedback_type, '未知')} - {self.article_id}"


class ArticleMember(Model):
    """文章成员表（记录文章的成员可见性）"""
    id = fields.BigIntField(pk=True)
    article = fields.ForeignKeyField("models.Article", related_name="members", description="文章")
    user = fields.ForeignKeyField("models.User", related_name="article_memberships", description="用户")
    role = fields.IntField(default=0, description="角色：0-只读，1-编辑者，2-管理员")
    joined_at = fields.DatetimeField(auto_now_add=True, description="加入时间")
    status = fields.IntField(default=1, description="状态：0-已移除，1-正常")
    added_by = fields.ForeignKeyField("models.User", related_name="added_article_members", null=False, description="添加人")

    class Meta:
        table = "article_members"
        table_description = "文章成员表"
        unique_together = (("article", "user"),)

    def __str__(self):
        return f"{self.user.username} in {self.article.title}"
