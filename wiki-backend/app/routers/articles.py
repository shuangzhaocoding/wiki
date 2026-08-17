"""
文章相关路由
"""
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from tortoise import Tortoise
from tortoise.expressions import F, Q
from tortoise.transactions import in_transaction
from app.enums import ArticleNodeType, PermissionType, ResourceType
from app.models.user import User
from app.models.role import Role, UserRole
from app.models.article import (
    Article,
    ArticleVersion,
    ArticleInteraction,
    ArticleStats,
    ArticleFeedback,
    ArticleMember,
    Tag,
    ArticleTag,
)
from app.models.file import File
from app.models.knowledge_base import KnowledgeBase, KnowledgeBaseMember
from app.models.team_space import TeamSpace, TeamMember
from app.models.notification import Notification
from app.core.dependencies import get_current_active_user
from app.core.response import success_response, error_response
from app.schemas.user import UserResponse
from app.utils.permissions import get_effective_role, max_effective_role, require_permission

router = APIRouter()


class ArticleCreate(BaseModel):
    knowledge_base_id: int
    parent_id: Optional[int] = None
    node_type: int = Field(
        ArticleNodeType.ARTICLE,
        description="节点类型：1-文章，2-目录",
    )
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    visibility: Optional[int] = None  # 默认继承知识库
    status: int = 1  # 1-草稿，2-已发布
    after_article_id: Optional[int] = None  # 插入到该兄弟节点之后；为空则排在同级第一位。须为同知识库、同父下的文章 ID
    is_original: bool = True
    is_ai_generated: bool = False
    tag_ids: Optional[List[int]] = Field(
        default=None,
        description="标签 ID 列表，须均为当前知识库下的标签；不传或空列表表示不关联标签",
    )


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    node_type: Optional[int] = Field(None, description="节点类型：1-文章，2-目录")
    content: Optional[str] = None
    summary: Optional[str] = None
    visibility: Optional[int] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None  # 排序顺序，在父级目录下的显示顺序
    status: Optional[int] = None
    is_original: Optional[bool] = None
    is_ai_generated: Optional[bool] = None
    tag_ids: Optional[List[int]] = Field(
        default=None,
        description="标签 ID 列表；请求体中包含本字段时全文替换（可为空列表表示清空），不传则保持原标签不变",
    )


class ChildPositionUpdate(BaseModel):
    """按前端事件类型移动节点；inner=作为 target 子节点（排在子节点末位），before=插到 target 前，after=插到 target 后，none=不操作"""
    event_type: Literal["inner", "before", "after", "none"]
    target_node_id: Optional[int] = None  # inner/before/after 时必填


class ArticleMemberAdd(BaseModel):
    user_id: Optional[int] = None  # 单个用户；与 role_ids 至少传一种
    role_ids: Optional[List[int]] = None  # 系统角色 ID 列表，将拥有这些角色的全部用户加入文章
    role: int = Field(1, description="文章成员角色：0-只读，1-编辑者，2-管理员")


class ArticleMemberBatchRemove(BaseModel):
    """按系统角色批量移除：移除本文章中、且拥有指定系统角色的成员（文章作者不会被移除）"""
    role_ids: List[int] = Field(..., min_length=1, description="系统角色 ID 列表")


class ArticleMemberUpdate(BaseModel):
    role: int  # 角色：0-只读，1-编辑者，2-管理员


class ArticleResponse(BaseModel):
    id: int
    knowledge_base_id: int
    parent_id: Optional[int] = None
    node_type: int = Field(ArticleNodeType.ARTICLE, description="节点类型：1-文章，2-目录")
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    author_id: int
    author_name: Optional[str] = None  # 作者用户名或昵称
    updated_by_id: Optional[int] = None  # 最后更新人ID
    updated_by_name: Optional[str] = None  # 最后更新人用户名或昵称
    visibility: int
    sort_order: int
    status: int
    is_original: bool = True
    is_ai_generated: bool = False
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    my_role: Optional[int] = None  # 当前用户在此文章的有效角色：0-只读，1-编辑者，2-管理员（列表/树节点）
    tag_ids: Optional[List[int]] = None  # 标签 ID，与 tag_names 顺序一致
    tag_names: Optional[List[str]] = None  # 标签名称列表

    class Config:
        from_attributes = True


async def _batch_article_tag_maps(
    article_ids: List[int],
) -> tuple[dict[int, List[int]], dict[int, List[str]]]:
    """批量：文章 ID -> (tag_ids, tag_names)，顺序与 ArticleTag 表记录顺序一致。"""
    if not article_ids:
        return {}, {}
    rows = (
        await ArticleTag.filter(article_id__in=article_ids)
        .select_related("tag")
        .order_by("article_id", "id")
    )
    ids_by: dict[int, List[int]] = defaultdict(list)
    names_by: dict[int, List[str]] = defaultdict(list)
    for at in rows:
        if at.tag_id and at.tag is not None:
            ids_by[at.article_id].append(at.tag_id)
            names_by[at.article_id].append(at.tag.name)
    return dict(ids_by), dict(names_by)


@router.get(
    "/recent-created",
    summary="最近7天新添加的公开文章",
    description="获取最近7天内新创建的、已发布且公开可见的文章，按创建时间倒序取前10条。",
)
async def get_recent_created_articles(
    current_user: User = Depends(get_current_active_user),
):
    """
    最近7天新添加的10条公开文章（status=2, visibility=3）。
    """
    since = datetime.utcnow() - timedelta(days=30)
    articles = (
        await Article.filter(
            status__not=0,  # 已发布
            visibility=3,  # 公开可见
            created_at__gte=since,
        )
        .order_by("-created_at")
        .limit(10)
        .all()
    )

    author_ids = list({a.author_id for a in articles})
    authors_map = {}
    if author_ids:
        authors = await User.filter(id__in=author_ids).all()
        authors_map = {u.id: (u.nickname or u.username) for u in authors}

    aid_list = [a.id for a in articles]
    tag_ids_map, tag_names_map = await _batch_article_tag_maps(aid_list)

    items = [
        {
            "id": a.id,
            "knowledge_base_id": a.knowledge_base_id,
            "node_type": a.node_type,
            "title": a.title,
            "summary": a.summary,
            "author_id": a.author_id,
            "author": authors_map.get(a.author_id),
            "visibility": a.visibility,
            "status": a.status,
            "is_original": a.is_original,
            "is_ai_generated": a.is_ai_generated,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "updated_at": a.updated_at.isoformat() if a.updated_at else None,
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "tag_ids": tag_ids_map.get(a.id, []),
            "tag_names": tag_names_map.get(a.id, []),
        }
        for a in articles
    ]

    return success_response(data=items, message="获取成功")


@router.get(
    "/recent-updated",
    summary="最近7天新更新的公开文章",
    description="获取最近7天内有更新的、已发布且公开可见的文章，按更新时间倒序取前10条。",
)
async def get_recent_updated_articles(
    current_user: User = Depends(get_current_active_user),
):
    """
    最近7天新更新的10条公开文章（status=2, visibility=3）。
    """
    since = datetime.utcnow() - timedelta(days=30)
    articles = (
        await Article.filter(
            status__not=0,  # 已发布
            visibility=3,  # 公开可见
            updated_at__gte=since,
        )
        .order_by("-updated_at")
        .limit(10)
        .all()
    )

    author_ids = list({a.author_id for a in articles})
    authors_map = {}
    if author_ids:
        authors = await User.filter(id__in=author_ids).all()
        authors_map = {u.id: (u.nickname or u.username) for u in authors}

    aid_list = [a.id for a in articles]
    tag_ids_map, tag_names_map = await _batch_article_tag_maps(aid_list)

    items = [
        {
            "id": a.id,
            "knowledge_base_id": a.knowledge_base_id,
            "node_type": a.node_type,
            "title": a.title,
            "summary": a.summary,
            "author_id": a.author_id,
            "author": authors_map.get(a.author_id),
            "visibility": a.visibility,
            "status": a.status,
            "is_original": a.is_original,
            "is_ai_generated": a.is_ai_generated,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "updated_at": a.updated_at.isoformat() if a.updated_at else None,
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "tag_ids": tag_ids_map.get(a.id, []),
            "tag_names": tag_names_map.get(a.id, []),
        }
        for a in articles
    ]

    return success_response(data=items, message="获取成功")


