"""
业务枚举（整型值与数据库/API 约定一致）。
"""
from enum import IntEnum


class ResourceType(IntEnum):
    """资源类型：1-团队空间，2-知识库，3-文章"""

    TEAM_SPACE = 1
    KNOWLEDGE_BASE = 2
    ARTICLE = 3


class ArticleNodeType(IntEnum):
    """文章树节点类型：1-文章，2-目录"""

    ARTICLE = 1
    DIRECTORY = 2


class ApplicationStatus(IntEnum):
    """资源申请状态：0-待审核，1-已同意，2-已拒绝"""

    PENDING = 0
    APPROVED = 1
    REJECTED = 2


# 角色
class PermissionType(IntEnum):
    """权限类型：0-只读，1-可编辑，2-管理员"""
    READ = 0
    EDIT = 1
    ADMIN = 2