<script setup lang="ts">
/**
 * YoloMetricsCard - YOLO训练指标卡片
 * 显示 mAP, Precision, Recall, Loss 等核心指标
 */

import { Icon } from '@iconify/vue'
import AnimatedCard from '@/components/common/AnimatedCard.vue'
import type { JobStatus } from './types'

defineProps<{
  currentJob: JobStatus | null
}>()
</script>

<template>
  <AnimatedCard class="yolo-metrics-card" :hoverable="false">
    <div class="metrics-header">
      <div class="header-left">
        <div class="icon-badge">
          <Icon icon="ph:chart-bar-fill" :width="22" />
        </div>
        <div>
          <h2 class="title">YOLO训练指标</h2>
          <p class="subtitle">实时检测性能监控</p>
        </div>
      </div>
      <div v-if="currentJob?.yoloMetrics" class="epoch-badge">
        <Icon icon="ph:repeat" :width="14" />
        <span>Epoch {{ currentJob.yoloMetrics.currentEpoch }}/{{ currentJob.yoloMetrics.totalEpochs }}</span>
      </div>
    </div>
    
    <div v-if="currentJob?.yoloMetrics" class="metrics-grid">
      <!-- mAP@50 -->
      <div class="metric-item map">
        <div class="metric-icon"><Icon icon="ph:target-fill" :width="24" /></div>
        <div class="metric-content">
          <div class="metric-label">mAP@50</div>
          <div class="metric-value">{{ (currentJob.yoloMetrics.mAP50 * 100).toFixed(1) }}%</div>
          <div class="metric-trend up">
            <Icon icon="ph:arrow-up-right" :width="12" />
            <span>+{{ ((currentJob.yoloMetrics.mAP50 - 0.15) * 100).toFixed(1) }}%</span>
          </div>
        </div>
      </div>
      
      <!-- mAP@50:95 -->
      <div class="metric-item map-secondary">
        <div class="metric-icon"><Icon icon="ph:crosshair-fill" :width="24" /></div>
        <div class="metric-content">
          <div class="metric-label">mAP@50:95</div>
          <div class="metric-value">{{ (currentJob.yoloMetrics.mAP5095 * 100).toFixed(1) }}%</div>
          <div class="metric-trend up">
            <Icon icon="ph:arrow-up-right" :width="12" />
            <span>+{{ ((currentJob.yoloMetrics.mAP5095 - 0.08) * 100).toFixed(1) }}%</span>
          </div>
        </div>
      </div>
      
      <!-- Precision -->
      <div class="metric-item precision">
        <div class="metric-icon"><Icon icon="ph:check-circle-fill" :width="24" /></div>
        <div class="metric-content">
          <div class="metric-label">精确率 (P)</div>
          <div class="metric-value">{{ (currentJob.yoloMetrics.precision * 100).toFixed(1) }}%</div>
          <div class="metric-bar">
            <div class="bar-fill precision" :style="{ width: `${currentJob.yoloMetrics.precision * 100}%` }"></div>
          </div>
        </div>
      </div>
      
      <!-- Recall -->
      <div class="metric-item recall">
        <div class="metric-icon"><Icon icon="ph:circles-three-fill" :width="24" /></div>
        <div class="metric-content">
          <div class="metric-label">召回率 (R)</div>
          <div class="metric-value">{{ (currentJob.yoloMetrics.recall * 100).toFixed(1) }}%</div>
          <div class="metric-bar">
            <div class="bar-fill recall" :style="{ width: `${currentJob.yoloMetrics.recall * 100}%` }"></div>
          </div>
        </div>
      </div>
      
      <!-- Box Loss -->
      <div class="metric-item loss">
        <div class="metric-icon"><Icon icon="ph:bounding-box-fill" :width="24" /></div>
        <div class="metric-content">
          <div class="metric-label">Box Loss</div>
          <div class="metric-value">{{ currentJob.yoloMetrics.boxLoss.toFixed(4) }}</div>
          <div class="metric-trend down">
            <Icon icon="ph:arrow-down-right" :width="12" />
            <span>-{{ (0.08 - currentJob.yoloMetrics.boxLoss).toFixed(3) }}</span>
          </div>
        </div>
      </div>
      
      <!-- Total Loss -->
      <div class="metric-item total-loss">
        <div class="metric-icon"><Icon icon="ph:trend-down-fill" :width="24" /></div>
        <div class="metric-content">
          <div class="metric-label">总损失</div>
          <div class="metric-value">
            {{ (currentJob.yoloMetrics.boxLoss + currentJob.yoloMetrics.clsLoss + currentJob.yoloMetrics.objLoss).toFixed(4) }}
          </div>
          <div class="metric-trend down">
            <Icon icon="ph:arrow-down-right" :width="12" />
            <span>收敛中</span>
          </div>
        </div>
      </div>
    </div>
  </AnimatedCard>