def _siblings_filter(knowledge_base_id: int, parent_id: Optional[int]) -> dict:
    q = {"knowledge_base_id": knowledge_base_id, "status__gt": 0}
    if parent_id is None:
        q["parent_id__isnull"] = True
    else:
        q["parent_id"] = parent_id
    return q


async def _resolve_article_my_role(article: Article, current_user: User) -> int:
    """当前用户在此文章内的有效角色：0-只读，1-编辑者，2-管理员（与 app.utils.permissions 向上继承一致）。"""
    r = await get_effective_role(current_user, ResourceType.ARTICLE, article.id)
    return r if r is not None else 0


def _local_team_space_role_from_maps(
    ts: Optional[TeamSpace], uid: int, tm_map: dict[int, int]
) -> Optional[int]:
    """与 permissions._local_role_team_space 一致（批量用内存表）。"""
    if not ts:
        return None
    if ts.visibility == 1:
        return 2 if ts.owner_id == uid else None
    if ts.visibility == 2:
        if ts.owner_id == uid:
            return 2
        return tm_map.get(ts.id)
    if ts.visibility == 3:
        if ts.owner_id == uid:
            return 2
        return tm_map.get(ts.id) if ts.id in tm_map else 0
    return None


def _local_kb_role_from_maps(kb: KnowledgeBase, uid: int, kb_mem_map: dict[int, int]) -> Optional[int]:
    """与 permissions._local_role_knowledge_base 一致。"""
    if kb.visibility == 1:
        return 2 if kb.owner_id == uid else None
    if kb.visibility == 2:
        if kb.owner_id == uid:
            return 2
        return kb_mem_map.get(kb.id)
    if kb.visibility == 3:
        if kb.owner_id == uid:
            return 2
        return kb_mem_map.get(kb.id) if kb.id in kb_mem_map else 0
    return None


def _kb_effective_from_maps(
    kb: KnowledgeBase,
    uid: int,
    kb_mem_map: dict[int, int],
    ts_map: dict[int, TeamSpace],
    tm_map: dict[int, int],
) -> Optional[int]:
    """与 permissions._effective_role_knowledge_base 一致。"""
    lr = _local_kb_role_from_maps(kb, uid, kb_mem_map)
    if kb.visibility == 1:
        return lr
    ts = ts_map.get(kb.team_space_id)
    pr = _local_team_space_role_from_maps(ts, uid, tm_map)
    return max_effective_role(lr, pr)


def _local_article_role_from_maps(a: Article, uid: int, am_map: dict[int, int]) -> Optional[int]:
    """与 permissions._local_role_article 一致。"""
    if a.visibility == 1:
        return 2 if a.author_id == uid else None
    if a.visibility == 2:
        if a.author_id == uid:
            return 2
        return am_map.get(a.id)
    if a.visibility == 3:
        if a.author_id == uid:
            return 2
        return am_map.get(a.id) if a.id in am_map else 0
    return None


def _article_effective_from_maps(
    a: Article,
    uid: int,
    am_map: dict[int, int],
    kb_eff_map: dict[int, Optional[int]],
) -> int:
    """与 permissions._effective_role_article 一致；无权限时返回 0。"""
    loc = _local_article_role_from_maps(a, uid, am_map)
    if a.visibility == 1:
        eff = loc
    else:
        ke = kb_eff_map.get(a.knowledge_base_id)
        eff = max_effective_role(loc, ke)
    return eff if eff is not None else 0


async def _batch_article_my_roles(articles: List[Article], current_user: User) -> dict:
    """批量计算当前用户在每篇文章中的有效角色 article_id -> 0/1/2，与 get_effective_role(ARTICLE) 一致。"""
    if not articles:
        return {}
    uid = current_user.id
    article_ids = [a.id for a in articles]
    kb_ids = list({a.knowledge_base_id for a in articles})

    am_rows = await ArticleMember.filter(
        article_id__in=article_ids, user_id=uid, status=1
    ).values_list("article_id", "role")
    am_map = {aid: r for aid, r in am_rows}

    kbs = await KnowledgeBase.filter(id__in=kb_ids, status=1).all()
    kb_map = {kb.id: kb for kb in kbs}
    ts_ids = list({kb.team_space_id for kb in kbs})

    kb_mem_rows = await KnowledgeBaseMember.filter(
        knowledge_base_id__in=kb_ids, user_id=uid, status=1
    ).values_list("knowledge_base_id", "role")
    kb_mem_map = {kbid: r for kbid, r in kb_mem_rows}

    tss = await TeamSpace.filter(id__in=ts_ids, status=1).all()
    ts_map = {ts.id: ts for ts in tss}

    tm_rows = await TeamMember.filter(
        team_space_id__in=ts_ids, user_id=uid, status=1
    ).values_list("team_space_id", "role")
    tm_map = {tsid: r for tsid, r in tm_rows}

    kb_eff_map: dict[int, Optional[int]] = {}
    for kb_id in kb_ids:
        kb = kb_map.get(kb_id)
        if not kb:
            kb_eff_map[kb_id] = None
        else:
            kb_eff_map[kb_id] = _kb_effective_from_maps(
                kb, uid, kb_mem_map, ts_map, tm_map
            )

    return {
        a.id: _article_effective_from_maps(a, uid, am_map, kb_eff_map)
        for a in articles
    }


