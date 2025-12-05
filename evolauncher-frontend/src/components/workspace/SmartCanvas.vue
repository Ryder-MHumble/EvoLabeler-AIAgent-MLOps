<script setup lang="ts">
/**
 * SmartCanvas Component
 * 
 * 中间智能画布 - 显示图像和 Agent 标注的覆盖层
 * 支持交互式编辑边界框（拖动和调整大小）
 */

import { computed, ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { Icon } from '@iconify/vue'
import { useMissionStore } from '@/store/mission'
import type { BoundingBox } from '@/api/types'

const missionStore = useMissionStore()

// 画布引用
const canvasRef = ref<HTMLDivElement | null>(null)
const imageRef = ref<HTMLImageElement | null>(null)
const svgRef = ref<SVGSVGElement | null>(null)

// 当前图像
const currentImage = computed(() => missionStore.currentImage)

// 选中的边界框
const selectedBBox = ref<string | null>(null)

// 图像加载状态
const imageLoaded = ref(false)

// 画布尺寸和图像实际尺寸
const canvasSize = ref({ width: 0, height: 0 })
const imageSize = ref({ width: 0, height: 0, naturalWidth: 0, naturalHeight: 0 })
const imageScale = ref({ x: 1, y: 1 })

// 拖动状态
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0, bbox: null as BoundingBox | null })
const resizeHandle = ref<string | null>(null) // 'nw', 'ne', 'sw', 'se', 'n', 's', 'e', 'w'

// 监听图像变化
watch(currentImage, () => {
  imageLoaded.value = false
  selectedBBox.value = null
  isDragging.value = false
  resizeHandle.value = null
}, { immediate: true })

// 更新画布尺寸和图像缩放
const updateCanvasSize = () => {
  if (canvasRef.value && imageRef.value && imageLoaded.value) {
    const containerRect = canvasRef.value.getBoundingClientRect()
    const imgRect = imageRef.value.getBoundingClientRect()
    
    canvasSize.value = {
      width: containerRect.width,
      height: containerRect.height
    }
    
    imageSize.value = {
      width: imgRect.width,
      height: imgRect.height,
      naturalWidth: imageRef.value.naturalWidth,
      naturalHeight: imageRef.value.naturalHeight
    }
    
    // 计算缩放比例（归一化坐标到实际像素）
    imageScale.value = {
      x: imgRect.width / imageRef.value.naturalWidth,
      y: imgRect.height / imageRef.value.naturalHeight
    }
  }
}

// 将归一化坐标转换为SVG像素坐标
const normalizeToSVG = (normalized: number, dimension: number) => {
  return normalized * dimension
}

// 将SVG像素坐标转换为归一化坐标
const svgToNormalize = (pixel: number, dimension: number) => {
  return Math.max(0, Math.min(1, pixel / dimension))
}

// 获取置信度颜色
const getConfidenceColor = (confidence: number) => {
  if (confidence >= 0.8) return '#10b981' // emerald
  if (confidence >= 0.6) return '#eab308' // yellow
  return '#f97316' // orange
}

// 点击边界框
const handleBBoxClick = (bbox: BoundingBox, event: MouseEvent) => {
  event.stopPropagation()
  selectedBBox.value = bbox.id
}

// 点击画布空白处取消选择
const handleCanvasClick = () => {
  selectedBBox.value = null
}

// 开始拖动
const handleMouseDown = (bbox: BoundingBox, event: MouseEvent, handle?: string) => {
  event.stopPropagation()
  event.preventDefault()
  
  selectedBBox.value = bbox.id
  
  if (handle) {
    // 调整大小
    resizeHandle.value = handle
  } else {
    // 拖动整个边界框
    isDragging.value = true
  }
  
  dragStart.value = {
    x: event.clientX,
    y: event.clientY,
    bbox: { ...bbox }
  }
}

