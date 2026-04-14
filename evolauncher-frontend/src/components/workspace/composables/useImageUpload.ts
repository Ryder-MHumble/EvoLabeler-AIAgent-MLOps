/**
 * 图像上传 Composable
 * 负责单张图像上传和拖拽上传功能
 */

import { ref, type Ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useMissionStore } from '@/store/mission'
import type { WorkItem } from '@/mock/projectJourney'

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
  const missionStore = useMissionStore()
  const fileInputRef = ref<HTMLInputElement | null>(null)

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
      const workItem: Partial<WorkItem> = {
        id: `upload-${Date.now()}`,
        projectId: missionStore.projectId || missionStore.currentMission?.id.replace(/^mission-/, '') || 'manual',
        url,
        thumbnailUrl: url,
        confidence: 1.0,
        source: 'manual',
        boundingBoxes: [],
        status: 'incoming',
        queueState: 'review',
        readyForCompletion: false,
        createdAt: new Date().toISOString(),
        analysis: {
          riskLevel: 'medium',
          reasons: ['本地上传样本已进入统一工作台。', '建议补充标注后确认并推进下一张。'],
          recommendedAction: '完成当前样本后继续处理下一张。',
          tags: ['本地上传'],
        },
        agentComment: '这是你刚刚上传的本地样本，系统已把它接入统一协同队列。'
      }
      missionStore.addImageToStream(workItem, true)
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
    clearStoreImage()
    imageLoaded.value = false
    resetView()
    resetAnnotation()
  }

  return {
    fileInputRef,
    triggerFileUpload,
    handleFileSelect,
    handleDrop,
    handleDragOver,
    clearAllSelection
  }
}
