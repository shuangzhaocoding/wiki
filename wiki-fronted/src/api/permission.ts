import request from './request'

/** 资源类型：1-团队空间，2-知识库，3-文章 */
export const RESOURCE_TYPE = {
  TEAM_SPACE: 1,
  KNOWLEDGE_BASE: 2,
  ARTICLE: 3
} as const

/** 资源管理员项 */
export interface ResourceAdminItem {
  id?: number
  user_id: number
  username?: string
  email?: string
  [key: string]: unknown
}

// 权限 API
export const permissionApi = {
  /** 获取资源管理员列表 GET /api/permissions/admins */
  async getResourceAdmins(resourceType: number, resourceId: number): Promise<ResourceAdminItem[]> {
    const res: any = await request.get('/permissions/admins', {
      params: {
        resource_type: resourceType,
        resource_id: resourceId
      }
    })
    if (Array.isArray(res)) {
      return res as ResourceAdminItem[]
    }
    if (res && typeof res === 'object' && 'items' in res) {
      return ((res as { items: ResourceAdminItem[] }).items) || []
    }
    return []
  }
}
