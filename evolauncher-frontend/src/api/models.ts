/**
 * Models API Client
 *
 * Provides type-safe API calls for model version management, health monitoring,
 * metrics history, rollback operations, and EvoLoop round inspection.
 *
 * Usage:
 * ```typescript
 * import { modelsApi } from '@/api/models'
 *
 * const versions = await modelsApi.listVersions('proj_001')
 * const health = await modelsApi.getHealth('proj_001')
 * const history = await modelsApi.getHistory('proj_001', 20)
 * await modelsApi.rollback('proj_001', 'version_abc')
 * const rounds = await modelsApi.listRounds('proj_001')
 * ```
 */

import { withRetry } from '@/utils/retry'
import { API_BASE_URL, USE_BACKEND_API, snakeToCamel } from '@/api/client'

// ============================================
// Type Definitions
// ============================================

/**
 * Training/evaluation metrics for a model version.
 */
export interface ModelMetrics {
  mAP50?: number
  mAP5095?: number
  precision?: number
  recall?: number
  valLoss?: number
  trainLoss?: number
}

/**
 * A single model version record.
 */
export interface ModelVersion {
  id: string
  projectId: string
  version: string
  roundNumber: number
  modelPath: string
  metrics: ModelMetrics
  calibrationEce?: number
  isBest: boolean
  isActive: boolean
  createdAt: string
}

/**
 * Response for listing model versions.
 */
export interface ModelVersionsResponse {
  projectId: string
  versions: ModelVersion[]
  total: number
}

/**
 * A single health check result.
 */
export interface HealthCheck {
  name: string
  passed: boolean
  severity: string
  message: string
}

/**
 * Aggregated health report for a project's active model.
 */
export interface HealthReport {
  overallStatus: string
  checks: HealthCheck[]
  recommendation: string
}

/**
 * Response for model health endpoint.
 */
export interface ModelHealthResponse {
  projectId: string
  activeVersion?: string
  bestVersion?: string
  healthReport: HealthReport
}

/**
 * A single metrics history entry (used for charting trends).
 */
export interface MetricsHistoryEntry {
  version: string
  roundNumber: number
  mAP50?: number
  mAP5095?: number
  precision?: number
  recall?: number
  valLoss?: number
  trainLoss?: number
  calibrationEce?: number
  isBest: boolean
  createdAt: string
}

/**
 * Response for metrics history endpoint.
 */
export interface MetricsHistoryResponse {
  projectId: string
  history: MetricsHistoryEntry[]
  total: number
}

/**
 * Rollback operation response.
 */
export interface RollbackResponse {
  message: string
  projectId: string
  success: boolean
  [key: string]: unknown
}

/**
 * A single EvoLoop round record.
 */
export interface EvoRound {
  id: string
  roundNumber: number
  status: string
  inputImageCount: number
  outputImageCount: number
  metricsBefore?: ModelMetrics
  metricsAfter?: ModelMetrics
  metricsDelta?: ModelMetrics
  shouldContinue: boolean
  continueReason?: string
  dataQualityGatePassed: boolean
  modelHealthReport?: Record<string, unknown>
  wasRolledBack: boolean
  createdAt: string
}

/**
 * Response for listing EvoLoop rounds.
 */
export interface EvoRoundsResponse {
  projectId: string
  rounds: EvoRound[]
  total: number
}

// ============================================
// API Client Class
// ============================================

class ModelsApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  /**
   * List all model versions for a project with their metrics.
   */
  async listVersions(projectId: string): Promise<ModelVersionsResponse> {
    return withRetry<ModelVersionsResponse>(async () => {
      if (!USE_BACKEND_API) {
        throw new Error('Backend API not enabled. Using mock data instead.')
      }

      const url = `${this.baseUrl}/models/${projectId}/versions`
      const response = await fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      })

      if (!response.ok) {
        throw new Error(`Failed to list model versions: ${response.statusText}`)
      }

      const data = await response.json()
      return {
        projectId: data.project_id,
        versions: (data.versions || []).map((v: Record<string, unknown>) =>
          this.transformModelVersion(v),
        ),
        total: data.total,
      }
    })
  }

  /**
   * Get comprehensive model health report for a project.
   */
  async getHealth(projectId: string): Promise<ModelHealthResponse> {
    return withRetry<ModelHealthResponse>(async () => {
      if (!USE_BACKEND_API) {
        throw new Error('Backend API not enabled. Using mock data instead.')
      }

      const url = `${this.baseUrl}/models/${projectId}/health`
      const response = await fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      })

      if (!response.ok) {
        throw new Error(`Failed to get model health: ${response.statusText}`)
      }

      const data = await response.json()
      return {
        projectId: data.project_id,
        activeVersion: data.active_version,
        bestVersion: data.best_version,
        healthReport: snakeToCamel<HealthReport>(data.health_report),
      }
    })
  }

  /**
   * Get metrics history over time for charting trends.
   *
   * @param projectId - Project identifier
   * @param limit - Maximum number of entries (1-100, default 20)
   */
  async getHistory(
    projectId: string,
    limit?: number,
  ): Promise<MetricsHistoryResponse> {
    return withRetry<MetricsHistoryResponse>(async () => {
      if (!USE_BACKEND_API) {
        throw new Error('Backend API not enabled. Using mock data instead.')
      }

      const queryParams = new URLSearchParams()
      if (limit !== undefined) queryParams.append('limit', limit.toString())

      const qs = queryParams.toString()
      const url = `${this.baseUrl}/models/${projectId}/history${qs ? `?${qs}` : ''}`

      const response = await fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      })

      if (!response.ok) {
        throw new Error(`Failed to get metrics history: ${response.statusText}`)
      }

      const data = await response.json()
      return {
        projectId: data.project_id,
        history: (data.history || []).map((entry: Record<string, unknown>) =>
          this.transformHistoryEntry(entry),
        ),
        total: data.total,
      }
    })
  }

  /**
   * Manually rollback to a specific model version.
   */
  async rollback(
    projectId: string,
    versionId: string,
  ): Promise<RollbackResponse> {
    return withRetry<RollbackResponse>(async () => {
      if (!USE_BACKEND_API) {
        throw new Error('Backend API not enabled. Using mock data instead.')
      }

      const url = `${this.baseUrl}/models/${projectId}/rollback/${versionId}`
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })

      if (!response.ok) {
        const errorText = await response.text().catch(() => response.statusText)
        throw new Error(`Failed to rollback model: ${errorText}`)
      }

      const data = await response.json()
      return snakeToCamel<RollbackResponse>(data)
    })
  }

  /**
   * List EvoLoop rounds for a project, optionally filtered by job ID.
   */
  async listRounds(
    projectId: string,
    jobId?: string,
  ): Promise<EvoRoundsResponse> {
    return withRetry<EvoRoundsResponse>(async () => {
      if (!USE_BACKEND_API) {
        throw new Error('Backend API not enabled. Using mock data instead.')
      }

      const queryParams = new URLSearchParams()
      if (jobId) queryParams.append('job_id', jobId)

      const qs = queryParams.toString()
      const url = `${this.baseUrl}/models/${projectId}/rounds${qs ? `?${qs}` : ''}`

      const response = await fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      })

      if (!response.ok) {
        throw new Error(`Failed to list EvoLoop rounds: ${response.statusText}`)
      }

      const data = await response.json()
      return {
        projectId: data.project_id,
        rounds: (data.rounds || []).map((r: Record<string, unknown>) =>
          snakeToCamel<EvoRound>(r),
        ),
        total: data.total,
      }
    })
  }

  // ============================================
  // Private Helpers
  // ============================================

  /**
   * Transform a backend model version record to the frontend interface.
   */
  private transformModelVersion(data: Record<string, unknown>): ModelVersion {
    const raw = snakeToCamel<Record<string, unknown>>(data)
    // Metrics is a nested object that also needs key transformation
    return {
      ...raw,
      metrics: snakeToCamel<ModelMetrics>(data.metrics as Record<string, unknown> || {}),
    } as ModelVersion
  }

  /**
   * Transform a backend metrics history entry to the frontend interface.
   */
  private transformHistoryEntry(data: Record<string, unknown>): MetricsHistoryEntry {
    return snakeToCamel<MetricsHistoryEntry>(data)
  }
}

// ============================================
// Export singleton instance
// ============================================

/**
 * Models API client singleton.
 * Use this instance for all model-related API calls.
 */
export const modelsApi = new ModelsApiClient(API_BASE_URL)

/**
 * Export for testing.
 */
export { ModelsApiClient }
