<script setup lang="ts">
/**
 * LiveTerminal Component
 * 
 * 底部实时终端 - 显示 Agent 的思考过程日志
 * 可折叠，自动滚动到最新日志
 */

import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { Icon } from '@iconify/vue'
import { useMissionStore } from '@/store/mission'
import type { AgentLog } from '@/api/types'

const missionStore = useMissionStore()

// 终端展开/折叠状态
const isExpanded = ref(false)

// 终端引用
const terminalRef = ref<HTMLDivElement | null>(null)

// 日志列表
const logs = computed(() => missionStore.agentLogs)

// 切换展开/折叠
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

// 获取日志级别颜色
const getLogLevelColor = (level: AgentLog['level']) => {
  switch (level) {
    case 'success':
      return '#10b981'
    case 'warning':
      return '#eab308'
    case 'error':
      return '#ef4444'
    case 'info':
    default:
      return '#60a5fa'
  }
}

// 获取日志级别图标
const getLogLevelIcon = (level: AgentLog['level']) => {
  switch (level) {
    case 'success':
      return 'ph:check-circle'
    case 'warning':
      return 'ph:warning'
    case 'error':
      return 'ph:x-circle'
    case 'info':
    default:
      return 'ph:info'
  }
}

// 格式化时间
const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  })
}

// 自动滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (terminalRef.value && isExpanded.value) {
    terminalRef.value.scrollTop = terminalRef.value.scrollHeight
  }
}

// 监听日志变化，自动滚动
watch(logs, () => {
  scrollToBottom()
}, { deep: true })

// 监听展开状态，展开时滚动到底部
watch(isExpanded, (expanded) => {
  if (expanded) {
    scrollToBottom()
  }
})

onMounted(() => {
  // 加载初始日志
  missionStore.loadAgentLogs()
  // 启动日志流
  missionStore.startLogStream()
})

onUnmounted(() => {
  // 停止日志流
  missionStore.stopLogStream()
})
</script>

<template>
  <div class="live-terminal" :class="{ 'expanded': isExpanded }">
    <!-- 终端头部 -->
    <div class="terminal-header" @click="toggleExpanded">
      <div class="header-left">
        <Icon icon="ph:terminal" :width="18" />
        <span class="header-title">Agent 终端</span>
        <span class="log-count">{{ logs.length }}</span>
      </div>
      <div class="header-right">
        <Icon
          :icon="isExpanded ? 'ph:caret-down' : 'ph:caret-up'"
          :width="18"
          class="toggle-icon"
        />
      </div>
    </div>

    <!-- 终端内容 -->
    <div
      v-if="isExpanded"
      ref="terminalRef"
      class="terminal-content"
    >
      <div
        v-for="log in logs"
        :key="log.id"
        class="log-entry"
        :style="{ '--log-color': getLogLevelColor(log.level) }"
      >
        <div class="log-time">{{ formatTime(log.timestamp) }}</div>
        <div class="log-level">
          <Icon :icon="getLogLevelIcon(log.level)" :width="14" />
        </div>
        <div class="log-category">[{{ log.category }}]</div>
        <div class="log-message">{{ log.message }}</div>
      </div>
      
      <!-- 空状态 -->
      <div v-if="logs.length === 0" class="empty-logs">
        <Icon icon="ph:terminal-window" :width="32" />
        <p>等待 Agent 日志...</p>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.live-terminal {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 30px;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(12px);
  border-top: 1px solid rgba(74, 105, 255, 0.2);
  z-index: 1000;
  transition: height 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &.expanded {
    height: 200px;
  }
}

.terminal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 16px;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s ease;
  
  &:hover {
    background: rgba(74, 105, 255, 0.1);
  }
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #10b981;
  font-size: 13px;
  font-weight: 600;
  font-family: 'Monaco', 'Courier New', monospace;
}

.header-title {
  color: #10b981;
}

.log-count {
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
  font-size: 11px;
  font-weight: 700;
}

.header-right {
  display: flex;
  align-items: center;
  color: var(--color-text-secondary);
}

.toggle-icon {
  transition: transform 0.3s ease;
  
  .expanded & {
    transform: rotate(180deg);
  }
}

.terminal-content {
  height: calc(200px - 30px);
  overflow-y: auto;
  overflow-x: hidden;
  padding: 12px 16px;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
  @include custom-scrollbar;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.5);
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(74, 105, 255, 0.4);
    border-radius: 3px;
    
    &:hover {
      background: rgba(74, 105, 255, 0.6);
    }
  }
}

.log-entry {
  display: grid;
  grid-template-columns: 80px 20px auto 1fr;
  gap: 12px;
  padding: 4px 0;
  color: #10b981;
  transition: background 0.2s ease;
  
  &:hover {
    background: rgba(16, 185, 129, 0.05);
  }
}

.log-time {
  color: rgba(16, 185, 129, 0.6);
  font-size: 11px;
}

.log-level {
  display: flex;
  align-items: center;
  color: var(--log-color);
}

.log-category {
  color: rgba(16, 185, 129, 0.8);
  font-weight: 600;
}

.log-message {
  color: #10b981;
  word-break: break-word;
}

.empty-logs {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px 20px;
  color: rgba(16, 185, 129, 0.5);
  
  p {
    margin: 0;
    font-size: 13px;
  }
}
</style>