@router.post("", summary="创建文章", description="在指定知识库中创建新文章；仅 after_article_id 控制插入位置，为空则排在同级第一位")
async def create_article(
    article_data: ArticleCreate,
    current_user: User = Depends(get_current_active_user)
):
    """创建文章。after_article_id 为空则排第一位（S=0，兄弟全体 +1）；有值则插到该兄弟之后（先 shift 再插入）。"""
    # 检查知识库是否存在并有权限
    kb = await KnowledgeBase.get_or_none(id=article_data.knowledge_base_id, status=1)
    if not kb:
        return error_response(404, "知识库不存在")
    
    await require_permission(user=current_user, resource_type=ResourceType.KNOWLEDGE_BASE, 
    resource_id=article_data.knowledge_base_id, required_permission=PermissionType.EDIT)
    
    # 如果指定了父文章，检查父文章是否存在
    if article_data.parent_id:
        parent = await Article.get_or_none(id=article_data.parent_id, status__gt=0)
        if not parent:
            return error_response(404, "父文章不存在")
        if parent.knowledge_base_id != article_data.knowledge_base_id:
            return error_response(400, "父文章必须属于同一知识库")
    
    # 如果未指定可见性，继承知识库的可见性
    visibility = article_data.visibility or kb.visibility
    
    # 如果状态为已发布，设置发布时间
    published_at = None
    if article_data.status == 2:
        published_at = datetime.utcnow()
    
    # 解析目标 sort_order S：after_article_id 为空=第一位(S=0)，否则=该兄弟.sort_order+1
    sf = _siblings_filter(article_data.knowledge_base_id, article_data.parent_id)
    if article_data.after_article_id is None:
        S = 0
    else:
        sib = await Article.get_or_none(id=article_data.after_article_id, **sf)
        if not sib:
            return error_response(400, "after_article_id 需为同知识库、同父下的有效文章 ID")
        S = sib.sort_order + 1

    tag_ids_raw = article_data.tag_ids or []
    unique_tag_ids = list(dict.fromkeys(tag_ids_raw))
    tag_by_id = {}
    if unique_tag_ids:
        tag_rows = await Tag.filter(
            id__in=unique_tag_ids,
            knowledge_base_id=article_data.knowledge_base_id,
        ).all()
        if len(tag_rows) != len(unique_tag_ids):
            return error_response(400, "标签不存在或不属于当前知识库")
        tag_by_id = {t.id: t for t in tag_rows}

    async with in_transaction():
        # 腾出位置：>=S 的兄弟 sort_order+1（S=0 时即全体 +1）
        await Article.filter(**sf, sort_order__gte=S).update(sort_order=F("sort_order") + 1)
        article = await Article.create(
            knowledge_base=kb,
            parent_id=article_data.parent_id,
            node_type=article_data.node_type,
            title=article_data.title,
            content=article_data.content,
            summary=article_data.summary,
            author=current_user,
            visibility=visibility,
            sort_order=S,
            status=article_data.status,
            is_original=article_data.is_original,
            is_ai_generated=article_data.is_ai_generated,
            published_at=published_at
        )
        # 自动将创建者加入文章成员表，角色为管理员
        await ArticleMember.create(
            article=article,
            user=current_user,
            role=2,
            added_by=current_user,
        )
        for tid in unique_tag_ids:
            await ArticleTag.create(article=article, tag=tag_by_id[tid])

    # 查询作者信息（创建者就是current_user）
    author_name = current_user.nickname or current_user.username
    
    # 构建返回数据
    out = ArticleResponse.model_validate(article).model_dump()
    out["author_name"] = author_name
    out["updated_by_id"] = article.updated_by_id
    out["updated_by_name"] = None
    out["my_role"] = await _resolve_article_my_role(article, current_user)
    out["tag_ids"] = unique_tag_ids
    out["tag_names"] = [tag_by_id[tid].name for tid in unique_tag_ids]

    return success_response(data=out, message="创建成功")


async def find_root_article(article: Article) -> Article:
    """递归查找文章的根节点（parent为null的节点）"""
    if article.parent_id is None:
        return article
    parent = await Article.get_or_none(id=article.parent_id, status__gt=0)
    if parent is None:
        return article
    return await find_root_article(parent)


def build_article_tree(
    articles: List[Article],
    articles_map: dict,
    users_map: dict,
    has_children_map: dict,
    my_role_map: dict,
    tag_ids_map: dict,
    tag_names_map: dict,
) -> List[dict]:
    """构建文章树形结构（不包含 content 字段）"""
    tree = []
    # 按sort_order和created_at排序
    sorted_articles = sorted(articles, key=lambda x: (x.sort_order, -x.created_at.timestamp() if x.created_at else 0))
    
    for article in sorted_articles:
        article_data = ArticleResponse.model_validate(article).model_dump(exclude={"content"})
        article_data["has_children"] = has_children_map.get(article.id, False)
        article_data["author_name"] = users_map.get(article.author_id)
        article_data["updated_by_id"] = article.updated_by_id
        article_data["updated_by_name"] = users_map.get(article.updated_by_id) if article.updated_by_id else None
        article_data["my_role"] = my_role_map.get(article.id, 0)
        article_data["tag_ids"] = tag_ids_map.get(article.id, [])
        article_data["tag_names"] = tag_names_map.get(article.id, [])
        # 如果有子节点，递归构建子树
        if article.id in articles_map:
            children = articles_map[article.id]
            article_data["children"] = build_article_tree(
                children,
                articles_map,
                users_map,
                has_children_map,
                my_role_map,
                tag_ids_map,
                tag_names_map,
            )
        else:
            article_data["children"] = []
        tree.append(article_data)
    return tree


@router.get("", summary="获取文章列表", description="获取文章列表，支持按知识库、父文章、状态等筛选")
async def get_articles(
    knowledge_base_id: Optional[int] = Query(..., description="知识库ID筛选"),
    parent_id: Optional[int] = Query(None, description="父文章ID筛选，0或null表示顶级文章"),
    article_id: Optional[int] = Query(None, description="文章ID筛选"),
    status: Optional[int] = Query(None, description="状态筛选：1-草稿，2-已发布"),
    current_user: User = Depends(get_current_active_user)
):
    """获取文章列表，支持分页和筛选。可见性与权限模块一致：个人仅作者；成员/公开在知识库内列出后由 my_role 体现继承。"""
    # 如果 article_id 不为空，先解析根节点并校验目标知识库可读
    root_article_id = None
    if article_id:
        target_article = await Article.get_or_none(id=article_id, status__gt=0)
        if target_article:
            if target_article.knowledge_base_id:
                await require_permission(
                    user=current_user,
                    resource_type=ResourceType.KNOWLEDGE_BASE,
                    resource_id=target_article.knowledge_base_id,
                    required_permission=PermissionType.READ,
                )
            root_article = await find_root_article(target_article)
            root_article_id = root_article.id

    # 已校验知识库可读时：成员可见文章可通过知识库/团队空间继承，不再仅限 ArticleMember
    if knowledge_base_id:
        await require_permission(
            user=current_user,
            resource_type=ResourceType.KNOWLEDGE_BASE,
            resource_id=knowledge_base_id,
            required_permission=PermissionType.READ,
        )
        visibility_filter = (
            Q(visibility=1, author_id=current_user.id)
            | Q(visibility=2)
            | Q(visibility=3)
        )
    else:
        member_article_ids = await ArticleMember.filter(
            user_id=current_user.id, status=1
        ).values_list("article_id", flat=True)
        member_article_ids = list(member_article_ids) if member_article_ids else []
        visibility_filter = (
            Q(visibility=3)
            | Q(visibility=1, author_id=current_user.id)
            | (Q(visibility=2) & Q(id__in=member_article_ids))
        )

    query = Article.filter(status__gt=0).filter(visibility_filter)

    if knowledge_base_id:
        query = query.filter(knowledge_base_id=knowledge_base_id)
    
    # 如果article_id不为空，需要构建整个目录树
    if root_article_id:
        # 获取所有属于该知识库的文章（含可见性过滤），用于构建目录树
        all_articles_query = Article.filter(
            knowledge_base_id=knowledge_base_id, status__gt=0
        ).filter(visibility_filter)
        if status:
            all_articles_query = all_articles_query.filter(status=status)
        all_articles = await all_articles_query.order_by("sort_order", "-created_at").all()
        
        # 构建文章映射：parent_id -> [子文章列表]
        articles_map = {}
        root_articles = []
        
        for article in all_articles:
            if article.parent_id is None:
                root_articles.append(article)
            else:
                if article.parent_id not in articles_map:
                    articles_map[article.parent_id] = []
                articles_map[article.parent_id].append(article)
        
        # 基于可见文章构建 has_children（仅统计可见子节点）
        has_children_map = {pid: True for pid in articles_map}

        # 批量查询作者信息和更新人信息
        author_ids = list(set([article.author_id for article in all_articles]))
        updated_by_ids = list(set([article.updated_by_id for article in all_articles if article.updated_by_id]))
        all_user_ids = list(set(author_ids + updated_by_ids))
        
        users_map = {}
        if all_user_ids:
            users = await User.filter(id__in=all_user_ids).all()
            for user in users:
                users_map[user.id] = user.nickname or user.username

        my_role_map = await _batch_article_my_roles(all_articles, current_user)

        all_aids = [a.id for a in all_articles]
        tag_ids_map, tag_names_map = await _batch_article_tag_maps(all_aids)

        # 构建树形结构
        tree = build_article_tree(
            root_articles,
            articles_map,
            users_map,
            has_children_map,
            my_role_map,
            tag_ids_map,
            tag_names_map,
        )
        
        data = {
            "items": tree,
            "total": len(all_articles),
        }
        return success_response(data=data, message="获取成功")
    
    # 原有的逻辑处理
    if not parent_id:
        query = query.filter(parent_id__isnull=True)
    else:
        query = query.filter(parent_id=parent_id)
    
    if status:
        query = query.filter(status=status)
    
    # 计算总数
    total = await query.count()
    
    # 按排序顺序和创建时间排序（先按sort_order升序，相同sort_order按创建时间降序）
    articles = await query.order_by("sort_order", "-created_at").all()
    
    # 获取所有文章ID，批量查询哪些文章有可见子节点
    article_ids = [article.id for article in articles]
    has_children_map = {}
    if article_ids:
        children_articles = await Article.filter(
            parent_id__in=article_ids,
            status__gt=0
        ).filter(visibility_filter).values_list("parent_id", flat=True)
        for parent_id in children_articles:
            if parent_id:
                has_children_map[parent_id] = True

    # 批量查询作者信息和更新人信息
    author_ids = list(set([article.author_id for article in articles]))
    updated_by_ids = list(set([article.updated_by_id for article in articles if article.updated_by_id]))
    all_user_ids = list(set(author_ids + updated_by_ids))
    
    users_map = {}
    if all_user_ids:
        users = await User.filter(id__in=all_user_ids).all()
        for user in users:
            users_map[user.id] = user.nickname or user.username

    my_role_map = await _batch_article_my_roles(articles, current_user)

    tag_ids_map, tag_names_map = await _batch_article_tag_maps(article_ids)

    # 构建返回数据，添加has_children、author_name和updated_by_name字段（不含content）
    items = []
    for article in articles:
        article_data = ArticleResponse.model_validate(article).model_dump(exclude={"content"})
        article_data["has_children"] = has_children_map.get(article.id, False)
        article_data["author_name"] = users_map.get(article.author_id)
        article_data["updated_by_id"] = article.updated_by_id
        article_data["updated_by_name"] = users_map.get(article.updated_by_id) if article.updated_by_id else None
        article_data["my_role"] = my_role_map.get(article.id, 0)
        article_data["tag_ids"] = tag_ids_map.get(article.id, [])
        article_data["tag_names"] = tag_names_map.get(article.id, [])
        if article_data["has_children"] and not article_data.get("children"):
            article_data["children"] = [{}]
        else:
            article_data["children"] = []
        items.append(article_data)
    
    data = {
        "items": items,
        "total": total,
    }
    return success_response(data=data, message="获取成功")


