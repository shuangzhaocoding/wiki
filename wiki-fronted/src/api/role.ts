import request from './request'

// 角色创建请求
export interface RoleCreate {
  name: string
  code: string
  description?: string | null
  permissions?: Record<string, any> | null
  status?: number // 0-禁用，1-启用，默认1
}

// 角色更新请求
export interface RoleUpdate {
  name?: string | null
  code?: string | null
  description?: string | null
  permissions?: Record<string, any> | null
  status?: number | null // 0-禁用，1-启用
}

// 角色响应（permissions 可能为权限ID数组 [1,2,3] 或对象格式）
export interface Role {
  id: number
  name: string
  code: string
  description?: string | null
  permissions?: number[] | Record<string, any> | null
  status: number // 0-禁用，1-启用
  created_at?: string
  updated_at?: string
}

// 角色列表响应
export interface RoleListResponse {
  items: Role[]
  total: number
}

// 角色筛选参数
export interface RoleFilterParams {
  page?: number
  page_size?: number
  status?: number | null // 0-禁用，1-启用
  keyword?: string | null // 关键词搜索（角色名称或代码）
}

// 分页列表响应：{ items: [], total: number } 或 直接数组（兼容时 total=items.length）
function normalizeRoleList(res: unknown): RoleListResponse {
  if (Array.isArray(res)) {
    return { items: res as Role[], total: res.length }
  }
  if (res && typeof res === 'object') {
    const o = res as Record<string, unknown>
    const items = (Array.isArray(o.items) ? o.items : []) as Role[]
    const total = typeof o.total === 'number' ? o.total : items.length
    return { items, total }
  }
  return { items: [], total: 0 }
}

// 角色 API
export const roleApi = {
  /** 获取角色列表 GET /api/roles */
  async getRoles(params?: RoleFilterParams): Promise<RoleListResponse> {
    const queryParams: Record<string, any> = {}

    if (params?.page) {
      queryParams.page = params.page
    }

    if (params?.page_size) {
      queryParams.page_size = params.page_size
    }

    if (params?.status !== undefined && params?.status !== null) {
      queryParams.status = params.status
    }

    if (params?.keyword) {
      queryParams.keyword = params.keyword
    }

    const res = await request.get('/roles', { params: queryParams })
    return normalizeRoleList(res)
  },

  /** 创建角色 POST /api/roles */
  async createRole(data: RoleCreate): Promise<Role> {
    return await request.post('/roles', data)
  },

  /** 获取角色详情 GET /api/roles/{role_id} */
  async getRole(roleId: number): Promise<Role> {
    return await request.get(`/roles/${roleId}`)
  },

  /** 更新角色 PUT /api/roles/{role_id} */
  async updateRole(roleId: number, data: RoleUpdate): Promise<Role> {
    return await request.put(`/roles/${roleId}`, data)
  },

  /** 删除角色 DELETE /api/roles/{role_id} */
  async deleteRole(roleId: number): Promise<void> {
    return await request.delete(`/roles/${roleId}`)
  },

  /** 启用角色 PUT /api/roles/{role_id}/enable */
  async enableRole(roleId: number): Promise<void> {
    return await request.put(`/roles/${roleId}/enable`)
  },

  /** 禁用角色 PUT /api/roles/{role_id}/disable */
  async disableRole(roleId: number): Promise<void> {
    return await request.put(`/roles/${roleId}/disable`)
  },

  /** 更新角色权限 PUT /api/roles/{role_id}/permissions */
  async updateRolePermissions(roleId: number, permissionIds: number[]): Promise<void> {
    return await request.put(`/roles/${roleId}/permissions`, {
      permissions: permissionIds
    })
  }
}
