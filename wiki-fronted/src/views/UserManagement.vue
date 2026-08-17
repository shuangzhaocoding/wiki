<template>
  <div class="user-management-page">
    <div class="content-header">
      <h1 class="content-title">{{ translate('knowledge.userManagement') }}</h1>
      <tiny-button type="primary" @click="showCreateModal = true">
        {{ translate('userManagement.create') }}
      </tiny-button>
    </div>

    <!-- 用户列表表格 -->
    <div class="table-view">
      <tiny-grid
        :data="users"
        :loading="loading"
        border
        highlight-hover-row
        width="100%"
        class="user-grid"
        show-header
      >
        <tiny-grid-column 
          field="username" 
          :title="translate('userManagement.username')" 
          :label="translate('userManagement.username')" 
          min-width="150" 
          align="left"
        />
        <tiny-grid-column 
          field="email" 
          :title="translate('userManagement.email')" 
          :label="translate('userManagement.email')" 
          min-width="200" 
          align="left"
        />
        <tiny-grid-column 
          field="status" 
          :title="translate('userManagement.status')" 
          :label="translate('userManagement.status')" 
          width="100" 
          align="center"
        >
          <template #default="{ row }">
            <span class="status-badge" :class="getStatusClass(row.status)">
              {{ getStatusText(row.status) }}
            </span>
          </template>
        </tiny-grid-column>
        <tiny-grid-column 
          field="created_at" 
          :title="translate('userManagement.createdAt')" 
          :label="translate('userManagement.createdAt')" 
          width="160" 
          align="center"
        >
          <template #default="{ row }">
            {{ formatDate(row.created_at) || '—' }}
          </template>
        </tiny-grid-column>
        <tiny-grid-column 
          field="actions" 
          :title="translate('userManagement.actions')" 
          :label="translate('userManagement.actions')" 
          width="200" 
          align="center"
          fixed="right"
        >
          <template #default="{ row }">
            <div class="table-actions" @click.stop>
              <button 
                type="button"
                class="table-action-btn table-action-btn-role"
                @click="handleManageRoles(row)"
                :title="translate('userManagement.manageRoles')"
              >
                <svg viewBox="0 0 1024 1024" width="14" height="14" fill="currentColor">
                  <path d="M512 64L128 192v320c0 212.064 175.936 384 384 384s384-171.936 384-384V192L512 64zm0 64v576c-164.672 0-320-131.328-320-320V256l320-128z"/>
                </svg>
              </button>
              <!-- 根据启用状态显示：禁用时显示启用按钮，启用时显示禁用按钮 -->
              <button 
                v-if="row.status === 0"
                type="button"
                class="table-action-btn table-action-btn-success"
                @click="handleEnableUser(row)"
                :title="translate('userManagement.enable')"
              >
                <svg viewBox="0 0 1024 1024" width="14" height="14" fill="currentColor">
                  <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm193.5 301.7l-210.6 292a31.8 31.8 0 0 1-51.7 0L318.5 484.9c-3.8-5.3 0-12.7 6.5-12.7h46.9c10.2 0 19.9 4.9 25.9 13.3l71.2 98.8 157.2-218c6-8.3 15.6-13.3 25.9-13.3H699c6.5 0 10.3 7.4 6.5 12.7z"/>
                </svg>
              </button>
              <button 
                v-else-if="row.status === 1"
                type="button"
                class="table-action-btn table-action-btn-warning"
                @click="handleDisableUser(row)"
                :title="translate('userManagement.disable')"
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
      <div v-if="users.length === 0 && !loading" class="empty-state">
        <p>{{ translate('userManagement.empty') }}</p>
      </div>
    </div>

    <!-- 创建用户弹窗 -->
    <tiny-dialog-box
      v-model:visible="showCreateModal"
      :title="translate('userManagement.create')"
      width="500px"
    >
      <tiny-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <tiny-form-item :label="translate('userManagement.username')" prop="username">
          <tiny-input
            v-model="createForm.username"
            :placeholder="translate('userManagement.usernamePlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('userManagement.email')" prop="email">
          <tiny-input
            v-model="createForm.email"
            :placeholder="translate('userManagement.emailPlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('userManagement.password')" prop="password">
          <tiny-input
            v-model="createForm.password"
            type="password"
            :placeholder="translate('userManagement.passwordPlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('userManagement.roles')" prop="roleIds">
          <tiny-select
            v-model="createForm.roleIds"
            multiple
            filterable
            :placeholder="translate('userManagement.rolesPlaceholder')"
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
        <tiny-button @click="handleCancelCreate">{{ translate('common.cancel') }}</tiny-button>
        <tiny-button type="primary" :loading="creating" @click="handleCreate">{{ translate('common.confirm') }}</tiny-button>
      </template>
    </tiny-dialog-box>

    <!-- 编辑用户弹窗 -->
    <tiny-dialog-box
      v-model:visible="showEditModal"
      :title="translate('userManagement.edit')"
      width="500px"
    >
      <tiny-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="100px"
      >
        <tiny-form-item :label="translate('userManagement.username')" prop="username">
          <tiny-input
            v-model="editForm.username"
            :placeholder="translate('userManagement.usernamePlaceholder')"
            disabled
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('userManagement.email')" prop="email">
          <tiny-input
            v-model="editForm.email"
            :placeholder="translate('userManagement.emailPlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('userManagement.status')" prop="status">
          <tiny-select v-model="editForm.status" :placeholder="translate('userManagement.statusPlaceholder')">
            <tiny-option :label="translate('userManagement.status.normal')" :value="1" />
            <tiny-option :label="translate('userManagement.status.banned')" :value="0" />
          </tiny-select>
        </tiny-form-item>
      </tiny-form>
      <template #footer>
        <tiny-button @click="showEditModal = false">{{ translate('common.cancel') }}</tiny-button>
        <tiny-button type="primary" :loading="updating" @click="handleUpdate">{{ translate('common.confirm') }}</tiny-button>
      </template>
    </tiny-dialog-box>

    <!-- 角色管理弹窗 -->
    <tiny-dialog-box
      v-model:visible="showRoleModal"
      :title="translate('userManagement.roleManagement')"
      width="80%"
    >
      <div class="role-modal-content">
        <div class="role-search-bar">
          <tiny-input
            v-model="roleSearchKeyword"
            :placeholder="translate('userManagement.roleSearchPlaceholder')"
            clearable
            style="width: 300px;"
          >
            <template #prefix>
              <svg viewBox="0 0 1024 1024" width="16" height="16" fill="currentColor">
                <path d="M469.333 128c-188.586 0-341.333 152.747-341.333 341.333 0 188.587 152.747 341.333 341.333 341.333 72.533 0 139.52-22.613 194.56-61.227l165.547 165.546c16.64 16.64 43.52 16.64 60.16 0 16.64-16.64 16.64-43.52 0-60.16L723.627 750.08c38.613-55.04 61.226-122.027 61.226-194.56 0-188.587-152.747-341.333-341.333-341.333z m0 85.333c141.227 0 256 114.774 256 256s-114.773 256-256 256-256-114.774-256-256 114.773-256 256-256z"/>
              </svg>
            </template>
          </tiny-input>
        </div>
        <tiny-grid
          :data="filteredRoles"
          :loading="roleLoading"
          border
          highlight-hover-row
          width="100%"
          height="400px"
          class="role-grid"
          show-header
        >
          <tiny-grid-column 
            field="name" 
            :title="translate('roleManagement.name')" 
            :label="translate('roleManagement.name')" 
            min-width="150" 
            align="left"
          />
          <tiny-grid-column 
            field="code" 
            :title="translate('roleManagement.code')" 
            :label="translate('roleManagement.code')" 
            min-width="150" 
            align="left"
          >
            <template #default="{ row }">
              <span class="role-code-badge">{{ row.code }}</span>
            </template>
          </tiny-grid-column>
          <tiny-grid-column 
            field="description" 
            :title="translate('roleManagement.description')" 
            :label="translate('roleManagement.description')" 
            min-width="200" 
            show-overflow="tooltip" 
            align="left"
          >
            <template #default="{ row }">
              <span>{{ row.description || '—' }}</span>
            </template>
          </tiny-grid-column>
          <tiny-grid-column 
            :title="translate('userManagement.roleStatus')" 
            :label="translate('userManagement.roleStatus')" 
            width="100" 
            align="center"
          >
            <template #default="{ row }">
              <span :class="isRoleAssigned(row.id) ? 'role-status-enabled' : 'role-status-disabled'">
                {{ isRoleAssigned(row.id) ? translate('userManagement.roleEnabled') : translate('userManagement.roleDisabled') }}
              </span>
            </template>
          </tiny-grid-column>
          <tiny-grid-column 
            :title="translate('userManagement.actions')" 
            :label="translate('userManagement.actions')" 
            width="150" 
            align="center"
            fixed="right"
          >
            <template #default="{ row }">
              <div class="role-actions" @click.stop>
                <tiny-button 
                  v-if="!isRoleAssigned(row.id)"
                  size="small"
                  type="primary"
                  @click="handleEnableRole(row)"
                >
                  {{ translate('userManagement.assignRole') }}
                </tiny-button>
                <tiny-button 
                  v-else
                  size="small"
                  type="warning"
                  @click="handleDisableRole(row)"
                >
                  {{ translate('userManagement.unassignRole') }}
                </tiny-button>
              </div>
            </template>
          </tiny-grid-column>
        </tiny-grid>
      </div>
      <template #footer>
        <tiny-button @click="showRoleModal = false">{{ translate('common.cancel') }}</tiny-button>
      </template>
    </tiny-dialog-box>
  </div>
