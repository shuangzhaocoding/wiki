"""
用户相关路由
"""
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from tortoise import Tortoise
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from app.models.user import User
from app.models.article import Article, ArticleInteraction, ArticleFeedback
from app.models.team_space import TeamSpace, TeamMember
from app.models.knowledge_base import KnowledgeBase, KnowledgeBaseMember
from app.models.role import Role, UserRole
from app.core.dependencies import get_current_active_user
from app.core.response import success_response, error_response
from app.core.security import get_password_hash
from app.schemas.user import UserResponse, UserUpdate, UserCreateRequest
from app.utils.permissions import require_permission

router = APIRouter()


def _article_item_dict(article: Article, users_map: dict, extra_field: str, extra_value: Optional[str]) -> dict:
    """构建文章项字典（含文章详情与扩展时间字段）"""
    item = {
        "id": article.id,
        "knowledge_base_id": article.knowledge_base_id,
        "parent_id": article.parent_id,
        "node_type": article.node_type,
        "title": article.title,
        "content": article.content,
        "summary": article.summary,
        "author_id": article.author_id,
        "author_name": users_map.get(article.author_id),
        "updated_by_id": article.updated_by_id,
        "updated_by_name": users_map.get(article.updated_by_id) if article.updated_by_id else None,
        "visibility": article.visibility,
        "sort_order": article.sort_order,
        "status": article.status,
        "is_original": article.is_original,
        "is_ai_generated": article.is_ai_generated,
        "published_at": article.published_at.isoformat() if article.published_at else None,
        "created_at": article.created_at.isoformat() if article.created_at else None,
        "updated_at": article.updated_at.isoformat() if article.updated_at else None,
    }
    if extra_field:
        item[extra_field] = extra_value
    return item


