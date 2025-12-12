<script setup lang="ts">
/**
 * SmartCanvas Component
 * 
 * 中间智能画布 - 显示图像和 Agent 标注的覆盖层
 * 支持交互式编辑边界框（拖动和调整大小）
 * 支持绘制新的边界框
 * 
 * 功能特性：
 * - 选择工具：选中并编辑现有标注框
 * - 绘制工具：绘制新的标注框
 * - 确认/删除标注
 * - 标签编辑
 * - 批量操作
 * - 图像上传功能
 * - 导出YOLO格式标注
 */

import { computed, ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { Icon } from '@iconify/vue'
import { useMissionStore } from '@/store/mission'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { BoundingBox } from '@/api/types'

const missionStore = useMissionStore()

// 工具类型
type ToolType = 'select' | 'draw' | 'pan'

// 画布引用
const canvasRef = ref<HTMLDivElement | null>(null)
const imageRef = ref<HTMLImageElement | null>(null)
const svgRef = ref<SVGSVGElement | null>(null)
const imageWrapperRef = ref<HTMLDivElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

// 当前图像
const currentImage = computed(() => localImage.value || missionStore.currentImage)

// 本地上传的图像
const localImage = ref<{
  id: string
  url: string
  confidence: number
  source: 'upload' | 'crawler' | 'agent_recommended'
  boundingBoxes: BoundingBox[]
} | null>(null)

// 当前工具
const currentTool = ref<ToolType>('select')

// 选中的边界框
const selectedBBox = ref<string | null>(null)

// 图像加载状态
const imageLoaded = ref(false)

// 画布尺寸和图像实际尺寸（未缩放前）
const canvasSize = ref({ width: 0, height: 0 })
const baseImageSize = ref({ width: 0, height: 0, naturalWidth: 0, naturalHeight: 0 })
const imageScale = ref({ x: 1, y: 1 })
// 平移偏移（用于 pan 工具）
const panOffset = ref({ x: 0, y: 0 })

// 拖动状态
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0, bbox: null as BoundingBox | null })
const resizeHandle = ref<string | null>(null)

// 绘制状态
const isDrawing = ref(false)
const drawStart = ref({ x: 0, y: 0 })
const drawCurrent = ref({ x: 0, y: 0 })

// Pan 状态
const isPanning = ref(false)
const panStart = ref({ x: 0, y: 0 })

// 缩放状态
const zoomLevel = ref(1)
const minZoom = 0.25
const maxZoom = 5

// 标签选项
const labelOptions = ['海上风电平台', '风机叶片', '支撑结构', '建筑物', '道路', '农田', '船舶', '其他']

// 监听图像变化
watch(() => missionStore.currentImage, () => {
  if (!localImage.value) {
    imageLoaded.value = false
    selectedBBox.value = null
    isDragging.value = false
    resizeHandle.value = null
    isDrawing.value = false
    zoomLevel.value = 1
    panOffset.value = { x: 0, y: 0 }
  }
}, { immediate: true })

// 监听缩放级别变化，更新画布尺寸
watch(zoomLevel, () => {
  nextTick(updateCanvasSize)
})

// 更新画布尺寸和图像缩放
const updateCanvasSize = () => {
  if (canvasRef.value && imageRef.value && imageLoaded.value) {
    const containerRect = canvasRef.value.getBoundingClientRect()
    
    canvasSize.value = {
      width: containerRect.width,
      height: containerRect.height
    }
    
    // 获取未缩放时的图像尺寸
    const naturalWidth = imageRef.value.naturalWidth
    const naturalHeight = imageRef.value.naturalHeight
    
    // 计算适应容器的基础尺寸（不考虑缩放）
    const containerAspect = containerRect.width / containerRect.height
    const imageAspect = naturalWidth / naturalHeight
    
    let baseWidth: number, baseHeight: number
    if (imageAspect > containerAspect) {
      baseWidth = containerRect.width * 0.95
      baseHeight = baseWidth / imageAspect
    } else {
      baseHeight = containerRect.height * 0.95
      baseWidth = baseHeight * imageAspect
    }
    
    baseImageSize.value = {
      width: baseWidth,
      height: baseHeight,
      naturalWidth,
      naturalHeight
    }
    
    // 计算缩放比例（归一化坐标到基础像素）
    imageScale.value = {
      x: baseWidth / naturalWidth,
      y: baseHeight / naturalHeight
    }
  }
}

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

