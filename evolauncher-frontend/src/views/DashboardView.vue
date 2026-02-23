<script setup lang="ts">
/**
 * Dashboard View - 仪表盘主视图
 * 
 * 模块化重构版本：
 * - HeroSection: 顶部 Hero 区域
 * - ProjectList: 项目列表（包含 ProjectCard）
 * - AgentStatusList: Agent 状态列表
 */

import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import gsap from 'gsap'

// 子组件
import HeroSection from '@/components/dashboard/HeroSection.vue'
import ProjectList from '@/components/dashboard/ProjectList.vue'
import AgentStatusList from '@/components/dashboard/AgentStatusList.vue'
import CreateProjectWizard from '@/components/project/CreateProjectWizard.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'

// 数据与类型
// Real API client + mock fallback for projects
import { projectsApi } from '@/api/projects'
import { USE_BACKEND_API } from '@/api/client'
import { fetchProjects, type Project } from '@/mock/projects'

// TODO: Replace with real backend API when agents/metrics endpoints are available
import { fetchAgentStatuses, type AgentStatus } from '@/mock/agents'
import { systemMetrics, type SystemMetric } from '@/mock/systemMetrics'

import { ElNotification, ElMessage } from 'element-plus'

const router = useRouter()
const { t } = useI18n()

// 状态
const projects = ref<Project[]>([])
const isLoading = ref(true)
const isLoadingAgents = ref(true)
const agentStatuses = ref<AgentStatus[]>([])
const metrics = ref<SystemMetric[]>(systemMetrics)
const showCreateWizard = ref(false)

// ========== 数据加载 ==========
const loadProjects = async () => {
  isLoading.value = true
  try {
    let data: Project[]

    if (USE_BACKEND_API) {
      try {
        // Try real backend API first
        const response = await projectsApi.list()
        // Transform API Project to mock-compatible Project type
        data = response.projects.map((p) => ({
          id: p.id,
          name: p.name,
          imageCount: p.imageCount,
          createdAt: p.createdAt,
          updatedAt: p.updatedAt,
          status: p.status,
          thumbnailUrl: p.thumbnailUrl || '',
          description: p.description,
          accuracy: p.accuracy,
        }))
        console.info('[Dashboard] Loaded projects from backend API')
      } catch (apiError) {
        // Backend unavailable — fall back to mock data
        console.warn('[Dashboard] Backend API failed, falling back to mock data:', apiError)
        data = await fetchProjects()
      }
    } else {
      // Backend API disabled — use mock data directly
      data = await fetchProjects()
    }

    projects.value = data
    await nextTick()
    animateCards()
  } catch (error) {
    console.error('Failed to load projects:', error)
    ElNotification.error({
      title: 'Network',
      message: 'Unable to refresh projects. Retrying mechanism exhausted.'
    })
  } finally {
    isLoading.value = false
  }
}

const loadAgents = async () => {
  isLoadingAgents.value = true
  try {
    agentStatuses.value = await fetchAgentStatuses()
    await nextTick()
    animateAgents()
  } catch (error) {
    console.error('Failed to load agent statuses', error)
    ElNotification.warning({
      title: 'Agents',
      message: 'Could not refresh agent telemetry.'
    })
  } finally {
    isLoadingAgents.value = false
  }
}

// ========== GSAP 动画 ==========
const animateCards = () => {
  const cards = document.querySelectorAll('.project-card')
  gsap.fromTo(
    cards,
    { opacity: 0, y: 40, scale: 0.95 },
    {
      opacity: 1,
      y: 0,
      scale: 1,
      duration: 0.6,
      stagger: 0.1,
      ease: 'power4.out',
      clearProps: 'all'
    }
  )
}

const animateAgents = () => {
  const cards = document.querySelectorAll('.agent-card')
  gsap.fromTo(
    cards,
    { opacity: 0, x: 24 },
    {
      opacity: 1,
      x: 0,
      duration: 0.5,
      stagger: 0.08,
      ease: 'power3.out',
      clearProps: 'all'
    }
  )
}

const animateMetrics = () => {
  const cards = document.querySelectorAll('.metric-card')
  gsap.fromTo(
    cards,
    { scale: 0.92, opacity: 0 },
    {
      scale: 1,
      opacity: 1,
      duration: 0.4,
      stagger: 0.05,
      ease: 'back.out(1.4)',
      clearProps: 'all'
    }
  )
}

// ========== 事件处理 ==========
const handleCreateProject = () => {
  showCreateWizard.value = true
}

const openCoPilotWorkspace = () => {
  router.push({ name: 'CoPilotWorkspace' })
}

const openProject = (project: Project) => {
  try {
    router.push({
      name: 'ProjectWorkspace',
      params: { id: project.id }
    })
  } catch (error) {
    console.error('Failed to open project:', error)
    ElMessage.error(t('errors.unknownError'))
  }
}

const handleProjectCreated = async (newProject: Project) => {
  projects.value.unshift(newProject)
  
  ElNotification.success({
    title: '成功',
    message: `项目 "${newProject.name}" 创建成功`,
    duration: 2500
  })
  
  await nextTick()
  
  const newCard = document.querySelector('.project-card:first-child')
  if (newCard) {
    gsap.fromTo(
      newCard,
      { scale: 0.9, opacity: 0 },
      { 
        scale: 1, 
        opacity: 1, 
        duration: 0.6, 
        ease: 'back.out(1.5)',
        onComplete: () => {
          setTimeout(() => openProject(newProject), 500)
        }
      }
    )
  }
}

// ========== 生命周期 ==========
onMounted(async () => {
  await nextTick()
  animateMetrics()
  loadProjects()
  loadAgents()
})
</script>

<template>
  <div class="dashboard-view">
    <!-- Hero Section -->
    <HeroSection 
      :metrics="metrics"
      @create-project="handleCreateProject"
      @open-copilot="openCoPilotWorkspace"
    />

    <!-- 项目创建向导 -->
    <CreateProjectWizard
      v-model:visible="showCreateWizard"
      @created="handleProjectCreated"
    />
    
    <!-- Loading state -->
    <div v-if="isLoading" class="content-grid">
      <div class="projects-grid">
        <LoadingSkeleton v-for="i in 6" :key="i" variant="card" height="280px" />
      </div>
    </div>
    <!-- Main Content Layout -->
    <div v-else class="content-grid">
      <!-- Left Column: Projects -->
      <ProjectList
        :projects="projects"
        :is-loading="isLoading"
        @create-project="handleCreateProject"
        @open-project="openProject"
      />

      <!-- Right Column: Agent Telemetry -->
      <AgentStatusList
        :agents="agentStatuses"
        :is-loading="isLoadingAgents"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.dashboard-view {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  @include custom-scrollbar;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 32px;
  padding: 0 clamp(24px, 3vw, 40px) 40px;
  
  @media (max-width: 1280px) {
    grid-template-columns: 1fr;
  }
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

// 响应式设计
@media (max-width: 768px) {
  .content-grid {
    padding: 0 16px 32px;
  }
}
</style>
