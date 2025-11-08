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

// 新建项目对话框
const showCreateProjectDialog = ref(false)
const newProjectName = ref('')
const newProjectDescription = ref('')
const isCreatingProject = ref(false)

// 项目创建表单数据
const projectForm = ref({
  name: '',
  description: '',
  dataSource: 'local', // 'local' | 'remote'
  remoteUrl: '',
  modelType: 'yolov8s', // 'yolov8n' | 'yolov8s' | 'yolov8m' | 'yolov8l'
  customWeights: null as File | null,
  uploadedFiles: [] as File[],
  // 高级设置
  batchSize: 16,
  learningRate: 0.001,
  maxIterations: 100
})

// 文件上传相关
const fileInputRef = ref<HTMLInputElement | null>(null)
const weightsInputRef = ref<HTMLInputElement | null>(null)

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    projectForm.value.uploadedFiles = Array.from(target.files)
  }
}

const handleWeightsSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    projectForm.value.customWeights = target.files[0]
  }
}

const triggerFileUpload = () => {
  fileInputRef.value?.click()
}

const triggerWeightsUpload = () => {
  weightsInputRef.value?.click()
}

const removeUploadedFile = (index: number) => {
  projectForm.value.uploadedFiles.splice(index, 1)
}

const removeCustomWeights = () => {
  projectForm.value.customWeights = null
  if (weightsInputRef.value) {
    weightsInputRef.value.value = ''
  }
}

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

// 打开创建项目对话框
const handleCreateProject = () => {
  showCreateProjectDialog.value = true
  // 重置表单
  projectForm.value = {
    name: '',
    description: '',
    dataSource: 'local',
    remoteUrl: '',
    modelType: 'yolov8s',
    customWeights: null,
    uploadedFiles: [],
    batchSize: 16,
    learningRate: 0.001,
    maxIterations: 100
  }
}