@router.get(
    "/search",
    summary="搜索文章",
    description="按关键词对文章标题模糊搜索；可选知识库ID；按阅读量、点赞量、收藏量倒序；分页，默认每页10条。",
)
async def search_articles(
    keyword: str = Query(..., min_length=1, description="关键词，对标题模糊匹配"),
    knowledge_base_id: Optional[int] = Query(None, description="知识库ID，不传则搜全部"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数，默认10"),
    current_user: User = Depends(get_current_active_user),
):
    """标题模糊搜索，可选知识库，按 view_count、like_count、collect_count 倒序，分页。"""
    if knowledge_base_id is not None:
        await require_permission(user=current_user, resource_type=ResourceType.KNOWLEDGE_BASE, 
        resource_id=knowledge_base_id, required_permission=PermissionType.READ)
    conn = Tortoise.get_connection("default")
    like_arg = f"%{keyword}%"
    offset = (page - 1) * page_size

    # 动态 WHERE：status、title LIKE、可选 knowledge_base_id
    where = "a.status > 0 AND a.title LIKE %s"
    params = [like_arg]
    if knowledge_base_id is not None:
        where += " AND a.knowledge_base_id = %s"
        params.append(knowledge_base_id)

    # 总数
    count_sql = f"""
    SELECT COUNT(*) AS total
    FROM articles a
    WHERE {where}
    """
    _, count_rows = await conn.execute_query(count_sql, params)
    total = int(count_rows[0]["total"]) if count_rows else 0

    # 分页列表：LEFT JOIN article_stats，按阅读量、点赞量、收藏量倒序
    list_sql = f"""
    SELECT
        a.id, a.knowledge_base_id, a.parent_id, a.title, a.content, a.summary,
        a.author_id, a.visibility, a.sort_order, a.status, a.published_at,
        a.updated_by_id, a.created_at, a.updated_at,
        COALESCE(s.view_count, 0) AS view_count,
        COALESCE(s.like_count, 0) AS like_count,
        COALESCE(s.collect_count, 0) AS collect_count
    FROM articles a
    LEFT JOIN article_stats s ON s.article_id = a.id
    WHERE {where}
    ORDER BY COALESCE(s.view_count, 0) DESC, COALESCE(s.like_count, 0) DESC, COALESCE(s.collect_count, 0) DESC
    LIMIT %s OFFSET %s
    """
    _, rows = await conn.execute_query(list_sql, params + [page_size, offset])

    if not rows:
        return success_response(
            data={"items": [], "total": total, "page": page, "page_size": page_size},
            message="获取成功",
        )

    # 批量查作者、更新人
    author_ids = list({r["author_id"] for r in rows})
    updated_ids = list({r["updated_by_id"] for r in rows if r.get("updated_by_id")})
    user_ids = list(set(author_ids + updated_ids))
    users = await User.filter(id__in=user_ids).all()
    users_map = {u.id: (u.nickname or u.username) for u in users}

    # 批量查知识库名称、所属团队空间
    kb_ids = list({r["knowledge_base_id"] for r in rows})
    kbs = await KnowledgeBase.filter(id__in=kb_ids).values_list("id", "name", "team_space_id")
    kb_map = {kb[0]: kb[1] for kb in kbs}
    kb_to_ts = {kb[0]: kb[2] for kb in kbs if kb[2]}
    ts_ids = list({kb[2] for kb in kbs if kb[2]})
    ts_list = await TeamSpace.filter(id__in=ts_ids).values_list("id", "name") if ts_ids else []
    ts_map = {t[0]: t[1] for t in ts_list}

    search_article_ids = [r["id"] for r in rows]
    tag_ids_map, tag_names_map = await _batch_article_tag_maps(search_article_ids)

    def _dt(v):
        return v.isoformat() if v and hasattr(v, "isoformat") else v

    items = []
    for r in rows:
        kb_id = r["knowledge_base_id"]
        ts_id = kb_to_ts.get(kb_id)
        items.append({
            "id": r["id"],
            "knowledge_base_id": kb_id,
            "knowledge_base_name": kb_map.get(kb_id),
            "team_space_id": ts_id,
            "team_space_name": ts_map.get(ts_id) if ts_id else None,
            "parent_id": r["parent_id"],
            "title": r["title"],
            "content": r["content"],
            "summary": r["summary"],
            "author_id": r["author_id"],
            "author_name": users_map.get(r["author_id"]),
            "updated_by_id": r.get("updated_by_id"),
            "updated_by_name": users_map.get(r["updated_by_id"]) if r.get("updated_by_id") else None,
            "visibility": r["visibility"],
            "sort_order": r["sort_order"],
            "status": r["status"],
            "published_at": _dt(r.get("published_at")),
            "created_at": _dt(r.get("created_at")),
            "updated_at": _dt(r.get("updated_at")),
            "view_count": int(r.get("view_count") or 0),
            "like_count": int(r.get("like_count") or 0),
            "collect_count": int(r.get("collect_count") or 0),
            "tag_ids": tag_ids_map.get(r["id"], []),
            "tag_names": tag_names_map.get(r["id"], []),
        })

    return success_response(
        data={"items": items, "total": total, "page": page, "page_size": page_size},
        message="获取成功",
    )


@router.get(
    "/search/members",
    summary="搜索文章成员",
    description="按关键词搜索用户（邮箱/用户名/昵称），或按文章获取成员。keyword 与 article_id 至少传一个；传 article_id 时标注 is_member、role、joined_at。",
)
async def search_article_members(
    keyword: Optional[str] = Query(None, description="搜索关键词（匹配邮箱、用户名、昵称）；与 article_id 至少传一个"),
    article_id: Optional[int] = Query(None, description="文章ID；不为空时限定为该文章成员并标注 is_member"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
):
    """搜索用户：keyword 匹配邮箱/用户名/昵称；传 article_id 时限定为文章成员并标注 is_member、role、joined_at。"""
    k = keyword.strip() if (keyword and keyword.strip()) else ""
    if not k and article_id is None:
        return error_response(400, "关键词与文章ID至少传一个")

    member_ids: set = set()
    member_info_map: dict = {}
    if article_id is not None:
        article = await Article.get_or_none(id=article_id, status__gt=0)
        if not article:
            return error_response(404, "文章不存在")
        await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
        resource_id=article_id, required_permission=PermissionType.READ)
        members = await ArticleMember.filter(
            article_id=article_id, status=1
        ).values_list("user_id", "role", "joined_at")
        member_ids = {uid for uid, _, _ in members}
        member_info_map = {
            uid: {"role": role, "joined_at": joined_at}
            for uid, role, joined_at in members
        }

    query = User.filter(status=1)
    if k:
        query = query.filter(
            Q(username__icontains=k)
            | Q(email__icontains=k)
            | Q(nickname__icontains=k)
        )
    if article_id is not None and not k:
        query = query.filter(id__in=member_ids) if member_ids else query.filter(id=-1)

    total = await query.count()
    offset = (page - 1) * page_size
    users = await query.order_by("-created_at").offset(offset).limit(page_size).all()

    items = []
    for user in users:
        d = UserResponse.model_validate(user).model_dump()
        d["is_member"] = False
        d["role"] = None
        d["joined_at"] = None
        if article_id is not None:
            d["is_member"] = user.id in member_ids
            if user.id in member_info_map:
                info = member_info_map[user.id]
                d["role"] = info["role"]
                d["joined_at"] = info["joined_at"].isoformat() if info["joined_at"] else None
        items.append(d)

    return success_response(
        data={"items": items, "total": total, "page": page, "page_size": page_size},
        message="获取成功",
    )


@router.post(
    "/{article_id}/members",
    summary="添加文章成员（支持批量）",
    description="user_id 与系统 role_ids 至少传一种；传 role_ids 时将拥有这些系统角色的用户全部加入，并使用统一的成员 role。个人可见文章(visibility=1)不可添加成员。",
)
async def add_article_member(
    article_id: int,
    member_data: ArticleMemberAdd,
    current_user: User = Depends(get_current_active_user),
):
    """添加文章成员；可传 user_id 或系统 role_ids 批量添加。"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    if article.visibility == 1:
        return error_response(403, "个人可见文章，仅作者可访问，不可添加成员")

    await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
    resource_id=article_id, required_permission=PermissionType.EDIT)

    has_user = member_data.user_id is not None
    has_roles = bool(member_data.role_ids and len(member_data.role_ids) > 0)
    if not has_user and not has_roles:
        return error_response(400, "user_id 与 role_ids 至少传一种")

    user_ids_to_add: set = set()
    if member_data.user_id is not None:
        user_ids_to_add.add(member_data.user_id)
    if member_data.role_ids:
        rid_set = list(dict.fromkeys(member_data.role_ids))
        roles = await Role.filter(id__in=rid_set, status=1).all()
        valid_role_ids = {r.id for r in roles}
        if len(valid_role_ids) != len(rid_set):
            invalid = set(rid_set) - valid_role_ids
            return error_response(400, f"无效或已禁用的角色ID: {sorted(invalid)}")
        ur_rows = await UserRole.filter(
            role_id__in=rid_set,
            status=1,
        ).values_list("user_id", flat=True)
        user_ids_to_add.update(ur_rows)

    if not user_ids_to_add:
        return error_response(400, "没有可添加的用户")

    users = await User.filter(id__in=list(user_ids_to_add), status=1)
    found_ids = {u.id for u in users}
    missing = user_ids_to_add - found_ids
    if missing:
        return error_response(404, f"用户不存在或已禁用: {sorted(missing)}")

    async with in_transaction():
        existing_list = await ArticleMember.filter(
            article_id=article_id,
            user_id__in=list(found_ids),
        ).all()
        existing_by_uid = {m.user_id: m for m in existing_list}
        for u in users:
            ex = existing_by_uid.get(u.id)
            if ex:
                ex.status = 1
                ex.role = member_data.role
                ex.added_by = current_user
                await ex.save()
            else:
                await ArticleMember.create(
                    article=article,
                    user=u,
                    role=member_data.role,
                    added_by=current_user,
                )

    return success_response(message="成员添加成功")


@router.put(
    "/{article_id}/members/{user_id}",
    summary="修改文章成员角色",
    description="修改指定成员在文章中的角色。",
)
async def update_article_member(
    article_id: int,
    user_id: int,
    member_data: ArticleMemberUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """修改文章成员角色"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")

    await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
    resource_id=article_id, required_permission=PermissionType.ADMIN)

    member = await ArticleMember.get_or_none(
        article_id=article_id,
        user_id=user_id,
        status=1,
    )
    if not member:
        return error_response(404, "成员不存在")

    member.role = member_data.role
    await member.save()
    return success_response(message="成员信息更新成功")


