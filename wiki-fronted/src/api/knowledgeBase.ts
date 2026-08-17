import request from './request'

// 知识库创建请求
export interface KnowledgeBaseCreate {
  team_space_id: number
  name: string
  description?: string | null
  visibility?: number | null
  icon?: string | null
}

// 知识库更新请求
export interface KnowledgeBaseUpdate {
  name?: string | null
  description?: string | null
  visibility?: number | null
  icon?: string | null
  sort_order?: number | null
}

// 知识库响应
export interface KnowledgeBase {
  id: number
  team_space_id: number
  team_space_name?: string | null
  name: string
  description?: string | null
  visibility: number
  icon?: string | null
  sort_order?: number | null
  created_at?: string
  updated_at?: string
  owner_id?: number
  owner_name?: string | null // 创建者名称
  my_role?: number | null // 我的角色：0-只读，1-编辑者，2-管理员
  /** 当前用户在团队空间中的成员角色（GET /knowledge-bases/{id}） */
  team_space_role?: number | null
  /** 当前用户在知识库中的成员角色（GET /knowledge-bases/{id}） */
  knowledge_base_role?: number | null
}

// 知识库列表响应
export interface KnowledgeBaseListResponse {
  items: KnowledgeBase[]
  total: number
}

// 知识库筛选参数
export interface KnowledgeBaseFilterParams {
  filter_type?: 'created' | 'joined' | 'invited' | 'all' | null // 筛选类型：我创建的、我加入的、受邀加入
  keyword?: string | null // 搜索关键词（所有tab都可以使用）
  visibility?: number | null // 可见性筛选
  page?: number | null // 页码
  page_size?: number | null // 每页数量
  team_space_id?: number | null // 团队空间ID
}

// 知识库成员搜索参数
export interface KnowledgeBaseMemberSearchParams {
  knowledge_base_id: number // 知识库ID（必需）
  keyword?: string // 搜索关键词
  is_member?: boolean | null // 是否为成员（null表示全部）
  /** 按系统角色 ID 筛选（多选） */
  role_ids?: number[]
  page?: number // 页码
  page_size?: number // 每页数量
}

/** 添加成员：单用户 user_id + role；按系统角色批量 role_ids + 统一 role */
export interface KnowledgeBaseMemberAdd {
  user_id?: number
  role?: number
  role_ids?: number[]
}

/** 按系统角色批量移除 POST /knowledge-bases/{id}/members/batch-remove */
export interface KnowledgeBaseMemberBatchRemove {
  role_ids: number[]
}

/** 知识库标签（GET /knowledge-bases/{kb_id}/tags 等，字段以后端为准） */
export interface KnowledgeBaseTag {
  id: number
  knowledge_base_id?: number
  name: string
  color?: string | null
  created_at?: string
  updated_at?: string
}

/** POST /knowledge-bases/{kb_id}/tags */
export interface KnowledgeBaseTagCreate {
  name: string
  color?: string | null
}

/** PUT /knowledge-bases/{kb_id}/tags/{tag_id} */
export interface KnowledgeBaseTagUpdate {
  name?: string | null
  color?: string | null
}

// 知识库成员搜索项
export interface KnowledgeBaseMemberSearchItem {
  id: number
  user_id: number
  username?: string
  email?: string
  is_member?: boolean // 是否为知识库成员
  role?: number // 角色：0-只读，1-编辑者，2-管理员
  joined_at?: string // 加入时间
}

