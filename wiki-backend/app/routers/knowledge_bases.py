"""
知识库相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from tortoise.expressions import Q
from tortoise.transactions import in_transaction
from app.enums import ResourceType
from app.models.article import Article
from app.models.user import User
from app.models.role import Role, UserRole
from app.models.knowledge_base import KnowledgeBase, KnowledgeBaseMember
from app.models.team_space import TeamSpace, TeamMember
from app.core.dependencies import get_current_active_user
from app.core.response import success_response, error_response
from app.schemas.user import UserResponse
from app.utils.permissions import require_permission

router = APIRouter()


async def _resolve_knowledge_base_my_role(
    kb: KnowledgeBase,
    current_user: User,
    team_space: Optional[TeamSpace] = None,
) -> int:
    """当前用户在此知识库的有效角色：0-只读，1-编辑者，2-管理员。创建者优先；否则知识库成员；否则级联所属团队空间。"""
    if kb.owner_id == current_user.id:
        return 2
    kb_mem = await KnowledgeBaseMember.get_or_none(
        knowledge_base_id=kb.id, user_id=current_user.id, status=1
    )
    if kb_mem:
        return kb_mem.role

    ts = team_space if team_space is not None else await TeamSpace.get_or_none(
        id=kb.team_space_id, status=1
    )
    if not ts:
        return 0
    if ts.owner_id == current_user.id:
        return 2
    tm = await TeamMember.get_or_none(
        team_space_id=ts.id, user_id=current_user.id, status=1
    )
    if tm:
        return tm.role
    return 0


async def _direct_knowledge_base_role(kb: KnowledgeBase, current_user: User) -> Optional[int]:
    """知识库维度角色：创建者为 2；否则取 KnowledgeBaseMember.role；无成员记录且非创建者为 null。"""
    if kb.owner_id == current_user.id:
        return 2
    m = await KnowledgeBaseMember.get_or_none(
        knowledge_base_id=kb.id, user_id=current_user.id, status=1
    )
    return m.role if m else None


async def _direct_team_space_role(ts: Optional[TeamSpace], current_user: User) -> Optional[int]:
    """所属团队空间维度角色：空间创建者为 2；否则取 TeamMember.role；无成员记录且非创建者为 null。"""
    if not ts:
        return None
    if ts.owner_id == current_user.id:
        return 2
    tm = await TeamMember.get_or_none(
        team_space_id=ts.id, user_id=current_user.id, status=1
    )
    return tm.role if tm else None


class KnowledgeBaseCreate(BaseModel):
    team_space_id: int
    name: str
    description: Optional[str] = None
    visibility: Optional[int] = None  # 默认继承团队空间
    icon: Optional[str] = None


class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[int] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None


class KnowledgeBaseResponse(BaseModel):
    id: int
    team_space_id: int
    team_space_name: Optional[str] = None
    name: str
    description: Optional[str] = None
    owner_id: int
    owner_name: Optional[str] = None
    visibility: int
    icon: Optional[str] = None
    sort_order: int
    status: int
    my_role: Optional[int] = None  # 当前用户有效角色（级联）：0-只读，1-编辑者，2-管理员
    knowledge_base_role: Optional[int] = Field(
        None,
        description="在知识库维度：创建者/成员表为 0/1/2；既非创建者也无成员记录时为 null",
    )
    team_space_role: Optional[int] = Field(
        None,
        description="在所属团队空间维度：空间创建者/成员表为 0/1/2；既非创建者也无成员记录时为 null",
    )
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KnowledgeBaseMemberAdd(BaseModel):
    user_id: Optional[int] = None  # 单个用户；与 role_ids 至少传一种
    role_ids: Optional[List[int]] = None  # 系统角色 ID 列表，将拥有这些角色的全部用户加入知识库
    role: int = Field(1, description="知识库成员角色：0-只读，1-编辑者，2-管理员")


class KnowledgeBaseMemberBatchRemove(BaseModel):
    """按系统角色批量移除：移除本知识库中、且拥有指定系统角色的成员（知识库创建者不会被移除）"""
    role_ids: List[int] = Field(..., min_length=1, description="系统角色 ID 列表")


class KnowledgeBaseMemberUpdate(BaseModel):
    role: int  # 角色：0-只读，1-编辑者，2-管理员


@router.post("")
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_active_user)
):
    """创建知识库"""
    # 检查团队空间是否存在并有权限
    team_space = await TeamSpace.get_or_none(id=kb_data.team_space_id, status=1)
    if not team_space:
        return error_response(404, "团队空间不存在")
    
    await require_permission(user=current_user, resource_type=ResourceType.TEAM_SPACE, resource_id=kb_data.team_space_id, required_permission=1)
    
    name_stripped = kb_data.name.strip() if kb_data.name else ""
    if not name_stripped:
        return error_response(400, "知识库名称不能为空")
    dup = await KnowledgeBase.get_or_none(
        team_space_id=kb_data.team_space_id,
        name=name_stripped,
        status=1,
    )
    if dup:
        return error_response(400, "该团队空间下已存在同名知识库")
    
    # 如果未指定可见性，继承团队空间的可见性
    visibility = kb_data.visibility or team_space.visibility
    
    async with in_transaction():
        kb = await KnowledgeBase.create(
            team_space=team_space,
            name=name_stripped,
            description=kb_data.description,
            owner=current_user,
            visibility=visibility,
            icon=kb_data.icon
        )
        # 自动添加创建者为管理员
        await KnowledgeBaseMember.create(
            knowledge_base=kb,
            user=current_user,
            role=2,  # 管理员
            added_by=current_user
        )
    
    data = KnowledgeBaseResponse.model_validate(kb).model_dump()
    data["owner_name"] = current_user.nickname or current_user.username
    return success_response(data=data, message="创建成功")


@router.get("")
async def get_knowledge_bases(
    filter_type: Optional[Literal["all", "created", "joined", "invited"]] = Query(
        "all",
        description="筛选类型：all-全部知识库，created-我创建的，joined-我加入的，invited-受邀加入",
    ),
    keyword: Optional[str] = Query(None, description="关键词筛选（名称、描述）"),
    visibility: Optional[int] = Query(None, description="可见性筛选（可选，与 filter_type 叠加）"),
    team_space_id: Optional[int] = Query(None, description="团队空间ID筛选（可选，与 filter_type 叠加）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
):
    """获取知识库列表。支持按类型筛选、关键词搜索、可见性筛选、团队空间筛选与分页。"""
    query = KnowledgeBase.filter(status=1)
    
    # 如果指定了团队空间ID，先检查权限并筛选
    if team_space_id:
        # 检查团队空间权限
        await require_permission(user=current_user, resource_type=ResourceType.TEAM_SPACE, resource_id=team_space_id, required_permission=0)
        query = query.filter(team_space_id=team_space_id)
    
    # 用户加入的知识库ID（通过 KnowledgeBaseMember）
    member_kbs = await KnowledgeBaseMember.filter(
        user_id=current_user.id, status=1
    ).values_list("knowledge_base_id", flat=True)
    member_kb_ids = list(member_kbs) if member_kbs else []

    # 用户加入的团队空间：成员表 + 空间创建者（用于「未加入知识库但属团队空间成员」可见性）
    tm_rows = await TeamMember.filter(
        user_id=current_user.id, status=1
    ).values_list("team_space_id", "role")
    ts_role_map: dict = {tid: r for tid, r in tm_rows}
    owned_ts_ids = await TeamSpace.filter(
        owner_id=current_user.id, status=1
    ).values_list("id", flat=True)
    for tid in owned_ts_ids:
        ts_role_map[tid] = max(ts_role_map.get(tid, 0), 2)
    member_team_space_ids = list(ts_role_map.keys())

    if filter_type == "created":
        query = query.filter(owner_id=current_user.id)
    elif filter_type == "joined":
        if not member_kb_ids:
            query = query.filter(id=-1)  # 无加入记录则结果为空
        else:
            query = query.filter(id__in=member_kb_ids)
    elif filter_type == "invited":
        # 受邀加入：是成员且非创建者
        if not member_kb_ids:
            query = query.filter(id=-1)
        else:
            query = query.filter(id__in=member_kb_ids).exclude(
                owner_id=current_user.id
            )
    else:
        # all：公共；或非公共且用户是知识库成员；或用户创建；或「成员可见」且用户是所属团队空间成员（未入知识库成员表也可见）
        base = Q(visibility=3)
        if member_kb_ids:
            base |= (Q(visibility__lte=2) & Q(id__in=member_kb_ids))
        base |= Q(owner_id=current_user.id)
        if member_team_space_ids:
            base |= Q(visibility=2, team_space_id__in=member_team_space_ids)
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
    knowledge_bases = await query.order_by("sort_order").offset(offset).limit(page_size).all()
    ts_ids = list({kb.team_space_id for kb in knowledge_bases})
    ts_list = await TeamSpace.filter(id__in=ts_ids).values_list("id", "name") if ts_ids else []
    ts_map = {t[0]: t[1] for t in ts_list}
    owner_name_map = {}
    owner_ids = list({kb.owner_id for kb in knowledge_bases})
    if owner_ids:
        owners = await User.filter(id__in=owner_ids).all()
        owner_name_map = {u.id: (u.nickname or u.username) for u in owners}
    kb_ids = [kb.id for kb in knowledge_bases]
    member_roles = await KnowledgeBaseMember.filter(
        knowledge_base_id__in=kb_ids, user_id=current_user.id, status=1
    ).values_list("knowledge_base_id", "role")
    member_role_map = {r[0]: r[1] for r in member_roles}
    items = []
    for kb in knowledge_bases:
        d = KnowledgeBaseResponse.model_validate(kb).model_dump()
        d["team_space_name"] = ts_map.get(kb.team_space_id)
        d["owner_name"] = owner_name_map.get(kb.owner_id)
        if kb.owner_id == current_user.id:
            d["my_role"] = 2
        elif kb.id in member_role_map:
            d["my_role"] = member_role_map[kb.id]
        elif kb.team_space_id in ts_role_map:
            d["my_role"] = ts_role_map[kb.team_space_id]
        else:
            d["my_role"] = 0
        items.append(d)
    return success_response(
        data={"items": items, "total": total, "page": page, "page_size": page_size},
        message="获取成功",
    )


@router.get("/{kb_id}")
async def get_knowledge_base(
    kb_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """获取知识库详情"""
    kb = await KnowledgeBase.filter(id=kb_id, status=1).select_related("team_space").first()
    if not kb:
        return error_response(404, "知识库不存在")
    
    auth_check_result = await require_permission(user=current_user, resource_type=ResourceType.KNOWLEDGE_BASE, resource_id=kb_id, required_permission=0)
    data = KnowledgeBaseResponse.model_validate(kb).model_dump()
    ts = await kb.team_space
    data["team_space_name"] = ts.name if ts else None
    data["my_role"] = auth_check_result.role
    data["knowledge_base_role"] = auth_check_result.role
    data["team_space_role"] = auth_check_result.role
    return success_response(data=data, message="获取成功")


@router.put("/{kb_id}")
async def update_knowledge_base(
    kb_id: int,
    kb_data: KnowledgeBaseUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """更新知识库"""
    kb = await KnowledgeBase.get_or_none(id=kb_id, status=1)
    if not kb:
        return error_response(404, "知识库不存在")
    
    await require_permission(user=current_user, resource_type=ResourceType.KNOWLEDGE_BASE, resource_id=kb_id, required_permission=1)
    
    update_data = kb_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(kb, key, value)
    
    await kb.save()
    owner = await User.get_or_none(id=kb.owner_id)
    data = KnowledgeBaseResponse.model_validate(kb).model_dump()
    data["owner_name"] = (owner.nickname or owner.username) if owner else None
    return success_response(data=data, message="更新成功")


@router.delete("/{kb_id}")
async def delete_knowledge_base(
    kb_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """删除知识库"""
    async with in_transaction():
        kb = await KnowledgeBase.get_or_none(id=kb_id, status=1)
        if not kb:
            return error_response(404, "知识库不存在")
        
        await require_permission(user=current_user, resource_type=ResourceType.KNOWLEDGE_BASE, resource_id=kb_id, required_permission=2)
        
        # 软删除该知识库下的所有文章
        await Article.filter(knowledge_base_id=kb_id).exclude(status=0).update(status=0)
        
        kb.status = 0
        await kb.save()
    return success_response(message="删除成功")


@router.post(
    "/{kb_id}/members",
    summary="添加知识库成员（支持批量）",
    description="user_id 与系统 role_ids 至少传一种；传 role_ids 时将拥有这些系统角色的用户全部加入，并使用统一的成员 role。",
)
async def add_knowledge_base_member(
    kb_id: int,
    member_data: KnowledgeBaseMemberAdd,
    current_user: User = Depends(get_current_active_user)
):
    """添加知识库成员；可传 user_id 或系统 role_ids 批量添加。"""
    kb = await KnowledgeBase.get_or_none(id=kb_id, status=1)
    if not kb:
        return error_response(404, "知识库不存在")
    
    if kb.visibility == 1:
        return error_response(403, "个人知识库，仅创建者可见，不可添加成员")

    await require_permission(user=current_user, resource_type=ResourceType.KNOWLEDGE_BASE, resource_id=kb_id, required_permission=1)

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
        existing_list = await KnowledgeBaseMember.filter(
            knowledge_base_id=kb_id,
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
                await KnowledgeBaseMember.create(
                    knowledge_base=kb,
                    user=u,
                    role=member_data.role,
                    added_by=current_user,
                )

    return success_response(message="成员添加成功")


@router.put("/{kb_id}/members/{user_id}")
async def update_knowledge_base_member(
    kb_id: int,
    user_id: int,
    member_data: KnowledgeBaseMemberUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """修改知识库成员（角色）"""
    kb = await KnowledgeBase.get_or_none(id=kb_id, status=1)
    if not kb:
        return error_response(404, "知识库不存在")
    
    # 检查权限
    await require_permission(user=current_user, resource_type=ResourceType.KNOWLEDGE_BASE, resource_id=kb_id, required_permission=2)
    
    member = await KnowledgeBaseMember.get_or_none(
        knowledge_base_id=kb_id,
        user_id=user_id,
        status=1
    )
    if not member:
        return error_response(404, "成员不存在")
    
    # 更新角色
    member.role = member_data.role
    await member.save()
    
    return success_response(message="成员信息更新成功")


@router.delete("/{kb_id}/members/{user_id}")
async def remove_knowledge_base_member(
    kb_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """移除知识库成员"""
    kb = await KnowledgeBase.get_or_none(id=kb_id, status=1)
    if not kb:
        return error_response(404, "知识库不存在")
    
    # 检查权限
    await require_permission(user=current_user, resource_type=ResourceType.KNOWLEDGE_BASE, resource_id=kb_id, required_permission=2)
    
    if kb.owner_id == user_id:
        return error_response(400, "此知识库由您创建，不可移除自身")

    member = await KnowledgeBaseMember.get_or_none(
        knowledge_base_id=kb_id,
        user_id=user_id
    )
    if not member:
        return error_response(404, "成员不存在")

    member.status = 0
    await member.save()
    return success_response(message="成员移除成功")


@router.post(
    "/{kb_id}/members/batch-remove",
    summary="按系统角色批量移除知识库成员",
    description="根据系统角色 ID 解析用户，将本知识库中属于这些角色的有效成员移除（软删除）；知识库创建者不会被移除。",
)
async def batch_remove_knowledge_base_members_by_roles(
    kb_id: int,
    body: KnowledgeBaseMemberBatchRemove,
    current_user: User = Depends(get_current_active_user),
):
    """按系统角色批量移除知识库成员。"""
    kb = await KnowledgeBase.get_or_none(id=kb_id, status=1)
    if not kb:
        return error_response(404, "知识库不存在")

    await require_permission(user=current_user, resource_type=ResourceType.KNOWLEDGE_BASE, resource_id=kb_id, required_permission=2)

    rid_set = list(dict.fromkeys(body.role_ids))
    roles = await Role.filter(id__in=rid_set, status=1).all()
    valid_role_ids = {r.id for r in roles}
    if len(valid_role_ids) != len(rid_set):
        invalid = set(rid_set) - valid_role_ids
        return error_response(400, f"无效或已禁用的角色ID: {sorted(invalid)}")

    user_ids_from_roles = set(
        await UserRole.filter(role_id__in=rid_set, status=1).values_list("user_id", flat=True)
    )
    user_ids_from_roles.discard(kb.owner_id)
    if not user_ids_from_roles:
        return success_response(data={"removed_count": 0}, message="没有可移除的成员")

    members = await KnowledgeBaseMember.filter(
        knowledge_base_id=kb_id,
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
    summary="搜索知识库成员",
    description="根据知识库ID搜索知识库成员，支持关键词过滤（匹配邮箱、用户名、昵称）",
)
async def search_knowledge_base_members(
    knowledge_base_id: int,
    keyword: Optional[str] = Query(None, description="搜索关键词（匹配邮箱、用户名、昵称）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
):
    """根据知识库ID搜索知识库成员"""
    # 检查知识库是否存在并有权限
    k = keyword.strip() if (keyword and keyword.strip()) else ""

    member_ids: set = set()
    member_info_map: dict = {}  # user_id -> {"role": int, "joined_at": datetime}
    if knowledge_base_id is not None:
        knowledge_base = await KnowledgeBase.get_or_none(id=knowledge_base_id, status=1)
        if not knowledge_base:
            return error_response(404, "知识库不存在")
        await require_permission(user=current_user, resource_type=ResourceType.KNOWLEDGE_BASE, resource_id=knowledge_base_id, required_permission=0)
        members = await KnowledgeBaseMember.filter(
            knowledge_base_id=knowledge_base_id, status=1
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
    if knowledge_base_id is not None and not k:
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
        if knowledge_base_id is not None:
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
