<template>
  <div class="permission-management-page">
    <div class="content-header">
      <h1 class="content-title">{{ translate('knowledge.permissionManagement') }}</h1>
      <tiny-button type="primary" @click="showCreateModal = true">
        {{ translate('permissionManagement.create') }}
      </tiny-button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-bar">
      <tiny-input
        v-model="searchKeyword"
        :placeholder="translate('permissionManagement.searchPlaceholder')"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
        style="width: 300px;"
      >
        <template #prefix>
          <svg viewBox="0 0 1024 1024" width="16" height="16" fill="currentColor">
            <path d="M469.333 128c-188.586 0-341.333 152.747-341.333 341.333 0 188.587 152.747 341.333 341.333 341.333 72.533 0 139.52-22.613 194.56-61.227l165.547 165.546c16.64 16.64 43.52 16.64 60.16 0 16.64-16.64 16.64-43.52 0-60.16L723.627 750.08c38.613-55.04 61.226-122.027 61.226-194.56 0-188.587-152.747-341.333-341.333-341.333z m0 85.333c141.227 0 256 114.774 256 256s-114.773 256-256 256-256-114.774-256-256 114.773-256 256-256z"/>
          </svg>
        </template>
      </tiny-input>
      <tiny-select
        v-model="filterStatus"
        :placeholder="translate('permissionManagement.statusFilter')"
        clearable
        style="width: 150px;"
        @change="handleSearch"
      >
        <tiny-option :label="translate('permissionManagement.statusAll')" :value="null" />
        <tiny-option :label="translate('permissionManagement.statusEnabled')" :value="1" />
        <tiny-option :label="translate('permissionManagement.statusDisabled')" :value="0" />
      </tiny-select>
      <tiny-select
        v-model="filterCategory"
        :placeholder="translate('permissionManagement.categoryFilter')"
        clearable
        style="width: 150px;"
        @change="handleSearch"
      >
        <tiny-option :label="translate('permissionManagement.categoryAll')" :value="null" />
        <tiny-option 
          v-for="cat in categories" 
          :key="cat" 
          :label="cat" 
          :value="cat" 
        />
      </tiny-select>
      <tiny-button @click="handleSearch">{{ translate('common.search') }}</tiny-button>
    </div>

    <!-- 权限列表表格 -->
    <div class="table-view">
      <tiny-grid
        :data="permissions"
        :loading="loading"
        border
        highlight-hover-row
        width="100%"
        class="permission-grid"
        show-header
      >
        <tiny-grid-column 
          field="name" 
          :title="translate('permissionManagement.name')" 
          :label="translate('permissionManagement.name')" 
          min-width="150" 
          align="left"
        />
        <tiny-grid-column 
          field="code" 
          :title="translate('permissionManagement.code')" 
          :label="translate('permissionManagement.code')" 
          min-width="150" 
          align="left"
        >
          <template #default="{ row }">
            <span class="permission-code-badge">{{ row.code }}</span>
          </template>
        </tiny-grid-column>
        <tiny-grid-column 
          field="category" 
          :title="translate('permissionManagement.category')" 
          :label="translate('permissionManagement.category')" 
          width="120" 
          align="center"
        >
          <template #default="{ row }">
            <span>{{ row.category || '—' }}</span>
          </template>
        </tiny-grid-column>
        <tiny-grid-column 
          field="description" 
          :title="translate('permissionManagement.description')" 
          :label="translate('permissionManagement.description')" 
          min-width="200" 
          show-overflow="tooltip" 
          align="left"
        >
          <template #default="{ row }">
            <span>{{ row.description || '—' }}</span>
          </template>
        </tiny-grid-column>
        <tiny-grid-column 
          field="status" 
          :title="translate('permissionManagement.status')" 
          :label="translate('permissionManagement.status')" 
          width="100" 
          align="center"
        >
          <template #default="{ row }">
            <span class="status-badge" :class="row.status === 1 ? 'status-enabled' : 'status-disabled'">
              {{ row.status === 1 ? translate('permissionManagement.statusEnabled') : translate('permissionManagement.statusDisabled') }}
            </span>
          </template>
        </tiny-grid-column>
        <tiny-grid-column 
          field="created_at" 
          :title="translate('permissionManagement.createdAt')" 
          :label="translate('permissionManagement.createdAt')" 
          width="160" 
          align="center"
        >
          <template #default="{ row }">
            {{ formatDate(row.created_at) || '—' }}
          </template>
        </tiny-grid-column>
        <tiny-grid-column 
          field="actions" 
          :title="translate('permissionManagement.actions')" 
          :label="translate('permissionManagement.actions')" 
          width="160" 
          align="center"
          fixed="right"
        >
          <template #default="{ row }">
            <div class="table-actions" @click.stop>
              <button 
                type="button"
                class="table-action-btn"
                @click="handleEditPermission(row)"
                :title="translate('permissionManagement.edit')"
              >
                <svg viewBox="0 0 1024 1024" width="14" height="14" fill="currentColor">
                  <path d="M832 512a32 32 0 1 1 64 0v352a32 32 0 0 1-32 32H160a32 32 0 0 1-32-32V160a32 32 0 0 1 32-32h352a32 32 0 1 1 0 64H192v640h640V512z"/>
                  <path d="M469.952 554.24l45.248-45.248 141.888 141.888-45.248 45.248zM832 128a32 32 0 0 1 9.408 62.592l-9.408 1.408-192 192a32 32 0 0 1-45.248-45.248L786.752 128H832z"/>
                </svg>
              </button>
              <button 
                v-if="row.status === 0"
                type="button"
                class="table-action-btn table-action-btn-success"
                @click="handleEnablePermission(row)"
                :title="translate('permissionManagement.enable')"
              >
                <svg viewBox="0 0 1024 1024" width="14" height="14" fill="currentColor">
                  <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm193.5 301.7l-210.6 292a31.8 31.8 0 0 1-51.7 0L318.5 484.9c-3.8-5.3 0-12.7 6.5-12.7h46.9c10.2 0 19.9 4.9 25.9 13.3l71.2 98.8 157.2-218c6-8.3 15.6-13.3 25.9-13.3H699c6.5 0 10.3 7.4 6.5 12.7z"/>
                </svg>
              </button>
              <button 
                v-if="row.status === 1"
                type="button"
                class="table-action-btn table-action-btn-warning"
                @click="handleDisablePermission(row)"
                :title="translate('permissionManagement.disable')"
              >
                <svg viewBox="0 0 1024 1024" width="14" height="14" fill="currentColor">
                  <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z"/>
                  <path d="M686.7 638.6L512 464l-174.7 174.7c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L466.7 418.7c12.5-12.5 32.8-12.5 45.3 0L512 464l45.3-45.3c12.5-12.5 32.8-12.5 45.3 0l174.7 174.7c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0z"/>
                </svg>
              </button>
            </div>
          </template>
        </tiny-grid-column>
      </tiny-grid>
      <div v-if="permissions.length === 0 && !loading" class="empty-state">
        <p>{{ translate('permissionManagement.empty') }}</p>
      </div>
    </div>

    <!-- 创建权限弹窗 -->
    <tiny-dialog-box
      v-model:visible="showCreateModal"
      :title="translate('permissionManagement.create')"
      width="500px"
    >
      <tiny-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <tiny-form-item :label="translate('permissionManagement.name')" prop="name">
          <tiny-input
            v-model="createForm.name"
            :placeholder="translate('permissionManagement.namePlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('permissionManagement.code')" prop="code">
          <tiny-input
            v-model="createForm.code"
            :placeholder="translate('permissionManagement.codePlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('permissionManagement.category')" prop="category">
          <tiny-input
            v-model="createForm.category"
            :placeholder="translate('permissionManagement.categoryPlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('permissionManagement.description')" prop="description">
          <tiny-input
            v-model="createForm.description"
            type="textarea"
            :rows="4"
            :placeholder="translate('permissionManagement.descriptionPlaceholder')"
          />
        </tiny-form-item>
      </tiny-form>
      <template #footer>
        <tiny-button @click="handleCancelCreate">{{ translate('common.cancel') }}</tiny-button>
        <tiny-button type="primary" :loading="creating" @click="handleCreate">{{ translate('common.confirm') }}</tiny-button>
      </template>
    </tiny-dialog-box>

    <!-- 编辑权限弹窗 -->
    <tiny-dialog-box
      v-model:visible="showEditModal"
      :title="translate('permissionManagement.edit')"
      width="500px"
    >
      <tiny-form
        ref="editFormRef"
        :model="editForm"
        :rules="createRules"
        label-width="100px"
      >
        <tiny-form-item :label="translate('permissionManagement.name')" prop="name">
          <tiny-input
            v-model="editForm.name"
            :placeholder="translate('permissionManagement.namePlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('permissionManagement.code')" prop="code">
          <tiny-input
            v-model="editForm.code"
            :placeholder="translate('permissionManagement.codePlaceholder')"
            disabled
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('permissionManagement.category')" prop="category">
          <tiny-input
            v-model="editForm.category"
            :placeholder="translate('permissionManagement.categoryPlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('permissionManagement.description')" prop="description">
          <tiny-input
            v-model="editForm.description"
            type="textarea"
            :rows="4"
            :placeholder="translate('permissionManagement.descriptionPlaceholder')"
          />
        </tiny-form-item>
      </tiny-form>
      <template #footer>
        <tiny-button @click="showEditModal = false">{{ translate('common.cancel') }}</tiny-button>
        <tiny-button type="primary" :loading="updating" @click="handleUpdate">{{ translate('common.confirm') }}</tiny-button>
      </template>
    </tiny-dialog-box>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Button as TinyButton, DialogBox as TinyDialogBox, Form as TinyForm, FormItem as TinyFormItem, Input as TinyInput, Select as TinySelect, Option as TinyOption, Grid as TinyGrid, GridColumn as TinyGridColumn } from '@opentiny/vue'