// 创建新项目（完整流程）
const createProject = async () => {
  // 验证表单
  if (!projectForm.value.name.trim()) {
    ElMessage.warning(t('dashboard.newProjectDialog.projectNameRequired'))
    return
  }
  
  if (projectForm.value.dataSource === 'local' && projectForm.value.uploadedFiles.length === 0) {
    ElMessage.warning('Please upload training data')
    return
  }
  
  if (projectForm.value.dataSource === 'remote' && !projectForm.value.remoteUrl.trim()) {
    ElMessage.warning('Please provide a remote URL')
    return
  }
  
  isCreatingProject.value = true
  
  try {
    // 模拟API调用 - 上传文件和创建项目
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 创建新项目对象
    const newProject: Project = {
      id: `proj-${Date.now()}`,
      name: projectForm.value.name.trim(),
      description: projectForm.value.description.trim() || '',
      status: 'idle',
      imageCount: projectForm.value.uploadedFiles.length || 0,
      accuracy: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    
    // 添加到项目列表
    projects.value.unshift(newProject)
    
    // 关闭对话框
    showCreateProjectDialog.value = false
    
    // 成功提示
    ElNotification.success({
      title: t('common.success'),
      message: t('dashboard.projectCreated', { name: newProject.name }),
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
    
  } catch (error) {
    console.error('Failed to create project:', error)
    ElMessage.error(t('errors.saveFailed'))
  } finally {
    isCreatingProject.value = false
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

    <!-- 新建项目对话框 - 完整流程 -->
    <el-dialog
      v-model="showCreateProjectDialog"
      :title="$t('dashboard.newProjectDialog.title')"
      width="650px"
      :close-on-click-modal="false"
      center
      class="create-project-dialog"
    >
      <el-form :model="projectForm" label-position="top" class="project-form">
        <!-- 项目基础信息 -->
        <el-form-item :label="$t('dashboard.newProjectDialog.projectName')" required>
          <el-input
            v-model="projectForm.name"
            :placeholder="$t('dashboard.newProjectDialog.projectNamePlaceholder')"
            size="large"
            clearable
          />
        </el-form-item>
        
        <el-form-item :label="$t('dashboard.newProjectDialog.description')">
          <el-input
            v-model="projectForm.description"
            :placeholder="$t('dashboard.newProjectDialog.descriptionPlaceholder')"
            type="textarea"
            :rows="2"
            clearable
          />
        </el-form-item>
        
        <!-- 数据源选择 -->
        <el-form-item :label="$t('dashboard.newProjectDialog.dataSource')" required>
          <el-radio-group v-model="projectForm.dataSource" size="large">
            <el-radio-button label="local">
              <Icon icon="ph:folder" :width="16" class="mr-1" />
              {{ $t('dashboard.newProjectDialog.localFiles') }}
            </el-radio-button>
            <el-radio-button label="remote">
              <Icon icon="ph:link" :width="16" class="mr-1" />
              {{ $t('dashboard.newProjectDialog.remoteUrl') }}
            </el-radio-button>
          </el-radio-group>
        </el-form-item>
        
        <!-- 本地文件上传 -->
        <el-form-item v-if="projectForm.dataSource === 'local'" :label="$t('dashboard.newProjectDialog.uploadData')" required>
          <div class="upload-zone" @click="triggerFileUpload">
            <input
              ref="fileInputRef"
              type="file"
              multiple
              accept="image/*"
              style="display: none"
              @change="handleFileSelect"
            />
            <Icon icon="ph:upload-simple" :width="32" class="upload-icon" />
            <p class="upload-text">{{ $t('dashboard.newProjectDialog.uploadDescription') }}</p>
            <p v-if="projectForm.uploadedFiles.length > 0" class="upload-count">
              {{ projectForm.uploadedFiles.length }} file(s) selected
            </p>
          </div>
          
          <!-- 已上传文件列表 -->
          <div v-if="projectForm.uploadedFiles.length > 0" class="uploaded-files">
            <div v-for="(file, index) in projectForm.uploadedFiles.slice(0, 5)" :key="index" class="file-item">
              <Icon icon="ph:file-image" :width="16" />
              <span class="file-name">{{ file.name }}</span>
              <el-button
                type="text"
                size="small"
                @click.stop="removeUploadedFile(index)"
              >
                <Icon icon="ph:x" :width="14" />
              </el-button>
            </div>
            <p v-if="projectForm.uploadedFiles.length > 5" class="more-files">
              +{{ projectForm.uploadedFiles.length - 5 }} more files
            </p>
          </div>
        </el-form-item>
        
        <!-- 远程URL -->
        <el-form-item v-else :label="$t('dashboard.newProjectDialog.remoteUrl')" required>
          <el-input
            v-model="projectForm.remoteUrl"
            placeholder="https://example.com/dataset.zip"
            size="large"
          >
            <template #prefix>
              <Icon icon="ph:link" :width="16" />
            </template>
          </el-input>
        </el-form-item>
        
        <!-- 模型选择 -->
        <el-form-item :label="$t('dashboard.newProjectDialog.modelSelection')" required>
          <el-select v-model="projectForm.modelType" size="large" style="width: 100%">
            <el-option value="yolov8n" :label="$t('dashboard.newProjectDialog.yolov8n')" />
            <el-option value="yolov8s" :label="$t('dashboard.newProjectDialog.yolov8s')" />
            <el-option value="yolov8m" :label="$t('dashboard.newProjectDialog.yolov8m')" />
            <el-option value="yolov8l" :label="$t('dashboard.newProjectDialog.yolov8l')" />
          </el-select>
        </el-form-item>
        
        <!-- 自定义权重文件 -->
        <el-form-item :label="$t('dashboard.newProjectDialog.customWeights')">
          <el-button @click="triggerWeightsUpload" size="large" style="width: 100%">
            <input
              ref="weightsInputRef"
              type="file"
              accept=".pt,.pth"
              style="display: none"
              @change="handleWeightsSelect"
            />
            <Icon icon="ph:upload" :width="16" class="mr-2" />
            {{ projectForm.customWeights ? projectForm.customWeights.name : $t('dashboard.newProjectDialog.uploadWeights') }}
          </el-button>
          <el-button
            v-if="projectForm.customWeights"
            type="text"
            size="small"
            @click="removeCustomWeights"
            class="mt-1"
          >
            <Icon icon="ph:x" :width="14" class="mr-1" />
            Remove
          </el-button>
        </el-form-item>
        
        <!-- 高级设置 -->
        <el-collapse class="advanced-settings">
          <el-collapse-item :title="$t('dashboard.newProjectDialog.advancedSettings')">
            <el-form-item :label="$t('dashboard.newProjectDialog.batchSize')">
              <el-input-number v-model="projectForm.batchSize" :min="1" :max="128" size="large" />
            </el-form-item>
            
            <el-form-item :label="$t('dashboard.newProjectDialog.learningRate')">
              <el-input-number v-model="projectForm.learningRate" :min="0.0001" :max="1" :step="0.0001" size="large" />
            </el-form-item>
            
            <el-form-item :label="$t('dashboard.newProjectDialog.maxIterations')">
              <el-input-number v-model="projectForm.maxIterations" :min="1" :max="1000" size="large" />
            </el-form-item>
          </el-collapse-item>
        </el-collapse>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateProjectDialog = false" size="large">
            {{ $t('dashboard.newProjectDialog.cancel') }}
          </el-button>
          <el-button 
            type="primary" 
            size="large"
            @click="createProject"
            :loading="isCreatingProject"
            :disabled="!projectForm.name.trim()"
          >
            <Icon v-if="!isCreatingProject" icon="ph:plus-circle" :width="18" class="mr-2" />
            {{ isCreatingProject ? $t('dashboard.newProjectDialog.creating') : $t('dashboard.newProjectDialog.create') }}
          </el-button>
        </div>
      </template>
    </el-dialog>

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

// Create Project Dialog
.create-project-dialog {
  .project-form {
    max-height: 60vh;
    overflow-y: auto;
    @include custom-scrollbar;
    padding-right: $spacing-sm;
  }
  
  .upload-zone {
    border: 2px dashed var(--color-border);
    border-radius: $radius-lg;
    padding: $spacing-2xl;
    text-align: center;
    cursor: pointer;
    transition: all $transition-base;
    background: var(--color-surface-elevated);
    
    &:hover {
      border-color: var(--color-primary);
      background: var(--color-surface);
      transform: translateY(-2px);
      box-shadow: $shadow-md;
    }
    
    .upload-icon {
      color: var(--color-primary);
      margin-bottom: $spacing-sm;
    }
    
    .upload-text {
      font-size: $font-size-sm;
      color: var(--color-text-secondary);
      margin: 0;
    }
    
    .upload-count {
      font-size: $font-size-sm;
      color: var(--color-primary);
      font-weight: $font-weight-medium;
      margin-top: $spacing-xs;
      margin-bottom: 0;
    }
  }
  
  .uploaded-files {
    margin-top: $spacing-md;
    max-height: 200px;
    overflow-y: auto;
    @include custom-scrollbar;
    
    .file-item {
      display: flex;
      align-items: center;
      gap: $spacing-sm;
      padding: $spacing-sm;
      background: var(--color-surface-elevated);
      border-radius: $radius-md;
      margin-bottom: $spacing-xs;
      transition: all $transition-base;
      
      &:hover {
        background: var(--color-surface);
        transform: translateX(4px);
      }
      
      .file-name {
        flex: 1;
        font-size: $font-size-sm;
        color: var(--color-text-primary);
        @include truncate;
      }
    }
    
    .more-files {
      font-size: $font-size-xs;
      color: var(--color-text-tertiary);
      text-align: center;
      margin-top: $spacing-sm;
      margin-bottom: 0;
    }
  }
  
  .advanced-settings {
    margin-top: $spacing-lg;
    border: 1px solid var(--color-border);
    border-radius: $radius-md;
    background: var(--color-surface-elevated);
    
    :deep(.el-collapse-item__header) {
      padding: $spacing-md;
      font-weight: $font-weight-medium;
      color: var(--color-text-secondary);
      transition: all $transition-base;
      
      &:hover {
        color: var(--color-primary);
      }
    }
    
    :deep(.el-collapse-item__content) {
      padding: $spacing-md;
    }
  }
  
  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: $spacing-md;
  }
}
</style>

