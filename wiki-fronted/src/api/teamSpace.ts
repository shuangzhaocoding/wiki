import request from './request'

// 团队空间创建请求
export interface TeamSpaceCreate {
  name: string
  description?: string | null
  visibility?: number
  cover_image?: string | null
}

// 团队空间更新请求
export interface TeamSpaceUpdate {
  name?: string | null
  description?: string | null
  visibility?: number | null
  cover_image?: string | null
}

// 团队空间响应
export interface TeamSpace {
  id: number
  name: string
  description?: string | null
  visibility: number
  cover_image?: string | null
  created_at?: string
  updated_at?: string
  owner_id?: number
  owner_name?: string // 创建人名称
  my_role?: number // 我的角色：0-只读，1-编辑者，2-管理员
}

// 团队空间列表响应
export interface TeamSpaceListResponse {
  items: TeamSpace[]
  total: number
}

// 团队成员添加请求（单用户：user_id + role；按系统角色批量：role_ids）
export interface TeamMemberAdd {
  user_id?: number
  role?: number
  role_ids?: number[]
}

/** 按系统角色批量移除成员 POST /team-spaces/{id}/members/batch-remove */
export interface TeamMemberBatchRemove {
  role_ids: number[]
}

// 团队成员
export interface TeamMember {
  id: number
  user_id: number
  username?: string
  email?: string
  role: number
  created_at?: string
}

// 团队空间筛选参数
export interface TeamSpaceFilterParams {
  filter_type?: 'created' | 'joined' | 'invited' | 'all' | null // 筛选类型：我创建的、我加入的、受邀加入
  keyword?: string | null // 搜索关键词（所有tab都可以使用）
  visibility?: number | null // 可见性筛选
  page?: number | null // 页码
  page_size?: number | null // 每页数量
}

/** 用户搜索参数 */
export interface TeamSpaceSearchParams {
  team_space_id?: number // 团队空间ID
  knowledge_base_id?: number // 知识库ID
  keyword?: string // 搜索关键词
  is_member?: boolean | null // 是否为成员（null表示全部）
  /** 按系统角色 ID 筛选（多选），对应查询参数 role_ids */
  role_ids?: number[]
  page?: number // 页码
  page_size?: number // 每页数量
}

/** 团队空间搜索项 */
export interface TeamSpaceSearchItem {
  id: number
  user_id: number
  username?: string
  email?: string
  is_member?: boolean // 是否为团队成员
  role?: number // 角色：0-只读，1-编辑者，2-管理员
  joined_at?: string // 加入时间
}

// 团队空间 API
export const teamSpaceApi = {
  // 获取团队空间列表（支持分页，返回对象包含 items 和 total）
  async getTeamSpaces(params?: TeamSpaceFilterParams): Promise<TeamSpaceListResponse | TeamSpace[]> {
    const queryParams: Record<string, any> = {}
    
    // 处理筛选参数
    if (params?.filter_type) {
      queryParams.filter_type = params.filter_type
    }
    
    // 处理搜索关键词
    if (params?.keyword) {
      queryParams.keyword = params.keyword
    }
    
    // 处理可见性筛选
    if (params?.visibility !== undefined && params?.visibility !== null) {
      queryParams.visibility = params.visibility
    }
    
    // 处理分页参数
    if (params?.page !== undefined && params?.page !== null) {
      queryParams.page = params.page
    }
    
    if (params?.page_size !== undefined && params?.page_size !== null) {
      queryParams.page_size = params.page_size
    }
    
    const response = await request.get('/team-spaces', { params: queryParams })
    
    // 如果返回的是数组，直接返回（兼容旧接口）
    if (Array.isArray(response)) {
      return response
    }
    
    // 如果返回的是对象，返回完整对象（包含 items 和 total）
    if (response && typeof response === 'object' && 'items' in response) {
      const responseData = response as { items: TeamSpace[]; total?: number }
      return {
        items: responseData.items || [],
        total: responseData.total || responseData.items?.length || 0
      } as TeamSpaceListResponse
    }
    
    // 默认返回空列表
    return { items: [], total: 0 }
  },

  // 获取团队空间详情
  async getTeamSpace(teamSpaceId: number): Promise<TeamSpace> {
    return request.get(`/team-spaces/${teamSpaceId}`)
  },

  // 创建团队空间
  async createTeamSpace(data: TeamSpaceCreate): Promise<TeamSpace> {
    return request.post('/team-spaces', data)
  },

  // 更新团队空间
  async updateTeamSpace(teamSpaceId: number, data: TeamSpaceUpdate): Promise<TeamSpace> {
    return request.put(`/team-spaces/${teamSpaceId}`, data)
  },

  // 删除团队空间
  async deleteTeamSpace(teamSpaceId: number): Promise<void> {
    return request.delete(`/team-spaces/${teamSpaceId}`)
  },

  // 添加团队成员
  async addTeamMember(teamSpaceId: number, data: TeamMemberAdd): Promise<void> {
    return request.post(`/team-spaces/${teamSpaceId}/members`, data)
  },

  // 移除团队成员
  async removeTeamMember(teamSpaceId: number, userId: number): Promise<void> {
    return request.delete(`/team-spaces/${teamSpaceId}/members/${userId}`)
  },

  /** 按系统角色批量移除 POST /team-spaces/{id}/members/batch-remove */
  async batchRemoveTeamMembers(teamSpaceId: number, data: TeamMemberBatchRemove): Promise<void> {
    return request.post(`/team-spaces/${teamSpaceId}/members/batch-remove`, data)
  },

  // 更新团队成员角色
  async updateTeamMemberRole(teamSpaceId: number, userId: number, role: number): Promise<void> {
    return request.put(`/team-spaces/${teamSpaceId}/members/${userId}`, { role })
  },

  /** 搜索用户 GET /api/users/search?team_space_id=&knowledge_base_id=&keyword=&is_member=&page=&page_size= */
  async searchTeamSpacesMembers(params: TeamSpaceSearchParams): Promise<{ items: TeamSpaceSearchItem[]; total: number }> {
    const queryParams: Record<string, any> = {}
    
    if (params.team_space_id !== undefined && params.team_space_id !== null) {
      queryParams.team_space_id = params.team_space_id
    }
    
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

    const res = await request.get('/team-spaces/search/members', {
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
      return { items: res as TeamSpaceSearchItem[], total: res.length }
    }
    
    if (res && typeof res === 'object' && 'items' in res) {
      const o = res as Record<string, unknown>
      const items = (Array.isArray(o.items) ? o.items : []) as TeamSpaceSearchItem[]
      const total = typeof o.total === 'number' ? o.total : items.length
      return { items, total }
    }
    
    return { items: [], total: 0 }
  }
}
