<script setup lang="ts">
/**
 * AgentTelemetryPanel - Agent遥测面板
 * 显示多智能体协作状态
 */

import { ref, onMounted, nextTick } from 'vue'
import { Icon } from '@iconify/vue'
import gsap from 'gsap'
import AnimatedCard from '@/components/common/AnimatedCard.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import { fetchAgentStatuses, type AgentStatus } from '@/mock/agents'
import { ElNotification } from 'element-plus'

const agentTelemetry = ref<AgentStatus[]>([])
const isLoading = ref(true)

const loadAgentTelemetry = async () => {
  isLoading.value = true
  try {
    agentTelemetry.value = await fetchAgentStatuses()
    await nextTick()
    animateCards()
  } catch (error) {
    console.error('Agent telemetry error', error)
    ElNotification.warning({
      title: 'Agents',
      message: 'Unable to sync agent telemetry snapshot.'
    })
  } finally {
    isLoading.value = false
  }
}

const animateCards = () => {
  const cards = document.querySelectorAll('.agent-card:not(.skeleton)')
  gsap.fromTo(
    cards,
    { opacity: 0, y: 16 },
    { opacity: 1, y: 0, duration: 0.4, stagger: 0.08, ease: 'power3.out', clearProps: 'all' }
  )
}

onMounted(() => {
  loadAgentTelemetry()
})
</script>

<template>
  <AnimatedCard class="agent-telemetry-panel" :hoverable="false">
    <div class="panel-header">
      <div class="header-left">
        <div class="icon-badge agent">
          <Icon icon="ph:robot-fill" :width="18" />
        </div>
        <div>
          <h2 class="panel-title">Agent 遥测</h2>
          <p class="panel-subtitle">多智能体协作状态监控</p>
        </div>
      </div>
      <div class="panel-badge">
        <span class="badge-value">{{ agentTelemetry.length }}</span>
        <span class="badge-label">活跃</span>
      </div>
    </div>

    <div class="agents-grid">
      <div v-if="isLoading" v-for="i in 4" :key="`skeleton-${i}`" class="agent-card skeleton">
        <LoadingSkeleton type="title" width="50%" />
        <LoadingSkeleton type="text" width="80%" :count="2" />
      </div>

      <div
        v-else
        v-for="agent in agentTelemetry"
        :key="agent.id"
        class="agent-card"
        :class="`agent-${agent.status}`"
      >
        <div class="agent-header">
          <div class="agent-icon">
            <Icon 
              :icon="agent.name.includes('INFERENCE') ? 'ph:lightning-fill' :
                     agent.name.includes('ANALYSIS') ? 'ph:brain-fill' :
                     agent.name.includes('ACQUISITION') ? 'ph:download-fill' :
                     'ph:gear-fill'" 
              :width="18" 
            />
          </div>
          <div class="agent-info">
            <h3 class="agent-name">{{ agent.displayName }}</h3>
            <span class="agent-id">{{ agent.name }}</span>
          </div>
          <div class="agent-status" :class="agent.status">
            <span class="status-dot"></span>
            <span class="status-text">{{ agent.status === 'running' ? '运行中' : agent.status === 'waiting' ? '等待' : '空闲' }}</span>
          </div>
        </div>
        
        <p class="agent-desc">{{ agent.description }}</p>

        <div class="agent-metrics">
          <div class="metric">
            <Icon icon="ph:gauge-fill" :width="13" />
            <div class="metric-content">
              <span class="metric-label">置信度</span>
              <span class="metric-value">{{ Math.round(agent.confidence * 100) }}%</span>
            </div>
          </div>
          <div class="metric">
            <Icon icon="ph:arrow-clockwise-fill" :width="13" />
            <div class="metric-content">
              <span class="metric-label">吞吐量</span>
              <span class="metric-value">{{ agent.throughput }}/min</span>
            </div>
          </div>
          <div class="metric">
            <Icon icon="ph:check-circle-fill" :width="13" />
            <div class="metric-content">
              <span class="metric-label">已处理</span>
              <span class="metric-value">{{ agent.metrics.processed }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AnimatedCard>
</template>

<style scoped lang="scss">
.agent-telemetry-panel {
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-badge {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  &.agent {
    background: linear-gradient(135deg, rgba(74, 105, 255, 0.15), rgba(138, 43, 226, 0.15));
    color: #4A69FF;
  }
}

.panel-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 2px 0;
}

.panel-subtitle {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin: 0;
}

.panel-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6px 14px;
  background: var(--color-surface-elevated);
  border-radius: 10px;
  min-width: 56px;
  
  .dark & { background: rgba(30, 41, 59, 0.5); }
}

.badge-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1;
}

.badge-label {
  font-size: 11px;
  color: var(--color-text-secondary);
  margin-top: 2px;
}

// 更紧凑的卡片网格
.agents-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  
  @media (max-width: 1400px) {
    gap: 10px;
  }
  
  @media (max-width: 1200px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
}

// 更紧凑的卡片设计
.agent-card {
  background: var(--color-surface-elevated);
  border-radius: 14px;
  padding: 14px 16px;
  border: 2px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 10px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #4A69FF, #8B5CF6);
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  .dark & {
    background: rgba(30, 41, 59, 0.5);
    border-color: rgba(255, 255, 255, 0.15);
  }
  
  &.agent-running {
    border-color: rgba(16, 185, 129, 0.5);
    
    &::before {
      opacity: 1;
      background: linear-gradient(90deg, #10B981, #34D399);
    }
  }
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    border-color: var(--color-primary);
    
    &::before { opacity: 1; }
    
    .dark & { box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3); }
  }
  
  &.skeleton {
    background: transparent;
    border: none;
    box-shadow: none;
    transform: none;
    
    &::before { display: none; }
  }
}

.agent-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.agent-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(74, 105, 255, 0.2), rgba(138, 43, 226, 0.2));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4A69FF;
  flex-shrink: 0;
}

.agent-info {
  flex: 1;
  min-width: 0;
}

.agent-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 2px 0;
  line-height: 1.2;
  @include truncate;
}

.agent-id {
  font-size: 11px;
  color: var(--color-text-tertiary);
  font-family: 'Monaco', 'Courier New', monospace;
  @include truncate;
}

.agent-status {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
  
  &.running {
    background: rgba(16, 185, 129, 0.15);
    color: #10B981;
    
    .status-dot {
      background: #10B981;
      box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
      animation: pulse 2s ease-in-out infinite;
    }
  }
  
  &.waiting {
    background: rgba(251, 191, 36, 0.15);
    color: #FBBF24;
    .status-dot { background: #FBBF24; }
  }
  
  &.idle {
    background: rgba(156, 163, 175, 0.15);
    color: #9CA3AF;
    .status-dot { background: #9CA3AF; }
  }
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.15); }
}

.agent-desc {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.5;
  @include line-clamp(2);
}

// 紧凑的指标行布局
.agent-metrics {
  display: flex;
  gap: 8px;
  padding-top: 10px;
  border-top: 1px solid var(--color-border);
}

.metric {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: rgba(74, 105, 255, 0.06);
  border-radius: 10px;
  
  .dark & { background: rgba(96, 165, 250, 0.12); }
  
  > svg {
    color: #4A69FF;
    flex-shrink: 0;
    width: 16px;
    height: 16px;
  }
}

.metric-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
  gap: 2px;
}

.metric-label {
  font-size: 10px;
  color: var(--color-text-tertiary);
  font-weight: 500;
  @include truncate;
}

.metric-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary);
  @include truncate;
}
</style>