@router.delete(
    "/{article_id}/members/{user_id}",
    summary="移除文章成员",
    description="从文章中移除指定成员；文章作者不可被移除。",
)
async def remove_article_member(
    article_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """移除文章成员"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")

    await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
    resource_id=article_id, required_permission=PermissionType.ADMIN)

    if article.author_id == user_id:
        return error_response(400, "文章作者不可被移除")

    member = await ArticleMember.get_or_none(
        article_id=article_id,
        user_id=user_id,
    )
    if not member:
        return error_response(404, "成员不存在")

    member.status = 0
    await member.save()
    return success_response(message="成员移除成功")


@router.post(
    "/{article_id}/members/batch-remove",
    summary="按系统角色批量移除文章成员",
    description="根据系统角色 ID 解析用户，将本文章中属于这些角色的有效成员移除（软删除）；文章作者不会被移除。",
)
async def batch_remove_article_members_by_roles(
    article_id: int,
    body: ArticleMemberBatchRemove,
    current_user: User = Depends(get_current_active_user),
):
    """按系统角色批量移除文章成员。"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")

    await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
    resource_id=article_id, required_permission=PermissionType.ADMIN)

    rid_set = list(dict.fromkeys(body.role_ids))
    roles = await Role.filter(id__in=rid_set, status=1).all()
    valid_role_ids = {r.id for r in roles}
    if len(valid_role_ids) != len(rid_set):
        invalid = set(rid_set) - valid_role_ids
        return error_response(400, f"无效或已禁用的角色ID: {sorted(invalid)}")

    user_ids_from_roles = set(
        await UserRole.filter(role_id__in=rid_set, status=1).values_list("user_id", flat=True)
    )
    user_ids_from_roles.discard(article.author_id)
    if not user_ids_from_roles:
        return success_response(data={"removed_count": 0}, message="没有可移除的成员")

    members = await ArticleMember.filter(
        article_id=article_id,
        user_id__in=list(user_ids_from_roles),
        status=1,
    ).all()
    if not members:
        return success_response(data={"removed_count": 0}, message="没有可移除的成员")

    async with in_transaction():
        for m in members:
            m.status = 0
            await m.save()

    return success_response(
        data={"removed_count": len(members)},
        message="批量移除成功",
    )


