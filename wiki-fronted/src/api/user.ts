import request from './request'

// 收藏/点赞/浏览记录项的通用结构（兼容多种后端返回格式）
export interface UserActivityItem {
  id: number
  article_id?: number
  knowledge_base_id?: number
  /** 顶层 title（部分接口扁平化返回） */
  title?: string
  article_title?: string
  article?: {
    id: number
    title?: string
    name?: string
    knowledge_base_id?: number
    summary?: string
    view_count?: number
    like_count?: number
    created_at?: string
    updated_at?: string
  }
  created_at?: string
  collected_at?: string
  liked_at?: string
  browsed_at?: string
}

/** 每日统计项：接口返回 { date, reads, collections, likes } */
export interface DailyStatItem {
  date: string
  reads?: number
  collections?: number
  likes?: number
}





// 分页列表响应：{ items: [], total: number } 或 直接数组（兼容时 total=items.length）
function normalizePageList(res: unknown): { items: UserActivityItem[]; total: number } {
  if (Array.isArray(res)) {
    return { items: res as UserActivityItem[], total: res.length }
  }
  if (res && typeof res === 'object') {
    const o = res as Record<string, unknown>
    const items = (Array.isArray(o.items) ? o.items : []) as UserActivityItem[]
    const total = typeof o.total === 'number' ? o.total : items.length
    return { items, total }
  }
  return { items: [], total: 0 }
}

// 从 item 中解析出：文章ID、知识库ID、标题、时间
export function parseActivityItem(item: UserActivityItem): {
  articleId: number
  knowledgeBaseId: number
  title: string
  time: string
} {
  const articleId = item.article_id ?? item.article?.id ?? item.id
  const knowledgeBaseId =
    item.knowledge_base_id ?? item.article?.knowledge_base_id ?? 0
  const title =
    item.title ??
    item.article_title ??
    item.article?.title ??
    item.article?.name ??
    ''
  const time =
    item.collected_at ??
    item.liked_at ??
    item.browsed_at ??
    item.created_at ??
    item.article?.updated_at ??
    ''
  return { articleId, knowledgeBaseId, title, time }
}

export const userApi = {
  /** 个人收藏 GET /api/users/me/collections?page=1&page_size=10 */
  async getMyCollections(page: number, page_size: number): Promise<{ items: UserActivityItem[]; total: number }> {
    const res = await request.get('/users/me/collections', { params: { page, page_size } })
    return normalizePageList(res)
  },

  /** 个人点赞 GET /api/users/me/likes?page=1&page_size=10 */
  async getMyLikes(page: number, page_size: number): Promise<{ items: UserActivityItem[]; total: number }> {
    const res = await request.get('/users/me/likes', { params: { page, page_size } })
    return normalizePageList(res)
  },

  /** 个人浏览记录 GET /api/users/me/browse-history?page=1&page_size=10 */
  async getMyBrowseHistory(page: number, page_size: number): Promise<{ items: UserActivityItem[]; total: number }> {
    const res = await request.get('/users/me/browse-history', { params: { page, page_size } })
    return normalizePageList(res)
  },

  /** 个人每日数据统计 GET /api/users/me/daily-stats?start_date=&end_date= */
  async getDailyStats(params?: { start_date?: string; end_date?: string }): Promise<DailyStatItem[]> {
    const res = await request.get('/users/me/daily-stats', { params: params || {} })
    if (Array.isArray(res)) return res as DailyStatItem[]
    if (res && typeof res === 'object' && 'items' in res) {
      return ((res as { items: unknown }).items as DailyStatItem[]) || []
    }
    return []
  },


}
