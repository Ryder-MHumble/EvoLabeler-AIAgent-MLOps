<script setup lang="ts">
/**
 * TrainingDetailsCard - 训练详情卡片
 * 显示模型配置、硬件资源、时间信息等
 * 支持项目特定的配置数据
 */

import { Icon } from '@iconify/vue'
import AnimatedCard from '@/components/common/AnimatedCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import type { JobStatus } from './types'
import type { ProjectWorkspaceConfig } from '@/mock/projectWorkspaceData'

const props = defineProps<{
  currentJob: JobStatus | null
  projectConfig?: ProjectWorkspaceConfig
}>()

const formatTime = (isoString?: string) => {
  if (!isoString) return 'N/A'
  const date = new Date(isoString)
  return date.toLocaleTimeString()
}
</script>

<template>
  <AnimatedCard class="training-details-card" :hoverable="false">
    <h2 class="card-title">
      <Icon icon="ph:info" :width="18" class="title-icon" />
      训练详情
    </h2>
    
    <div v-if="currentJob || projectConfig" class="details-content">
      <!-- 基本状态 -->
      <div class="detail-section">
        <div class="section-title">基本信息</div>
        <div class="detail-item">
          <div class="item-icon status"><Icon icon="ph:circle-fill" :width="8" /></div>
          <div class="item-content">
            <span class="item-label">状态</span>
            <StatusBadge :status="currentJob?.status || projectConfig?.status || 'idle'" size="small" />
          </div>
        </div>
        <div class="detail-item">
          <div class="item-icon progress"><Icon icon="ph:chart-line-up" :width="12" /></div>
          <div class="item-content">
            <span class="item-label">当前进度</span>
            <span class="item-value">{{ 
              projectConfig 
                ? ((projectConfig.trainingConfig.currentEpoch / projectConfig.trainingConfig.totalEpochs) * 100).toFixed(1) 
                : (currentJob?.progress || 0).toFixed(1) 
            }}%</span>
          </div>
        </div>
      </div>
      
      <!-- YOLO 配置 - 优先使用项目配置 -->
      <div class="detail-section">
        <div class="section-title">模型配置</div>
        <div class="detail-item">
          <div class="item-icon model"><Icon icon="ph:cube" :width="12" /></div>
          <div class="item-content">
            <span class="item-label">模型架构</span>
            <span class="item-value highlight">{{ projectConfig?.modelArchitecture || 'YOLOv8n' }}</span>
          </div>
        </div>
        <div class="detail-item">
          <div class="item-icon"><Icon icon="ph:stack" :width="12" /></div>
          <div class="item-content">
            <span class="item-label">批量大小</span>
            <span class="item-value">{{ projectConfig?.trainingConfig.batchSize || currentJob?.yoloMetrics?.batchSize || 16 }}</span>
          </div>
        </div>
        <div class="detail-item">
          <div class="item-icon"><Icon icon="ph:graduation-cap" :width="12" /></div>
          <div class="item-content">
            <span class="item-label">学习率</span>
            <span class="item-value code">{{ projectConfig?.trainingConfig.learningRate || currentJob?.yoloMetrics?.learningRate?.toExponential(2) || '1.00e-2' }}</span>
          </div>
        </div>
        <div class="detail-item">
          <div class="item-icon"><Icon icon="ph:image-square" :width="12" /></div>
          <div class="item-content">
            <span class="item-label">输入尺寸</span>
            <span class="item-value">{{ projectConfig?.trainingConfig.inputSize || '640×640' }}</span>
          </div>
        </div>
      </div>
      
      <!-- 硬件资源 -->
      <div class="detail-section">
        <div class="section-title">硬件资源</div>
        <div class="detail-item">
          <div class="item-icon gpu"><Icon icon="ph:cpu" :width="12" /></div>
          <div class="item-content">
            <span class="item-label">GPU 显存</span>
            <span class="item-value">{{ projectConfig?.hardware.gpuMemory || currentJob?.yoloMetrics?.gpuMemory || '8.2GB / 12GB' }}</span>
          </div>
        </div>
        <div class="detail-item">
          <div class="item-icon"><Icon icon="ph:gauge" :width="12" /></div>
          <div class="item-content">
            <span class="item-label">GPU 利用率</span>
            <span class="item-value">{{ projectConfig?.hardware.gpuUsage || currentJob?.yoloMetrics?.gpuUtilization?.toFixed(0) || 90 }}%</span>
          </div>
        </div>
      </div>
      
      <!-- 时间信息 -->
      <div class="detail-section">
        <div class="section-title">时间信息</div>
        <div class="detail-item">
          <div class="item-icon time"><Icon icon="ph:clock" :width="12" /></div>
          <div class="item-content">
            <span class="item-label">开始时间</span>
            <span class="item-value">{{ projectConfig?.timing.startTime || formatTime(currentJob?.startedAt) }}</span>
          </div>
        </div>
        <div class="detail-item">
          <div class="item-icon"><Icon icon="ph:timer" :width="12" /></div>
          <div class="item-content">
            <span class="item-label">每轮耗时</span>
            <span class="item-value">{{ projectConfig?.timing.epochTime || (currentJob?.yoloMetrics?.epochTime?.toFixed(0) + 's') || '55s' }}</span>
          </div>
        </div>
        <div class="detail-item">
          <div class="item-icon eta"><Icon icon="ph:hourglass-medium" :width="12" /></div>
          <div class="item-content">
            <span class="item-label">预计剩余</span>
            <span class="item-value highlight">{{ projectConfig?.timing.estimatedRemaining || currentJob?.yoloMetrics?.eta || '4h 8m' }}</span>
          </div>
        </div>
      </div>
      
      <!-- 数据集信息 -->
      <div class="detail-section">
        <div class="section-title">数据集</div>
        <div class="detail-item">
          <div class="item-icon data"><Icon icon="ph:database" :width="12" /></div>
          <div class="item-content">
            <span class="item-label">样本总数</span>
            <span class="item-value">{{ (projectConfig?.dataset.totalSamples || currentJob?.metrics?.totalSamples || 3420).toLocaleString() }}</span>
          </div>
        </div>
        <div class="detail-item">
          <div class="item-icon"><Icon icon="ph:check-square" :width="12" /></div>
          <div class="item-content">
            <span class="item-label">已处理</span>
            <span class="item-value">{{ (projectConfig?.dataset.processedSamples || currentJob?.metrics?.samplesProcessed || 193).toLocaleString() }}</span>
          </div>
        </div>
        <div class="detail-item full-width">
          <div class="data-progress">
            <div 
              class="progress-fill" 
              :style="{ width: `${(
                (projectConfig?.dataset.processedSamples || currentJob?.metrics?.samplesProcessed || 0) / 
                (projectConfig?.dataset.totalSamples || currentJob?.metrics?.totalSamples || 1)
              ) * 100}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </AnimatedCard>
