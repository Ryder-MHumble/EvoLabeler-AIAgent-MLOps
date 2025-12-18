<script setup lang="ts">
/**
 * 画布工具栏组件
 * 包含工具选择、缩放控制、上传/导入/导出等功能
 */

import { Icon } from '@iconify/vue'
import type { ToolType } from '../constants/annotation'

const props = defineProps<{
  currentTool: ToolType
  zoomLevel: number
  minZoom: number
  maxZoom: number
  hasImage: boolean
  hasAnnotations: boolean
}>()

const emit = defineEmits<{
  setTool: [tool: ToolType]
  zoom: [delta: number]
  resetView: []
  upload: []
  importDataset: []
  export: []
  confirmAll: []
  clearSelection: []
}>()
</script>

<template>
  <div class="canvas-toolbar">
    <!-- 工具选择 -->
    <div class="toolbar-group">
      <button
        @click="emit('setTool', 'select')"
        :class="['tool-btn', { active: currentTool === 'select' }]"
        title="选择工具 (V)"
      >
        <Icon icon="ph:cursor" :width="20" />
      </button>
      <button
        @click="emit('setTool', 'draw')"
        :class="['tool-btn', { active: currentTool === 'draw' }]"
        title="绘制工具 (B)"
      >
        <Icon icon="ph:selection" :width="20" />
      </button>
      <button
        @click="emit('setTool', 'pan')"
        :class="['tool-btn', { active: currentTool === 'pan' }]"
        title="平移工具 (H)"
      >
        <Icon icon="ph:hand" :width="20" />
      </button>
    </div>
    
    <div class="toolbar-divider"></div>
    
    <!-- 缩放控制 -->
    <div class="toolbar-group">
      <button
        @click="emit('zoom', -0.25)"
        class="tool-btn"
        :disabled="zoomLevel <= minZoom"
        title="缩小 (-)"
      >
        <Icon icon="ph:minus" :width="18" />
      </button>
      <span class="zoom-label">{{ Math.round(zoomLevel * 100) }}%</span>
      <button
        @click="emit('zoom', 0.25)"
        class="tool-btn"
        :disabled="zoomLevel >= maxZoom"
        title="放大 (+)"
      >
        <Icon icon="ph:plus" :width="18" />
      </button>
      <button
        @click="emit('resetView')"
        class="tool-btn"
        title="重置视图 (0)"
      >
        <Icon icon="ph:arrows-in-simple" :width="18" />
      </button>
    </div>
    
    <div class="toolbar-divider"></div>
    
    <!-- 文件操作 -->
    <div class="toolbar-group">
      <button
        @click="emit('upload')"
        class="tool-btn upload"
        title="上传单张图像"
      >
        <Icon icon="ph:upload-simple" :width="18" />
        <span>上传</span>
      </button>
      <button
        @click="emit('importDataset')"
        class="tool-btn import"
        title="导入已标注数据集（支持YOLO/JSON格式）"
      >
        <Icon icon="ph:folder-open" :width="18" />
        <span>导入数据集</span>
      </button>
      <button
        v-if="hasAnnotations"
        @click="emit('export')"
        class="tool-btn export"
        title="导出标注"
      >
        <Icon icon="ph:export" :width="18" />
        <span>导出</span>
      </button>
    </div>
    
    <div class="toolbar-divider" v-if="hasImage"></div>
    
    <!-- 批量操作 -->
    <div class="toolbar-group" v-if="hasImage">
      <button
        @click="emit('confirmAll')"
        class="tool-btn success"
        title="确认所有标注"
      >
        <Icon icon="ph:check-circle" :width="20" />
        <span>全部确认</span>
      </button>
      <button
        @click="emit('clearSelection')"
        class="tool-btn clear"
        title="清除选择，返回上传状态"
      >
        <Icon icon="ph:x-circle" :width="20" />
        <span>清除选择</span>
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.canvas-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--color-surface-elevated);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 4px;
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: var(--color-border);
  margin: 0 8px;
}

.tool-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover:not(:disabled) {
    background: var(--color-surface);
    color: var(--color-text-primary);
    transform: translateY(-1px);
  }
  
  &.active {
    background: linear-gradient(135deg, rgba(74, 105, 255, 0.15), rgba(138, 43, 226, 0.15));
    color: var(--color-primary);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  // 带文字的按钮样式
  &.upload, &.import, &.export, &.success, &.clear {
    width: auto;
    padding: 0 12px;
    
    span {
      font-size: 13px;
      font-weight: 500;
    }
  }
  
  &.success {
    color: #10b981;
    &:hover { background: rgba(16, 185, 129, 0.1); }
  }
  
  &.upload {
    color: var(--color-primary);
    &:hover { background: rgba(74, 105, 255, 0.1); }
  }
  
  &.import {
    color: #8b5cf6;
    &:hover { background: rgba(139, 92, 246, 0.1); }
  }
  
  &.export {
    color: #f59e0b;
    &:hover { background: rgba(245, 158, 11, 0.1); }
  }
  
  &.clear {
    color: #6b7280;
    &:hover {
      background: rgba(107, 114, 128, 0.1);
      color: #374151;
    }
  }
}

.zoom-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  min-width: 45px;
  text-align: center;
}
</style>

