<template>
  <div class="notifications-page">
    <div class="notifications-container">
      <div class="page-header">
        <h1 class="page-title">{{ translate('notifications.title') }}</h1>
        <div class="header-actions">
          <button
            v-if="filteredUnreadCount > 0"
            type="button"
            class="text-action-btn"
            @click="markAllRead"
          >
            {{ translate('notifications.markAllRead') }}
          </button>
          <button
            v-if="readCount > 0 && activeTab === 'read'"
            type="button"
            class="text-action-btn"
            @click="clearRead"
          >
            {{ translate('notifications.clearRead') }}
          </button>
        </div>
      </div>

      <div class="notifications-body">
        <aside class="notifications-sidebar">
          <button
            class="sidebar-item"
            :class="{ active: typeFilter === 'all' }"
            @click="typeFilter = 'all'"
          >
            {{ translate('notifications.tabAll') }}
          </button>
          <button
            class="sidebar-item"
            :class="{ active: typeFilter === 'reading' }"
            @click="typeFilter = 'reading'"
          >
            签读消息
          </button>
          <button
            class="sidebar-item"
            :class="{ active: typeFilter === 'resource' }"
            @click="typeFilter = 'resource'"
          >
            资源申请
          </button>
          <button
            class="sidebar-item"
            :class="{ active: typeFilter === 'articleFeedback' }"
            @click="typeFilter = 'articleFeedback'"
          >
            文章反馈
          </button>
          <button
            class="sidebar-item"
            :class="{ active: typeFilter === 'commentReply' }"
            @click="typeFilter = 'commentReply'"
          >
            {{ translate('notifications.typeCommentReply') }}
          </button>
          <button
            class="sidebar-item"
            :class="{ active: typeFilter === 'articleComment' }"
            @click="typeFilter = 'articleComment'"
          >
            {{ translate('notifications.typeArticleComment') }}
          </button>
        </aside>

        <div class="notifications-main">
          <div class="tabs">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              class="tab-btn"
              :class="{ active: activeTab === tab.key }"
              @click="activeTab = tab.key"
            >
              {{ tab.label }}
              <span v-if="tab.key === 'unread' && filteredUnreadCount > 0" class="tab-badge">
                {{ filteredUnreadCount > 99 ? '99+' : filteredUnreadCount }}
              </span>
            </button>
          </div>

          <div class="notifications-list">
            <div v-if="loading" class="empty-state">
              <p>{{ translate('common.loading') }}</p>
            </div>
            <div v-else-if="filteredList.length === 0" class="empty-state">
              <p>{{ emptyHint }}</p>
            </div>

            <template v-else>
              <div
                v-for="notification in filteredList"
                :key="notification.id"
                class="notification-item"
                :class="{ unread: !notification.read }"
                @click="handleNotificationClick(notification)"
              >
                <div class="notification-icon" :class="'type-' + notification.type">
                  <svg v-if="notification.type === 'system'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                    <path d="M13.73 21a2 2 0 0 1-3.46 0" />
                  </svg>
                  <svg v-else-if="notification.type === 'comment'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                  <svg v-else-if="notification.type === 'feedback'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                    <circle cx="12" cy="7" r="4" />
                  </svg>
                </div>
                <div class="notification-content">
                  <div class="notification-head">
                    <span class="notification-type-tag" :class="'type-' + notification.type">
                      {{ getTypeLabel(notification.type) }}
                    </span>
                    <span class="notification-time">{{ formatTime(notification.time) }}</span>
                  </div>
                  <h3 class="notification-title">{{ notification.title }}</h3>
                  <p class="notification-message">{{ notification.content }}</p>
                  <p v-if="notification.extra" class="notification-extra">{{ notification.extra }}</p>
                  <span class="notification-status" :class="{ unread: !notification.read }">
                    {{ notification.read ? translate('notifications.tabRead') : translate('notifications.tabUnread') }}
                  </span>
                </div>
                <div v-if="!notification.read" class="unread-dot" />
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Modal } from '@opentiny/vue'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'
import { notificationApi, toNotification, type NotificationItem } from '../api/notification'

const router = useRouter()
const localeStore = useLocaleStore()

const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

