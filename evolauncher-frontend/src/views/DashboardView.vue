<script setup lang="ts">
/**
 * Dashboard View
 * 
 * Design Philosophy:
 * - Grid-based card layout showcasing all projects
 * - Stagger animation on mount using GSAP for dynamic feel
 * - Skeleton loading states for optimal UX
 * - Responsive grid that adapts to window size
 * 
 * Animation Strategy:
 * - Cards appear one by one with stagger effect
 * - Each card slides up and fades in
 * - Creates a sense of content "building up" on screen
 */

import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Icon } from '@iconify/vue'
import gsap from 'gsap'
import AnimatedCard from '@/components/common/AnimatedCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import CreateProjectWizard from '@/components/project/CreateProjectWizard.vue'
import { fetchProjects, type Project } from '@/mock/projects'
import { fetchAgentStatuses, type AgentStatus } from '@/mock/agents'
import { systemMetrics, type SystemMetric } from '@/mock/systemMetrics'
import { ElNotification, ElMessage } from 'element-plus'

const router = useRouter()
const { t } = useI18n()

const projects = ref<Project[]>([])
const isLoading = ref(true)
const isLoadingAgents = ref(true)
const agentStatuses = ref<AgentStatus[]>([])
const metrics = ref<SystemMetric[]>(systemMetrics)

// 项目创建向导
const showCreateWizard = ref(false)

