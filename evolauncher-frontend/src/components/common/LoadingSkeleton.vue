<script setup lang="ts">
/**
 * LoadingSkeleton — 骨架屏加载占位组件
 *
 * Props:
 *   variant: 'card' | 'text' | 'chart' — 骨架类型
 *   lines: number — 文本类型的行数 (default: 3)
 *   height: string — 自定义高度 (default: auto)
 */
defineProps<{
  variant?: 'card' | 'text' | 'chart'
  lines?: number
  height?: string
}>()
</script>

<template>
  <div
    class="loading-skeleton"
    :class="[`skeleton-${variant || 'card'}`]"
    :style="height ? { height } : {}"
  >
    <template v-if="variant === 'text'">
      <div
        v-for="i in (lines || 3)"
        :key="i"
        class="skeleton-line"
        :style="{ width: i === (lines || 3) ? '60%' : '100%' }"
      />
    </template>
    <template v-else-if="variant === 'chart'">
      <div class="skeleton-chart-header">
        <div class="skeleton-title" />
        <div class="skeleton-legend" />
      </div>
      <div class="skeleton-chart-body" />
    </template>
    <template v-else>
      <div class="skeleton-header">
        <div class="skeleton-icon" />
        <div class="skeleton-title" />
      </div>
      <div class="skeleton-body">
        <div class="skeleton-line" style="width: 90%" />
        <div class="skeleton-line" style="width: 75%" />
        <div class="skeleton-line" style="width: 60%" />
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">
.loading-skeleton {
  border-radius: 12px;
  background: var(--color-surface, #fff);
  border: 1px solid var(--color-border, rgba(0, 0, 0, 0.06));
  padding: 20px;
  overflow: hidden;
}

// Shimmer animation
@keyframes shimmer {
  0% { background-position: -200px 0; }
  100% { background-position: 200px 0; }
}

%shimmer-base {
  background: linear-gradient(
    90deg,
    rgba(0, 0, 0, 0.04) 25%,
    rgba(0, 0, 0, 0.08) 50%,
    rgba(0, 0, 0, 0.04) 75%
  );
  background-size: 400px 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: 6px;
}

// Card variant
.skeleton-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.skeleton-icon {
  @extend %shimmer-base;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  flex-shrink: 0;
}

.skeleton-title {
  @extend %shimmer-base;
  height: 16px;
  width: 120px;
}

.skeleton-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-line {
  @extend %shimmer-base;
  height: 12px;
}

// Chart variant
.skeleton-chart {
  min-height: 200px;
}

.skeleton-chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.skeleton-legend {
  @extend %shimmer-base;
  height: 12px;
  width: 180px;
}

.skeleton-chart-body {
  @extend %shimmer-base;
  height: 160px;
  border-radius: 8px;
}

// Text variant
.skeleton-text {
  padding: 12px 16px;
}
</style>
