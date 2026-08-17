<template>
  <div class="knowledge-management-page">
    <div class="main-layout">
      <!-- 左侧导航栏 -->
      <aside class="sidebar">
        <nav class="sidebar-nav">
          <router-link to="/" class="sidebar-item">
            <span>{{ translate('nav.home') }}</span>
          </router-link>
          
          <div class="sidebar-group">
            <div class="sidebar-group-header" @click="toggleSpaceManagement">
              <span>{{ translate('knowledge.spaceManagement') }}</span>
              <svg 
                viewBox="0 0 1024 1024" 
                width="12" 
                height="12" 
                fill="currentColor"
                :class="{ 'rotate': spaceManagementExpanded }"
              >
                <path d="M512 768L128 384h768z"/>
              </svg>
            </div>
            <div v-if="spaceManagementExpanded" class="sidebar-group-content">
              <router-link to="/team-spaces" class="sidebar-sub-item">
                {{ translate('knowledge.teamSpace') }}
              </router-link>
              <router-link to="/knowledge" class="sidebar-sub-item">
                {{ translate('knowledge.knowledgeBase') }}
              </router-link>
            </div>
          </div>

          <div class="sidebar-group">
            <div class="sidebar-group-header" @click="togglePersonalCenter">
              <span>{{ translate('knowledge.personalCenter') }}</span>
              <svg 
                viewBox="0 0 1024 1024" 
                width="12" 
                height="12" 
                fill="currentColor"
                :class="{ 'rotate': personalCenterExpanded }"
              >
                <path d="M512 768L128 384h768z"/>
              </svg>
            </div>
            <div v-if="personalCenterExpanded" class="sidebar-group-content">
              <!-- 个人中心子菜单项 -->
            </div>
          </div>

          <div class="sidebar-group">
            <div class="sidebar-group-header" @click="toggleAnnouncement">
              <span>{{ translate('knowledge.announcement') }}</span>
              <svg 
                viewBox="0 0 1024 1024" 
                width="12" 
                height="12" 
                fill="currentColor"
                :class="{ 'rotate': announcementExpanded }"
              >
                <path d="M512 768L128 384h768z"/>
              </svg>
            </div>
            <div v-if="announcementExpanded" class="sidebar-group-content">
              <router-link to="/knowledge" class="sidebar-sub-item">
                {{ translate('knowledge.developmentLog') }}
              </router-link>
            </div>
          </div>
        </nav>
      </aside>

      <!-- 主内容区域 -->
      <main class="content-area">
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
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'

const localeStore = useLocaleStore()

// 侧边栏展开状态
const spaceManagementExpanded = ref(true)
const personalCenterExpanded = ref(false)
const announcementExpanded = ref(true)

// 标签页
const activeTab = ref('updateLog')

// 响应式翻译函数
const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

const toggleSpaceManagement = () => {
  spaceManagementExpanded.value = !spaceManagementExpanded.value
}

const togglePersonalCenter = () => {
  personalCenterExpanded.value = !personalCenterExpanded.value
}

const toggleAnnouncement = () => {
  announcementExpanded.value = !announcementExpanded.value
}
</script>

<style scoped lang="less">
.knowledge-management-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.main-layout {
  display: flex;
  flex: 1;
  width: 100%;
}

.sidebar {
  width: 200px;
  background: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  padding: 20px 0;
  min-height: calc(100vh - 64px);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
}

.sidebar-item {
  padding: 12px 20px;
  color: #333;
  text-decoration: none;
  font-size: 14px;
  transition: background-color 0.3s;

  &:hover {
    background-color: #e4e7ed;
  }

  &.router-link-active {
    background-color: #e4e7ed;
    color: var(--primary-color, #8b5cf6);
    font-weight: 500;
  }
}

.sidebar-group {
  margin-top: 8px;
}

.sidebar-group-header {
  padding: 12px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  color: #333;
  font-size: 14px;
  transition: background-color 0.3s;

  &:hover {
    background-color: #e4e7ed;
  }

  svg {
    transition: transform 0.3s;
    transform: rotate(-90deg);

    &.rotate {
      transform: rotate(0deg);
    }
  }
}

.sidebar-group-content {
  padding-left: 20px;
}

.sidebar-sub-item {
  display: block;
  padding: 10px 20px;
  color: #666;
  text-decoration: none;
  font-size: 13px;
  transition: color 0.3s;

  &:hover {
    color: var(--primary-color, #8b5cf6);
  }

  &.router-link-active {
    color: var(--primary-color, #8b5cf6);
    font-weight: 500;
  }
}

.content-area {
  flex: 1;
  padding: 30px 40px;
  background: #fff;
  margin: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

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

@media (max-width: 768px) {
  .main-layout {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    min-height: auto;
  }

  .content-area {
    margin: 10px;
    padding: 20px;
  }
}
</style>
