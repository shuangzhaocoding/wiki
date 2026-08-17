import axios from 'axios'
import { authUtils } from '../utils/auth'
import { Modal } from '@opentiny/vue'
import { router } from '../router'
import { getLocaleBcp47 } from '../i18n'

// 创建 axios 实例
// 使用相对路径，通过 Vite 代理转发到后端
const request = axios.create({
  baseURL: '/api',
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：添加 token
request.interceptors.request.use(
  (config) => {
    const authHeader = authUtils.getAuthHeader()
    if (authHeader) {
      config.headers.Authorization = authHeader
    }
    // 与界面语言一致，便于后端返回本地化文案或校验
    config.headers['Accept-Language'] = getLocaleBcp47()
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 后端响应格式接口
interface ApiResponse<T = any> {
  code: number
  data: T
  message?: string
}

/** 同一时间段内多次失败只弹一次，避免并发接口同时报错刷屏 */
let lastErrorToastAt = 0
const ERROR_TOAST_COOLDOWN_MS = 1000

function showRequestError(message: string) {
  const now = Date.now()
  if (now - lastErrorToastAt < ERROR_TOAST_COOLDOWN_MS) {
    return
  }
  lastErrorToastAt = now
  console.log('message', message)

  Modal.message({
    message: message || '请求失败',
    status: 'error',
    duration: 3000
  })
}

// 响应拦截器：处理错误
request.interceptors.response.use(
  (response) => {
    const res: ApiResponse = response.data

    if (res.code === 200) {
      return res.data
    }
    if (res.code === 401) {
      authUtils.clearToken()
      Modal.message({ message: '登录已过期，请重新登录', status: 'error' })
      router.push('/login')
      return Promise.reject({
        code: 401,
        message: '登录已过期，请重新登录'
      })
    }
    const errMsg = res.message || '请求失败'
    showRequestError(errMsg)
    return Promise.reject({
      code: res.code,
      message: errMsg
    })
  },
  (error) => {
    if (error.response) {
      const res: ApiResponse = error.response.data || {}
      const errMsg = res.message || error.message || '请求失败'
      showRequestError(errMsg)
      return Promise.reject({
        code: res.code || error.response.status,
        message: errMsg
      })
    }
    const errMsg = error.message || '网络异常，请稍后重试'
    showRequestError(errMsg)
    return Promise.reject({
      code: -1,
      message: errMsg
    })
  }
)

export default request
