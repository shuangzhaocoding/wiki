import request from './request'

// 签读任务创建请求体
export interface AssignReadingTaskRequest {
  article_id: number
  /** 所属知识库 ID */
  knowledge_base_id: number
  /** 要求阅读时长，单位：秒（后端字段 required_seconds） */
  required_seconds: number
  /** 截止时间，ISO 日期时间字符串，例如 2026-03-31T23:59:59Z */
  deadline: string
  /** 签读对象角色 ID 列表 */
  role_ids: number[]
}

/** 签读任务项（GET /api/reading-tasks/me 返回的 items 元素） */
export interface ReadingTaskItem {
  id: number
  article_id: number
  article_title: string | null
  knowledge_base_id: number
  knowledge_base_name: string | null
  required_seconds: number
  deadline: string | null
  status: number // 0-未开始，1-进行中，2-已完成，3-已过期，4-已取消
  started_at: string | null
  finished_at: string | null
  actual_seconds: number | null
  created_at: string
  updated_at: string
}

/** 签读任务分组项（GET /api/reading-tasks 返回的 items 元素） */
export interface ReadingTaskGroupItem {
  batch_id: number
  article_id: number
  article_title: string | null
  knowledge_base_id: number
  knowledge_base_name: string | null
  required_seconds: number
  deadline: string | null
  created_by_id: number
  created_by_name: string | null
  role_ids: number[]
  task_count: number
  /** 批次状态：0-有效，1-已取消 */
  status?: number
  created_at?: string | null
}

/** 批次任务项（GET /api/reading-tasks/batches/{batch_id}/tasks 返回的 items 元素） */
export interface BatchTaskItem {
  id: number
  user_id: number
  username: string | null
  nickname: string | null
  role_id: number | null
  role_name: string | null
  status: number
  required_seconds: number
  actual_seconds: number | null
  started_at: string | null
  finished_at: string | null
  created_at: string | null
  updated_at: string | null
}

/** 修改批次请求体 */
export interface BatchUpdateRequest {
  required_seconds?: number
  deadline?: string | null
  role_ids?: number[]
}

/** 签读任务列表响应（管理端） */
export interface AllReadingTasksResponse {
  items: ReadingTaskGroupItem[]
  total: number
  page: number
  page_size: number
}

/** 我的签读任务列表响应 */
export interface MyReadingTasksResponse {
  items: ReadingTaskItem[]
  total: number
  page: number
  page_size: number
}

/** 签读检查响应（GET /api/reading-tasks/check） */
export interface SignReadCheckResponse {
  need_sign_read: boolean
  article_id: number
  task_id?: number
  status?: number // 0-未开始，1-进行中，2-已完成，3-已过期，4-已取消
  actual_seconds?: number
  required_seconds?: number
  remaining_seconds?: number
  deadline?: string | null
  created_by_name?: string | null
  created_at?: string | null
}

