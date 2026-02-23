<script setup lang="ts">
/**
 * ModelVersionsPanel - 模型版本面板
 *
 * 以表格形式展示模型版本列表，支持回滚操作。
 */

import { Icon } from '@iconify/vue'
import AnimatedCard from '@/components/common/AnimatedCard.vue'
import type { ModelVersion } from '@/api/models'

defineProps<{
  versions: ModelVersion[]
  isLoading: boolean
}>()

const emit = defineEmits<{
  rollback: [versionId: string]
}>()

/**
 * Format a metric value (0-1) to a percentage string with 1 decimal place.
 * Returns '--' for undefined/null values.
 */
function fmtPct(value: number | undefined | null): string {
  if (value === undefined || value === null) return '--'
  return `${(value * 100).toFixed(1)}%`
}
</script>

<template>
  <AnimatedCard class="model-versions-panel" :hoverable="false">
    <div class="panel-header">
      <h2 class="card-title">
        <Icon icon="ph:git-branch" :width="18" class="title-icon" />
        模型版本
      </h2>
    </div>

    <!-- Loading state -->
    <div v-if="isLoading" class="loading-state">
      <div class="skeleton-row" v-for="i in 3" :key="i" />
    </div>

    <!-- Empty state -->
    <div v-else-if="versions.length === 0" class="empty-state">
      <Icon icon="ph:package" :width="28" class="empty-icon" />
      <span>暂无模型版本</span>
    </div>

    <!-- Versions table -->
    <div v-else class="table-wrapper">
      <table class="versions-table">
        <thead>
          <tr>
            <th>Version</th>
            <th>Round</th>
            <th>mAP50</th>
            <th>Precision</th>
            <th>Recall</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="v in versions"
            :key="v.id"
            :class="{ 'row-active': v.isActive, 'row-best': v.isBest }"
          >
            <td class="col-version">
              <span class="version-name">{{ v.version }}</span>
              <el-tag v-if="v.isBest" size="small" type="warning" class="badge badge-best">
                最佳
              </el-tag>
              <el-tag v-if="v.isActive" size="small" class="badge badge-active">
                激活
              </el-tag>
            </td>
            <td class="col-round">{{ v.roundNumber }}</td>
            <td class="col-metric">{{ fmtPct(v.metrics.mAP50) }}</td>
            <td class="col-metric">{{ fmtPct(v.metrics.precision) }}</td>
            <td class="col-metric">{{ fmtPct(v.metrics.recall) }}</td>
            <td class="col-action">
              <el-button
                v-if="!v.isActive"
                size="small"
                plain
                @click="emit('rollback', v.id)"
              >
                回滚
              </el-button>
              <span v-else class="active-label">当前</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </AnimatedCard>
</template>

<style scoped lang="scss">
.model-versions-panel {
  display: flex;
  flex-direction: column;
}

.panel-header {
  margin-bottom: 12px;
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

.loading-state {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-row {
  height: 32px;
  background: var(--color-surface-elevated, #f1f5f9);
  border-radius: 6px;
  animation: shimmer 1.5s infinite;
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px 0;
  gap: 8px;

  .empty-icon {
    color: var(--color-text-tertiary);
  }

  span {
    font-size: 13px;
    color: var(--color-text-tertiary);
  }
}

.table-wrapper {
  overflow-x: auto;

  &::-webkit-scrollbar {
    height: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(74, 105, 255, 0.3);
    border-radius: 2px;
  }
}

.versions-table {
  width: 100%;
  border-collapse: collapse;
  font-size: clamp(11px, 1vw, 13px);

  th {
    text-align: left;
    padding: 8px 10px;
    font-weight: 600;
    color: var(--color-text-tertiary);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid var(--color-border);
    white-space: nowrap;
  }

  td {
    padding: 8px 10px;
    border-bottom: 1px solid var(--color-border);
    white-space: nowrap;
    color: var(--color-text-secondary);
  }

  tbody tr:last-child td {
    border-bottom: none;
  }

  tbody tr:hover {
    background: rgba(74, 105, 255, 0.04);
  }

  .row-active {
    background: rgba(74, 105, 255, 0.06);
  }

  .row-best {
    background: rgba(245, 158, 11, 0.04);
  }
}

.col-version {
  display: flex;
  align-items: center;
  gap: 6px;
}

.version-name {
  font-weight: 600;
  color: var(--color-text-primary);
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
}

.badge {
  font-size: 10px;
  padding: 0 6px;
  height: 18px;
  line-height: 18px;
}

.badge-best {
  // el-tag type="warning" handles the gold color
}

.badge-active {
  // el-tag default handles the blue color
}

.col-round {
  text-align: center;
  font-weight: 500;
}

.col-metric {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  font-weight: 500;
}

.col-action {
  text-align: right;
}

.active-label {
  font-size: 11px;
  color: var(--color-primary);
  font-weight: 600;
}
</style>
