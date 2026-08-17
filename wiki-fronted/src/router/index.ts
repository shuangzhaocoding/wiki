import { createRouter, createWebHistory } from 'vue-router'
import { authUtils } from '../utils/auth'
import { hasPermission } from '../utils/permission'
import { useUserStore } from '../stores/user'
import { doneTopProgress, startTopProgress } from '../utils/topProgress'
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
      meta: {
        title: '登录',
        requiresAuth: false
      }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/Register.vue'),
      meta: {
        title: '注册',
        requiresAuth: false
      }
    },
    {
      path: '/forgot-password',
      name: 'ForgotPassword',
      component: () => import('../views/ForgotPassword.vue'),
      meta: {
        title: '忘记密码',
        requiresAuth: false
      }
    },
    {
      path: '/',
      name: 'Home',
      component: () => import('../views/Home.vue'),
      meta: {
        title: '首页',
        requiresAuth: true
      }
    },
    {
      path: '/notifications',
      name: 'Notifications',
      component: () => import('../views/Notifications.vue'),
      meta: {
        title: '消息通知',
        requiresAuth: true
      }
    },
    {
      path: '/knowledge',
      component: () => import('../views/KnowledgeLayout.vue'),
      meta: {
        requiresAuth: true
      },
      children: [
        {
          path: 'user-management',
          name: 'UserManagement',
          component: () => import('../views/UserManagement.vue'),
          meta: {
            title: '用户管理',
            requiresAuth: true,
            requiredPermissions: 'user_manage_port'
          }
        },
        {
          path: 'role-management',
          name: 'RoleManagement',
          component: () => import('../views/RoleManagement.vue'),
          meta: {
            title: '角色管理',
            requiresAuth: true,
            requiredPermissions: 'role_manage_port'
          }
        },
        {
          path: 'permission-management',
          name: 'PermissionManagement',
          component: () => import('../views/PermissionManagement.vue'),
          meta: {
            title: '权限管理',
            requiresAuth: true,
            requiredPermissions: 'permission_manage_port'
          }
        },
        {
          path: 'banner-management',
          name: 'BannerManagement',
          component: () => import('../views/BannerManagement.vue'),
          meta: {
            title: 'Banner 管理',
            requiresAuth: true,
            // requiredPermissions: 'system_banner_manage_port'
          }
        },
        {
          path: 'team-spaces',
          name: 'TeamSpaceManagement',
          component: () => import('../views/TeamSpaceManagement.vue'),
          meta: {
            title: '团队空间管理',
            requiresAuth: true,
            requiredPermissions: 'team_space_port'
          }
        },
        {
          path: 'knowledge-spaces/:teamSpaceId?',
          name: 'KnowledgeSpace',
          component: () => import('../views/KnowledgeSpace.vue'),
          meta: {
            title: '知识空间',
            requiresAuth: true,
            requiredPermissions: 'knowledge_space_port'
          }
        },
        {
          path: 'personal-center',
          name: 'PersonalCenter',
          component: () => import('../views/PersonalCenter.vue'),
          meta: {
            title: '个人中心',
            requiresAuth: true
          }
        },
        {
          path: 'my-reading-tasks',
          name: 'MyReadingTasks',
          component: () => import('../views/MyReadingTasks.vue'),
          meta: {
            title: '我的签读',
            requiresAuth: true
          }
        },
        {
          path: 'sign-reading-management',
          name: 'SignReadingManagement',
          component: () => import('../views/SignReadingManagement.vue'),
          meta: {
            title: '签读管理',
            requiresAuth: true
          }
        },
        {
          path: 'collections',
          name: 'PersonalCollections',
          component: () => import('../views/PersonalCollections.vue'),
          meta: {
            title: '个人收藏',
            requiresAuth: true
          }
        },
        {
          path: 'likes',
          name: 'PersonalLikes',
          component: () => import('../views/PersonalLikes.vue'),
          meta: {
            title: '个人点赞',
            requiresAuth: true
          }
        },
        {
          path: 'browse-history',
          name: 'PersonalBrowseHistory',
          component: () => import('../views/PersonalBrowseHistory.vue'),
          meta: {
            title: '个人浏览记录',
            requiresAuth: true
          }
        },
        {
          path: 'daily-stats',
          name: 'PersonalDailyStats',
          component: () => import('../views/PersonalDailyStats.vue'),
          meta: {
            title: '个人数据统计',
            requiresAuth: true
          }
        },
        // 资源审批
        {
          path: 'my-applications',
          name: 'MyApplications',
          component: () => import('../views/MyApplications.vue'),
          meta: {
            title: '我的申请',
            requiresAuth: true
          }
        },
        {
          path: 'pending-review',
          name: 'PendingReview',
          component: () => import('../views/PendingReview.vue'),
          meta: {
            title: '我的审批',
            requiresAuth: true
          }
        },
        // 反馈处理
        {
          path: 'my-feedbacks',
          name: 'MyFeedbacks',
          component: () => import('../views/MyFeedbacks.vue'),
          meta: {
            title: '我的反馈',
            requiresAuth: true
          }
        },
        {
          path: 'feedback-handling',
          name: 'FeedbackHandling',
          component: () => import('../views/FeedbackHandling.vue'),
          meta: {
            title: '反馈处理',
            requiresAuth: true
          }
        }
      ]
    },
    {
      path: '/articles/:knowledgeBaseId',
      name: 'ArticleManagement',
      component: () => import('../views/ArticleManagement.vue'),
      meta: {
        title: '文章管理',
        requiresAuth: true
      }
    },
  ]
})

// 路由守卫：检查认证状态和权限
router.beforeEach(async (to, _from, next) => {
  startTopProgress()
  const isAuthenticated = authUtils.isAuthenticated()
  
  // 如果访问需要认证的页面但未登录，跳转到登录页
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
    return
  }
  
  // 如果已登录但访问登录/注册页，跳转到首页
  if ((to.path === '/login' || to.path === '/register' || to.path === '/forgot-password') && isAuthenticated) {
    next('/')
    return
  }
  const userStore = useUserStore()
  let userId = userStore.currentUserId
  // 仅在有 token 时拉取当前用户；未登录访问登录页等场景不应请求 /api/users/me
  if (!userId && isAuthenticated) {
    await userStore.fetchCurrentUser()
    userId = userStore.currentUserId
    console.log('userId1111', to.path)
    console.log('userStore.currentUserRoles------router', userStore.currentUserRoles)
  }
  
  // 检查权限
  if (isAuthenticated && to.meta.requiredPermissions) {
    try {
      const requiredPermissions = to.meta.requiredPermissions as string | string[]
      console.log('requiredPermissions', requiredPermissions)
      const hasAccess = await hasPermission(requiredPermissions)
      console.log('hasAccess', hasAccess)
      
      // 设置权限检查结果到路由 meta，用于在布局中显示无权限页面
      if (!hasAccess) {
        to.meta.hasPermission = false
        // 仍然允许导航，让布局组件显示无权限页面
      } else {
        to.meta.hasPermission = true
      }
    } catch (error) {
      console.error('权限检查失败:', error)
      // 如果权限检查出错，允许访问（避免因为权限系统问题导致无法访问）
      to.meta.hasPermission = true
    }
  } else {
    // 如果没有权限要求，默认有权限
    to.meta.hasPermission = true
  }
  
  next()
})

router.afterEach(() => {
  doneTopProgress()
})

router.onError(() => {
  doneTopProgress()
})

export { router }