const loadProjects = async () => {
  isLoading.value = true
  try {
    const data = await fetchProjects()
    projects.value = data
    
    // Wait for DOM update before animating
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

/**
 * GSAP stagger animation for cards
 * 
 * Design Intent: Use GSAP's stagger feature to create a cascading
 * entrance effect. Power4.easeOut creates a natural, smooth deceleration
 * that feels more organic than linear timing.
 */
const animateCards = () => {
  const cards = document.querySelectorAll('.project-card')
  
  gsap.fromTo(
    cards,
    {
      opacity: 0,
      y: 40,
      scale: 0.95
    },
    {
      opacity: 1,
      y: 0,
      scale: 1,
      duration: 0.6,
      stagger: 0.1, // 100ms delay between each card
      ease: 'power4.out', // Smooth deceleration curve
      clearProps: 'all' // Clean up inline styles after animation
    }
  )
}

const animateAgents = () => {
  const cards = document.querySelectorAll('.agent-card')
  
  gsap.fromTo(
    cards,
    {
      opacity: 0,
      x: 24
    },
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

const trendIcon = (trend: SystemMetric['trend']) => {
  switch (trend) {
    case 'up':
      return 'ph:arrow-up-right'
    case 'down':
      return 'ph:arrow-down-right'
    default:
      return 'ph:minus'
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

const openProject = (project: Project) => {
  try {
    // 导航到项目工作区
    router.push({
      name: 'ProjectWorkspace',
      params: { id: project.id }
    })
  } catch (error) {
    console.error('Failed to open project:', error)
    ElMessage.error(t('errors.unknownError'))
  }
}

// 打开创建项目向导
const handleCreateProject = () => {
  showCreateWizard.value = true
}

// 处理项目创建完成
const handleProjectCreated = async (newProject: Project) => {
    // 添加到项目列表
    projects.value.unshift(newProject)
    
    // 成功提示
    ElNotification.success({
    title: '成功',
    message: `项目 "${newProject.name}" 创建成功`,
    duration: 2500
    })
    
    // 等待动画完成
    await nextTick()
    
    // 高亮新项目卡片
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
            // 动画完成后，自动导航到新项目工作区
            setTimeout(() => {
              openProject(newProject)
            }, 500)
          }
        }
      )
  }
}

onMounted(async () => {
  await nextTick()
  animateMetrics()
  loadProjects()
  loadAgents()
})
</script>

<template>
  <div class="dashboard-view">
    <!-- Header Section -->
    <div class="dashboard-header">
      <div class="header-content">
        <h1 class="dashboard-title">{{ $t('dashboard.title') }}</h1>
        <p class="dashboard-subtitle">{{ $t('dashboard.subtitle') }}</p>
      </div>
      <el-button type="primary" size="large" @click="handleCreateProject">
        <Icon icon="ph:plus-circle" :width="20" class="mr-2" />
        {{ $t('dashboard.createProject') }}
      </el-button>
    </div>

    <!-- 项目创建向导 -->
    <CreateProjectWizard
      v-model:visible="showCreateWizard"
      @created="handleProjectCreated"
    />

    <!-- System Metrics -->
    <section class="metrics-section">
      <AnimatedCard
        v-for="metric in metrics"
        :key="metric.id"
        class="metric-card"
        :hoverable="true"
      >
        <div class="metric-header">
          <span class="metric-label">{{ metric.label }}</span>
          <span
            class="metric-trend"
            :class="metric.trend"
          >
            <Icon :icon="trendIcon(metric.trend)" :width="16" />
            <span v-if="metric.delta !== 0">
              {{ metric.trend === 'down' ? '-' : '+' }}{{ metric.delta }}{{ metric.unit }}
            </span>
          </span>
        </div>
        <div class="metric-value">
          {{ metric.value.toLocaleString() }}
          <span v-if="metric.unit" class="metric-unit">{{ metric.unit }}</span>
        </div>
        <p class="metric-description">
          {{ metric.description }}
        </p>
        <div class="metric-glow"></div>
      </AnimatedCard>
    </section>

    <!-- Agent Telemetry -->
    <section class="agents-section">
      <div class="section-heading">
        <h2 class="section-title">{{ $t('dashboard.multiAgentTelemetry') }}</h2>
        <span class="section-subtitle">{{ $t('dashboard.liveSnapshots') }}</span>
      </div>

      <div class="agents-grid">
        <AnimatedCard
          v-if="isLoadingAgents"
          v-for="n in 4"
          :key="`agent-skeleton-${n}`"
          class="agent-card"
          :hoverable="false"
        >
          <LoadingSkeleton type="title" width="40%" />
          <LoadingSkeleton type="text" width="80%" count="2" />
          <LoadingSkeleton type="text" width="60%" />
        </AnimatedCard>

        <AnimatedCard
          v-else
          v-for="agent in agentStatuses"
          :key="agent.id"
          class="agent-card"
        >
          <div class="agent-card-header">
            <div class="agent-identity">
              <div class="agent-avatar" :class="agent.mood">
                <Icon icon="ph:robot-fill" :width="22" />
              </div>
              <div>
                <h3 class="agent-name">{{ agent.displayName }}</h3>
                <p class="agent-role">{{ agent.name }}</p>
              </div>
            </div>
            <StatusBadge
              :status="agent.status === 'waiting' ? 'idle' : agent.status"
              :size="'small'"
              :show-icon="true"
            />
          </div>

          <p class="agent-description">
            {{ agent.description }}
          </p>

          <div class="agent-metrics">
            <div class="agent-metric">
              <span class="agent-metric-label">{{ $t('agent.metrics.confidence') }}</span>
              <span class="agent-metric-value">{{ Math.round(agent.confidence * 100) }}%</span>
            </div>
            <div class="agent-metric">
              <span class="agent-metric-label">{{ $t('agent.metrics.throughput') }}</span>
              <span class="agent-metric-value">{{ agent.throughput }}/min</span>
            </div>
            <div class="agent-metric">
              <span class="agent-metric-label">{{ $t('agent.metrics.success') }}</span>
              <span class="agent-metric-value">{{ Math.round(agent.metrics.successRate * 100) }}%</span>
            </div>
          </div>

          <div class="agent-context">
            <div>
              <span class="agent-context-label">{{ $t('agent.lastTask') }}</span>
              <p class="agent-context-text">{{ agent.lastTask }}</p>
            </div>
            <div>
              <span class="agent-context-label">{{ $t('agent.nextAction') }}</span>
              <p class="agent-context-text">{{ agent.nextAction }}</p>
            </div>
          </div>
        </AnimatedCard>
      </div>
    </section>
    
    <!-- Stats Cards (optional, can be added later) -->
    
    <!-- Projects Grid -->
    <div class="projects-section">
      <!-- 项目列表标题 -->
      <div class="section-heading">
        <h2 class="section-title">
          <Icon icon="ph:folder-open" :width="28" class="mr-2" />
          我的项目
        </h2>
        <span class="section-subtitle">
          {{ projects.length > 0 ? `共 ${projects.length} 个项目` : '暂无项目' }}
        </span>
      </div>
      
      <!-- Loading State -->
      <div v-if="isLoading" class="projects-grid">
        <AnimatedCard
          v-for="i in 6"
          :key="`skeleton-${i}`"
          :hoverable="false"
        >
          <LoadingSkeleton type="image" height="180px" />
          <div class="mt-4">
            <LoadingSkeleton type="title" width="60%" />
            <LoadingSkeleton type="text" width="40%" count="2" />
          </div>
        </AnimatedCard>
      </div>
      
      <!-- Projects List -->
      <div v-else-if="projects.length > 0" class="projects-grid">
        <AnimatedCard
          v-for="project in projects"
          :key="project.id"
          class="project-card"
          :hoverable="true"
          :clickable="true"
          @click="openProject(project)"
          padding="0"
        >
          <!-- Project Thumbnail -->
          <div class="project-thumbnail">
            <img
              :src="project.thumbnailUrl"
              :alt="project.name"
              class="thumbnail-image"
            />
            <div class="thumbnail-overlay">
              <StatusBadge :status="project.status" />
            </div>
          </div>
          
          <!-- Project Info -->
          <div class="project-info">
            <h3 class="project-name">{{ project.name }}</h3>
            <p class="project-description" v-if="project.description">
              {{ project.description }}
            </p>
            
            <div class="project-meta">
              <div class="meta-item">
                <Icon icon="ph:images" :width="16" />
                <span>{{ project.imageCount }} images</span>
              </div>
              <div class="meta-item" v-if="project.accuracy">
                <Icon icon="ph:chart-line" :width="16" />
                <span>{{ project.accuracy }}%</span>
              </div>
            </div>
            
            <div class="project-footer">
              <span class="project-date">
                {{ formatDate(project.updatedAt) }}
              </span>
            </div>
          </div>
        </AnimatedCard>
      </div>
      
      <!-- Empty State -->
      <div v-else class="empty-state">
        <Icon icon="ph:folder-open" :width="80" class="empty-icon" />
        <h3 class="empty-title">{{ $t('dashboard.noProjects') }}</h3>
        <p class="empty-description">{{ $t('dashboard.noProjectsDesc') }}</p>
        <el-button type="primary" size="large">
          {{ $t('dashboard.createProject') }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.dashboard-view {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  padding: $spacing-2xl;
  @include custom-scrollbar;
}

// Header
.dashboard-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: $spacing-2xl;
  gap: $spacing-lg;
}

.header-content {
  flex: 1;
}

.dashboard-title {
  font-size: $font-size-4xl;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  margin-bottom: $spacing-xs;
}

.dashboard-subtitle {
  font-size: $font-size-lg;
  color: var(--color-text-secondary);
}

// Metrics Section
.metrics-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: $spacing-lg;
  margin-bottom: $spacing-2xl;
}

.metric-card {
  position: relative;
  overflow: hidden;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-sm;
}

.metric-label {
  font-size: $font-size-sm;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-text-tertiary);
}

