<template>
  <div :class="['loading-container', { 'loading-absolute': absolute, 'loading-inline': !absolute }]">
    <div class="loading-spinner">
      <div class="spinner-circle"></div>
      <div class="spinner-circle"></div>
      <div class="spinner-circle"></div>
    </div>
    <p v-if="showText" class="loading-text">{{ text || translate('common.loading') }}</p>
  </div>
</template>

<script setup lang="ts">
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'

const localeStore = useLocaleStore()

interface Props {
  absolute?: boolean
  showText?: boolean
  text?: string
}

withDefaults(defineProps<Props>(), {
  absolute: false,
  showText: true,
  text: ''
})

// 响应式翻译函数
const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}
</script>

<style scoped lang="less">
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.loading-absolute {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
}

.loading-inline {
  min-height: 200px;
}

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 20px;
}

.spinner-circle {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #8b5cf6;
  animation: loading-bounce 1.4s ease-in-out infinite both;
  
  &:nth-child(1) {
    animation-delay: -0.32s;
  }
  
  &:nth-child(2) {
    animation-delay: -0.16s;
  }
  
  &:nth-child(3) {
    animation-delay: 0s;
  }
}

.loading-text {
  color: #8b5cf6;
  font-size: 14px;
  font-weight: 500;
  margin: 0;
  animation: loading-pulse 1.5s ease-in-out infinite;
}

// 加载弹跳动画
@keyframes loading-bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

// 加载脉冲动画
@keyframes loading-pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