// 将归一化坐标转换为SVG像素坐标（考虑缩放和偏移）
const normalizeToSVG = (normalized: number, dimension: 'x' | 'y') => {
  if (dimension === 'x') {
    return imageOffset.value.x + normalized * scaledImageSize.value.width
  } else {
    return imageOffset.value.y + normalized * scaledImageSize.value.height
  }
}

// 将SVG像素坐标转换为归一化坐标
const svgToNormalize = (pixel: number, dimension: 'x' | 'y') => {
  if (dimension === 'x') {
    return Math.max(0, Math.min(1, (pixel - imageOffset.value.x) / scaledImageSize.value.width))
  } else {
    return Math.max(0, Math.min(1, (pixel - imageOffset.value.y) / scaledImageSize.value.height))
  }
}

// 获取置信度颜色
const getConfidenceColor = (confidence: number) => {
  if (confidence >= 0.8) return '#10b981' // emerald
  if (confidence >= 0.6) return '#eab308' // yellow
  return '#f97316' // orange
}

// 切换工具
const setTool = (tool: ToolType) => {
  currentTool.value = tool
  selectedBBox.value = null
}

// 点击边界框
const handleBBoxClick = (bbox: BoundingBox, event: MouseEvent) => {
  if (currentTool.value !== 'select') return
  event.stopPropagation()
  selectedBBox.value = bbox.id
}

// 点击画布空白处
const handleCanvasClick = (event: MouseEvent) => {
  if (currentTool.value === 'select') {
    selectedBBox.value = null
  }
}

// 开始拖动边界框
const handleBBoxMouseDown = (bbox: BoundingBox, event: MouseEvent, handle?: string) => {
  if (currentTool.value !== 'select') return
  event.stopPropagation()
  event.preventDefault()
  
  selectedBBox.value = bbox.id
  
  if (handle) {
    resizeHandle.value = handle
  } else {
    isDragging.value = true
  }
  
  dragStart.value = {
    x: event.clientX,
    y: event.clientY,
    bbox: { ...bbox }
  }
}

// 开始绘制新边界框
const handleDrawStart = (event: MouseEvent) => {
  if (!canvasRef.value) return
  
  const rect = canvasRef.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  // Pan 模式
  if (currentTool.value === 'pan') {
    event.preventDefault()
    isPanning.value = true
    panStart.value = { x: event.clientX, y: event.clientY }
    return
  }
  
  // 绘制模式
  if (currentTool.value !== 'draw') return
  
  event.preventDefault()
  isDrawing.value = true
  drawStart.value = { x, y }
  drawCurrent.value = { x, y }
}