.metric-trend {
  display: inline-flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: $font-size-xs;
  font-weight: $font-weight-medium;

  &.up {
    color: #10B981;
  }

  &.down {
    color: #EF4444;
  }

  &.steady {
    color: var(--color-text-tertiary);
  }
}

.metric-value {
  font-size: 2.5rem;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  line-height: 1.1;
}

.metric-unit {
  font-size: $font-size-base;
  margin-left: $spacing-xs;
  color: var(--color-text-secondary);
}

.metric-description {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  margin-top: $spacing-sm;
}

.metric-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle at top right,
    rgba(74, 105, 255, 0.15),
    transparent 55%
  );
  pointer-events: none;
  transition: opacity $transition-base;
  opacity: 0;

  .metric-card:hover & {
    opacity: 1;
  }
}

// Agents section
.agents-section {
  margin-bottom: $spacing-2xl;
}

.section-heading {
  display: flex;
  flex-direction: column;
  margin-bottom: $spacing-lg;
}

.section-title {
  font-size: $font-size-2xl;
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
}

.section-subtitle {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: $spacing-lg;
}

.agent-card {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
  height: 100%;
}

.agent-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.agent-identity {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.agent-avatar {
  width: 40px;
  height: 40px;
  border-radius: $radius-full;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 10px 20px rgba(74, 105, 255, 0.2);
  transition: all $transition-base;

  &.stable {
    background: linear-gradient(135deg, #4A69FF, #7AA2F7);
  }

  &.alert {
    background: linear-gradient(135deg, #F59E0B, #F97316);
  }

  &.critical {
    background: linear-gradient(135deg, #EF4444, #F87171);
  }
}

.agent-card:hover .agent-avatar {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 14px 24px rgba(74, 105, 255, 0.25);
}

.agent-name {
  font-size: $font-size-lg;
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
  margin: 0;
}

.agent-role {
  font-size: $font-size-xs;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.agent-description {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  margin: 0;
  @include line-clamp(2); // 限制最多2行，防止溢出
  word-break: break-word; // 长单词换行
}

.agent-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $spacing-sm;
}

.agent-metric {
  background: var(--color-surface-elevated);
  border-radius: $radius-md;
  padding: $spacing-sm;
  display: flex;
  flex-direction: column;
  gap: 4px;
  transition: transform $transition-base;

  &:hover {
    transform: translateY(-2px);
  }
}

.agent-metric-label {
  font-size: $font-size-xs;
  color: var(--color-text-tertiary);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  white-space: nowrap; // 防止换行
  overflow: hidden;
  text-overflow: ellipsis;
}

.agent-metric-value {
  font-size: $font-size-base;
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
  white-space: nowrap; // 防止换行
  overflow: hidden;
  text-overflow: ellipsis;
}

.agent-context {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: $spacing-md;
}

.agent-context-label {
  font-size: $font-size-xs;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.agent-context-text {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  margin: 0;
  @include truncate; // 单行截断
  word-break: break-word;
}

// Projects Grid
.projects-section {
  animation: fadeIn 0.5s ease-in-out;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: $spacing-xl;
}

// Project Card
.project-card {
  // Card content structure
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.project-thumbnail {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: var(--color-surface-elevated);
}

.thumbnail-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
  
  .project-card:hover & {
    transform: scale(1.05);
  }
}

.thumbnail-overlay {
  position: absolute;
  top: $spacing-md;
  right: $spacing-md;
}

.project-info {
  padding: $spacing-lg;
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.project-name {
  font-size: $font-size-xl;
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
  margin: 0;
  @include truncate;
}

.project-description {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  @include line-clamp(2);
  margin: 0;
}

.project-meta {
  display: flex;
  gap: $spacing-lg;
  margin-top: $spacing-xs;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: $font-size-sm;
  color: var(--color-text-tertiary);
}

.project-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: $spacing-sm;
  padding-top: $spacing-sm;
  border-top: 1px solid var(--color-border);
}

.project-date {
  font-size: $font-size-xs;
  color: var(--color-text-tertiary);
}

// Empty State
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $spacing-3xl;
  text-align: center;
  min-height: 400px;
}

.empty-icon {
  color: var(--color-text-tertiary);
  margin-bottom: $spacing-lg;
  opacity: 0.5;
}

.empty-title {
  font-size: $font-size-2xl;
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
  margin-bottom: $spacing-sm;
}

.empty-description {
  font-size: $font-size-base;
  color: var(--color-text-secondary);
  margin-bottom: $spacing-xl;
}

// Utility classes
.mr-1 {
  margin-right: 4px;
}

.mr-2 {
  margin-right: $spacing-xs;
}

.mt-1 {
  margin-top: 4px;
}

.mt-4 {
  margin-top: $spacing-md;
}

// 仪表盘整体优化
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: $spacing-2xl;
  
  // 响应式间距
  @media (max-width: 1024px) {
    gap: $spacing-xl;
  }
}
</style>

