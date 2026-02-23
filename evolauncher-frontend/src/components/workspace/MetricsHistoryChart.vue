<script setup lang="ts">
/**
 * MetricsHistoryChart - 指标趋势图
 *
 * SVG 折线图，展示模型各版本 mAP50、Precision、Recall 指标趋势。
 * 设计参考 LossChartCard.vue 的 SVG 绘制模式。
 */

import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import AnimatedCard from '@/components/common/AnimatedCard.vue'
import type { MetricsHistoryEntry } from '@/api/models'

const props = defineProps<{
  history: MetricsHistoryEntry[]
  isLoading: boolean
}>()

// Chart dimensions
const chartWidth = 600
const chartHeight = 180
const paddingLeft = 40
const paddingRight = 20
const paddingTop = 15
const paddingBottom = 25

const plotWidth = computed(() => chartWidth - paddingLeft - paddingRight)
const plotHeight = computed(() => chartHeight - paddingTop - paddingBottom)

/** Sort history by round number. */
const sortedHistory = computed(() =>
  [...props.history].sort((a, b) => a.roundNumber - b.roundNumber),
)

/** X scale: maps index to x coordinate. */
function xPos(index: number): number {
  const count = sortedHistory.value.length
  if (count <= 1) return paddingLeft + plotWidth.value / 2
  return paddingLeft + (index / (count - 1)) * plotWidth.value
}

/** Y scale: maps a metric value (0-1) to y coordinate. */
function yPos(value: number): number {
  const clamped = Math.max(0, Math.min(1, value))
  return paddingTop + (1 - clamped) * plotHeight.value
}

/** Build an SVG polyline points string for a given metric key. */
function buildLine(key: 'mAP50' | 'precision' | 'recall'): string {
  return sortedHistory.value
    .map((entry, i) => {
      const val = entry[key]
      if (val === undefined || val === null) return null
      return `${xPos(i)},${yPos(val)}`
    })
    .filter(Boolean)
    .join(' ')
}

/** Get the latest value for a metric key. */
function latestValue(key: 'mAP50' | 'precision' | 'recall'): string {
  if (sortedHistory.value.length === 0) return '--'
  const last = sortedHistory.value[sortedHistory.value.length - 1]
  const v = last[key]
  if (v === undefined || v === null) return '--'
  return (v * 100).toFixed(1) + '%'
}

/** Y-axis tick labels (0, 0.25, 0.5, 0.75, 1.0). */
const yTicks = [0, 0.25, 0.5, 0.75, 1.0]

/** X-axis labels (round numbers). */
const xLabels = computed(() =>
  sortedHistory.value.map((e) => `R${e.roundNumber}`),
)

/** Index of the best entry (where isBest === true). */
const bestIndex = computed(() =>
  sortedHistory.value.findIndex((e) => e.isBest),
)
</script>