// 鼠标移动
const handleMouseMove = (event: MouseEvent) => {
  if (!currentImage.value) return
  
  // Pan 模式
  if (isPanning.value) {
    const deltaX = event.clientX - panStart.value.x
    const deltaY = event.clientY - panStart.value.y
    panOffset.value = {
      x: panOffset.value.x + deltaX,
      y: panOffset.value.y + deltaY
    }
    panStart.value = { x: event.clientX, y: event.clientY }
    return
  }
  
  // 绘制模式
  if (isDrawing.value && canvasRef.value) {
    const rect = canvasRef.value.getBoundingClientRect()
    drawCurrent.value = {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    }
    return
  }
  
  // 选择模式 - 拖动或调整大小
  if (!selectedBBox.value) return
  
  const bbox = currentImage.value.boundingBoxes.find(b => b.id === selectedBBox.value)
  if (!bbox) return
  
  // 使用缩放后的图像尺寸计算归一化坐标变化
  const deltaX = (event.clientX - dragStart.value.x) / scaledImageSize.value.width
  const deltaY = (event.clientY - dragStart.value.y) / scaledImageSize.value.height
  
  if (isDragging.value && dragStart.value.bbox) {
    // 拖动整个边界框 - 优化性能，直接修改数据
    const newX = Math.max(0, Math.min(1 - bbox.width, dragStart.value.bbox.x + deltaX))
    const newY = Math.max(0, Math.min(1 - bbox.height, dragStart.value.bbox.y + deltaY))
    
    // 直接修改本地数据以提高性能
    bbox.x = newX
    bbox.y = newY
  } else if (resizeHandle.value && dragStart.value.bbox) {
    // 调整大小
    let newX = dragStart.value.bbox.x
    let newY = dragStart.value.bbox.y
    let newWidth = dragStart.value.bbox.width
    let newHeight = dragStart.value.bbox.height
    
    if (resizeHandle.value.includes('w')) {
      newX = Math.max(0, dragStart.value.bbox.x + deltaX)
      newWidth = Math.max(0.03, dragStart.value.bbox.width - deltaX)
    }
    if (resizeHandle.value.includes('e')) {
      newWidth = Math.max(0.03, dragStart.value.bbox.width + deltaX)
    }
    if (resizeHandle.value.includes('n')) {
      newY = Math.max(0, dragStart.value.bbox.y + deltaY)
      newHeight = Math.max(0.03, dragStart.value.bbox.height - deltaY)
    }
    if (resizeHandle.value.includes('s')) {
      newHeight = Math.max(0.03, dragStart.value.bbox.height + deltaY)
    }
    
    // 确保不超出边界
    if (newX + newWidth > 1) {
      newWidth = 1 - newX
    }
    if (newY + newHeight > 1) {
      newHeight = 1 - newY
    }
    
    // 直接修改本地数据以提高性能
    bbox.x = newX
    bbox.y = newY
    bbox.width = newWidth
    bbox.height = newHeight
  }
}

// 鼠标释放
const handleMouseUp = () => {
  // 完成 Pan
  if (isPanning.value) {
    isPanning.value = false
    panStart.value = { x: 0, y: 0 }
    return
  }
  
  // 完成绘制
  if (isDrawing.value && currentImage.value) {
    const x1 = svgToNormalize(Math.min(drawStart.value.x, drawCurrent.value.x), 'x')
    const y1 = svgToNormalize(Math.min(drawStart.value.y, drawCurrent.value.y), 'y')
    const x2 = svgToNormalize(Math.max(drawStart.value.x, drawCurrent.value.x), 'x')
    const y2 = svgToNormalize(Math.max(drawStart.value.y, drawCurrent.value.y), 'y')
    
    const width = x2 - x1
    const height = y2 - y1
    
    // 只有当边界框足够大时才创建
    if (width > 0.02 && height > 0.02) {
      const newBBox: BoundingBox = {
        id: `bbox-${Date.now()}`,
        x: x1,
        y: y1,
        width,
        height,
        confidence: 1.0,
        label: '目标',
        status: 'pending'
      }
      
      currentImage.value.boundingBoxes.push(newBBox)
      selectedBBox.value = newBBox.id
      setTool('select')
      
      ElMessage.success('标注框已创建，请设置标签')
    }
    
    isDrawing.value = false
    drawStart.value = { x: 0, y: 0 }
    drawCurrent.value = { x: 0, y: 0 }
    return
  }
  
  // 完成拖动/调整大小 - 同步到 store（仅当不是本地图像时）
  if ((isDragging.value || resizeHandle.value) && selectedBBox.value && currentImage.value) {
    const bbox = currentImage.value.boundingBoxes.find(b => b.id === selectedBBox.value)
    if (bbox && !localImage.value) {
      missionStore.updateBBox(currentImage.value.id, bbox.id, {
        x: bbox.x,
        y: bbox.y,
        width: bbox.width,
        height: bbox.height
      })
    }
  }
  
  isDragging.value = false
  resizeHandle.value = null
  dragStart.value = { x: 0, y: 0, bbox: null }
}