@router.put(
    "/{article_id}/position",
    summary="调整子节点顺序",
    description="按 event_type 移动：inner=作为 target_node_id 的子节点（排在子节点末位）；before=插到 target 前；after=插到 target 后；none=不操作。",
)
async def update_article_position(
    article_id: int,
    body: ChildPositionUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """inner：parent_id=target，sort_order=其子末位（max+1）；before：与 target 同父，sort_order=target；after：同父，sort_order=target+1；none：直接返回。"""
    if body.event_type == "none":
        return success_response(data=None, message="未执行操作")

    if body.target_node_id is None:
        return error_response(400, "inner、before、after 时 target_node_id 必填")

    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
    resource_id=article_id, required_permission=PermissionType.READ)

    target = await Article.get_or_none(id=body.target_node_id, status__gt=0)
    if not target:
        return error_response(400, "target_node_id 对应的文章不存在")
    if target.id == article_id:
        return error_response(400, "target_node_id 不能为当前文章")
    if target.knowledge_base_id != article.knowledge_base_id:
        return error_response(400, "仅支持在同一知识库内移动")

    O_old = article.sort_order

    if body.event_type == "inner":
        # 作为 target 的子节点，放到其子节点最后面（sort_order=末位，即 max+1）
        node = target
        while node.parent_id is not None:
            parent = await Article.get_or_none(id=node.parent_id, status__gt=0)
            if not parent:
                break
            if parent.id == article_id:
                return error_response(400, "不能移动到自身子节点之下，会形成环")
            node = parent

        new_parent_id = body.target_node_id
        old_sf = _siblings_filter(article.knowledge_base_id, article.parent_id)
        new_sf = _siblings_filter(article.knowledge_base_id, new_parent_id)
        same_parent = (article.parent_id == new_parent_id)

        async with in_transaction():
            # S = target 子节点（排除当前文章）的 max(sort_order)+1，无则 0
            row = await Article.filter(**new_sf).exclude(id=article_id).order_by("-sort_order").limit(1).values_list("sort_order", flat=True)
            S = (row[0] + 1) if row else 0

            if same_parent:
                # 同父内挪到末位：(O_old, max] -1 收口，再设 article.sort_order=S
                await Article.filter(**new_sf, sort_order__gt=O_old).update(sort_order=F("sort_order") - 1)
                article.sort_order = S
            else:
                await Article.filter(**old_sf, sort_order__gt=O_old).update(sort_order=F("sort_order") - 1)
                article.parent_id = new_parent_id
                article.sort_order = S
            await article.save()
        return success_response(data={"sort_order": S, "parent_id": new_parent_id}, message="已移动至目标节点下末位")

    if body.event_type == "before":
        new_parent_id = target.parent_id
        S = target.sort_order
    else:  # after
        new_parent_id = target.parent_id
        S = target.sort_order + 1

    old_sf = _siblings_filter(article.knowledge_base_id, article.parent_id)
    new_sf = _siblings_filter(target.knowledge_base_id, new_parent_id)
    changing_parent = (article.parent_id != new_parent_id)

    async with in_transaction():
        if changing_parent:
            await Article.filter(**old_sf, sort_order__gt=O_old).update(sort_order=F("sort_order") - 1)
        await Article.filter(**new_sf, sort_order__gte=S).exclude(id=article_id).update(sort_order=F("sort_order") + 1)
        article.parent_id = new_parent_id
        article.sort_order = S
        await article.save()

    return success_response(
        data={"sort_order": S, "parent_id": new_parent_id},
        message="已插入到目标节点之前" if body.event_type == "before" else "已插入到目标节点之后",
    )


@router.get("/{article_id}", summary="获取文章详情", description="根据文章ID获取文章详细信息")
async def get_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """获取文章详情"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    
    auth_check_result = await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, resource_id=article_id, required_permission=0)
    
    # 插入浏览记录（action_type=5）
    await ArticleInteraction.create(
        article=article,
        user=current_user,
        action_type=5  # 5-浏览
    )
    # article_stats 浏览量 +1
    stats, _ = await ArticleStats.get_or_create(article=article)
    stats.view_count += 1
    await stats.save()
    
    # 查询作者信息
    author = await article.author
    author_name = author.nickname or author.username if author else None
    
    # 查询更新人信息
    updated_by_name = None
    if article.updated_by_id:
        updated_by = await article.updated_by
        updated_by_name = (updated_by.nickname or updated_by.username) if updated_by else None

    # 构建返回数据
    article_data = ArticleResponse.model_validate(article).model_dump()
    article_data["author_name"] = author_name
    article_data["updated_by_id"] = article.updated_by_id
    article_data["updated_by_name"] = updated_by_name
    article_data["my_role"] = auth_check_result.role

    tid_map, tname_map = await _batch_article_tag_maps([article_id])
    article_data["tag_ids"] = tid_map.get(article_id, [])
    article_data["tag_names"] = tname_map.get(article_id, [])

    return success_response(data=article_data, message="获取成功")


@router.get("/{article_id}/attachments", summary="获取文章附件", description="根据文章ID获取该文章下所有附件")
async def get_article_attachments(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """获取文章所有附件"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
    resource_id=article_id, required_permission=PermissionType.READ)
    files = await File.filter(article_id=article_id, status=1).order_by("-created_at")
    items = [
        {
            "id": f.id,
            "filename": f.filename,
            "file_url": f.file_url,
            "file_type": f.file_type,
            "file_size": f.file_size,
            "article_id": f.article_id,
            "created_at": f.created_at,
        }
        for f in files
    ]
    return success_response(data=items, message="请求成功")




