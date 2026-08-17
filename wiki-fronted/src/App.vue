<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
import { computed } from 'vue'
// @ts-ignore
import AppHeader from './components/AppHeader.vue'

const route = useRoute()
// 登录、注册、忘记密码不显示 header（name + 规范化 path，避免尾部斜杠仍挂载 AppHeader）
const showHeader = computed(() => {
  if (route.name === 'Login' || route.name === 'Register' || route.name === 'ForgotPassword') {
    return false
  }
  const p = (route.path.replace(/\/$/, '') || '/') as string
  return p !== '/login' && p !== '/register' && p !== '/forgot-password'
})
</script>

<template>
  <div class="app-container">
    <AppHeader v-if="showHeader" />
    <RouterView class="app-main" />
  </div>
</template>

<style lang="less">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}
</style>