// ========== 图像上传功能 ==========
const triggerFileUpload = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    const reader = new FileReader()
    
    reader.onload = (e) => {
      const url = e.target?.result as string
      localImage.value = {
        id: `upload-${Date.now()}`,
        url,
        confidence: 1.0,
        source: 'upload',
        boundingBoxes: []
      }
      imageLoaded.value = false
      selectedBBox.value = null
      zoomLevel.value = 1
      panOffset.value = { x: 0, y: 0 }
      
      ElMessage.success('图像已加载，开始标注吧！')
    }
    
    reader.readAsDataURL(file)
  }
  // 清空 input 以便再次选择同一文件
  target.value = ''
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    const file = event.dataTransfer.files[0]
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const url = e.target?.result as string
        localImage.value = {
          id: `upload-${Date.now()}`,
          url,
          confidence: 1.0,
          source: 'upload',
          boundingBoxes: []
        }
        imageLoaded.value = false
        selectedBBox.value = null
        zoomLevel.value = 1
        panOffset.value = { x: 0, y: 0 }
        
        ElMessage.success('图像已加载，开始标注吧！')
      }
      reader.readAsDataURL(file)
    }
  }
}

const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
}

// 清除本地图像
const clearLocalImage = () => {
  localImage.value = null
  imageLoaded.value = false
  selectedBBox.value = null
  zoomLevel.value = 1
  panOffset.value = { x: 0, y: 0 }
}

// ========== 导出标注功能 ==========
const exportAnnotations = async () => {
  if (!currentImage.value || currentImage.value.boundingBoxes.length === 0) {
    ElMessage.warning('没有可导出的标注数据')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      '选择导出格式',
      '导出标注',
      {
        confirmButtonText: 'YOLO格式',
        cancelButtonText: 'JSON格式',
        distinguishCancelAndClose: true
      }
    )
    exportYOLO()
  } catch (action) {
    if (action === 'cancel') {
      exportJSON()
    }
  }
}

// 导出 YOLO 格式 (txt)
const exportYOLO = () => {
  if (!currentImage.value) return
  
  // YOLO格式: class_id center_x center_y width height (归一化坐标)
  const lines = currentImage.value.boundingBoxes.map((bbox) => {
    const classId = labelOptions.indexOf(bbox.label || '其他')
    const centerX = bbox.x + bbox.width / 2
    const centerY = bbox.y + bbox.height / 2
    return `${classId >= 0 ? classId : labelOptions.length - 1} ${centerX.toFixed(6)} ${centerY.toFixed(6)} ${bbox.width.toFixed(6)} ${bbox.height.toFixed(6)}`
  })
  
  const content = lines.join('\n')
  downloadFile(content, `${currentImage.value.id}_annotations.txt`, 'text/plain')
  
  // 同时导出类别文件
  const classesContent = labelOptions.join('\n')
  downloadFile(classesContent, 'classes.txt', 'text/plain')
  
  ElMessage.success('YOLO格式标注已导出')
}

// 导出 JSON 格式
const exportJSON = () => {
  if (!currentImage.value) return
  
  const data = {
    image_id: currentImage.value.id,
    image_width: baseImageSize.value.naturalWidth,
    image_height: baseImageSize.value.naturalHeight,
    annotations: currentImage.value.boundingBoxes.map((bbox) => ({
      id: bbox.id,
      label: bbox.label || '目标',
      confidence: bbox.confidence,
      status: bbox.status,
      bbox: {
        x: bbox.x,
        y: bbox.y,
        width: bbox.width,
        height: bbox.height
      },
      // 像素坐标
      bbox_pixels: {
        x: Math.round(bbox.x * baseImageSize.value.naturalWidth),
        y: Math.round(bbox.y * baseImageSize.value.naturalHeight),
        width: Math.round(bbox.width * baseImageSize.value.naturalWidth),
        height: Math.round(bbox.height * baseImageSize.value.naturalHeight)
      }
    }))
  }
  
  const content = JSON.stringify(data, null, 2)
  downloadFile(content, `${currentImage.value.id}_annotations.json`, 'application/json')
  
  ElMessage.success('JSON格式标注已导出')
}

