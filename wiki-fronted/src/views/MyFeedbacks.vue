<template>
  <div class="feedbacks-page">
    <div class="content-header">
      <h1 class="content-title">{{ translate('feedback.myFeedbacks') }}</h1>
      <div class="header-filters">
        <tiny-select
          v-model="statusFilter"
          :placeholder="translate('feedback.filterByStatus')"
          style="width: 150px;"
          clearable
          @change="handleStatusFilterChange"
        >
          <tiny-option :label="translate('feedback.status.all')" :value="null" />
          <tiny-option :label="translate('feedback.status.pending')" :value="1" />
          <tiny-option :label="translate('feedback.status.processing')" :value="2" />
          <tiny-option :label="translate('feedback.status.resolved')" :value="3" />
          <tiny-option :label="translate('feedback.status.closed')" :value="4" />
        </tiny-select>
      </div>
    </div>
    <div class="feedbacks-content" :class="{ 'loading-active': loading }">
      <div v-if="loading" class="loading-wrapper">
        <LoadingSpinner :absolute="false" />
      </div>
      <template v-else>
        <div v-if="list.length === 0" class="empty-state">
          <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          <p>{{ translate('feedback.myFeedbacksEmpty') }}</p>
        </div>
        <template v-else>
          <tiny-grid
            :data="list"
            :loading="loading"
            border
            highlight-hover-row
            width="100%"
            class="feedbacks-grid"
            show-header
          >
            <tiny-grid-column field="article_title" :title="translate('feedback.articleTitle')" min-width="180" align="left" show-overflow="tooltip">
              <template #default="{ row }">
                <span
                  v-if="row.knowledge_base_id != null && row.article_id != null"
                  class="title-link"
                  @click="goToArticle(row)"
                >
                  {{ row.article_title || '—' }}
                </span>
                <span v-else>{{ row.article_title || '—' }}</span>
              </template>
            </tiny-grid-column>
            <tiny-grid-column field="user_name" :title="translate('feedback.feedbackUser')" width="120" align="left" show-overflow="tooltip">
              <template #default="{ row }">
                <span>{{ row.user_name || '—' }}</span>
              </template>
            </tiny-grid-column>
            <tiny-grid-column field="created_at" :title="translate('feedback.feedbackTime')" width="160" align="center">
              <template #default="{ row }">
                <span class="time-text">{{ formatTime(row.created_at) }}</span>
              </template>
            </tiny-grid-column>
            <tiny-grid-column field="feedback_type" :title="translate('feedback.feedbackType')" width="100" align="center">
              <template #default="{ row }">
                <span class="type-badge">{{ getFeedbackTypeText(row.feedback_type) }}</span>
              </template>
            </tiny-grid-column>
            <tiny-grid-column field="content" :title="translate('feedback.content')" width="100" align="center">
              <template #default="{ row }">
                <span class="content-link" @click="openContentDialog(row)">{{ translate('feedback.clickToView') }}</span>
              </template>
            </tiny-grid-column>
            <tiny-grid-column field="status" :title="translate('feedback.statusLabel')" width="100" align="center">
              <template #default="{ row }">
                <span class="status-badge" :class="getStatusBadgeClass(row.status)">
                  {{ getStatusText(row.status) }}
                </span>
              </template>
            </tiny-grid-column>
            <tiny-grid-column field="admin_reply" :title="translate('feedback.adminReply')" min-width="150" align="left" show-overflow="tooltip">
              <template #default="{ row }">
                <span v-if="row.admin_reply" class="reply-text">{{ row.admin_reply }}</span>
                <span v-else class="text-placeholder">—</span>
              </template>
            </tiny-grid-column>
            <tiny-grid-column field="reply_time" :title="translate('feedback.replyTime')" width="160" align="center">
              <template #default="{ row }">
                <span v-if="row.reply_time" class="time-text">{{ formatTime(row.reply_time) }}</span>
                <span v-else class="text-placeholder">—</span>
              </template>
            </tiny-grid-column>
          </tiny-grid>
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

    <!-- 反馈内容只读弹窗 -->
    <tiny-dialog-box
      v-model:visible="contentDialogVisible"
      :title="translate('feedback.content')"
      width="90%"
      max-height="80%"
      class="content-view-dialog"
    >
      <FluentEditorV4
        v-if="contentDialogVisible"
        :model-value="contentDialogContent"
        :modules="previewEditorModules"
        :toolbar="false"
        :disabled="true"
        class="content-preview-editor"
      />
      <template #footer>
        <tiny-button @click="contentDialogVisible = false">{{ translate('common.close') }}</tiny-button>
      </template>
    </tiny-dialog-box>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Select as TinySelect, Option as TinyOption, Pager as TinyPager, 
