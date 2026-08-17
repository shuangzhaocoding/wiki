"""
评论相关路由
"""
from fastapi import APIRouter, Depends
from typing import Optional, Tuple
from datetime import datetime, timezone
from pydantic import BaseModel
from tortoise.transactions import in_transaction
from app.models.user import User
from app.models.comment import Comment, CommentReaction
from app.models.article import Article, ArticleStats
from app.models.notification import Notification
from app.core.dependencies import get_current_active_user
from app.core.response import success_response, error_response
from app.utils.permissions import require_permission

router = APIRouter()


class CommentCreate(BaseModel):
    article_id: int
    parent_id: Optional[int] = None  # 回复的评论ID
    content: str


class CommentUpdate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    article_id: int
    user_id: int
    parent_id: Optional[int] = None
    content: str
    status: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


def format_time_ago(dt: datetime) -> str:
    """格式化时间为相对时间显示"""
    now = datetime.now(timezone.utc)
    # 确保dt有时区信息
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    diff = now - dt
    seconds = int(diff.total_seconds())
    
    if seconds < 0:
        return "刚刚"
    elif seconds < 60:
        return "刚刚" if seconds < 10 else f"{seconds}秒前"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}分钟前"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours}小时前"
    else:
        # 超过一天显示实际日期
        return dt.strftime("%Y-%m-%d")


def build_comment_response(
    comment: Comment,
    users_map: dict,
    first_comment_id: Optional[int] = None,
    reply_comment_id: Optional[int] = None,
    reply_user_info: Optional[dict] = None,
    reaction_map: Optional[dict] = None,
) -> dict:
    """构建单个评论的响应数据。reaction_map: comment_id -> 1(点赞) 或 2(踩)，用于当前用户状态。"""
    user_info = users_map.get(comment.user_id, {})
    r = reaction_map or {}
    action = r.get(comment.id)
    out = {
        "id": comment.id,
        "article_id": comment.article_id,
        "user_id": comment.user_id,
        "user_name": user_info.get("nickname") or user_info.get("username", ""),
        "username": user_info.get("username", ""),
        "avatar": user_info.get("avatar", ""),
        "comment": comment.content,
        "first_comment_id": first_comment_id,
        "reply_comment_id": reply_comment_id,
        "reply_user_id": reply_user_info.get("id") if reply_user_info else None,
        "reply_user_name": reply_user_info.get("nickname") or reply_user_info.get("username") if reply_user_info else None,
        "create_time": format_time_ago(comment.created_at),
        "update_time": format_time_ago(comment.updated_at) if comment.updated_at != comment.created_at else None,
        "like_count": getattr(comment, "like_count", 0),
        "dislike_count": getattr(comment, "dislike_count", 0),
        "is_liked": action == 1,
        "is_disliked": action == 2,
        "children": [],
    }
    return out


