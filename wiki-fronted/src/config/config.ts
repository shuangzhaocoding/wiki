// 仅供 Vite 开发代理使用；生产构建由 nginx 将 /api 反代到后端
const isProductEnv = false // false true

let apiUrl = ''
if (isProductEnv) {
  apiUrl = 'http://python:5005'
} else {
  apiUrl = 'http://localhost:5005'
}
const useConfig = {
  apiUrl
}
export default useConfig