</template>

<script setup lang="ts">
// 检查角色是否已分配（确保类型匹配）
const isRoleAssigned = (roleId: number): boolean => {
  return selectedRoleIds.value.some(id => Number(id) === Number(roleId))
}
import { ref, onMounted, computed, watch } from 'vue'
import { Button as TinyButton, DialogBox as TinyDialogBox, Form as TinyForm, FormItem as TinyFormItem, Input as TinyInput, Select as TinySelect, Option as TinyOption, Grid as TinyGrid, GridColumn as TinyGridColumn } from '@opentiny/vue'
import { t } from '../i18n'
import { Modal } from '@opentiny/vue'
import { useLocaleStore } from '../stores/locale'
import { userManagementApi, type User, type RoleInfo } from '../api/userManagement'
import { roleApi, type Role } from '../api/role'

const localeStore = useLocaleStore()

// 响应式翻译函数
const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

// 角色管理相关
const showRoleModal = ref(false)
const roleLoading = ref(false)
const allRoles = ref<Role[]>([])
const selectedRoleIds = ref<number[]>([])
const currentUserId = ref<number | null>(null)
const roleSearchKeyword = ref('')

// 数据
const loading = ref(false)
const users = ref<User[]>([])

// 创建表单
const showCreateModal = ref(false)
const creating = ref(false)
const createFormRef = ref()
const createForm = ref({
  username: '',
  email: '',
  password: '',
  roleIds: [] as number[]
})

