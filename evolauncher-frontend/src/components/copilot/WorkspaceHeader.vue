<script setup lang="ts">
/**
 * WorkspaceHeader - CoPilot 工作区顶部状态栏
 * 显示项目信息、标注进度、快捷键帮助
 */

import { ref } from 'vue'
import { Icon } from '@iconify/vue'

defineProps<{
  projectName: string
  projectBadge: string
  progress: {
    total: number
    completed: number
    pending: number
    incoming: number
    percentage: number
  }
}>()

// 快捷键显示
const showShortcuts = ref(false)

// 快捷键列表
const shortcuts = [
  { key: 'V', action: '选择工具' },
  { key: 'B', action: '绘制工具' },
  { key: '空格', action: '确认选中标注' },
  { key: 'Delete', action: '删除选中标注' },
  { key: '+/-', action: '缩放画布' },
  { key: '鼠标拖拽', action: '移动标注框' }
]
</script>

<template>
  <div class="workspace-header">
    <div class="header-left">
      <div class="project-info">
        <Icon icon="ph:folder-open-fill" :width="18" class="project-icon" />
        <span class="project-name">{{ projectName }}</span>
        <span class="project-badge">{{ projectBadge }}</span>
      </div>
    </div>
    
    <div class="header-center">
      <!-- 标注进度条 -->
      <div class="progress-bar-container">
        <div class="progress-stats">
          <span class="progress-text">标注进度</span>
          <span class="progress-value">{{ progress.percentage }}%</span>
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${progress.percentage}%` }"
          ></div>
        </div>
        <div class="progress-details">
          <span>{{ progress.completed }}/{{ progress.total }} 已完成</span>
          <span class="pending-count" v-if="progress.pending > 0">
            · {{ progress.pending }} 待确认
          </span>
        </div>
      </div>
    </div>
    
    <div class="header-right">
      <!-- 快捷键提示 -->
      <button 
        class="shortcuts-btn"
        @click="showShortcuts = !showShortcuts"
        title="快捷键帮助"
      >
        <Icon icon="ph:keyboard" :width="18" />
        <span>快捷键</span>
      </button>
      
      <!-- 快捷键面板 -->
      <div v-if="showShortcuts" class="shortcuts-panel">
        <div class="shortcuts-header">
          <Icon icon="ph:keyboard-fill" :width="16" />
          <span>快捷键列表</span>
          <button class="close-btn" @click="showShortcuts = false">
            <Icon icon="ph:x" :width="14" />
          </button>
        </div>
        <div class="shortcuts-list">
          <div 
            v-for="shortcut in shortcuts" 
            :key="shortcut.key"
            class="shortcut-item"
          >
            <kbd>{{ shortcut.key }}</kbd>
            <span>{{ shortcut.action }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.workspace-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.project-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.project-icon {
  color: var(--color-primary);
}

.project-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.project-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
  background: linear-gradient(135deg, rgba(74, 105, 255, 0.15), rgba(138, 43, 226, 0.15));
  color: var(--color-primary);
}

.header-center {
  flex: 1;
  max-width: 400px;
}

.progress-bar-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-text {
  font-size: 11px;
  color: var(--color-text-tertiary);
  font-weight: 500;
}

.progress-value {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-primary);
}

.progress-bar {
  height: 6px;
  background: rgba(74, 105, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4A69FF, #8B5CF6);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-details {
  font-size: 11px;
  color: var(--color-text-tertiary);
  display: flex;
  gap: 4px;
}

.pending-count {
  color: #F59E0B;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

.shortcuts-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-surface-elevated);
  color: var(--color-text-secondary);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(74, 105, 255, 0.1);
    border-color: var(--color-primary);
    color: var(--color-primary);
  }
}

.shortcuts-panel {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  width: 220px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  z-index: 100;
  overflow: hidden;
}

.shortcuts-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--color-surface-elevated);
  border-bottom: 1px solid var(--color-border);
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
  
  .close-btn {
    margin-left: auto;
    background: none;
    border: none;
    color: var(--color-text-tertiary);
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    display: flex;
    
    &:hover {
      background: rgba(239, 68, 68, 0.1);
      color: #EF4444;
    }
  }
}

.shortcuts-list {
  padding: 8px;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 10px;
  border-radius: 6px;
  
  &:hover {
    background: var(--color-surface-elevated);
  }
  
  kbd {
    min-width: 60px;
    padding: 4px 8px;
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    font-size: 11px;
    font-family: 'Monaco', 'Courier New', monospace;
    font-weight: 600;
    color: var(--color-text-primary);
    text-align: center;
  }
  
  span {
    font-size: 12px;
    color: var(--color-text-secondary);
  }
}
</style>

