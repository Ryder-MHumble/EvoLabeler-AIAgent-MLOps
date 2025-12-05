<script setup lang="ts">
/**
 * AgentPanel Component
 * 
 * 右侧 Agent 面板 - 显示 VLM 分析结果和置信度
 * 对话式情报中心
 */

import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useMissionStore } from '@/store/mission'

const missionStore = useMissionStore()

// 当前图像
const currentImage = computed(() => missionStore.currentImage)

// Agent 评论
const agentComment = computed(() => {
  return currentImage.value?.agentComment || '等待图像选择...'
})

// 总体置信度
const overallConfidence = computed(() => {
  return currentImage.value?.confidence || 0
})

// 检测到的对象列表
const detectedObjects = computed(() => {
  if (!currentImage.value) return []
  
  return currentImage.value.boundingBoxes.map(bbox => ({
    label: bbox.label || '未知对象',
    confidence: bbox.confidence,
    description: `置信度: ${Math.round(bbox.confidence * 100)}%`
  }))
})

// 获取置信度颜色
const getConfidenceColor = (confidence: number) => {
  if (confidence >= 0.8) return '#10b981'
  if (confidence >= 0.6) return '#eab308'
  return '#f97316'
}

// 获取置信度等级
const getConfidenceLevel = (confidence: number) => {
  if (confidence >= 0.8) return '高'
  if (confidence >= 0.6) return '中'
  return '低'
}
</script>

<template>
  <div class="agent-panel">
    <!-- 面板标题 -->
    <div class="panel-header">
      <div class="header-icon">
        <Icon icon="ph:robot-fill" :width="24" />
      </div>
      <div class="header-text">
        <h3 class="panel-title">Agent 分析</h3>
        <p class="panel-subtitle">VLM 智能分析结果</p>
      </div>
    </div>

    <!-- Agent 评论 -->
    <div class="agent-comment-section">
      <div class="section-label">
        <Icon icon="ph:chat-circle" :width="16" />
        <span>分析评论</span>
      </div>
      <div class="comment-content">
        <p>{{ agentComment }}</p>
      </div>
    </div>

    <!-- 置信度仪表 -->
    <div class="confidence-section">
      <div class="section-label">
        <Icon icon="ph:gauge" :width="16" />
        <span>总体置信度</span>
      </div>
      <div class="confidence-meter">
        <div class="meter-bar">
          <div
            class="meter-fill"
            :style="{
              width: `${overallConfidence * 100}%`,
              backgroundColor: getConfidenceColor(overallConfidence)
            }"
          ></div>
        </div>
        <div class="meter-info">
          <span class="meter-value">{{ Math.round(overallConfidence * 100) }}%</span>
          <span class="meter-level" :style="{ color: getConfidenceColor(overallConfidence) }">
            {{ getConfidenceLevel(overallConfidence) }}
          </span>
        </div>
      </div>
    </div>

    <!-- 检测到的对象 -->
    <div class="detected-objects-section">
      <div class="section-label">
        <Icon icon="ph:target" :width="16" />
        <span>检测对象 ({{ detectedObjects.length }})</span>
      </div>
      <div class="objects-list">
        <div
          v-for="(obj, index) in detectedObjects"
          :key="index"
          class="object-item"
        >
          <div class="object-icon">
            <Icon icon="ph:square" :width="16" />
          </div>
          <div class="object-info">
            <div class="object-label">{{ obj.label }}</div>
            <div class="object-desc">{{ obj.description }}</div>
          </div>
          <div
            class="object-confidence"
            :style="{ color: getConfidenceColor(obj.confidence) }"
          >
            {{ Math.round(obj.confidence * 100) }}%
          </div>
        </div>
        
        <div v-if="detectedObjects.length === 0" class="empty-objects">
          <Icon icon="ph:image-square" :width="32" />
          <p>暂无检测对象</p>
        </div>
      </div>
    </div>

    <!-- 操作建议 -->
    <div v-if="currentImage" class="recommendations-section">
      <div class="section-label">
        <Icon icon="ph:lightbulb" :width="16" />
        <span>操作建议</span>
      </div>
      <div class="recommendations-list">
        <div
          v-if="overallConfidence >= 0.8"
          class="recommendation-item success"
        >
          <Icon icon="ph:check-circle" :width="16" />
          <span>置信度高，建议自动确认</span>
        </div>
        <div
          v-else-if="overallConfidence >= 0.6"
          class="recommendation-item warning"
        >
          <Icon icon="ph:warning" :width="16" />
          <span>置信度中等，建议人工审核</span>
        </div>
        <div
          v-else
          class="recommendation-item error"
        >
          <Icon icon="ph:x-circle" :width="16" />
          <span>置信度较低，需要人工确认</span>
        </div>
        
        <div class="recommendation-item info">
          <Icon icon="ph:keyboard" :width="16" />
          <span>按空格键快速确认选中标注</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.agent-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
  border-radius: 16px;
  padding: 20px;
  overflow-y: auto;
  @include custom-scrollbar;
  gap: 20px;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--color-border);
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(74, 105, 255, 0.2), rgba(138, 43, 226, 0.2));
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  flex-shrink: 0;
}

.header-text {
  flex: 1;
}

.panel-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
}

.panel-subtitle {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin: 0;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 12px;
  
  svg {
    color: var(--color-primary);
  }
}

.agent-comment-section {
  padding: 16px;
  background: var(--color-surface-elevated);
  border-radius: 12px;
  border: 1px solid var(--color-border);
}

.comment-content {
  p {
    margin: 0;
    font-size: 14px;
    line-height: 1.6;
    color: var(--color-text-secondary);
  }
}

.confidence-section {
  padding: 16px;
  background: var(--color-surface-elevated);
  border-radius: 12px;
  border: 1px solid var(--color-border);
}

.confidence-meter {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meter-bar {
  width: 100%;
  height: 12px;
  background: rgba(74, 105, 255, 0.1);
  border-radius: 6px;
  overflow: hidden;
}

.meter-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.5s ease;
  box-shadow: 0 0 8px currentColor;
}

.meter-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.meter-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.meter-level {
  font-size: 13px;
  font-weight: 600;
}

.detected-objects-section {
  padding: 16px;
  background: var(--color-surface-elevated);
  border-radius: 12px;
  border: 1px solid var(--color-border);
}

.objects-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.object-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--color-surface);
  border-radius: 8px;
  border: 1px solid var(--color-border);
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateX(4px);
    border-color: var(--color-primary);
  }
}

.object-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: rgba(74, 105, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  flex-shrink: 0;
}

.object-info {
  flex: 1;
  min-width: 0;
}

.object-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.object-desc {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.object-confidence {
  font-size: 16px;
  font-weight: 700;
  flex-shrink: 0;
}

.empty-objects {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 32px 16px;
  color: var(--color-text-tertiary);
  
  p {
    margin: 0;
    font-size: 13px;
  }
}

.recommendations-section {
  padding: 16px;
  background: var(--color-surface-elevated);
  border-radius: 12px;
  border: 1px solid var(--color-border);
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recommendation-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  
  &.success {
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.2);
  }
  
  &.warning {
    background: rgba(234, 179, 8, 0.1);
    color: #eab308;
    border: 1px solid rgba(234, 179, 8, 0.2);
  }
  
  &.error {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.2);
  }
  
  &.info {
    background: rgba(74, 105, 255, 0.1);
    color: var(--color-primary);
    border: 1px solid rgba(74, 105, 255, 0.2);
  }
}
</style>


