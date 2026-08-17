import request from './request'

// 系统权限创建请求
export interface SystemPermissionCreate {
  name: string
  code: string
  description?: string | null
  category?: string | null
  status?: number // 0-禁用，1-启用，默认1
  sort_order?: number // 排序顺序，默认0
}

// 系统权限更新请求
export interface SystemPermissionUpdate {
  name?: string | null
  code?: string | null
  description?: string | null
  category?: string | null
  status?: number | null // 0-禁用，1-启用
  sort_order?: number | null // 排序顺序
}

// 系统权限响应
export interface SystemPermission {
  id: number
  name: string
  code: string
  description?: string | null
  category?: string | null
  status: number // 0-禁用，1-启用
  sort_order: number
  created_at?: string
  updated_at?: string
}

// 权限列表响应
export interface SystemPermissionListResponse {
  items: SystemPermission[]
  total: number
}

// 权限筛选参数
export interface SystemPermissionFilterParams {
  page?: number
  page_size?: number
  status?: number | null // 0-禁用，1-启用
  category?: string | null // 权限分类
  keyword?: string | null // 关键词搜索（权限名称或代码）
}

// 分页列表响应：{ items: [], total: number } 或 直接数组（兼容时 total=items.length）
function normalizePermissionList(res: unknown): SystemPermissionListResponse {
  if (Array.isArray(res)) {
    return { items: res as SystemPermission[], total: res.length }
  }
  if (res && typeof res === 'object') {
    const o = res as Record<string, unknown>
    const items = (Array.isArray(o.items) ? o.items : []) as SystemPermission[]
    const total = typeof o.total === 'number' ? o.total : items.length
    return { items, total }
  }
  return { items: [], total: 0 }
}

// 系统权限 API
export const systemPermissionApi = {
  /** 获取权限列表 GET /api/system-permissions */
  async getPermissions(params?: SystemPermissionFilterParams): Promise<SystemPermissionListResponse> {
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
    
    if (params?.category) {
      queryParams.category = params.category
    }
    
    if (params?.keyword) {
      queryParams.keyword = params.keyword
    }
    
    const res = await request.get('/system-permissions', { params: queryParams })
    return normalizePermissionList(res)
  },

  /** 创建权限 POST /api/system-permissions */
  async createPermission(data: SystemPermissionCreate): Promise<SystemPermission> {
    return await request.post('/system-permissions', data)
  },

  /** 获取权限详情 GET /api/system-permissions/{permission_id} */
  async getPermission(permissionId: number): Promise<SystemPermission> {
    return await request.get(`/system-permissions/${permissionId}`)
  },

  /** 更新权限 PUT /api/system-permissions/{permission_id} */
  async updatePermission(permissionId: number, data: SystemPermissionUpdate): Promise<SystemPermission> {
    return await request.put(`/system-permissions/${permissionId}`, data)
  },

  /** 删除权限 DELETE /api/system-permissions/{permission_id} */
  async deletePermission(permissionId: number): Promise<void> {
    return await request.delete(`/system-permissions/${permissionId}`)
  },

  /** 启用权限 PUT /api/system-permissions/{permission_id}/enable */
  async enablePermission(permissionId: number): Promise<void> {
    return await request.put(`/system-permissions/${permissionId}/enable`)
  },

  /** 禁用权限 PUT /api/system-permissions/{permission_id}/disable */
  async disablePermission(permissionId: number): Promise<void> {
    return await request.put(`/system-permissions/${permissionId}/disable`)
  },

  /** 获取权限分类列表 GET /api/system-permissions/categories/list */
  async getCategories(): Promise<string[]> {
    const res = await request.get('/system-permissions/categories/list')
    if (Array.isArray(res)) {
      return res as string[]
    }
    if (res && typeof res === 'object' && 'items' in res) {
      return ((res as { items: unknown }).items as string[]) || []
    }
    return []
  }
}
