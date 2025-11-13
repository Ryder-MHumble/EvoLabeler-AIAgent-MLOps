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
    <!-- Hero Section - Redesigned -->
    <div class="hero-section">
      <div class="hero-background">
        <div class="hero-glow hero-glow-1"></div>
        <div class="hero-glow hero-glow-2"></div>
        <div class="hero-glow hero-glow-3"></div>
      </div>
      
      <div class="hero-content">
        <div class="hero-text">
          <div class="hero-badge">
            <Icon icon="ph:sparkle-fill" :width="16" />
            <span>AI驱动的进化式标注平台</span>
          </div>
          <h1 class="hero-title">{{ $t('dashboard.title') }}</h1>
          <p class="hero-subtitle">通过主动学习与多智能体协作，持续优化模型性能，自动化标注流程，让AI训练更高效</p>
        </div>
        
        <el-button 
          type="primary" 
          size="large" 
          @click="handleCreateProject"
          class="hero-cta"
        >
          <Icon icon="ph:plus-circle" :width="22" />
          <span>{{ $t('dashboard.createProject') }}</span>
          <Icon icon="ph:arrow-right" :width="18" />
        </el-button>
      </div>
      
      <!-- Quick Stats in Hero -->
      <div class="hero-stats">
        <div 
          v-for="metric in metrics" 
          :key="metric.id" 
          class="hero-stat-item metric-card"
        >
          <div class="hero-stat-icon">
            <Icon 
              :icon="metric.id === 'active-projects' ? 'ph:folder-open-fill' : 
                     metric.id === 'total-images' ? 'ph:images-fill' : 
                     metric.id === 'avg-accuracy' ? 'ph:chart-line-up-fill' : 
                     'ph:cpu-fill'" 
              :width="24" 
            />
          </div>
          <div class="hero-stat-content">
            <div class="hero-stat-value">
              {{ metric.value.toLocaleString() }}
              <span v-if="metric.unit">{{ metric.unit }}</span>
            </div>
            <div class="hero-stat-label">{{ metric.label }}</div>
            <div class="hero-stat-trend" :class="metric.trend">
              <Icon :icon="trendIcon(metric.trend)" :width="14" />
              <span v-if="metric.delta !== 0">
                {{ metric.trend === 'down' ? '-' : '+' }}{{ metric.delta }}{{ metric.unit }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 项目创建向导 -->
    <CreateProjectWizard
      v-model:visible="showCreateWizard"
      @created="handleProjectCreated"
    />
    
    <!-- Main Content Layout -->
    <div class="content-grid">
      <!-- Left Column: Projects -->
      <div class="projects-column">
        <div class="section-header-modern">
          <div class="section-header-left">
            <div class="section-icon-badge">
              <Icon icon="ph:folder-open-fill" :width="20" />
            </div>
            <div>
              <h2 class="section-title-modern">我的项目</h2>
              <p class="section-desc-modern">
                {{ projects.length > 0 ? `共 ${projects.length} 个进化项目` : '开始创建您的第一个项目' }}
              </p>
            </div>
          </div>
          <el-button text @click="handleCreateProject">
            <Icon icon="ph:plus" :width="18" />
            <span>新建</span>
          </el-button>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="projects-list">
          <AnimatedCard
            v-for="i in 6"
            :key="`skeleton-${i}`"
            :hoverable="false"
          >
            <LoadingSkeleton type="image" height="200px" />
            <div class="mt-4">
              <LoadingSkeleton type="title" width="60%" />
              <LoadingSkeleton type="text" width="40%" count="2" />
            </div>
          </AnimatedCard>
        </div>
        
        <!-- Projects List -->
        <div v-else-if="projects.length > 0" class="projects-list">
        <AnimatedCard
          v-for="project in projects"
          :key="project.id"
          class="project-card"
          :hoverable="true"
          :clickable="true"
          @click="openProject(project)"
          padding="0"
        >
          <!-- Project Thumbnail Image -->
          <div class="project-thumbnail">
            <img 
              :src="project.thumbnailUrl || `https://picsum.photos/seed/${project.id}/400/300`" 
              :alt="project.name"
              class="project-image"
            />
            <!-- Status Tag - Premium Design -->
            <div class="project-tag-wrapper">
              <div class="project-tag" :class="`tag-${project.status}`">
                <span class="tag-dot"></span>
                <span class="tag-text">{{ $t(`status.${project.status}`) }}</span>
              </div>
            </div>
            <!-- Gradient Overlay -->
            <div class="project-image-overlay"></div>
          </div>
          
          <!-- Bottom Section with Info -->
          <div class="project-bottom-section">
            <h3 class="project-title">{{ project.name }}</h3>
            <p class="project-description" v-if="project.description">
              {{ project.description }}
            </p>
            
            <div class="project-stats-row">
              <div class="stat-item">
                <span class="stat-value">{{ project.imageCount }}</span>
                <span class="stat-label">图像数</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ project.accuracy || 0 }}%</span>
                <span class="stat-label">准确率</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ project.status === 'completed' ? '✓' : '•' }}</span>
                <span class="stat-label">状态</span>
            </div>
            </div>
          </div>
        </AnimatedCard>
        </div>
        
        <!-- Empty State -->
        <div v-else class="empty-state-modern">
          <div class="empty-illustration">
            <Icon icon="ph:folder-open" :width="80" />
          </div>
          <h3 class="empty-title">{{ $t('dashboard.noProjects') }}</h3>
          <p class="empty-description">{{ $t('dashboard.noProjectsDesc') }}</p>
          <el-button type="primary" size="large" @click="handleCreateProject">
            <Icon icon="ph:plus-circle" :width="20" />
            <span>{{ $t('dashboard.createProject') }}</span>
          </el-button>
        </div>
      </div>
      
      <!-- Right Column: Agent Telemetry -->
      <div class="telemetry-column">
        <div class="section-header-modern">
          <div class="section-header-left">
            <div class="section-icon-badge agents">
              <Icon icon="ph:robot-fill" :width="20" />
            </div>
            <div>
              <h2 class="section-title-modern">智能体状态</h2>
              <p class="section-desc-modern">{{ $t('dashboard.liveSnapshots') }}</p>
            </div>
          </div>
        </div>
        
        <div class="agents-list">
          <AnimatedCard
            v-if="isLoadingAgents"
            v-for="n in 4"
            :key="`agent-skeleton-${n}`"
            class="agent-card-compact"
            :hoverable="false"
          >
            <LoadingSkeleton type="title" width="40%" />
            <LoadingSkeleton type="text" width="80%" count="2" />
          </AnimatedCard>

          <AnimatedCard
            v-else
            v-for="agent in agentStatuses"
            :key="agent.id"
            class="agent-card-compact"
          >
            <div class="agent-compact-header">
              <div class="agent-avatar-small" :class="agent.mood">
                <Icon icon="ph:robot-fill" :width="18" />
              </div>
              <div class="agent-compact-info">
                <h3 class="agent-name-compact">{{ agent.displayName }}</h3>
                <p class="agent-role-compact">{{ agent.name }}</p>
              </div>
              <StatusBadge
                :status="agent.status === 'waiting' ? 'idle' : agent.status"
                :size="'small'"
              />
            </div>

            <div class="agent-compact-metrics">
              <div class="agent-compact-metric">
                <Icon icon="ph:gauge-fill" :width="14" />
                <span>{{ Math.round(agent.confidence * 100) }}%</span>
              </div>
              <div class="agent-compact-metric">
                <Icon icon="ph:lightning-fill" :width="14" />
                <span>{{ agent.throughput }}/min</span>
              </div>
              <div class="agent-compact-metric">
                <Icon icon="ph:check-circle-fill" :width="14" />
                <span>{{ Math.round(agent.metrics.successRate * 100) }}%</span>
              </div>
            </div>
          </AnimatedCard>
        </div>
      </div>
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