@router.put("/{article_id}", summary="更新文章", description="更新文章信息，会自动创建版本历史")
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """更新文章"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    
    # 检查权限（作者或有编辑权限）
    if article.author_id != current_user.id:
        await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
        resource_id=article_id, required_permission=PermissionType.EDIT)
    
    update_data = article_data.model_dump(exclude_unset=True)
    update_data.pop("tag_ids", None)

    sync_tags = "tag_ids" in article_data.model_fields_set
    unique_tag_ids: List[int] = []
    tag_by_id: dict = {}
    if sync_tags:
        raw_ids = article_data.tag_ids or []
        unique_tag_ids = list(dict.fromkeys(raw_ids))
        if unique_tag_ids:
            tag_rows = await Tag.filter(
                id__in=unique_tag_ids,
                knowledge_base_id=article.knowledge_base_id,
            ).all()
            if len(tag_rows) != len(unique_tag_ids):
                return error_response(400, "标签不存在或不属于当前知识库")
            tag_by_id = {t.id: t for t in tag_rows}

    async with in_transaction():
        # 创建版本历史
        version_count = await ArticleVersion.filter(article_id=article.id).count()
        await ArticleVersion.create(
            article=article,
            version=version_count + 1,
            title=article.title,
            content=article.content,
            author=current_user,
            change_log="更新文章",
        )

        # 如果状态改为已发布，设置发布时间
        if article_data.status == 2 and article.status != 2:
            update_data["published_at"] = datetime.utcnow()

        for key, value in update_data.items():
            setattr(article, key, value)

        article.updated_by = current_user
        await article.save()

        if sync_tags:
            await ArticleTag.filter(article_id=article.id).delete()
            for tid in unique_tag_ids:
                await ArticleTag.create(article=article, tag=tag_by_id[tid])

    # 查询作者信息
    author = await article.author
    author_name = author.nickname or author.username if author else None
    
    # 查询更新人信息
    updated_by_name = current_user.nickname or current_user.username
    
    # 构建返回数据
    out = ArticleResponse.model_validate(article).model_dump()
    out["author_name"] = author_name
    out["updated_by_id"] = article.updated_by_id
    out["updated_by_name"] = updated_by_name
    if sync_tags:
        out["tag_ids"] = unique_tag_ids
        out["tag_names"] = [tag_by_id[tid].name for tid in unique_tag_ids]
    else:
        tid_map, tname_map = await _batch_article_tag_maps([article.id])
        out["tag_ids"] = tid_map.get(article.id, [])
        out["tag_names"] = tname_map.get(article.id, [])

    return success_response(data=out, message="更新成功")


@router.delete("/{article_id}", summary="删除文章", description="软删除文章（将状态设置为0）")
async def delete_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """删除文章"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    
    # 检查权限（作者或管理员）
    if article.author_id != current_user.id:
        await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
        resource_id=article_id, required_permission=PermissionType.ADMIN)
    
    article.status = 0
    await article.save()
    return success_response(message="删除成功")


@router.post("/{article_id}/publish", summary="发布文章", description="将草稿状态的文章发布")
async def publish_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """发布文章"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    
    if article.author_id != current_user.id:
        await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
        resource_id=article_id, required_permission=PermissionType.EDIT)
    
    article.status = 2
    if not article.published_at:
        article.published_at = datetime.utcnow()
    await article.save()
    
    return success_response(message="发布成功")


@router.get("/{article_id}/versions", summary="获取文章版本历史", description="获取文章的所有版本历史记录")
async def get_article_versions(
    article_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """获取文章版本历史"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    
    await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
    resource_id=article_id, required_permission=PermissionType.READ)
    
    versions = await ArticleVersion.filter(article_id=article_id).order_by("-version").all()
    data = [
        {
            "id": v.id,
            "version": v.version,
            "title": v.title,
            "content": v.content,
            "change_log": v.change_log,
            "author_id": v.author_id,
            "created_at": v.created_at.isoformat() if v.created_at else None
        }
        for v in versions
    ]
    return success_response(data=data, message="获取成功")


@router.post("/{article_id}/rollback/{version_id}", summary="回滚文章版本", description="将文章回滚到指定的历史版本")
async def rollback_article(
    article_id: int,
    version_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """回滚文章到指定版本"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    
    if article.author_id != current_user.id:
        await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
        resource_id=article_id, required_permission=PermissionType.EDIT)
    
    version = await ArticleVersion.get_or_none(id=version_id, article_id=article_id)
    if not version:
        return error_response(404, "版本不存在")
    
    # 保存当前版本
    # 获取当前文章的版本数量，计算新版本号
    version_count = await ArticleVersion.filter(article_id=article.id).count()
    await ArticleVersion.create(
        article=article,
        version=version_count + 1,
        title=article.title,
        content=article.content,
        author=current_user,
        change_log=f"回滚到版本{version.version}"
    )
    
    # 回滚内容
    article.title = version.title
    article.content = version.content
    await article.save()

    return success_response(message="回滚成功")


@router.post("/{article_id}/like", summary="点赞文章", description="对文章进行点赞")
async def like_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """点赞文章"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    
    await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
    resource_id=article_id, required_permission=PermissionType.READ)
    
    # 检查用户当前的点赞状态
    latest_like = await ArticleInteraction.filter(
        article_id=article_id,
        user_id=current_user.id,
        action_type__in=[1, 2]  # 1-点赞，2-取消点赞
    ).order_by("-created_at").first()
    
    # 如果已经点赞，返回提示
    if latest_like and latest_like.action_type == 1:
        return error_response(400, "已经点赞过了")
    
    # 记录点赞行为
    await ArticleInteraction.create(
        article=article,
        user=current_user,
        action_type=1  # 1-点赞
    )
    
    # 更新统计数据
    stats, created = await ArticleStats.get_or_create(article=article)
    stats.like_count += 1
    await stats.save()
    
    return success_response(data={"like_count": stats.like_count}, message="点赞成功")


@router.post("/{article_id}/unlike", summary="取消点赞", description="取消对文章的点赞")
async def unlike_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """取消点赞文章"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    
    await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
    resource_id=article_id, required_permission=PermissionType.READ)
    
    # 检查用户当前的点赞状态
    latest_like = await ArticleInteraction.filter(
        article_id=article_id,
        user_id=current_user.id,
        action_type__in=[1, 2]  # 1-点赞，2-取消点赞
    ).order_by("-created_at").first()
    
    # 如果没有点赞过，返回提示
    if not latest_like or latest_like.action_type == 2:
        return error_response(400, "尚未点赞")
    
    # 记录取消点赞行为
    await ArticleInteraction.create(
        article=article,
        user=current_user,
        action_type=2  # 2-取消点赞
    )
    
    # 更新统计数据
    stats, created = await ArticleStats.get_or_create(article=article)
    stats.like_count = max(0, stats.like_count - 1)
    await stats.save()
    
    return success_response(data={"like_count": stats.like_count}, message="取消点赞成功")


@router.post("/{article_id}/collect", summary="收藏文章", description="收藏文章")
async def collect_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """收藏文章"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    
    await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
    resource_id=article_id, required_permission=PermissionType.READ)
    
    # 检查用户当前的收藏状态
    latest_collect = await ArticleInteraction.filter(
        article_id=article_id,
        user_id=current_user.id,
        action_type__in=[3, 4]  # 3-收藏，4-取消收藏
    ).order_by("-created_at").first()
    
    # 如果已经收藏，返回提示
    if latest_collect and latest_collect.action_type == 3:
        return error_response(400, "已经收藏过了")
    
    # 记录收藏行为
    await ArticleInteraction.create(
        article=article,
        user=current_user,
        action_type=3  # 3-收藏
    )
    
    # 更新统计数据
    stats, created = await ArticleStats.get_or_create(article=article)
    stats.collect_count += 1
    await stats.save()
    
    return success_response(data={"collect_count": stats.collect_count}, message="收藏成功")


