/**
 * Workspace Store
 *
 * Manages all workspace data for a given project:
 * model versions, health reports, metrics history, and EvoLoop rounds.
 * Data is fetched from the backend via modelsApi and polled at intervals.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { modelsApi } from '@/api/models'
import { USE_BACKEND_API } from '@/api/client'
import type {
  ModelVersion,
  ModelHealthResponse,
  MetricsHistoryEntry,
  EvoRound,
} from '@/api/models'

export const useWorkspaceStore = defineStore('workspace', () => {
  // ============================================
  // State
  // ============================================

  const projectId = ref<string>('')
  const evoRounds = ref<EvoRound[]>([])
  const modelVersions = ref<ModelVersion[]>([])
  const healthReport = ref<ModelHealthResponse | null>(null)
  const metricsHistory = ref<MetricsHistoryEntry[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  // Polling handles
  let healthPollInterval: ReturnType<typeof setInterval> | null = null
  let roundsPollInterval: ReturnType<typeof setInterval> | null = null

  // ============================================
  // Computed
  // ============================================

  /** Latest round number, or 0 if no rounds exist. */
  const currentRound = computed<number>(() => {
    if (evoRounds.value.length === 0) return 0
    return Math.max(...evoRounds.value.map((r) => r.roundNumber))
  })

  /** The model version marked as best, if any. */
  const bestVersion = computed<ModelVersion | undefined>(() => {
    return modelVersions.value.find((v) => v.isBest)
  })

  /** The model version marked as active, if any. */
  const activeVersion = computed<ModelVersion | undefined>(() => {
    return modelVersions.value.find((v) => v.isActive)
  })

  /** Simplified overall health status string. */
  const overallHealth = computed<string>(() => {
    if (!healthReport.value) return 'unknown'
    return healthReport.value.healthReport.overallStatus
  })

  // ============================================
  // Actions
  // ============================================

  /**
   * Load all workspace data for a project in parallel.
   * Falls back to empty state if the backend is not available.
   */
  async function loadProjectWorkspace(id: string) {
    projectId.value = id
    isLoading.value = true
    error.value = null

    if (!USE_BACKEND_API) {
      console.warn('[workspace] Backend API disabled, using empty state')
      evoRounds.value = []
      modelVersions.value = []
      healthReport.value = null
      metricsHistory.value = []
      isLoading.value = false
      return
    }

    try {
      const [versionsRes, healthRes, historyRes, roundsRes] =
        await Promise.allSettled([
          modelsApi.listVersions(id),
          modelsApi.getHealth(id),
          modelsApi.getHistory(id, 20),
          modelsApi.listRounds(id),
        ])

      modelVersions.value =
        versionsRes.status === 'fulfilled' ? versionsRes.value.versions : []
      healthReport.value =
        healthRes.status === 'fulfilled' ? healthRes.value : null
      metricsHistory.value =
        historyRes.status === 'fulfilled' ? historyRes.value.history : []
      evoRounds.value =
        roundsRes.status === 'fulfilled' ? roundsRes.value.rounds : []

      // Log any individual failures
      ;[versionsRes, healthRes, historyRes, roundsRes].forEach((result, i) => {
        if (result.status === 'rejected') {
          const names = ['versions', 'health', 'history', 'rounds']
          console.warn(
            `[workspace] Failed to load ${names[i]}:`,
            result.reason,
          )
        }
      })
    } catch (e) {
      console.warn('[workspace] Failed to load workspace data:', e)
      error.value = e instanceof Error ? e.message : String(e)
      evoRounds.value = []
      modelVersions.value = []
      healthReport.value = null
      metricsHistory.value = []
    } finally {
      isLoading.value = false
    }
  }

  /** Reload health report only. */
  async function refreshHealth() {
    if (!USE_BACKEND_API || !projectId.value) return

    try {
      healthReport.value = await modelsApi.getHealth(projectId.value)
    } catch (e) {
      console.warn('[workspace] Failed to refresh health:', e)
    }
  }

  /** Reload EvoLoop rounds only. */
  async function refreshRounds() {
    if (!USE_BACKEND_API || !projectId.value) return

    try {
      const res = await modelsApi.listRounds(projectId.value)
      evoRounds.value = res.rounds
    } catch (e) {
      console.warn('[workspace] Failed to refresh rounds:', e)
    }
  }

  /** Rollback to a specific model version. */
  async function rollbackModel(versionId: string) {
    if (!USE_BACKEND_API || !projectId.value) return

    try {
      await modelsApi.rollback(projectId.value, versionId)
      // Reload versions and health after rollback
      await Promise.allSettled([
        loadProjectWorkspace(projectId.value),
      ])
    } catch (e) {
      console.warn('[workspace] Failed to rollback model:', e)
      error.value = e instanceof Error ? e.message : String(e)
    }
  }

  /** Start polling: health every 10s, rounds every 30s. */
  function startPolling() {
    stopPolling()

    healthPollInterval = setInterval(() => {
      refreshHealth()
    }, 10_000)

    roundsPollInterval = setInterval(() => {
      refreshRounds()
    }, 30_000)
  }

  /** Stop all polling intervals. */
  function stopPolling() {
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
    // State
    projectId,
    evoRounds,
    modelVersions,
    healthReport,
    metricsHistory,
    isLoading,
    error,

    // Computed
    currentRound,
    bestVersion,
    activeVersion,
    overallHealth,

    // Actions
    loadProjectWorkspace,
    refreshHealth,
    refreshRounds,
    rollbackModel,
    startPolling,
    stopPolling,
  }
})