@router.get("/me")
async def get_my_info(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    user_data = UserResponse.model_validate(current_user).model_dump()
    return success_response(data=user_data, message="获取成功")


@router.put("/me")
async def update_my_info(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """更新当前用户信息"""
    
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    await current_user.save()
    user_data = UserResponse.model_validate(current_user).model_dump()
    return success_response(data=user_data, message="更新成功")


@router.get(
    "/me/feedbacks",
    summary="当前用户反馈列表",
    description="分页获取当前用户提交的文章反馈，返回含文章标题、文章所属知识库ID等字段。",
)
async def get_my_feedbacks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[int] = Query(None, description="状态筛选：1-待处理，2-处理中，3-已处理，4-已关闭"),
    current_user: User = Depends(get_current_active_user),
):
    """获取当前用户的反馈列表，含文章对应的知识库ID、文章标题。"""
    query = ArticleFeedback.filter(user_id=current_user.id, status__gt=0)
    if status is not None:
        if status not in (1, 2, 3, 4):
            return error_response(400, "状态值无效")
        query = query.filter(status=status)

    total = await query.count()
    offset = (page - 1) * page_size
    feedbacks = await query.order_by("-created_at").offset(offset).limit(page_size).all()

    if not feedbacks:
        return success_response(
            data={"items": [], "total": total, "page": page, "page_size": page_size},
            message="获取成功",
        )

    article_ids = list({f.article_id for f in feedbacks})
    articles = await Article.filter(id__in=article_ids).values_list("id", "title", "knowledge_base_id")
    article_map = {aid: {"title": title, "knowledge_base_id": kb_id} for aid, title, kb_id in articles}

    feedback_user_name = current_user.nickname or current_user.username

    items = []
    for f in feedbacks:
        article_info = article_map.get(f.article_id) or {}
        items.append({
            "id": f.id,
            "article_id": f.article_id,
            "article_title": article_info.get("title"),
            "knowledge_base_id": article_info.get("knowledge_base_id"),
            "feedback_type": f.feedback_type,
            "content": f.content,
            "status": f.status,
            "user_name": feedback_user_name,
            "reply": f.reply,
            "reply_by_id": f.reply_by_id,
            "reply_at": f.reply_at.isoformat() if f.reply_at else None,
            "created_at": f.created_at.isoformat() if f.created_at else None,
            "updated_at": f.updated_at.isoformat() if f.updated_at else None,
        })

    return success_response(
        data={"items": items, "total": total, "page": page, "page_size": page_size},
        message="获取成功",
    )


@router.get("/me/collections", summary="个人收藏", description="分页获取当前用户收藏的文章列表，含文章详情")
async def get_my_collections(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
):
    """个人收藏：取每个文章下最新一条 3/4 为 3 的记录，关联文章详情并分页"""
    conn = Tortoise.get_connection("default")
    uid = current_user.id
    offset = (page - 1) * page_size

    # 总数：当前仍为收藏态的文章数（最新一条 action_type in (3,4) 且为 3）
    count_sql = """
    SELECT COUNT(*) AS total FROM (
        SELECT ai.article_id FROM article_interactions ai
        INNER JOIN (
            SELECT article_id, MAX(created_at) AS max_created
            FROM article_interactions
            WHERE user_id = %s AND action_type IN (3, 4)
            GROUP BY article_id
        ) latest ON ai.article_id = latest.article_id AND ai.created_at = latest.max_created
        INNER JOIN articles a ON a.id = ai.article_id AND a.status > 0
        WHERE ai.user_id = %s AND ai.action_type = 3
    ) t
    """
    _, count_rows = await conn.execute_query(count_sql, [uid, uid])
    total = int(count_rows[0]["total"]) if count_rows else 0

    # 分页：article_id, collected_at，按 collected_at 倒序
    list_sql = """
    SELECT ai.article_id, ai.created_at AS collected_at
    FROM article_interactions ai
    INNER JOIN (
        SELECT article_id, MAX(created_at) AS max_created
        FROM article_interactions
        WHERE user_id = %s AND action_type IN (3, 4)
        GROUP BY article_id
    ) latest ON ai.article_id = latest.article_id AND ai.created_at = latest.max_created
    INNER JOIN articles a ON a.id = ai.article_id AND a.status > 0
    WHERE ai.user_id = %s AND ai.action_type = 3
    ORDER BY ai.created_at DESC
    LIMIT %s OFFSET %s
    """
    _, rows = await conn.execute_query(list_sql, [uid, uid, page_size, offset])
    id_at = [(r["article_id"], r["collected_at"]) for r in rows]

    if not id_at:
        return success_response(
            data={"items": [], "total": total, "page": page, "page_size": page_size},
            message="获取成功",
        )

    article_ids = [a[0] for a in id_at]
    at_map = {a[0]: (a[1].strftime("%Y-%m-%d %H:%M:%S") if hasattr(a[1], "strftime") else str(a[1])) for a in id_at}

    articles = await Article.filter(id__in=article_ids, status__gt=0).prefetch_related("author", "updated_by")
    amap = {a.id: a for a in articles}
    author_ids = list({a.author_id for a in articles})
    updated_ids = list({a.updated_by_id for a in articles if a.updated_by_id})
    user_ids = list(set(author_ids + updated_ids))
    users = await User.filter(id__in=user_ids).all()
    users_map = {u.id: (u.nickname or u.username) for u in users}

    items = []
    for aid in article_ids:
        a = amap.get(aid)
        if not a:
            continue
        items.append(_article_item_dict(a, users_map, "collected_at", at_map.get(aid)))

    return success_response(
        data={"items": items, "total": total, "page": page, "page_size": page_size},
        message="获取成功",
    )


@router.get("/me/likes", summary="个人点赞", description="分页获取当前用户点赞的文章列表，含文章详情")
async def get_my_likes(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
):
    """个人点赞：取每个文章下最新一条 1/2 为 1 的记录，关联文章详情并分页"""
    conn = Tortoise.get_connection("default")
    uid = current_user.id
    offset = (page - 1) * page_size

    count_sql = """
    SELECT COUNT(*) AS total FROM (
        SELECT ai.article_id FROM article_interactions ai
        INNER JOIN (
            SELECT article_id, MAX(created_at) AS max_created
            FROM article_interactions
            WHERE user_id = %s AND action_type IN (1, 2)
            GROUP BY article_id
        ) latest ON ai.article_id = latest.article_id AND ai.created_at = latest.max_created
        INNER JOIN articles a ON a.id = ai.article_id AND a.status > 0
        WHERE ai.user_id = %s AND ai.action_type = 1
    ) t
    """
    _, count_rows = await conn.execute_query(count_sql, [uid, uid])
    total = int(count_rows[0]["total"]) if count_rows else 0

    list_sql = """
    SELECT ai.article_id, ai.created_at AS liked_at
    FROM article_interactions ai
    INNER JOIN (
        SELECT article_id, MAX(created_at) AS max_created
        FROM article_interactions
        WHERE user_id = %s AND action_type IN (1, 2)
        GROUP BY article_id
    ) latest ON ai.article_id = latest.article_id AND ai.created_at = latest.max_created
    INNER JOIN articles a ON a.id = ai.article_id AND a.status > 0
    WHERE ai.user_id = %s AND ai.action_type = 1
    ORDER BY ai.created_at DESC
    LIMIT %s OFFSET %s
    """
    _, rows = await conn.execute_query(list_sql, [uid, uid, page_size, offset])
    id_at = [(r["article_id"], r["liked_at"]) for r in rows]

    if not id_at:
        return success_response(
            data={"items": [], "total": total, "page": page, "page_size": page_size},
            message="获取成功",
        )

    article_ids = [a[0] for a in id_at]
    at_map = {a[0]: (a[1].strftime("%Y-%m-%d %H:%M:%S") if hasattr(a[1], "strftime") else str(a[1])) for a in id_at}

    articles = await Article.filter(id__in=article_ids, status__gt=0).prefetch_related("author", "updated_by")
    amap = {a.id: a for a in articles}
    author_ids = list({a.author_id for a in articles})
    updated_ids = list({a.updated_by_id for a in articles if a.updated_by_id})
    user_ids = list(set(author_ids + updated_ids))
    users = await User.filter(id__in=user_ids).all()
    users_map = {u.id: (u.nickname or u.username) for u in users}

    items = []
    for aid in article_ids:
        a = amap.get(aid)
        if not a:
            continue
        items.append(_article_item_dict(a, users_map, "liked_at", at_map.get(aid)))

    return success_response(
        data={"items": items, "total": total, "page": page, "page_size": page_size},
        message="获取成功",
    )


@router.get("/me/browse-history", summary="个人浏览记录", description="分页获取当前用户浏览记录，按最近浏览时间倒序，含文章详情")
async def get_my_browse_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
):
    """个人浏览记录：action_type=5，按文章去重，以最近一次浏览时间倒序，关联文章详情并分页"""
    conn = Tortoise.get_connection("default")
    uid = current_user.id
    offset = (page - 1) * page_size

    count_sql = """
    SELECT COUNT(*) AS total FROM (
        SELECT ai.article_id
        FROM article_interactions ai
        INNER JOIN articles a ON a.id = ai.article_id AND a.status > 0
        WHERE ai.user_id = %s AND ai.action_type = 5
        GROUP BY ai.article_id
    ) t
    """
    _, count_rows = await conn.execute_query(count_sql, [uid])
    total = int(count_rows[0]["total"]) if count_rows else 0

    list_sql = """
    SELECT ai.article_id, MAX(ai.created_at) AS viewed_at
    FROM article_interactions ai
    INNER JOIN articles a ON a.id = ai.article_id AND a.status > 0
    WHERE ai.user_id = %s AND ai.action_type = 5
    GROUP BY ai.article_id
    ORDER BY viewed_at DESC
    LIMIT %s OFFSET %s
    """
    _, rows = await conn.execute_query(list_sql, [uid, page_size, offset])
    id_at = [(r["article_id"], r["viewed_at"]) for r in rows]

    if not id_at:
        return success_response(
            data={"items": [], "total": total, "page": page, "page_size": page_size},
            message="获取成功",
        )

    article_ids = [a[0] for a in id_at]
    at_map = {a[0]: (a[1].strftime("%Y-%m-%d %H:%M:%S") if hasattr(a[1], "strftime") else str(a[1])) for a in id_at}

    articles = await Article.filter(id__in=article_ids, status__gt=0).prefetch_related("author", "updated_by")
    amap = {a.id: a for a in articles}
    author_ids = list({a.author_id for a in articles})
    updated_ids = list({a.updated_by_id for a in articles if a.updated_by_id})
    user_ids = list(set(author_ids + updated_ids))
    users = await User.filter(id__in=user_ids).all()
    users_map = {u.id: (u.nickname or u.username) for u in users}

    items = []
    for aid in article_ids:
        a = amap.get(aid)
        if not a:
            continue
        items.append(_article_item_dict(a, users_map, "viewed_at", at_map.get(aid)))

    return success_response(
        data={"items": items, "total": total, "page": page, "page_size": page_size},
        message="获取成功",
    )


