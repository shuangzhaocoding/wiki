// Token 存储工具
const TOKEN_KEY = 'wiki_token'
const TOKEN_TYPE_KEY = 'wiki_token_type'

export const authUtils = {
  // 保存 token
  setToken(token: string, tokenType: string = 'bearer') {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(TOKEN_TYPE_KEY, tokenType)
  },

  // 获取 token
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  },

  // 获取 token type
  getTokenType(): string {
    return localStorage.getItem(TOKEN_TYPE_KEY) || 'bearer'
  },

  // 获取完整的 Authorization header 值
  getAuthHeader(): string | null {
    const token = this.getToken()
    const tokenType = this.getTokenType()
    return token ? `${tokenType} ${token}` : null
  },

  // 清除 token
  clearToken() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(TOKEN_TYPE_KEY)
  },

  // 检查是否已登录
  isAuthenticated(): boolean {
    return !!this.getToken()
  }
}