// 知识库 API
export const knowledgeBaseApi = {
  // 获取知识库列表（支持筛选和分页）
  async getKnowledgeBases(params?: KnowledgeBaseFilterParams | number | null): Promise<KnowledgeBaseListResponse | KnowledgeBase[]> {
    const queryParams: Record<string, any> = {}
    
    // 兼容旧接口：如果传入的是 number 或 null，表示 team_space_id
    if (typeof params === 'number' || params === null || params === undefined) {
      const teamSpaceId = params
      if (teamSpaceId !== undefined && teamSpaceId !== null) {
        queryParams.team_space_id = teamSpaceId
      }
      const response = await request.get('/knowledge-bases', { params: queryParams })
      // 如果返回的是数组，直接返回；如果是对象且有 items 字段，返回 items
      if (Array.isArray(response)) {
        return response
      }
      if (response && typeof response === 'object' && 'items' in response) {
        return (response as any).items || []
      }
      return []
    }
    
    // 新接口：支持筛选参数
    const filterParams = params as KnowledgeBaseFilterParams
    
    // 处理筛选类型
    if (filterParams.filter_type) {
      queryParams.filter_type = filterParams.filter_type
    }
    
    // 处理搜索关键词
    if (filterParams.keyword) {
      queryParams.keyword = filterParams.keyword
    }
    
    // 处理可见性筛选
    if (filterParams.visibility !== undefined && filterParams.visibility !== null) {
      queryParams.visibility = filterParams.visibility
    }
    
    // 处理团队空间ID
    if (filterParams.team_space_id !== undefined && filterParams.team_space_id !== null) {
      queryParams.team_space_id = filterParams.team_space_id
    }
    
    // 处理分页参数
    if (filterParams.page !== undefined && filterParams.page !== null) {
      queryParams.page = filterParams.page
    }
    
    if (filterParams.page_size !== undefined && filterParams.page_size !== null) {
      queryParams.page_size = filterParams.page_size
    }
    
    const response = await request.get('/knowledge-bases', { params: queryParams })
    
    // 如果返回的是数组，直接返回（兼容旧接口）
    if (Array.isArray(response)) {
      return response
    }
    
    // 如果返回的是对象，返回完整对象（包含 items 和 total）
    if (response && typeof response === 'object' && 'items' in response) {
      const responseData = response as unknown as { items: KnowledgeBase[]; total?: number }
      return {
        items: responseData.items || [],
        total: responseData.total || responseData.items?.length || 0
      } as KnowledgeBaseListResponse
    }
    
    return { items: [], total: 0 }
  },

  // 获取知识库详情
  async getKnowledgeBase(kbId: number): Promise<KnowledgeBase> {
    return request.get(`/knowledge-bases/${kbId}`)
  },

  // 创建知识库
  async createKnowledgeBase(data: KnowledgeBaseCreate): Promise<KnowledgeBase> {
    return request.post('/knowledge-bases', data)
  },

  // 更新知识库
  async updateKnowledgeBase(kbId: number, data: KnowledgeBaseUpdate): Promise<KnowledgeBase> {
    return request.put(`/knowledge-bases/${kbId}`, data)
  },

  // 删除知识库
  async deleteKnowledgeBase(kbId: number): Promise<void> {
    return request.delete(`/knowledge-bases/${kbId}`)
  },

  // 添加知识库成员（单用户 user_id + role；或按系统角色批量 role_ids + 统一 role）
  async addKnowledgeBaseMember(kbId: number, data: KnowledgeBaseMemberAdd): Promise<void> {
    return request.post(`/knowledge-bases/${kbId}/members`, data)
  },

  // 按系统角色批量移除成员 POST /knowledge-bases/{id}/members/batch-remove
  async batchRemoveKnowledgeBaseMembers(kbId: number, data: KnowledgeBaseMemberBatchRemove): Promise<void> {
    return request.post(`/knowledge-bases/${kbId}/members/batch-remove`, data)
  },

  // 移除知识库成员
  async removeKnowledgeBaseMember(kbId: number, userId: number): Promise<void> {
    return request.delete(`/knowledge-bases/${kbId}/members/${userId}`)
  },

  // 更新知识库成员角色
  async updateKnowledgeBaseMemberRole(kbId: number, userId: number, role: number): Promise<void> {
    return request.put(`/knowledge-bases/${kbId}/members/${userId}`, { role })
  },

  // 搜索知识库成员 GET /api/knowledge-bases/search/members?knowledge_base_id=&keyword=&is_member=&page=&page_size=
  async searchKnowledgeBaseMembers(params: KnowledgeBaseMemberSearchParams): Promise<{ items: KnowledgeBaseMemberSearchItem[]; total: number }> {
    const queryParams: Record<string, any> = {}
    
    // 知识库ID是必需的
    if (params.knowledge_base_id !== undefined && params.knowledge_base_id !== null) {
      queryParams.knowledge_base_id = params.knowledge_base_id
    }
    
    if (params.keyword) {
      queryParams.keyword = params.keyword.trim()
    }
    
    if (params.is_member !== undefined && params.is_member !== null) {
      queryParams.is_member = params.is_member
    }
    
    if (params.page !== undefined && params.page !== null) {
      queryParams.page = params.page
    }
    
    if (params.page_size !== undefined && params.page_size !== null) {
      queryParams.page_size = params.page_size
    }

    if (params.role_ids && params.role_ids.length > 0) {
      queryParams.role_ids = params.role_ids
    }

    const res = await request.get('/knowledge-bases/search/members', {
      params: queryParams,
      paramsSerializer: (p) => {
        const usp = new URLSearchParams()
        for (const [k, v] of Object.entries(p as Record<string, unknown>)) {
          if (v === undefined || v === null) continue
          if (k === 'role_ids' && Array.isArray(v)) {
            ;(v as number[]).forEach((id) => usp.append('role_ids', String(id)))
          } else if (v !== '') {
            usp.append(k, String(v))
          }
        }
        return usp.toString()
      }
    })
    
    // 处理响应：可能是数组或对象
    if (Array.isArray(res)) {
      return { items: res as KnowledgeBaseMemberSearchItem[], total: res.length }
    }
    
    if (res && typeof res === 'object' && 'items' in res) {
      const o = res as Record<string, unknown>
      const items = (Array.isArray(o.items) ? o.items : []) as KnowledgeBaseMemberSearchItem[]
      const total = typeof o.total === 'number' ? o.total : items.length
      return { items, total }
    }
    
    return { items: [], total: 0 }
  },

  /** 标签列表 GET /knowledge-bases/{kb_id}/tags?keyword= */
  async listKnowledgeBaseTags(
    kbId: number,
    params?: { keyword?: string | null }
  ): Promise<KnowledgeBaseTag[]> {
    const query: Record<string, string> = {}
    if (params?.keyword != null && String(params.keyword).trim() !== '') {
      query.keyword = String(params.keyword).trim()
    }
    const res = await request.get(`/knowledge-bases/${kbId}/tags`, {
      params: Object.keys(query).length ? query : undefined
    })
    if (Array.isArray(res)) {
      return res as KnowledgeBaseTag[]
    }
    if (res && typeof res === 'object' && 'items' in res) {
      const o = res as { items?: KnowledgeBaseTag[] }
      return o.items ?? []
    }
    return []
  },

  /** 创建标签 POST /knowledge-bases/{kb_id}/tags */
  async createKnowledgeBaseTag(kbId: number, data: KnowledgeBaseTagCreate): Promise<KnowledgeBaseTag> {
    return request.post(`/knowledge-bases/${kbId}/tags`, data)
  },

  /** 标签详情 GET /knowledge-bases/{kb_id}/tags/{tag_id} */
  async getKnowledgeBaseTag(kbId: number, tagId: number): Promise<KnowledgeBaseTag> {
    return request.get(`/knowledge-bases/${kbId}/tags/${tagId}`)
  },

  /** 更新标签 PUT /knowledge-bases/{kb_id}/tags/{tag_id} */
  async updateKnowledgeBaseTag(
    kbId: number,
    tagId: number,
    data: KnowledgeBaseTagUpdate
  ): Promise<KnowledgeBaseTag> {
    return request.put(`/knowledge-bases/${kbId}/tags/${tagId}`, data)
  },

  /** 删除标签 DELETE /knowledge-bases/{kb_id}/tags/{tag_id} */
  async deleteKnowledgeBaseTag(kbId: number, tagId: number): Promise<void> {
    return request.delete(`/knowledge-bases/${kbId}/tags/${tagId}`)
  },
}
