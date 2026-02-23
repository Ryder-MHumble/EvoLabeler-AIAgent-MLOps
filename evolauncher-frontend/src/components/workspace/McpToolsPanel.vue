<script setup lang="ts">
/**
 * McpToolsPanel - MCP工具注册表面板
 * 显示模型上下文协议工具状态
 */

import { ref, onMounted, nextTick } from 'vue'
import { Icon } from '@iconify/vue'
import gsap from 'gsap'
import AnimatedCard from '@/components/common/AnimatedCard.vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import { fetchMcpToolStatus, type McpToolStatus } from '@/mock/mcpTools'
import { ElNotification } from 'element-plus'

const mcpRegistry = ref<McpToolStatus[]>([])
const isLoading = ref(true)

const loadMcpRegistry = async () => {
  isLoading.value = true
  try {
    mcpRegistry.value = await fetchMcpToolStatus()
    await nextTick()
    animateList()
  } catch (error) {
    console.error('MCP registry error', error)
    ElNotification.error({
      title: 'MCP Tools',
      message: 'Failed to query MCP tool registry.'
    })
  } finally {
    isLoading.value = false
  }
}

const animateList = () => {
  const rows = document.querySelectorAll('.mcp-item:not(.skeleton)')
  gsap.fromTo(
    rows,
    { opacity: 0, x: -10 },
    { opacity: 1, x: 0, duration: 0.3, stagger: 0.05, ease: 'power2.out', clearProps: 'all' }
  )
}

onMounted(() => {
  loadMcpRegistry()
})
</script>

<template>
  <AnimatedCard class="mcp-tools-panel" :hoverable="false">
    <div class="panel-header">
      <div class="header-left">
        <div class="icon-badge mcp">
          <Icon icon="ph:toolbox-fill" :width="18" />
        </div>
        <div>
          <h2 class="panel-title">MCP 工具注册表</h2>
          <p class="panel-subtitle">模型上下文协议工具编排</p>
        </div>
      </div>
      <div class="panel-badge">
        <span class="badge-value">{{ mcpRegistry.length }}</span>
        <span class="badge-label">工具</span>
      </div>
    </div>

    <div class="mcp-list">
      <div v-if="isLoading" v-for="i in 4" :key="`skeleton-${i}`" class="mcp-item skeleton">
        <LoadingSkeleton type="text" width="60%" />
      </div>

      <div
        v-else
        v-for="tool in mcpRegistry"
        :key="tool.id"
        class="mcp-item"
        :class="`mcp-${tool.status}`"
      >
        <div class="mcp-header">
          <div class="mcp-icon">
            <Icon 
              :icon="tool.name.includes('Scene') ? 'ph:map-pin-fill' :
                     tool.name.includes('Keyword') ? 'ph:key-fill' :
                     tool.name.includes('Quality') ? 'ph:shield-check-fill' :
                     'ph:cpu-fill'" 
              :width="16" 
            />
          </div>
          <div class="mcp-info">
            <h3 class="mcp-name">{{ tool.name }}</h3>
            <p class="mcp-desc">{{ tool.description }}</p>
          </div>
        </div>
        
        <div class="mcp-metrics">
          <div class="mcp-metric">
            <Icon icon="ph:clock-fill" :width="12" />
            <span class="metric-label">延迟</span>
            <span class="metric-value">{{ tool.latency }}ms</span>
          </div>
          <div class="mcp-metric">
            <Icon icon="ph:chart-bar-fill" :width="12" />
            <span class="metric-label">使用率</span>
            <span class="metric-value">{{ tool.usage }}%</span>
          </div>
          <div class="mcp-status" :class="tool.status">
            <span class="status-dot"></span>
            <span class="status-text">
              {{ tool.status === 'online' ? '在线' : tool.status === 'degraded' ? '降级' : '离线' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </AnimatedCard>
</template>

<style scoped lang="scss">
.mcp-tools-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
  flex-wrap: wrap;
  gap: 10px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.icon-badge {
  width: clamp(32px, 2.8vw, 38px);
  height: clamp(32px, 2.8vw, 38px);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  &.mcp {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(59, 130, 246, 0.15));
    color: #10B981;

    .dark & {
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.25), rgba(96, 165, 250, 0.25));
    }
  }
}

.panel-title {
  font-size: clamp(13px, 1.2vw, 16px);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 2px 0;
}

.panel-subtitle {
  font-size: clamp(10px, 0.9vw, 12px);
  color: var(--color-text-secondary);
  margin: 0;
}

.panel-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4px 12px;
  background: var(--color-surface-elevated);
  border-radius: 8px;
  min-width: 50px;
  
  .dark & { background: rgba(30, 41, 59, 0.5); }
}

.badge-value {
  font-size: clamp(14px, 1.3vw, 18px);
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1;
}

.badge-label {
  font-size: clamp(9px, 0.8vw, 11px);
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.mcp-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
  min-height: 0;
}

.mcp-item {
  background: var(--color-surface-elevated);
  border-radius: 12px;
  padding: 14px;
  border: 2px solid var(--color-border);
  transition: all 0.3s ease;
  position: relative;
  
  .dark & {
    background: rgba(30, 41, 59, 0.5);
    border-color: rgba(255, 255, 255, 0.15);
  }
  
  &.mcp-online {
    border-left: 4px solid #10B981;
  }
  
  &.mcp-degraded {
    border-left: 4px solid #F59E0B;
  }
  
  &.mcp-offline {
    border-left: 4px solid #EF4444;
  }
  
  &:hover {
    transform: translateX(4px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  }

  .dark &:hover {
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  }
  
  &.skeleton {
    background: transparent;
    border: none;
    box-shadow: none;
    transform: none;
  }
}

.mcp-header {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 10px;
}

.mcp-icon {
  width: clamp(30px, 2.8vw, 38px);
  height: clamp(30px, 2.8vw, 38px);
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(59, 130, 246, 0.2));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #10B981;
  flex-shrink: 0;

  .dark & {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.3), rgba(96, 165, 250, 0.3));
  }
}

.mcp-info {
  flex: 1;
  min-width: 0;
}

.mcp-name {
  font-size: clamp(13px, 1.15vw, 16px);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
  @include truncate;
}

.mcp-desc {
  font-size: clamp(10px, 0.9vw, 12px);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.4;
  @include line-clamp(2);
}

.mcp-metrics {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
  padding-top: 8px;
  border-top: 1px solid var(--color-border);
}

.mcp-metric {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: clamp(11px, 0.95vw, 13px);
  
  > svg {
    color: var(--color-text-tertiary);
    flex-shrink: 0;
  }
}

.metric-label {
  color: var(--color-text-tertiary);
  font-weight: 500;
}

.metric-value {
  color: var(--color-text-primary);
  font-weight: 700;
}

.mcp-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: clamp(10px, 0.9vw, 12px);
  font-weight: 600;
  margin-left: auto;
  
  &.online {
    background: rgba(16, 185, 129, 0.15);
    color: #10B981;
    
    .status-dot {
      background: #10B981;
      box-shadow: 0 0 6px rgba(16, 185, 129, 0.5);
    }
  }
  
  &.degraded {
    background: rgba(251, 191, 36, 0.15);
    color: #FBBF24;
    .status-dot { background: #FBBF24; }
  }
  
  &.offline {
    background: rgba(239, 68, 68, 0.15);
    color: #EF4444;
    .status-dot { background: #EF4444; }
  }
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}
</style>

