<script setup lang="ts">
/**
 * SmartCanvas Component - 重构版
 * 
 * 智能标注画布 - 模块化架构
 * 
 * 模块组成：
 * - Composables: useCanvas, useAnnotation, useImageUpload, useDatasetImport, useAnnotationExport
 * - Components: CanvasToolbar, AnnotationEditor, AnnotationOverlay, ImageInfoBar, EmptyCanvas
 * - Utils: annotation.ts (工具函数)
 * - Constants: annotation.ts (常量定义)
 */

import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { Icon } from '@iconify/vue'
import { useMissionStore } from '@/store/mission'

// Composables
import { useCanvas } from './composables/useCanvas'
import { useAnnotation } from './composables/useAnnotation'
import { useImageUpload } from './composables/useImageUpload'
import { useDatasetImport } from './composables/useDatasetImport'
import { useAnnotationExport } from './composables/useAnnotationExport'

// Components
import CanvasToolbar from './canvas/CanvasToolbar.vue'
import AnnotationEditor from './canvas/AnnotationEditor.vue'
import AnnotationOverlay from './canvas/AnnotationOverlay.vue'
import ImageInfoBar from './canvas/ImageInfoBar.vue'
import EmptyCanvas from './canvas/EmptyCanvas.vue'

// Constants
import { ZOOM_CONFIG, type ToolType } from './constants/annotation'

const missionStore = useMissionStore()

// Refs
const canvasRef = ref<HTMLDivElement | null>(null)
const imageRef = ref<HTMLImageElement | null>(null)
const imageWrapperRef = ref<HTMLDivElement | null>(null)
const imageLoaded = ref(false)
const currentTool = ref<ToolType>('select')

// ========== 画布管理 ==========
const canvas = useCanvas(canvasRef, imageRef, imageLoaded)

// ========== 标注管理 ==========
const annotation = useAnnotation(
  currentTool,
  imageWrapperRef,
  canvas.scaledImageSize,
  canvas.svgToNormalize
)

// ========== 图像上传 ==========
const {
  fileInputRef, // Used in template ref binding
  localImage,
  triggerFileUpload,
  handleFileSelect,
  handleDrop,
  handleDragOver,
  clearAllSelection
} = useImageUpload(
  imageLoaded,
  canvas.resetView,
  annotation.resetState
)

// ========== 数据集导入 ==========
const {
  datasetInputRef, // Used in template ref binding
  triggerDatasetImport,
  handleDatasetImport
} = useDatasetImport()

// ========== 标注导出 ==========
const exportHandler = useAnnotationExport(
  annotation.currentImage,
  canvas.baseImageSize
)

// 当前显示的图像（本地或 store）
const currentImage = computed(() => localImage.value || missionStore.currentImage)

// 监听图像变化
watch(() => missionStore.currentImage, () => {
  if (!localImage.value) {
    imageLoaded.value = false
    annotation.resetState()
    canvas.resetView()
  }
}, { immediate: true })

// 监听缩放变化
watch(canvas.zoomLevel, () => {
  canvas.updateCanvasSize()
})

// 图像加载完成
const handleImageLoad = async () => {
  imageLoaded.value = true
  await canvas.updateCanvasSize()
}

// 切换工具
const setTool = (tool: ToolType) => {
  currentTool.value = tool
  annotation.selectedBBox.value = null
}

// ========== 鼠标事件处理 ==========
const handleMouseDown = (event: MouseEvent) => {
  // Pan 模式
  if (currentTool.value === 'pan') {
    canvas.startPan(event)
    return
  }
  
  // 绘制模式
  if (currentTool.value === 'draw') {
    annotation.handleDrawStart(event)
  }
}

const handleMouseMove = (event: MouseEvent) => {
  // Pan 模式
  if (canvas.isPanning.value) {
    canvas.movePan(event)
    return
  }
  
  // 绘制模式
  if (annotation.isDrawing.value) {
    annotation.handleDrawMove(event)
    return
  }
  
  // 编辑模式（拖动/调整大小）
  if (annotation.isDragging.value || annotation.resizeHandle.value) {
    annotation.handleBBoxMove(event)
  }
}

const handleMouseUp = () => {
  // 完成 Pan
  if (canvas.isPanning.value) {
    canvas.endPan()
    return
  }
  
  // 完成绘制
  if (annotation.isDrawing.value) {
    annotation.finishDraw()
    return
  }
  
  // 完成拖动/调整大小
  if (annotation.isDragging.value || annotation.resizeHandle.value) {
    annotation.finishBBoxEdit()
  }
}

// ========== 键盘快捷键 ==========
const handleKeyPress = (e: KeyboardEvent) => {
  // 空格键确认
  if (e.code === 'Space' && annotation.selectedBBox.value && currentImage.value) {
    e.preventDefault()
    annotation.confirmSelectedBBox()
  }
  
  // Delete/Backspace键删除
  if ((e.key === 'Delete' || e.key === 'Backspace') && annotation.selectedBBox.value) {
    e.preventDefault()
    annotation.deleteSelectedBBox()
  }
  
  // 工具切换
  if (e.key === 'v' || e.key === 'V') setTool('select')
  if (e.key === 'b' || e.key === 'B') setTool('draw')
  if (e.key === 'h' || e.key === 'H') setTool('pan')
  
  // 视图控制
  if (e.key === '0') canvas.resetView()
  if (e.key === '+' || e.key === '=') canvas.handleZoom(ZOOM_CONFIG.STEP)
  if (e.key === '-' || e.key === '_') canvas.handleZoom(-ZOOM_CONFIG.STEP)
  
  // Escape取消
  if (e.key === 'Escape') {
    annotation.selectedBBox.value = null
    annotation.isDrawing.value = false
    canvas.isPanning.value = false
  }
}