<template>
  <AnimatedCard class="metrics-history-chart" :hoverable="false">
    <div class="chart-header">
      <h2 class="card-title">
        <Icon icon="ph:chart-line-up" :width="18" class="title-icon" />
        指标趋势
      </h2>
      <div class="chart-legend">
        <div class="legend-item">
          <span class="legend-dot map"></span>
          <span class="legend-label">mAP50</span>
          <span class="legend-value">{{ latestValue('mAP50') }}</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot precision"></span>
          <span class="legend-label">Precision</span>
          <span class="legend-value">{{ latestValue('precision') }}</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot recall"></span>
          <span class="legend-label">Recall</span>
          <span class="legend-value">{{ latestValue('recall') }}</span>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="loading-state">
      <div class="skeleton-chart" />
    </div>

    <!-- Empty -->
    <div v-else-if="history.length === 0" class="empty-state">
      <Icon icon="ph:chart-line" :width="28" class="empty-icon" />
      <span>暂无历史数据</span>
    </div>

    <!-- SVG Chart -->
    <div v-else class="chart-container">
      <svg
        :viewBox="`0 0 ${chartWidth} ${chartHeight}`"
        class="chart-svg"
        preserveAspectRatio="xMidYMid meet"
      >
        <!-- Grid lines -->
        <g class="grid">
          <line
            v-for="tick in yTicks"
            :key="`grid-${tick}`"
            :x1="paddingLeft"
            :y1="yPos(tick)"
            :x2="chartWidth - paddingRight"
            :y2="yPos(tick)"
            stroke="var(--color-border)"
            stroke-width="1"
            opacity="0.2"
          />
        </g>

        <!-- Y-axis labels -->
        <g class="y-labels">
          <text
            v-for="tick in yTicks"
            :key="`ylabel-${tick}`"
            :x="paddingLeft - 6"
            :y="yPos(tick) + 4"
            text-anchor="end"
            fill="var(--color-text-tertiary)"
            font-size="9"
          >
            {{ tick.toFixed(2) }}
          </text>
        </g>

        <!-- X-axis labels -->
        <g class="x-labels">
          <text
            v-for="(label, i) in xLabels"
            :key="`xlabel-${i}`"
            :x="xPos(i)"
            :y="chartHeight - 4"
            text-anchor="middle"
            fill="var(--color-text-tertiary)"
            font-size="9"
          >
            {{ label }}
          </text>
        </g>

        <!-- mAP50 line (blue) -->
        <polyline
          v-if="buildLine('mAP50')"
          :points="buildLine('mAP50')"
          fill="none"
          stroke="#4A69FF"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />

        <!-- Precision line (green) -->
        <polyline
          v-if="buildLine('precision')"
          :points="buildLine('precision')"
          fill="none"
          stroke="#10B981"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />

        <!-- Recall line (purple) -->
        <polyline
          v-if="buildLine('recall')"
          :points="buildLine('recall')"
          fill="none"
          stroke="#8B5CF6"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />

        <!-- Data point circles -->
        <g v-for="(entry, i) in sortedHistory" :key="`dots-${i}`">
          <circle
            v-if="entry.mAP50 != null"
            :cx="xPos(i)"
            :cy="yPos(entry.mAP50)"
            r="3"
            fill="#4A69FF"
          />
          <circle
            v-if="entry.precision != null"
            :cx="xPos(i)"
            :cy="yPos(entry.precision)"
            r="3"
            fill="#10B981"
          />
          <circle
            v-if="entry.recall != null"
            :cx="xPos(i)"
            :cy="yPos(entry.recall)"
            r="3"
            fill="#8B5CF6"
          />
        </g>

        <!-- Star marker on best entry -->
        <g v-if="bestIndex >= 0 && sortedHistory[bestIndex].mAP50 != null">
          <text
            :x="xPos(bestIndex)"
            :y="yPos(sortedHistory[bestIndex].mAP50!) - 8"
            text-anchor="middle"
            font-size="14"
            fill="#F59E0B"
          >
            &#9733;
          </text>
        </g>
      </svg>
    </div>
  </AnimatedCard>
</template>

<style scoped lang="scss">
.metrics-history-chart {
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 10px;
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

.chart-legend {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: clamp(10px, 0.9vw, 12px);
}

.legend-dot {
  width: 10px;
  height: 3px;
  border-radius: 2px;

  &.map {
    background: #4A69FF;
  }

  &.precision {
    background: #10B981;
  }

  &.recall {
    background: #8B5CF6;
  }
}

.legend-label {
  color: var(--color-text-tertiary);
  font-weight: 500;
}

.legend-value {
  color: var(--color-text-secondary);
  font-weight: 600;
  font-family: 'Monaco', monospace;
  font-size: 10px;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
}

.skeleton-chart {
  width: 100%;
  height: 160px;
  background: var(--color-surface-elevated, #f1f5f9);
  border-radius: 8px;
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
  height: 200px;
  gap: 8px;

  .empty-icon {
    color: var(--color-text-tertiary);
  }

  span {
    font-size: 13px;
    color: var(--color-text-tertiary);
  }
}

.chart-container {
  height: 200px;
  width: 100%;
}

.chart-svg {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
