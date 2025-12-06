<script setup lang="ts">
/**
 * Workspace View - 工作区主视图
 * 
 * 模块化重构版本：
 * - EvolutionMonitor: 进化任务监视器
 * - YoloMetricsCard: YOLO训练指标
 * - LossChartCard: 损失曲线图
 * - TrainingDetailsCard: 训练详情
 * - AgentTelemetryPanel: Agent遥测
 * - McpToolsPanel: MCP工具注册表
 */

import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'

// 子组件
import EvolutionMonitor from '@/components/workspace/EvolutionMonitor.vue'
import YoloMetricsCard from '@/components/workspace/YoloMetricsCard.vue'
import LossChartCard from '@/components/workspace/LossChartCard.vue'
import TrainingDetailsCard from '@/components/workspace/TrainingDetailsCard.vue'
import AgentTelemetryPanel from '@/components/workspace/AgentTelemetryPanel.vue'
import McpToolsPanel from '@/components/workspace/McpToolsPanel.vue'

// 类型和Mock数据
import type { StepConfig, YoloLossData, ProjectInfo, JobStatus } from '@/components/workspace/types'
import { createJobStatusStream, type JobStep } from '@/mock/jobStatus'

const { t } = useI18n()
const route = useRoute()

// 状态
const currentJob = ref<JobStatus | null>(null)
const stopStream = ref<(() => void) | null>(null)
const currentStepIndex = ref(0)
const lossChartRef = ref<InstanceType<typeof LossChartCard> | null>(null)

// 当前项目信息
const currentProject = ref<ProjectInfo>({
  id: route.params.id || '2',
  name: '医学影像数据集',
  status: 'training'
})

// 步骤配置
const steps = ref<StepConfig[]>([
  { key: 'initialization', label: t('steps.initialization'), icon: 'ph:gear' },
  { key: 'data_preparation', label: t('steps.dataPreparation'), icon: 'ph:database' },
  { key: 'model_training', label: t('steps.modelTraining'), icon: 'ph:brain' },
  { key: 'active_learning', label: t('steps.activeLearning'), icon: 'ph:arrows-clockwise' },
  { key: 'inference', label: t('steps.inference'), icon: 'ph:lightning' },
  { key: 'completed', label: t('steps.completed'), icon: 'ph:check-circle' }
])

// 损失数据生成
const generateYoloLossData = (): YoloLossData => {
  const epochs = Array.from({ length: 100 }, (_, i) => i + 1)
  
  const boxLoss = epochs.map((_, i) => {
    const base = 0.08
    const decay = Math.exp(-i / 25) * 0.06
    const noise = (Math.random() - 0.5) * 0.003
    return Math.max(0.015, base * (0.3 + decay) + noise)
  })
  
  const clsLoss = epochs.map((_, i) => {
    const base = 0.05
    const decay = Math.exp(-i / 30) * 0.04
    const noise = (Math.random() - 0.5) * 0.002
    return Math.max(0.008, base * (0.25 + decay) + noise)
  })
  
  const objLoss = epochs.map((_, i) => {
    const base = 0.04
    const decay = Math.exp(-i / 20) * 0.035
    const noise = (Math.random() - 0.5) * 0.002
    return Math.max(0.006, base * (0.2 + decay) + noise)
  })
  
  const totalLoss = epochs.map((_, i) => boxLoss[i] + clsLoss[i] + objLoss[i])
  const valLoss = totalLoss.map((loss) => Math.max(0.03, loss * 1.15 + (Math.random() - 0.4) * 0.01))
  
  return { epochs, boxLoss, clsLoss, objLoss, totalLoss, valLoss }
}

const lossData = ref<YoloLossData>(generateYoloLossData())
let lossUpdateInterval: ReturnType<typeof setInterval> | null = null

