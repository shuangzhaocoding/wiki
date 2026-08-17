import request from './request'

// 用户创建请求
export interface UserCreate {
  username: string
  email: string
  password: string
  role_ids?: number[]
}

// 用户更新请求
export interface UserUpdate {
  email?: string | null
  status?: number | null // 0-封禁，1-正常
}

// 用户响应
export interface User {
  id: number
  username: string
  email: string
  status: number // 0-封禁，1-正常
  roles?: RoleInfo[] | null
  created_at?: string
  updated_at?: string
}

// 权限信息
export interface PermissionInfo {
  id: number
  name: string
  code: string
  description?: string
  category?: string
}

// 角色信息（用户拥有的角色）
export interface RoleInfo {
  id: number
  name: string
  code: string
  permissions?: PermissionInfo[]
  assigned_at?: string
  assigned_by?: number
}

// 用户列表响应
export interface UserListResponse {
  items: User[]
  total: number
}

// 用户筛选参数
export interface UserFilterParams {
  page?: number
  page_size?: number
  status?: number | null // 0-封禁，1-正常
  keyword?: string | null // 关键词搜索（用户名或邮箱）
}

// 分页列表响应：{ items: [], total: number } 或 直接数组（兼容时 total=items.length）
function normalizeUserList(res: unknown): UserListResponse {
  if (Array.isArray(res)) {
    return { items: res as User[], total: res.length }
  }
  if (res && typeof res === 'object') {
    const o = res as Record<string, unknown>
    const items = (Array.isArray(o.items) ? o.items : []) as User[]
    const total = typeof o.total === 'number' ? o.total : items.length
    return { items, total }
  }
  return { items: [], total: 0 }
}

// 用户角色分配请求
export interface UserRoleAssign {
  user_id: number
  role_ids: number[]
}

// 用户管理 API
export const userManagementApi = {
  /** 获取用户列表 GET /api/users */
  async getUsers(params?: UserFilterParams): Promise<UserListResponse> {
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

    const res = await request.get('/users', { params: queryParams })
    return normalizeUserList(res)
  },

  /** 创建用户 POST /api/users */
  async createUser(data: UserCreate): Promise<User> {
    return await request.post('/users', data)
  },

  /** 获取用户详情 GET /api/users/{user_id} */
  async getUser(userId: number): Promise<User> {
    return await request.get(`/users/${userId}`)
  },

  /** 获取用户及其角色信息 GET /api/user-roles/users/{user_id} */
  async getUserWithRoles(userId: number): Promise<User> {
    return await request.get(`/user-roles/users/${userId}`)
  },

  /** 更新用户 PUT /api/users/{user_id} */
  async updateUser(userId: number, data: UserUpdate): Promise<User> {
    return await request.put(`/users/${userId}`, data)
  },

  /** 删除用户 DELETE /api/users/{user_id} */
  async deleteUser(userId: number): Promise<void> {
    return await request.delete(`/users/${userId}`)
  },

  /** 启用用户 PUT /api/user-roles/{user_id}/enable */
  async enableUser(userId: number): Promise<void> {
    return await request.put(`/user-roles/${userId}/enable`)
  },

  /** 禁用用户 PUT /api/user-roles/{user_id}/disable */
  async disableUser(userId: number): Promise<void> {
    return await request.put(`/user-roles/${userId}/disable`)
  },

  /** 获取用户角色列表 GET /api/user-roles/{user_id}/roles */
  async getUserRoles(userId: number): Promise<RoleInfo[]> {
    const res = await request.get(`/user-roles/${userId}/roles`)
    
    // 处理不同的返回格式
    if (Array.isArray(res)) {
      // 如果返回的是数组，直接返回
      return res as RoleInfo[]
    }
    
    if (res && typeof res === 'object') {
      // 处理 {code: 200, data: {roles: [...]}} 格式
      if ('data' in res && res.data && typeof res.data === 'object') {
        const data = res.data as Record<string, unknown>
        if ('roles' in data && Array.isArray(data.roles)) {
          return (data.roles as RoleInfo[]) || []
        }
      }
      // 如果返回的是对象，尝试提取 items 或 roles 字段
      if ('items' in res && Array.isArray((res as { items: unknown }).items)) {
        return ((res as { items: unknown }).items as RoleInfo[]) || []
      }
      if ('roles' in res && Array.isArray((res as { roles: unknown }).roles)) {
        return ((res as { roles: unknown }).roles as RoleInfo[]) || []
      }
      // 如果返回的是单个角色对象，包装成数组
      if ('id' in res && 'name' in res && 'code' in res) {
        return [{ id: (res as any).id, name: (res as any).name, code: (res as any).code }]
      }
    }
    
    return []
  },

  /** 为用户分配角色（批量） POST /api/user-roles/assign */
  async assignUserRoles(data: UserRoleAssign): Promise<void> {
    return await request.post('/user-roles/assign', data)
  },

  /** 为用户添加单个角色 POST /api/user-roles/{user_id}/roles/{role_id} */
  async addUserRole(userId: number, roleId: number): Promise<void> {
    return await request.post(`/user-roles/${userId}/roles/${roleId}`)
  },

  /** 移除用户的单个角色 DELETE /api/user-roles/{user_id}/roles/{role_id} */
  async removeUserRole(userId: number, roleId: number): Promise<void> {
    return await request.delete(`/user-roles/${userId}/roles/${roleId}`)
  },

  /** 更新用户角色（批量分配，使用 assign 接口） PUT /api/user-roles/{user_id}/roles */
  async updateUserRoles(userId: number, roleIds: number[]): Promise<void> {
    return await request.post('/user-roles/assign', {
      user_id: userId,
      role_ids: roleIds
    })
  },

  /** 获取用户角色列表 GET /api/user-roles */
  async getUserRoleList(params?: { page?: number; page_size?: number }): Promise<UserListResponse> {
    const queryParams: Record<string, any> = {}
    if (params?.page) {
      queryParams.page = params.page
    }
    if (params?.page_size) {
      queryParams.page_size = params.page_size
    }
    const res = await request.get('/user-roles', { params: queryParams })
    return normalizeUserList(res)
  }
}
