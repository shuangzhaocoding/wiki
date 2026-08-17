"""
团队空间相关路由
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from tortoise.transactions import in_transaction
from tortoise.expressions import Q
from app.models.article import Article
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User
from app.models.role import Role, UserRole
from app.models.team_space import TeamSpace, TeamMember
from app.core.dependencies import get_current_active_user
from app.core.response import success_response, error_response
from app.schemas.user import UserResponse
from app.utils.permissions import require_permission

router = APIRouter()


# Schema定义
class TeamSpaceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    visibility: int = 1  # 1-个人可见，2-团队成员可见，3-公开可见
    cover_image: Optional[str] = None


class TeamSpaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[int] = None
    cover_image: Optional[str] = None


class TeamSpaceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner_id: int
    visibility: int
    cover_image: Optional[str] = None
    status: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeamMemberAdd(BaseModel):
    user_id: Optional[int] = None  # 单个用户；与 role_ids 至少传一种
    role_ids: Optional[List[int]] = None  # 系统角色 ID 列表，将拥有这些角色的全部用户加入空间
    role: int = Field(1, description="团队成员角色：0-只读，1-编辑者，2-管理员")


class TeamMemberUpdate(BaseModel):
    role: int  # 角色：0-只读，1-编辑者，2-管理员


class TeamMemberBatchRemove(BaseModel):
    """按系统角色批量移除：移除当前空间中、且拥有指定系统角色的成员（空间创建者不会被移除）"""
    role_ids: List[int] = Field(..., min_length=1, description="系统角色 ID 列表")


@router.post("")
async def create_team_space(
    team_space_data: TeamSpaceCreate,
    current_user: User = Depends(get_current_active_user)
):
    """创建团队空间"""
    # 检查团队空间名称是否已存在
    existing = await TeamSpace.get_or_none(name=team_space_data.name, status=1)
    if existing:
        return error_response(400, "团队空间名称已存在")
    
    async with in_transaction():
        team_space = await TeamSpace.create(
            name=team_space_data.name,
            description=team_space_data.description,
            owner_id=current_user.id,  # 使用owner_id字段，传入用户ID
            visibility=team_space_data.visibility,
            cover_image=team_space_data.cover_image
        )
        # 自动添加创建者为管理员
        await TeamMember.create(
            team_space=team_space,
            user=current_user,
            role=2,  # 管理员
            added_by=current_user
        )
        data = TeamSpaceResponse.model_validate(team_space).model_dump()
        return success_response(data=data, message="创建成功")


@router.get("")
async def get_team_spaces(
    filter_type: Optional[Literal["all", "created", "joined", "invited"]] = Query(
        "all",
        description="筛选类型：all-全部空间，created-我创建的，joined-我加入的，invited-受邀加入",
    ),
    keyword: Optional[str] = Query(None, description="关键词筛选（名称、描述）"),
    visibility: Optional[int] = Query(None, description="可见性筛选（可选，与 filter_type 叠加）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
):
    """获取团队空间列表。支持按类型筛选、关键词搜索与分页。"""
    query = TeamSpace.filter(status=1)

    # 用户加入的团队空间 ID（含受邀）
    member_spaces = await TeamMember.filter(
        user_id=current_user.id, status=1
    ).values_list("team_space_id", flat=True)
    member_space_ids = list(member_spaces) if member_spaces else []

    if filter_type == "created":
        query = query.filter(owner_id=current_user.id)
    elif filter_type == "joined":
        if not member_space_ids:
            query = query.filter(id=-1)  # 无加入记录则结果为空
        else:
            query = query.filter(id__in=member_space_ids)
    elif filter_type == "invited":
        # 受邀加入：是成员且非创建者
        if not member_space_ids:
            query = query.filter(id=-1)
        else:
            query = query.filter(id__in=member_space_ids).exclude(
                owner_id=current_user.id
            )
    else:
        # all：公共空间（visibility>=2）或非公共空间但用户是成员
        base = Q(visibility=3)
        if member_space_ids:
            base |= (Q(visibility__lte=2) & Q(id__in=member_space_ids))
        query = query.filter(base)

    if keyword and keyword.strip():
        k = keyword.strip()
        query = query.filter(
            Q(name__icontains=k) | Q(description__icontains=k)
        )

    if visibility is not None:
        query = query.filter(visibility=visibility)

    total = await query.count()
    offset = (page - 1) * page_size
    team_spaces = await query.order_by("-created_at").offset(offset).limit(page_size).all()

    # 根据 owner_id 获取创建人名称，以及当前用户在空间内的角色
    owner_ids = list({ts.owner_id for ts in team_spaces})
    owners = await User.filter(id__in=owner_ids).all()
    owner_name_map = {u.id: (u.nickname or u.username) for u in owners}

    space_ids = [ts.id for ts in team_spaces]
    members = await TeamMember.filter(
        team_space_id__in=space_ids,
        user_id=current_user.id,
        status=1,
    ).values_list("team_space_id", "role")
    my_role_map = {tid: role for tid, role in members}

    items = []
    for ts in team_spaces:
        d = TeamSpaceResponse.model_validate(ts).model_dump()
        d["owner_name"] = owner_name_map.get(ts.owner_id)
        if ts.owner_id == current_user.id:
            d["my_role"] = 2  # 创建者视为管理员
        else:
            role = my_role_map.get(ts.id)
            if role is not None:
                d["my_role"] = role  # 成员取角色
            elif ts.visibility == 3:
                d["my_role"] = 0  # 公开空间非成员默认为只读
            else:
                d["my_role"] = None  # 非公开且非成员
        items.append(d)

    return success_response(
        data={"items": items, "total": total, "page": page, "page_size": page_size},
        message="获取成功",
    )


@router.get("/{team_space_id}")
async def get_team_space(
    team_space_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """获取团队空间详情"""
    team_space = await TeamSpace.get_or_none(id=team_space_id, status=1)
    if not team_space:
        return error_response(404, "团队空间不存在")
    
    # 检查权限
    await require_permission(current_user, 1, team_space_id, 0)
    
    data = TeamSpaceResponse.model_validate(team_space).model_dump()
    return success_response(data=data, message="获取成功")


@router.put("/{team_space_id}")
async def update_team_space(
    team_space_id: int,
    team_space_data: TeamSpaceUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """更新团队空间"""
    team_space = await TeamSpace.get_or_none(id=team_space_id, status=1)
    if not team_space:
        return error_response(404, "团队空间不存在")
    
    # 检查权限（需要管理员权限）
    if team_space.owner_id != current_user.id:
        await require_permission(current_user, 1, team_space_id, 1)
    
    update_data = team_space_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(team_space, key, value)
    
    await team_space.save()
    data = TeamSpaceResponse.model_validate(team_space).model_dump()
    return success_response(data=data, message="更新成功")


@router.delete("/{team_space_id}")
async def delete_team_space(
    team_space_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """删除团队空间"""
    async with in_transaction():
        team_space = await TeamSpace.get_or_none(id=team_space_id, status=1)
        if not team_space:
            return error_response(404, "团队空间不存在")
        
        # 只有空间管理员可以删除
        if team_space.owner_id != current_user.id:
            await require_permission(current_user, 1, team_space_id, 2)
        team_space.status = 0
        await team_space.save()

        # 软删除该团队空间下所有知识空间下的所有文章
        kb_ids = await KnowledgeBase.filter(team_space_id=team_space_id).values_list("id", flat=True)
        if kb_ids:
            await Article.filter(knowledge_base_id__in=kb_ids).exclude(status=0).update(status=0)
        
        # 软删除该团队空间下的所有知识空间
        await KnowledgeBase.filter(team_space_id=team_space_id, status=1).update(status=0)
        
        
    return success_response(message="删除成功")


@router.post("/{team_space_id}/members")
async def add_team_member(
    team_space_id: int,
    member_data: TeamMemberAdd,
    current_user: User = Depends(get_current_active_user)
):
    """添加团队成员"""
    team_space = await TeamSpace.get_or_none(id=team_space_id, status=1)
    if not team_space:
        return error_response(404, "团队空间不存在")
    if team_space.visibility == 1:
        return error_response(403, "个人空间，仅创建者可见，不可添加成员")

    # 检查权限
    await require_permission(current_user, 1, team_space_id, 2)

    has_user = member_data.user_id is not None
    has_roles = bool(member_data.role_ids and len(member_data.role_ids) > 0)
    if not has_user and not has_roles:
        return error_response(400, "user_id 与 role_ids 至少传一种")

    user_ids_to_add: set = set()
    if member_data.user_id is not None:
        user_ids_to_add.add(member_data.user_id)
    if member_data.role_ids:
        rid_set = list(dict.fromkeys(member_data.role_ids))  # 去重保序
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
        existing_list = await TeamMember.filter(
            team_space_id=team_space_id,
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
                await TeamMember.create(
                    team_space=team_space,
                    user=u,
                    role=member_data.role,
                    added_by=current_user,
                )

    return success_response(message="成员添加成功")


@router.put("/{team_space_id}/members/{user_id}")
async def update_team_member(
    team_space_id: int,
    user_id: int,
    member_data: TeamMemberUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """修改团队成员（角色）"""
    team_space = await TeamSpace.get_or_none(id=team_space_id, status=1)
    if not team_space:
        return error_response(404, "团队空间不存在")
    
    # 检查权限
    await require_permission(current_user, 1, team_space_id, 2)
    
    member = await TeamMember.get_or_none(
        team_space_id=team_space_id,
        user_id=user_id,
        status=1
    )
    if not member:
        return error_response(404, "成员不存在")
    
    # 更新角色
    member.role = member_data.role
    await member.save()
    
    return success_response(message="成员信息更新成功")


@router.delete("/{team_space_id}/members/{user_id}")
async def remove_team_member(
    team_space_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """移除团队成员"""
    team_space = await TeamSpace.get_or_none(id=team_space_id, status=1)
    if not team_space:
        return error_response(404, "团队空间不存在")
    
    # 检查权限
    await require_permission(current_user, 1, team_space_id, 2)
    
    if team_space.owner_id == user_id:
        return error_response(400, "此空间由您创建，不可移除自身")

    member = await TeamMember.get_or_none(
        team_space_id=team_space_id,
        user_id=user_id
    )
    if not member:
        return error_response(404, "成员不存在")

    member.status = 0
    await member.save()
    return success_response(message="成员移除成功")


@router.post(
    "/{team_space_id}/members/batch-remove",
    summary="按系统角色批量移除成员",
    description="根据系统角色 ID 解析用户，将本团队中属于这些角色的有效成员移除（软删除）；空间创建者不会被移除。",
)
async def batch_remove_team_members_by_roles(
    team_space_id: int,
    body: TeamMemberBatchRemove,
    current_user: User = Depends(get_current_active_user),
):
    """按系统角色批量移除团队成员。"""
    team_space = await TeamSpace.get_or_none(id=team_space_id, status=1)
    if not team_space:
        return error_response(404, "团队空间不存在")

    await require_permission(current_user, 1, team_space_id, 2)

    rid_set = list(dict.fromkeys(body.role_ids))
    roles = await Role.filter(id__in=rid_set, status=1).all()
    valid_role_ids = {r.id for r in roles}
    if len(valid_role_ids) != len(rid_set):
        invalid = set(rid_set) - valid_role_ids
        return error_response(400, f"无效或已禁用的角色ID: {sorted(invalid)}")

    user_ids_from_roles = set(
        await UserRole.filter(role_id__in=rid_set, status=1).values_list("user_id", flat=True)
    )
    user_ids_from_roles.discard(team_space.owner_id)
    if not user_ids_from_roles:
        return success_response(data={"removed_count": 0}, message="没有可移除的成员")

    members = await TeamMember.filter(
        team_space_id=team_space_id,
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


@router.get(
    "/search/members",
    summary="搜索用户",
    description="按关键词搜索用户（邮箱/用户名/昵称），或按团队空间获取成员。keyword 与 team_space_id 至少传一个；传 team_space_id 时标注 is_member。",
)
async def search_users(
    keyword: Optional[str] = Query(None, description="搜索关键词（匹配邮箱、用户名、昵称）；与 team_space_id 至少传一个"),
    team_space_id: Optional[int] = Query(None, description="团队空间ID；不为空时限定为该空间成员并标注 is_member"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
):
    """搜索用户：keyword 匹配邮箱/用户名/昵称；传 team_space_id 时限定为空间成员并标注 is_member。"""
    k = keyword.strip() if (keyword and keyword.strip()) else ""
    if not k and team_space_id is None:
        return error_response(400, "关键词与团队空间ID至少传一个")

    member_ids: set = set()
    member_info_map: dict = {}  # user_id -> {"role": int, "joined_at": datetime}
    if team_space_id is not None:
        team_space = await TeamSpace.get_or_none(id=team_space_id, status=1)
        if not team_space:
            return error_response(404, "团队空间不存在")
        await require_permission(current_user, 1, team_space_id, 0)
        members = await TeamMember.filter(
            team_space_id=team_space_id, status=1
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
    if team_space_id is not None and not k:
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
        if team_space_id is not None:
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
