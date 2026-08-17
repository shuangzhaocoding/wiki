<template>
  <div class="no-permission-page">
    <div class="no-permission-content">
      <div class="icon-wrapper">
        <svg viewBox="0 0 1024 1024" width="120" height="120" fill="currentColor" class="icon">
          <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z"/>
          <path d="M464 688a48 48 0 1 0 96 0 48 48 0 1 0-96 0zm24-112h48c4.4 0 8-3.6 8-8V296c0-4.4-3.6-8-8-8h-48c-4.4 0-8 3.6-8 8v272c0 4.4 3.6 8 8 8z"/>
        </svg>
      </div>
      <h2 class="title">{{ translate('common.noPermission') }}</h2>
      <p class="description">{{ translate('common.noPermissionDescription') }}</p>
      <div class="actions">
        <tiny-button type="primary" @click="goHome">
          {{ translate('common.backToHome') }}
        </tiny-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { TinyButton } from '@opentiny/vue'
import { useRouter } from 'vue-router'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'

const router = useRouter()
const localeStore = useLocaleStore()

const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

const goHome = () => {
  router.push('/')
}
</script>

<style scoped lang="less">
.no-permission-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  width: 100%;
}

.no-permission-content {
  text-align: center;
  padding: 40px;
}

.icon-wrapper {
  margin-bottom: 24px;
  color: #d3d3d3;
}

.icon {
  display: inline-block;
}

.title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
}

.description {
  font-size: 16px;
  color: #666;
  margin: 0 0 32px 0;
  line-height: 1.6;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}
</style>