// 编辑表单
const showEditModal = ref(false)
const updating = ref(false)
const editFormRef = ref()
const editingUserId = ref<number | null>(null)
const editForm = ref({
  username: '',
  email: '',
  status: 1
})

// 表单校验规则
const createRules = {
  username: [{ required: true, message: () => translate('userManagement.usernameRequired'), trigger: 'blur' }],
  email: [
    { required: true, message: () => translate('userManagement.emailRequired'), trigger: 'blur' },
    { type: 'email', message: () => translate('userManagement.emailInvalid'), trigger: 'blur' }
  ],
  password: [{ required: true, message: () => translate('userManagement.passwordRequired'), trigger: 'blur' }]
}

const editRules = {
  email: [
    { required: true, message: () => translate('userManagement.emailRequired'), trigger: 'blur' },
    { type: 'email', message: () => translate('userManagement.emailInvalid'), trigger: 'blur' }
  ],
  status: [{ required: true, message: () => translate('userManagement.statusRequired'), trigger: 'change' }]
}

// 获取状态文本和样式
const getStatusText = (status: number) => {
  return status === 1 ? translate('userManagement.status.normal') : translate('userManagement.status.banned')
}

const getStatusClass = (status: number) => {
  return status === 1 ? 'status-normal' : 'status-banned'
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

// 过滤后的角色列表
const filteredRoles = computed(() => {
  if (!roleSearchKeyword.value) {
    return allRoles.value
  }
  const keyword = roleSearchKeyword.value.toLowerCase()
  return allRoles.value.filter(role => 
    role.name.toLowerCase().includes(keyword) || 
    role.code.toLowerCase().includes(keyword)
  )
})

// 加载用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await userManagementApi.getUsers()
    users.value = response.items
  } catch (error) {
    console.error('加载用户列表失败:', error)
    Modal.message({ message: translate('userManagement.fetchError'), status: 'error' })
  } finally {
    loading.value = false
  }
}