@router.get(
    "/me/daily-stats",
    summary="个人每日统计",
    description="按日统计当前用户的阅读数、收藏量、点赞数，默认最近一个月；返回格式适用于图表。",
)
async def get_my_daily_stats(
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD，默认约 30 天前"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD，默认今天"),
    current_user: User = Depends(get_current_active_user),
):
    """按日统计：阅读数(action_type=5)、收藏量(action_type=3)、点赞数(action_type=1)。"""
    today = date.today()
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return error_response(400, "end_date 格式应为 YYYY-MM-DD")
    else:
        end = today
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            return error_response(400, "start_date 格式应为 YYYY-MM-DD")
    else:
        start = today - timedelta(days=30)
    if start > end:
        return error_response(400, "start_date 不能大于 end_date")

    # 生成日期序列（含 start、end）
    dates = []
    d = start
    while d <= end:
        dates.append(d.isoformat())
        d += timedelta(days=1)

    conn = Tortoise.get_connection("default")
    uid = current_user.id
    # 使用 00:00:00 与次日 00:00:00 作为范围，兼容各数据库
    ts_start = datetime.combine(start, datetime.min.time())
    ts_end = datetime.combine(end + timedelta(days=1), datetime.min.time())

    async def run_count(action_type: int):
        sql = """
        SELECT DATE(created_at) AS d, COUNT(*) AS c
        FROM article_interactions
        WHERE user_id = %s AND action_type = %s
          AND created_at >= %s AND created_at < %s
        GROUP BY d
        """
        _, rows = await conn.execute_query(sql, [uid, action_type, ts_start, ts_end])
        return {str(r["d"]): int(r["c"]) for r in rows}

    reads_map = await run_count(5)   # 5-浏览/阅读
    cols_map = await run_count(3)    # 3-收藏
    likes_map = await run_count(1)   # 1-点赞

    # 按前端需要的结构：{ date, reads, collections, likes }，与示例的 Month / Domestic / Abroad 对应
    items = [
        {
            "date": d,
            "reads": reads_map.get(d, 0),
            "collections": cols_map.get(d, 0),
            "likes": likes_map.get(d, 0),
        }
        for d in dates
    ]
    return success_response(data=items, message="获取成功")





