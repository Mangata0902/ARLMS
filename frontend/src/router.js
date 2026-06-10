import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // ==================== 空白布局（无侧边栏）====================
  {
    path: '/login',
    name: 'Login',
    component: () => import('./views/Login.vue'),
    meta: { layout: 'blank' }
  },

  // ==================== 主布局（有侧边栏）====================
  {
    path: '/',
    redirect: '/chat'
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('./views/Chat.vue')
  },
  {
    path: '/chat/:session_id',
    name: 'ChatSession',
    component: () => import('./views/Chat.vue')
  },
  {
    path: '/detection',
    name: 'Detection',
    component: () => import('./views/Detection.vue')
  },
  {
    path: '/ingestion',
    name: 'Ingestion',
    component: () => import('./views/Ingestion.vue')
  },
  {
    path: '/materials',
    name: 'Materials',
    component: () => import('./views/Materials.vue')
  },
  {
    path: '/research',
    name: 'Research',
    component: () => import('./views/Research.vue')
  },
  {
    path: '/revision',
    name: 'Revision',
    component: () => import('./views/Revision.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('./views/Settings.vue')
  },

  // ==================== 404 兜底 ====================
  {
    path: '/:pathMatch(.*)*',
    redirect: '/chat'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ==================== 路由守卫（登录鉴权）====================
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  // 未登录且访问的不是登录页，强制跳转登录
  if (!token && to.name !== 'Login') {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router