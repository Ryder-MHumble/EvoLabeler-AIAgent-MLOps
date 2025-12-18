<script setup lang="ts">
/**
 * 空画布组件
 * 显示上传提示和拖拽区域
 */

import { Icon } from '@iconify/vue'

defineEmits<{
  upload: []
  dragover: [event: DragEvent]
  drop: [event: DragEvent]
}>()
</script>

<template>
  <div 
    class="empty-canvas"
    @dragover="$emit('dragover', $event)"
    @drop="$emit('drop', $event)"
  >
    <div class="empty-icon">
      <Icon icon="ph:image-square" :width="80" />
    </div>
    <h3>请选择或上传图像</h3>
    <p>从左侧选择图像或拖拽/点击上传开始标注</p>
    <button class="upload-btn" @click="$emit('upload')">
      <Icon icon="ph:upload-simple" :width="20" />
      <span>上传图像</span>
    </button>
  </div>
</template>

<style scoped lang="scss">
.empty-canvas {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 40px;
  text-align: center;
}

.empty-icon {
  width: 120px;
  height: 120px;
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(74, 105, 255, 0.1), rgba(138, 43, 226, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  opacity: 0.7;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.7; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.05); }
}

h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

p {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
}

.upload-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  margin-top: 16px;
  border: 2px dashed var(--color-primary);
  border-radius: 12px;
  background: rgba(74, 105, 255, 0.05);
  color: var(--color-primary);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover {
    background: rgba(74, 105, 255, 0.15);
    border-style: solid;
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(74, 105, 255, 0.2);
  }
  
  &:active {
    transform: translateY(0);
  }
}
</style>

