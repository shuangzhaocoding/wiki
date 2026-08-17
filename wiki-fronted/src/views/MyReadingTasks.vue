<template>
  <div class="reading-tasks-page">
    <div class="content-header">
      <h1 class="content-title">{{ translate('personalCenter.myReadingTasks') }}</h1>
    </div>
    <div class="filter-tabs">
      <tiny-tabs v-model="activeTab">
        <tiny-tab-item :key="'all'" :title="translate('readingTask.statusAll')" name="all" />
        <tiny-tab-item :key="'0'" :title="translate('readingTask.statusNotStarted')" name="0" />
        <tiny-tab-item :key="'1'" :title="translate('readingTask.statusInProgress')" name="1" />
        <tiny-tab-item :key="'2'" :title="translate('readingTask.statusCompleted')" name="2" />
        <tiny-tab-item :key="'3'" :title="translate('readingTask.statusExpired')" name="3" />
        <tiny-tab-item :key="'4'" :title="translate('readingTask.statusCancelled')" name="4" />
      </tiny-tabs>
    </div>
    <div class="activity-content" :class="{ 'loading-active': loading }">
      <div v-if="loading" class="loading-wrapper">
        <LoadingSpinner :absolute="false" />
      </div>
      <template v-else>
        <div v-if="list.length === 0" class="empty-state">
          <p>{{ translate('personalCenter.myReadingTasksEmpty') }}</p>
        </div>
        <template v-else>
          <div class="activity-list">
            <div
              v-for="item in list"
              :key="item.id"
              class="activity-item"
              @click="goToArticle(item)"
            >
              <div class="item-icon reading-task">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10 9 9 9 8 9"/>
                </svg>
              </div>
              <div class="item-body">
                <h3 class="item-title">{{ item.article_title || '—' }}</h3>
                <div class="item-meta">
                  <span v-if="item.knowledge_base_name" class="meta-item">{{ item.knowledge_base_name }}</span>
                  <span class="meta-item">{{ translate('readingTask.requiredMinutes', { minutes: String(Math.ceil(item.required_seconds / 60)) }) }}</span>
                  <span v-if="item.deadline" class="meta-item">{{ translate('readingTask.deadline') }}: {{ formatDate(item.deadline) }}</span>
                  <span class="meta-item">{{ getStatusText(item.status) }}</span>
                </div>
                <span class="item-time">{{ formatTime(item.created_at) }}</span>
              </div>
              <span class="item-arrow">→</span>
            </div>
          </div>
          <div class="pager-wrap">
            <tiny-pager
              :current-page="currentPage"
              :page-size="pageSize"
              :total="total"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next, jumper"
              :hide-on-single-page="true"
              @page-change="onPageChange"
            />
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Modal, Pager as TinyPager, TinyTabs, TinyTabItem } from '@opentiny/vue'
import { readingTaskApi, type ReadingTaskItem } from '../api/readingTask'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'
// @ts-ignore
import LoadingSpinner from '../components/LoadingSpinner.vue'

const router = useRouter()
const localeStore = useLocaleStore()
const loading = ref(false)
const list = ref<ReadingTaskItem[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const activeTab = ref<string>('all')

const onPageChange = (e: { currentPage: number; pageSize: number }) => {
  currentPage.value = e.currentPage
  pageSize.value = e.pageSize
  fetchList()
}

watch(activeTab, () => {
  currentPage.value = 1
  fetchList()
})

const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

const getStatusText = (status: number): string => {
  const map: Record<number, string> = {
    0: translate('readingTask.statusNotStarted'),
    1: translate('readingTask.statusInProgress'),
    2: translate('readingTask.statusCompleted'),
    3: translate('readingTask.statusExpired'),
    4: translate('readingTask.statusCancelled')
  }
  return map[status] ?? '—'
}

const formatDate = (iso: string) => {
  if (!iso) return '—'
  try {
    const d = new Date(iso)
    if (isNaN(d.getTime())) return '—'
    return d.toLocaleString(localeStore.currentLocale === 'zh' ? 'zh-CN' : 'en-US')
  } catch {
    return '—'
  }
}

const formatTime = (time: string) => {
  if (!time) return ''
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

const goToArticle = (item: ReadingTaskItem) => {
  const href = router.resolve({
    path: `/articles/${item.knowledge_base_id}`,
    query: { articleId: String(item.article_id) }
  }).href
  window.open(href, '_blank')
}

const fetchList = async () => {
  try {
    loading.value = true
    const status = activeTab.value === 'all' ? undefined : Number(activeTab.value)
    const res = await readingTaskApi.getMyReadingTasks({
      status,
      page: currentPage.value,
      page_size: pageSize.value
    })
    list.value = res.items
    total.value = res.total
  } catch (e: any) {
    Modal.message({ message: e?.message || translate('personalCenter.fetchError'), status: 'error' })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped lang="less">
@import './PersonalActivityList.less';

.reading-tasks-page {
  width: 100%;
}

.filter-tabs {
  margin-bottom: 20px;

  :deep(.tiny-tabs) {
    .tiny-tabs__header {
      margin-bottom: 0;
    }
    .tiny-tabs__item {
      padding: 8px 16px;
      font-size: 14px;
    }
  }
}

.item-icon.reading-task {
  background: rgba(34, 197, 94, 0.12);
  color: #22c55e;
}

.item-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
  font-size: 12px;
  color: #666;

  .meta-item {
    &::after {
      content: '·';
      margin-left: 8px;
      color: #bbb;
    }

    &:last-child::after {
      display: none;
    }
  }
}
</style>
