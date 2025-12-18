/**
 * 图像上传 Composable
 * 负责单张图像上传和拖拽上传功能
 */

import { ref, type Ref } from 'vue'
import { ElMessage } from 'element-plus'

import type { BoundingBox } from '@/api/types'

export interface LocalImage {
  id: string
  url: string
  thumbnailUrl?: string
  confidence: number
  source: 'manual' | 'crawler' | 'agent_recommended'
  boundingBoxes: BoundingBox[]
  status: 'incoming' | 'pending' | 'confirmed' | 'archived'
  createdAt: string
}

export const useImageUpload = (
  imageLoaded: Ref<boolean>,
  resetView: () => void,
  resetAnnotation: () => void
) => {
  const fileInputRef = ref<HTMLInputElement | null>(null)
  const localImage = ref<LocalImage | null>(null)

  /**
   * 触发文件选择
   */
  const triggerFileUpload = () => {
    fileInputRef.value?.click()
  }

  /**
   * 处理文件选择
   */
  const handleFileSelect = (event: Event) => {
    const target = event.target as HTMLInputElement
    if (!target.files || !target.files[0]) return
    
    const file = target.files[0]
    processImageFile(file)
    target.value = '' // 清空以便再次选择同一文件
  }

  /**
   * 处理拖拽上传
   */
  const handleDrop = (event: DragEvent) => {
    event.preventDefault()
    
    if (!event.dataTransfer?.files || !event.dataTransfer.files[0]) return
    
    const file = event.dataTransfer.files[0]
    if (file.type.startsWith('image/')) {
      processImageFile(file)
    }
  }

  /**
   * 处理拖拽悬停
   */
  const handleDragOver = (event: DragEvent) => {
    event.preventDefault()
  }

  /**
   * 处理图像文件
   */
  const processImageFile = (file: File) => {
    const reader = new FileReader()
    
    reader.onload = (e) => {
      const url = e.target?.result as string
      localImage.value = {
        id: `upload-${Date.now()}`,
        url,
        thumbnailUrl: url,
        confidence: 1.0,
        source: 'manual',
        boundingBoxes: [],
        status: 'incoming',
        createdAt: new Date().toISOString()
      }
      imageLoaded.value = false
      resetView()
      resetAnnotation()
      
      ElMessage.success('图像已加载，开始标注吧！')
    }
    
    reader.readAsDataURL(file)
  }

  /**
   * 清除所有选择
   */
  const clearAllSelection = (clearStoreImage: () => void) => {
    localImage.value = null
    clearStoreImage()
    imageLoaded.value = false
    resetView()
    resetAnnotation()
  }

  return {
    fileInputRef,
    localImage,
    triggerFileUpload,
    handleFileSelect,
    handleDrop,
    handleDragOver,
    clearAllSelection
  }
}