// 更新损失数据
const updateLossData = () => {
  if (!currentJob.value || currentJob.value.status !== 'running') return
  
  const lastBoxLoss = lossData.value.boxLoss[lossData.value.boxLoss.length - 1]
  const lastClsLoss = lossData.value.clsLoss[lossData.value.clsLoss.length - 1]
  const lastObjLoss = lossData.value.objLoss[lossData.value.objLoss.length - 1]
  const lastValLoss = lossData.value.valLoss[lossData.value.valLoss.length - 1]
  
  lossData.value.epochs.push(lossData.value.epochs.length + 1)
  
  const newBoxLoss = Math.max(0.015, lastBoxLoss - 0.0003 + (Math.random() - 0.5) * 0.002)
  const newClsLoss = Math.max(0.008, lastClsLoss - 0.0002 + (Math.random() - 0.5) * 0.001)
  const newObjLoss = Math.max(0.006, lastObjLoss - 0.0002 + (Math.random() - 0.5) * 0.001)
  
  lossData.value.boxLoss.push(newBoxLoss)
  lossData.value.clsLoss.push(newClsLoss)
  lossData.value.objLoss.push(newObjLoss)
  lossData.value.totalLoss.push(newBoxLoss + newClsLoss + newObjLoss)
  lossData.value.valLoss.push(Math.max(0.03, lastValLoss - 0.0006 + (Math.random() - 0.4) * 0.003))
  
  // 保持最多300个数据点
  if (lossData.value.epochs.length > 300) {
    lossData.value.epochs.shift()
    lossData.value.boxLoss.shift()
    lossData.value.clsLoss.shift()
    lossData.value.objLoss.shift()
    lossData.value.totalLoss.shift()
    lossData.value.valLoss.shift()
  }
  
  lossChartRef.value?.scrollToEnd()
}

const startLossUpdate = () => {
  if (lossUpdateInterval) return
  lossUpdateInterval = setInterval(updateLossData, 2000)
}

const stopLossUpdate = () => {
  if (lossUpdateInterval) {
    clearInterval(lossUpdateInterval)
    lossUpdateInterval = null
  }
}

// 任务监控
const startJobMonitoring = () => {
  stopStream.value = createJobStatusStream((status: JobStatus) => {
    currentJob.value = status
    
    const stepIndex = steps.value.findIndex(s => s.key === status.currentStep)
    if (stepIndex !== -1) {
      currentStepIndex.value = stepIndex
    }
    
    if (status.status === 'running' && stepIndex >= 2) {
      startLossUpdate()
    } else {
      stopLossUpdate()
    }
  }, 2000)
}

const stopJobMonitoring = () => {
  if (stopStream.value) {
    stopStream.value()
    stopStream.value = null
  }
}

watch(() => currentJob.value?.status, (status) => {
  if (status === 'completed') {
    setTimeout(stopJobMonitoring, 3000)
  }
})

onMounted(() => {
  startJobMonitoring()
})

onUnmounted(() => {
  stopJobMonitoring()
  stopLossUpdate()
})
</script>

<template>
  <div class="workspace-view">
    <!-- 页头 -->
    <header class="workspace-header">
      <div class="header-main">
        <div class="project-badge">
          <Icon icon="ph:folder-open-fill" :width="18" />
          <span>当前项目</span>
        </div>
        <h1 class="workspace-title">{{ currentProject.name }}</h1>
        <p class="workspace-subtitle">{{ $t('workspace.subtitle') }}</p>
      </div>
      
      <div v-if="currentJob" class="job-controls">
        <el-button size="large">
          <Icon icon="ph:pause" :width="18" class="btn-icon" />
          {{ $t('workspace.pauseJob') }}
        </el-button>
        <el-button size="large" type="danger">
          <Icon icon="ph:stop" :width="18" class="btn-icon" />
          {{ $t('workspace.stopJob') }}
        </el-button>
      </div>
    </header>
    
    <!-- 主内容区：三列布局 -->
    <section class="main-section">
      <!-- 左侧：进化任务监视器 -->
      <EvolutionMonitor
        :steps="steps"
        :current-job="currentJob"
        :current-step-index="currentStepIndex"
        class="monitor-panel"
      />
      
      <!-- 中间：指标 + 损失曲线 -->
      <div class="center-panel">
        <YoloMetricsCard :current-job="currentJob" class="metrics-card" />
        <LossChartCard ref="lossChartRef" :loss-data="lossData" class="chart-card" />
          </div>
          
      <!-- 右侧：训练详情 -->
      <TrainingDetailsCard :current-job="currentJob" class="details-panel" />
    </section>
    
    <!-- 底部区域：Agent遥测 + MCP工具 -->
    <section class="secondary-section">
      <AgentTelemetryPanel class="agent-panel" />
      <McpToolsPanel class="mcp-panel" />
    </section>
  </div>
