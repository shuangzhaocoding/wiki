<template>
  <div class="applications-page">
    <div class="content-header">
      <h1 class="content-title">{{ translate('applications.myApplications') }}</h1>
      <div class="header-filters">
        <tiny-select
          v-model="statusFilter"
          :placeholder="translate('applications.filterByStatus')"
          style="width: 150px;"
          clearable
          @change="handleStatusFilterChange"
        >
          <tiny-option :label="translate('applications.status.all')" :value="null" />
          <tiny-option :label="translate('applications.status.pending')" :value="0" />
          <tiny-option :label="translate('applications.status.approved')" :value="1" />
          <tiny-option :label="translate('applications.status.rejected')" :value="2" />
        </tiny-select>
      </div>
    </div>
    <div class="applications-content" :class="{ 'loading-active': loading }">
      <div v-if="loading" class="loading-wrapper">
        <LoadingSpinner :absolute="false" />
      </div>
      <template v-else>
        <div v-if="list.length === 0" class="empty-state">
          <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 12h6m-3-3v6m-9 1V7a2 2 0 0 1 2-2h6l2 2h6a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          </svg>
          <p>{{ translate('applications.myApplicationsEmpty') }}</p>
        </div>
        <template v-else>
          <tiny-grid
            :data="list"
            :loading="loading"
            border
            highlight-hover-row
            width="100%"
            class="applications-grid"
            show-header
          >
            <tiny-grid-column field="resource_name" :title="translate('applications.resourceName')" :label="translate('applications.resourceName')" min-width="180" align="left" show-overflow="tooltip">
              <template #default="{ row }">
                <div class="resource-cell">
                  <span class="resource-icon">
                    <svg v-if="row.resource_type === 1" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                    </svg>
                    <svg v-else-if="row.resource_type === 2" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="currentColor">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>
                    </svg>
                  </span>
                  <span 
                    class="resource-name resource-link" 
                    @click.stop="handleResourceClick(row)"
                    :title="row.resource_name || translate('applications.unknownResource')"
                  >
                    {{ row.resource_name || translate('applications.unknownResource') }}
                  </span>
                </div>
              </template>
            </tiny-grid-column>
            <tiny-grid-column field="resource_type" :title="translate('applications.resourceType')" :label="translate('applications.resourceType')" width="120" align="center">
              <template #default="{ row }">
                <span class="resource-type-badge">{{ getResourceTypeText(row.resource_type) }}</span>
              </template>
            </tiny-grid-column>
            <tiny-grid-column field="applicant_name" :title="translate('applications.applicant')" :label="translate('applications.applicant')" width="120" align="left" show-overflow="tooltip">
              <template #default="{ row }">
                <span>{{ row.applicant_name || row.applicant_email || String(row.applicant_id) }}</span>
              </template>
            </tiny-grid-column>
            <tiny-grid-column field="applied_role" :title="translate('applications.appliedRole')" :label="translate('applications.appliedRole')" width="100" align="center">
              <template #default="{ row }">
                <span class="role-badge">{{ getRoleText(row.applied_role) }}</span>
              </template>
            </tiny-grid-column>
            <tiny-grid-column field="status" :title="translate('applications.status')" :label="translate('applications.status')" width="100" align="center">
              <template #default="{ row }">
                <span class="status-badge" :class="getStatusBadgeClass(row.status)">
                  {{ getStatusText(row.status) }}
                </span>
              </template>
            </tiny-grid-column>
            <tiny-grid-column field="message" :title="translate('applications.message')" :label="translate('applications.message')" min-width="200" align="left" show-overflow="tooltip">
              <template #default="{ row }">
                <span v-if="row.message" class="message-text">{{ row.message }}</span>
                <span v-else class="text-placeholder">—</span>
              </template>
            </tiny-grid-column>
            <tiny-grid-column field="reviewers" :title="translate('applications.nextReviewers')" :label="translate('applications.nextReviewers')" min-width="150" align="left" show-overflow="tooltip">
              <template #default="{ row }">
                <span v-if="row.reviewers && row.reviewers.length > 0" class="reviewers-text">
                  {{ row.reviewers.map((r: any) => r.name || String(r.id)).join(', ') }}
                </span>
                <span v-else class="text-placeholder">—</span>
              </template>
            </tiny-grid-column>
            <tiny-grid-column field="replied_by_name" :title="translate('applications.reviewedBy')" :label="translate('applications.reviewedBy')" width="120" align="left" show-overflow="tooltip">
              <template #default="{ row }">
                <span v-if="row.replied_by_name">{{ row.replied_by_name }}</span>
                <span v-else class="text-placeholder">—</span>
              </template>
            </tiny-grid-column>
            <tiny-grid-column field="reply_message" :title="translate('applications.reply')" :label="translate('applications.reply')" min-width="150" align="left" show-overflow="tooltip">
              <template #default="{ row }">
                <span v-if="row.reply_message" class="reply-text">{{ row.reply_message }}</span>
                <span v-else class="text-placeholder">—</span>
              </template>
            </tiny-grid-column>
            <tiny-grid-column field="created_at" :title="translate('applications.appliedAt')" :label="translate('applications.appliedAt')" width="160" align="center">
              <template #default="{ row }">
                <span class="time-text">{{ formatTime(row.created_at) }}</span>
              </template>
            </tiny-grid-column>
            <tiny-grid-column field="replied_at" :title="translate('applications.reviewedAt')" :label="translate('applications.reviewedAt')" width="160" align="center">
              <template #default="{ row }">
                <span v-if="row.replied_at" class="time-text">{{ formatTime(row.replied_at) }}</span>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Select as TinySelect, Option as TinyOption, Pager as TinyPager, Grid as TinyGrid, GridColumn as TinyGridColumn, Modal } from '@opentiny/vue'
