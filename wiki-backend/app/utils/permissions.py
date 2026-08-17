"""
权限检查工具函数
"""
from typing import NamedTuple, Optional

from app.enums import ResourceType
from app.models.user import User
from app.models.team_space import TeamMember, TeamSpace
from app.models.article import Article, ArticleMember
from app.models.knowledge_base import KnowledgeBase, KnowledgeBaseMember


class PermissionCheckResult(NamedTuple):
    """权限检查结果：是否满足所需权限，以及在该资源上的有效角色（含向上继承）。"""

    allowed: bool
    role: Optional[int]  # 0-只读, 1-编辑, 2-管理员；无任何访问时为 None


def _max_role(a: Optional[int], b: Optional[int]) -> Optional[int]:
    if a is None:
        return b
    if b is None:
        return a
    return max(a, b)


def max_effective_role(a: Optional[int], b: Optional[int]) -> Optional[int]:
    """合并两个层级上的角色（取较大），与资源权限继承规则一致。"""
    return _max_role(a, b)


async def _local_role_team_space(user: User, team_space_id: int) -> Optional[int]:
    """用户在该团队空间上的直接角色（不向上查找）。"""
    team_space = await TeamSpace.get_or_none(id=team_space_id, status=1)
    if not team_space:
        return None

    if team_space.visibility == 1:
        return 2 if team_space.owner_id == user.id else None
    if team_space.visibility == 2:
        if team_space.owner_id == user.id:
            return 2
        team_member = await TeamMember.get_or_none(
            team_space_id=team_space_id,
            user_id=user.id,
            status=1,
        )
        return team_member.role if team_member else None
    if team_space.visibility == 3:
        if team_space.owner_id == user.id:
            return 2
        team_member = await TeamMember.get_or_none(
            team_space_id=team_space_id,
            user_id=user.id,
            status=1,
        )
        return team_member.role if team_member else 0
    return None


async def _local_role_knowledge_base(user: User, kb: KnowledgeBase) -> Optional[int]:
    """用户在该知识库上的直接角色（不向上查找）。"""
    kb_id = kb.id
    if kb.visibility == 1:
        return 2 if kb.owner_id == user.id else None
    if kb.visibility == 2:
        if kb.owner_id == user.id:
            return 2
        kb_member = await KnowledgeBaseMember.get_or_none(
            knowledge_base_id=kb_id,
            user_id=user.id,
            status=1,
        )
        return kb_member.role if kb_member else None
    if kb.visibility == 3:
        if kb.owner_id == user.id:
            return 2
        kb_member = await KnowledgeBaseMember.get_or_none(
            knowledge_base_id=kb_id,
            user_id=user.id,
            status=1,
        )
        return kb_member.role if kb_member else 0
    return None


async def _local_role_article(user: User, article: Article) -> Optional[int]:
    """用户在该文章上的直接角色（不向上查找）。"""
    resource_id = article.id
    if article.visibility == 1:
        return 2 if article.author_id == user.id else None
    if article.visibility == 2:
        if article.author_id == user.id:
            return 2
        article_member = await ArticleMember.get_or_none(
            article_id=resource_id,
            user_id=user.id,
            status=1,
        )
        return article_member.role if article_member else None
    if article.visibility == 3:
        if article.author_id == user.id:
            return 2
        article_member = await ArticleMember.get_or_none(
            article_id=resource_id,
            user_id=user.id,
            status=1,
        )
        return article_member.role if article_member else 0
    return None


async def _effective_role_team_space(user: User, team_space_id: int) -> Optional[int]:
    """团队空间上的有效角色（无父级）。"""
    return await _local_role_team_space(user, team_space_id)


async def _effective_role_knowledge_base(user: User, kb: KnowledgeBase) -> Optional[int]:
    """知识库上的有效角色（个人库不继承团队；成员/公共可向上合并团队空间角色）。"""
    local = await _local_role_knowledge_base(user, kb)
    if kb.visibility == 1:
        return local
    parent = await _effective_role_team_space(user, kb.team_space_id)
    return _max_role(local, parent)


async def _effective_role_article(user: User, article: Article) -> Optional[int]:
    """文章上的有效角色（个人文章不继承；成员/公共可向上合并知识库→团队空间）。"""
    local = await _local_role_article(user, article)
    if article.visibility == 1:
        return local
    kb = await KnowledgeBase.get_or_none(id=article.knowledge_base_id, status=1)
    if not kb:
        return local
    parent = await _effective_role_knowledge_base(user, kb)
    return _max_role(local, parent)


async def get_effective_role(
    user: User,
    resource_type: int,
    resource_id: int,
) -> Optional[int]:
    """解析用户在指定资源上的有效角色（含层级继承），与 check_user_permission 一致。"""
    return await _effective_role_for_resource(user, resource_type, resource_id)


async def _effective_role_for_resource(
    user: User,
    resource_type: int,
    resource_id: int,
) -> Optional[int]:
    """解析用户在指定资源上的有效角色（含层级继承）。"""
    if resource_type == ResourceType.TEAM_SPACE:
        return await _effective_role_team_space(user, resource_id)

    if resource_type == ResourceType.KNOWLEDGE_BASE:
        kb = await KnowledgeBase.get_or_none(id=resource_id, status=1)
        if not kb:
            return None
        return await _effective_role_knowledge_base(user, kb)

    if resource_type == ResourceType.ARTICLE:
        article = await Article.get_or_none(id=resource_id, status__gt=0)
        if not article:
            return None
        return await _effective_role_article(user, article)

    return None


async def check_user_permission(
    user: User,
    resource_type: int,
    resource_id: int,
    required_permission: int = 0,  # 0-只读, 1-可编辑, 2-管理员
) -> PermissionCheckResult:
    """
    检查用户对资源的权限，并返回有效角色。

    resource_type: 1-团队空间, 2-知识库, 3-文章
    required_permission: 0-只读, 1-可编辑, 2-管理员

    权限校验规则：
    1. 检查资源可见性：
       - visibility=1（个人）：只有创建者/作者可访问
       - visibility=2（成员）：创建者/作者 + 成员列表中的用户可访问
       - visibility=3（公共）：所有人可访问（只读）
    2. 检查角色权限：
       - role=0（只读）：只能阅读
       - role=1（编辑者）：可修改编辑
       - role=2（管理员）：可随意操作，包括删除
    3. 向上级联：将子资源上的直接角色与父资源上的有效角色取较大值（文章→知识库→团队空间；
       知识库→团队空间）。个人可见（visibility=1）的资源不向父级继承。
    """
    role = await _effective_role_for_resource(user, resource_type, resource_id)
    allowed = role is not None and role >= required_permission
    return PermissionCheckResult(allowed, role)


async def require_permission(
    user: User,
    resource_type: int,
    resource_id: int,
    required_permission: int = 0,  # 0-只读, 1-可编辑, 2-管理员
) -> PermissionCheckResult:
    """要求权限，没有权限则抛出异常；成功时返回检查结果（含 role）。"""
    from fastapi import HTTPException, status

    result = await check_user_permission(
        user, resource_type, resource_id, required_permission
    )
    if not result.allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足",
        )
    return result