// 清除所有选择
const handleClearSelection = () => {
  clearAllSelection(() => {
    missionStore.currentImage = null
  })
}

// 确认所有标注
const handleConfirmAll = () => {
  exportHandler.confirmAllBBoxes(missionStore.updateBBox)
}

// 生命周期
onMounted(() => {
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mouseup', handleMouseUp)
  window.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('mouseup', handleMouseUp)
  window.removeEventListener('keydown', handleKeyPress)
})
</script>

<template>
  <div class="smart-canvas" ref="canvasRef" @wheel="canvas.handleWheel">
    <!-- 隐藏的文件输入 -->
    <input
      ref="fileInputRef"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleFileSelect"
    />
    
    <!-- 隐藏的数据集导入输入 -->
    <input
      ref="datasetInputRef"
      type="file"
      accept="image/*,.txt,.json"
      multiple
      style="display: none"
      @change="handleDatasetImport"
    />
    
    <!-- 工具栏 -->
    <CanvasToolbar
      :current-tool="currentTool"
      :zoom-level="canvas.zoomLevel.value"
      :min-zoom="ZOOM_CONFIG.MIN"
      :max-zoom="ZOOM_CONFIG.MAX"
      :has-image="!!currentImage"
      :has-annotations="!!currentImage && currentImage.boundingBoxes.length > 0"
      @set-tool="setTool"
      @zoom="canvas.handleZoom"
      @reset-view="canvas.resetView"
      @upload="triggerFileUpload"
      @import-dataset="triggerDatasetImport"
      @export="exportHandler.exportAnnotations"
      @confirm-all="handleConfirmAll"
      @clear-selection="handleClearSelection"
    />

    <!-- 空状态 -->
    <EmptyCanvas
      v-if="!currentImage"
      @upload="triggerFileUpload"
      @dragover="handleDragOver"
      @drop="handleDrop"
    />

    <!-- 画布内容 -->
    <div 
      v-else 
      class="canvas-content"
      @dragover="handleDragOver"
      @drop="handleDrop"
    >
      <!-- 图像容器 -->
      <div 
        class="image-container"
        :class="{ 
          'tool-draw': currentTool === 'draw',
          'tool-pan': currentTool === 'pan',
          'is-panning': canvas.isPanning.value
        }"
        @mousedown="handleMouseDown"
        @click="annotation.handleCanvasClick"
      >
        <!-- 图像包装器（包含图像和标注层） -->
        <div 
          ref="imageWrapperRef"
          class="image-wrapper"
          :style="{
            width: `${canvas.scaledImageSize.value.width}px`,
            height: `${canvas.scaledImageSize.value.height}px`,
            transform: `translate(${canvas.imageOffset.value.x}px, ${canvas.imageOffset.value.y}px)`
          }"
        >
          <!-- 图像 -->
          <img
            v-if="currentImage.url"
            ref="imageRef"
            :src="currentImage.url"
            :alt="currentImage.id"
            @load="handleImageLoad"
            class="canvas-image"
            :style="{
              width: `${canvas.scaledImageSize.value.width}px`,
              height: `${canvas.scaledImageSize.value.height}px`
            }"
            draggable="false"
          />
          
          <!-- 标注覆盖层 -->
          <AnnotationOverlay
            v-if="imageLoaded"
            :bounding-boxes="currentImage.boundingBoxes"
            :selected-b-box-id="annotation.selectedBBox.value"
            :current-tool="currentTool"
            :normalize-to-s-v-g="canvas.normalizeToSVG"
            :scaled-image-size="canvas.scaledImageSize.value"
            :drawing-rect="annotation.getDrawingRect.value"
            @bbox-click="annotation.handleBBoxClick"
            @bbox-mouse-down="annotation.handleBBoxMouseDown"
          />
        </div>
        
        <!-- 加载状态 -->
        <div v-if="!imageLoaded" class="image-loading">
          <Icon icon="ph:spinner" :width="32" class="animate-spin" />
          <p>加载中...</p>
        </div>
      </div>

      <!-- 标注编辑面板 -->
      <AnnotationEditor
        v-if="annotation.selectedBBoxData.value && currentTool === 'select'"
        :bbox="annotation.selectedBBoxData.value"
        @update-label="annotation.updateLabel"
        @confirm="annotation.confirmSelectedBBox"
        @delete="annotation.deleteSelectedBBox"
      />

      <!-- 图像信息栏 -->
      <ImageInfoBar
        :image="currentImage"
        :image-width="canvas.baseImageSize.value.naturalWidth"
        :image-height="canvas.baseImageSize.value.naturalHeight"
      />
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

// 画布内容
.canvas-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
  position: relative;
}

// 图像容器
.image-container {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
  overflow: hidden;
  min-height: 0;
  cursor: default;
  
  &.tool-draw {
    cursor: crosshair;
  }
  
  &.tool-pan {
    cursor: grab;
    
    &.is-panning {
      cursor: grabbing;
    }
  }
}

// 图像包装器
.image-wrapper {
  position: absolute;
  will-change: transform;
  display: block;
}

// 图像
.canvas-image {
  display: block;
  object-fit: contain;
  user-select: none;
  pointer-events: none;
  position: relative;
  z-index: 1;
}

// 加载状态
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

// 动画
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
