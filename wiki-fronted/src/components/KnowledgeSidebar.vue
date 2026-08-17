<template>
  <aside
    class="sidebar"
    :class="{ 'sidebar--drawer-open': props.compact && props.drawerOpen }"
  >
    <div v-if="props.compact" class="sidebar-drawer-header">
      <span class="sidebar-drawer-title">{{ translate('nav.menuTitle') }}</span>
      <button
        type="button"
        class="sidebar-drawer-close"
        :aria-label="translate('nav.closeMenu')"
        @click="emit('navigate')"
      >
        <svg viewBox="0 0 1024 1024" width="18" height="18" fill="currentColor" aria-hidden="true">
          <path d="M563.8 512l262.5-312.9c4.4-5.2.7-13.1-6.1-13.1h-54.9c-4.7 0-9.2 2.1-12.3 5.7L511.6 449.8 295.1 191.7c-3.1-3.6-7.6-5.7-12.3-5.7H228c-6.8 0-10.5 7.9-6.1 13.1L459.4 512 196.9 824.9A7.95 7.95 0 0 0 203 838h54.8c4.7 0 9.2-2.1 12.3-5.7l216.5-258.1 216.5 258.1c3.1 3.6 7.6 5.7 12.3 5.7h54.8c6.8 0 10.5-7.9 6.1-13.1L563.8 512z"/>
        </svg>
      </button>
    </div>
    <tiny-tree
      ref="treeRef"
      :data="menuData"
      :props="treeProps"
      node-key="path"
      :highlight-current="true"
      :default-expanded-keys="defaultExpandedKeys"
      @node-click="handleNodeClick"
      class="sidebar-tree"
    >
    </tiny-tree>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { TinyTree } from '@opentiny/vue'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'
import { getCurrentRolePermissions } from '../utils/permission'

const props = withDefaults(
  defineProps<{
    compact?: boolean
    drawerOpen?: boolean
  }>(),
  {
    compact: false,
    drawerOpen: false
  }
)

const emit = defineEmits<{
  navigate: []
}>()

const router = useRouter()
const route = useRoute()
const localeStore = useLocaleStore()
const treeRef = ref()

interface MenuNode {
  path: string
  label: string
  /** 权限码，当前角色需拥有此权限才展示；无此字段表示所有人可见 */
  show?: string
  children?: MenuNode[]
}

// 响应式翻译函数
const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

// Tree 配置
const treeProps = {
  children: 'children',
  label: 'label'
}

// 当前角色权限字典 { code: true }
const permissionDict = ref<Record<string, boolean>>({})

// 原始菜单数据（含 show 权限字段）
const rawMenuData = computed<MenuNode[]>(() => [
  { path: '/', label: translate('nav.home') },
  {
    path: '/knowledge/space-management',
    label: translate('knowledge.spaceManagement'),
    children: [
      { path: '/knowledge/team-spaces', label: translate('knowledge.teamSpace'), show: 'team_space_port' },
      { path: '/knowledge/knowledge-spaces', label: translate('knowledge.knowledgeBase'), show: 'knowledge_space_port' }
    ]
  },
  // {
  //   path: '/knowledge/sign-reading-center-group',
  //   label: translate('knowledge.signReadingCenter'),
  //   children: [
  //     {
  //       path: '/knowledge/my-reading-tasks',

  //       label: translate('personalCenter.myReadingTasks')
  //     },
  //     {
  //       path: '/knowledge/sign-reading-management',
  //       show: 'read_manage',
  //       label: translate('signReadingManagement.title')
  //     }
  //   ]
  // },
  {
    path: '/knowledge/personal-center-group',
    label: translate('knowledge.personalCenter'),
    children: [
      {
        path: '/knowledge/personal-center',
        label: translate('personalCenter.title')
      },
      {
        path: '/knowledge/collections',
        label: translate('personalCenter.collections')
      },
      {
        path: '/knowledge/likes',
        label: translate('personalCenter.likes')
      },
      {
        path: '/knowledge/browse-history',
        label: translate('personalCenter.browseHistory')
      },
      {
        path: '/knowledge/daily-stats',
        label: translate('personalCenter.dailyStats')
      }
    ]
  },
  {
    path: '/knowledge/resource-approval-group',
    label: translate('knowledge.resourceApproval'),
    children: [
      {
        path: '/knowledge/my-applications',
        label: translate('applications.myApplications')
      },
      {
        path: '/knowledge/pending-review',
        label: translate('applications.pendingReview')
      }
    ]
  },
  {
    path: '/knowledge/feedback-group',
    label: translate('feedback.section'),
    children: [
      {
        path: '/knowledge/my-feedbacks',
        label: translate('feedback.myFeedbacks')
      },
      {
        path: '/knowledge/feedback-handling',
        show: 'feedback_handle',
        label: translate('feedback.handling')
      }
    ]
  },
  {
    path: '/knowledge/system-setting-group',
    label: translate('knowledge.systemSetting'),
    children: [
      { path: '/knowledge/user-management', label: translate('knowledge.userManagement'), show: 'user_manage_port' },
      { path: '/knowledge/role-management', label: translate('knowledge.roleManagement'), show: 'role_manage_port' },
      { path: '/knowledge/permission-management', label: translate('knowledge.permissionManagement'), show: 'permission_manage_port' },
      { path: '/knowledge/banner-management', label: translate('banner.management'), show: 'banner_manage_port' }
    ]
  }
])

