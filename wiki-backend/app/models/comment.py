"""
评论模型
"""
from tortoise.models import Model
from tortoise import fields


class Comment(Model):
    """评论表"""
    id = fields.BigIntField(pk=True)
    article = fields.ForeignKeyField("models.Article", related_name="comments", description="文章")
    user = fields.ForeignKeyField("models.User", related_name="comments", description="评论者")
    parent = fields.ForeignKeyField("models.Comment", related_name="replies", null=True, description="父评论")
    first_comment = fields.ForeignKeyField("models.Comment", related_name="thread_comments", null=True, description="一级评论（根评论）")
    reply_to_user = fields.ForeignKeyField("models.User", related_name="replied_comments", null=True, description="被回复的用户")
    content = fields.TextField(description="评论内容")
    like_count = fields.IntField(default=0, description="点赞数")
    dislike_count = fields.IntField(default=0, description="踩数")
    status = fields.IntField(default=1, description="状态：0-已删除，1-正常")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "comments"
        table_description = "评论表"


class CommentReaction(Model):
    """评论点赞/踩记录表。同一用户对同一条评论只能有一种反应：点赞或踩，互斥。"""
    id = fields.BigIntField(pk=True)
    comment = fields.ForeignKeyField("models.Comment", related_name="reactions", description="评论")
    user = fields.ForeignKeyField("models.User", related_name="comment_reactions", description="用户")
    action_type = fields.IntField(description="1-点赞，2-踩")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "comment_reactions"
        table_description = "评论点赞踩记录表"
        unique_together = (("comment", "user"),)

    def __str__(self):
        return f"comment={self.comment_id} user={self.user_id} type={self.action_type}"