type TabKey = 'all' | 'unread' | 'read'
type NotifType =
  | 'system'
  | 'comment'
  | 'feedback'
  | 'mention'
  | 'reading_task_assigned'
  | 'resource_application'
  | 'article_feedback'
  | 'comment_reply'
  | 'article_comment'
type TypeFilter = 'all' | 'reading' | 'resource' | 'articleFeedback' | 'commentReply' | 'articleComment'

interface Notification {
  id: number
  type: NotifType
  title: string
  content: string
  extra?: string
  link?: string
  time: string
  read: boolean
}

const tabs = computed(() => [
  { key: 'all' as TabKey, label: translate('notifications.tabAll') },
  { key: 'unread' as TabKey, label: translate('notifications.tabUnread') },
  { key: 'read' as TabKey, label: translate('notifications.tabRead') }
])

const activeTab = ref<TabKey>('all')
const loading = ref(false)
const list = ref<Notification[]>([])
const typeFilter = ref<TypeFilter>('all')

const filteredUnreadCount = computed(() => list.value.filter((n) => !n.read).length)
const readCount = computed(() => list.value.filter((n) => n.read).length)

const filteredList = computed(() => {
  const data = list.value
  if (activeTab.value === 'unread') return data.filter((n) => !n.read)
  if (activeTab.value === 'read') return data.filter((n) => n.read)
  return data
})

const emptyHint = computed(() => {
  if (activeTab.value === 'unread') return translate('notifications.emptyUnread')
  if (activeTab.value === 'read') return translate('notifications.emptyRead')
  return translate('notifications.empty')
})

const getTypeLabel = (type: NotifType | string) => {
  const keyMap: Record<string, string> = {
    system: 'notifications.typeSystem',
    comment: 'notifications.typeComment',
    feedback: 'notifications.typeFeedback',
    mention: 'notifications.typeMention',
    reading_task_assigned: 'notifications.typeReadingTask',
    resource_application: 'notifications.typeResourceApplication',
    article_feedback: 'notifications.typeArticleFeedback',
    comment_reply: 'notifications.typeCommentReply',
    article_comment: 'notifications.typeArticleComment'
  }
  return translate(keyMap[type] ?? 'notifications.typeSystem')
}

const formatTime = (time: string) => {
  if (!time) return '—'
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  if (minutes < 1) return translate('notifications.time.justNow')
  if (minutes < 60) return translate('notifications.time.minutesAgo', { minutes: String(minutes) })
  if (hours < 24) return translate('notifications.time.hoursAgo', { hours: String(hours) })
  if (days < 30) return translate('notifications.time.daysAgo', { days: String(days) })
  return date.toLocaleDateString()
}

const fetchList = async () => {
  try {
    loading.value = true
    const params: { page: number; page_size: number; type?: string | null } = {
      page: 1,
      page_size: 100
    }
    if (typeFilter.value === 'reading') {
      params.type = 'reading_task_assigned'
    } else if (typeFilter.value === 'resource') {
      params.type = 'resource_application'
    } else if (typeFilter.value === 'articleFeedback') {
      params.type = 'article_feedback'
    } else if (typeFilter.value === 'commentReply') {
      params.type = 'comment_reply'
    } else if (typeFilter.value === 'articleComment') {
      params.type = 'article_comment'
    }
    const res = await notificationApi.getNotifications(params)
    list.value = res.items.map((n: NotificationItem) => toNotification(n))
  } catch (e: any) {
    Modal.message({
      message: e?.message ?? translate('notifications.fetchError'),
      status: 'error'
    })
    list.value = []
  } finally {
    loading.value = false
  }
}

const toggleRead = async (n: Notification) => {
  const newRead = !n.read
  try {
    await notificationApi.updateNotification(n.id, { is_read: newRead })
    n.read = newRead
  } catch (e: any) {
    Modal.message({
      message: e?.message ?? translate('notifications.updateError'),
      status: 'error'
    })
  }
}

const handleNotificationClick = async (n: Notification) => {
  if (!n.read) {
    await toggleRead(n)
  }
  if (n.link) {
      window.open(n.link, '_blank')
    
  }
}

