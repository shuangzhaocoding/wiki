<template>
  <div class="sign-reading-management-page">
    <div class="content-header">
      <h1 class="content-title">{{ translate('signReadingManagement.title') }}</h1>
    </div>

    <div class="filter-bar">
      <span class="filter-label">{{ translate('signReadingManagement.batchStatus') }}：</span>
      <tiny-select
        v-model="statusFilter"
        :placeholder="translate('signReadingManagement.filterByStatus')"
        style="width: 160px"
        @change="onStatusFilterChange"
      >
        <tiny-option :label="translate('signReadingManagement.statusAll')" :value="-1" />
        <tiny-option :label="translate('signReadingManagement.batchStatusActive')" :value="0" />
        <tiny-option :label="translate('signReadingManagement.batchStatusCancelled')" :value="1" />
      </tiny-select>
    </div>

    <div class="table-view">
      <tiny-grid
        ref="gridRef"
        :data="list"
        :loading="loading"
        border
        highlight-hover-row
        width="100%"
        class="task-grid"
        show-header
        :expand-config="{ trigger: 'row' }"
        row-id="batch_id"
        @toggle-expand-change="onExpandChange"
      >
        <tiny-grid-column type="expand" width="50">
          <template #default="{ row }">
            <div class="expand-content">
              <div v-if="batchTasksLoading[row.batch_id]" class="expand-loading">
                {{ translate('common.loading') }}
              </div>
              <tiny-grid
                v-else-if="(batchTasksMap[row.batch_id]?.length ?? 0) > 0"
                :data="batchTasksMap[row.batch_id] || []"
                border
                size="small"
                class="nested-task-grid"
              >
                <tiny-grid-column
                  field="username"
                  :title="translate('signReadingManagement.taskUser')"
                  min-width="120"
                >
                  <template #default="{ row: task }">
                    {{ task.nickname || task.username || '—' }}
                  </template>
                </tiny-grid-column>
                <tiny-grid-column
                  field="role_name"
                  :title="translate('signReadingManagement.taskRole')"
                  min-width="120"
                >
                  <template #default="{ row: task }">
                    {{ task.role_name || '—' }}
                  </template>
                </tiny-grid-column>
                <tiny-grid-column
                  field="status"
                  :title="translate('signReadingManagement.taskStatus')"
                  width="100"
                  align="center"
                >
                  <template #default="{ row: task }">
                    <span class="batch-status-badge" :class="getTaskStatusClass(task.status)">
                      {{ getTaskStatusText(task.status) }}
                    </span>
                  </template>
                </tiny-grid-column>
                <tiny-grid-column
                  field="actual_seconds"
                  :title="translate('signReadingManagement.actualDuration')"
                  width="120"
                  align="center"
                >
                  <template #default="{ row: task }">
                    {{ task.actual_seconds != null ? translate('readingTask.requiredMinutes', { minutes: String(Math.ceil((task.actual_seconds || 0) / 60)) }) : '—' }}
                  </template>
                </tiny-grid-column>
              </tiny-grid>
              <div v-else class="expand-empty">
                {{ translate('signReadingManagement.noTasks') }}
              </div>
            </div>
          </template>
        </tiny-grid-column>
        <tiny-grid-column
          field="article_title"
          :title="translate('signReadingManagement.articleTitle')"
          min-width="180"
          align="left"
        >
          <template #default="{ row }">
            <a class="article-link" @click.stop="goToArticle(row)">
              {{ row.article_title || '—' }}
            </a>
          </template>
        </tiny-grid-column>
        <tiny-grid-column
          field="knowledge_base_name"
          :title="translate('signReadingManagement.knowledgeBase')"
          min-width="140"
          align="left"
        >
          <template #default="{ row }">
            {{ row.knowledge_base_name || '—' }}
          </template>
        </tiny-grid-column>
        <tiny-grid-column
          field="required_seconds"
          :title="translate('signReadingManagement.requiredDuration')"
          width="120"
          align="center"
        >
          <template #default="{ row }">
            {{ translate('readingTask.requiredMinutes', { minutes: String(Math.ceil(row.required_seconds / 60)) }) }}
          </template>
        </tiny-grid-column>
        <tiny-grid-column
          field="deadline"
          :title="translate('readingTask.deadline')"
          width="160"
          align="center"
        >
          <template #default="{ row }">
            {{ formatDate(row.deadline) || '—' }}
          </template>
        </tiny-grid-column>
        <tiny-grid-column
          field="created_by_name"
          :title="translate('signReadingManagement.creator')"
          min-width="120"
          align="left"
        >
          <template #default="{ row }">
            {{ row.created_by_name || '—' }}
          </template>
        </tiny-grid-column>
        <tiny-grid-column
          field="role_ids"
          :title="translate('signReadingManagement.targetRoles')"
          min-width="150"
          align="left"
        >
          <template #default="{ row }">
            <span v-if="row.role_ids && row.role_ids.length">
              {{ getRoleNames(row.role_ids) }}
            </span>
            <span v-else>—</span>
          </template>
        </tiny-grid-column>
        <tiny-grid-column
          field="task_count"
          :title="translate('signReadingManagement.taskCount')"
          width="100"
          align="center"
        >
          <template #default="{ row }">
            {{ row.task_count ?? 0 }}
          </template>
        </tiny-grid-column>
        <tiny-grid-column
          field="status"
          :title="translate('signReadingManagement.batchStatus')"
          width="100"
          align="center"
        >
          <template #default="{ row }">
            <span class="batch-status-badge" :class="getBatchStatusClass(row.status)">
              {{ getBatchStatusText(row.status) }}
            </span>
          </template>
        </tiny-grid-column>
        <tiny-grid-column
          field="actions"
          :title="translate('userManagement.actions')"
          width="180"
          align="center"
          fixed="right"
        >
          <template #default="{ row }">
            <tiny-button size="small" type="text" :text="textBtn" @click="goToArticle(row)">
              {{ translate('signReadingManagement.viewArticle') }}
            </tiny-button>
            <tiny-button type="text" v-if="row.batch_id && row.status !== 1" size="small" :text="textBtn" @click="openEditDialog(row)">
              {{ translate('common.edit') }}
            </tiny-button>
            <tiny-button type="text" v-if="row.batch_id && row.status !== 1" size="small" :text="textBtn" @click="handleCancelBatch(row)">
              {{ translate('signReadingManagement.cancelBatch') }}
            </tiny-button>
          </template>
        </tiny-grid-column>
      </tiny-grid>
      <div v-if="list.length === 0 && !loading" class="empty-state">
        <p>{{ translate('signReadingManagement.empty') }}</p>
      </div>
    </div>

    <!-- 编辑批次弹窗 -->
    <tiny-dialog-box
      v-model:visible="editDialogVisible"
      :title="translate('signReadingManagement.editBatch')"
      width="500px"
    >
      <tiny-form ref="editFormRef" :model="editForm" label-width="120px">
        <tiny-form-item :label="translate('article.signReadDuration')" prop="duration">
          <tiny-input
            v-model.number="editForm.duration"
            type="number"
            min="1"
            :placeholder="translate('article.signReadDurationPlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('article.signReadDeadline')" prop="deadline">
          <tiny-date-picker
            v-model="editForm.deadline"
            type="date"
            :placeholder="translate('article.signReadDeadlinePlaceholder')"
            style="width: 100%"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('article.signReadTargets')" prop="roleIds">
          <tiny-select
            v-model="editForm.roleIds"
            multiple
            filterable
            :placeholder="translate('article.signReadTargetsPlaceholder')"
            style="width: 100%"
          >
            <tiny-option
              v-for="role in allRoles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </tiny-select>
        </tiny-form-item>
      </tiny-form>
      <template #footer>
        <tiny-button @click="editDialogVisible = false">{{ translate('common.cancel') }}</tiny-button>
        <tiny-button type="primary" :loading="editSubmitting" @click="handleEditSubmit">
          {{ translate('common.confirm') }}
        </tiny-button>
      </template>
    </tiny-dialog-box>

    <div v-if="total > 0" class="pager-wrap">
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Modal, Grid as TinyGrid, GridColumn as TinyGridColumn, Button as TinyButton, Pager as TinyPager, DialogBox as TinyDialogBox, Form as TinyForm, FormItem as TinyFormItem, Input as TinyInput, DatePicker as TinyDatePicker, Select as TinySelect, Option as TinyOption } from '@opentiny/vue'
import { readingTaskApi, type ReadingTaskGroupItem, type BatchTaskItem } from '../api/readingTask'
import { roleApi, type Role } from '../api/role'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'