</template>

<style scoped lang="scss">
.yolo-metrics-card {
  display: flex;
  flex-direction: column;
}

.metrics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border);
  flex-wrap: wrap;
  gap: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-badge {
  width: clamp(36px, 3.2vw, 44px);
  height: clamp(36px, 3.2vw, 44px);
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(74, 105, 255, 0.2), rgba(138, 43, 226, 0.2));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4A69FF;
  flex-shrink: 0;
}

.title {
  font-size: clamp(14px, 1.3vw, 18px);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 2px 0;
}

.subtitle {
  font-size: clamp(10px, 0.9vw, 12px);
  color: var(--color-text-secondary);
  margin: 0;
}

.epoch-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  background: linear-gradient(135deg, rgba(74, 105, 255, 0.15), rgba(138, 43, 226, 0.15));
  border-radius: 20px;
  font-size: clamp(10px, 0.9vw, 12px);
  font-weight: 600;
  color: var(--color-primary);
  
  svg {
    animation: spin 3s linear infinite;
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: clamp(8px, 1vw, 12px);
  
  @media (max-width: 1400px) {
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
  }
  
  @media (max-width: 900px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.metric-item {
  background: var(--color-surface-elevated);
  border-radius: 10px;
  padding: clamp(10px, 1vw, 14px);
  border: 1px solid var(--color-border);
  display: flex;
  align-items: flex-start;
  gap: 10px;
  transition: all 0.3s ease;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    border-radius: 10px 10px 0 0;
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  .dark & {
    background: rgba(30, 41, 59, 0.4);
  }
  
  &.map {
    &::before { background: linear-gradient(90deg, #10B981, #34D399); }
    .metric-icon { background: rgba(16, 185, 129, 0.15); color: #10B981; }
  }
  
  &.map-secondary {
    &::before { background: linear-gradient(90deg, #3B82F6, #60A5FA); }
    .metric-icon { background: rgba(59, 130, 246, 0.15); color: #3B82F6; }
  }
  
  &.precision {
    &::before { background: linear-gradient(90deg, #8B5CF6, #A78BFA); }
    .metric-icon { background: rgba(139, 92, 246, 0.15); color: #8B5CF6; }
  }
  
  &.recall {
    &::before { background: linear-gradient(90deg, #06B6D4, #22D3EE); }
    .metric-icon { background: rgba(6, 182, 212, 0.15); color: #06B6D4; }
  }
  
  &.loss, &.total-loss {
    &::before { background: linear-gradient(90deg, #EF4444, #F87171); }
    .metric-icon { background: rgba(239, 68, 68, 0.15); color: #EF4444; }
  }
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
    
    &::before { opacity: 1; }
    
    .dark & {
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
    }
  }
}

.metric-icon {
  width: clamp(32px, 2.8vw, 40px);
  height: clamp(32px, 2.8vw, 40px);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.metric-content {
  flex: 1;
  min-width: 0;
}

.metric-label {
  font-size: clamp(9px, 0.85vw, 11px);
  color: var(--color-text-secondary);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 2px;
}

.metric-value {
  font-size: clamp(16px, 1.5vw, 22px);
  font-weight: 800;
  color: var(--color-text-primary);
  line-height: 1.1;
}

.metric-trend {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: clamp(9px, 0.8vw, 11px);
  font-weight: 600;
  margin-top: 4px;
  
  &.up { color: #10B981; }
  &.down { color: #EF4444; }
}

.metric-bar {
  width: 100%;
  height: 5px;
  background: rgba(74, 105, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  margin-top: 6px;
}

.bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
  
  &.precision { background: linear-gradient(90deg, #8B5CF6, #A78BFA); }
  &.recall { background: linear-gradient(90deg, #06B6D4, #22D3EE); }
}
</style>

