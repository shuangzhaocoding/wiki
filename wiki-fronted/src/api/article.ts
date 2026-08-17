import request from './request'
import { permissionApi, RESOURCE_TYPE as PERMISSION_RESOURCE_TYPE } from './permission'

const APPLICATION_RESOURCE_TYPE = {
  ARTICLE: 3
} as const

// 文章创建请求
export interface ArticleCreate {
  knowledge_base_id: number
  parent_id?: number | null
  title: string
  content?: string | null
  summary?: string | null
  /** 知识库标签 ID 列表 */
  tag_ids?: number[] | null
  sort_order?: number | null
  /** 树结构中前节点的节点ID，即新节点排在其后；默认为 null */
  after_article_id?: number | null
  /** 节点类型：1=文章，2=目录 */
  node_type?: number | null
  /** 可见范围：1=私有，2=仅成员，3=公开（与编辑文章弹窗一致） */
  visibility?: number | null
}

// 文章更新请求
export interface ArticleUpdate {
  parent_id?: number | null
  title?: string | null
  content?: string | null
  summary?: string | null
  /** 知识库标签 ID 列表 */
  tag_ids?: number[] | null
  sort_order?: number | null
  /** 可见范围：1=私有，2=仅成员，3=公开 */
  visibility?: number | null
  /** 节点类型：1=文章，2=目录 */
  node_type?: number | null
  /** 是否原创 */
  is_original?: boolean | null
  /** 是否含 AI 生成内容 */
  is_ai_generated?: boolean | null
}

// 文章响应
export interface Article {
  id: number
  knowledge_base_id: number
  parent_id?: number | null
  title: string
  content?: string | null
  summary?: string | null
  /** 展示用标签名（兼容旧字段） */
  tags?: string[] | null
  /** 文章标签名称列表（文章详情，优先用于展示） */
  tag_names?: string[] | null
  /** 知识库标签 ID 列表（若后端返回） */
  tag_ids?: number[] | null
  sort_order?: number | null
  created_at?: string
  updated_at?: string
  author_id?: number
  author_name?: string
  updated_by_id?: number
  updated_by_name?: string
  view_count?: number
  like_count?: number
  collect_count?: number
  comment_count?: number
  feedback_count?: number
  has_children?: boolean // 是否有子节点
  children?: Article[] // 子节点
  /** 节点类型：1=文章，2=目录 */
  node_type?: number | null
  /** 可见范围：0=私有，1=公开，2=仅成员 */
  visibility?: number | null
  /** 我的角色：0-只读，1-编辑者，2-管理员 */
  my_role?: number | null
  /** 是否原创 */
  is_original?: boolean | null
  /** 是否含 AI 生成内容 */
  is_ai_generated?: boolean | null
}

/** 文章搜索项：GET /articles/search 返回的 data.items 元素 */
export interface ArticleSearchItem {
  id: number
  knowledge_base_id: number
  knowledge_base_name?: string | null
  team_space_id?: number | null
  team_space_name?: string | null
  title: string
  summary?: string | null
  author_name?: string
  updated_by_name?: string
  created_at?: string
  updated_at?: string
  view_count?: number
  [key: string]: unknown
}

// 目录/分类响应
export interface Category {
  id: number
  knowledge_base_id: number
  parent_id?: number | null
  name: string
  sort_order?: number | null
  children?: Category[]
  type?: 'category' | 'article' // 区分目录和文章
  category_id?: number | null // 文章的目录ID
}

/** 文章附件 */
export interface Attachment {
  id: number
  article_id: number
  filename: string
  file_url: string
  file_type?: string | null
  file_size?: number | null
  created_at?: string | null
  created_by_id?: number | null
  created_by_name?: string | null
}