</template>

<style scoped lang="scss">
.training-details-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: clamp(13px, 1.2vw, 16px);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 12px;
  flex-shrink: 0;
  
  .title-icon { color: var(--color-primary); }
}

.details-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
  padding-right: 4px;
  @include custom-scrollbar;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-bottom: 10px;
  margin-bottom: 4px;
  border-bottom: 1px solid var(--color-border);
  
  &:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }
}

.section-title {
  font-size: clamp(9px, 0.85vw, 10px);
  font-weight: 600;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 2px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 8px;
  background: var(--color-surface-elevated);
  transition: all 0.2s ease;
  
  .dark & {
    background: rgba(30, 41, 59, 0.3);
  }
  
  &:hover {
    background: rgba(74, 105, 255, 0.05);
  }

  .dark &:hover {
    background: rgba(96, 165, 250, 0.1);
  }
  
  &.full-width {
    padding: 6px 0;
    background: transparent;
    
    &:hover { background: transparent; }
  }
}

.item-icon {
  width: 20px;
  height: 20px;
  border-radius: 5px;
  background: rgba(74, 105, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4A69FF;
  flex-shrink: 0;

  .dark & {
    background: rgba(96, 165, 250, 0.15);
  }

  &.status { background: rgba(16, 185, 129, 0.1); color: #10B981; }
  &.progress { background: rgba(59, 130, 246, 0.1); color: #3B82F6; }
  &.model { background: rgba(139, 92, 246, 0.1); color: #8B5CF6; }
  &.gpu { background: rgba(245, 158, 11, 0.1); color: #F59E0B; }
  &.time { background: rgba(6, 182, 212, 0.1); color: #06B6D4; }
  &.eta { background: rgba(239, 68, 68, 0.1); color: #EF4444; }
  &.data { background: rgba(16, 185, 129, 0.1); color: #10B981; }
}

.item-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-width: 0;
}

.item-label {
  font-size: clamp(10px, 0.9vw, 11px);
  color: var(--color-text-secondary);
  font-weight: 500;
}

.item-value {
  font-size: clamp(10px, 0.95vw, 12px);
  color: var(--color-text-primary);
  font-weight: 600;
  @include truncate;
  
  &.highlight {
    color: var(--color-primary);
    font-weight: 700;
  }
  
  &.code {
    font-family: 'Monaco', 'Courier New', monospace;
    font-size: clamp(9px, 0.85vw, 11px);
    background: rgba(74, 105, 255, 0.08);
    padding: 2px 5px;
    border-radius: 4px;

    .dark & {
      background: rgba(96, 165, 250, 0.15);
    }
  }
}

.data-progress {
  width: 100%;
  height: 5px;
  background: rgba(74, 105, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  
  .dark & { background: rgba(96, 165, 250, 0.15); }
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10B981, #34D399);
  border-radius: 3px;
  transition: width 0.5s ease;
}
</style>

