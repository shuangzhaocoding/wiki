<template>
  <div class="knowledge-announcement-page">
    <div class="content-header">
      <h1 class="content-title">{{ translate('knowledge.announcement') }}</h1>
    </div>

    <div class="content-tabs">
      <div 
        class="tab-item" 
        :class="{ active: activeTab === 'updateLog' }"
        @click="activeTab = 'updateLog'"
      >
        {{ translate('knowledge.updateLog') }}
      </div>
      <div 
        class="tab-item" 
        :class="{ active: activeTab === 'userGroup' }"
        @click="activeTab = 'userGroup'"
      >
        {{ translate('knowledge.userGroup') }}
      </div>
      <div 
        class="tab-item" 
        :class="{ active: activeTab === 'features' }"
        @click="activeTab = 'features'"
      >
        {{ translate('knowledge.features') }}
      </div>
    </div>

    <div class="content-body">
      <div v-if="activeTab === 'updateLog'" class="update-log-list">
        <div class="update-item">
          <span class="new-badge">NEW</span>
          <div class="update-content">
            <h3 class="update-title">{{ translate('knowledge.version') }} v1.1</h3>
            <span class="update-date">2024-07-01</span>
          </div>
        </div>
        <div class="update-item">
          <div class="update-content">
            <h3 class="update-title">{{ translate('knowledge.version') }} v1.0</h3>
            <span class="update-date">2024-06-07</span>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'userGroup'" class="tab-content">
        <p>{{ translate('knowledge.userGroupContent') }}</p>
      </div>

      <div v-if="activeTab === 'features'" class="tab-content">
        <p>{{ translate('knowledge.featuresContent') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'

const localeStore = useLocaleStore()

// 标签页
const activeTab = ref('updateLog')

// 响应式翻译函数
const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}
</script>

<style scoped lang="less">
.content-header {
  margin-bottom: 30px;
}

.content-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.content-tabs {
  display: flex;
  gap: 30px;
  border-bottom: 2px solid #e4e7ed;
  margin-bottom: 30px;
}

.tab-item {
  padding: 12px 0;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  position: relative;
  transition: color 0.3s;

  &:hover {
    color: var(--primary-color, #8b5cf6);
  }

  &.active {
    color: var(--primary-color, #8b5cf6);
    font-weight: 500;

    &::after {
      content: '';
      position: absolute;
      bottom: -2px;
      left: 0;
      right: 0;
      height: 2px;
      background-color: var(--primary-color, #8b5cf6);
    }
  }
}

.content-body {
  min-height: 400px;
}

.update-log-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.update-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  transition: box-shadow 0.3s;

  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
}

.new-badge {
  padding: 4px 8px;
  background-color: #f56c6c;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  border-radius: 4px;
  white-space: nowrap;
}

.update-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.update-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.update-date {
  font-size: 14px;
  color: #999;
}

.tab-content {
  padding: 20px 0;
  color: #666;
  line-height: 1.6;
}
</style>
