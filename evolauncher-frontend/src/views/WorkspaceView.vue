<script setup lang="ts">
/**
 * Workspace View
 * 
 * Design Philosophy:
 * - Three-column layout for monitoring active learning workflow
 * - Real-time job status updates with smooth step transitions
 * - Animated progress indicators using GSAP
 * - Live log streaming for transparency
 * 
 * Key Features:
 * - Evolution Task Monitor with animated step progression
 * - Real-time metrics visualization
 * - Live log output
 * - Job control buttons
 * 
 * Animation Strategy:
 * - Smooth step transitions with indicator movement
 * - Progress bars animate with easing
 * - New log entries fade in from top
 */

import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import gsap from 'gsap'
import AnimatedCard from '@/components/common/AnimatedCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import { createJobStatusStream, type JobStatus, type JobStep } from '@/mock/jobStatus'
import { fetchAgentStatuses, type AgentStatus } from '@/mock/agents'
import { fetchMcpToolStatus, type McpToolStatus } from '@/mock/mcpTools'
import { ElNotification } from 'element-plus'

const { t } = useI18n()

const currentJob = ref<JobStatus | null>(null)
const stopStream = ref<(() => void) | null>(null)
const agentTelemetry = ref<AgentStatus[]>([])
const mcpRegistry = ref<McpToolStatus[]>([])
const isLoadingAgents = ref(true)
const isLoadingMcp = ref(true)
const stepsContainer = ref<HTMLElement | null>(null)
const stepHighlight = ref<HTMLElement | null>(null)

// 当前项目信息（从路由获取）
const router = useRouter()
const route = useRoute()
const currentProject = ref({
  id: route.params.id || '2',
  name: '医学影像数据集',
  status: 'training' as const
})

// Loss数据 - 模拟训练损失曲线
const lossData = ref({
  epochs: Array.from({ length: 50 }, (_, i) => i + 1),
  trainLoss: Array.from({ length: 50 }, (_, i) => {
    const base = 2.5
    const decay = Math.exp(-i / 15)
    const noise = (Math.random() - 0.5) * 0.1
    return Math.max(0.1, base * decay + noise)
  }),
  valLoss: Array.from({ length: 50 }, (_, i) => {
    const base = 2.8
    const decay = Math.exp(-i / 18)
    const noise = (Math.random() - 0.5) * 0.15
    return Math.max(0.15, base * decay + noise)
  })
})

// Step configuration
const steps = ref<Array<{ key: JobStep; label: string; icon: string }>>([
  { key: 'initialization', label: t('steps.initialization'), icon: 'ph:gear' },
  { key: 'data_preparation', label: t('steps.dataPreparation'), icon: 'ph:database' },
  { key: 'model_training', label: t('steps.modelTraining'), icon: 'ph:brain' },
  { key: 'active_learning', label: t('steps.activeLearning'), icon: 'ph:arrows-clockwise' },
  { key: 'inference', label: t('steps.inference'), icon: 'ph:lightning' },
  { key: 'completed', label: t('steps.completed'), icon: 'ph:check-circle' }
])

const currentStepIndex = ref(0)

/**
 * Start job monitoring
 * Creates a stream that updates job status every 2 seconds
 */
const startJobMonitoring = () => {
  stopStream.value = createJobStatusStream((status: JobStatus) => {
    currentJob.value = status
    
    // Update current step index
    const stepIndex = steps.value.findIndex(s => s.key === status.currentStep)
    if (stepIndex !== -1 && stepIndex !== currentStepIndex.value) {
      animateStepTransition(stepIndex)
    }
  }, 2000)
}

/**
 * Animate step transition using GSAP
 * 
 * Design Intent: When the job progresses to a new step, animate the
 * active indicator smoothly to the new position. This creates a sense
 * of continuous progress rather than discrete jumps.
 */
const animateStepTransition = (newIndex: number) => {
  const oldIndex = currentStepIndex.value
  currentStepIndex.value = newIndex
  
  requestAnimationFrame(() => {
    highlightStep(newIndex)
  })
}