@router.post("")
async def create_comment(
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user)
):
    """创建评论"""
    # 检查文章是否存在并有权限
    article = await Article.get_or_none(id=comment_data.article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    
    await require_permission(current_user, 3, comment_data.article_id, 0)
    
    first_comment_id = None
    reply_to_user_id = None
    parent_id = comment_data.parent_id
    
    # 如果指定了父评论，检查父评论是否存在
    if parent_id:
        parent = await Comment.get_or_none(id=parent_id, status=1)
        if not parent:
            return error_response(404, "父评论不存在")
        if parent.article_id != comment_data.article_id:
            return error_response(400, "父评论必须属于同一文章")
        
        # 设置被回复的用户
        reply_to_user_id = parent.user_id
        
        # 找到一级评论（根评论）
        if parent.first_comment_id is None:
            # 父评论就是一级评论
            first_comment_id = parent.id
        else:
            # 父评论不是一级评论，继承其first_comment_id
            first_comment_id = parent.first_comment_id
    
    comment = await Comment.create(
        article=article,
        user=current_user,
        parent_id=parent_id,
        first_comment_id=first_comment_id,
        reply_to_user_id=reply_to_user_id,
        content=comment_data.content
    )
    
    # 更新文章统计的评论数
    stats, _ = await ArticleStats.get_or_create(article=article)
    stats.comment_count += 1
    await stats.save()

    # 创建评论通知：
    # 1. 如果是回复他人评论，则通知被回复用户
    # 2. 否则通知文章作者（如果作者不是自己）
    if reply_to_user_id and reply_to_user_id != current_user.id:
        await Notification.create(
            user_id=reply_to_user_id,
            type="comment_reply",
            title="评论回复通知",
            content=f"您有新的评论回复，请及时处理，可点击链接查看详情， 已读忽略",
            link=f"/articles/{article.knowledge_base_id}?articleId={article.id}&tab=comments",
            is_read=0,
        )
    elif article.author_id != current_user.id:
        await Notification.create(
            user_id=article.author_id,
            type="article_comment",
            title="文章评论通知",
            content=f"您有新的文章评论，请及时处理，可点击链接查看详情， 已读忽略",
            link=f"/articles/{article.knowledge_base_id}?articleId={article.id}&tab=comments",
            is_read=0,
        )
    
    # 获取用户信息
    user_info = {
        "id": current_user.id,
        "username": current_user.username,
        "nickname": current_user.nickname,
        "avatar": current_user.avatar,
    }
    
    # 获取被回复用户信息
    reply_user_info = None
    if reply_to_user_id:
        reply_user = await User.get_or_none(id=reply_to_user_id)
        if reply_user:
            reply_user_info = {
                "id": reply_user.id,
                "username": reply_user.username,
                "nickname": reply_user.nickname,
            }
    
    data = build_comment_response(
        comment,
        {current_user.id: user_info},
        first_comment_id,
        parent_id,
        reply_user_info
    )
    
    return success_response(data=data, message="评论成功")


@router.get("/article/{article_id}")
async def get_article_comments(
    article_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """获取文章评论列表（树形结构）"""
    article = await Article.get_or_none(id=article_id, status__gt=0)
    if not article:
        return error_response(404, "文章不存在")
    
    await require_permission(current_user, 3, article_id, 0)
    
    # 获取所有评论，按创建时间升序（最早的在前）
    comments = await Comment.filter(article_id=article_id, status=1).order_by("created_at").all()
    
    if not comments:
        return success_response(data=[], message="获取成功")
    
    # 批量获取所有相关用户信息
    user_ids = set()
    for comment in comments:
        user_ids.add(comment.user_id)
        if comment.reply_to_user_id:
            user_ids.add(comment.reply_to_user_id)
    
    users = await User.filter(id__in=list(user_ids)).all()
    users_map = {
        user.id: {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "avatar": user.avatar,
        }
        for user in users
    }
    
    # 当前用户对每条评论的点赞/踩状态 comment_id -> 1(点赞) | 2(踩)
    comment_ids = [c.id for c in comments]
    reactions = await CommentReaction.filter(
        comment_id__in=comment_ids,
        user_id=current_user.id,
    ).values_list("comment_id", "action_type")
    reaction_map = {cid: at for cid, at in reactions}

    # 分离一级评论和回复
    root_comments = []  # 一级评论（parent_id为null）
    replies_by_first_comment = {}  # 按一级评论ID分组的回复

    for comment in comments:
        if comment.parent_id is None:
            root_comments.append(comment)
        else:
            first_id = comment.first_comment_id
            if first_id not in replies_by_first_comment:
                replies_by_first_comment[first_id] = []
            replies_by_first_comment[first_id].append(comment)

    result = []
    for root_comment in root_comments:
        root_data = build_comment_response(
            root_comment,
            users_map,
            None,
            None,
            None,
            reaction_map=reaction_map,
        )
        replies = replies_by_first_comment.get(root_comment.id, [])
        children = []
        for reply in replies:
            reply_user_info = None
            if reply.reply_to_user_id:
                reply_user_info = users_map.get(reply.reply_to_user_id)
            reply_data = build_comment_response(
                reply,
                users_map,
                reply.first_comment_id,
                reply.parent_id,
                reply_user_info,
                reaction_map=reaction_map,
            )
            children.append(reply_data)
        root_data["children"] = children
        result.append(root_data)
    
    return success_response(data=result, message="获取成功")


@router.put("/{comment_id}")
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """更新评论"""
    comment = await Comment.get_or_none(id=comment_id, status=1)
    if not comment:
        return error_response(404, "评论不存在")
    
    # 只能修改自己的评论
    if comment.user_id != current_user.id:
        return error_response(403, "只能修改自己的评论")
    
    comment.content = comment_data.content
    await comment.save()
    
    data = CommentResponse.model_validate(comment).model_dump()
    return success_response(data=data, message="更新成功")


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """删除评论"""
    comment = await Comment.get_or_none(id=comment_id, status=1)
    if not comment:
        return error_response(404, "评论不存在")
    
    # 可以删除自己的评论或文章作者/管理员可以删除
    if comment.user_id != current_user.id:
        article = await comment.article
        if article.author_id != current_user.id:
            await require_permission(current_user, 3, article.id, 2)
    
    comment.status = 0
    await comment.save()

    # 更新文章统计的评论数
    article = await comment.article
    stats, _ = await ArticleStats.get_or_create(article=article)
    stats.comment_count = max(0, stats.comment_count - 1)
    await stats.save()

    return success_response(message="删除成功")


def _reaction_state(reaction: Optional[CommentReaction]) -> Tuple[bool, bool]:
    if not reaction:
        return False, False
    return (reaction.action_type == 1, reaction.action_type == 2)


@router.post(
    "/{comment_id}/like",
    summary="点赞评论",
    description="点赞评论。同一用户对同一条评论只能点赞或踩其一；已点赞再次调用即取消点赞，已踩则切换为点赞。",
)
async def like_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """点赞评论。互斥：不能同时点赞与踩；再次点赞则取消。"""
    comment = await Comment.get_or_none(id=comment_id, status=1)
    if not comment:
        return error_response(404, "评论不存在")
    await require_permission(current_user, 3, comment.article_id, 0)

    async with in_transaction():
        existing = await CommentReaction.get_or_none(comment_id=comment_id, user_id=current_user.id)
        if existing is None:
            await CommentReaction.create(comment_id=comment_id, user_id=current_user.id, action_type=1)
            comment.like_count += 1
        elif existing.action_type == 1:
            await existing.delete()
            comment.like_count = max(0, comment.like_count - 1)
        else:
            existing.action_type = 1
            await existing.save()
            comment.dislike_count = max(0, comment.dislike_count - 1)
            comment.like_count += 1
        await comment.save()

    cur = await CommentReaction.get_or_none(comment_id=comment_id, user_id=current_user.id)
    is_liked, is_disliked = _reaction_state(cur)
    return success_response(
        data={"like_count": comment.like_count, "dislike_count": comment.dislike_count, "is_liked": is_liked, "is_disliked": is_disliked},
        message="点赞成功" if is_liked else "已取消点赞",
    )


@router.post(
    "/{comment_id}/dislike",
    summary="踩评论",
    description="踩评论。同一用户对同一条评论只能点赞或踩其一；已踩再次调用即取消踩，已点赞则切换为踩。",
)
async def dislike_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """踩评论。互斥：不能同时点赞与踩；再次踩则取消。"""
    comment = await Comment.get_or_none(id=comment_id, status=1)
    if not comment:
        return error_response(404, "评论不存在")
    await require_permission(current_user, 3, comment.article_id, 0)

    async with in_transaction():
        existing = await CommentReaction.get_or_none(comment_id=comment_id, user_id=current_user.id)
        if existing is None:
            await CommentReaction.create(comment_id=comment_id, user_id=current_user.id, action_type=2)
            comment.dislike_count += 1
        elif existing.action_type == 2:
            await existing.delete()
            comment.dislike_count = max(0, comment.dislike_count - 1)
        else:
            existing.action_type = 2
            await existing.save()
            comment.like_count = max(0, comment.like_count - 1)
            comment.dislike_count += 1
        await comment.save()

    cur = await CommentReaction.get_or_none(comment_id=comment_id, user_id=current_user.id)
    is_liked, is_disliked = _reaction_state(cur)
    return success_response(
        data={"like_count": comment.like_count, "dislike_count": comment.dislike_count, "is_liked": is_liked, "is_disliked": is_disliked},
        message="踩成功" if is_disliked else "已取消踩",
    )