export const readingTaskApi = {
  /**
   * 创建/分配签读任务
   * POST /api/reading-tasks/assign
   */
  async assignTask(payload: AssignReadingTaskRequest): Promise<void> {
    await request.post('/reading-tasks/assign', payload)
  },

  /**
   * 获取所有签读任务（按文章、创建人分组）
   * GET /api/reading-tasks?page=1&page_size=10
   */
  /**
   * 修改签读任务批次
   * PUT /api/reading-tasks/batches/{batch_id}
   */
  async updateBatch(batchId: number, payload: BatchUpdateRequest): Promise<void> {
    await request.put(`/reading-tasks/batches/${batchId}`, payload)
  },

  /**
   * 获取批次下的所有任务
   * GET /api/reading-tasks/batches/{batch_id}/tasks
   */
  async getBatchTasks(
    batchId: number,
    params?: { status?: number; page?: number; page_size?: number }
  ): Promise<{ items: BatchTaskItem[]; total: number; page: number; page_size: number }> {
    const queryParams: Record<string, number> = { page: 1, page_size: 100 }
    if (params?.status !== undefined && params?.status !== null) {
      queryParams.status = params.status
    }
    if (params?.page !== undefined) queryParams.page = params.page
    if (params?.page_size !== undefined) queryParams.page_size = params.page_size
    const res = await request.get(`/reading-tasks/batches/${batchId}/tasks`, {
      params: queryParams
    })
    const o = res as unknown as Record<string, unknown>
    return {
      items: (Array.isArray(o.items) ? o.items : []) as BatchTaskItem[],
      total: typeof o.total === 'number' ? o.total : 0,
      page: typeof o.page === 'number' ? o.page : 1,
      page_size: typeof o.page_size === 'number' ? o.page_size : 10
    }
  },

  /**
   * 取消指定批次下的所有未完成任务
   * POST /api/reading-tasks/batches/{batch_id}/cancel
   */
  async cancelBatch(batchId: number): Promise<{ cancelled_count: number }> {
    const res = await request.post(`/reading-tasks/batches/${batchId}/cancel`)
    const o = res as unknown as Record<string, unknown>
    return {
      cancelled_count: typeof o.cancelled_count === 'number' ? o.cancelled_count : 0
    }
  },

  async getAllReadingTasks(params?: {
    page?: number
    page_size?: number
    status?: number | null
  }): Promise<AllReadingTasksResponse> {
    const queryParams: Record<string, number | null> = {}
    if (params?.page !== undefined && params?.page !== null) {
      queryParams.page = params.page
    }
    if (params?.page_size !== undefined && params?.page_size !== null) {
      queryParams.page_size = params.page_size
    }
    if (params?.status !== undefined && params?.status !== null) {
      queryParams.status = params.status
    }
    const res = await request.get('/reading-tasks', { params: queryParams })
    const o = res as unknown as Record<string, unknown>
    return {
      items: (Array.isArray(o.items) ? o.items : []) as ReadingTaskGroupItem[],
      total: typeof o.total === 'number' ? o.total : 0,
      page: typeof o.page === 'number' ? o.page : 1,
      page_size: typeof o.page_size === 'number' ? o.page_size : 10
    }
  },

  /**
   * 获取当前用户的签读任务列表
   * GET /api/reading-tasks/me?status=&page=1&page_size=10
   */
  /**
   * 检查当前用户是否需要签读指定文章
   * GET /api/reading-tasks/check?article_id=xxx
   */
  async checkArticleSignRead(articleId: number): Promise<SignReadCheckResponse> {
    const res = await request.get('/reading-tasks/check', {
      params: { article_id: articleId }
    })
    const o = res as unknown as Record<string, unknown>
    return {
      need_sign_read: !!o.need_sign_read,
      article_id: Number(o.article_id) || articleId,
      task_id: o.task_id != null ? Number(o.task_id) : undefined,
      status: o.status != null ? Number(o.status) : undefined,
      actual_seconds: o.actual_seconds != null ? Number(o.actual_seconds) : undefined,
      required_seconds: o.required_seconds != null ? Number(o.required_seconds) : undefined,
      remaining_seconds: o.remaining_seconds != null ? Number(o.remaining_seconds) : undefined,
      deadline: o.deadline != null ? String(o.deadline) : undefined,
      created_by_name: o.created_by_name != null ? String(o.created_by_name) : undefined,
      created_at: o.created_at != null ? String(o.created_at) : undefined
    }
  },

  /**
   * 更新签读任务状态
   * PUT /api/reading-tasks/{task_id}/status
   */
  async updateTaskStatus(
    taskId: number,
    payload: { status: number; actual_seconds?: number }
  ): Promise<void> {
    await request.put(`/reading-tasks/${taskId}/status`, payload)
  },

  async getMyReadingTasks(params?: {
    status?: number
    page?: number
    page_size?: number
  }): Promise<MyReadingTasksResponse> {
    const queryParams: Record<string, number> = {}
    if (params?.status !== undefined && params?.status !== null) {
      queryParams.status = params.status
    }
    if (params?.page !== undefined && params?.page !== null) {
      queryParams.page = params.page
    }
    if (params?.page_size !== undefined && params?.page_size !== null) {
      queryParams.page_size = params.page_size
    }
    const res = await request.get('/reading-tasks/me', { params: queryParams })
    const o = res as unknown as Record<string, unknown>
    return {
      items: (Array.isArray(o.items) ? o.items : []) as ReadingTaskItem[],
      total: typeof o.total === 'number' ? o.total : 0,
      page: typeof o.page === 'number' ? o.page : 1,
      page_size: typeof o.page_size === 'number' ? o.page_size : 10
    }
  }
}

