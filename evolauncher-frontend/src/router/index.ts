import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router'

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
  },
  {
    path: '/copilot/:id?',
    name: 'CoPilotWorkspace',
    component: () => import('@/views/CoPilotWorkspaceView.vue'),
    meta: {
      title: '协同工作区'
    }
  }
]

const router = createRouter({
  // 使用 Hash 路由以兼容 Electron 打包后的 file:// 协议，避免首次进入白屏
  history: createWebHashHistory(),
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

