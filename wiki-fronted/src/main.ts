import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import '@opentiny/vue-theme/index.css'
import App from './App.vue'
import { router } from './router'
import { initTheme } from './utils/theme'
// 一些旧浏览器或内置 WebView 不支持 crypto.randomUUID，这里做一次全局兼容处理
if (typeof window !== 'undefined') {
  const g: any = window as any
  const cryptoRef: any = g.crypto || g.msCrypto || {}

  function fallbackRandomUUID() {
    // RFC4122 v4 简单实现
    let getRandomValues = cryptoRef.getRandomValues?.bind(cryptoRef) as
      | ((arr: Uint8Array) => Uint8Array)
      | undefined

    if (!getRandomValues) {
      // 退化实现，安全性要求不高，只用于组件内部 key 等
      getRandomValues = (arr: Uint8Array) => {
        for (let i = 0; i < arr.length; i++) {
          arr[i] = Math.floor(Math.random() * 256)
        }
        return arr
      }
    }

    const bytes = new Uint8Array(16)
    getRandomValues(bytes)

    // Per RFC4122 v4
    bytes[6] = ((bytes[6] ?? 0) & 0x0f) | 0x40
    bytes[8] = ((bytes[8] ?? 0) & 0x3f) | 0x80

    const hex: string[] = []
    for (let i = 0; i < bytes.length; i++) {
      hex.push((bytes[i] ?? 0).toString(16).padStart(2, '0'))
    }

    return `${hex[0]}${hex[1]}${hex[2]}${hex[3]}-${hex[4]}${hex[5]}-${hex[6]}${hex[7]}-${hex[8]}${hex[9]}-${hex[10]}${hex[11]}${hex[12]}${hex[13]}${hex[14]}${hex[15]}`
  }

  if (!g.crypto) {
    g.crypto = {
      getRandomValues: cryptoRef.getRandomValues?.bind(cryptoRef),
      randomUUID: fallbackRandomUUID
    }
  } else if (typeof (g.crypto as any).randomUUID !== 'function') {
    ;(g.crypto as any).randomUUID = fallbackRandomUUID
  }
}

// 初始化主题
initTheme()

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')