// 根据 permissionDict 和 show 字段过滤菜单（无权限的节点及空分组隐藏）
const filterMenuByShow = (nodes: MenuNode[], dict: Record<string, boolean>): MenuNode[] => {
  return nodes
    .map((node) => {
      if (node.children && node.children.length > 0) {
        const filteredChildren = filterMenuByShow(node.children, dict)
        if (filteredChildren.length === 0) return null
        return { ...node, children: filteredChildren }
      }
      if (!node.show) return { ...node }
      return dict[node.show] ? { ...node } : null
    })
    .filter((n): n is MenuNode => n !== null)
}

// 过滤后的菜单数据（无权限项不展示）
const menuData = computed<MenuNode[]>(() => filterMenuByShow(rawMenuData.value, permissionDict.value))

// 默认展开的菜单项
const defaultExpandedKeys = ref<string[]>([])

// 节点点击处理
const handleNodeClick = (data: MenuNode) => {
  // 如果节点有子节点或者是分组节点（path 包含 -group），不进行跳转
  if (data.children && data.children.length > 0) {
    return
  }
  // 如果是分组节点路径（用于分组，不是实际路由），不跳转
  if (data.path && data.path.includes('-group')) {
    return
  }
  
  if (data.path && data.path !== route.path) {
    router.push(data.path)
    emit('navigate')
  }
}

// 加载当前角色权限并映射为字典
const loadPermissionDict = async () => {
  try {
    const codes = await getCurrentRolePermissions()
    permissionDict.value = codes.reduce<Record<string, boolean>>((acc, code) => {
      acc[code] = true
      return acc
    }, {})
  } catch (error) {
    console.error('加载角色权限失败:', error)
    permissionDict.value = {}
  }
}

// 根据当前路由设置高亮和展开状态（优化路径匹配）
const updateMenuState = () => {
  const currentPath = route.path
  
  // 设置当前高亮节点
  if (treeRef.value) {
    // 查找匹配的节点路径（支持路径前缀匹配）
    const findNodePath = (nodes: MenuNode[], targetPath: string): string | null => {
      for (const node of nodes) {
        // 跳过分组节点
        if (node.path && node.path.includes('-group')) {
          if (node.children) {
            const found = findNodePath(node.children, targetPath)
            if (found) {
              // 展开父节点
              if (!defaultExpandedKeys.value.includes(node.path)) {
                defaultExpandedKeys.value.push(node.path)
              }
              return found
            }
          }
          continue
        }
        
        // 精确匹配
        if (node.path === targetPath) {
          return node.path
        }
        
        // 路径前缀匹配（处理带参数的路由，如 /knowledge/knowledge-spaces/:teamSpaceId?）
        if (node.path && targetPath.startsWith(node.path + '/')) {
          // 检查是否是子路由
          const pathParts = targetPath.split('/')
          const nodePathParts = node.path.split('/')
          if (pathParts.length >= nodePathParts.length && 
              pathParts.slice(0, nodePathParts.length).join('/') === node.path) {
            return node.path
          }
        }
        
        if (node.children) {
          const found = findNodePath(node.children, targetPath)
          if (found) {
            // 展开父节点
            if (!defaultExpandedKeys.value.includes(node.path)) {
              defaultExpandedKeys.value.push(node.path)
            }
            return found
          }
        }
      }
      return null
    }
    
    const matchedPath = findNodePath(menuData.value, currentPath)
    if (matchedPath && treeRef.value.setCurrentKey) {
      nextTick(() => {
        treeRef.value.setCurrentKey(matchedPath)
      })
    }
  }
}

