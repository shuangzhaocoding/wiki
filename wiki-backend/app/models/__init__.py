"""
数据库模型
"""
from app.models.user import User
from app.models.team_space import TeamSpace, TeamMember
from app.models.knowledge_base import KnowledgeBase, KnowledgeBaseMember
from app.models.article import (
    Article,
    ArticleVersion,
    Tag,
    ArticleTag,
    ArticleInteraction,
    ArticleStats,
    ArticleFeedback,
    ArticleMember,
)
from app.models.permission import Permission
from app.models.comment import Comment, CommentReaction
from app.models.file import File
from app.models.application import ResourceApplication
from app.models.role import Role, UserRole
from app.models.system_permission import SystemPermission
from app.models.banner import Banner
from app.models.reading_task import ReadingTaskBatch, ReadingTask
from app.models.notification import Notification

__all__ = [
    "User",
    "TeamSpace",
    "TeamMember",
    "KnowledgeBase",
    "KnowledgeBaseMember",
    "Article",
    "ArticleVersion",
    "Tag",
    "ArticleTag",
    "ArticleInteraction",
    "ArticleStats",
    "ArticleFeedback",
    "ArticleMember",
    "Permission",
    "Comment",
    "CommentReaction",
    "File",
    "ResourceApplication",
    "Role",
    "UserRole",
    "SystemPermission",
    "Banner",
    "ReadingTaskBatch",
    "ReadingTask",
    "Notification",
]