// ========== Hero Section ==========
.hero-section {
  position: relative;
  padding: clamp($spacing-3xl, 5vw, $spacing-4xl) clamp($spacing-xl, 3vw, $spacing-3xl);
  margin-bottom: $spacing-3xl;
  overflow: hidden;
  border-radius: 32px;
  background: linear-gradient(135deg, 
    rgba(74, 105, 255, 0.05) 0%,
    rgba(138, 43, 226, 0.05) 100%
  );
  
  .dark & {
    background: linear-gradient(135deg, 
      rgba(96, 165, 250, 0.08) 0%,
      rgba(167, 139, 250, 0.08) 100%
    );
  }
  
  // 添加网格背景
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: 
      linear-gradient(rgba(74, 105, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(74, 105, 255, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    opacity: 0.5;
    animation: gridMove 20s linear infinite;
    
    .dark & {
      background-image: 
        linear-gradient(rgba(96, 165, 250, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(96, 165, 250, 0.05) 1px, transparent 1px);
    }
  }
}

@keyframes gridMove {
  0% { transform: translate(0, 0); }
  100% { transform: translate(50px, 50px); }
}

.hero-background {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.hero-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.5;
  animation: float 25s ease-in-out infinite;
  
  &.hero-glow-1 {
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(74, 105, 255, 0.4), transparent 70%);
    top: -300px;
    left: -150px;
    animation-name: float1;
  }
  
  &.hero-glow-2 {
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(138, 43, 226, 0.3), transparent 70%);
    bottom: -250px;
    right: -100px;
    animation-name: float2;
    animation-delay: -8s;
  }
  
  &.hero-glow-3 {
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(16, 185, 129, 0.25), transparent 70%);
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    animation-name: pulse;
    animation-delay: -16s;
  }
}

