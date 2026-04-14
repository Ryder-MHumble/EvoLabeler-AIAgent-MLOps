/**
 * Mission Store
 *
 * 统一管理项目级协同标注状态。
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type {
  AgentLog,
  BoundingBox,
  DataStreamCategory,
  Mission,
  QueueState,
} from '@/api/types'
import { fetchAgentLogs } from '@/api/mocks/mock_logs'
import { fetchMissions, fetchMissionById, updateMissionStatus } from '@/api/mocks/mock_missions'
import { fetchImageStream } from '@/api/mocks/mock_stream'
import type { ActivityItem, WorkItem } from '@/mock/projectJourney'

const queuePriority: QueueState[] = ['ready', 'review', 'imported', 'done']

const toLogLevel = (tone: ActivityItem['tone']): AgentLog['level'] => {
  if (tone === 'success') return 'success'
  if (tone === 'warning') return 'warning'
  return 'info'
}

const activityToLog = (activity: ActivityItem): AgentLog => ({
  id: `log-${activity.id}`,
  timestamp: activity.timestamp,
  level: toLogLevel(activity.tone),
  category: activity.tone === 'loop' ? 'Loop' : 'Workspace',
  message: `${activity.title} · ${activity.detail}`,
})

const normalizeQueueState = (item: Partial<WorkItem>): QueueState => {
  if (item.queueState) return item.queueState
  if (item.status === 'confirmed' || item.status === 'archived') return 'done'
  return item.confidence && item.confidence >= 0.8 ? 'ready' : 'review'
}

const normalizeWorkItem = (item: Partial<WorkItem>, projectId: string): WorkItem => {
  const queueState = normalizeQueueState(item)
  return {
    id: item.id || `${projectId}-work-${Date.now()}`,
    projectId,
    url: item.url || '',
    thumbnailUrl: item.thumbnailUrl || item.url || '',
    source: item.source || 'manual',
    status: item.status || (queueState === 'done' ? 'confirmed' : queueState === 'ready' ? 'pending' : 'incoming'),
    queueState,
    confidence: item.confidence ?? 1,
    boundingBoxes: (item.boundingBoxes || []).map((bbox) => ({ ...bbox })),
    createdAt: item.createdAt || new Date().toISOString(),
    confirmedAt: item.confirmedAt,
    readyForCompletion: item.readyForCompletion ?? queueState === 'ready',
    analysis: item.analysis || {
      riskLevel: queueState === 'ready' ? 'low' : 'medium',
      reasons: ['等待项目工作台进一步分析。'],
      recommendedAction: queueState === 'ready' ? '确认并进入下一张' : '继续人工复核',
      tags: ['统一工作台'],
    },
    agentComment: item.agentComment || '等待协同工作台进一步处理当前样本。',
  }
}

export const useMissionStore = defineStore('mission', () => {
  const projectId = ref('')
  const currentMission = ref<Mission | null>(null)
  const missions = ref<Mission[]>([])
  const imageStream = ref<WorkItem[]>([])
  const currentImage = ref<WorkItem | null>(null)
  const agentLogs = ref<AgentLog[]>([])
  const isLoadingMissions = ref(false)
  const isLoadingStream = ref(false)
  const isLoadingLogs = ref(false)

  const currentWorkItem = computed(() => currentImage.value)

  const getImageStreamByCategory = computed(() => {
    return (category: DataStreamCategory): WorkItem[] => {
      if (category === 'incoming') {
        return imageStream.value.filter((item) => item.status === 'incoming')
      }
      if (category === 'pending') {
        return imageStream.value.filter((item) => item.status === 'pending')
      }
      if (category === 'library') {
        return imageStream.value.filter(
          (item) => item.status === 'confirmed' || item.status === 'archived',
        )
      }
      return []
    }
  })

  const getImageStreamByQueue = computed(() => {
    return (queueState: QueueState): WorkItem[] =>
      imageStream.value.filter((item) => item.queueState === queueState)
  })

  const orderedWorkItems = computed(() =>
    [...imageStream.value].sort((left, right) => {
      return queuePriority.indexOf(left.queueState) - queuePriority.indexOf(right.queueState)
    }),
  )

  const streamStats = computed(() => {
    const ready = imageStream.value.filter((item) => item.queueState === 'ready').length
    const review = imageStream.value.filter((item) => item.queueState === 'review').length
    const imported = imageStream.value.filter((item) => item.queueState === 'imported').length
    const done = imageStream.value.filter((item) => item.queueState === 'done').length

    return {
      incoming: review,
      pending: ready + imported,
      library: done,
      total: imageStream.value.length,
      ready,
      review,
      imported,
      done,
    }
  })

  const loadMissions = async () => {
    isLoadingMissions.value = true
    try {
      const data = await fetchMissions()
      missions.value = data
      if (!currentMission.value && data.length > 0) {
        currentMission.value = data[0]
      }
    } finally {
      isLoadingMissions.value = false
    }
  }

  const selectMission = async (missionId: string) => {
    const mission = await fetchMissionById(missionId)
    if (mission) {
      currentMission.value = mission
      projectId.value = missionId.replace(/^mission-/, '')
      await loadImageStream()
    }
  }

  const loadImageStream = async () => {
    isLoadingStream.value = true
    try {
      const data = await fetchImageStream()
      imageStream.value = data.map((item) =>
        normalizeWorkItem(item as Partial<WorkItem>, projectId.value || 'legacy'),
      )
      currentImage.value = orderedWorkItems.value[0] || imageStream.value[0] || null
    } finally {
      isLoadingStream.value = false
    }
  }

  const loadAgentLogs = async () => {
    isLoadingLogs.value = true
    try {
      agentLogs.value = await fetchAgentLogs()
    } finally {
      isLoadingLogs.value = false
    }
  }

  const hydrateProjectMission = (
    mission: Mission,
    workItems: WorkItem[],
    activities: ActivityItem[] = [],
  ) => {
    projectId.value = mission.id.replace(/^mission-/, '')
    missions.value = [mission]
    currentMission.value = mission
    imageStream.value = workItems.map((item) => normalizeWorkItem(item, projectId.value))
    currentImage.value =
      orderedWorkItems.value.find((item) => item.queueState !== 'done') ||
      orderedWorkItems.value[0] ||
      null
    agentLogs.value = activities.map(activityToLog)
  }

  const setAgentLogsFromActivities = (activities: ActivityItem[]) => {
    agentLogs.value = activities.map(activityToLog)
  }

  const selectImage = (imageId: string) => {
    const image = imageStream.value.find((item) => item.id === imageId)
    if (image) {
      currentImage.value = image
    }
  }

  const selectNextImage = () => {
    currentImage.value =
      orderedWorkItems.value.find((item) => item.queueState !== 'done') ||
      orderedWorkItems.value[0] ||
      null
    return currentImage.value
  }

  const setImageStream = (items: WorkItem[]) => {
    imageStream.value = items.map((item) => normalizeWorkItem(item, projectId.value || item.projectId))
    if (!currentImage.value || !imageStream.value.some((item) => item.id === currentImage.value?.id)) {
      selectNextImage()
    }
  }

  const addImageToStream = async (image: Partial<WorkItem>, select = true) => {
    const normalized = normalizeWorkItem(image, projectId.value || image.projectId || 'manual')
    imageStream.value.unshift(normalized)
    if (select) {
      currentImage.value = normalized
    }
    return normalized
  }

  const updateLocalBBox = (imageId: string, bboxId: string, updates: Partial<BoundingBox>) => {
    const image = imageStream.value.find((item) => item.id === imageId)
    if (!image) return null
    const bbox = image.boundingBoxes.find((entry) => entry.id === bboxId)
    if (!bbox) return null
    Object.assign(bbox, updates)
    if (currentImage.value?.id === imageId) {
      currentImage.value = image
    }
    image.readyForCompletion = image.boundingBoxes.every((entry) => entry.status === 'confirmed')
    return bbox
  }

  const updateBBox = async (imageId: string, bboxId: string, updates: Partial<BoundingBox>) => {
    return updateLocalBBox(imageId, bboxId, updates)
  }

  const confirmImageTask = async (imageId: string) => {
    const image = imageStream.value.find((item) => item.id === imageId)
    if (!image) return null
    image.queueState = 'done'
    image.status = 'confirmed'
    image.confirmedAt = new Date().toISOString()
    image.readyForCompletion = false
    image.boundingBoxes.forEach((bbox) => {
      bbox.status = 'confirmed'
    })
    if (currentImage.value?.id === imageId) {
      selectNextImage()
    }
    return image
  }

  const completeCurrentImage = () => {
    if (!currentImage.value) return null
    currentImage.value.boundingBoxes.forEach((bbox) => {
      bbox.status = 'confirmed'
    })
    currentImage.value.status = 'confirmed'
    currentImage.value.queueState = 'done'
    currentImage.value.readyForCompletion = false
    currentImage.value.confirmedAt = new Date().toISOString()
    return selectNextImage()
  }

  const markCurrentForReview = () => {
    if (!currentImage.value) return null
    currentImage.value.queueState = 'review'
    currentImage.value.status = 'incoming'
    currentImage.value.readyForCompletion = false
    return selectNextImage()
  }

  const skipCurrentImage = () => {
    return markCurrentForReview()
  }

  const updateMission = async (missionId: string, status: Mission['status'], progress?: number) => {
    const updated = await updateMissionStatus(missionId, status, progress)
    const index = missions.value.findIndex((item) => item.id === missionId)
    if (index !== -1) {
      missions.value[index] = updated
    }
    if (currentMission.value?.id === missionId) {
      currentMission.value = updated
    }
    return updated
  }

  return {
    projectId,
    currentMission,
    missions,
    imageStream,
    currentImage,
    currentWorkItem,
    agentLogs,
    isLoadingMissions,
    isLoadingStream,
    isLoadingLogs,
    getImageStreamByCategory,
    getImageStreamByQueue,
    orderedWorkItems,
    streamStats,
    loadMissions,
    selectMission,
    loadImageStream,
    loadAgentLogs,
    hydrateProjectMission,
    setAgentLogsFromActivities,
    setImageStream,
    selectImage,
    selectNextImage,
    addImageToStream,
    confirmImageTask,
    updateBBox,
    completeCurrentImage,
    markCurrentForReview,
    skipCurrentImage,
    updateMission,
  }
})