import { applicationApi, type Application, APPLICATION_STATUS, APPLICATION_ROLE, RESOURCE_TYPE } from '../api/application'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'
// @ts-ignore
import LoadingSpinner from '../components/LoadingSpinner.vue'

const localeStore = useLocaleStore()
const loading = ref(false)
const list = ref<Application[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const statusFilter = ref<number | null>(null)

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
  if (status === APPLICATION_STATUS.PENDING) return translate('applications.status.pending')
  if (status === APPLICATION_STATUS.APPROVED) return translate('applications.status.approved')
  if (status === APPLICATION_STATUS.REJECTED) return translate('applications.status.rejected')
  return translate('applications.status.unknown')
}

const getStatusBadgeClass = (status: number) => {
  if (status === APPLICATION_STATUS.PENDING) return 'badge-pending'
  if (status === APPLICATION_STATUS.APPROVED) return 'badge-approved'
  if (status === APPLICATION_STATUS.REJECTED) return 'badge-rejected'
  return ''
}

const getResourceTypeText = (type: number) => {
  if (type === RESOURCE_TYPE.TEAM_SPACE) return translate('applications.resourceType.teamSpace')
  if (type === RESOURCE_TYPE.KNOWLEDGE_BASE) return translate('applications.resourceType.knowledgeBase')
  if (type === RESOURCE_TYPE.ARTICLE) return translate('applications.resourceType.article')
  return translate('applications.resourceType.unknown')
}

const getRoleText = (role: number) => {
  if (role === APPLICATION_ROLE.READONLY) return translate('article.role.readonly')
  if (role === APPLICATION_ROLE.EDITOR) return translate('article.role.editor')
  if (role === APPLICATION_ROLE.ADMIN) return translate('article.role.admin')
  return translate('applications.role.unknown')
}

const handleResourceClick = (row: Application) => {
  if (!row.resource_name) return
  
  let url = ''
  if (row.resource_type === RESOURCE_TYPE.TEAM_SPACE) {
    // 团队空间
    url = `/knowledge/team-spaces?name=${encodeURIComponent(row.resource_name)}`
  } else if (row.resource_type === RESOURCE_TYPE.KNOWLEDGE_BASE) {
    // 知识库
    url = `/knowledge/knowledge-spaces?name=${encodeURIComponent(row.resource_name)}`
  } else if (row.resource_type === RESOURCE_TYPE.ARTICLE) {
    // 文章
    const knowledgeBaseId = (row as any).knowledge_base_id || row.resource_id
    url = `/articles/${knowledgeBaseId}?articleId=${row.resource_id}`
  } else {
    return
  }
  
  window.open(url, '_blank')
}

const fetchList = async () => {
  try {
    loading.value = true
    const res = await applicationApi.getApplications({
      list_type: 'my',
      status: statusFilter.value,
      page: currentPage.value,
      page_size: pageSize.value
    })
    list.value = res.items
    total.value = res.total
  } catch (e: any) {
    Modal.message({ message: e?.message || translate('applications.fetchError'), status: 'error' })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped lang="less">
.applications-page {
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

.applications-content {
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

.applications-grid {
  background: var(--bg-color, #fff);
  border-radius: 8px;
  overflow: hidden;
}

:deep(.tiny-grid) {
  border-radius: 8px;
}

:deep(.tiny-grid__wrapper) {
  border-radius: 8px;
}

:deep(.tiny-grid thead),
:deep(.tiny-grid .tiny-grid-header) {
  background: var(--bg-color-secondary, #fafafa);
}

:deep(.tiny-grid th),
:deep(.tiny-grid thead th),
:deep(.tiny-grid .tiny-grid-header th),
:deep(.tiny-grid .tiny-grid-header__column) {
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

:deep(.tiny-grid tbody tr:hover td),
:deep(.tiny-grid .tiny-grid-row:hover td) {
  background: rgba(139, 92, 246, 0.04);
}

.resource-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.resource-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color, #8b5cf6);

  svg {
    width: 18px;
    height: 18px;
  }
}

.resource-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.resource-link {
  color: var(--primary-color, #8b5cf6);
  cursor: pointer;
  transition: color 0.2s ease;
  
  &:hover {
    color: var(--primary-color-hover, #7c3aed);
    text-decoration: underline;
  }
}

.resource-type-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  background: rgba(139, 92, 246, 0.1);
  color: var(--primary-color, #8b5cf6);
}

.role-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;

  &.badge-pending {
    background: rgba(230, 162, 60, 0.1);
    color: var(--warning-color, #e6a23c);
  }

  &.badge-approved {
    background: rgba(103, 194, 58, 0.1);
    color: var(--success-color, #67c23a);
  }

  &.badge-rejected {
    background: rgba(245, 108, 108, 0.1);
    color: var(--danger-color, #f56c6c);
  }
}

.message-text,
.reviewers-text,
.reply-text {
  color: var(--text-color, #303133);
  font-size: 13px;
}

.text-placeholder {
  color: var(--text-color-secondary, #909399);
  font-style: italic;
}

.time-text {
  color: var(--text-color-secondary, #606266);
  font-size: 13px;
}

.pager-wrap {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .content-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  :deep(.tiny-grid) {
    font-size: 12px;
  }

  :deep(.tiny-grid th),
  :deep(.tiny-grid td) {
    padding: 8px 12px;
  }
}
</style>