const router = useRouter()
const localeStore = useLocaleStore()

// text 按钮样式（OpenTiny 类型定义为 string，实际可接受 boolean）
const textBtn = true as unknown as string

const loading = ref(false)
const list = ref<ReadingTaskGroupItem[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const allRoles = ref<Role[]>([])
const statusFilter = ref<number>(-1)
const gridRef = ref()

// 展开行：批次下的任务
const batchTasksMap = ref<Record<number, BatchTaskItem[]>>({})
const batchTasksLoading = ref<Record<number, boolean>>({})

// 编辑批次
const editDialogVisible = ref(false)
const editFormRef = ref()
const editSubmitting = ref(false)
const editingBatchId = ref<number | null>(null)
const editForm = ref({
  duration: null as number | null,
  deadline: null as Date | null,
  roleIds: [] as number[]
})

const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}
// template refs
void gridRef
void editFormRef

const roleMap = computed(() => {
  const map: Record<number, string> = {}
  allRoles.value.forEach(r => {
    map[r.id] = r.name
  })
  return map
})

// 批次状态：0-有效，1-已取消
const getBatchStatusText = (status: number | undefined) => {
  if (status === 0) return translate('signReadingManagement.batchStatusActive')
  if (status === 1) return translate('signReadingManagement.batchStatusCancelled')
  return '—'
}