// 加载所有角色
const fetchAllRoles = async () => {
  roleLoading.value = true
  try {
    const response = await roleApi.getRoles({
      page: 1,
      page_size: 100,
      status: 1 // 只获取启用的角色
    })
    allRoles.value = response.items
  } catch (error) {
    console.error('加载角色列表失败:', error)
    Modal.message({ message: translate('userManagement.fetchRolesError'), status: 'error' })
  } finally {
    roleLoading.value = false
  }
}

// 打开创建弹窗时加载角色列表
watch(showCreateModal, (visible) => {
  if (visible) {
    fetchAllRoles()
  }
})

// 加载用户角色
const fetchUserRoles = async (userId: number) => {
  try {
    const roles = await userManagementApi.getUserRoles(userId)
    // 确保正确提取角色ID，兼容不同的数据结构
    selectedRoleIds.value = roles.map((role: RoleInfo) => {
      // 如果 role 是数字，直接返回
      if (typeof role === 'number') {
        return role
      }
      // 如果 role 是对象，提取 id 字段
      if (role && typeof role === 'object' && 'id' in role) {
        return Number(role.id)
      }
      return null
    }).filter((id: number | null): id is number => id !== null && id !== undefined)
  } catch (error) {
    console.error('加载用户角色失败:', error)
    Modal.message({ message: translate('userManagement.fetchUserRolesError'), status: 'error' })
    selectedRoleIds.value = []
  }
}

// 管理角色
const handleManageRoles = async (user: User) => {
  currentUserId.value = user.id
  roleSearchKeyword.value = ''
  selectedRoleIds.value = []
  showRoleModal.value = true
  
  // 先加载所有角色
  await fetchAllRoles()
  // 然后加载用户角色
  await fetchUserRoles(user.id)
}

// 启用角色（给用户添加此角色）
const handleEnableRole = async (role: Role) => {
  if (!currentUserId.value) return
  
  try {
    // 调用 API 添加单个角色
    await userManagementApi.addUserRole(currentUserId.value, role.id)
    
    // 添加到选中列表
    if (!selectedRoleIds.value.includes(role.id)) {
      selectedRoleIds.value.push(role.id)
    }
    
    // 重新获取用户角色列表以确保状态正确
    await fetchUserRoles(currentUserId.value)
    
    Modal.message({ message: translate('userManagement.enableRoleSuccess'), status: 'success' })
  } catch (error: any) {
    const errorMessage = error?.response?.data?.detail || error?.message || translate('userManagement.enableRoleError')
    Modal.message({ message: errorMessage, status: 'error' })
    // 如果失败，重新获取用户角色列表以恢复正确状态
    if (currentUserId.value) {
      await fetchUserRoles(currentUserId.value)
    }
  }
}

