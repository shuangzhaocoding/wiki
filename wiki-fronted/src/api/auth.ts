import request from './request'

// 登录请求参数
export interface LoginRequest {
  username: string
  password: string
}

// 注册请求参数
export interface RegisterRequest {
  username: string
  password: string
  email: string
  email_code: string
  nickname?: string | null
}

export interface SendRegisterCodeRequest {
  email: string
}

export interface SendResetPasswordCodeRequest {
  email: string
}

export interface ResetPasswordRequest {
  email: string
  email_code: string
  new_password: string
}

// Token 响应
export interface TokenResponse {
  access_token: string
  token_type: string
}

// 用户信息响应
export interface UserResponse {
  id: number
  username: string
  email?: string
  avatar?: string
  status?: number
  created_at?: string
  last_login_at?: string
}

// 更新用户信息请求
export interface UserUpdateRequest {
  username?: string
  email?: string
}

// 认证 API
export const authApi = {
  // 登录
  async login(data: LoginRequest): Promise<TokenResponse> {
    return request.post('/auth/login', data)
  },

  // 注册
  async register(data: RegisterRequest): Promise<TokenResponse | Record<string, any>> {
    return request.post('/auth/register', data)
  },

  // 发送注册邮箱验证码
  async sendRegisterCode(data: SendRegisterCodeRequest): Promise<Record<string, any>> {
    return request.post('/auth/send-register-code', data)
  },

  // 发送重置密码邮箱验证码
  async sendResetPasswordCode(data: SendResetPasswordCodeRequest): Promise<Record<string, any>> {
    return request.post('/auth/send-reset-password-code', data)
  },

  // 重置密码
  async resetPassword(data: ResetPasswordRequest): Promise<Record<string, any>> {
    return request.post('/auth/reset-password', data)
  },

  // 获取当前用户信息
  async getCurrentUser(): Promise<UserResponse> {
    return request.get('/users/me')
  },

  // 更新当前用户信息
  async updateUser(data: UserUpdateRequest): Promise<UserResponse> {
    return request.put('/users/me', data)
  }
}
