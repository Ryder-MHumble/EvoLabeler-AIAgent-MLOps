/**
 * 标注管理 Composable
 * 负责标注框的创建、编辑、选择等功能
 */

import { ref, computed, type Ref } from 'vue'
import type { BoundingBox } from '@/api/types'
import { useMissionStore } from '@/store/mission'
import { ElMessage } from 'element-plus'
import { MIN_BBOX_SIZE } from '../constants/annotation'
import type { ToolType } from '../constants/annotation'
import { annotationsApi } from '@/api/annotations'
import { USE_BACKEND_API } from '@/api/client'

export const useAnnotation = (
  currentTool: Ref<ToolType>,
  imageWrapperRef: Ref<HTMLDivElement | null>,
  scaledImageSize: Ref<{ width: number; height: number }>,
  svgToNormalize: (pixel: number, dimension: 'x' | 'y') => number
) => {
  const missionStore = useMissionStore()

  // 选中的边界框
  const selectedBBox = ref<string | null>(null)

  // 拖动状态
  const isDragging = ref(false)
  const dragStart = ref({ x: 0, y: 0, bbox: null as BoundingBox | null })
  const resizeHandle = ref<string | null>(null)

  // 绘制状态
  const isDrawing = ref(false)
  const drawStart = ref({ x: 0, y: 0 })
  const drawCurrent = ref({ x: 0, y: 0 })

  // 当前图像（本地或store）
  const currentImage = computed(() => {
    return missionStore.currentImage
  })

  // 获取选中的边界框数据
  const selectedBBoxData = computed(() => {
    if (!selectedBBox.value || !currentImage.value) return null
    return currentImage.value.boundingBoxes.find(b => b.id === selectedBBox.value)
  })

  // 获取绘制中的边界框
  const getDrawingRect = computed(() => {
    if (!isDrawing.value) return null

    return {
      x: Math.min(drawStart.value.x, drawCurrent.value.x),
      y: Math.min(drawStart.value.y, drawCurrent.value.y),
      width: Math.abs(drawCurrent.value.x - drawStart.value.x),
      height: Math.abs(drawCurrent.value.y - drawStart.value.y)
    }
  })

  /**
   * 点击边界框
   */
  const handleBBoxClick = (bbox: BoundingBox) => {
    if (currentTool.value !== 'select') return
    selectedBBox.value = bbox.id
  }

  /**
   * 点击画布空白处
   */
  const handleCanvasClick = () => {
    if (currentTool.value === 'select') {
      selectedBBox.value = null
    }
  }

  /**
   * 开始拖动边界框
   */
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

  /**
   * 开始绘制新边界框
   */
  const handleDrawStart = (event: MouseEvent) => {
    if (!imageWrapperRef.value || currentTool.value !== 'draw') return

    event.preventDefault()
    const rect = imageWrapperRef.value.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    isDrawing.value = true
    drawStart.value = { x, y }
    drawCurrent.value = { x, y }
  }

  /**
   * 绘制移动
   */
  const handleDrawMove = (event: MouseEvent) => {
    if (!isDrawing.value || !imageWrapperRef.value) return

    const rect = imageWrapperRef.value.getBoundingClientRect()
    drawCurrent.value = {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    }
  }

  /**
   * 拖动/调整大小移动
   */
  const handleBBoxMove = (event: MouseEvent) => {
    if (!selectedBBox.value || !currentImage.value) return

    const bbox = currentImage.value.boundingBoxes.find(b => b.id === selectedBBox.value)
    if (!bbox) return

    const deltaX = (event.clientX - dragStart.value.x) / scaledImageSize.value.width
    const deltaY = (event.clientY - dragStart.value.y) / scaledImageSize.value.height

    if (isDragging.value && dragStart.value.bbox) {
      // 拖动整个边界框
      bbox.x = Math.max(0, Math.min(1 - bbox.width, dragStart.value.bbox.x + deltaX))
      bbox.y = Math.max(0, Math.min(1 - bbox.height, dragStart.value.bbox.y + deltaY))
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
      if (newX + newWidth > 1) newWidth = 1 - newX
      if (newY + newHeight > 1) newHeight = 1 - newY

      bbox.x = newX
      bbox.y = newY
      bbox.width = newWidth
      bbox.height = newHeight
    }
  }

  /**
   * 完成绘制
   */
  const finishDraw = () => {
    if (!isDrawing.value || !currentImage.value) return

    const x1 = svgToNormalize(Math.min(drawStart.value.x, drawCurrent.value.x), 'x')
    const y1 = svgToNormalize(Math.min(drawStart.value.y, drawCurrent.value.y), 'y')
    const x2 = svgToNormalize(Math.max(drawStart.value.x, drawCurrent.value.x), 'x')
    const y2 = svgToNormalize(Math.max(drawStart.value.y, drawCurrent.value.y), 'y')

    const width = x2 - x1
    const height = y2 - y1

    if (width > MIN_BBOX_SIZE && height > MIN_BBOX_SIZE) {
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
      currentTool.value = 'select'

      // Persist to backend (fire-and-forget)
      if (USE_BACKEND_API) {
        annotationsApi
          .create({
            projectId: missionStore.currentMission?.id || '',
            imageId: currentImage.value.id,
            bboxes: [
              {
                x: x1,
                y: y1,
                width,
                height,
                label: '目标',
                confidence: 1.0
              }
            ]
          })
          .catch(err => {
            console.warn('[annotation] Failed to persist new bbox:', err)
          })
      }

      ElMessage.success('标注框已创建，请设置标签')
    }

    isDrawing.value = false
    drawStart.value = { x: 0, y: 0 }
    drawCurrent.value = { x: 0, y: 0 }
  }

  /**
   * 完成拖动/调整大小
   */
  const finishBBoxEdit = () => {
    if ((isDragging.value || resizeHandle.value) && selectedBBox.value && currentImage.value) {
      const bbox = currentImage.value.boundingBoxes.find(b => b.id === selectedBBox.value)
      if (bbox) {
        missionStore.updateBBox(currentImage.value.id, bbox.id, {
          x: bbox.x,
          y: bbox.y,
          width: bbox.width,
          height: bbox.height
        })

        if (USE_BACKEND_API) {
          annotationsApi
            .update(bbox.id, {
              bboxes: [
                {
                  x: bbox.x,
                  y: bbox.y,
                  width: bbox.width,
                  height: bbox.height,
                  label: bbox.label || '目标',
                  confidence: bbox.confidence
                }
              ]
            })
            .catch(err => {
              console.warn('[annotation] Failed to persist bbox edit:', err)
            })
        }
      }
    }

    isDragging.value = false
    resizeHandle.value = null
    dragStart.value = { x: 0, y: 0, bbox: null }
  }

  /**
   * 确认选中的标注框
   */
  const confirmSelectedBBox = () => {
    if (!selectedBBox.value || !currentImage.value) return

    const bbox = currentImage.value.boundingBoxes.find(b => b.id === selectedBBox.value)
    if (bbox && bbox.status === 'pending') {
      missionStore.updateBBox(currentImage.value.id, bbox.id, { status: 'confirmed' })

      if (USE_BACKEND_API) {
        annotationsApi
          .update(bbox.id, {
            bboxes: [
              {
                x: bbox.x,
                y: bbox.y,
                width: bbox.width,
                height: bbox.height,
                label: bbox.label || '目标',
                confidence: bbox.confidence
              }
            ],
            metadata: { status: 'confirmed' }
          })
          .catch(err => {
            console.warn('[annotation] Failed to persist confirmation:', err)
          })
      }

      ElMessage.success('标注已确认')
    }
  }

  /**
   * 删除选中的标注框
   */
  const deleteSelectedBBox = () => {
    if (!selectedBBox.value || !currentImage.value) return

    const index = currentImage.value.boundingBoxes.findIndex(b => b.id === selectedBBox.value)
    if (index > -1) {
      const deletedBBoxId = currentImage.value.boundingBoxes[index].id
      currentImage.value.boundingBoxes.splice(index, 1)
      selectedBBox.value = null

      if (USE_BACKEND_API) {
        annotationsApi.delete(deletedBBoxId).catch(err => {
          console.warn('[annotation] Failed to persist deletion:', err)
        })
      }

      ElMessage.info('标注已删除')
    }
  }

  /**
   * 更新标签
   */
  const updateLabel = (label: string) => {
    if (!selectedBBox.value || !currentImage.value) return

    const bbox = currentImage.value.boundingBoxes.find(b => b.id === selectedBBox.value)
    if (bbox) {
      missionStore.updateBBox(currentImage.value.id, bbox.id, { label })

      if (USE_BACKEND_API) {
        annotationsApi
          .update(bbox.id, {
            bboxes: [
              {
                x: bbox.x,
                y: bbox.y,
                width: bbox.width,
                height: bbox.height,
                label,
                confidence: bbox.confidence
              }
            ]
          })
          .catch(err => {
            console.warn('[annotation] Failed to persist label update:', err)
          })
      }
    }
  }

  /**
   * 重置状态
   */
  const resetState = () => {
    selectedBBox.value = null
    isDragging.value = false
    resizeHandle.value = null
    isDrawing.value = false
  }

  return {
    // State
    selectedBBox,
    isDragging,
    resizeHandle,
    isDrawing,
    drawStart,
    drawCurrent,
    currentImage,
    selectedBBoxData,
    getDrawingRect,

    // Methods
    handleBBoxClick,
    handleCanvasClick,
    handleBBoxMouseDown,
    handleDrawStart,
    handleDrawMove,
    handleBBoxMove,
    finishDraw,
    finishBBoxEdit,
    confirmSelectedBBox,
    deleteSelectedBBox,
    updateLabel,
    resetState
  }
}