const highlightStep = (index: number) => {
  if (!stepsContainer.value || !stepHighlight.value) {
    return
  }

  const stepElements = stepsContainer.value.querySelectorAll('.el-step')
  const target = stepElements[index] as HTMLElement | undefined

  if (!target) {
    return
  }

  const containerRect = stepsContainer.value.getBoundingClientRect()
  const targetRect = target.getBoundingClientRect()
  const offsetY = targetRect.top - containerRect.top

  gsap.to(stepHighlight.value, {
    y: offsetY,
    height: targetRect.height,
    duration: 0.6,
    ease: 'power3.out'
  })

  gsap.fromTo(
    target,
    { scale: 0.98 },
    {
      scale: 1,
      duration: 0.4,
      ease: 'back.out(1.6)'
    }
  )
}

const handleResize = () => {
  requestAnimationFrame(() => highlightStep(currentStepIndex.value))
}

/**
 * Stop job monitoring
 */
const stopJobMonitoring = () => {
  if (stopStream.value) {
    stopStream.value()
    stopStream.value = null
  }
}

// Watch for job completion
watch(() => currentJob.value?.status, (status) => {
  if (status === 'completed') {
    setTimeout(() => {
      stopJobMonitoring()
    }, 3000)
  }
})

onMounted(() => {
  startJobMonitoring()
  loadAgentTelemetry()
  loadMcpRegistry()

  nextTick(() => {
    highlightStep(currentStepIndex.value)
  })

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  stopJobMonitoring()
  window.removeEventListener('resize', handleResize)
})

const formatTime = (isoString?: string) => {
  if (!isoString) return 'N/A'
  const date = new Date(isoString)
  return date.toLocaleTimeString()
}

const loadAgentTelemetry = async () => {
  isLoadingAgents.value = true
  try {
    agentTelemetry.value = await fetchAgentStatuses()
    await nextTick()
    animateAgentTelemetry()
  } catch (error) {
    console.error('Agent telemetry error', error)
    ElNotification.warning({
      title: 'Agents',
      message: 'Unable to sync agent telemetry snapshot.'
    })
  } finally {
    isLoadingAgents.value = false
  }
}

const animateAgentTelemetry = () => {
  const cards = document.querySelectorAll('.agent-telemetry-card')
  gsap.fromTo(
    cards,
    { opacity: 0, y: 20 },
    {
      opacity: 1,
      y: 0,
      duration: 0.4,
      stagger: 0.1,
      ease: 'power3.out',
      clearProps: 'all'
    }
  )
}

const loadMcpRegistry = async () => {
  isLoadingMcp.value = true
  try {
    mcpRegistry.value = await fetchMcpToolStatus()
    await nextTick()
    animateMcpList()
  } catch (error) {
    console.error('MCP registry error', error)
    ElNotification.error({
      title: 'MCP Tools',
      message: 'Failed to query MCP tool registry.'
    })
  } finally {
    isLoadingMcp.value = false
  }
}

const animateMcpList = () => {
  const rows = document.querySelectorAll('.mcp-row')
  gsap.fromTo(
    rows,
    { opacity: 0, x: -12 },
    {
      opacity: 1,
      x: 0,
      duration: 0.35,
      stagger: 0.06,
      ease: 'power2.out',
      clearProps: 'all'
    }
  )
}
</script>

