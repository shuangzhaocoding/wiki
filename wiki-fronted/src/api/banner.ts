import request from './request'

// Banner 数据结构
export interface Banner {
  id: number
  title: string
  description?: string | null
  image_url: string
  link_url?: string | null
  sort_order: number
  status: number // 0-禁用，1-启用
  created_at?: string
  updated_at?: string
  created_by?: string | null
  updated_by?: string | null
}

// Banner 创建请求
export interface BannerCreate {
  title: string
  description?: string | null
  image_url: string
  link_url?: string | null
  sort_order?: number
  status?: number
}

// Banner 更新请求
export interface BannerUpdate {
  title?: string | null
  description?: string | null
  image_url?: string | null
  link_url?: string | null
  sort_order?: number | null
  status?: number | null
}

// Banner 列表响应
export interface BannerListResponse {
  items: Banner[]
  total: number
}

// Banner 筛选参数
export interface BannerFilterParams {
  page?: number
  page_size?: number
  status?: number | null // 0-禁用，1-启用
  keyword?: string | null // 标题关键字
}

function normalizeBannerList(res: unknown): BannerListResponse {
  if (Array.isArray(res)) {
    return { items: res as Banner[], total: res.length }
  }
  if (res && typeof res === 'object') {
    const o = res as Record<string, unknown>
    const items = (Array.isArray(o.items) ? o.items : []) as Banner[]
    const total = typeof o.total === 'number' ? o.total : items.length
    return { items, total }
  }
  return { items: [], total: 0 }
}

// Banner 管理 API
export const bannerApi = {
  /** 获取 Banner 列表 GET /api/banners */
  async getBanners(params?: BannerFilterParams): Promise<BannerListResponse> {
    const query: Record<string, any> = {}
    if (params?.page) query.page = params.page
    if (params?.page_size) query.page_size = params.page_size
    if (params?.status !== undefined && params?.status !== null) {
      query.status = params.status
    }
    if (params?.keyword) query.keyword = params.keyword

    const res = await request.get('/banners', { params: query })
    return normalizeBannerList(res)
  },

  /** 创建 Banner POST /api/banners */
  async createBanner(data: BannerCreate): Promise<Banner> {
    return await request.post('/banners', data)
  },

  /** 更新 Banner PUT /api/banners/{banner_id} */
  async updateBanner(bannerId: number, data: BannerUpdate): Promise<Banner> {
    return await request.put(`/banners/${bannerId}`, data)
  },

  /** 删除 Banner DELETE /api/banners/{banner_id} */
  async deleteBanner(bannerId: number): Promise<void> {
    return await request.delete(`/banners/${bannerId}`)
  },

  /** 更新 Banner 状态 PUT /api/banners/{banner_id}/status */
  async updateBannerStatus(bannerId: number, status: number): Promise<void> {
    // 后端接口定义为：PUT /api/banners/{banner_id}/status?status={status}
    return await request.put(`/banners/${bannerId}/status`, undefined, {
      params: { status }
    })
  }
}

