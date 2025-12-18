/**
 * 画布管理 Composable
 * 负责画布尺寸、缩放、平移等核心功能
 */

import { ref, computed, watch, onMounted, onUnmounted, nextTick, type Ref } from 'vue'
import { ZOOM_CONFIG, IMAGE_FIT_SCALE } from '../constants/annotation'

export interface CanvasSize {
  width: number
  height: number
}

export interface ImageSize {
  width: number
  height: number
  naturalWidth: number
  naturalHeight: number
}

export interface Offset {
  x: number
  y: number
}

export const useCanvas = (
  canvasRef: Ref<HTMLDivElement | null>,
  imageRef: Ref<HTMLImageElement | null>,
  imageLoaded: Ref<boolean>
) => {
  // 画布和图像尺寸
  const canvasSize = ref<CanvasSize>({ width: 0, height: 0 })
  const baseImageSize = ref<ImageSize>({ width: 0, height: 0, naturalWidth: 0, naturalHeight: 0 })
  
  // 缩放和平移
  const zoomLevel = ref(1)
  const panOffset = ref<Offset>({ x: 0, y: 0 })
  
  // Pan 状态
  const isPanning = ref(false)
  const panStart = ref<Offset>({ x: 0, y: 0 })

  // 计算当前缩放后的图像尺寸
  const scaledImageSize = computed(() => ({
    width: baseImageSize.value.width * zoomLevel.value,
    height: baseImageSize.value.height * zoomLevel.value
  }))

  // 计算图像在容器中的偏移（居中 + 平移）
  const imageOffset = computed(() => ({
    x: (canvasSize.value.width - scaledImageSize.value.width) / 2 + panOffset.value.x,
    y: (canvasSize.value.height - scaledImageSize.value.height) / 2 + panOffset.value.y
  }))

  // 图像缩放比例（归一化坐标到基础像素）
  const imageScale = computed(() => ({
    x: baseImageSize.value.width / baseImageSize.value.naturalWidth,
    y: baseImageSize.value.height / baseImageSize.value.naturalHeight
  }))

  /**
   * 更新画布尺寸和图像缩放
   */
  const updateCanvasSize = () => {
    if (!canvasRef.value || !imageRef.value || !imageLoaded.value) return
    
    const containerRect = canvasRef.value.getBoundingClientRect()
    canvasSize.value = {
      width: containerRect.width,
      height: containerRect.height
    }
    
    const naturalWidth = imageRef.value.naturalWidth
    const naturalHeight = imageRef.value.naturalHeight
    const containerAspect = containerRect.width / containerRect.height
    const imageAspect = naturalWidth / naturalHeight
    
    let baseWidth: number, baseHeight: number
    if (imageAspect > containerAspect) {
      baseWidth = containerRect.width * IMAGE_FIT_SCALE
      baseHeight = baseWidth / imageAspect
    } else {
      baseHeight = containerRect.height * IMAGE_FIT_SCALE
      baseWidth = baseHeight * imageAspect
    }
    
    baseImageSize.value = {
      width: baseWidth,
      height: baseHeight,
      naturalWidth,
      naturalHeight
    }
  }

  /**
   * 缩放控制
   */
  const handleZoom = (delta: number) => {
    const newZoom = Math.max(
      ZOOM_CONFIG.MIN,
      Math.min(ZOOM_CONFIG.MAX, zoomLevel.value + delta)
    )
    zoomLevel.value = newZoom
  }

  /**
   * 滚轮缩放
   */
  const handleWheel = (event: WheelEvent) => {
    if (event.ctrlKey || event.metaKey) {
      event.preventDefault()
      const delta = event.deltaY > 0 ? -0.1 : 0.1
      handleZoom(delta)
    }
  }

  /**
   * 开始平移
   */
  const startPan = (event: MouseEvent) => {
    event.preventDefault()
    isPanning.value = true
    panStart.value = { x: event.clientX, y: event.clientY }
  }

  /**
   * 平移中
   */
  const movePan = (event: MouseEvent) => {
    if (!isPanning.value) return
    
    const deltaX = event.clientX - panStart.value.x
    const deltaY = event.clientY - panStart.value.y
    panOffset.value = {
      x: panOffset.value.x + deltaX,
      y: panOffset.value.y + deltaY
    }
    panStart.value = { x: event.clientX, y: event.clientY }
  }

  /**
   * 结束平移
   */
  const endPan = () => {
    isPanning.value = false
    panStart.value = { x: 0, y: 0 }
  }

  /**
   * 重置视图
   */
  const resetView = () => {
    zoomLevel.value = 1
    panOffset.value = { x: 0, y: 0 }
  }

  /**
   * 将归一化坐标转换为SVG像素坐标
   */
  const normalizeToSVG = (normalized: number, dimension: 'x' | 'y'): number => {
    if (dimension === 'x') {
      return normalized * scaledImageSize.value.width
    } else {
      return normalized * scaledImageSize.value.height
    }
  }

  /**
   * 将SVG像素坐标转换为归一化坐标
   */
  const svgToNormalize = (pixel: number, dimension: 'x' | 'y'): number => {
    if (dimension === 'x') {
      return Math.max(0, Math.min(1, pixel / scaledImageSize.value.width))
    } else {
      return Math.max(0, Math.min(1, pixel / scaledImageSize.value.height))
    }
  }

  // 监听缩放变化，更新画布
  watch(zoomLevel, () => {
    nextTick(updateCanvasSize)
  })

  // 挂载和卸载
  onMounted(() => {
    window.addEventListener('resize', updateCanvasSize)
    updateCanvasSize()
  })

  onUnmounted(() => {
    window.removeEventListener('resize', updateCanvasSize)
  })

  return {
    // State
    canvasSize,
    baseImageSize,
    zoomLevel,
    panOffset,
    isPanning,
    scaledImageSize,
    imageOffset,
    imageScale,
    
    // Methods
    updateCanvasSize,
    handleZoom,
    handleWheel,
    startPan,
    movePan,
    endPan,
    resetView,
    normalizeToSVG,
    svgToNormalize
  }
}

