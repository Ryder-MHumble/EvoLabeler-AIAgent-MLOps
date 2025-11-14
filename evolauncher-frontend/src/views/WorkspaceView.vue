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

// Loss数据 - 动态训练损失曲线
const lossData = ref({
  epochs: Array.from({ length: 100 }, (_, i) => i + 1),
  trainLoss: Array.from({ length: 100 }, (_, i) => {
    const base = 2.5
    const decay = Math.exp(-i / 15)
    const noise = (Math.random() - 0.5) * 0.1
    return Math.max(0.1, base * decay + noise)
  }),
  valLoss: Array.from({ length: 100 }, (_, i) => {
    const base = 2.8
    const decay = Math.exp(-i / 18)
    const noise = (Math.random() - 0.5) * 0.15
    return Math.max(0.15, base * decay + noise)
  })
})

const chartScrollRef = ref<HTMLElement | null>(null)
const visibleRange = ref({ start: 70, end: 100 }) // 显示最后30个数据点
const isDragging = ref(false)
const dragStart = ref({ x: 0, scrollLeft: 0 })

// 动态更新损失数据
let lossUpdateInterval: ReturnType<typeof setInterval> | null = null

const updateLossData = () => {
  if (!currentJob.value || currentJob.value.status !== 'running') return
  
  const currentEpoch = lossData.value.epochs.length
  const lastTrainLoss = lossData.value.trainLoss[lossData.value.trainLoss.length - 1]
  const lastValLoss = lossData.value.valLoss[lossData.value.valLoss.length - 1]
  
  // 添加新数据点（模拟训练进行）
  lossData.value.epochs.push(currentEpoch + 1)
  lossData.value.trainLoss.push(
    Math.max(0.05, lastTrainLoss - 0.01 + (Math.random() - 0.5) * 0.02)
  )
  lossData.value.valLoss.push(
    Math.max(0.05, lastValLoss - 0.008 + (Math.random() - 0.5) * 0.02)
  )
  
  // 保持最多200个数据点
  if (lossData.value.epochs.length > 200) {
    lossData.value.epochs.shift()
    lossData.value.trainLoss.shift()
    lossData.value.valLoss.shift()
  }
  
  // 自动滚动到最新位置
  if (chartScrollRef.value) {
    chartScrollRef.value.scrollLeft = chartScrollRef.value.scrollWidth
  }
  
  visibleRange.value = {
    start: Math.max(0, lossData.value.epochs.length - 30),
    end: lossData.value.epochs.length
  }
}

const startLossUpdate = () => {
  if (lossUpdateInterval) return
  lossUpdateInterval = setInterval(updateLossData, 2000) // 每2秒更新一次
}

const stopLossUpdate = () => {
  if (lossUpdateInterval) {
    clearInterval(lossUpdateInterval)
    lossUpdateInterval = null
  }
}

// 拖动处理
const handleMouseDown = (e: MouseEvent) => {
  if (!chartScrollRef.value) return
  isDragging.value = true
  dragStart.value = {
    x: e.pageX - chartScrollRef.value.offsetLeft,
    scrollLeft: chartScrollRef.value.scrollLeft
  }
  chartScrollRef.value.style.cursor = 'grabbing'
}

const handleMouseMove = (e: MouseEvent) => {
  if (!isDragging.value || !chartScrollRef.value) return
  e.preventDefault()
  const x = e.pageX - chartScrollRef.value.offsetLeft
  const walk = (x - dragStart.value.x) * 2
  chartScrollRef.value.scrollLeft = dragStart.value.scrollLeft - walk
}

const handleMouseUp = () => {
  isDragging.value = false
  if (chartScrollRef.value) {
    chartScrollRef.value.style.cursor = 'grab'
  }
}

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
    
    // 启动损失更新
    if (status.status === 'running' && stepIndex >= 2) {
      startLossUpdate()
    } else {
      stopLossUpdate()
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
    // 初始化滚动到最新位置
    if (chartScrollRef.value) {
      chartScrollRef.value.scrollLeft = chartScrollRef.value.scrollWidth
    }
  })

  window.addEventListener('resize', handleResize)
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
})

