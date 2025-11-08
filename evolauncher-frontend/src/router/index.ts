import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: {
      title: '项目仪表盘'
    }
  },
  {
    path: '/project/:id',
    name: 'ProjectWorkspace',
    component: () => import('@/views/WorkspaceView.vue'),
    meta: {
      title: '工作区'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard for page titles
router.beforeEach((to, _from, next) => {
  // Set page title
  const title = to.meta.title as string
  if (title) {
    document.title = `${title} - EvoLabeler`
  }
  
  next()
})

export default router

