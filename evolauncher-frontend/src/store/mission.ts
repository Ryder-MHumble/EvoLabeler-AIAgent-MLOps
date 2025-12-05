/**
 * Mission Store
 * 
 * 管理任务状态、数据流和 Agent 日志
 * 使用 Pinia 进行状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Mission, ImageTask, AgentLog, DataStreamCategory } from '@/api/types'
import { fetchMissions, fetchMissionById, updateMissionStatus } from '@/api/mocks/mock_missions'
import { fetchImageStream, updateImageTaskStatus, updateBoundingBox } from '@/api/mocks/mock_stream'
import { fetchAgentLogs, createAgentLogStream } from '@/api/mocks/mock_logs'

export const useMissionStore = defineStore('mission', () => {
  // ========== State ==========
  
  // 当前选中的任务
  const currentMission = ref<Mission | null>(null)
  
  // 所有任务列表
  const missions = ref<Mission[]>([])
  
  // 图像数据流
  const imageStream = ref<ImageTask[]>([])
  
  // 当前选中的图像
  const currentImage = ref<ImageTask | null>(null)
  
  // Agent 日志列表
  const agentLogs = ref<AgentLog[]>([])
  
  // 日志流控制
  const logStreamStop = ref<(() => void) | null>(null)
  
  // 加载状态
  const isLoadingMissions = ref(false)
  const isLoadingStream = ref(false)
  const isLoadingLogs = ref(false)

  // ========== Getters ==========
  
  /**
   * 按分类获取图像流
   */
  const getImageStreamByCategory = computed(() => {
    return (category: DataStreamCategory): ImageTask[] => {
      if (category === 'incoming') {
        return imageStream.value.filter(img => img.status === 'incoming')
      } else if (category === 'pending') {
        return imageStream.value.filter(img => img.status === 'pending')
      } else if (category === 'library') {
        return imageStream.value.filter(img => img.status === 'confirmed' || img.status === 'archived')
      }
      return []
    }
  })

  /**
   * 数据流统计
   */
  const streamStats = computed(() => {
    return {
      incoming: imageStream.value.filter(img => img.status === 'incoming').length,
      pending: imageStream.value.filter(img => img.status === 'pending').length,
      library: imageStream.value.filter(img => img.status === 'confirmed' || img.status === 'archived').length,
      total: imageStream.value.length
    }
  })

  // ========== Actions ==========
  
  /**
   * 加载所有任务
   */
  const loadMissions = async () => {
    isLoadingMissions.value = true
    try {
      const data = await fetchMissions()
      missions.value = data
      
      // 如果没有当前任务，设置第一个为当前任务
      if (!currentMission.value && data.length > 0) {
        currentMission.value = data[0]
      }
    } catch (error) {
      console.error('Failed to load missions:', error)
      throw error
    } finally {
      isLoadingMissions.value = false
    }
  }

  /**
   * 选择任务
   */
  const selectMission = async (missionId: string) => {
    try {
      const mission = await fetchMissionById(missionId)
      if (mission) {
        currentMission.value = mission
        // 加载该任务的数据流
        await loadImageStream()
        // 启动日志流
        startLogStream()
      }
    } catch (error) {
      console.error('Failed to select mission:', error)
      throw error
    }
  }

  /**
   * 加载图像数据流
   */
  const loadImageStream = async () => {
    isLoadingStream.value = true
    try {
      const data = await fetchImageStream()
      imageStream.value = data
    } catch (error) {
      console.error('Failed to load image stream:', error)
      throw error
    } finally {
      isLoadingStream.value = false
    }
  }

  /**
   * 选择图像
   */
  const selectImage = (imageId: string) => {
    const image = imageStream.value.find(img => img.id === imageId)
    if (image) {
      currentImage.value = image
    }
  }

  /**
   * 确认图像任务
   */
  const confirmImageTask = async (imageId: string) => {
    try {
      const updated = await updateImageTaskStatus(imageId, 'confirmed')
      
      // 更新本地状态
      const index = imageStream.value.findIndex(img => img.id === imageId)
      if (index !== -1) {
        imageStream.value[index] = updated
      }
      
      // 如果当前图像被确认，更新当前图像
      if (currentImage.value?.id === imageId) {
        currentImage.value = updated
      }
      
      return updated
    } catch (error) {
      console.error('Failed to confirm image task:', error)
      throw error
    }
  }

  /**
   * 更新边界框
   */
  const updateBBox = async (
    imageId: string,
    bboxId: string,
    updates: Partial<import('@/api/types').BoundingBox>
  ) => {
    try {
      const updated = await updateBoundingBox(imageId, bboxId, updates)
      
      // 更新本地状态
      const image = imageStream.value.find(img => img.id === imageId)
      if (image) {
        const bboxIndex = image.boundingBoxes.findIndex(b => b.id === bboxId)
        if (bboxIndex !== -1) {
          image.boundingBoxes[bboxIndex] = updated
        }
      }
      
      // 如果当前图像被更新，同步更新
      if (currentImage.value?.id === imageId) {
        const bboxIndex = currentImage.value.boundingBoxes.findIndex(b => b.id === bboxId)
        if (bboxIndex !== -1) {
          currentImage.value.boundingBoxes[bboxIndex] = updated
        }
      }
      
      return updated
    } catch (error) {
      console.error('Failed to update bounding box:', error)
      throw error
    }
  }

  /**
   * 加载 Agent 日志
   */
  const loadAgentLogs = async () => {
    isLoadingLogs.value = true
    try {
      const logs = await fetchAgentLogs()
      agentLogs.value = logs
    } catch (error) {
      console.error('Failed to load agent logs:', error)
      throw error
    } finally {
      isLoadingLogs.value = false
    }
  }

  /**
   * 启动日志流
   */
  const startLogStream = () => {
    // 先停止现有的流
    if (logStreamStop.value) {
      logStreamStop.value()
    }
    
    // 创建新的日志流
    logStreamStop.value = createAgentLogStream((log: AgentLog) => {
      agentLogs.value.push(log)
      
      // 保持最多 200 条日志
      if (agentLogs.value.length > 200) {
        agentLogs.value = agentLogs.value.slice(-200)
      }
    }, 3000)
  }

  /**
   * 停止日志流
   */
  const stopLogStream = () => {
    if (logStreamStop.value) {
      logStreamStop.value()
      logStreamStop.value = null
    }
  }

  /**
   * 更新任务状态
   */
  const updateMission = async (
    missionId: string,
    status: Mission['status'],
    progress?: number
  ) => {
    try {
      const updated = await updateMissionStatus(missionId, status, progress)
      
      // 更新本地状态
      const index = missions.value.findIndex(m => m.id === missionId)
      if (index !== -1) {
        missions.value[index] = updated
      }
      
      // 如果当前任务被更新，同步更新
      if (currentMission.value?.id === missionId) {
        currentMission.value = updated
      }
      
      return updated
    } catch (error) {
      console.error('Failed to update mission:', error)
      throw error
    }
  }

  return {
    // State
    currentMission,
    missions,
    imageStream,
    currentImage,
    agentLogs,
    isLoadingMissions,
    isLoadingStream,
    isLoadingLogs,
    
    // Getters
    getImageStreamByCategory,
    streamStats,
    
    // Actions
    loadMissions,
    selectMission,
    loadImageStream,
    selectImage,
    confirmImageTask,
    updateBBox,
    loadAgentLogs,
    startLogStream,
    stopLogStream,
    updateMission
  }
})