const getBatchStatusClass = (status: number | undefined) => {
  if (status === 0) return 'batch-status-active'
  if (status === 1) return 'batch-status-cancelled'
  return ''
}

// 任务状态：0-未开始，1-进行中，2-已完成，3-已过期，4-已取消
const getTaskStatusText = (status: number) => {
  const map: Record<number, string> = {
    0: translate('readingTask.statusNotStarted'),
    1: translate('readingTask.statusInProgress'),
    2: translate('readingTask.statusCompleted'),
    3: translate('readingTask.statusExpired'),
    4: translate('readingTask.statusCancelled')
  }
  return map[status] ?? '—'
}

const getTaskStatusClass = (status: number) => {
  if (status === 2) return 'batch-status-active'
  if (status === 3 || status === 4) return 'batch-status-cancelled'
  return 'batch-status-pending'
}

const getRoleNames = (roleIds: number[]) => {
  if (!roleIds?.length) return '—'
  return roleIds.map(id => roleMap.value[id] ?? `#${id}`).join(', ')
}

const formatDate = (iso: string | null) => {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    if (isNaN(d.getTime())) return ''
    return d.toLocaleString(localeStore.currentLocale === 'zh' ? 'zh-CN' : 'en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return ''
  }
}

const openEditDialog = async (row: ReadingTaskGroupItem) => {
  const batchId = row.batch_id
  if (batchId == null) {
    Modal.message({ message: translate('signReadingManagement.batchIdRequired'), status: 'warning' })
    return
  }
  editingBatchId.value = batchId
  editForm.value = {
    duration: Math.ceil(row.required_seconds / 60),
    deadline: row.deadline ? new Date(row.deadline) : null,
    roleIds: [...(row.role_ids || [])]
  }
  // 打开弹窗时加载角色列表，确保下拉框有最新数据
  await fetchRoles()
  editDialogVisible.value = true
}

const handleEditSubmit = async () => {
  if (editingBatchId.value == null) return
  if (!editForm.value.duration || editForm.value.duration <= 0) {
    Modal.message({ message: translate('article.signReadDurationRequired'), status: 'warning' })
    return
  }
  editSubmitting.value = true
  try {
    const deadlineStr = editForm.value.deadline
      ? (() => {
          const d = new Date(editForm.value.deadline as Date)
          d.setHours(23, 59, 59, 999)
          return d.toISOString()
        })()
      : undefined
    await readingTaskApi.updateBatch(editingBatchId.value, {
      required_seconds: (editForm.value.duration as number) * 60,
      deadline: deadlineStr,
      role_ids: editForm.value.roleIds
    })
    Modal.message({ message: translate('signReadingManagement.updateSuccess'), status: 'success' })
    editDialogVisible.value = false
    await fetchList()
  } catch (e: any) {
    Modal.message({
      message: e?.message || translate('signReadingManagement.updateError'),
      status: 'error'
    })
  } finally {
    editSubmitting.value = false
  }
}

