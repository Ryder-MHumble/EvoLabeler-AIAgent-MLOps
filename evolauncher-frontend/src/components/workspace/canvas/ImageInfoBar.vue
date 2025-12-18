<script setup lang="ts">
/**
 * 图像信息栏组件
 * 显示图像ID、尺寸、标注数量等信息
 */

import { Icon } from '@iconify/vue'
import type { ImageTask } from '@/api/types'

defineProps<{
  image: ImageTask
  imageWidth: number
  imageHeight: number
}>()
</script>

<template>
  <div class="image-info-bar">
    <div class="info-item">
      <Icon icon="ph:info" :width="16" />
      <span>{{ image.id }}</span>
    </div>
    
    <div class="info-item" v-if="imageWidth > 0">
      <Icon icon="ph:frame-corners" :width="16" />
      <span>{{ imageWidth }}×{{ imageHeight }}</span>
    </div>
    
    <div class="info-item">
      <Icon icon="ph:square" :width="16" />
      <span>{{ image.boundingBoxes.length }} 个标注</span>
    </div>
    
    <div class="info-item">
      <Icon icon="ph:source" :width="16" />
      <span>{{ 
        image.source === 'crawler' ? '爬虫' : 
        image.source === 'agent_recommended' ? 'Agent推荐' : 
        '本地上传' 
      }}</span>
    </div>
    
    <div class="info-item hint">
      <Icon icon="ph:keyboard" :width="16" />
      <span>V选择 | B绘制 | H平移 | 0重置 | ±缩放</span>
    </div>
  </div>
</template>

<style scoped lang="scss">
.image-info-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: var(--color-surface-elevated);
  border-top: 1px solid var(--color-border);
  flex-wrap: wrap;
  flex-shrink: 0;
  min-height: 48px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--color-text-secondary);
  
  svg {
    color: var(--color-primary);
    flex-shrink: 0;
  }
  
  span {
    white-space: nowrap;
  }
  
  &.hint {
    margin-left: auto;
    color: var(--color-text-tertiary);
    font-size: 12px;
    background: rgba(74, 105, 255, 0.08);
    padding: 4px 10px;
    border-radius: 6px;
    
    @media (max-width: 1200px) {
      display: none;
    }
  }
}
</style>

