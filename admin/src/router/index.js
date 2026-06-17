import { createRouter, createWebHistory } from 'vue-router'
import { getToken, isAdmin } from '@/utils/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '管理员登录' }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '数据看板', icon: 'DataBoard' }
      },
      {
        path: 'polls/pending',
        name: 'PendingPolls',
        component: () => import('@/views/PollManagement.vue'),
        meta: { title: '审核投票', icon: 'DocumentChecked', status: 'pending' }
      },
      {
        path: 'polls/rejected',
        name: 'RejectedPolls',
        component: () => import('@/views/PollManagement.vue'),
        meta: { title: '删除违规投票', icon: 'Delete', status: 'rejected' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = getToken()

  if (to.meta.title) {
    document.title = `${to.meta.title} - 投票系统管理后台`
  }

  if (to.path === '/login') {
    if (token && isAdmin()) {
      next('/')
    } else {
      next()
    }
    return
  }

  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  if (to.meta.requiresAdmin && !isAdmin()) {
    next('/login')
    return
  }

  next()
})

export default router