// 文章 API
export const articleApi = {
  // 获取知识库的文章列表（也可以用于获取目录）
  async getArticles(knowledgeBaseId: number, parentId?: number | null, articleId?: number | null): Promise<Article[] | any[]> {
    const params: Record<string, any> = {
      knowledge_base_id: knowledgeBaseId
    }
    if (parentId !== undefined && parentId !== null) {
      params.parent_id = parentId
    }
    if (articleId !== undefined && articleId !== null) {
      params.article_id = articleId
    }
    const response = await request.get(`/articles`, { params })
    if (Array.isArray(response)) {
      return response
    }
    if (response && typeof response === 'object' && 'items' in response) {
      return (response as any).items || []
    }
    return []
  },

  // 获取文章详情
  async getArticle(articleId: number): Promise<Article> {
    return request.get(`/articles/${articleId}`)
  },

  // 创建文章
  async createArticle(data: ArticleCreate): Promise<Article> {
    return request.post('/articles', data)
  },

  // 更新文章
  async updateArticle(articleId: number, data: ArticleUpdate): Promise<Article> {
    return request.put(`/articles/${articleId}`, data)
  },

  // 删除文章
  async deleteArticle(articleId: number): Promise<void> {
    return request.delete(`/articles/${articleId}`)
  },

  // 获取知识库的目录树
  async getCategories(knowledgeBaseId: number): Promise<Category[]> {
    const response = await request.get(`/articles/${knowledgeBaseId}/categories`)
    if (Array.isArray(response)) {
      return response
    }
    if (response && typeof response === 'object' && 'items' in response) {
      return (response as any).items || []
    }
    return []
  },

  // 创建目录
  async createCategory(knowledgeBaseId: number, data: { parent_id?: number | null; name: string; sort_order?: number | null }): Promise<Category> {
    return request.post(`/articles/${knowledgeBaseId}/categories`, data)
  },

  // 更新目录
  async updateCategory(categoryId: number, data: { name?: string | null; parent_id?: number | null; sort_order?: number | null }): Promise<Category> {
    return request.put(`/articles/${categoryId}`, data)
  },

  // 删除目录
  async deleteCategory(categoryId: number): Promise<void> {
    return request.delete(`/articles/${categoryId}`)
  },

  // 点赞文章
  async likeArticle(articleId: number): Promise<{ message: string; like_count: number }> {
    return request.post(`/articles/${articleId}/like`)
  },

  // 取消点赞
  async unlikeArticle(articleId: number): Promise<{ message: string; like_count: number }> {
    return request.post(`/articles/${articleId}/unlike`)
  },

  // 收藏文章
  async collectArticle(articleId: number): Promise<{ message: string }> {
    return request.post(`/articles/${articleId}/collect`)
  },

  // 取消收藏
  async uncollectArticle(articleId: number): Promise<{ message: string }> {
    return request.post(`/articles/${articleId}/uncollect`)
  },

  // 获取文章统计信息（点赞、收藏等状态）
  async getArticleStats(articleId: number): Promise<{
    view_count: number
    like_count: number
    collect_count: number
    comment_count: number
    feedback_count: number
    is_liked: boolean
    is_collected: boolean
  }> {
    return request.get(`/articles/${articleId}/stats`)
  },

  /**
   * 调整文章位置
   * PUT /api/articles/{article_id}/position
   * @param articleId 被移动的文章 ID
   * @param params.event_type 事件类型：inner=拖入为子节点，before=目标前，after=目标后，none=无效/取消
   * @param params.target_node_id 目标节点 ID；event_type 为 inner/before/after 时必填
   */
  async updateArticlePosition(
    articleId: number,
    params: {
      event_type: 'inner' | 'before' | 'after' | 'none'
      target_node_id?: number | null
    }
  ): Promise<unknown> {
    return request.put(`/articles/${articleId}/position`, params)
  },

  /** 文章关键词模糊搜索 GET /articles/search?keyword=&page=1&page_size=10&knowledge_base_id=，返回 { items, total, page, page_size } */
  async searchArticles(keyword: string, page: number, page_size: number, knowledge_base_id?: number): Promise<{
    items: ArticleSearchItem[]
    total: number
    page: number
    page_size: number
  }> {
    const params: Record<string, any> = { keyword: keyword.trim(), page, page_size }
    if (knowledge_base_id !== undefined && knowledge_base_id !== null) {
      params.knowledge_base_id = knowledge_base_id
    }
    const res = await request.get('/articles/search', {
      params
    })
    if (res && typeof res === 'object') {
      const o = res as unknown as Record<string, unknown>
      return {
        items: (Array.isArray(o.items) ? o.items : []) as ArticleSearchItem[],
        total: typeof o.total === 'number' ? o.total : 0,
        page: typeof o.page === 'number' ? o.page : page,
        page_size: typeof o.page_size === 'number' ? o.page_size : page_size
      }
    }
    return { items: [], total: 0, page: 1, page_size }
  },

  /** 获取文章历史版本列表 GET /articles/{article_id}/versions */
  async getArticleVersions(articleId: number): Promise<ArticleVersion[]> {
    const res = await request.get(`/articles/${articleId}/versions`)
    if (Array.isArray(res)) {
      return res as ArticleVersion[]
    }
    if (res && typeof res === 'object' && 'items' in res) {
      return (res as { items: ArticleVersion[] }).items || []
    }
    return []
  },

  /** 回滚到指定版本 POST /articles/{article_id}/versions/{version_id}/restore */
  async restoreArticleVersion(articleId: number, versionId: number): Promise<void> {
    return request.post(`/articles/${articleId}/versions/${versionId}/restore`)
  },

  /** 对比版本差异 GET /articles/{article_id}/versions/compare?version_id1=&version_id2= */
  async compareArticleVersions(articleId: number, versionId1: number, versionId2: number): Promise<{
    diff: string
    version1: ArticleVersion
    version2: ArticleVersion
  }> {
    return request.get(`/articles/${articleId}/versions/compare`, {
      params: { version_id1: versionId1, version_id2: versionId2 }
    })
  },

  /** 获取文章附件列表 GET /articles/{article_id}/attachments */
  async getArticleAttachments(articleId: number): Promise<Attachment[]> {
    const res = await request.get(`/articles/${articleId}/attachments`)
    if (Array.isArray(res)) {
      return res as Attachment[]
    }
    if (res && typeof res === 'object' && 'items' in res) {
      return (res as { items: Attachment[] }).items || []
    }
    return []
  },

  /** 上传文章附件 POST /articles/{article_id}/attachments */
  async uploadArticleAttachment(articleId: number, file: File, onProgress?: (progress: number) => void): Promise<Attachment> {
    const formData = new FormData()
    formData.append('file', file)
    
    const config: any = {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
    
    if (onProgress) {
      config.onUploadProgress = (progressEvent: any) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(percentCompleted)
        }
      }
    }
    
    return request.post(`/articles/${articleId}/attachments`, formData, config)
  },

  /** 删除文章附件 DELETE /articles/{article_id}/attachments/{attachment_id} */
  async deleteArticleAttachment(articleId: number, attachmentId: number): Promise<void> {
    return request.delete(`/articles/${articleId}/attachments/${attachmentId}`)
  },

  /** 添加文章成员：单用户 user_id + role；或按系统角色批量 role_ids + 统一 role */
  async addArticleMember(articleId: number, data: ArticleMemberAdd): Promise<void> {
    return request.post(`/articles/${articleId}/members`, data)
  },

  /** 按系统角色批量移除 POST /articles/{article_id}/members/batch-remove */
  async batchRemoveArticleMembers(articleId: number, data: ArticleMemberBatchRemove): Promise<void> {
    return request.post(`/articles/${articleId}/members/batch-remove`, data)
  },

  // 移除文章成员
  async removeArticleMember(articleId: number, userId: number): Promise<void> {
    return request.delete(`/articles/${articleId}/members/${userId}`)
  },

  // 更新文章成员角色
  async updateArticleMemberRole(articleId: number, userId: number, role: number): Promise<void> {
    return request.put(`/articles/${articleId}/members/${userId}`, { role })
  },

  /** 获取文章管理员列表 GET /api/permissions/admins（无权限时可调用于展示管理员以便申请） */
  async getArticleAdmins(articleId: number): Promise<ArticleAdminItem[]> {
    const list = await permissionApi.getResourceAdmins(PERMISSION_RESOURCE_TYPE.ARTICLE, articleId)
    return list as ArticleAdminItem[]
  },

  /** 获取最近7天内新创建的、已发布且公开可见的文章，按创建时间倒序取前10条
   *  GET /articles/recent-created
   */
  async getRecentCreatedArticles(): Promise<ArticleSearchItem[]> {
    const res = await request.get('/articles/recent-created')
    if (Array.isArray(res)) {
      return res as ArticleSearchItem[]
    }
    if (res && typeof res === 'object' && 'items' in res) {
      return (res as { items: ArticleSearchItem[] }).items || []
    }
    return []
  },

  /** 获取最近7天内有更新的、已发布且公开可见的文章，按更新时间倒序取前10条
   *  GET /articles/recent-updated
   */
  async getRecentUpdatedArticles(): Promise<ArticleSearchItem[]> {
    const res = await request.get('/articles/recent-updated')
    if (Array.isArray(res)) {
      return res as ArticleSearchItem[]
    }
    if (res && typeof res === 'object' && 'items' in res) {
      return (res as { items: ArticleSearchItem[] }).items || []
    }
    return []
  },

  /** 申请文章权限 -> POST /api/applications */
  async applyForEdit(articleId: number, data: { role: number; message?: string | null; reviewer_ids?: number[] | null }): Promise<void> {
    await request.post('/applications', {
      resource_type: APPLICATION_RESOURCE_TYPE.ARTICLE,
      resource_id: articleId,
      applied_role: data.role,
      message: data.message ?? null,
      reviewer_ids: data.reviewer_ids ?? null
    })
  },

  // 搜索文章成员 GET /api/articles/search/members?article_id=&keyword=&is_member=&role_ids=&page=&page_size=
  async searchArticleMembers(params: ArticleMemberSearchParams): Promise<{ items: ArticleMemberSearchItem[]; total: number }> {
    const queryParams: Record<string, any> = {
      article_id: params.article_id
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
    
    const res = await request.get('/articles/search/members', {
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
    
    if (Array.isArray(res)) {
      return { items: res as ArticleMemberSearchItem[], total: res.length }
    }
    
    if (res && typeof res === 'object' && 'items' in res) {
      const o = res as Record<string, unknown>
      const items = (Array.isArray(o.items) ? o.items : []) as ArticleMemberSearchItem[]
      const total = typeof o.total === 'number' ? o.total : items.length
      return { items, total }
    }
    
    return { items: [], total: 0 }
  }
}

/** 文章历史版本 */
export interface ArticleVersion {
  id: number
  article_id: number
  version_number: number
  title: string
  content: string
  summary?: string | null
  tags?: string[] | null
  created_at: string
  created_by_id?: number
  created_by_name?: string
  is_current?: boolean // 是否为当前版本
}

/** 文章成员搜索项 */
export interface ArticleMemberSearchItem {
  id: number
  user_id: number
  username?: string
  email?: string
  is_member?: boolean // 是否为文章成员
  role?: number // 角色：0-只读，1-编辑者，2-管理员
  joined_at?: string // 加入时间
}

/** 搜索文章成员参数 */
export interface ArticleMemberSearchParams {
  article_id: number
  keyword?: string
  is_member?: boolean | null
  /** 按系统角色 ID 筛选（多选） */
  role_ids?: number[]
  page?: number
  page_size?: number
}

/** 添加文章成员：单用户 user_id + role；按系统角色批量 role_ids + 统一 role */
export interface ArticleMemberAdd {
  user_id?: number
  role?: number
  role_ids?: number[]
}

/** 按系统角色批量移除 */
export interface ArticleMemberBatchRemove {
  role_ids: number[]
}

/** 文章管理员项（GET /articles/{id}/admins 返回） */
export interface ArticleAdminItem {
  id?: number
  user_id: number
  username?: string
  email?: string
  [key: string]: unknown
}
