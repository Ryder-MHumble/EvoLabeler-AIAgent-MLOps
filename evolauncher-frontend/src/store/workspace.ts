/**
 * Workspace Store
 *
 * 为统一项目工作台提供训练侧状态。
 */

import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { modelsApi } from '@/api/models'
import { USE_BACKEND_API } from '@/api/client'
import type {
  EvoRound,
  MetricsHistoryEntry,
  ModelHealthResponse,
  ModelVersion,
} from '@/api/models'
import type { YoloLossData } from '@/components/workspace/types'
import type { JobStatus } from '@/mock/jobStatus'
import { createProjectJourneySeed, type JourneyTrainState } from '@/mock/projectJourney'
import { fetchProjectById } from '@/mock/projects'

const emptyLossData = (): YoloLossData => ({
  epochs: [1],
  boxLoss: [0],
  clsLoss: [0],
  objLoss: [0],
  totalLoss: [0],
  valLoss: [0],
})

export const useWorkspaceStore = defineStore('workspace', () => {
  const projectId = ref('')
  const evoRounds = ref<EvoRound[]>([])
  const modelVersions = ref<ModelVersion[]>([])
  const healthReport = ref<ModelHealthResponse | null>(null)
  const metricsHistory = ref<MetricsHistoryEntry[]>([])
  const jobStatus = ref<JobStatus | null>(null)
  const lossData = ref<YoloLossData>(emptyLossData())
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  let healthPollInterval: ReturnType<typeof setInterval> | null = null
  let roundsPollInterval: ReturnType<typeof setInterval> | null = null

  const currentRound = computed(() => {
    if (evoRounds.value.length === 0) return 0
    return Math.max(...evoRounds.value.map((round) => round.roundNumber))
  })

  const bestVersion = computed(() => modelVersions.value.find((version) => version.isBest))
  const activeVersion = computed(() => modelVersions.value.find((version) => version.isActive))
  const overallHealth = computed(() => healthReport.value?.healthReport.overallStatus || 'unknown')

  const applyDemoWorkspace = (state: JourneyTrainState) => {
    jobStatus.value = state.jobStatus
    lossData.value = state.lossData
    evoRounds.value = state.evoRounds
    modelVersions.value = state.modelVersions
    healthReport.value = state.healthReport
    metricsHistory.value = state.metricsHistory
  }

  const getTrainState = (): JourneyTrainState => ({
    jobStatus: jobStatus.value,
    lossData: lossData.value,
    evoRounds: evoRounds.value,
    modelVersions: modelVersions.value,
    healthReport: healthReport.value,
    metricsHistory: metricsHistory.value,
  })

  async function loadProjectWorkspace(id: string) {
    projectId.value = id
    isLoading.value = true
    error.value = null

    if (!USE_BACKEND_API) {
      const project = await fetchProjectById(id).catch(() => undefined)
      applyDemoWorkspace(createProjectJourneySeed(project || {
        id,
        name: '新建进化项目',
        description: '统一项目工作台正在准备训练上下文。',
        status: 'idle',
        imageCount: 24,
        accuracy: 0,
        thumbnailUrl: '',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }).finalSnapshot.train)
      isLoading.value = false
      return
    }

    try {
      const [versionsRes, healthRes, historyRes, roundsRes] = await Promise.allSettled([
        modelsApi.listVersions(id),
        modelsApi.getHealth(id),
        modelsApi.getHistory(id, 20),
        modelsApi.listRounds(id),
      ])

      modelVersions.value = versionsRes.status === 'fulfilled' ? versionsRes.value.versions : []
      healthReport.value = healthRes.status === 'fulfilled' ? healthRes.value : null
      metricsHistory.value = historyRes.status === 'fulfilled' ? historyRes.value.history : []
      evoRounds.value = roundsRes.status === 'fulfilled' ? roundsRes.value.rounds : []
    } catch (err) {
      error.value = err instanceof Error ? err.message : String(err)
    } finally {
      isLoading.value = false
    }
  }

  async function refreshHealth() {
    if (!USE_BACKEND_API || !projectId.value) return
    try {
      healthReport.value = await modelsApi.getHealth(projectId.value)
    } catch (err) {
      console.warn('[workspace] Failed to refresh health:', err)
    }
  }

  async function refreshRounds() {
    if (!USE_BACKEND_API || !projectId.value) return
    try {
      const rounds = await modelsApi.listRounds(projectId.value)
      evoRounds.value = rounds.rounds
    } catch (err) {
      console.warn('[workspace] Failed to refresh rounds:', err)
    }
  }

  async function rollbackModel(versionId: string) {
    if (!USE_BACKEND_API || !projectId.value) return
    try {
      await modelsApi.rollback(projectId.value, versionId)
      await loadProjectWorkspace(projectId.value)
    } catch (err) {
      error.value = err instanceof Error ? err.message : String(err)
    }
  }

  const startPolling = () => {
    stopPolling()
    if (!USE_BACKEND_API) return

    healthPollInterval = setInterval(() => {
      refreshHealth()
    }, 10_000)
    roundsPollInterval = setInterval(() => {
      refreshRounds()
    }, 30_000)
  }

  const stopPolling = () => {
    if (healthPollInterval) {
      clearInterval(healthPollInterval)
      healthPollInterval = null
    }
    if (roundsPollInterval) {
      clearInterval(roundsPollInterval)
      roundsPollInterval = null
    }
  }

  return {
    projectId,
    evoRounds,
    modelVersions,
    healthReport,
    metricsHistory,
    jobStatus,
    lossData,
    isLoading,
    error,
    currentRound,
    bestVersion,
    activeVersion,
    overallHealth,
    applyDemoWorkspace,
    getTrainState,
    loadProjectWorkspace,
    refreshHealth,
    refreshRounds,
    rollbackModel,
    startPolling,
    stopPolling,
  }
})
