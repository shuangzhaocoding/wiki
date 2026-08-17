<template>
  <div class="personal-center-page">
    <div class="content-header">
      <h1 class="content-title">{{ translate('personalCenter.title') }}</h1>
      <tiny-button 
        v-if="!isEditing" 
        type="primary" 
        @click="startEdit"
      >
        {{ translate('personalCenter.edit') }}
      </tiny-button>
      <div v-else class="edit-actions">
        <tiny-button @click="cancelEdit">
          {{ translate('common.cancel') }}
        </tiny-button>
        <tiny-button type="primary" @click="handleSave" :loading="saving">
          {{ translate('common.save') }}
        </tiny-button>
      </div>
    </div>

    <div class="profile-content" :class="{ 'loading-active': loading }">
      <div v-if="loading" class="loading-wrapper">
        <LoadingSpinner :absolute="false" />
      </div>
      <div v-if="!loading" class="profile-card">
        <!-- 头像和基本信息区域 -->
        <div class="profile-header">
          <div class="avatar-section">
            <img 
              :src="getAvatarUrl()" 
              :alt="userForm.username"
              class="avatar"
              @error="handleAvatarError"
            />
          </div>
          <div class="profile-info">
            <h2 class="profile-username">{{ userForm.username }}</h2>
            <div class="status-badge" :class="getStatusClass()">
              {{ getStatusText() }}
            </div>
          </div>
        </div>

        <tiny-form
          ref="formRef"
          :model="userForm"
          :rules="formRules"
          label-width="120px"
          :disabled="!isEditing"
        >
          <tiny-form-item :label="translate('personalCenter.username')" prop="username">
            <tiny-input
              v-model="userForm.username"
              :placeholder="translate('personalCenter.usernamePlaceholder')"
            />
          </tiny-form-item>

          <tiny-form-item :label="translate('personalCenter.email')" prop="email">
            <tiny-input
              v-model="userForm.email"
              :placeholder="translate('personalCenter.emailPlaceholder')"
              :disabled="true"
            />
            <span class="form-tip">{{ translate('personalCenter.emailTip') }}</span>
          </tiny-form-item>

          <tiny-form-item :label="translate('personalCenter.status')">
            <span class="readonly-field status-text" :class="getStatusClass()">
              {{ getStatusText() }}
            </span>
          </tiny-form-item>

          <tiny-form-item :label="translate('personalCenter.createdAt')">
            <span class="readonly-field">{{ formatDate(userForm.created_at) }}</span>
          </tiny-form-item>

          <tiny-form-item :label="translate('personalCenter.lastLoginAt')">
            <span class="readonly-field">{{ formatDate(userForm.last_login_at) }}</span>
          </tiny-form-item>
        </tiny-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Button as TinyButton, Form as TinyForm, FormItem as TinyFormItem, Input as TinyInput } from '@opentiny/vue'
import { authApi, type UserResponse } from '../api/auth'
import { useUserStore } from '../stores/user'
import { t } from '../i18n'
import { Modal } from '@opentiny/vue'
import { useLocaleStore } from '../stores/locale'
// @ts-ignore
import LoadingSpinner from '../components/LoadingSpinner.vue'
// @ts-ignore
import defaultAvatar from '../assets/default-avatar.svg'

const localeStore = useLocaleStore()
const userStore = useUserStore()

// 数据
const loading = ref(false)
const saving = ref(false)
const isEditing = ref(false)
const userInfo = ref<UserResponse | null>(null)
const formRef = ref()

// 表单数据
const userForm = ref({
  username: '',
  email: '',
  avatar: '',
  status: 1,
  created_at: '',
  last_login_at: ''
})

// 原始数据（用于取消编辑时恢复）
const originalData = ref({
  username: '',
  email: '',
  avatar: '',
  status: 1,
  created_at: '',
  last_login_at: ''
})

// 头像加载错误处理
const avatarError = ref(false)

// 表单验证规则
const formRules = {
  username: [
    { required: true, message: () => translate('personalCenter.usernameRequired'), trigger: 'blur' }
  ]
}

// 响应式翻译函数
const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

// 获取头像URL
const getAvatarUrl = () => {
  if (avatarError.value || !userForm.value.avatar) {
    return defaultAvatar
  }
  return userForm.value.avatar
}

// 处理头像加载错误
const handleAvatarError = () => {
  avatarError.value = true
}

// 获取状态文本
const getStatusText = () => {
  return userForm.value.status === 1 
    ? translate('personalCenter.status.normal')
    : translate('personalCenter.status.banned')
}

// 获取状态样式类
const getStatusClass = () => {
  return userForm.value.status === 1 ? 'status-normal' : 'status-banned'
}

// 格式化日期
const formatDate = (dateStr?: string) => {
  if (!dateStr) return translate('personalCenter.notSet')
  try {
    const date = new Date(dateStr)
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
  } catch {
    return dateStr
  }
}

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    loading.value = true
    avatarError.value = false
    const user = await authApi.getCurrentUser()
    userInfo.value = user
    userForm.value = {
      username: user.username || '',
      email: user.email || '',
      avatar: user.avatar || '',
      status: user.status ?? 1,
      created_at: user.created_at || '',
      last_login_at: user.last_login_at || ''
    }
    originalData.value = { ...userForm.value }
  } catch (error: any) {
    Modal.message({
      message: error.message || translate('personalCenter.fetchError'),
      status: 'error'
    })
  } finally {
    loading.value = false
  }
}

// 开始编辑
const startEdit = () => {
  isEditing.value = true
}

// 取消编辑
const cancelEdit = () => {
  userForm.value = { ...originalData.value }
  isEditing.value = false
  formRef.value?.clearValidate()
}

// 保存修改
const handleSave = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        saving.value = true
        await authApi.updateUser({
          username: userForm.value.username || undefined
        })
        Modal.message({
          message: translate('personalCenter.updateSuccess'),
          status: 'success'
        })
        originalData.value = { ...userForm.value }
        isEditing.value = false
        await fetchUserInfo() // 重新获取最新数据
        // 同步更新到 store
        if (userInfo.value) {
          userStore.updateUser(userInfo.value)
        }
      } catch (error: any) {
        Modal.message({
          message: error.message || translate('personalCenter.updateError'),
          status: 'error'
        })
      } finally {
        saving.value = false
      }
    }
  })
}

// 初始化
onMounted(() => {
  fetchUserInfo()
})
</script>

<style scoped lang="less">
.personal-center-page {
  width: 100%;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.content-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.edit-actions {
  display: flex;
  gap: 10px;
}

.profile-content {
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

.profile-card {
  background: #fff;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding-bottom: 30px;
  margin-bottom: 30px;
  border-bottom: 1px solid #e4e7ed;
}

.avatar-section {
  flex-shrink: 0;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #e4e7ed;
  background: #f5f7fa;
}

.profile-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.profile-username {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  
  &.status-normal {
    background-color: #f0f9ff;
    color: #409eff;
  }
  
  &.status-banned {
    background-color: #fef0f0;
    color: #f56c6c;
  }
}

.form-tip {
  display: block;
  margin-top: 5px;
  font-size: 12px;
  color: #999;
}

.readonly-field {
  color: #666;
  font-size: 14px;
  
  &.status-text {
    font-weight: 500;
    
    &.status-normal {
      color: #409eff;
    }
    
    &.status-banned {
      color: #f56c6c;
    }
  }
}

@media (max-width: 768px) {
  .content-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .profile-card {
    padding: 20px;
  }
}
</style>
