<template>
  <div class="feedback-handling-page">
    <div class="content-header">
      <h1 class="content-title">{{ translate('feedback.handling') }}</h1>
    </div>
    <div class="feedback-handling-content">
      <div class="empty-state">
        <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>
        </svg>
        <p>{{ translate('feedback.handlingHint') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'

const localeStore = useLocaleStore()

const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}
</script>

<style scoped lang="less">
.feedback-handling-page {
  width: 100%;
}

.content-header {
  margin-bottom: 24px;
}

.content-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color, #303133);
}

.feedback-handling-content {
  width: 100%;
  min-height: 400px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-color-secondary, #909399);
  text-align: center;
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}
</style>
