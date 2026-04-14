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
    component: () => import('@/views/project/ProjectWorkspaceShellView.vue'),
    children: [
      {
        path: '',
        redirect: (to) => ({
          name: 'ProjectOverview',
          params: { id: to.params.id },
          query: to.query,
        }),
      },
      {
        path: 'overview',
        name: 'ProjectOverview',
        component: () => import('@/views/project/ProjectOverviewView.vue'),
        meta: {
          title: '项目总览'
        }
      },
      {
        path: 'annotate',
        name: 'ProjectAnnotate',
        component: () => import('@/views/project/ProjectAnnotateView.vue'),
        meta: {
          title: '协同标注'
        }
      },
      {
        path: 'train',
        name: 'ProjectTrain',
        component: () => import('@/views/project/ProjectTrainView.vue'),
        meta: {
          title: '训练面板'
        }
      }
    ]
  },
  {
    path: '/copilot/:id?',
    redirect: (to) => {
      if (to.params.id) {
        return {
          name: 'ProjectAnnotate',
          params: { id: to.params.id },
          query: to.query,
        }
      }
      return { name: 'Dashboard' }
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