@keyframes float1 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(40px, -40px) scale(1.15); }
  66% { transform: translate(-30px, 30px) scale(0.9); }
}

@keyframes float2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(-35px, 35px) scale(1.1); }
  66% { transform: translate(40px, -25px) scale(0.95); }
}

@keyframes pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
  50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.3; }
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: $spacing-2xl;
  margin-bottom: $spacing-3xl;
  
  @media (max-width: 1024px) {
    flex-direction: column;
    text-align: center;
    align-items: center;
  }
}

.hero-text {
  flex: 1;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: $spacing-xs;
  padding: $spacing-sm $spacing-lg;
  background: rgba(74, 105, 255, 0.1);
  border: 1px solid rgba(74, 105, 255, 0.2);
  border-radius: $radius-full;
  font-size: $font-size-sm;
  font-weight: $font-weight-semibold;
  color: var(--color-primary);
  margin-bottom: $spacing-lg;
  backdrop-filter: blur(8px);
  
  .dark & {
    background: rgba(96, 165, 250, 0.15);
    border-color: rgba(96, 165, 250, 0.3);
  }
}

.hero-title {
  font-size: clamp($font-size-3xl, 5vw, 4rem);
  font-weight: $font-weight-extrabold;
  line-height: 1.1;
  margin-bottom: $spacing-md;
  background: linear-gradient(135deg, #4A69FF, #8B5CF6, #EC4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: clamp($font-size-base, 1.5vw, $font-size-lg);
  color: var(--color-text-secondary);
  margin: 0;
  max-width: 600px;
}

.hero-cta {
  display: inline-flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-lg $spacing-2xl;
  font-size: $font-size-lg;
  font-weight: $font-weight-bold;
  border-radius: $radius-full;
  box-shadow: 0 8px 24px rgba(74, 105, 255, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(74, 105, 255, 0.4);
  }
}

.hero-stats {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: $spacing-lg;
}

.hero-stat-item {
  display: flex;
  align-items: center;
  gap: $spacing-lg;
  padding: $spacing-xl;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  .dark & {
    background: rgba(30, 41, 59, 0.6);
    border-color: rgba(255, 255, 255, 0.1);
  }
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
  }
}

.hero-stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 18px;
  background: linear-gradient(135deg, #4A69FF, #7AA2F7);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 8px 20px rgba(74, 105, 255, 0.3);
}

.hero-stat-content {
  flex: 1;
}

.hero-stat-value {
  font-size: $font-size-3xl;
  font-weight: $font-weight-extrabold;
  color: var(--color-text-primary);
  line-height: 1;
  margin-bottom: 4px;
  
  span {
    font-size: $font-size-base;
    margin-left: 4px;
    color: var(--color-text-secondary);
  }
}

.hero-stat-label {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 4px;
}

.hero-stat-trend {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: $font-size-xs;
  font-weight: $font-weight-semibold;
  
  &.up { color: #10B981; }
  &.down { color: #EF4444; }
  &.steady { color: var(--color-text-tertiary); }
}

// ========== Main Content Grid ==========
.content-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: $spacing-2xl;
  padding: 0 clamp($spacing-xl, 3vw, $spacing-3xl) $spacing-3xl;
  
  @media (max-width: 1280px) {
    grid-template-columns: 1fr;
  }
}

// ========== Section Headers ==========
.section-header-modern {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-xl;
  padding-bottom: $spacing-lg;
  border-bottom: 2px solid var(--color-border);
}

.section-header-left {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.section-icon-badge {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, #4A69FF, #7AA2F7);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 6px 16px rgba(74, 105, 255, 0.3);
  
  &.agents {
    background: linear-gradient(135deg, #8B5CF6, #A78BFA);
    box-shadow: 0 6px 16px rgba(139, 92, 246, 0.3);
  }
}

.section-title-modern {
  font-size: $font-size-2xl;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  margin: 0;
  line-height: 1.2;
}

.section-desc-modern {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  margin: 0;
}

// ========== Projects Column ==========
.projects-column {
  min-width: 0;
}

.projects-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: $spacing-xl;
}

// Project Card - Premium Design with Image
.project-card {
  cursor: pointer;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);

  &:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
    
    .project-image {
      transform: scale(1.1);
    }
    
    .project-tag {
      transform: translateX(-4px);
    }
  }
  
  .dark & {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    
    &:hover {
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
    }
  }
}

// Project Thumbnail
.project-thumbnail {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.project-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.project-image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60%;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.7) 0%,
    rgba(0, 0, 0, 0.3) 50%,
    transparent 100%
  );
  pointer-events: none;
}

// Premium Tag Design
.project-tag-wrapper {
  position: absolute;
  top: $spacing-md;
  right: $spacing-md;
  z-index: 2;
}