// 监听路由变化，更新菜单高亮
watch(() => route.path, () => {
  updateMenuState()
}, { immediate: true })

// 组件挂载后加载权限并初始化菜单状态
onMounted(async () => {
  await loadPermissionDict()
  updateMenuState()
  setTimeout(() => loadPermissionDict().then(updateMenuState), 500)
})
</script>

<style scoped lang="less">
.sidebar {
  width: 250px;
  background: #f5f7fa;
  padding: 20px 0;
  height: calc(100vh - 64px);
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  box-sizing: border-box;
}

.sidebar-drawer-header {
  display: none;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px 10px;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.sidebar-drawer-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.sidebar-drawer-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #666;
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;

  &:hover {
    background: rgba(139, 92, 246, 0.1);
    color: var(--primary-color, #8b5cf6);
  }
}

@media (max-width: 1024px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 410;
    width: min(280px, 88vw) !important;
    max-width: 88vw;
    height: 100%;
    min-height: 100vh;
    min-height: 100dvh;
    padding-top: 0;
    transform: translateX(-100%);
    transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.14);
    border-right: 1px solid #e4e7ed;

    &.sidebar--drawer-open {
      transform: translateX(0);
    }
  }

  .sidebar-drawer-header {
    display: flex;
  }

  .sidebar-tree {
    padding-top: 4px;
  }

  :deep(.tiny-tree-node__content) {
    min-height: 40px;
    padding: 10px 16px !important;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: min(300px, 92vw) !important;
  }
}

.sidebar-tree {
  flex: 1;
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  
  :deep(.tiny-tree) {
    font-size: 14px;
    height: 100%;
    overflow-y: auto;
    overflow-x: hidden;
  }
  
  :deep(.tiny-tree-node) {
    padding: 4px 0;
    
    .tiny-tree-node__content {
      padding: 8px 20px;
      min-height: 36px;
      border-radius: 4px;
      margin: 2px 12px;
      transition: all 0.3s;
      
      &:hover {
        background-color: #e4e7ed;
      }
      
      &.is-current {
        color: var(--primary-color, #8b5cf6);
        font-weight: 500;
      }
      
      .tiny-tree-node__content-left {
        background-color: transparent;
      }
    }
  }
  
  // 子节点样式
  :deep(.tiny-tree-node__children) {
    .tiny-tree-node__content {
      padding-left: 10px;
      color: #666;
      font-size: 13px;
      
      &.is-current {
        color: var(--primary-color, #8b5cf6);
      }
    }
  }
}

// 美化滚动条
.sidebar {
  // Firefox
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
  
  // Webkit (Chrome, Safari, Edge)
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 3px;
    transition: background 0.3s;
    
    &:hover {
      background: rgba(0, 0, 0, 0.3);
    }
  }
}

.sidebar-tree {
  // Firefox
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
  
  // Webkit
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 3px;
    transition: background 0.3s;
    
    &:hover {
      background: rgba(0, 0, 0, 0.3);
    }
  }
  
  :deep(.tiny-tree) {
    // Firefox
    scrollbar-width: thin;
    scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
    
    // Webkit
    &::-webkit-scrollbar {
      width: 6px;
    }
    
    &::-webkit-scrollbar-track {
      background: transparent;
      border-radius: 3px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: rgba(0, 0, 0, 0.2);
      border-radius: 3px;
      transition: background 0.3s;
      
      &:hover {
        background: rgba(0, 0, 0, 0.3);
      }
    }
  }
}
</style>
