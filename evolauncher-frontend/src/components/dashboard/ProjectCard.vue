<script setup lang="ts">
/**
 * ProjectCard - 项目卡片组件
 * 展示项目缩略图、状态、统计信息、EvoLoop状态指示器
 */

import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import AnimatedCard from '@/components/common/AnimatedCard.vue'
import type { Project } from '@/mock/projects'

const props = defineProps<{
  project: Project
}>()

const emit = defineEmits<{
  (e: 'click', project: Project): void
}>()

// ========== EvoLoop Status Indicators ==========
// TODO: These placeholder values should come from a real API endpoint
// (e.g., modelsApi.getHealth / modelsApi.listRounds) per project in the future.

/** Show EvoLoop row only for training or completed projects */
const showEvoLoop = computed(() =>
  props.project.status === 'training' || props.project.status === 'completed'
)

/** Placeholder EvoLoop round count */
const evoRoundCount = 3

/** Placeholder mAP50 score (percentage) */
const latestMapScore = 85

/** Placeholder health status */
const healthStatus: 'healthy' | 'warning' | 'critical' = 'healthy'

const healthColor = computed(() => {
  switch (healthStatus) {
    case 'healthy': return '#10B981'
    case 'warning': return '#F59E0B'
    case 'critical': return '#EF4444'
    default: return '#94A3B8'
  }
})
</script>

<template>
  <AnimatedCard
    class="project-card"
    :hoverable="true"
    :clickable="true"
    @click="emit('click', project)"
    padding="0"
  >
    <!-- Project Thumbnail Image -->
    <div class="project-thumbnail">
      <img 
        :src="project.thumbnailUrl || `https://picsum.photos/seed/${project.id}/400/300`" 
        :alt="project.name"
        class="project-image"
      />
      <!-- Status Tag -->
      <div class="project-tag-wrapper">
        <div class="project-tag" :class="`tag-${project.status}`">
          <span class="tag-dot"></span>
          <span class="tag-text">{{ $t(`project.status.${project.status}`) }}</span>
        </div>
      </div>
      <!-- Gradient Overlay -->
      <div class="project-image-overlay"></div>
    </div>
    
    <!-- Bottom Section with Info -->
    <div class="project-bottom-section">
      <h3 class="project-title">{{ project.name }}</h3>
      <p class="project-description" v-if="project.description">
        {{ project.description }}
      </p>
      
      <div class="project-stats-row">
        <div class="stat-item">
          <span class="stat-value">{{ project.imageCount }}</span>
          <span class="stat-label">图像数</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ project.accuracy || 0 }}%</span>
          <span class="stat-label">准确率</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ project.status === 'completed' ? '✓' : '•' }}</span>
          <span class="stat-label">状态</span>
        </div>
      </div>

      <!-- EvoLoop Status Indicator Row -->
      <!-- TODO: Replace placeholder data with real per-project model API data -->
      <div v-if="showEvoLoop" class="evoloop-row">
        <div class="evoloop-item">
          <Icon icon="ph:arrows-clockwise" :width="14" class="evoloop-icon" />
          <span class="evoloop-badge">Round {{ evoRoundCount }}</span>
        </div>
        <div class="evoloop-item">
          <Icon icon="ph:chart-line-up" :width="14" class="evoloop-icon" />
          <span class="evoloop-metric">mAP50: {{ latestMapScore }}%</span>
        </div>
        <div class="evoloop-item">
          <span class="evoloop-health-dot" :style="{ backgroundColor: healthColor }"></span>
          <span class="evoloop-health-label">{{ healthStatus }}</span>
        </div>
      </div>
    </div>
  </AnimatedCard>
</template>

<style scoped lang="scss">
.project-card {
  cursor: pointer;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);

  &:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
    
    .project-image { transform: scale(1.1); }
    .project-tag { transform: translateX(-4px); }
  }
  
  .dark & {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    &:hover { box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6); }
  }
}

.project-thumbnail {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.project-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.project-image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60%;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.7) 0%,
    rgba(0, 0, 0, 0.3) 50%,
    transparent 100%
  );
  pointer-events: none;
}

.project-tag-wrapper {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2;
}

.project-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 50px;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);

  .dark & {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    border-color: rgba(255, 255, 255, 0.1);
  }

  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  
  &.tag-idle {
    background: rgba(148, 163, 184, 0.95);
    color: white;
    .tag-dot { background: white; box-shadow: 0 0 8px rgba(255, 255, 255, 0.8); }
  }
  
  &.tag-training {
    background: rgba(59, 130, 246, 0.95);
    color: white;
    .tag-dot { background: white; animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
  }
  
  &.tag-labeling {
    background: rgba(139, 92, 246, 0.95);
    color: white;
    .tag-dot { background: white; animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
  }
  
  &.tag-completed {
    background: rgba(16, 185, 129, 0.95);
    color: white;
    .tag-dot { background: white; box-shadow: 0 0 8px rgba(255, 255, 255, 0.8); }
  }
  
  &.tag-error {
    background: rgba(239, 68, 68, 0.95);
    color: white;
    .tag-dot { background: white; box-shadow: 0 0 8px rgba(255, 255, 255, 0.8); }
  }
}

.tag-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

@keyframes pulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 8px rgba(255, 255, 255, 0.8); }
  50% { opacity: 0.5; box-shadow: 0 0 4px rgba(255, 255, 255, 0.4); }
}

.project-bottom-section {
  padding: 16px;
}

.project-title {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  text-align: center;
  margin: 0 0 8px 0;
  @include truncate;
}

.project-description {
  font-size: 13px;
  color: var(--color-text-secondary);
  text-align: center;
  @include line-clamp(2);
  margin: 0 0 16px 0;
  min-height: 2.4em;
}

.project-stats-row {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}

.stat-item {
  flex: 1;
  text-align: center;
  padding: 4px;
  
  &:nth-child(2) {
    border-left: 1px solid var(--color-border);
    border-right: 1px solid var(--color-border);
  }
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  display: block;
  color: var(--color-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 11px;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

// ========== EvoLoop Status Row ==========
.evoloop-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px dashed var(--color-border);
}

.evoloop-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.evoloop-icon {
  color: var(--color-primary);
  flex-shrink: 0;
}

.evoloop-badge {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-secondary);
  background: rgba(74, 105, 255, 0.1);
  padding: 2px 8px;
  border-radius: 10px;

  .dark & {
    background: rgba(96, 165, 250, 0.2);
  }
}

.evoloop-metric {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.evoloop-health-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: 0 0 6px currentColor;

  .dark & {
    box-shadow: 0 0 8px currentColor, 0 0 12px currentColor;
  }
}

.evoloop-health-label {
  font-size: 11px;
  font-weight: 500;
  color: var(--color-text-tertiary);
  text-transform: capitalize;
}
</style>