import { t } from '../i18n'
import { Modal } from '@opentiny/vue'
import { useLocaleStore } from '../stores/locale'
import { systemPermissionApi, type SystemPermission } from '../api/systemPermission'

const localeStore = useLocaleStore()

// 响应式翻译函数
const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

// 数据
const loading = ref(false)
const permissions = ref<SystemPermission[]>([])
const categories = ref<string[]>([])
const searchKeyword = ref('')
const filterStatus = ref<number | null>(null)
const filterCategory = ref<string | null>(null)

// 创建表单
const showCreateModal = ref(false)
const creating = ref(false)
const createFormRef = ref()
const createForm = ref<{ name: string; code: string; category: string; description: string; sort_order?: number }>({
  name: '',
  code: '',
  category: '',
  description: ''
})

// 编辑表单
const showEditModal = ref(false)
const updating = ref(false)
const editFormRef = ref()
const editingPermissionId = ref<number | null>(null)
const editForm = ref({
  name: '',
  code: '',
  category: '',
  description: ''
})

// 表单校验规则
const createRules = {
  name: [{ required: true, message: () => translate('permissionManagement.nameRequired'), trigger: 'blur' }],
  code: [{ required: true, message: () => translate('permissionManagement.codeRequired'), trigger: 'blur' }]
}