// 下载文件辅助函数
const downloadFile = (content: string, filename: string, mimeType: string) => {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// 重置视图
const resetView = () => {
  zoomLevel.value = 1
  panOffset.value = { x: 0, y: 0 }
}

// 图像加载完成
const handleImageLoad = async () => {
  imageLoaded.value = true
  await nextTick()
  updateCanvasSize()
}

// 确认选中的标注框
const confirmSelectedBBox = () => {
  if (!selectedBBox.value || !currentImage.value) return
  
  const bbox = currentImage.value.boundingBoxes.find(b => b.id === selectedBBox.value)
  if (bbox && bbox.status === 'pending') {
    missionStore.updateBBox(currentImage.value.id, bbox.id, {
      status: 'confirmed'
    })
    ElMessage.success('标注已确认')
  }
}

// 删除选中的标注框
const deleteSelectedBBox = () => {
  if (!selectedBBox.value || !currentImage.value) return
  
  const index = currentImage.value.boundingBoxes.findIndex(b => b.id === selectedBBox.value)
  if (index > -1) {
    currentImage.value.boundingBoxes.splice(index, 1)
    selectedBBox.value = null
    ElMessage.info('标注已删除')
  }
}

// 更新标签
const updateLabel = (label: string) => {
  if (!selectedBBox.value || !currentImage.value) return
  
  const bbox = currentImage.value.boundingBoxes.find(b => b.id === selectedBBox.value)
  if (bbox) {
    missionStore.updateBBox(currentImage.value.id, bbox.id, {
      label
    })
  }
}

// 确认所有标注
const confirmAllBBoxes = async () => {
  if (!currentImage.value) return
  
  try {
    await ElMessageBox.confirm(
      '确认将所有标注框标记为已确认？',
      '批量确认',
      { confirmButtonText: '确认', cancelButtonText: '取消', type: 'info' }
    )
    
    currentImage.value.boundingBoxes.forEach(bbox => {
      if (bbox.status === 'pending') {
        missionStore.updateBBox(currentImage.value!.id, bbox.id, {
          status: 'confirmed'
        })
      }
    })
    
    ElMessage.success('所有标注已确认')
  } catch {
    // 用户取消
  }
}

// 键盘快捷键
const handleKeyPress = (e: KeyboardEvent) => {
  // 空格键确认
  if (e.code === 'Space' && selectedBBox.value && currentImage.value) {
    e.preventDefault()
    confirmSelectedBBox()
  }
  
  // Delete/Backspace键删除
  if ((e.key === 'Delete' || e.key === 'Backspace') && selectedBBox.value && currentImage.value) {
    e.preventDefault()
    deleteSelectedBBox()
  }
  
  // V键切换选择工具
  if (e.key === 'v' || e.key === 'V') {
    setTool('select')
  }
  
  // B键切换绘制工具
  if (e.key === 'b' || e.key === 'B') {
    setTool('draw')
  }
  
  // H键切换平移工具
  if (e.key === 'h' || e.key === 'H') {
    setTool('pan')
  }
  
  // 0键重置视图
  if (e.key === '0') {
    resetView()
  }
  
  // +/- 键缩放
  if (e.key === '+' || e.key === '=') {
    handleZoom(0.25)
  }
  if (e.key === '-' || e.key === '_') {
    handleZoom(-0.25)
  }
  
  // Escape取消选择
  if (e.key === 'Escape') {
    selectedBBox.value = null
    isDrawing.value = false
    isPanning.value = false
  }
}

// 缩放控制
const handleZoom = (delta: number) => {
  const newZoom = Math.max(minZoom, Math.min(maxZoom, zoomLevel.value + delta))
  zoomLevel.value = newZoom
}

// 滚轮缩放
const handleWheel = (event: WheelEvent) => {
  if (!currentImage.value) return
  
  // Ctrl + 滚轮 或 直接滚轮缩放
  if (event.ctrlKey || event.metaKey) {
    event.preventDefault()
    const delta = event.deltaY > 0 ? -0.1 : 0.1
    handleZoom(delta)
  }
}

// 获取调整大小手柄位置
const getResizeHandlePosition = (bbox: BoundingBox, handle: string) => {
  const x = normalizeToSVG(bbox.x, 'x')
  const y = normalizeToSVG(bbox.y, 'y')
  const w = bbox.width * scaledImageSize.value.width
  const h = bbox.height * scaledImageSize.value.height
  
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

// 获取绘制中边界框的样式
const getDrawingRect = computed(() => {
  if (!isDrawing.value) return null
  
  const x = Math.min(drawStart.value.x, drawCurrent.value.x)
  const y = Math.min(drawStart.value.y, drawCurrent.value.y)
  const width = Math.abs(drawCurrent.value.x - drawStart.value.x)
  const height = Math.abs(drawCurrent.value.y - drawStart.value.y)
  
  return { x, y, width, height }
})

// 获取选中的边界框
const selectedBBoxData = computed(() => {
  if (!selectedBBox.value || !currentImage.value) return null
  return currentImage.value.boundingBoxes.find(b => b.id === selectedBBox.value)
})

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

// 获取边界框的缩放后尺寸
const getScaledBBoxSize = (bbox: BoundingBox) => ({
  width: bbox.width * scaledImageSize.value.width,
  height: bbox.height * scaledImageSize.value.height
})
</script>

<template>
  <div class="smart-canvas" ref="canvasRef" @wheel="handleWheel">
    <!-- 隐藏的文件上传 input -->
    <input
      ref="fileInputRef"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleFileSelect"
    />
    
    <!-- 工具栏 -->
    <div class="canvas-toolbar">
      <div class="toolbar-group">
        <button
          @click="setTool('select')"
          :class="['tool-btn', { active: currentTool === 'select' }]"
          title="选择工具 (V)"
        >
          <Icon icon="ph:cursor" :width="20" />
        </button>
        <button
          @click="setTool('draw')"
          :class="['tool-btn', { active: currentTool === 'draw' }]"
          title="绘制工具 (B)"
        >
          <Icon icon="ph:selection" :width="20" />
        </button>
        <button
          @click="setTool('pan')"
          :class="['tool-btn', { active: currentTool === 'pan' }]"
          title="平移工具 (H)"
        >
          <Icon icon="ph:hand" :width="20" />
        </button>
      </div>
      
      <div class="toolbar-divider"></div>
      
      <div class="toolbar-group">
        <button
          @click="handleZoom(-0.25)"
          class="tool-btn"
          :disabled="zoomLevel <= minZoom"
          title="缩小 (-)"
        >
          <Icon icon="ph:minus" :width="18" />
        </button>
        <span class="zoom-label">{{ Math.round(zoomLevel * 100) }}%</span>
        <button
          @click="handleZoom(0.25)"
          class="tool-btn"
          :disabled="zoomLevel >= maxZoom"
          title="放大 (+)"
        >
          <Icon icon="ph:plus" :width="18" />
        </button>
        <button
          @click="resetView"
          class="tool-btn"
          title="重置视图 (0)"
        >
          <Icon icon="ph:arrows-in-simple" :width="18" />
        </button>
      </div>
      
      <div class="toolbar-divider"></div>
      
      <div class="toolbar-group">
        <button
          @click="triggerFileUpload"
          class="tool-btn upload"
          title="上传图像"
        >
          <Icon icon="ph:upload-simple" :width="18" />
          <span>上传</span>
        </button>
        <button
          v-if="currentImage && currentImage.boundingBoxes.length > 0"
          @click="exportAnnotations"
          class="tool-btn export"
          title="导出标注"
        >
          <Icon icon="ph:export" :width="18" />
          <span>导出</span>
        </button>
      </div>
      
      <div class="toolbar-divider" v-if="currentImage"></div>
      
      <div class="toolbar-group" v-if="currentImage">
        <button
          @click="confirmAllBBoxes"
          class="tool-btn success"
          title="确认所有标注"
        >
          <Icon icon="ph:check-circle" :width="20" />
          <span>全部确认</span>
        </button>
        <button
          v-if="localImage"
          @click="clearLocalImage"
          class="tool-btn danger"
          title="清除本地图像"
        >
          <Icon icon="ph:x-circle" :width="20" />
        </button>
      </div>
    </div>

    <!-- 空状态 - 支持拖拽上传 -->
    <div 
      v-if="!currentImage" 
      class="empty-canvas"
      @dragover="handleDragOver"
      @drop="handleDrop"
    >
      <div class="empty-icon">
        <Icon icon="ph:image-square" :width="80" />
      </div>
      <h3>请选择或上传图像</h3>
      <p>从左侧选择图像或拖拽/点击上传开始标注</p>
      <button class="upload-btn" @click="triggerFileUpload">
        <Icon icon="ph:upload-simple" :width="20" />
        <span>上传图像</span>
      </button>
    </div>

    <!-- 图像和覆盖层 -->
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
          'is-panning': isPanning
        }"
        @mousedown="handleDrawStart"
        @click="handleCanvasClick"
      >
        <!-- 图像包装器（用于统一变换） -->
        <div 
          ref="imageWrapperRef"
          class="image-wrapper"
          :style="{
            width: `${scaledImageSize.width}px`,
            height: `${scaledImageSize.height}px`,
            transform: `translate(${imageOffset.x}px, ${imageOffset.y}px)`
          }"
        >
          <img
            v-if="currentImage.url"
            ref="imageRef"
            :src="currentImage.url"
            :alt="currentImage.id"
            @load="handleImageLoad"
            class="canvas-image"
            :style="{
              width: `${scaledImageSize.width}px`,
              height: `${scaledImageSize.height}px`
            }"
            draggable="false"
          />
        </div>
        
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
          <!-- 现有边界框 -->
          <g
            v-for="bbox in currentImage.boundingBoxes"
            :key="bbox.id"
            @click.stop="handleBBoxClick(bbox, $event)"
            @mousedown.stop="handleBBoxMouseDown(bbox, $event)"
            :class="[
              'bbox-group',
              { 'selected': selectedBBox === bbox.id },
              { 'confirmed': bbox.status === 'confirmed' }
            ]"
          >
            <!-- 边界框 -->
            <rect
              :x="normalizeToSVG(bbox.x, 'x')"
              :y="normalizeToSVG(bbox.y, 'y')"
              :width="getScaledBBoxSize(bbox).width"
              :height="getScaledBBoxSize(bbox).height"
              :fill="getConfidenceColor(bbox.confidence)"
              :fill-opacity="bbox.status === 'confirmed' ? 0.15 : 0.08"
              :stroke="selectedBBox === bbox.id ? '#4A69FF' : getConfidenceColor(bbox.confidence)"
              :stroke-width="selectedBBox === bbox.id ? 3 : 2"
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
                :fill="selectedBBox === bbox.id ? '#4A69FF' : getConfidenceColor(bbox.confidence)"
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
            
            <!-- 调整大小手柄（仅选中时显示） -->
            <template v-if="selectedBBox === bbox.id && currentTool === 'select'">
              <circle
                v-for="handle in ['nw', 'ne', 'sw', 'se', 'n', 's', 'e', 'w']"
                :key="handle"
                :cx="getResizeHandlePosition(bbox, handle).x"
                :cy="getResizeHandlePosition(bbox, handle).y"
                r="6"
                fill="#4A69FF"
                stroke="white"
                stroke-width="2"
                class="resize-handle"
                :class="`handle-${handle}`"
                @mousedown.stop="handleBBoxMouseDown(bbox, $event, handle)"
              />
            </template>
          </g>
          
          <!-- 绘制中的边界框 -->
          <rect
            v-if="isDrawing && getDrawingRect"
            :x="getDrawingRect.x"
            :y="getDrawingRect.y"
            :width="getDrawingRect.width"
            :height="getDrawingRect.height"
            fill="rgba(74, 105, 255, 0.1)"
            stroke="#4A69FF"
            stroke-width="2"
            stroke-dasharray="8,4"
            rx="4"
            class="drawing-rect"
          />
        </svg>
      </div>

      <!-- 选中边界框的编辑面板 -->
      <div v-if="selectedBBoxData && currentTool === 'select'" class="bbox-edit-panel">
        <div class="edit-panel-header">
          <Icon icon="ph:pencil-simple" :width="18" />
          <span>编辑标注</span>
        </div>
        
        <div class="edit-panel-body">
          <div class="edit-row">
            <label>标签</label>
            <select 
              :value="selectedBBoxData.label"
              @change="updateLabel(($event.target as HTMLSelectElement).value)"
              class="label-select"
            >
              <option v-for="label in labelOptions" :key="label" :value="label">
                {{ label }}
              </option>
            </select>
          </div>
          
          <div class="edit-row">
            <label>置信度</label>
            <span class="confidence-value" :style="{ color: getConfidenceColor(selectedBBoxData.confidence) }">
              {{ Math.round(selectedBBoxData.confidence * 100) }}%
            </span>
          </div>
          
          <div class="edit-row">
            <label>状态</label>
            <span :class="['status-badge', selectedBBoxData.status]">
              {{ selectedBBoxData.status === 'confirmed' ? '已确认' : '待确认' }}
            </span>
          </div>
        </div>
        
        <div class="edit-panel-actions">
          <button 
            @click="confirmSelectedBBox"
            class="action-btn confirm"
            :disabled="selectedBBoxData.status === 'confirmed'"
          >
            <Icon icon="ph:check" :width="16" />
            确认
          </button>
          <button @click="deleteSelectedBBox" class="action-btn delete">
            <Icon icon="ph:trash" :width="16" />
            删除
          </button>
        </div>
      </div>

      <!-- 图像信息栏 -->
      <div class="image-info-bar">
        <div class="info-item">
          <Icon icon="ph:info" :width="16" />
          <span>{{ currentImage.id }}</span>
        </div>
        <div class="info-item" v-if="baseImageSize.naturalWidth > 0">
          <Icon icon="ph:frame-corners" :width="16" />
          <span>{{ baseImageSize.naturalWidth }}×{{ baseImageSize.naturalHeight }}</span>
        </div>
        <div class="info-item">
          <Icon icon="ph:square" :width="16" />
          <span>{{ currentImage.boundingBoxes.length }} 个标注</span>
        </div>
        <div class="info-item">
          <Icon icon="ph:source" :width="16" />
          <span>{{ currentImage.source === 'crawler' ? '爬虫' : 
                   currentImage.source === 'agent_recommended' ? 'Agent推荐' : 
                   '本地上传' }}</span>
        </div>
        <div class="info-item hint">
          <Icon icon="ph:keyboard" :width="16" />
          <span>V选择 | B绘制 | H平移 | 0重置 | ±缩放</span>
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