// 鼠标移动
const handleMouseMove = (event: MouseEvent) => {
  if (!currentImage.value || !selectedBBox.value) return
  
  const bbox = currentImage.value.boundingBoxes.find(b => b.id === selectedBBox.value)
  if (!bbox) return
  
  const deltaX = (event.clientX - dragStart.value.x) / imageSize.value.width
  const deltaY = (event.clientY - dragStart.value.y) / imageSize.value.height
  
  if (isDragging.value && dragStart.value.bbox) {
    // 拖动整个边界框
    const newX = Math.max(0, Math.min(1 - bbox.width, dragStart.value.bbox.x + deltaX))
    const newY = Math.max(0, Math.min(1 - bbox.height, dragStart.value.bbox.y + deltaY))
    
    missionStore.updateBBox(currentImage.value.id, bbox.id, {
      x: newX,
      y: newY
    })
  } else if (resizeHandle.value && dragStart.value.bbox) {
    // 调整大小
    let newX = dragStart.value.bbox.x
    let newY = dragStart.value.bbox.y
    let newWidth = dragStart.value.bbox.width
    let newHeight = dragStart.value.bbox.height
    
    if (resizeHandle.value.includes('w')) {
      newX = Math.max(0, dragStart.value.bbox.x + deltaX)
      newWidth = Math.max(0.05, dragStart.value.bbox.width - deltaX)
    }
    if (resizeHandle.value.includes('e')) {
      newWidth = Math.max(0.05, dragStart.value.bbox.width + deltaX)
    }
    if (resizeHandle.value.includes('n')) {
      newY = Math.max(0, dragStart.value.bbox.y + deltaY)
      newHeight = Math.max(0.05, dragStart.value.bbox.height - deltaY)
    }
    if (resizeHandle.value.includes('s')) {
      newHeight = Math.max(0.05, dragStart.value.bbox.height + deltaY)
    }
    
    // 确保不超出边界
    if (newX + newWidth > 1) {
      newWidth = 1 - newX
    }
    if (newY + newHeight > 1) {
      newHeight = 1 - newY
    }
    
    missionStore.updateBBox(currentImage.value.id, bbox.id, {
      x: newX,
      y: newY,
      width: newWidth,
      height: newHeight
    })
  }
}

// 鼠标释放
const handleMouseUp = () => {
  isDragging.value = false
  resizeHandle.value = null
  dragStart.value = { x: 0, y: 0, bbox: null }
}

// 图像加载完成
const handleImageLoad = async () => {
  imageLoaded.value = true
  await nextTick()
  updateCanvasSize()
}

// 键盘快捷键 - 空格键确认
const handleKeyPress = (e: KeyboardEvent) => {
  if (e.code === 'Space' && selectedBBox.value && currentImage.value) {
    e.preventDefault()
    const bbox = currentImage.value.boundingBoxes.find(b => b.id === selectedBBox.value)
    if (bbox && bbox.status === 'pending') {
      missionStore.updateBBox(currentImage.value.id, bbox.id, {
        status: 'confirmed'
      })
    }
  }
  
  // Delete键删除选中的边界框
  if ((e.key === 'Delete' || e.key === 'Backspace') && selectedBBox.value && currentImage.value) {
    e.preventDefault()
    const bbox = currentImage.value.boundingBoxes.find(b => b.id === selectedBBox.value)
    if (bbox) {
      // 从图像中移除边界框
      const index = currentImage.value.boundingBoxes.findIndex(b => b.id === bbox.id)
      if (index > -1) {
        currentImage.value.boundingBoxes.splice(index, 1)
        selectedBBox.value = null
      }
    }
  }
}

// 获取调整大小手柄位置
const getResizeHandlePosition = (bbox: BoundingBox, handle: string) => {
  const x = normalizeToSVG(bbox.x, canvasSize.value.width)
  const y = normalizeToSVG(bbox.y, canvasSize.value.height)
  const w = normalizeToSVG(bbox.width, canvasSize.value.width)
  const h = normalizeToSVG(bbox.height, canvasSize.value.height)
  
  const handleSize = 8
  const positions: Record<string, { x: number; y: number }> = {
    'nw': { x: x, y: y },
    'ne': { x: x + w, y: y },
    'sw': { x: x, y: y + h },
    'se': { x: x + w, y: y + h },
    'n': { x: x + w / 2, y: y },
    's': { x: x + w / 2, y: y + h },
    'e': { x: x + w, y: y + h / 2 },
    'w': { x: x, y: y + h / 2 }
  }
  
  return positions[handle] || { x: 0, y: 0 }
}

onMounted(() => {
  window.addEventListener('resize', updateCanvasSize)
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mouseup', handleMouseUp)
  window.addEventListener('keydown', handleKeyPress)
  updateCanvasSize()
})

onUnmounted(() => {
  window.removeEventListener('resize', updateCanvasSize)
  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('mouseup', handleMouseUp)
  window.removeEventListener('keydown', handleKeyPress)
})
</script>