const handleCancelBatch = async (row: ReadingTaskGroupItem) => {
  const batchId = row.batch_id
  if (batchId == null) {
    Modal.message({ message: translate('signReadingManagement.batchIdRequired'), status: 'warning' })
    return
  }
  try {
    await Modal.confirm({
      title: translate('signReadingManagement.cancelBatchConfirmTitle'),
      message: translate('signReadingManagement.cancelBatchConfirmMessage'),
      status: 'warning'
    })
  } catch {
    return
  }
  try {
    const res = await readingTaskApi.cancelBatch(batchId)
    Modal.message({
      message: translate('signReadingManagement.cancelSuccess', { count: String(res.cancelled_count) }),
      status: 'success'
    })
    await fetchList()
  } catch (e: any) {
    Modal.message({
      message: e?.message || translate('signReadingManagement.cancelError'),
      status: 'error'
    })
  }
}

const goToArticle = (row: ReadingTaskGroupItem) => {
  const href = router.resolve({
    path: `/articles/${row.knowledge_base_id}`,
    query: { articleId: String(row.article_id) }
  }).href
  window.open(href, '_blank')
}

const onPageChange = (e: { currentPage: number; pageSize: number }) => {
  currentPage.value = e.currentPage
  pageSize.value = e.pageSize
  fetchList()
}

const onStatusFilterChange = () => {
  currentPage.value = 1
  fetchList()
}

const onExpandChange = async (
  eventParams: { $table?: { expandeds?: ReadingTaskGroupItem[] }; row?: ReadingTaskGroupItem; rowIndex?: number },
  _event?: Event
) => {
  const row = eventParams?.row
  if (!row?.batch_id) return
  // 事件在 toggle 之后触发，通过 expandeds 判断是否已展开
  const expanded = eventParams?.$table?.expandeds?.includes(row) ?? false
  if (!expanded) return
  if (batchTasksMap.value[row.batch_id]) return // 已加载过
  batchTasksLoading.value = { ...batchTasksLoading.value, [row.batch_id]: true }
  try {
    const res = await readingTaskApi.getBatchTasks(row.batch_id, { page_size: 100 })
    batchTasksMap.value = { ...batchTasksMap.value, [row.batch_id]: res.items }
  } catch (e) {
    Modal.message({
      message: (e as Error)?.message || translate('signReadingManagement.fetchTasksError'),
      status: 'error'
    })
  } finally {
    batchTasksLoading.value = { ...batchTasksLoading.value, [row.batch_id]: false }
  }
}

const fetchList = async () => {
  try {
    loading.value = true
    const res = await readingTaskApi.getAllReadingTasks({
      page: currentPage.value,
      page_size: pageSize.value,
      status: statusFilter.value >= 0 ? statusFilter.value : undefined
    })
    list.value = res.items
    total.value = res.total
  } catch (e: any) {
    Modal.message({
      message: e?.message || translate('signReadingManagement.fetchError'),
      status: 'error'
    })
  } finally {
    loading.value = false
  }
}

const fetchRoles = async () => {
  try {
    const res = await roleApi.getRoles({ page: 1, page_size: 100, status: 1 })
    allRoles.value = res.items || []
  } catch (e) {
    console.error('加载角色列表失败', e)
    allRoles.value = []
  }
}

onMounted(async () => {
  await fetchRoles()
  await fetchList()
})
</script>

<style scoped lang="less">
.sign-reading-management-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: calc(100vh - 64px);
}

.content-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;

  .content-title {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    color: #303133;
  }
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;

  .filter-label {
    font-size: 14px;
    color: #606266;
  }
}

.table-view {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);

  .task-grid {
    :deep(.tiny-grid) {
      width: 100% !important;
    }
  }

  .article-link {
    color: var(--primary-color, #8b5cf6);
    cursor: pointer;
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }

  .batch-status-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;

    &.batch-status-active {
      background: #ecfdf5;
      color: #059669;
    }

    &.batch-status-cancelled {
      background: #f3f4f6;
      color: #6b7280;
    }

    &.batch-status-pending {
      background: #fef3c7;
      color: #d97706;
    }
  }

  .expand-content {
    padding: 16px 24px;
    background: #fafafa;
  }

  .expand-loading {
    padding: 20px;
    text-align: center;
    color: #909399;
    font-size: 14px;
  }

  .expand-empty {
    padding: 20px;
    text-align: center;
    color: #909399;
    font-size: 14px;
  }

  .nested-task-grid {
    :deep(.tiny-grid) {
      width: 100% !important;
    }
  }
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
  font-size: 14px;
}

.pager-wrap {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
