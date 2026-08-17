import request from './request'

/** 通知类型 */
export type NotificationType = 'system' | 'comment' | 'feedback' | 'mention'

/** 通知项（接口返回） */
export interface NotificationItem {
  id: number
  type: NotificationType | string
  title: string
  /** 消息内容（优先使用，兼容 message） */
  content?: string | null
  message?: string | null
  extra?: string | null
  /** 消息跳转链接 */
  link?: string | null
  /** 创建时间，ISO 字符串 */
  created_at?: string | null
  /** 是否已读 */
  is_read?: boolean
  read?: boolean
}

/** 通知列表响应 */
export interface NotificationListResponse {
  items: NotificationItem[]
  total: number
  page?: number
  page_size?: number
}

/** 获取通知列表参数 */
export interface NotificationListParams {
  page?: number
  page_size?: number
  /** 筛选：0-未读，1-已读，不传则全部 */
  is_read?: number | null
  /** 消息类型，例如 reading_task_assigned，不传则全部 */
  type?: string | null
}

/** 更新通知状态请求 */
export interface NotificationUpdateRequest {
  is_read?: boolean
}

function normalizeList(res: unknown): NotificationListResponse {
  if (Array.isArray(res)) {
    return { items: res as NotificationItem[], total: res.length }
  }
  if (res && typeof res === 'object') {
    const o = res as Record<string, unknown>
    const items = (Array.isArray(o.items) ? o.items : []) as NotificationItem[]
    const total = typeof o.total === 'number' ? o.total : items.length
    return {
      items,
      total,
      page: typeof o.page === 'number' ? o.page : 1,
      page_size: typeof o.page_size === 'number' ? o.page_size : 10
    }
  }
  return { items: [], total: 0 }
}

/** 将接口数据转为组件使用的格式 */
export function toNotification(n: NotificationItem) {
  const read = n.is_read ?? n.read ?? false
  const time = n.created_at ?? ''
  const content = n.content ?? n.message ?? ''
  return {
    id: n.id,
    type: (n.type || 'system') as NotificationType,
    title: n.title || '',
    content,
    extra: n.extra ?? undefined,
    link: n.link ?? undefined,
    time,
    read
  }
}

export const notificationApi = {
  /**
   * 获取未读消息数量
   * GET /api/notifications/unread-count
   */
  async getUnreadCount(): Promise<number> {
    const res = await request.get('/notifications/unread-count') as unknown
    if (typeof res === 'number') return Math.max(0, res)
    if (res && typeof res === 'object') {
      const o = res as Record<string, unknown>
      const count = o.count ?? o.unread_count
      if (typeof count === 'number') return Math.max(0, count)
    }
    return 0
  },

  /**
   * 获取所有消息
   * GET /api/notifications
   */
  async getNotifications(params?: NotificationListParams): Promise<NotificationListResponse> {
    const query: Record<string, string | number | null> = {}
    if (params?.page != null) query.page = params.page
    if (params?.page_size != null) query.page_size = params.page_size
    if (params?.is_read != null && params.is_read >= 0) query.is_read = params.is_read
    if (params?.type) query.type = params.type
    const res = await request.get('/notifications', { params: query })
    return normalizeList(res)
  },

  /**
   * 更新消息状态
   * PUT /api/notifications/{notification_id}
   */
  async updateNotification(
    notificationId: number,
    payload: NotificationUpdateRequest
  ): Promise<void> {
    await request.put(`/notifications/${notificationId}`, payload)
  }
}
