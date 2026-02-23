<script setup lang="ts">
/**
 * ModelHealthCard - 模型健康状态卡片
 *
 * 展示模型的整体健康状况、健康检查列表和改进建议。
 */

import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import AnimatedCard from '@/components/common/AnimatedCard.vue'
import type { ModelHealthResponse } from '@/api/models'

const props = defineProps<{
  healthReport: ModelHealthResponse | null
  isLoading: boolean
}>()

/** Map overall status to visual config. */
const statusConfig = computed(() => {
  if (!props.healthReport) {
    return { icon: 'ph:question', color: '#94A3B8', label: '无模型', cssClass: 'status-none' }
  }

  const status = props.healthReport.healthReport.overallStatus.toLowerCase()

  if (status === 'healthy') {
    return { icon: 'ph:check-circle-fill', color: '#10B981', label: '健康', cssClass: 'status-healthy' }
  }
  if (status === 'warning') {
    return { icon: 'ph:warning-fill', color: '#F59E0B', label: '警告', cssClass: 'status-warning' }
  }
  if (status === 'critical') {
    return { icon: 'ph:x-circle-fill', color: '#EF4444', label: '严重', cssClass: 'status-critical' }
  }
  if (status === 'no_model') {
    return { icon: 'ph:question', color: '#94A3B8', label: '无模型', cssClass: 'status-none' }
  }

  return { icon: 'ph:question', color: '#94A3B8', label: status, cssClass: 'status-none' }
})

/** Version display string. */
const versionDisplay = computed(() => {
  if (!props.healthReport) return ''
  const parts: string[] = []
  if (props.healthReport.activeVersion) {
    parts.push(`${props.healthReport.activeVersion} (活跃)`)
  }
  if (props.healthReport.bestVersion) {
    parts.push(`${props.healthReport.bestVersion} (最佳)`)
  }
  return parts.join(' / ')
})
</script>

<template>
  <AnimatedCard class="model-health-card" :hoverable="false">
    <div class="card-header">
      <h2 class="card-title">
        <Icon icon="ph:heartbeat" :width="18" class="title-icon" />
        模型健康
      </h2>
    </div>

    <!-- Loading skeleton -->
    <div v-if="isLoading" class="loading-state">
      <div class="skeleton-circle" />
      <div class="skeleton-line wide" />
      <div class="skeleton-line" />
      <div class="skeleton-line" />
    </div>

    <!-- No data -->
    <div v-else-if="!healthReport" class="empty-state">
      <div class="status-circle status-none">
        <Icon icon="ph:question" :width="28" />
      </div>
      <span class="status-label">无模型</span>
    </div>

    <!-- Health display -->
    <template v-else>
      <!-- Overall status indicator -->
      <div class="status-section">
        <div class="status-circle" :class="statusConfig.cssClass">
          <Icon :icon="statusConfig.icon" :width="28" />
        </div>
        <div class="status-info">
          <span class="status-label" :style="{ color: statusConfig.color }">
            {{ statusConfig.label }}
          </span>
          <span v-if="versionDisplay" class="version-info">{{ versionDisplay }}</span>
        </div>
      </div>

      <!-- Health checks list -->
      <div v-if="healthReport.healthReport.checks.length > 0" class="checks-list">
        <div
          v-for="(check, idx) in healthReport.healthReport.checks"
          :key="idx"
          class="check-item"
        >
          <Icon
            :icon="check.passed ? 'ph:check-circle-fill' : 'ph:x-circle-fill'"
            :width="16"
            :class="check.passed ? 'check-pass' : 'check-fail'"
          />
          <span class="check-name">{{ check.name }}</span>
          <el-tag
            size="small"
            :type="check.severity === 'critical' ? 'danger' : check.severity === 'warning' ? 'warning' : 'info'"
            class="severity-badge"
          >
            {{ check.severity }}
          </el-tag>
          <span class="check-message">{{ check.message }}</span>
        </div>
      </div>

      <!-- Recommendation -->
      <div v-if="healthReport.healthReport.recommendation" class="recommendation">
        <Icon icon="ph:lightbulb" :width="14" class="rec-icon" />
        <span>{{ healthReport.healthReport.recommendation }}</span>
      </div>
    </template>
  </AnimatedCard>
</template>

<style scoped lang="scss">
.model-health-card {
  display: flex;
  flex-direction: column;
}

.card-header {
  margin-bottom: 14px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: clamp(13px, 1.2vw, 16px);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;

  .title-icon {
    color: var(--color-primary);
  }
}

// Loading state
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 16px 0;
}

.skeleton-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--color-surface-elevated, #f1f5f9);
  animation: shimmer 1.5s infinite;
}

.skeleton-line {
  height: 14px;
  width: 60%;
  background: var(--color-surface-elevated, #f1f5f9);
  border-radius: 4px;
  animation: shimmer 1.5s infinite;

  &.wide {
    width: 80%;
  }
}

@keyframes shimmer {
  0%,
  100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}

// Empty state
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 0;

  .status-label {
    font-size: 13px;
    color: var(--color-text-tertiary);
  }
}

// Status section
.status-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.status-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;

  &.status-healthy {
    background: rgba(16, 185, 129, 0.12);
    color: #10B981;
  }

  &.status-warning {
    background: rgba(245, 158, 11, 0.12);
    color: #F59E0B;
  }

  &.status-critical {
    background: rgba(239, 68, 68, 0.12);
    color: #EF4444;
  }

  &.status-none {
    background: var(--color-surface-elevated, #f1f5f9);
    color: #94A3B8;
  }
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.status-label {
  font-size: 16px;
  font-weight: 700;
}

.version-info {
  font-size: 11px;
  color: var(--color-text-tertiary);
  font-family: 'Monaco', 'Menlo', monospace;
}

// Health checks list
.checks-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.check-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  flex-wrap: wrap;
}

.check-pass {
  color: #10B981;
}

.check-fail {
  color: #EF4444;
}

.check-name {
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
}

.severity-badge {
  font-size: 10px;
  padding: 0 5px;
  height: 16px;
  line-height: 16px;
}

.check-message {
  color: var(--color-text-tertiary);
  font-size: 11px;
  flex: 1;
  min-width: 0;
}

// Recommendation
.recommendation {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 10px;
  background: rgba(74, 105, 255, 0.05);
  border-radius: 8px;
  border-left: 3px solid var(--color-primary);
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.5;

  .rec-icon {
    color: var(--color-primary);
    flex-shrink: 0;
    margin-top: 1px;
  }
}
</style>