</template>

<style scoped lang="scss">
// ========== 页面整体布局 ==========
// 关键：设置 overflow-y: auto 让页面内部滚动（因为 app-main 是 overflow: hidden）
.workspace-view {
  width: 100%;
  height: 100%; // 填满 app-main
  padding: clamp(16px, 2vw, 24px);
  padding-bottom: clamp(32px, 4vw, 48px); // 底部留白
  display: flex;
  flex-direction: column;
  gap: clamp(16px, 2vw, 24px);
  overflow-y: auto; // 关键：让页面可滚动
  overflow-x: hidden;
  @include custom-scrollbar;
  
  // 页面背景
  background: var(--color-bg);
}

// ========== 页头 ==========
.workspace-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;
}

.header-main {
  flex: 1;
  min-width: 200px;
}

.project-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  background: rgba(74, 105, 255, 0.1);
  border-radius: 20px;
  font-size: clamp(11px, 1vw, 13px);
  font-weight: 500;
  color: var(--color-primary);
  margin-bottom: 8px;
}

.workspace-title {
  font-size: clamp(20px, 2.5vw, 28px);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
  line-height: 1.2;
}

.workspace-subtitle {
  font-size: clamp(13px, 1.2vw, 15px);
  color: var(--color-text-secondary);
  margin: 0;
}

.job-controls {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  
  .btn-icon {
    margin-right: 6px;
  }
}

// ========== 主内容区 - 三列对齐 ==========
.main-section {
  display: grid;
  grid-template-columns: minmax(220px, 280px) minmax(400px, 1fr) minmax(240px, 320px);
  gap: clamp(12px, 1.5vw, 20px);
  align-items: stretch; // 关键：让三列底部对齐
  
  @media (max-width: 1400px) {
    grid-template-columns: minmax(200px, 260px) minmax(350px, 1fr) minmax(220px, 280px);
  }
  
  @media (max-width: 1200px) {
    grid-template-columns: minmax(200px, 1fr) minmax(200px, 1fr);
    grid-template-rows: auto auto;
    
    .monitor-panel {
      grid-column: 1;
      grid-row: 1;
    }
    
    .center-panel {
      grid-column: 2;
      grid-row: 1 / 3;
    }
  
    .details-panel {
      grid-column: 1;
      grid-row: 2;
    }
  }
  
  @media (max-width: 900px) {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
    
    .monitor-panel,
    .center-panel,
    .details-panel {
      grid-column: 1;
      grid-row: auto;
    }
  }
    }
    
.monitor-panel {
  // 不设置固定高度，让 grid stretch 自动填充
}

.center-panel {
  display: flex;
  flex-direction: column;
  gap: clamp(12px, 1.2vw, 16px);
  
  .metrics-card {
    flex-shrink: 0;
  }
  
  .chart-card {
  flex: 1;
    min-height: 200px;
  }
}

.details-panel {
  // 不设置 max-height，让它和中间列等高（通过 grid align-items: stretch）
  // 内部组件自己处理滚动
}

// ========== 底部区域 ==========
.secondary-section {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(0, 1fr);
  gap: clamp(12px, 1.5vw, 20px);
  align-items: start; // 让两个面板根据内容高度自适应
  flex-shrink: 0; // 不被压缩
  
  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
  }
}

.agent-panel,
.mcp-panel {
  flex-shrink: 0;
}
</style>