<template>
  <div class="workspace-view">
    <!-- Header -->
    <div class="workspace-header">
      <div class="header-main">
        <div class="project-badge">
          <Icon icon="ph:folder-open-fill" :width="20" />
          <span>当前项目</span>
        </div>
        <h1 class="workspace-title">{{ currentProject.name }}</h1>
        <p class="workspace-subtitle">{{ $t('workspace.subtitle') }}</p>
      </div>
      
      <div v-if="currentJob" class="job-controls">
        <el-button size="large">
          <Icon icon="ph:pause" :width="20" class="mr-2" />
          {{ $t('workspace.pauseJob') }}
        </el-button>
        <el-button size="large" type="danger">
          <Icon icon="ph:stop" :width="20" class="mr-2" />
          {{ $t('workspace.stopJob') }}
        </el-button>
      </div>
    </div>
    
    <!-- Main Content -->
    <div class="workspace-content">
      <!-- Left Column: Evolution Task Monitor -->
      <AnimatedCard class="monitor-card" :hoverable="false">
        <h2 class="card-title">
          <Icon icon="ph:flow-arrow" :width="24" class="mr-2" />
          {{ $t('workspace.evolutionMonitor') }}
        </h2>
        
        <div class="steps-container" ref="stepsContainer">
          <div class="steps-highlight" ref="stepHighlight"></div>

          <el-steps
            class="monitor-steps"
            direction="vertical"
            :active="currentStepIndex"
            finish-status="success"
          >
            <el-step
              v-for="(step, index) in steps"
              :key="step.key"
              :title="step.label"
              :class="{
                'is-current': currentJob && currentJob.currentStep === step.key,
                'is-complete': currentJob && steps.findIndex(s => s.key === currentJob.currentStep) > index
              }"
            >
              <template #icon>
                <div class="step-icon-wrapper">
                  <Icon :icon="step.icon" :width="18" />
                </div>
              </template>
              <template #description>
                <div class="step-description">
                  <div
                    v-if="currentJob && step.key === currentJob.currentStep"
                    class="step-progress"
                  >
                    <el-progress
                      :percentage="currentJob.progress"
                      :show-text="false"
                      :stroke-width="4"
                    />
                  </div>
                  <div v-else class="step-placeholder">
                    <span v-if="currentJob && steps.findIndex(s => s.key === currentJob.currentStep) > index">
                      {{ $t('workspace.completedViaResidual') }}
                    </span>
                    <span v-else>
                      {{ $t('workspace.pendingExecution') }}
                    </span>
                  </div>
                </div>
              </template>
            </el-step>
          </el-steps>
        </div>
      </AnimatedCard>
      
      <!-- Middle Column: Loss Chart & Metrics -->
      <div class="middle-column">
        <!-- Loss Chart Card -->
        <AnimatedCard class="loss-chart-card" :hoverable="false">
          <h2 class="card-title">
            <Icon icon="ph:chart-line" :width="24" class="mr-2" />
            训练损失曲线
          </h2>
          
          <div class="chart-container">
            <svg viewBox="0 0 600 240" class="loss-chart-svg">
              <!-- 背景网格 -->
              <defs>
                <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" style="stop-color:#4A69FF;stop-opacity:0.3" />
                  <stop offset="100%" style="stop-color:#4A69FF;stop-opacity:0.05" />
                </linearGradient>
              </defs>
              
              <!-- 网格线 -->
              <g class="grid-lines">
                <line v-for="i in 5" :key="`h${i}`" 
                  x1="50" :y1="30 + (i - 1) * 40" 
                  x2="560" :y2="30 + (i - 1) * 40" 
                  stroke="var(--color-border)" 
                  stroke-width="1" 
                  opacity="0.3" />
                <line v-for="i in 10" :key="`v${i}`" 
                  :x1="50 + (i - 1) * 57" y1="30" 
                  :x2="50 + (i - 1) * 57" y2="190" 
                  stroke="var(--color-border)" 
                  stroke-width="1" 
                  opacity="0.3" />
              </g>
              
              <!-- 训练损失曲线区域填充 -->
              <path
                :d="`M 50,190 ${lossData.epochs.map((e, i) => 
                  `L ${50 + (i / 49) * 510},${190 - (lossData.trainLoss[i] / 2.5) * 160}`
                ).join(' ')} L 560,190 Z`"
                fill="url(#chartGradient)"
              />
              
              <!-- 训练损失曲线 -->
              <polyline
                :points="lossData.epochs.map((e, i) => 
                  `${50 + (i / 49) * 510},${190 - (lossData.trainLoss[i] / 2.5) * 160}`
                ).join(' ')"
                fill="none"
                stroke="#4A69FF"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              
              <!-- 验证损失曲线 -->
              <polyline
                :points="lossData.epochs.map((e, i) => 
                  `${50 + (i / 49) * 510},${190 - (lossData.valLoss[i] / 2.5) * 160}`
                ).join(' ')"
                fill="none"
                stroke="#10B981"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-dasharray="6,3"
              />
              
              <!-- 坐标轴 -->
              <line x1="50" y1="190" x2="560" y2="190" stroke="var(--color-text-secondary)" stroke-width="1.5" />
              <line x1="50" y1="30" x2="50" y2="190" stroke="var(--color-text-secondary)" stroke-width="1.5" />
              
              <!-- 轴标签 -->
              <text x="305" y="215" text-anchor="middle" fill="var(--color-text-secondary)" font-size="12">训练轮次 (Epochs)</text>
              <text x="20" y="110" text-anchor="middle" fill="var(--color-text-secondary)" font-size="12" transform="rotate(-90, 20, 110)">Loss</text>
            </svg>
            
            <!-- 图例 -->
            <div class="chart-legend">
              <div class="legend-item">
                <div class="legend-line train"></div>
                <span class="legend-label">训练损失</span>
                <span class="legend-value">{{ lossData.trainLoss[lossData.trainLoss.length - 1].toFixed(3) }}</span>
              </div>
              <div class="legend-item">
                <div class="legend-line val"></div>
                <span class="legend-label">验证损失</span>
                <span class="legend-value">{{ lossData.valLoss[lossData.valLoss.length - 1].toFixed(3) }}</span>
              </div>
            </div>
          </div>
        </AnimatedCard>
        
        <!-- Job Details Card -->
        <AnimatedCard class="details-card" :hoverable="false">
          <h2 class="card-title">
            <Icon icon="ph:info" :width="24" class="mr-2" />
            {{ $t('workspace.jobDetails') }}
          </h2>
          
          <div v-if="currentJob" class="job-details">
            <div class="detail-row">
              <span class="detail-label">{{ $t('workspace.status') }}:</span>
              <StatusBadge :status="currentJob.status" />
            </div>
            <div class="detail-row">
              <span class="detail-label">{{ $t('workspace.progress') }}:</span>
              <span class="detail-value">{{ currentJob.progress.toFixed(1) }}%</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">{{ $t('common.started') }}:</span>
              <span class="detail-value">{{ formatTime(currentJob.startedAt) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">{{ $t('workspace.estimatedTime') }}:</span>
              <span class="detail-value">{{ formatTime(currentJob.estimatedCompletion) }}</span>
            </div>
          </div>
        </AnimatedCard>
        
        <AnimatedCard class="metrics-card" :hoverable="false">
          <h2 class="card-title">
            <Icon icon="ph:chart-bar" :width="24" class="mr-2" />
            {{ $t('workspace.metrics') }}
          </h2>
          
          <div v-if="currentJob?.metrics" class="metrics-grid">
            <div class="metric-item">
              <div class="metric-label">{{ $t('common.accuracy') }}</div>
              <div class="metric-value">
                {{ (currentJob.metrics.accuracy! * 100).toFixed(1) }}%
              </div>
            </div>
            <div class="metric-item">
              <div class="metric-label">{{ $t('common.loss') }}</div>
              <div class="metric-value">
                {{ currentJob.metrics.loss?.toFixed(3) }}
              </div>
            </div>
            <div class="metric-item">
              <div class="metric-label">{{ $t('common.samples') }}</div>
              <div class="metric-value">
                {{ currentJob.metrics.samplesProcessed }} / {{ currentJob.metrics.totalSamples }}
              </div>
            </div>
          </div>
        </AnimatedCard>
      </div>
      
      <!-- Right Column: Logs -->
      <AnimatedCard class="logs-card" :hoverable="false">
        <h2 class="card-title">
          <Icon icon="ph:terminal-window" :width="24" class="mr-2" />
          {{ $t('workspace.logs') }}
        </h2>
        
        <div class="logs-container">
          <div
            v-for="(log, index) in currentJob?.logs || []"
            :key="index"
            class="log-entry"
          >
            {{ log }}
          </div>
        </div>
      </AnimatedCard>
    </div>

    <div class="workspace-secondary">
      <AnimatedCard class="agent-telemetry-panel" :hoverable="false">
        <div class="panel-header">
          <div>
            <h2 class="panel-title">
              <Icon icon="ph:circles-three-plus" :width="22" class="mr-2" />
              {{ $t('workspace.agentTelemetry') }}
            </h2>
            <p class="panel-subtitle">
              {{ $t('workspace.residualConnections') }}
            </p>
          </div>
          <el-tag size="large" type="primary" effect="dark">
            {{ agentTelemetry.length }} {{ $t('common.active') }}
          </el-tag>
        </div>

        <div class="agent-telemetry-grid">
          <div
            v-if="isLoadingAgents"
            v-for="i in 4"
            :key="`agent-loader-${i}`"
            class="agent-telemetry-card skeleton"
          >
            <LoadingSkeleton type="title" width="50%" />
            <LoadingSkeleton type="text" width="80%" count="2" />
          </div>

          <div
            v-else
            v-for="agent in agentTelemetry"
            :key="agent.id"
            class="agent-telemetry-card"
          >
            <div class="agent-telemetry-header">
              <div>
                <h3>{{ agent.displayName }}</h3>
                <span class="agent-tag">{{ agent.name }}</span>
              </div>
              <StatusBadge
                :status="agent.status === 'waiting' ? 'idle' : agent.status"
                :size="'small'"
              />
            </div>
            <p class="agent-telemetry-description">
              {{ agent.description }}
            </p>

            <div class="agent-telemetry-stats">
              <div>
                <span class="stat-label">{{ $t('agent.metrics.confidence') }}</span>
                <span class="stat-value">{{ Math.round(agent.confidence * 100) }}%</span>
              </div>
              <div>
                <span class="stat-label">{{ $t('agent.metrics.throughput') }}</span>
                <span class="stat-value">{{ agent.throughput }}/min</span>
              </div>
              <div>
                <span class="stat-label">{{ $t('agent.processed') }}</span>
                <span class="stat-value">{{ agent.metrics.processed }}</span>
              </div>
            </div>

            <div class="agent-telemetry-footnote">
              <div>
                <span class="footnote-label">{{ $t('agent.lastTask') }}</span>
                <p>{{ agent.lastTask }}</p>
              </div>
              <div>
                <span class="footnote-label">{{ $t('agent.nextAction') }}</span>
                <p>{{ agent.nextAction }}</p>
              </div>
            </div>
          </div>
        </div>
      </AnimatedCard>

      <AnimatedCard class="mcp-panel" :hoverable="false">
        <div class="panel-header">
          <div>
            <h2 class="panel-title">
              <Icon icon="ph:factory" :width="22" class="mr-2" />
              {{ $t('workspace.mcpToolRegistry') }}
            </h2>
            <p class="panel-subtitle">
              通过模型上下文协议 (MCP) 编排工具，实现一致的自动化
            </p>
          </div>
          <el-tag size="large" effect="dark">
            {{ $t('workspace.toolCount', { count: mcpRegistry.length }) }}
          </el-tag>
        </div>

        <div class="mcp-table">
          <div class="mcp-row header">
            <span>{{ $t('mcp.tool') }}</span>
            <span>{{ $t('workspace.latency') }}</span>
            <span>{{ $t('mcp.usage') }}</span>
            <span>{{ $t('mcp.status') }}</span>
          </div>

          <div
            v-if="isLoadingMcp"
            v-for="i in 4"
            :key="`mcp-skeleton-${i}`"
            class="mcp-row"
          >
            <LoadingSkeleton type="text" width="60%" />
          </div>

          <div
            v-else
            v-for="tool in mcpRegistry"
            :key="tool.id"
            class="mcp-row"
          >
            <div>
              <span class="mcp-name">{{ tool.name }}</span>
              <p class="mcp-description">{{ tool.description }}</p>
            </div>
            <span>{{ tool.latency }} ms</span>
            <span>{{ tool.usage }}%</span>
            <el-tag
              :type="tool.status === 'online' ? 'success' : tool.status === 'degraded' ? 'warning' : 'danger'"
              effect="dark"
            >
              {{ tool.status }}
            </el-tag>
          </div>
        </div>
      </AnimatedCard>
    </div>
  </div>
</template>

<style scoped lang="scss">
.workspace-view {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: $spacing-2xl;
  overflow-y: auto;
  overflow-x: hidden;
  @include custom-scrollbar;
  
  // 响应式设计
  @media (max-width: 1024px) {
    padding: $spacing-xl;
  }
  
  @media (max-width: 768px) {
    padding: $spacing-lg;
  }
}

// Header
.workspace-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacing-2xl;
  flex-shrink: 0;
  gap: $spacing-md;
  
  // 小屏幕：堆叠布局
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: stretch;
    margin-bottom: $spacing-lg;
  }
}

.header-main {
  flex: 1;
}

.project-badge {
  display: inline-flex;
  align-items: center;
  gap: $spacing-xs;
  padding: $spacing-xs $spacing-md;
  background: rgba(74, 105, 255, 0.1);
  border-radius: $radius-full;
  font-size: $font-size-sm;
  font-weight: $font-weight-medium;
  color: var(--color-primary);
  margin-bottom: $spacing-sm;
}

.workspace-title {
  font-size: $font-size-4xl;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  margin: 0 0 $spacing-xs 0;
}

.workspace-subtitle {
  font-size: $font-size-base;
  color: var(--color-text-secondary);
  margin: 0;
}

.job-controls {
  display: flex;
  gap: $spacing-md;
  flex-wrap: wrap;
  
  // 小屏幕：按钮占满宽度
  @media (max-width: 768px) {
    width: 100%;
    
    > button {
      flex: 1;
      min-width: 120px;
    }
  }
}

// Main Content - 紧凑网格布局
.workspace-content {
  display: grid;
  grid-template-columns: 320px 1fr 360px;
  grid-template-rows: auto auto;
  gap: $spacing-lg;
  width: 100%;
  align-items: start;
  
  .monitor-card {
    grid-row: 1 / 3;
  }
  
  .middle-column {
    grid-row: 1 / 3;
    display: grid;
    grid-template-rows: auto auto auto;
    gap: $spacing-lg;
  }
  
  .logs-card {
    grid-row: 1 / 3;
  }
  
  // 中等屏幕：2列布局
  @media (max-width: 1440px) {
    grid-template-columns: 280px 1fr;
    gap: $spacing-lg;
    
    .monitor-card {
      grid-row: 1 / 2;
    }
    
    .middle-column {
      grid-column: 2;
      grid-row: 1 / 2;
    }
    
    .logs-card {
      grid-column: 1 / -1;
      grid-row: 2 / 3;
    }
  }
  
  // 小屏幕：单列布局
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    gap: $spacing-lg;
    
    .monitor-card,
    .middle-column,
    .logs-card {
      grid-column: 1;
      grid-row: auto;
    }
  }
  
  @media (max-width: 768px) {
    gap: $spacing-md;
  }
}

// Cards
.card-title {
  display: flex;
  align-items: center;
  font-size: $font-size-xl;
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
  margin-bottom: $spacing-lg;
}

.monitor-card,
.logs-card {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
  min-height: 0;
}

// Loss Chart Card
.loss-chart-card {
  .card-title {
    margin-bottom: $spacing-md;
  }
}

.chart-container {
  width: 100%;
}

.loss-chart-svg {
  width: 100%;
  height: 240px;
  display: block;
  margin-bottom: $spacing-sm;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: $spacing-xl;
  padding-top: $spacing-sm;
  border-top: 1px solid var(--color-border);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

.legend-line {
  width: 24px;
  height: 3px;
  border-radius: 2px;
  
  &.train {
    background: #4A69FF;
  }
  
  &.val {
    background: #10B981;
    position: relative;
    
    &::before,
    &::after {
      content: '';
      position: absolute;
      width: 6px;
      height: 3px;
      background: var(--color-surface);
    }
    
    &::before {
      left: 4px;
    }
    
    &::after {
      left: 14px;
    }
  }
}

.legend-label {
  font-size: $font-size-xs;
  color: var(--color-text-secondary);
}

.legend-value {
  font-size: $font-size-sm;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  margin-left: $spacing-xs;
}

// Evolution Steps
.steps-container {
  position: relative;
  flex: 1;
  padding-left: $spacing-sm;
  overflow-y: auto;
  max-height: 600px;
  @include custom-scrollbar;
  
  @media (max-width: 1024px) {
    max-height: 400px;
  }
}

.steps-highlight {
  position: absolute;
  left: 10px;
  top: 12px;
  width: 4px;
  height: 70px;
  border-radius: $radius-full;
  background: linear-gradient(180deg, var(--color-primary), rgba(74, 105, 255, 0.1));
  transform: translateY(0);
  z-index: 0;
}

:deep(.monitor-steps) {
  position: relative;
  padding-left: $spacing-lg;
}

:deep(.monitor-steps .el-step) {
  margin-bottom: $spacing-lg;
  transition: transform $transition-base;
}

:deep(.monitor-steps .el-step__head) {
  z-index: 1;
}

.step-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: $radius-full;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface-elevated);
  border: 2px solid var(--color-border);
  transition: all $transition-base;
  color: var(--color-text-secondary);
}

:deep(.monitor-steps .el-step.is-current .step-icon-wrapper) {
  background: var(--color-primary);
  color: white;
  box-shadow: 0 0 20px rgba(74, 105, 255, 0.35);
}

:deep(.monitor-steps .el-step.is-complete .step-icon-wrapper) {
  background: var(--color-success);
  color: white;
  border-color: transparent;
}

:deep(.monitor-steps .el-step__title) {
  font-weight: $font-weight-semibold;
  font-size: $font-size-base;
  color: var(--color-text-secondary);
}

:deep(.monitor-steps .el-step.is-current .el-step__title) {
  color: var(--color-text-primary);
}

:deep(.monitor-steps .el-step.is-complete .el-step__title) {
  color: var(--color-text-secondary);
  opacity: 0.9;
}

.step-description {
  margin-top: $spacing-sm;
  padding-left: $spacing-sm;
}

.step-progress {
  margin-top: $spacing-sm;
}

.step-placeholder {
  font-size: $font-size-xs;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

// Job Details
.job-details {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-sm 0;
  border-bottom: 1px solid var(--color-border);
  
  &:last-child {
    border-bottom: none;
  }
}

.detail-label {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  font-weight: $font-weight-medium;
}

.detail-value {
  font-size: $font-size-base;
  color: var(--color-text-primary);
  font-weight: $font-weight-semibold;
}

// Metrics
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $spacing-lg;
  
  // 小屏幕：单列布局
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: $spacing-md;
  }
}

.metric-item {
  text-align: center;
  padding: $spacing-lg;
  background: var(--color-surface-elevated);
  border-radius: $radius-lg;
  transition: all $transition-base;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: $shadow-md;
  }
}

.metric-label {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  margin-bottom: $spacing-xs;
}

.metric-value {
  font-size: $font-size-2xl;
  font-weight: $font-weight-bold;
  color: var(--color-primary);
}

// Logs
.logs-container {
  flex: 1;
  overflow-y: auto;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: $font-size-sm;
  background: var(--color-bg);
  border-radius: $radius-md;
  padding: $spacing-md;
  height: 300px;
  @include custom-scrollbar;
  
  @media (max-width: 1440px) {
    height: 240px;
  }
  
  @media (max-width: 1024px) {
    height: 280px;
  }
}

.log-entry {
  padding: $spacing-xs 0;
  color: var(--color-text-secondary);
  line-height: 1.6;
  animation: slideDown 0.3s ease;
  
  &:hover {
    color: var(--color-text-primary);
    background: var(--color-surface-elevated);
    padding-left: $spacing-sm;
    margin-left: -$spacing-sm;
    border-radius: $radius-sm;
  }
}

// Utility
.mr-2 {
  margin-right: $spacing-xs;
}

.workspace-secondary {
  margin-top: $spacing-xl;
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: $spacing-lg;
  align-items: start;
  
  // 小屏幕：单列布局
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    gap: $spacing-lg;
  }
  
  @media (max-width: 768px) {
    gap: $spacing-md;
  }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: $spacing-md;
  margin-bottom: $spacing-lg;
}

.panel-title {
  font-size: $font-size-xl;
  font-weight: $font-weight-semibold;
  margin: 0;
  display: flex;
  align-items: center;
  color: var(--color-text-primary);
}

.panel-subtitle {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  margin-top: $spacing-xs;
}

.agent-telemetry-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: $spacing-lg;
  
  // 大屏幕：3列布局
  @media (min-width: 1600px) {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  
  // 中等屏幕：2列布局
  @media (max-width: 1440px) and (min-width: 769px) {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: $spacing-md;
  }
  
  // 小屏幕：单列布局
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: $spacing-md;
  }
}

.agent-telemetry-card {
  background: var(--color-surface-elevated);
  border-radius: $radius-lg;
  padding: $spacing-lg;
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
  transition: transform $transition-base, box-shadow $transition-base;

  &:hover {
    transform: translateY(-4px);
    box-shadow: $shadow-lg;
  }

  &.skeleton {
    background: transparent;
    box-shadow: none;
    transform: none;
  }
}

.agent-telemetry-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.agent-telemetry-header h3 {
  margin: 0;
  font-size: $font-size-lg;
  color: var(--color-text-primary);
}

.agent-tag {
  font-size: $font-size-xs;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.agent-telemetry-description {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  margin: 0;
  @include line-clamp(2); // 限制最多2行
  word-break: break-word;
}

.agent-telemetry-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: $spacing-sm;
  margin-top: $spacing-sm;
  
  // 小屏幕：确保文字不会溢出
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 6px;
  }
}

.agent-telemetry-stats div {
  background: rgba(74, 105, 255, 0.08);
  border-radius: $radius-md;
  padding: $spacing-sm;
  display: flex;
  flex-direction: column;
  gap: 4px;

  .dark & {
    background: rgba(122, 162, 247, 0.12);
  }
}

.stat-label {
  font-size: $font-size-xs;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-value {
  font-size: $font-size-base;
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
}

.agent-telemetry-footnote {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: $spacing-md;
  margin-top: $spacing-sm;
}

.footnote-label {
  font-size: $font-size-xs;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.agent-telemetry-footnote p {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  margin: 0;
  @include truncate; // 单行截断
  word-break: break-word;
}

.agent-telemetry-panel,
.mcp-panel {
  display: flex;
  flex-direction: column;
  height: fit-content;
  min-height: 0;
}

.mcp-table {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.mcp-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr auto;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-sm $spacing-md;
  border-radius: $radius-md;
  background: rgba(124, 170, 255, 0.08);
  transition: transform $transition-base, box-shadow $transition-base;

  &:hover {
    transform: translateY(-2px);
    box-shadow: $shadow-md;
  }

  &.header {
    background: transparent;
    font-size: $font-size-xs;
    color: var(--color-text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
  
  // 小屏幕优化：堆叠布局
  @media (max-width: 768px) {
    grid-template-columns: 1fr auto;
    gap: $spacing-xs;
    padding: $spacing-sm;
    
    &.header {
      display: none; // 隐藏表头
    }
    
    > div:first-child {
      grid-column: 1 / -1;
    }
  }
}

.mcp-name {
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
  text-transform: capitalize;
}

.mcp-description {
  font-size: $font-size-xs;
  color: var(--color-text-secondary);
  margin: 0;
  @include truncate; // 单行截断
  word-break: break-word;
}
</style>