// 禁用角色（给用户取消此角色）
const handleDisableRole = async (role: Role) => {
  if (!currentUserId.value) return
  
  try {
    // 调用 API 移除单个角色
    await userManagementApi.removeUserRole(currentUserId.value, role.id)
    
    // 从选中列表移除
    const index = selectedRoleIds.value.indexOf(role.id)
    if (index > -1) {
      selectedRoleIds.value.splice(index, 1)
    }
    
    // 重新获取用户角色列表以确保状态正确
    await fetchUserRoles(currentUserId.value)
    
    Modal.message({ message: translate('userManagement.disableRoleSuccess'), status: 'success' })
  } catch (error: any) {
    const errorMessage = error?.response?.data?.detail || error?.message || translate('userManagement.disableRoleError')
    Modal.message({ message: errorMessage, status: 'error' })
    // 如果失败，重新获取用户角色列表以恢复正确状态
    if (currentUserId.value) {
      await fetchUserRoles(currentUserId.value)
    }
  }
}

// 创建用户
const handleCreate = async () => {
  if (!createFormRef.value) return
  
  await createFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    creating.value = true
    try {
      const payload = {
        username: createForm.value.username,
        email: createForm.value.email,
        password: createForm.value.password,
        role_ids: createForm.value.roleIds || []
      }
      await userManagementApi.createUser(payload)
      Modal.message({ message: translate('userManagement.createSuccess'), status: 'success' })
      resetCreateForm()
      showCreateModal.value = false
      await fetchUsers()
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || translate('userManagement.createError')
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
    username: '',
    email: '',
    password: '',
    roleIds: []
  }
  createFormRef.value?.resetFields()
}

// 编辑用户
const originalStatus = ref<number | null>(null)

const handleEditUser = (user: User) => {
  editingUserId.value = user.id
  originalStatus.value = user.status
  editForm.value = {
    username: user.username,
    email: user.email,
    status: user.status
  }
  showEditModal.value = true
}

// 更新用户
const handleUpdate = async () => {
  if (!editFormRef.value || !editingUserId.value) return
  
  await editFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    updating.value = true
    try {
      let hasStatusChange = false
      
      // 如果状态发生变化，使用 enableUser 或 disableUser 接口
      if (originalStatus.value !== null && editForm.value.status !== originalStatus.value) {
        hasStatusChange = true
        const uid = editingUserId.value
        if (uid == null) return
        if (editForm.value.status === 1) {
          // 从禁用变为启用
          await userManagementApi.enableUser(uid)
        } else if (editForm.value.status === 0) {
          // 从启用变为禁用
          await userManagementApi.disableUser(uid)
        }
      }
      
      // 检查邮箱是否有变化
      const currentUser = users.value.find(u => u.id === editingUserId.value)
      const emailChanged = currentUser && currentUser.email !== editForm.value.email
      
      // 如果邮箱有变化，尝试更新（如果后端支持）
      if (emailChanged) {
        const uid = editingUserId.value
        if (uid == null) return
        try {
          await userManagementApi.updateUser(uid, {
            email: editForm.value.email || null
          })
        } catch (updateError: any) {
          // 如果更新用户信息接口不存在（405 Method Not Allowed），只更新状态即可
          if (updateError?.response?.status === 405) {
            console.warn('更新用户信息接口不支持，仅更新状态')
            if (!hasStatusChange) {
              Modal.message({ 
                message: translate('userManagement.updateEmailNotSupported'), 
                status: 'warning' 
              })
              return
            }
          } else {
            throw updateError
          }
        }
      }
      
      // 如果既没有状态变化也没有邮箱变化，提示用户
      if (!hasStatusChange && !emailChanged) {
        Modal.message({ message: translate('userManagement.noChanges'), status: 'info' })
        showEditModal.value = false
        return
      }
      
      Modal.message({ message: translate('userManagement.updateSuccess'), status: 'success' })
      showEditModal.value = false
      await fetchUsers()
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || translate('userManagement.updateError')
      Modal.message({ message: errorMessage, status: 'error' })
    } finally {
      updating.value = false
    }
  })
}

