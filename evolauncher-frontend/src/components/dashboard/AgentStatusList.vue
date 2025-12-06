<script setup lang="ts">
/**
 * AgentStatusList - Agent 状态列表组件
 * 显示智能体状态概览
 */

import { Icon } from '@iconify/vue'
import AnimatedCard from '@/components/common/AnimatedCard.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import type { AgentStatus } from '@/mock/agents'

defineProps<{
  agents: AgentStatus[]
  isLoading: boolean
}>()
</script>

<template>
  <div class="telemetry-column">
    <div class="section-header-modern">
      <div class="section-header-left">
        <div class="section-icon-badge agents">
          <Icon icon="ph:robot-fill" :width="20" />
        </div>
        <div>
          <h2 class="section-title-modern">智能体状态</h2>
          <p class="section-desc-modern">{{ $t('dashboard.liveSnapshots') }}</p>
        </div>
      </div>
    </div>
    
    <div class="agents-list">
      <!-- Loading State -->
      <AnimatedCard
        v-if="isLoading"
        v-for="n in 4"
        :key="`agent-skeleton-${n}`"
        class="agent-card-compact"
        :hoverable="false"
      >
        <LoadingSkeleton type="title" width="40%" />
        <LoadingSkeleton type="text" width="80%" count="2" />
      </AnimatedCard>

      <!-- Agent Cards -->
      <AnimatedCard
        v-else
        v-for="agent in agents"
        :key="agent.id"
        class="agent-card-compact agent-card"
      >
        <div class="agent-compact-header">
          <div class="agent-avatar-small" :class="agent.mood">
            <Icon icon="ph:robot-fill" :width="18" />
          </div>
          <div class="agent-compact-info">
            <h3 class="agent-name-compact">{{ agent.displayName }}</h3>
            <p class="agent-role-compact">{{ agent.name }}</p>
          </div>
          <StatusBadge
            :status="agent.status === 'waiting' ? 'idle' : agent.status"
            :size="'small'"
          />
        </div>

        <div class="agent-compact-metrics">
          <div class="agent-compact-metric">
            <Icon icon="ph:gauge-fill" :width="14" />
            <span>{{ Math.round(agent.confidence * 100) }}%</span>
          </div>
          <div class="agent-compact-metric">
            <Icon icon="ph:lightning-fill" :width="14" />
            <span>{{ agent.throughput }}/min</span>
          </div>
          <div class="agent-compact-metric">
            <Icon icon="ph:check-circle-fill" :width="14" />
            <span>{{ Math.round(agent.metrics.successRate * 100) }}%</span>
          </div>
        </div>
      </AnimatedCard>
    </div>
  </div>
</template>

<style scoped lang="scss">
.telemetry-column {
  min-width: 0;
  
  @media (max-width: 1280px) {
    display: none;
  }
}

.section-header-modern {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--color-border);
}

.section-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-icon-badge {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  
  &.agents {
    background: linear-gradient(135deg, #8B5CF6, #A78BFA);
    box-shadow: 0 6px 16px rgba(139, 92, 246, 0.3);
  }
}

.section-title-modern {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
  line-height: 1.2;
}

.section-desc-modern {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0;
}

.agents-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.agent-card-compact {
  padding: 16px;
}

.agent-compact-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.agent-avatar-small {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(74, 105, 255, 0.25);

  &.stable {
    background: linear-gradient(135deg, #4A69FF, #7AA2F7);
  }

  &.alert {
    background: linear-gradient(135deg, #F59E0B, #F97316);
  }

  &.critical {
    background: linear-gradient(135deg, #EF4444, #F87171);
  }
}

.agent-compact-info {
  flex: 1;
  min-width: 0;
}

.agent-name-compact {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
  @include truncate;
}

.agent-role-compact {
  font-size: 11px;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.agent-compact-metrics {
  display: flex;
  gap: 16px;
  padding: 8px 12px;
  background: var(--color-surface-elevated);
  border-radius: 8px;
}

.agent-compact-metric {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  
  :deep(.iconify) {
    color: var(--color-primary);
  }
}
</style>

