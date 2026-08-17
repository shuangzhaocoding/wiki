import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, type UserResponse } from '../api/auth'
import { userManagementApi, type RoleInfo } from '../api/userManagement'

export const useUserStore = defineStore('user', () => {
  // 当前用户信息
  const currentUser = ref<UserResponse | null>(null)
  
  // 是否正在加载用户信息
  const loading = ref(false)
  
  // 当前用户ID（转换为 number，用于比较）
  const currentUserId = computed(() => {
    if (!currentUser.value) return null
    const userId = currentUser.value.id
    if (typeof userId === 'string') {
      return parseInt(userId, 10) || null
    }
    return userId || null
  })
  
  // 当前用户头像
  const currentUserAvatar = computed(() => {
    return currentUser.value?.avatar || ''
  })
  
  // 当前用户名
  const currentUsername = computed(() => {
    return currentUser.value?.username || ''
  })

  // 当前用户角色
  const currentUserRoles = ref<RoleInfo[]>([])
  
  // 获取用户信息
  const fetchCurrentUser = async () => {
    
    try {
      loading.value = true
      currentUser.value = await authApi.getCurrentUser()
      currentUserRoles.value = await userManagementApi.getUserRoles(currentUser.value.id)
    } catch (error) {
      console.error('获取用户信息失败:', error)
      currentUser.value = null
    } finally {
      loading.value = false
    }
  }
  
  // 更新用户信息（用于个人中心更新后同步）
  const updateUser = (user: UserResponse) => {
    currentUser.value = user
  }
  
  // 清除用户信息（用于登出）
  const clearUser = () => {
    currentUser.value = null
  }
  
  // 判断是否是评论作者
  const isCommentOwner = (commentUserId: number | undefined | null): boolean => {
    if (!currentUserId.value || commentUserId === undefined || commentUserId === null) {
      return false
    }
    // 确保类型一致进行比较（都转换为 number）
    const currentId = Number(currentUserId.value)
    const commentId = Number(commentUserId)
    return !isNaN(currentId) && !isNaN(commentId) && currentId === commentId
  }
  
  return {
    currentUser,
    loading,
    currentUserId,
    currentUserAvatar,
    currentUsername,
    fetchCurrentUser,
    updateUser,
    clearUser,
    isCommentOwner,
    currentUserRoles,
  }
})