// 格式化日期
const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 加载权限列表
const fetchPermissions = async () => {
  loading.value = true
  try {
    const response = await systemPermissionApi.getPermissions({
      keyword: searchKeyword.value || null,
      status: filterStatus.value,
      category: filterCategory.value,
      page: 1,
      page_size: 100
    })
    permissions.value = Array.isArray(response) ? response : response.items || []
  } catch (error) {
    console.error('加载权限列表失败:', error)
    Modal.message({ message: translate('permissionManagement.fetchError'), status: 'error' })
  } finally {
    loading.value = false
  }
}

// 加载分类列表
const fetchCategories = async () => {
  try {
    categories.value = await systemPermissionApi.getCategories()
  } catch (error) {
    console.error('加载分类列表失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  fetchPermissions()
}

// 创建权限
const handleCreate = async () => {
  if (!createFormRef.value) return
  
  await createFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    creating.value = true
    try {
      await systemPermissionApi.createPermission({
        name: createForm.value.name,
        code: createForm.value.code,
        category: createForm.value.category || null,
        description: createForm.value.description || null,
        status: 1
      })
      Modal.message({ message: translate('permissionManagement.createSuccess'), status: 'success' })
      resetCreateForm()
      showCreateModal.value = false
      await fetchPermissions()
      await fetchCategories() // 刷新分类列表
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || translate('permissionManagement.createError')
      Modal.message({ message: errorMessage, status: 'error' })
    } finally {
      creating.value = false
    }
  })
}

// 取消创建
const handleCancelCreate = () => {
  resetCreateForm()
  showCreateModal.value = false
}

// 重置创建表单
const resetCreateForm = () => {
  createForm.value = {
    name: '',
    code: '',
    category: '',
    description: '',
    sort_order: 0
  }
  createFormRef.value?.resetFields()
}

// 编辑权限
const handleEditPermission = (permission: SystemPermission) => {
  editingPermissionId.value = permission.id
  editForm.value = {
    name: permission.name,
    code: permission.code,
    category: permission.category || '',
    description: permission.description || ''
  }
  showEditModal.value = true
}

// 更新权限
const handleUpdate = async () => {
  if (!editFormRef.value || !editingPermissionId.value) return
  
  await editFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    updating.value = true
    try {
      const id = editingPermissionId.value
      if (id == null) return
      await systemPermissionApi.updatePermission(id, {
        name: editForm.value.name,
        category: editForm.value.category || null,
        description: editForm.value.description || null
      })
      Modal.message({ message: translate('permissionManagement.updateSuccess'), status: 'success' })
      showEditModal.value = false
      await fetchPermissions()
      await fetchCategories() // 刷新分类列表
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || translate('permissionManagement.updateError')
      Modal.message({ message: errorMessage, status: 'error' })
    } finally {
      updating.value = false
    }
  })
}