onUnmounted(() => {
  stopJobMonitoring()
  stopLossUpdate()
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
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
  const cards = document.querySelectorAll('.agent-card-modern:not(.skeleton)')
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
  const rows = document.querySelectorAll('.mcp-item-modern:not(.skeleton)')
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
    
    <!-- Main Content - 重构布局：指标为主，任务详情在侧 -->
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
      
      <!-- Middle Column: Metrics (Primary) + Loss Chart -->
      <div class="middle-column-primary">
        <!-- Metrics Card - 主要位置，更大更突出 -->
        <AnimatedCard class="metrics-card-primary" :hoverable="false">
          <div class="metrics-header-modern">
            <div class="metrics-header-left">
              <div class="metrics-icon-badge">
                <Icon icon="ph:chart-bar-fill" :width="24" />
              </div>
              <div>
                <h2 class="metrics-title-modern">核心指标</h2>
                <p class="metrics-subtitle-modern">实时训练性能监控</p>
              </div>
            </div>
          </div>
          
          <div v-if="currentJob?.metrics" class="metrics-grid-modern">
            <div class="metric-card-modern accuracy">
              <div class="metric-icon-wrapper">
                <Icon icon="ph:target-fill" :width="28" />
              </div>
              <div class="metric-content-modern">
                <div class="metric-label-modern">准确率</div>
                <div class="metric-value-modern">
                  {{ (currentJob.metrics.accuracy! * 100).toFixed(1) }}%
                </div>
                <div class="metric-trend">
                  <Icon icon="ph:arrow-up-right" :width="14" />
                  <span>+2.3%</span>
                </div>
              </div>
            </div>
            <div class="metric-card-modern loss">
              <div class="metric-icon-wrapper">
                <Icon icon="ph:trend-down-fill" :width="28" />
              </div>
              <div class="metric-content-modern">
                <div class="metric-label-modern">损失值</div>
                <div class="metric-value-modern">
                  {{ currentJob.metrics.loss?.toFixed(3) }}
                </div>
                <div class="metric-trend down">
                  <Icon icon="ph:arrow-down-right" :width="14" />
                  <span>-0.125</span>
                </div>
              </div>
            </div>
            <div class="metric-card-modern samples">
              <div class="metric-icon-wrapper">
                <Icon icon="ph:database-fill" :width="28" />
              </div>
              <div class="metric-content-modern">
                <div class="metric-label-modern">样本进度</div>
                <div class="metric-value-modern">
                  {{ currentJob.metrics.samplesProcessed }} / {{ currentJob.metrics.totalSamples }}
                </div>
                <div class="metric-progress-bar">
                  <div 
                    class="metric-progress-fill" 
                    :style="{ width: `${(currentJob.metrics.samplesProcessed / currentJob.metrics.totalSamples) * 100}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </AnimatedCard>
        
        <!-- Loss Chart Card -->
        <AnimatedCard class="loss-chart-card" :hoverable="false">
          <div class="loss-chart-header">
            <h2 class="card-title">
              <Icon icon="ph:chart-line" :width="20" class="mr-2" />
              训练损失曲线
            </h2>
            <div class="loss-chart-info">
              <span class="loss-current-value">
                训练: {{ lossData.trainLoss[lossData.trainLoss.length - 1]?.toFixed(3) }}
              </span>
              <span class="loss-current-value">
                验证: {{ lossData.valLoss[lossData.valLoss.length - 1]?.toFixed(3) }}
              </span>
            </div>
          </div>
          
          <div 
            ref="chartScrollRef"
            class="chart-scroll-container"
            @mousedown="handleMouseDown"
          >
            <div class="chart-wrapper" :style="{ width: `${lossData.epochs.length * 8}px` }">
              <svg :viewBox="`0 0 ${lossData.epochs.length * 8} 200`" class="loss-chart-svg-horizontal">
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
                    x1="0" :y1="20 + (i - 1) * 35" 
                    :x2="lossData.epochs.length * 8" :y2="20 + (i - 1) * 35" 
                    stroke="var(--color-border)" 
                    stroke-width="1" 
                    opacity="0.2" />
                  <line v-for="i in Math.floor(lossData.epochs.length / 10)" :key="`v${i}`" 
                    :x1="i * 80" y1="20" 
                    :x2="i * 80" y2="175" 
                    stroke="var(--color-border)" 
                    stroke-width="1" 
                    opacity="0.2" />
                </g>
                
                <!-- 训练损失曲线区域填充 -->
                <path
                  :d="`M 0,175 ${lossData.epochs.map((e, i) => 
                    `L ${i * 8},${175 - (lossData.trainLoss[i] / 2.5) * 155}`
                  ).join(' ')} L ${lossData.epochs.length * 8},175 Z`"
                  fill="url(#chartGradient)"
                />
                
                <!-- 训练损失曲线 -->
                <polyline
                  :points="lossData.epochs.map((e, i) => 
                    `${i * 8},${175 - (lossData.trainLoss[i] / 2.5) * 155}`
                  ).join(' ')"
                  fill="none"
                  stroke="#4A69FF"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="loss-line-animated"
                />
                
                <!-- 验证损失曲线 -->
                <polyline
                  :points="lossData.epochs.map((e, i) => 
                    `${i * 8},${175 - (lossData.valLoss[i] / 2.5) * 155}`
                  ).join(' ')"
                  fill="none"
                  stroke="#10B981"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-dasharray="5,3"
                  class="loss-line-animated"
                />
                
                <!-- 坐标轴 -->
                <line x1="0" y1="175" :x2="lossData.epochs.length * 8" y2="175" stroke="var(--color-text-secondary)" stroke-width="1.5" />
                <line x1="0" y1="20" x2="0" y2="175" stroke="var(--color-text-secondary)" stroke-width="1.5" />
                
                <!-- 轴标签 -->
                <text :x="lossData.epochs.length * 4" y="195" text-anchor="middle" fill="var(--color-text-secondary)" font-size="11">训练轮次 (Epochs)</text>
                <text x="15" y="100" text-anchor="middle" fill="var(--color-text-secondary)" font-size="11" transform="rotate(-90, 15, 100)">Loss</text>
              </svg>
            </div>
          </div>
        </AnimatedCard>
      </div>
      
      <!-- Right Column: Job Details -->
      <AnimatedCard class="details-card" :hoverable="false">
        <h2 class="card-title">
          <Icon icon="ph:info" :width="20" class="mr-2" />
          {{ $t('workspace.jobDetails') }}
        </h2>
        
        <div v-if="currentJob" class="job-details-modern">
          <div class="detail-item-modern">
            <div class="detail-icon-wrapper">
              <Icon icon="ph:circle-fill" :width="8" />
            </div>
            <div class="detail-content">
              <span class="detail-label-modern">{{ $t('workspace.status') }}</span>
              <StatusBadge :status="currentJob.status" />
            </div>
          </div>
          <div class="detail-item-modern">
            <div class="detail-icon-wrapper">
              <Icon icon="ph:chart-line-up" :width="12" />
            </div>
            <div class="detail-content">
              <span class="detail-label-modern">{{ $t('workspace.progress') }}</span>
              <span class="detail-value-modern">{{ currentJob.progress.toFixed(1) }}%</span>
            </div>
          </div>
          <div class="detail-item-modern">
            <div class="detail-icon-wrapper">
              <Icon icon="ph:clock" :width="12" />
            </div>
            <div class="detail-content">
              <span class="detail-label-modern">{{ $t('common.started') }}</span>
              <span class="detail-value-modern">{{ formatTime(currentJob.startedAt) }}</span>
            </div>
          </div>
          <div class="detail-item-modern">
            <div class="detail-icon-wrapper">
              <Icon icon="ph:clock-countdown" :width="12" />
            </div>
            <div class="detail-content">
              <span class="detail-label-modern">{{ $t('workspace.estimatedTime') }}</span>
              <span class="detail-value-modern">{{ formatTime(currentJob.estimatedCompletion) }}</span>
            </div>
          </div>
        </div>
      </AnimatedCard>
    </div>

    <div class="workspace-secondary">
      <AnimatedCard class="agent-telemetry-panel" :hoverable="false">
        <div class="panel-header-modern">
          <div class="panel-header-left">
            <div class="panel-icon-badge agent">
              <Icon icon="ph:robot-fill" :width="20" />
            </div>
            <div>
              <h2 class="panel-title-modern">Agent 遥测</h2>
              <p class="panel-subtitle-modern">多智能体协作状态监控</p>
            </div>
          </div>
          <div class="panel-badge-modern">
            <span class="badge-value">{{ agentTelemetry.length }}</span>
            <span class="badge-label">活跃</span>
          </div>
        </div>

        <div class="agent-telemetry-grid-modern">
          <div
            v-if="isLoadingAgents"
            v-for="i in 4"
            :key="`agent-loader-${i}`"
            class="agent-card-modern skeleton"
          >
            <LoadingSkeleton type="title" width="50%" />
            <LoadingSkeleton type="text" width="80%" count="2" />
          </div>

          <div
            v-else
            v-for="agent in agentTelemetry"
            :key="agent.id"
            class="agent-card-modern"
            :class="`agent-${agent.status}`"
          >
            <div class="agent-card-header-modern">
              <div class="agent-icon-wrapper">
                <Icon 
                  :icon="agent.name.includes('INFERENCE') ? 'ph:lightning-fill' :
                         agent.name.includes('ANALYSIS') ? 'ph:brain-fill' :
                         agent.name.includes('ACQUISITION') ? 'ph:download-fill' :
                         'ph:gear-fill'" 
                  :width="20" 
                />
              </div>
              <div class="agent-info-modern">
                <h3 class="agent-name-modern">{{ agent.displayName }}</h3>
                <span class="agent-id-modern">{{ agent.name }}</span>
              </div>
              <div class="agent-status-modern" :class="agent.status">
                <span class="status-dot"></span>
                <span class="status-text">{{ agent.status === 'running' ? '运行中' : agent.status === 'waiting' ? '等待' : '空闲' }}</span>
              </div>
            </div>
            
            <p class="agent-desc-modern">{{ agent.description }}</p>

            <div class="agent-metrics-modern">
              <div class="metric-item-modern">
                <Icon icon="ph:gauge-fill" :width="14" />
                <div class="metric-content">
                  <span class="metric-label">置信度</span>
                  <span class="metric-value">{{ Math.round(agent.confidence * 100) }}%</span>
                </div>
              </div>
              <div class="metric-item-modern">
                <Icon icon="ph:arrow-clockwise-fill" :width="14" />
                <div class="metric-content">
                  <span class="metric-label">吞吐量</span>
                  <span class="metric-value">{{ agent.throughput }}/min</span>
                </div>
              </div>
              <div class="metric-item-modern">
                <Icon icon="ph:check-circle-fill" :width="14" />
                <div class="metric-content">
                  <span class="metric-label">已处理</span>
                  <span class="metric-value">{{ agent.metrics.processed }}</span>
                </div>
              </div>
            </div>

            <div class="agent-actions-modern">
              <div class="action-item-modern">
                <Icon icon="ph:clock-clockwise" :width="12" />
                <span class="action-label">上次任务</span>
                <span class="action-text">{{ agent.lastTask }}</span>
              </div>
              <div class="action-item-modern">
                <Icon icon="ph:arrow-right" :width="12" />
                <span class="action-label">下一步</span>
                <span class="action-text">{{ agent.nextAction }}</span>
              </div>
            </div>
          </div>
        </div>
      </AnimatedCard>

      <AnimatedCard class="mcp-panel" :hoverable="false">
        <div class="panel-header-modern">
          <div class="panel-header-left">
            <div class="panel-icon-badge mcp">
              <Icon icon="ph:toolbox-fill" :width="20" />
            </div>
            <div>
              <h2 class="panel-title-modern">MCP 工具注册表</h2>
              <p class="panel-subtitle-modern">模型上下文协议工具编排</p>
            </div>
          </div>
          <div class="panel-badge-modern">
            <span class="badge-value">{{ mcpRegistry.length }}</span>
            <span class="badge-label">工具</span>
          </div>
        </div>

        <div class="mcp-list-modern">
          <div
            v-if="isLoadingMcp"
            v-for="i in 4"
            :key="`mcp-skeleton-${i}`"
            class="mcp-item-modern skeleton"
          >
            <LoadingSkeleton type="text" width="60%" />
          </div>

          <div
            v-else
            v-for="tool in mcpRegistry"
            :key="tool.id"
            class="mcp-item-modern"
            :class="`mcp-${tool.status}`"
          >
            <div class="mcp-item-header-modern">
              <div class="mcp-icon-wrapper">
                <Icon 
                  :icon="tool.name.includes('Scene') ? 'ph:map-pin-fill' :
                         tool.name.includes('Keyword') ? 'ph:key-fill' :
                         tool.name.includes('Quality') ? 'ph:shield-check-fill' :
                         'ph:cpu-fill'" 
                  :width="18" 
                />
              </div>
              <div class="mcp-info-modern">
                <h3 class="mcp-name-modern">{{ tool.name }}</h3>
                <p class="mcp-desc-modern">{{ tool.description }}</p>
              </div>
            </div>
            
            <div class="mcp-metrics-modern">
              <div class="mcp-metric-modern">
                <Icon icon="ph:clock-fill" :width="12" />
                <span class="mcp-metric-label">延迟</span>
                <span class="mcp-metric-value">{{ tool.latency }}ms</span>
              </div>
              <div class="mcp-metric-modern">
                <Icon icon="ph:chart-bar-fill" :width="12" />
                <span class="mcp-metric-label">使用率</span>
                <span class="mcp-metric-value">{{ tool.usage }}%</span>
              </div>
              <div class="mcp-status-modern" :class="tool.status">
                <span class="status-indicator"></span>
                <span class="status-text-modern">
                  {{ tool.status === 'online' ? '在线' : tool.status === 'degraded' ? '降级' : '离线' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </AnimatedCard>
    </div>
  </div>
</template>

<style scoped lang="scss">
.workspace-view {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: $spacing-lg $spacing-xl;
  overflow-y: auto;
  overflow-x: hidden;
  @include custom-scrollbar;
  position: relative;
  
  // 响应式设计
  @media (max-width: 1024px) {
    padding: $spacing-md $spacing-lg;
  }
  
  @media (max-width: 768px) {
    padding: $spacing-sm $spacing-md;
  }
}

// Header
.workspace-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacing-lg;
  flex-shrink: 0;
  gap: $spacing-md;
  
  // 小屏幕：堆叠布局
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: stretch;
    margin-bottom: $spacing-md;
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

// Main Content - 重构布局：指标为主，任务详情在右侧
.workspace-content {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) minmax(600px, 2.8fr) minmax(280px, 1fr);
  gap: $spacing-md;
  width: 100%;
  min-height: 600px;
  align-items: stretch;
  position: relative;
  z-index: 1;
  flex-shrink: 0;
  
  // 左侧：任务监视器
  .monitor-card {
    display: flex;
    flex-direction: column;
    min-width: 0;
    height: 100%;
    overflow: hidden;
  }
  
  // 中间主要区域：指标 + 损失曲线
  .middle-column-primary {
    display: flex;
    flex-direction: column;
    gap: $spacing-md;
    min-width: 0;
    height: 100%;
    
    .metrics-card-primary {
      display: flex;
      flex-direction: column;
      min-width: 0;
      flex-shrink: 0;
      overflow: hidden;
    }
    
    .loss-chart-card {
      display: flex;
      flex-direction: column;
      min-width: 0;
      flex: 1;
      min-height: 0;
      overflow: hidden;
    }
  }
  
  // 右侧：任务详情
  .details-card {
    display: flex;
    flex-direction: column;
    min-width: 0;
    height: 100%;
    overflow: hidden;
  }
  
  // 中等屏幕：2列布局
  @media (max-width: 1600px) {
    grid-template-columns: minmax(240px, 1fr) minmax(500px, 2.5fr);
    
    .monitor-card {
      grid-column: 1;
      grid-row: 1;
    }
    
    .middle-column-primary {
      grid-column: 2;
      grid-row: 1;
    }
  
    .details-card {
      grid-column: 1 / -1;
      grid-row: 2;
      height: auto;
      max-height: 200px;
    }
  }
  
  // 小屏幕：单列布局
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    gap: $spacing-md;
    
    .monitor-card,
    .middle-column-primary,
    .details-card {
      grid-column: 1;
      height: auto;
    }
    
    .monitor-card {
      min-height: 400px;
      max-height: 500px;
    }
    
    .details-card {
      max-height: 200px;
    }
  }
  
  @media (max-width: 768px) {
    gap: $spacing-sm;
  }
}

// Cards
.card-title {
  display: flex;
  align-items: center;
  font-size: clamp($font-size-base, 1.8vw, $font-size-xl);
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
  margin-bottom: clamp($spacing-sm, 1.2vw, $spacing-lg);
}

.monitor-card,
.logs-card {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
  min-height: 0;
  overflow: hidden;
  
  > * {
    flex-shrink: 0;
    
    &:last-child {
      flex: 1;
      min-height: 0;
      overflow-y: auto;
      overflow-x: hidden;
      // 只在内容溢出时显示滚动条
      scrollbar-width: thin;
      scrollbar-color: transparent transparent;
      
      &:hover {
        scrollbar-color: rgba(74, 105, 255, 0.3) transparent;
      }
      
      // Webkit浏览器
      &::-webkit-scrollbar {
        width: 6px;
      }
      
      &::-webkit-scrollbar-track {
        background: transparent;
      }
      
      &::-webkit-scrollbar-thumb {
        background: transparent;
        border-radius: 3px;
        transition: background 0.2s ease;
      }
      
      &:hover::-webkit-scrollbar-thumb {
        background: rgba(74, 105, 255, 0.3);
      }
      
      // 只在内容溢出时显示
      &:not(:hover) {
        scrollbar-width: none;
        
        &::-webkit-scrollbar {
          display: none;
        }
      }
    }
  }
}

// ========== Job Details Modern Design ==========
// ========== Job Details Modern Design ==========
.job-details-modern {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.detail-item-modern {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-sm;
  border-radius: $radius-md;
  background: var(--color-surface-elevated);
  transition: all 0.2s ease;
  
  .dark & {
    background: rgba(30, 41, 59, 0.3);
  }
  
  &:hover {
    background: rgba(74, 105, 255, 0.05);
    
    .dark & {
      background: rgba(96, 165, 250, 0.1);
    }
  }
}

.detail-icon-wrapper {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: rgba(74, 105, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4A69FF;
  flex-shrink: 0;
}

.detail-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-width: 0;
}

.detail-label-modern {
  font-size: $font-size-xs;
  color: var(--color-text-secondary);
  font-weight: $font-weight-medium;
}

.detail-value-modern {
  font-size: $font-size-sm;
  color: var(--color-text-primary);
  font-weight: $font-weight-semibold;
  @include truncate;
}

// ========== Metrics Primary Design ==========
.metrics-card-primary {
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.metrics-header-modern {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
  padding-bottom: $spacing-md;
  border-bottom: 1px solid var(--color-border);
}

.metrics-header-left {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.metrics-icon-badge {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(74, 105, 255, 0.2), rgba(138, 43, 226, 0.2));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4A69FF;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(74, 105, 255, 0.2);
}

.metrics-title-modern {
  font-size: $font-size-xl;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  margin: 0 0 2px 0;
}

.metrics-subtitle-modern {
  font-size: $font-size-xs;
  color: var(--color-text-secondary);
  margin: 0;
}

.metrics-grid-modern {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $spacing-md;
  
  @media (max-width: 1400px) {
    grid-template-columns: 1fr;
    gap: $spacing-sm;
  }
}

.metric-card-modern {
  background: var(--color-surface-elevated);
  border-radius: 16px;
  padding: $spacing-lg;
  border: 1px solid var(--color-border);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: flex-start;
  gap: $spacing-md;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #4A69FF, #8B5CF6);
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  .dark & {
    background: rgba(30, 41, 59, 0.4);
    border-color: rgba(255, 255, 255, 0.1);
  }
  
  &.accuracy {
    &::before {
      background: linear-gradient(90deg, #10B981, #34D399);
    }
    
    .metric-icon-wrapper {
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(52, 211, 153, 0.15));
      color: #10B981;
    }
  }
  
  &.loss {
    &::before {
      background: linear-gradient(90deg, #EF4444, #F87171);
    }
    
    .metric-icon-wrapper {
      background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(248, 113, 113, 0.15));
      color: #EF4444;
    }
  }
  
  &.samples {
    &::before {
      background: linear-gradient(90deg, #3B82F6, #60A5FA);
    }
    
    .metric-icon-wrapper {
      background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(96, 165, 250, 0.15));
      color: #3B82F6;
    }
  }
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
    border-color: var(--color-primary);
    
    &::before {
      opacity: 1;
    }
    
    .dark & {
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
    }
  }
}

.metric-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.3s ease;
  
  .metric-card-modern:hover & {
    transform: scale(1.1) rotate(5deg);
  }
}

.metric-content-modern {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.metric-label-modern {
  font-size: $font-size-xs;
  color: var(--color-text-secondary);
  font-weight: $font-weight-medium;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metric-value-modern {
  font-size: clamp($font-size-2xl, 3vw, $font-size-4xl);
  font-weight: $font-weight-extrabold;
  color: var(--color-text-primary);
  line-height: 1.1;
}

.metric-trend {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: $font-size-xs;
  font-weight: $font-weight-semibold;
  color: #10B981;
  margin-top: 4px;
  
  &.down {
    color: #EF4444;
  }
  
  > svg {
    flex-shrink: 0;
  }
}

.metric-progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(74, 105, 255, 0.1);
  border-radius: $radius-full;
  overflow: hidden;
  margin-top: 8px;
  
  .dark & {
    background: rgba(96, 165, 250, 0.15);
  }
}

.metric-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3B82F6, #60A5FA);
  border-radius: $radius-full;
  transition: width 0.5s ease;
}

// Loss Chart Card
.loss-chart-card {
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.loss-chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
  flex-shrink: 0;
  
  .card-title {
    margin: 0;
  }
}

.loss-chart-info {
  display: flex;
  gap: $spacing-lg;
}

.loss-current-value {
  font-size: $font-size-sm;
  font-weight: $font-weight-semibold;
  color: var(--color-text-secondary);
  padding: $spacing-xs $spacing-sm;
  background: var(--color-surface-elevated);
  border-radius: $radius-md;
  
  .dark & {
    background: rgba(30, 41, 59, 0.5);
  }
}

.chart-scroll-container {
  width: 100%;
  height: 220px;
  overflow-x: auto;
  overflow-y: hidden;
  cursor: grab;
  position: relative;
  @include custom-scrollbar;
  
  &:active {
    cursor: grabbing;
  }
  
  &::-webkit-scrollbar {
    height: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: var(--color-surface-elevated);
    border-radius: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(74, 105, 255, 0.4);
    border-radius: 4px;
    
    &:hover {
      background: rgba(74, 105, 255, 0.6);
    }
  }
}

.chart-wrapper {
  height: 200px;
  min-width: 100%;
}

.loss-chart-svg-horizontal {
  width: 100%;
  height: 200px;
  display: block;
}

.loss-line-animated {
  animation: lineDraw 0.5s ease-out;
}

@keyframes lineDraw {
  from {
    stroke-dasharray: 1000;
    stroke-dashoffset: 1000;
  }
  to {
    stroke-dasharray: 1000;
    stroke-dashoffset: 0;
  }
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
  overflow-x: hidden;
  min-height: 0;
  @include custom-scrollbar;
  
  // 确保内容不会被挤压
  display: flex;
  flex-direction: column;
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
  overflow-x: hidden;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: $font-size-sm;
  background: var(--color-bg);
  border-radius: $radius-md;
  padding: $spacing-md;
  min-height: 0;
  @include custom-scrollbar;
  word-wrap: break-word;
  
  .dark & {
    background: rgba(15, 23, 42, 0.6);
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
  padding-top: $spacing-lg;
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: $spacing-lg;
  align-items: start;
  position: relative;
  z-index: 0;
  clear: both;
  
  // 小屏幕：单列布局
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    gap: $spacing-md;
    margin-top: $spacing-lg;
    padding-top: $spacing-md;
  }
  
  @media (max-width: 768px) {
    gap: $spacing-sm;
    margin-top: $spacing-md;
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
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: $spacing-lg;
  
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
  min-width: 0;
  
  .dark & {
    background: rgba(30, 41, 59, 0.4);
  }

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
  min-width: 0;

  .dark & {
    background: rgba(96, 165, 250, 0.12);
  }

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

// ========== Modern Panel Header ==========
.panel-header-modern {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
  padding-bottom: $spacing-md;
  border-bottom: 1px solid var(--color-border);
}

.panel-header-left {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.panel-icon-badge {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  &.agent {
    background: linear-gradient(135deg, rgba(74, 105, 255, 0.15), rgba(138, 43, 226, 0.15));
    color: #4A69FF;
  }
  
  &.mcp {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(59, 130, 246, 0.15));
    color: #10B981;
  }
}

.panel-title-modern {
  font-size: $font-size-lg;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  margin: 0 0 2px 0;
}

.panel-subtitle-modern {
  font-size: $font-size-xs;
  color: var(--color-text-secondary);
  margin: 0;
}

.panel-badge-modern {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $spacing-xs $spacing-md;
  background: var(--color-surface-elevated);
  border-radius: $radius-md;
  min-width: 60px;
  
  .dark & {
    background: rgba(30, 41, 59, 0.5);
  }
}

.badge-value {
  font-size: $font-size-xl;
  font-weight: $font-weight-bold;
  color: var(--color-primary);
  line-height: 1;
}

.badge-label {
  font-size: $font-size-xs;
  color: var(--color-text-secondary);
  margin-top: 2px;
}

// ========== Agent Telemetry Modern Design ==========
.agent-telemetry-grid-modern {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: $spacing-lg;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: $spacing-md;
  }
}

.agent-card-modern {
  background: var(--color-surface-elevated);
  border-radius: 20px;
  padding: $spacing-lg;
  border: 2px solid var(--color-border);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #4A69FF, #8B5CF6);
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  .dark & {
    background: rgba(30, 41, 59, 0.5);
    border-color: rgba(255, 255, 255, 0.15);
  }
  
  &.agent-running {
    border-color: rgba(16, 185, 129, 0.4);
    border-width: 2px;
    
    &::before {
      opacity: 1;
      background: linear-gradient(90deg, #10B981, #34D399);
    }
  }
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
    border-color: var(--color-primary);
    
    &::before {
      opacity: 1;
    }
    
    .dark & {
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
    }
  }
  
  &.skeleton {
    background: transparent;
    border: none;
    box-shadow: none;
    transform: none;
    
    &::before {
      display: none;
    }
  }
}

.agent-card-header-modern {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.agent-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(74, 105, 255, 0.2), rgba(138, 43, 226, 0.2));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4A69FF;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(74, 105, 255, 0.2);
}

.agent-info-modern {
  flex: 1;
  min-width: 0;
}

.agent-name-modern {
  font-size: $font-size-lg;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
  line-height: 1.3;
  @include truncate;
}

.agent-id-modern {
  font-size: $font-size-sm;
  color: var(--color-text-tertiary);
  font-family: 'Monaco', 'Courier New', monospace;
  font-weight: $font-weight-medium;
  @include truncate;
}

.agent-status-modern {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: $radius-full;
  font-size: $font-size-sm;
  font-weight: $font-weight-semibold;
  flex-shrink: 0;
  
  &.running {
    background: rgba(16, 185, 129, 0.15);
    color: #10B981;
    
    .status-dot {
      width: 8px;
      height: 8px;
      background: #10B981;
      box-shadow: 0 0 12px rgba(16, 185, 129, 0.6);
      animation: pulse 2s ease-in-out infinite;
    }
  }
  
  &.waiting {
    background: rgba(251, 191, 36, 0.15);
    color: #FBBF24;
    
    .status-dot {
      width: 8px;
      height: 8px;
      background: #FBBF24;
    }
  }
  
  &.idle {
    background: rgba(156, 163, 175, 0.15);
    color: #9CA3AF;
    
    .status-dot {
      width: 8px;
      height: 8px;
      background: #9CA3AF;
    }
  }
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

.agent-desc-modern {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.6;
  @include line-clamp(2);
}

.agent-metrics-modern {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $spacing-sm;
  margin-top: $spacing-sm;
}

.metric-item-modern {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: $spacing-sm $spacing-md;
  background: rgba(74, 105, 255, 0.08);
  border-radius: 12px;
  font-size: $font-size-sm;
  
  .dark & {
    background: rgba(96, 165, 250, 0.15);
  }
  
  > svg {
    color: #4A69FF;
    flex-shrink: 0;
    width: 18px;
    height: 18px;
  }
}

.metric-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
  gap: 2px;
}

.metric-label {
  font-size: $font-size-xs;
  color: var(--color-text-tertiary);
  font-weight: $font-weight-medium;
  @include truncate;
}

.metric-value {
  font-size: $font-size-base;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  @include truncate;
}

.agent-actions-modern {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
  margin-top: $spacing-sm;
  padding-top: $spacing-md;
  border-top: 2px solid var(--color-border);
}

.action-item-modern {
  display: flex;
  align-items: flex-start;
  gap: $spacing-sm;
  font-size: $font-size-sm;
  line-height: 1.5;
  
  > svg {
    color: var(--color-text-tertiary);
    flex-shrink: 0;
    width: 16px;
    height: 16px;
    margin-top: 2px;
  }
}

.action-label {
  color: var(--color-text-tertiary);
  font-weight: $font-weight-semibold;
  min-width: 70px;
  flex-shrink: 0;
}

.action-text {
  color: var(--color-text-secondary);
  flex: 1;
  line-height: 1.5;
  word-break: break-word;
}

// ========== MCP Tools Modern Design ==========
.mcp-list-modern {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.mcp-item-modern {
  background: var(--color-surface-elevated);
  border-radius: 16px;
  padding: $spacing-lg;
  border: 2px solid var(--color-border);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  
  .dark & {
    background: rgba(30, 41, 59, 0.5);
    border-color: rgba(255, 255, 255, 0.15);
  }
  
  &.mcp-online {
    border-left: 4px solid #10B981;
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      bottom: 0;
      width: 4px;
      background: linear-gradient(180deg, #10B981, #34D399);
      border-radius: 16px 0 0 16px;
    }
  }
  
  &.mcp-degraded {
    border-left: 4px solid #F59E0B;
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      bottom: 0;
      width: 4px;
      background: linear-gradient(180deg, #F59E0B, #FBBF24);
      border-radius: 16px 0 0 16px;
    }
  }
  
  &.mcp-offline {
    border-left: 4px solid #EF4444;
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      bottom: 0;
      width: 4px;
      background: linear-gradient(180deg, #EF4444, #F87171);
      border-radius: 16px 0 0 16px;
    }
  }
  
  &:hover {
    transform: translateX(6px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    border-color: var(--color-primary);
    
    .dark & {
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }
  }
  
  &.skeleton {
    background: transparent;
    border: none;
    box-shadow: none;
    transform: none;
    
    &::before {
      display: none;
    }
  }
}

.mcp-item-header-modern {
  display: flex;
  align-items: flex-start;
  gap: $spacing-md;
  margin-bottom: $spacing-md;
}

.mcp-icon-wrapper {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(59, 130, 246, 0.2));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #10B981;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

.mcp-info-modern {
  flex: 1;
  min-width: 0;
}

.mcp-name-modern {
  font-size: $font-size-lg;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  margin: 0 0 6px 0;
  line-height: 1.3;
  @include truncate;
}

.mcp-desc-modern {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.6;
  @include line-clamp(2);
}

.mcp-metrics-modern {
  display: flex;
  align-items: center;
  gap: $spacing-lg;
  flex-wrap: wrap;
  padding-top: $spacing-sm;
  border-top: 2px solid var(--color-border);
}

.mcp-metric-modern {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: $font-size-sm;
  
  > svg {
    color: var(--color-text-tertiary);
    flex-shrink: 0;
    width: 16px;
    height: 16px;
  }
}

.mcp-metric-label {
  color: var(--color-text-tertiary);
  font-weight: $font-weight-medium;
}

.mcp-metric-value {
  color: var(--color-text-primary);
  font-weight: $font-weight-bold;
  font-size: $font-size-base;
}

.mcp-status-modern {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: $radius-full;
  font-size: $font-size-sm;
  font-weight: $font-weight-semibold;
  margin-left: auto;
  
  &.online {
    background: rgba(16, 185, 129, 0.15);
    color: #10B981;
    
    .status-indicator {
      width: 8px;
      height: 8px;
      background: #10B981;
      box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
    }
  }
  
  &.degraded {
    background: rgba(251, 191, 36, 0.15);
    color: #FBBF24;
    
    .status-indicator {
      width: 8px;
      height: 8px;
      background: #FBBF24;
    }
  }
  
  &.offline {
    background: rgba(239, 68, 68, 0.15);
    color: #EF4444;
    
    .status-indicator {
      width: 8px;
      height: 8px;
      background: #EF4444;
    }
  }
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-text-modern {
  @include truncate;
}
</style>


