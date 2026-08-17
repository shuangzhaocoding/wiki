<template>
  <div class="activity-list-page">
    <div class="content-header">
      <h1 class="content-title">{{ translate('personalCenter.browseHistory') }}</h1>
    </div>
    <div class="activity-content" :class="{ 'loading-active': loading }">
      <div v-if="loading" class="loading-wrapper">
        <LoadingSpinner :absolute="false" />
      </div>
      <template v-else>
        <div v-if="list.length === 0" class="empty-state">
          <p>{{ translate('personalCenter.browseHistoryEmpty') }}</p>
        </div>
        <template v-else>
          <div class="activity-list">
            <div
              v-for="item in list"
              :key="item.id"
              class="activity-item"
              @click="goToArticle(item)"
            >
              <div class="item-icon browse-history">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
              </div>
              <div class="item-body">
                <h3 class="item-title">{{ parseActivityItem(item).title || '—' }}</h3>
                <span class="item-time">{{ formatTime(parseActivityItem(item).time) }}</span>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Modal, Pager as TinyPager } from '@opentiny/vue'
import { userApi, type UserActivityItem, parseActivityItem } from '../api/user'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'
// @ts-ignore
import LoadingSpinner from '../components/LoadingSpinner.vue'

const router = useRouter()
const localeStore = useLocaleStore()
const loading = ref(false)
const list = ref<UserActivityItem[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const onPageChange = (e: { currentPage: number; pageSize: number }) => {
  currentPage.value = e.currentPage
  pageSize.value = e.pageSize
  fetchList()
}

const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
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

const goToArticle = (item: UserActivityItem) => {
  const { knowledgeBaseId, articleId } = parseActivityItem(item)
  if (knowledgeBaseId) {
    router.push({ path: `/articles/${knowledgeBaseId}`, query: { articleId: String(articleId) } })
  }
}

const fetchList = async () => {
  try {
    loading.value = true
    const { items, total: t } = await userApi.getMyBrowseHistory(currentPage.value, pageSize.value)
    list.value = items
    total.value = t
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
</style>