Grid as TinyGrid, GridColumn as TinyGridColumn, Modal, DialogBox as TinyDialogBox, 
Button as TinyButton } from '@opentiny/vue'
import FluentEditorV4 from '../components/FluentEditorV4.vue'
import { feedbackApi, type MyFeedbackItem, FEEDBACK_STATUS_PENDING, FEEDBACK_STATUS_PROCESSING, FEEDBACK_STATUS_RESOLVED, FEEDBACK_STATUS_CLOSED, FEEDBACK_TYPE_SUGGESTION, FEEDBACK_TYPE_BUG, FEEDBACK_TYPE_OTHER } from '../api/feedback'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'
// @ts-ignore
import LoadingSpinner from '../components/LoadingSpinner.vue'
const router = useRouter()
const localeStore = useLocaleStore()
const loading = ref(false)
const list = ref<MyFeedbackItem[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const statusFilter = ref<number | null>(null)

const contentDialogVisible = ref(false)
const contentDialogContent = ref('')
// 预览模式编辑器配置（无工具栏，只读）
const previewEditorModules = {
  toolbar: false
}


const goToArticle = (row: MyFeedbackItem) => {
  const kbId = row.knowledge_base_id ?? (row as Record<string, unknown>).knowledge_base_id
  const articleId = row.article_id
  if (kbId != null && articleId != null) {
    const route = router.resolve({ path: `/articles/${kbId}`, query: { articleId: String(articleId) } })
    window.open(route.href, '_blank')
  }
}

const openContentDialog = (row: MyFeedbackItem) => {
  contentDialogContent.value = row.content || ''
  contentDialogVisible.value = true
}

const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

const onPageChange = (e: { currentPage: number; pageSize: number }) => {
  currentPage.value = e.currentPage
  pageSize.value = e.pageSize
  fetchList()
}

const handleStatusFilterChange = () => {
  currentPage.value = 1
  fetchList()
}

const formatTime = (time: string) => {
  if (!time) return ''
  const date = new Date(time)
  const localeMap: Record<string, string> = {
    'zh': 'zh-CN',
    'en': 'en-US',
    'ko': 'ko-KR',
    'de': 'de-DE',
    'ja': 'ja-JP',
    'fr': 'fr-FR'
  }
  const locale = localeMap[localeStore.currentLocale] || 'zh-CN'
  return date.toLocaleString(locale)
}

const getStatusText = (status: number) => {
  if (status === FEEDBACK_STATUS_PENDING) return translate('feedback.status.pending')
  if (status === FEEDBACK_STATUS_PROCESSING) return translate('feedback.status.processing')
  if (status === FEEDBACK_STATUS_RESOLVED) return translate('feedback.status.resolved')
  if (status === FEEDBACK_STATUS_CLOSED) return translate('feedback.status.closed')
  return translate('feedback.status.unknown')
}

const getStatusBadgeClass = (status: number) => {
  if (status === FEEDBACK_STATUS_PENDING) return 'badge-pending'
  if (status === FEEDBACK_STATUS_PROCESSING) return 'badge-processing'
  if (status === FEEDBACK_STATUS_RESOLVED) return 'badge-resolved'
  if (status === FEEDBACK_STATUS_CLOSED) return 'badge-closed'
  return ''
}

const getFeedbackTypeText = (type: number) => {
  if (type === FEEDBACK_TYPE_SUGGESTION) return translate('feedback.type.suggestion')
  if (type === FEEDBACK_TYPE_BUG) return translate('feedback.type.bug')
  if (type === FEEDBACK_TYPE_OTHER) return translate('feedback.type.other')
  return translate('feedback.type.unknown')
}

const fetchList = async () => {
  try {
    loading.value = true
    const res = await feedbackApi.getMyFeedbacks({
      page: currentPage.value,
      page_size: pageSize.value,
      status: statusFilter.value
    })
    list.value = res.items
    total.value = res.total
  } catch (e: any) {
    Modal.message({ message: e?.message || translate('feedback.fetchError'), status: 'error' })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped lang="less">
.feedbacks-page {
  width: 100%;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.content-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color, #303133);
}

.header-filters {
  display: flex;
  gap: 12px;
}

.feedbacks-content {
  width: 100%;
  &.loading-active {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
  }
}

.loading-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
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

.feedbacks-grid {
  background: var(--bg-color, #fff);
  border-radius: 8px;
  overflow: hidden;
}

:deep(.tiny-grid thead),
:deep(.tiny-grid .tiny-grid-header) {
  background: var(--bg-color-secondary, #fafafa);
}

:deep(.tiny-grid th),
:deep(.tiny-grid .tiny-grid-header th) {
  font-weight: 600;
  color: var(--text-color, #303133);
  padding: 12px 16px;
  border-bottom: 2px solid var(--border-color, #e4e7ed);
}

:deep(.tiny-grid tbody td),
:deep(.tiny-grid .tiny-grid-body td) {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color, #e4e7ed);
}

:deep(.tiny-grid tbody tr:hover td) {
  background: rgba(139, 92, 246, 0.04);
}

.type-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  background: rgba(139, 92, 246, 0.1);
  color: var(--primary-color, #8b5cf6);
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  &.badge-pending {
    background: rgba(230, 162, 60, 0.1);
    color: var(--warning-color, #e6a23c);
  }
  &.badge-processing {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
  }
  &.badge-resolved {
    background: rgba(103, 194, 58, 0.1);
    color: var(--success-color, #67c23a);
  }
  &.badge-closed {
    background: rgba(144, 147, 153, 0.1);
    color: var(--text-color-secondary, #909399);
  }
}

.content-text,
.reply-text {
  font-size: 13px;
  color: var(--text-color, #303133);
}

.text-placeholder {
  color: var(--text-color-secondary, #909399);
  font-style: italic;
}

.time-text {
  color: var(--text-color-secondary, #606266);
  font-size: 13px;
}

.title-link {
  color: var(--primary-color, #8b5cf6);
  cursor: pointer;
  text-decoration: none;
  transition: opacity 0.2s;
  &:hover {
    text-decoration: underline;
    opacity: 0.85;
  }
}

.content-link {
  color: var(--primary-color, #8b5cf6);
  cursor: pointer;
  transition: opacity 0.2s;
  &:hover {
    opacity: 0.85;
    text-decoration: underline;
  }
}

.content-preview-editor {
  min-height: 180px;
}

:deep(.content-preview-editor .ql-container),
:deep(.content-preview-editor .ql-editor),
:deep(.content-view-dialog .ql-toolbar) {
  border: none !important;
}

:deep(.content-view-dialog .ql-toolbar) {
  display: none;
}

:deep(.tiny-editor-wrapper) {
  border: none !important;
}

.pager-wrap {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}
</style>
