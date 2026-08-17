import request from './request'

/** 资源类型：1-团队空间，2-知识库，3-文章 */
export const RESOURCE_TYPE = {
  TEAM_SPACE: 1,
  KNOWLEDGE_BASE: 2,
  ARTICLE: 3
} as const

/** 申请状态：0-待审核，1-已同意，2-已拒绝 */
export const APPLICATION_STATUS = {
  PENDING: 0,
  APPROVED: 1,
  REJECTED: 2
} as const

/** 申请角色：0-只读，1-编辑者，2-管理员 */
export const APPLICATION_ROLE = {
  READONLY: 0,
  EDITOR: 1,
  ADMIN: 2
} as const

/** 申请项 */
export interface Application {
  id: number
  resource_type: number
  resource_id: number
  resource_name?: string
  knowledge_base_id?: number | null
  applied_role: number
  message?: string | null
  reviewer_ids?: number[] | null
  reviewers?: Array<{ id: number; name?: string }> | null
  status: number
  created_at: string
  updated_at?: string
  applicant_id: number
  applicant_name?: string
  applicant_email?: string
  reviewed_at?: string | null
  reviewed_by_id?: number | null
  reviewed_by_name?: string | null
  reply_message?: string | null
  [key: string]: unknown
}

/** 申请列表响应 */
export interface ApplicationListResponse {
  items: Application[]
  total: number
  page: number
  page_size: number
}

/** 创建申请请求 */
export interface ApplicationCreate {
  resource_type: number
  resource_id: number
  applied_role?: number
  message?: string | null
  reviewer_ids?: number[] | null
}

/** 审核申请请求 */
export interface ApplicationReview {
  approved: boolean
  reply_message?: string | null
}

// 申请 API
export const applicationApi = {
  /** 获取申请列表 GET /api/applications?list_type=my|to_review&status=0|1|2&page=1&page_size=10 */
  async getApplications(params: {
    list_type: 'my' | 'to_review'
    status?: number | null
    page?: number
    page_size?: number
  }): Promise<ApplicationListResponse> {
    const queryParams: Record<string, any> = {
      list_type: params.list_type
    }
    if (params.status !== undefined && params.status !== null) {
      queryParams.status = params.status
    }
    if (params.page !== undefined) {
      queryParams.page = params.page
    }
    if (params.page_size !== undefined) {
      queryParams.page_size = params.page_size
    }
    const res: any = await request.get('/applications', { params: queryParams })
    if (res && typeof res === 'object') {
      const o = res as Record<string, unknown>
      return {
        items: (Array.isArray(o.items) ? o.items : []) as Application[],
        total: typeof o.total === 'number' ? o.total : 0,
        page: typeof o.page === 'number' ? o.page : 1,
        page_size: typeof o.page_size === 'number' ? o.page_size : 10
      }
    }
    return { items: [], total: 0, page: 1, page_size: 10 }
  },

  /** 审核申请 PUT /api/applications/{application_id}/review */
  async reviewApplication(applicationId: number, data: ApplicationReview): Promise<void> {
    await request.put(`/applications/${applicationId}/review`, data)
  },

  /** 申请资源权限 POST /api/applications */
  async applyForResource(data: ApplicationCreate): Promise<void> {
    await request.post('/applications', data)
  }
}