.project-tag {
  display: inline-flex;
  align-items: center;
  gap: $spacing-xs;
  padding: $spacing-sm $spacing-lg;
  border-radius: $radius-full;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  font-size: $font-size-xs;
  font-weight: $font-weight-bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  
  &.tag-idle {
    background: rgba(148, 163, 184, 0.95);
    color: white;
    
    .tag-dot {
      background: white;
      box-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
    }
  }
  
  &.tag-training {
    background: rgba(59, 130, 246, 0.95);
    color: white;
    
    .tag-dot {
      background: white;
      animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
  }
  
  &.tag-labeling {
    background: rgba(139, 92, 246, 0.95);
    color: white;
    
    .tag-dot {
      background: white;
      animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
  }
  
  &.tag-completed {
    background: rgba(16, 185, 129, 0.95);
    color: white;
    
    .tag-dot {
      background: white;
      box-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
    }
  }
  
  &.tag-error {
    background: rgba(239, 68, 68, 0.95);
    color: white;
    
    .tag-dot {
      background: white;
      box-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
    }
  }
}

.tag-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.tag-text {
  font-size: $font-size-xs;
  line-height: 1;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    box-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
  }
  50% {
    opacity: 0.5;
    box-shadow: 0 0 4px rgba(255, 255, 255, 0.4);
  }
}

// 底部信息区域
.project-bottom-section {
  padding: $spacing-lg;
}

.project-title {
  display: block;
  font-size: $font-size-lg;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  text-align: center;
  margin: 0 0 $spacing-sm 0;
  @include truncate;
}

.project-description {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  text-align: center;
  @include line-clamp(2);
  margin: 0 0 $spacing-lg 0;
  min-height: 2.4em;
}

// 统计信息行
.project-stats-row {
  display: flex;
  justify-content: space-between;
  margin-top: $spacing-lg;
  padding-top: $spacing-md;
  border-top: 1px solid var(--color-border);
}

.stat-item {
  flex: 1;
  text-align: center;
  padding: $spacing-xs;
  
  &:nth-child(2) {
    border-left: 1px solid var(--color-border);
    border-right: 1px solid var(--color-border);
  }
}

.stat-value {
  font-size: $font-size-lg;
  font-weight: $font-weight-bold;
  display: block;
  color: var(--color-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: $font-size-xs;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

// Empty State - Modern Design
.empty-state-modern {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: $spacing-4xl $spacing-2xl;
  text-align: center;
  min-height: 400px;
  background: var(--color-surface-elevated);
  border-radius: 24px;
  border: 2px dashed var(--color-border);
}

.empty-illustration {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(74, 105, 255, 0.1), rgba(138, 43, 226, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  margin-bottom: $spacing-xl;
  
  .dark & {
    background: linear-gradient(135deg, rgba(96, 165, 250, 0.15), rgba(167, 139, 250, 0.15));
  }
}

.empty-title {
  font-size: $font-size-2xl;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  margin-bottom: $spacing-sm;
}

.empty-description {
  font-size: $font-size-base;
  color: var(--color-text-secondary);
  margin-bottom: $spacing-xl;
  max-width: 400px;
}

// ========== Telemetry Column ==========
.telemetry-column {
  min-width: 0;
  
  @media (max-width: 1280px) {
    display: none; // Hide on smaller screens for better space usage
  }
}

.agents-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.agent-card-compact {
  padding: $spacing-lg;
}

.agent-compact-header {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-md;
}

.agent-avatar-small {
  width: 36px;
  height: 36px;
  border-radius: $radius-full;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(74, 105, 255, 0.25);

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

.agent-compact-info {
  flex: 1;
  min-width: 0;
}

.agent-name-compact {
  font-size: $font-size-base;
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
  margin: 0;
  @include truncate;
}

.agent-role-compact {
  font-size: $font-size-xs;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.agent-compact-metrics {
  display: flex;
  gap: $spacing-lg;
  padding: $spacing-sm $spacing-md;
  background: var(--color-surface-elevated);
  border-radius: $radius-md;
}

.agent-compact-metric {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: $font-size-sm;
  font-weight: $font-weight-semibold;
  color: var(--color-text-secondary);
  
  :deep(.iconify) {
    color: var(--color-primary);
  }
}

// Utility classes
.mr-2 {
  margin-right: $spacing-xs;
}

.mt-4 {
  margin-top: $spacing-md;
}

// Responsive Design
@media (max-width: 768px) {
  .hero-section {
    padding: $spacing-2xl $spacing-lg;
    margin-bottom: $spacing-2xl;
  }
  
  .hero-stats {
    grid-template-columns: 1fr;
  }
  
  .content-grid {
    padding: 0 $spacing-lg $spacing-2xl;
  }
  
  .projects-list {
    grid-template-columns: 1fr;
  }
}
</style>



