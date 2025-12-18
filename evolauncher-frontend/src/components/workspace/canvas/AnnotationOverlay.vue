<script setup lang="ts">
/**
 * 标注覆盖层组件
 * 渲染所有边界框和调整手柄
 */

import { Icon } from '@iconify/vue'
import type { BoundingBox } from '@/api/types'
import { RESIZE_HANDLES } from '../constants/annotation'
import { getConfidenceColor } from '../utils/annotation'

const props = defineProps<{
  boundingBoxes: BoundingBox[]
  selectedBBoxId: string | null
  currentTool: 'select' | 'draw' | 'pan'
  normalizeToSVG: (normalized: number, dimension: 'x' | 'y') => number
  scaledImageSize: { width: number; height: number }
  drawingRect: { x: number; y: number; width: number; height: number } | null
}>()

const emit = defineEmits<{
  bboxClick: [bbox: BoundingBox]
  bboxMouseDown: [bbox: BoundingBox, event: MouseEvent, handle?: string]
}>()

/**
 * 获取缩放后的边界框尺寸
 */
const getScaledBBoxSize = (bbox: BoundingBox) => ({
  width: bbox.width * props.scaledImageSize.width,
  height: bbox.height * props.scaledImageSize.height
})

/**
 * 获取调整手柄位置
 */
const getResizeHandlePosition = (bbox: BoundingBox, handle: string) => {
  const x = props.normalizeToSVG(bbox.x, 'x')
  const y = props.normalizeToSVG(bbox.y, 'y')
  const w = bbox.width * props.scaledImageSize.width
  const h = bbox.height * props.scaledImageSize.height
  
  const positions: Record<string, { x: number; y: number }> = {
    'nw': { x, y },
    'ne': { x: x + w, y },
    'sw': { x, y: y + h },
    'se': { x: x + w, y: y + h },
    'n': { x: x + w / 2, y },
    's': { x: x + w / 2, y: y + h },
    'e': { x: x + w, y: y + h / 2 },
    'w': { x, y: y + h / 2 }
  }
  
  return positions[handle] || { x: 0, y: 0 }
}
</script>

<template>
  <svg
    class="annotation-overlay"
    :width="scaledImageSize.width"
    :height="scaledImageSize.height"
  >
    <!-- 现有边界框 -->
    <g
      v-for="bbox in boundingBoxes"
      :key="bbox.id"
      @click.stop="emit('bboxClick', bbox)"
      @mousedown.stop="emit('bboxMouseDown', bbox, $event)"
      :class="[
        'bbox-group',
        { 'selected': selectedBBoxId === bbox.id },
        { 'confirmed': bbox.status === 'confirmed' }
      ]"
    >
      <!-- 边界框矩形 -->
      <rect
        :x="normalizeToSVG(bbox.x, 'x')"
        :y="normalizeToSVG(bbox.y, 'y')"
        :width="getScaledBBoxSize(bbox).width"
        :height="getScaledBBoxSize(bbox).height"
        :fill="getConfidenceColor(bbox.confidence)"
        :fill-opacity="bbox.status === 'confirmed' ? 0.15 : 0.08"
        :stroke="selectedBBoxId === bbox.id ? '#4A69FF' : getConfidenceColor(bbox.confidence)"
        :stroke-width="selectedBBoxId === bbox.id ? 3 : 2"
        :stroke-dasharray="bbox.status === 'pending' ? '6,4' : '0'"
        rx="4"
        class="bbox-rect"
      />
      
      <!-- 标签 -->
      <g class="bbox-label-group">
        <rect
          :x="normalizeToSVG(bbox.x, 'x')"
          :y="normalizeToSVG(bbox.y, 'y') - 24"
          :width="Math.max(60, (bbox.label?.length || 4) * 10 + 50)"
          height="22"
          :fill="selectedBBoxId === bbox.id ? '#4A69FF' : getConfidenceColor(bbox.confidence)"
          rx="4"
          class="bbox-label-bg"
        />
        <text
          :x="normalizeToSVG(bbox.x, 'x') + 6"
          :y="normalizeToSVG(bbox.y, 'y') - 8"
          fill="white"
          font-size="12"
          font-weight="600"
          class="bbox-label"
        >
          {{ bbox.label || '目标' }} {{ Math.round(bbox.confidence * 100) }}%
        </text>
      </g>
      
      <!-- 调整手柄（仅选中且在选择模式时显示） -->
      <template v-if="selectedBBoxId === bbox.id && currentTool === 'select'">
        <circle
          v-for="handle in RESIZE_HANDLES"
          :key="handle"
          :cx="getResizeHandlePosition(bbox, handle).x"
          :cy="getResizeHandlePosition(bbox, handle).y"
          r="6"
          fill="#4A69FF"
          stroke="white"
          stroke-width="2"
          class="resize-handle"
          :class="`handle-${handle}`"
          @mousedown.stop="emit('bboxMouseDown', bbox, $event, handle)"
        />
      </template>
    </g>
    
    <!-- 绘制中的边界框 -->
    <rect
      v-if="drawingRect"
      :x="drawingRect.x"
      :y="drawingRect.y"
      :width="drawingRect.width"
      :height="drawingRect.height"
      fill="rgba(74, 105, 255, 0.1)"
      stroke="#4A69FF"
      stroke-width="2"
      stroke-dasharray="8,4"
      rx="4"
      class="drawing-rect"
    />
  </svg>
</template>

<style scoped lang="scss">
.annotation-overlay {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
  user-select: none;
  z-index: 2;
  
  .bbox-group {
    pointer-events: all;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    
    .bbox-rect {
      transition: fill-opacity 0.2s ease, stroke 0.2s ease, stroke-width 0.2s ease;
    }
    
    &:hover .bbox-rect {
      fill-opacity: 0.15;
      stroke-width: 3;
    }
    
    &.selected .bbox-rect {
      fill-opacity: 0.2;
    }
    
    &.confirmed .bbox-rect {
      stroke-dasharray: 0;
    }
  }
  
  .bbox-label-group {
    pointer-events: none;
    user-select: none;
  }
  
  .bbox-label {
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  }
  
  .resize-handle {
    pointer-events: all;
    cursor: nwse-resize;
    transition: r 0.15s ease, fill 0.15s ease;
    
    &.handle-nw { cursor: nwse-resize; }
    &.handle-ne { cursor: nesw-resize; }
    &.handle-sw { cursor: nesw-resize; }
    &.handle-se { cursor: nwse-resize; }
    &.handle-n { cursor: ns-resize; }
    &.handle-s { cursor: ns-resize; }
    &.handle-e { cursor: ew-resize; }
    &.handle-w { cursor: ew-resize; }
    
    &:hover {
      r: 8;
      fill: #6366f1;
    }
  }
  
  .drawing-rect {
    animation: drawPulse 1s ease-in-out infinite;
  }
}

@keyframes drawPulse {
  0%, 100% { stroke-opacity: 1; }
  50% { stroke-opacity: 0.5; }
}
</style>