@router.post("/{article_id}/uncollect", summary="取消收藏", description="取消收藏文章")
async def uncollect_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """取消收藏文章"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    
    await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
    resource_id=article_id, required_permission=PermissionType.READ)
    
    # 检查用户当前的收藏状态
    latest_collect = await ArticleInteraction.filter(
        article_id=article_id,
        user_id=current_user.id,
        action_type__in=[3, 4]  # 3-收藏，4-取消收藏
    ).order_by("-created_at").first()
    
    # 如果没有收藏过，返回提示
    if not latest_collect or latest_collect.action_type == 4:
        return error_response(400, "尚未收藏")
    
    # 记录取消收藏行为
    await ArticleInteraction.create(
        article=article,
        user=current_user,
        action_type=4  # 4-取消收藏
    )
    
    # 更新统计数据
    stats, created = await ArticleStats.get_or_create(article=article)
    stats.collect_count = max(0, stats.collect_count - 1)
    await stats.save()
    
    return success_response(data={"collect_count": stats.collect_count}, message="取消收藏成功")


@router.get("/{article_id}/stats", summary="获取文章统计数据", description="获取文章的点赞数、浏览量、收藏数等统计数据")
async def get_article_stats(
    article_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """获取文章统计数据"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    
    await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
    resource_id=article_id, required_permission=PermissionType.READ)
    
    # 获取统计数据
    stats, created = await ArticleStats.get_or_create(article=article)
    
    # 查询当前用户的交互状态
    latest_like = await ArticleInteraction.filter(
        article_id=article_id,
        user_id=current_user.id,
        action_type__in=[1, 2]
    ).order_by("-created_at").first()
    is_liked = latest_like.action_type == 1 if latest_like else False
    
    latest_collect = await ArticleInteraction.filter(
        article_id=article_id,
        user_id=current_user.id,
        action_type__in=[3, 4]
    ).order_by("-created_at").first()
    is_collected = latest_collect.action_type == 3 if latest_collect else False
    
    data = {
        "view_count": stats.view_count,
        "like_count": stats.like_count,
        "collect_count": stats.collect_count,
        "comment_count": stats.comment_count,
        "share_count": stats.share_count,
        "feedback_count": stats.feedback_count,
        "is_liked": is_liked,
        "is_collected": is_collected,
    }
    
    return success_response(data=data, message="获取成功")


class FeedbackCreate(BaseModel):
    article_id: int
    feedback_type: int  # 反馈类型：1-错误报告，2-内容建议，3-格式问题，4-其他
    content: str


class FeedbackReply(BaseModel):
    reply: str  # 管理员回复内容


@router.post("/{article_id}/feedback", summary="提交文章反馈", description="提交对文章的反馈")
async def create_feedback(
    article_id: int,
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_active_user)
):
    """提交文章反馈"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    
    await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
    resource_id=article_id, required_permission=PermissionType.READ)
    
    # 验证反馈类型
    if feedback_data.feedback_type not in [1, 2, 3, 4]:
        return error_response(400, "反馈类型无效")
    
    # 创建反馈
    feedback = await ArticleFeedback.create(
        article=article,
        user=current_user,
        feedback_type=feedback_data.feedback_type,
        content=feedback_data.content,
    )
    
    # 更新文章统计的反馈数
    stats, _ = await ArticleStats.get_or_create(article=article)
    stats.feedback_count += 1
    await stats.save()

    # 为文章作者创建一条通知消息
    await Notification.create(
        user_id=article.author_id,
        type="article_feedback",
        title="文章收到新的反馈",
        content=f"您有新的文章反馈，请及时处理，可点击链接查看详情， 已读忽略",
        link=f"/articles/{article.knowledge_base_id}?articleId={article.id}&tab=feedback",
        is_read=0,
    )
    
    # 构建返回数据
    data = {
        "id": feedback.id,
        "article_id": feedback.article_id,
        "user_id": feedback.user_id,
        "feedback_type": feedback.feedback_type,
        "content": feedback.content,
        "status": feedback.status,
        "created_at": feedback.created_at.strftime("%Y-%m-%d %H:%M:%S") if feedback.created_at else None,
    }
    
    return success_response(data=data, message="反馈提交成功")


@router.get("/{article_id}/feedbacks", summary="获取文章反馈列表", description="获取文章的所有反馈列表")
async def get_article_feedbacks(
    article_id: int,
    status: Optional[int] = Query(None, description="状态筛选：1-待处理，2-处理中，3-已处理，4-已关闭"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user)
):
    """获取文章反馈列表"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    
    await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
    resource_id=article_id, required_permission=PermissionType.READ)
    
    # 构建查询
    query = ArticleFeedback.filter(article_id=article_id, status__gt=0)
    if status:
        query = query.filter(status=status)
    
    # 计算总数
    total = await query.count()
    
    # 分页查询
    feedbacks = await query.order_by("-created_at").offset((page - 1) * page_size).limit(page_size).all()
    
    # 批量获取用户信息
    user_ids = set([f.user_id for f in feedbacks])
    if user_ids:
        users = await User.filter(id__in=list(user_ids)).all()
        users_map = {user.id: user for user in users}
    else:
        users_map = {}
    
    # 构建返回数据
    items = []
    for feedback in feedbacks:
        user = users_map.get(feedback.user_id)
        reply_user = None
        if feedback.reply_by_id:
            reply_user = await User.get_or_none(id=feedback.reply_by_id)
        
        items.append({
            "id": feedback.id,
            "article_id": feedback.article_id,
            "user_id": feedback.user_id,
            "user_name": (user.nickname or user.username) if user else None,
            "feedback_type": feedback.feedback_type,
            "content": feedback.content,
            "status": feedback.status,
            "reply": feedback.reply,
            "reply_by_id": feedback.reply_by_id,
            "reply_by_name": (reply_user.nickname or reply_user.username) if reply_user else None,
            "reply_at": feedback.reply_at.strftime("%Y-%m-%d %H:%M:%S") if feedback.reply_at else None,
            "created_at": feedback.created_at.strftime("%Y-%m-%d %H:%M:%S") if feedback.created_at else None,
            "updated_at": feedback.updated_at.strftime("%Y-%m-%d %H:%M:%S") if feedback.updated_at else None,
        })
    
    data = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    
    return success_response(data=data, message="获取成功")


@router.put("/feedbacks/{feedback_id}/status", summary="更新反馈状态", description="管理员更新反馈的处理状态")
async def update_feedback_status(
    feedback_id: int,
    new_status: int = Query(..., description="新状态：1-待处理，2-处理中，3-已处理，4-已关闭"),
    current_user: User = Depends(get_current_active_user)
):
    """更新反馈状态（管理员）"""
    feedback = await ArticleFeedback.get_or_none(id=feedback_id, status__gt=0)
    if not feedback:
        return error_response(404, "反馈不存在")
    
    # 检查权限（文章作者或管理员）
    article = await feedback.article
    if article.author_id != current_user.id:
        await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
        resource_id=article.id, required_permission=PermissionType.ADMIN)
    
    # 验证状态
    if new_status not in [1, 2, 3, 4]:
        return error_response(400, "状态值无效")
    
    feedback.status = new_status
    await feedback.save()
    
    return success_response(data={"status": feedback.status}, message="状态更新成功")


@router.post("/feedbacks/{feedback_id}/reply", summary="回复反馈", description="管理员回复反馈")
async def reply_feedback(
    feedback_id: int,
    reply_data: FeedbackReply,
    current_user: User = Depends(get_current_active_user)
):
    """回复反馈（管理员）"""
    feedback = await ArticleFeedback.get_or_none(id=feedback_id, status__gt=0)
    if not feedback:
        return error_response(404, "反馈不存在")
    
    # 检查权限（文章作者或管理员）
    article = await feedback.article
    if article.author_id != current_user.id:
        await require_permission(user=current_user, resource_type=ResourceType.ARTICLE, 
        resource_id=article.id, required_permission=PermissionType.ADMIN)
    
    # 更新回复
    feedback.reply = reply_data.reply
    feedback.reply_by = current_user
    feedback.reply_at = datetime.utcnow()
    # 如果有回复，将状态更新为已处理
    feedback.status = 3
    await feedback.save()
    
    # 获取回复人信息
    reply_by_name = current_user.nickname or current_user.username
    
    data = {
        "id": feedback.id,
        "reply": feedback.reply,
        "reply_by_id": feedback.reply_by_id,
        "reply_by_name": reply_by_name,
        "reply_at": feedback.reply_at.isoformat() if feedback.reply_at else None,
        "status": feedback.status,
    }
    
    return success_response(data=data, message="回复成功")
