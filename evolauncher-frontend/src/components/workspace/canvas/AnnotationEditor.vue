<script setup lang="ts">
/**
 * 标注编辑面板组件
 * 显示和编辑选中标注框的属性
 */

import { Icon } from '@iconify/vue'
import type { BoundingBox } from '@/api/types'
import { LABEL_OPTIONS } from '../constants/annotation'
import { getConfidenceColor } from '../utils/annotation'

const props = defineProps<{
  bbox: BoundingBox
}>()

const emit = defineEmits<{
  updateLabel: [label: string]
  confirm: []
  delete: []
}>()
</script>

<template>
  <div class="annotation-editor">
    <div class="editor-header">
      <Icon icon="ph:pencil-simple" :width="18" />
      <span>编辑标注</span>
    </div>
    
    <div class="editor-body">
      <div class="editor-row">
        <label>标签</label>
        <select 
          :value="bbox.label"
          @change="emit('updateLabel', ($event.target as HTMLSelectElement).value)"
          class="label-select"
        >
          <option v-for="label in LABEL_OPTIONS" :key="label" :value="label">
            {{ label }}
          </option>
        </select>
      </div>
      
      <div class="editor-row">
        <label>置信度</label>
        <span 
          class="confidence-value" 
          :style="{ color: getConfidenceColor(bbox.confidence) }"
        >
          {{ Math.round(bbox.confidence * 100) }}%
        </span>
      </div>
      
      <div class="editor-row">
        <label>状态</label>
        <span :class="['status-badge', bbox.status]">
          {{ bbox.status === 'confirmed' ? '已确认' : '待确认' }}
        </span>
      </div>
    </div>
    
    <div class="editor-actions">
      <button 
        @click="emit('confirm')"
        class="action-btn confirm"
        :disabled="bbox.status === 'confirmed'"
      >
        <Icon icon="ph:check" :width="16" />
        确认
      </button>
      <button 
        @click="emit('delete')" 
        class="action-btn delete"
      >
        <Icon icon="ph:trash" :width="16" />
        删除
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.annotation-editor {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 220px;
  background: var(--color-surface-elevated);
  border-radius: 12px;
  border: 1px solid var(--color-border);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  z-index: 10;
  animation: slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  .dark & {
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.55);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.editor-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  background: linear-gradient(135deg, rgba(74, 105, 255, 0.1), rgba(138, 43, 226, 0.1));
  border-bottom: 1px solid var(--color-border);
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
  
  svg {
    color: var(--color-primary);
  }
}

.editor-body {
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.editor-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  label {
    font-size: 12px;
    color: var(--color-text-secondary);
    font-weight: 500;
  }
}

.label-select {
  padding: 6px 10px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 12px;
  cursor: pointer;
  outline: none;
  min-width: 100px;
  transition: border-color 0.2s ease;
  
  &:focus {
    border-color: var(--color-primary);
  }
  
  &:hover {
    border-color: var(--color-primary);
  }
}

.confidence-value {
  font-size: 14px;
  font-weight: 700;
}

.status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  
  &.pending {
    background: rgba(234, 179, 8, 0.15);
    color: #eab308;

    .dark & {
      background: rgba(234, 179, 8, 0.25);
    }
  }

  &.confirmed {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;

    .dark & {
      background: rgba(16, 185, 129, 0.25);
    }
  }
}

.editor-actions {
  display: flex;
  gap: 8px;
  padding: 12px 14px;
  border-top: 1px solid var(--color-border);
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  
  &.confirm {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
    
    &:hover:not(:disabled) {
      background: rgba(16, 185, 129, 0.25);
      transform: translateY(-1px);
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
  
  &.delete {
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    
    &:hover {
      background: rgba(239, 68, 68, 0.25);
      transform: translateY(-1px);
    }
  }
}
</style>

