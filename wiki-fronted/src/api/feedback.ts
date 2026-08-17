import request from './request'

// 反馈类型：1-建议 2-错误反馈 3-其他
export const FEEDBACK_TYPE_SUGGESTION = 1
export const FEEDBACK_TYPE_BUG = 2
export const FEEDBACK_TYPE_OTHER = 3

// 反馈状态：1-待处理 2-处理中 3-已处理 4-已关闭（与接口一致）
export const FEEDBACK_STATUS_PENDING = 1
export const FEEDBACK_STATUS_PROCESSING = 2
export const FEEDBACK_STATUS_RESOLVED = 3
export const FEEDBACK_STATUS_CLOSED = 4

// 创建反馈请求
export interface FeedbackCreate {
  article_id: number
  feedback_type: number
  content: string
}

// 反馈回复请求
export interface FeedbackReply {
  reply: string
}

// 反馈响应
export interface Feedback {
  id: number
  article_id: number
  feedback_type: number
  content: string
  status?: number
  user_id?: number
  user_name?: string
  user_avatar?: string
  created_at?: string
  admin_reply?: string
  reply_time?: string
}

export interface FeedbackListResponse {
  items?: Feedback[]
  total?: number
  page?: number
  page_size?: number
}

/** 当前用户反馈项（GET /api/users/me/feedbacks 返回，含文章标题、知识库ID等） */
export interface MyFeedbackItem {
  id: number
  article_id: number
  article_title?: string
  knowledge_base_id?: number
  user_name?: string
  feedback_type: number
  content: string
  status: number
  created_at?: string
  admin_reply?: string
  reply_time?: string
  [key: string]: unknown
}

// 反馈 API
export const feedbackApi = {
  /** 当前用户反馈列表 GET /api/users/me/feedbacks */
  async getMyFeedbacks(params?: {
    page?: number
    page_size?: number
    status?: number | null
  }): Promise<{ items: MyFeedbackItem[]; total: number; page: number; page_size: number }> {
    const res: any = await request.get('/users/me/feedbacks', { params: params || {} })
    if (res && typeof res === 'object') {
      const o = res as Record<string, unknown>
      return {
        items: (Array.isArray(o.items) ? o.items : []) as MyFeedbackItem[],
        total: typeof o.total === 'number' ? o.total : 0,
        page: typeof o.page === 'number' ? o.page : 1,
        page_size: typeof o.page_size === 'number' ? o.page_size : 10
      }
    }
    return { items: [], total: 0, page: 1, page_size: 10 }
  },

  // 创建反馈
  async createFeedback(articleId: number, data: Omit<FeedbackCreate, 'article_id'>): Promise<Feedback> {
    return request.post(`/articles/${articleId}/feedback`, { ...data, article_id: articleId })
  },

  // 获取文章反馈列表
  async getArticleFeedbacks(
    articleId: number,
    params?: { status?: number | null; page?: number; page_size?: number }
  ): Promise<Feedback[]> {
    const response = await request.get(`/articles/${articleId}/feedbacks`, { params })
    if (Array.isArray(response)) {
      return response
    }
    if (response && typeof response === 'object' && 'items' in response) {
      return (response as FeedbackListResponse).items || []
    }
    return []
  },

  // 更新反馈状态
  async updateFeedbackStatus(feedbackId: number, newStatus: number): Promise<void> {
    return request.put(`/articles/feedbacks/${feedbackId}/status`, null, {
      params: { new_status: newStatus }
    })
  },

  // 回复反馈
  async replyFeedback(feedbackId: number, data: FeedbackReply): Promise<void> {
    return request.post(`/articles/feedbacks/${feedbackId}/reply`, data)
  }
}