// 启用用户
const handleEnableUser = (user: User) => {
  Modal.confirm({
    title: translate('userManagement.enableConfirm'),
    message: translate('userManagement.enableMessage', { username: user.username }),
    status: 'info'
  }).then(async (result: string) => {
    if (result !== 'confirm') return
    try {
      await userManagementApi.enableUser(user.id)
      Modal.message({ message: translate('userManagement.enableSuccess'), status: 'success' })
      await fetchUsers()
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || translate('userManagement.enableError')
      Modal.message({ message: errorMessage, status: 'error' })
    }
  }).catch(() => {})
}

// 禁用用户
const handleDisableUser = (user: User) => {
  Modal.confirm({
    title: translate('userManagement.disableConfirm'),
    message: translate('userManagement.disableMessage', { username: user.username }),
    status: 'warning'
  }).then(async (result: string) => {
    if (result !== 'confirm') return
    try {
      await userManagementApi.disableUser(user.id)
      Modal.message({ message: translate('userManagement.disableSuccess'), status: 'success' })
      await fetchUsers()
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || translate('userManagement.disableError')
      Modal.message({ message: errorMessage, status: 'error' })
    }
  }).catch(() => {})
}

// 删除用户
const handleDeleteUser = (user: User) => {
  Modal.confirm({
    title: translate('userManagement.deleteConfirm'),
    message: translate('userManagement.deleteMessage', { username: user.username }),
    status: 'warning'
  }).then(async (result: string) => {
    if (result !== 'confirm') return
    try {
      await userManagementApi.deleteUser(user.id)
      Modal.message({ message: translate('userManagement.deleteSuccess'), status: 'success' })
      await fetchUsers()
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || translate('userManagement.deleteError')
      Modal.message({ message: errorMessage, status: 'error' })
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped lang="less">
.user-management-page {
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

.table-view {
  .user-grid {
    :deep(.tiny-grid) {
      width: 100% !important;
    }

    :deep(.tiny-grid__wrapper) {
      width: 100% !important;
    }
  }

  .empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #999;
  }

  .status-badge {
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;

    &.status-normal {
      background: #f0f9ff;
      color: #67c23a;
    }

    &.status-banned {
      background: #fef0f0;
      color: #f56c6c;
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

    &.table-action-btn-role:hover {
      background: #f0f9ff;
      color: var(--primary-color, #8b5cf6);
    }

    &.table-action-btn-success:hover {
      background: #f0f9ff;
      color: #52c41a;
    }

    &.table-action-btn-warning:hover {
      background: #fffbe6;
      color: #faad14;
    }
  }
}

.role-modal-content {
  .role-search-bar {
    margin-bottom: 16px;
  }

  .role-status-enabled {
    color: #52c41a;
    font-weight: 500;
  }

  .role-status-disabled {
    color: #909399;
  }

  .role-actions {
    display: flex;
    gap: 8px;
    justify-content: center;
    align-items: center;
  }

  .role-grid {
    :deep(.tiny-grid) {
      width: 100% !important;
    }

    :deep(.tiny-grid__wrapper) {
      width: 100% !important;
    }

    .role-code-badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 500;
      background: #f0f9ff;
      color: var(--primary-color, #8b5cf6);
    }
  }
}
</style>
