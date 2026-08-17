import { type RoleInfo } from '../api/userManagement'
import { useUserStore } from '../stores/user'

// 全局角色缓存（供 setRolesCache/clearRolesCache 使用，预留扩展）
let _cachedRoles: RoleInfo[] = []
let _cachedUserId: number | null = null

/**
 * 设置用户角色缓存（由 AppHeader 或其他组件在加载角色时调用）
 */
export function setRolesCache(roles: RoleInfo[], userId: number) {
  _cachedRoles = roles
  _cachedUserId = userId
}

/**
 * 清除角色缓存（登出时调用）
 */
export function clearRolesCache() {
  _cachedRoles = []
  _cachedUserId = null
}

/**
 * 获取当前角色的权限列表（使用缓存，不请求接口）
 */
export async function getCurrentRolePermissions(): Promise<string[]> {
  try {
    // 获取当前用户ID
    const userStore = useUserStore()
    let roles = userStore.currentUserRoles
    
    // 获取当前角色ID
    const currentRoleId = localStorage.getItem('current_role_id')
    if (!currentRoleId) {
      console.warn('无法获取当前角色ID')
      return []
    }
    
    const roleId = parseInt(currentRoleId, 10)
    if (isNaN(roleId)) {
      console.warn('当前角色ID无效:', currentRoleId)
      return []
    }
    console.log('roles', roles)
    // 从缓存中找到当前角色
    const currentRole = roles.find(role => role.id === roleId)
    if (!currentRole) {
      console.warn('无法找到当前角色:', roleId)
      return []
    }
    
    return currentRole.permissions?.map(perm => perm.code).filter(Boolean) ?? []
  } catch (error) {
    console.error('获取当前角色权限失败:', error)
    return []
  }
}

/**
 * 检查当前角色是否拥有指定权限（同步版本，使用缓存）
 * @param requiredPermissions 需要的权限code列表（可以是字符串或字符串数组）
 * @returns 是否拥有权限
 */
export async function hasPermission(requiredPermissions: string | string[]): Promise<boolean>{
  
  const permissions = await getCurrentRolePermissions()
  return permissions.some(perm => requiredPermissions.includes(perm))
}
