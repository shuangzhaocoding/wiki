import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import userConfig from './src/config/config'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    // 反向代理 / 内网域名访问 dev 时需放行 Host，否则 Vite 会返回 “Blocked request”
    allowedHosts: ['fae-wiki.narwaltech.com', 'localhost'],
    proxy: {
      '/api/': {
        target: userConfig.apiUrl,
        changeOrigin: true,
        secure: false
      }
    }
  }
})
