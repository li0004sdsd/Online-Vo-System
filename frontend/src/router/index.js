import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated } from '@/utils/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'PollList',
    component: () => import('@/views/PollList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/poll/:id',
    name: 'PollDetail',
    component: () => import('@/views/PollDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/create',
    name: 'CreatePoll',
    component: () => import('@/views/CreatePoll.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/results/:id',
    name: 'PollResults',
    component: () => import('@/views/PollResults.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && isAuthenticated()) {
    next('/')
  } else {
    next()
  }
})

export default router