// 工具栏
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
  transition: all 0.2s ease;
  
  &:hover:not(:disabled) {
    background: var(--color-surface);
    color: var(--color-text-primary);
  }
  
  &.active {
    background: linear-gradient(135deg, rgba(74, 105, 255, 0.15), rgba(138, 43, 226, 0.15));
    color: var(--color-primary);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  &.success {
    width: auto;
    padding: 0 12px;
    color: #10b981;
    
    &:hover {
      background: rgba(16, 185, 129, 0.1);
    }
    
    span {
      font-size: 13px;
      font-weight: 500;
    }
  }
  
  &.upload {
    width: auto;
    padding: 0 12px;
    color: var(--color-primary);
    
    &:hover {
      background: rgba(74, 105, 255, 0.1);
    }
    
    span {
      font-size: 13px;
      font-weight: 500;
    }
  }
  
  &.export {
    width: auto;
    padding: 0 12px;
    color: #f59e0b;
    
    &:hover {
      background: rgba(245, 158, 11, 0.1);
    }
    
    span {
      font-size: 13px;
      font-weight: 500;
    }
  }
  
  &.danger {
    width: 36px;
    color: #ef4444;
    
    &:hover {
      background: rgba(239, 68, 68, 0.1);
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

// 空状态
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
}

.empty-canvas h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.empty-canvas p {
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
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(74, 105, 255, 0.15);
    border-style: solid;
    transform: translateY(-2px);
  }
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

.image-wrapper {
  position: absolute;
  will-change: transform;
}

.canvas-image {
  display: block;
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

// 边界框覆盖层
.bbox-overlay {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
  user-select: none;
  
  .bbox-group {
    pointer-events: all;
    cursor: pointer;
    
    .bbox-rect {
      transition: fill-opacity 0.2s ease, stroke 0.2s ease;
    }
    
    &:hover .bbox-rect {
      fill-opacity: 0.15;
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

// 编辑面板
.bbox-edit-panel {
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
}

.edit-panel-header {
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

.edit-panel-body {
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.edit-row {
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
  
  &:focus {
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
  }
  
  &.confirmed {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
  }
}

.edit-panel-actions {
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
  transition: all 0.2s ease;
  
  &.confirm {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
    
    &:hover:not(:disabled) {
      background: rgba(16, 185, 129, 0.25);
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
    }
  }
}

// 信息栏
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
    background: rgba(74, 105, 255, 0.08);
    padding: 4px 10px;
    border-radius: 6px;
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
