import request from './request'

// 评论创建请求
export interface CommentCreate {
  article_id: number
  parent_id?: number | null
  content: string
}

// 评论更新请求
export interface CommentUpdate {
  content: string
}

// 评论响应
export interface Comment {
  id: number
  article_id: number
  parent_id?: number | null
  comment: string
  user_id: number
  user_name?: string
  user_avatar?: string
  create_time?: string
  updated_at?: string
  like_count?: number
  dislike_count?: number
  is_liked?: boolean
  is_disliked?: boolean
  children?: Comment[] // 子评论
}

// 评论 API
export const commentApi = {
  // 获取文章的评论列表
  async getArticleComments(articleId: number): Promise<Comment[]> {
    const response = await request.get(`/comments/article/${articleId}`)
    if (Array.isArray(response)) {
      return response
    }
    if (response && typeof response === 'object' && 'items' in response) {
      return (response as any).items || []
    }
    return []
  },

  // 创建评论
  async createComment(data: CommentCreate): Promise<Comment> {
    return request.post('/comments', data)
  },

  // 更新评论
  async updateComment(commentId: number, data: CommentUpdate): Promise<Comment> {
    return request.put(`/comments/${commentId}`, data)
  },

  // 删除评论
  async deleteComment(commentId: number): Promise<void> {
    return request.delete(`/comments/${commentId}`)
  },

  // 点赞评论
  async likeComment(commentId: number): Promise<void> {
    return request.post(`/comments/${commentId}/like`)
  },

  // 踩评论
  async dislikeComment(commentId: number): Promise<void> {
    return request.post(`/comments/${commentId}/dislike`)
  }
}