const markAllRead = async () => {
  const unreadList = list.value.filter((n) => !n.read)
  if (unreadList.length === 0) return
  try {
    await Promise.all(unreadList.map((n) => notificationApi.updateNotification(n.id, { is_read: true })))
    unreadList.forEach((n) => { n.read = true })
  } catch (e: any) {
    Modal.message({
      message: e?.message ?? translate('notifications.updateError'),
      status: 'error'
    })
  }
}

const clearRead = () => {
  list.value = list.value.filter((n) => !n.read)
}

watch(typeFilter, () => {
  fetchList()
})

onMounted(() => {
  fetchList()
})
</script>

<style scoped lang="less">
.notifications-page {
  height: calc(100vh - 64px);
  background: #f5f7fa;
  padding: 24px;
}

.notifications-container {
  width: 100%;
  max-width: 100%;
  margin: 0;
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.notifications-body {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  flex: 1;
  min-height: 0; // 允许子元素滚动
}

.notifications-sidebar {
  width: 160px;
  flex-shrink: 0;
  border-right: 1px solid #e5e7eb;
  padding-right: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
}

.sidebar-item {
  text-align: left;
  padding: 8px 10px;
  font-size: 14px;
  color: #666;
  background: none;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  outline: none;

  &:focus-visible {
    outline: none;
    box-shadow: 0 0 0 1px rgba(139, 92, 246, 0.4);
  }

  &.active {
    background: rgba(139, 92, 246, 0.08);
    color: var(--primary-color, #8b5cf6);
    font-weight: 600;
  }

  &:hover {
    background: rgba(139, 92, 246, 0.06);
    color: var(--primary-color, #8b5cf6);
  }
}

.notifications-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #333;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.text-action-btn {
  padding: 4px 8px;
  font-size: 13px;
  color: var(--primary-color, #8b5cf6);
  background: none;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.text-action-btn:hover {
  background: rgba(139, 92, 246, 0.1);
}

.tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.tab-btn {
  position: relative;
  padding: 8px 16px;
  font-size: 14px;
  color: #666;
  background: none;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: color 0.2s, background 0.2s;
  outline: none;

  &:focus-visible {
    outline: none;
    box-shadow: 0 0 0 1px rgba(139, 92, 246, 0.4);
  }

  &:hover {
    color: var(--primary-color, #8b5cf6);
    background: rgba(139, 92, 246, 0.06);
  }

  &.active {
    color: var(--primary-color, #8b5cf6);
    font-weight: 600;
    background: rgba(139, 92, 246, 0.1);
  }
}

.tab-badge {
  display: inline-block;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  margin-left: 6px;
  font-size: 11px;
  font-weight: 600;
  line-height: 18px;
  color: #fff;
  background: var(--primary-color, #8b5cf6);
  border-radius: 9px;
  vertical-align: middle;
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.notification-item {
  position: relative;
  display: flex;
  gap: 14px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;

  &:hover {
    border-color: rgba(139, 92, 246, 0.3);
    box-shadow: 0 2px 8px rgba(139, 92, 246, 0.08);
  }

  &.unread {
    background: rgba(139, 92, 246, 0.04);
    border-color: rgba(139, 92, 246, 0.25);
  }
}

.notification-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;

  svg {
    width: 20px;
    height: 20px;
    stroke: currentColor;
  }

  &.type-system {
    color: #8b5cf6;
    background: rgba(139, 92, 246, 0.12);
  }
  &.type-comment {
    color: #0ea5e9;
    background: rgba(14, 165, 233, 0.12);
  }
  &.type-feedback {
    color: #f59e0b;
    background: rgba(245, 158, 11, 0.12);
  }
  &.type-mention {
    color: #10b981;
    background: rgba(16, 185, 129, 0.12);
  }
}

.notification-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.notification-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.notification-type-tag {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;

  &.type-system {
    color: #6d28d9;
    background: rgba(139, 92, 246, 0.15);
  }
  &.type-comment {
    color: #0369a1;
    background: rgba(14, 165, 233, 0.15);
  }
  &.type-feedback {
    color: #b45309;
    background: rgba(245, 158, 11, 0.15);
  }
  &.type-mention {
    color: #047857;
    background: rgba(16, 185, 129, 0.15);
  }
}

.notification-time {
  font-size: 12px;
  color: #999;
  margin-left: auto;
}

.notification-title {
  margin: 0 0 6px 0;
  font-size: 15px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
}

.notification-message {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.55;
}

.notification-extra {
  margin: 8px 0 0 0;
  font-size: 13px;
  color: #999;
}

.notification-status {
  display: block;
  margin-top: auto;
  padding-top: 8px;
  font-size: 12px;
  color: #999;
  text-align: right;

  &.unread {
    color: var(--primary-color, #8b5cf6);
    font-weight: 500;
  }
}

.unread-dot {
  flex-shrink: 0;
  width: 8px;
  height: 8px;
  margin-top: 6px;
  border-radius: 50%;
  background: var(--primary-color, #8b5cf6);
}

.empty-state {
  text-align: center;
  padding: 48px 20px;
  color: #999;
  font-size: 15px;

  p {
    margin: 0;
  }
}

// 平板 (≤1024px)：类型筛选改为顶部横向滚动，主区域占满高度
@media (max-width: 1024px) {
  .notifications-page {
    padding: 16px;
    height: calc(100vh - 64px);
  }

  .notifications-container {
    padding: 16px;
    border-radius: 10px;
  }

  .notifications-body {
    flex-direction: column;
    gap: 12px;
    margin-top: 8px;
  }

  .notifications-sidebar {
    width: 100%;
    flex-direction: row;
    flex-wrap: nowrap;
    align-items: stretch;
    gap: 8px;
    padding-right: 0;
    padding-bottom: 12px;
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
    overflow-x: auto;
    overflow-y: hidden;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: thin;

    &::-webkit-scrollbar {
      height: 6px;
    }

    &::-webkit-scrollbar-thumb {
      background: rgba(139, 92, 246, 0.25);
      border-radius: 3px;
    }
  }

  .sidebar-item {
    flex: 0 0 auto;
    white-space: nowrap;
    padding: 10px 14px;
    font-size: 13px;
  }

  .notifications-main {
    min-height: 0;
  }

  .tabs {
    margin-bottom: 12px;
    padding-bottom: 12px;
    overflow-x: auto;
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;

    &::-webkit-scrollbar {
      display: none;
    }
  }

  .tab-btn {
    flex: 0 0 auto;
    padding: 8px 14px;
    font-size: 13px;
  }

  .page-header {
    margin-bottom: 12px;
  }
}

// 手机 (≤768px)：顶栏高度与留白收紧，列表卡片更易读
@media (max-width: 768px) {
  .notifications-page {
    padding: 12px;
    height: calc(100vh - 56px);
    box-sizing: border-box;
  }

  .notifications-container {
    padding: 12px;
    border-radius: 8px;
  }

  .page-title {
    font-size: 18px;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
    margin-bottom: 10px;
  }

  .header-actions {
    justify-content: flex-end;
    flex-wrap: wrap;
  }

  .text-action-btn {
    font-size: 12px;
    padding: 6px 10px;
  }

  .tabs {
    flex-wrap: nowrap;
    gap: 2px;
    margin-bottom: 12px;
    padding-bottom: 10px;
  }

  .tab-btn {
    padding: 8px 10px;
    font-size: 12px;
  }

  .tab-badge {
    margin-left: 4px;
    min-width: 16px;
    height: 16px;
    line-height: 16px;
    font-size: 10px;
  }

  .notification-item {
    padding: 12px;
    gap: 10px;
    align-items: flex-start;
  }

  .notification-icon {
    width: 36px;
    height: 36px;
    border-radius: 8px;

    svg {
      width: 18px;
      height: 18px;
    }
  }

  .notification-head {
    flex-wrap: wrap;
    gap: 6px;
  }

  .notification-time {
    margin-left: 0;
    width: 100%;
    order: 3;
  }

  .notification-type-tag {
    order: 1;
  }

  .notification-title {
    font-size: 14px;
  }

  .notification-message {
    font-size: 13px;
  }

  .notification-status {
    text-align: left;
    padding-top: 6px;
  }

  .empty-state {
    padding: 32px 16px;
    font-size: 14px;
  }
}

// 小屏手机 (≤480px)
@media (max-width: 480px) {
  .notifications-page {
    padding: 8px;
  }

  .notifications-container {
    padding: 10px;
  }

  .sidebar-item {
    padding: 8px 12px;
    font-size: 12px;
  }
}
</style>