// 删除权限
const handleDeletePermission = (permission: SystemPermission) => {
  Modal.confirm({
    title: translate('permissionManagement.deleteConfirm'),
    message: translate('permissionManagement.deleteMessage', { name: permission.name }),
    status: 'warning'
  }).then(async (result: string) => {
    if (result !== 'confirm') return
    try {
      await systemPermissionApi.deletePermission(permission.id)
      Modal.message({ message: translate('permissionManagement.deleteSuccess'), status: 'success' })
      await fetchPermissions()
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || translate('permissionManagement.deleteError')
      Modal.message({ message: errorMessage, status: 'error' })
    }
  }).catch(() => {})
}

// 启用权限
const handleEnablePermission = (permission: SystemPermission) => {
  Modal.confirm({
    title: translate('permissionManagement.enableConfirm'),
    message: translate('permissionManagement.enableMessage', { name: permission.name }),
    status: 'info'
  }).then(async (result: string) => {
    if (result !== 'confirm') return
    try {
      await systemPermissionApi.enablePermission(permission.id)
      Modal.message({ message: translate('permissionManagement.enableSuccess'), status: 'success' })
      await fetchPermissions()
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || translate('permissionManagement.enableError')
      Modal.message({ message: errorMessage, status: 'error' })
    }
  }).catch(() => {})
}

// 禁用权限
const handleDisablePermission = (permission: SystemPermission) => {
  Modal.confirm({
    title: translate('permissionManagement.disableConfirm'),
    message: translate('permissionManagement.disableMessage', { name: permission.name }),
    status: 'warning'
  }).then(async (result: string) => {
    if (result !== 'confirm') return
    try {
      await systemPermissionApi.disablePermission(permission.id)
      Modal.message({ message: translate('permissionManagement.disableSuccess'), status: 'success' })
      await fetchPermissions()
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || translate('permissionManagement.disableError')
      Modal.message({ message: errorMessage, status: 'error' })
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchPermissions()
  fetchCategories()
})
</script>

<style scoped lang="less">
.permission-management-page {
  padding: 30px;
  background: #fff;
  min-height: calc(100vh - 64px);
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.content-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  align-items: center;
  flex-wrap: wrap;
}

.table-view {
  background: #fff;
  border-radius: 8px;
  overflow-x: auto;
  box-sizing: border-box;

  // 确保表格宽度铺满
  :deep(.tiny-grid) {
    width: 100% !important;
  }

  :deep(.tiny-grid__wrapper) {
    width: 100% !important;
  }

  // 表头样式
  :deep(.tiny-grid thead),
  :deep(.tiny-grid .tiny-grid-header) {
    display: table-header-group !important;
  }

  :deep(.tiny-grid th),
  :deep(.tiny-grid thead th),
  :deep(.tiny-grid .tiny-grid-header th),
  :deep(.tiny-grid .tiny-grid-header__column) {
    font-weight: 600 !important;
    font-size: 13px !important;
    color: #303133 !important;
    background: #fafafa !important;
    padding: 12px 10px !important;
    border-bottom: 1px solid #e4e7ed !important;
    display: table-cell !important;
    visibility: visible !important;
    opacity: 1 !important;
    text-align: left;
  }

  // 表体样式
  :deep(.tiny-grid tbody td),
  :deep(.tiny-grid .tiny-grid-body td) {
    padding: 10px !important;
    font-size: 13px !important;
    color: #606266 !important;
  }

  :deep(.tiny-grid tbody tr:hover td),
  :deep(.tiny-grid .tiny-grid-row:hover td) {
    background-color: #f5f7fa !important;
  }

  .permission-code-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    background: #f0f9ff;
    color: var(--primary-color, #8b5cf6);
  }

  .status-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    
    &.status-enabled {
      background: #f0f9ff;
      color: #1890ff;
    }
    
    &.status-disabled {
      background: #fff7e6;
      color: #fa8c16;
    }
  }

  .table-actions {
    display: flex;
    gap: 8px;
    flex-wrap: nowrap;
    justify-content: center;
    align-items: center;
  }

  .table-action-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    border-radius: 4px;
    cursor: pointer;
    color: #909399;
    transition: all 0.2s;
    padding: 0;
    vertical-align: middle;

    svg {
      display: block;
      width: 14px;
      height: 14px;
      fill: currentColor;
    }

    &:hover {
      background: #f5f7fa;
      color: var(--primary-color, #8b5cf6);
    }

    &.table-action-btn-danger:hover {
      background: #fef0f0;
      color: #f56c6c;
    }

    &.table-action-btn-success:hover {
      background: #f0f9ff;
      color: #52c41a;
    }

    &.table-action-btn-warning:hover {
      background: #fff7e6;
      color: #fa8c16;
    }
  }

  .empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #999;
  }
}
</style>