<template>
  <div class="smart-canvas" ref="canvasRef" @click="handleCanvasClick">
    <!-- 空状态 -->
    <div v-if="!currentImage" class="empty-canvas">
      <Icon icon="ph:image-square" :width="64" />
      <p>请从左侧选择一张图像</p>
    </div>

    <!-- 图像和覆盖层 -->
    <div v-else class="canvas-content">
      <!-- 图像容器 -->
      <div class="image-container">
        <img
          v-if="currentImage.url"
          ref="imageRef"
          :src="currentImage.url"
          :alt="currentImage.id"
          @load="handleImageLoad"
          class="canvas-image"
          draggable="false"
        />
        
        <!-- 加载状态 -->
        <div v-if="!imageLoaded" class="image-loading">
          <Icon icon="ph:spinner" :width="32" class="animate-spin" />
          <p>加载中...</p>
        </div>

        <!-- 边界框覆盖层 -->
        <svg
          v-if="imageLoaded && canvasSize.width > 0"
          ref="svgRef"
          class="bbox-overlay"
          :width="canvasSize.width"
          :height="canvasSize.height"
        >
          <g
            v-for="bbox in currentImage.boundingBoxes"
            :key="bbox.id"
            @click.stop="handleBBoxClick(bbox, $event)"
            @mousedown.stop="handleMouseDown(bbox, $event)"
            :class="[
              'bbox-group',
              { 'selected': selectedBBox === bbox.id }
            ]"
          >
            <!-- 边界框 -->
            <rect
              :x="normalizeToSVG(bbox.x, canvasSize.width)"
              :y="normalizeToSVG(bbox.y, canvasSize.height)"
              :width="normalizeToSVG(bbox.width, canvasSize.width)"
              :height="normalizeToSVG(bbox.height, canvasSize.height)"
              :fill="getConfidenceColor(bbox.confidence)"
              :fill-opacity="bbox.status === 'confirmed' ? 0.2 : 0.1"
              :stroke="getConfidenceColor(bbox.confidence)"
              :stroke-width="selectedBBox === bbox.id ? 3 : (bbox.status === 'confirmed' ? 2 : 2)"
              :stroke-dasharray="bbox.status === 'pending' ? '5,5' : '0'"
              rx="4"
              :class="{ 'cursor-move': selectedBBox === bbox.id }"
            />
            
            <!-- 标签 -->
            <text
              :x="normalizeToSVG(bbox.x, canvasSize.width) + 4"
              :y="normalizeToSVG(bbox.y, canvasSize.height) - 4"
              :fill="getConfidenceColor(bbox.confidence)"
              font-size="12"
              font-weight="600"
              class="bbox-label"
            >
              {{ bbox.label || '目标' }} {{ Math.round(bbox.confidence * 100) }}%
            </text>
            
            <!-- 调整大小手柄（仅选中时显示） -->
            <template v-if="selectedBBox === bbox.id">
              <circle
                v-for="handle in ['nw', 'ne', 'sw', 'se', 'n', 's', 'e', 'w']"
                :key="handle"
                :cx="getResizeHandlePosition(bbox, handle).x"
                :cy="getResizeHandlePosition(bbox, handle).y"
                r="6"
                :fill="getConfidenceColor(bbox.confidence)"
                :stroke="'white'"
                stroke-width="2"
                class="resize-handle"
                :class="`handle-${handle}`"
                @mousedown.stop="handleMouseDown(bbox, $event, handle)"
                style="cursor: nwse-resize;"
              />
            </template>
          </g>
        </svg>
      </div>

      <!-- 图像信息栏 -->
      <div class="image-info-bar">
        <div class="info-item">
          <Icon icon="ph:info" :width="16" />
          <span>{{ currentImage.id }}</span>
        </div>
        <div class="info-item">
          <Icon icon="ph:gauge" :width="16" />
          <span>置信度: {{ Math.round(currentImage.confidence * 100) }}%</span>
        </div>
        <div class="info-item">
          <Icon icon="ph:square" :width="16" />
          <span>{{ currentImage.boundingBoxes.length }} 个标注</span>
        </div>
        <div class="info-item">
          <Icon icon="ph:source" :width="16" />
          <span>{{ currentImage.source === 'crawler' ? '爬虫' : 
                   currentImage.source === 'agent_recommended' ? 'Agent推荐' : 
                   '手动上传' }}</span>
        </div>
        <div v-if="selectedBBox" class="info-item hint">
          <Icon icon="ph:keyboard" :width="16" />
          <span>空格确认 | Delete删除</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.smart-canvas {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  min-height: 0;
}

.empty-canvas {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: var(--color-text-tertiary);
  
  p {
    margin: 0;
    font-size: 16px;
  }
}

.canvas-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.image-container {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
  overflow: hidden;
  min-height: 0;
  max-height: 100%;
}

.canvas-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  user-select: none;
  pointer-events: none;
}

.image-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--color-text-secondary);
  
  p {
    margin: 0;
    font-size: 14px;
  }
}

.bbox-overlay {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
  user-select: none;
  
  .bbox-group {
    pointer-events: all;
    cursor: pointer;
    transition: filter 0.2s ease;
    
    &:hover {
      filter: brightness(1.1);
    }
    
    &.selected {
      filter: brightness(1.3);
    }
  }
  
  .bbox-label {
    pointer-events: none;
    user-select: none;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
  }
  
  .resize-handle {
    pointer-events: all;
    cursor: nwse-resize;
    
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
      filter: brightness(1.2);
    }
  }
}

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
  }
  
  &.hint {
    margin-left: auto;
    color: var(--color-text-tertiary);
    font-size: 12px;
  }
}
</style>