@router.get("", summary="获取用户列表", description="分页获取所有用户列表，支持状态筛选和关键词搜索")
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[int] = Query(None, description="用户状态筛选：0-禁用，1-启用"),
    keyword: Optional[str] = Query(None, description="关键词搜索（用户名、邮箱、昵称）"),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户列表"""
    query = User.all()
    
    # 状态筛选
    if status is not None:
        if status not in (0, 1):
            return error_response(400, "状态值无效")
        query = query.filter(status=status)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            Q(username__icontains=keyword) |
            Q(email__icontains=keyword) |
            Q(nickname__icontains=keyword)
        )
    
    total = await query.count()
    offset = (page - 1) * page_size
    users = await query.order_by("-created_at").offset(offset).limit(page_size).all()
    
    items = [UserResponse.model_validate(user).model_dump() for user in users]
    
    data = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }
    return success_response(data=data, message="获取成功")


@router.post(
    "",
    summary="创建用户",
    description="创建用户并分配角色，需提供用户名、密码、邮箱及角色ID列表。",
)
async def create_user(
    body: UserCreateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """创建用户，包括用户名、密码、邮箱，并分配角色"""
    # 校验用户名是否已存在
    existing = await User.get_or_none(username=body.username)
    if existing:
        return error_response(400, "用户名已存在")

    # 校验邮箱是否已存在
    existing_email = await User.get_or_none(email=body.email)
    if existing_email:
        return error_response(400, "邮箱已被使用")

    # 校验角色是否存在且启用
    role_ids = list(set(body.role_ids)) if body.role_ids else []
    if role_ids:
        roles = await Role.filter(id__in=role_ids, status=1).all()
        valid_role_ids = {r.id for r in roles}
        if len(valid_role_ids) != len(role_ids):
            invalid_ids = set(role_ids) - valid_role_ids
            return error_response(400, f"部分角色ID不存在或已被禁用：{list(invalid_ids)}")

    async with in_transaction():
        user = await User.create(
            username=body.username,
            password=get_password_hash(body.password),
            email=body.email,
            status=1,
        )

        for role_id in role_ids:
            role = await Role.get(id=role_id)
            await UserRole.create(
                user=user,
                role=role,
                assigned_by=current_user,
                status=1,
            )

    user_data = UserResponse.model_validate(user).model_dump()
    return success_response(data=user_data, message="创建成功")


@router.get("/{user_id}")
async def get_user(user_id: int):
    """获取用户信息"""
    user = await User.get_or_none(id=user_id, status=1)
    if not user:
        return error_response(404, "用户不存在")
    user_data = UserResponse.model_validate(user).model_dump()
    return success_response(data=user_data, message="获取成功")
