/**
 * Annotations API Client
 *
 * Provides type-safe API calls for annotation management (CRUD operations
 * on bounding-box annotations attached to project images).
 *
 * Usage:
 * ```typescript
 * import { annotationsApi } from '@/api/annotations'
 *
 * // Create annotation
 * const annotation = await annotationsApi.create({
 *   projectId: 'proj_001',
 *   imageId: 'img_001',
 *   bboxes: [{ x: 0.1, y: 0.2, width: 0.3, height: 0.4, label: 'cat' }],
 * })
 *
 * // List annotations for a project image
 * const list = await annotationsApi.listByProject('proj_001', 'img_001')
 * ```
 */

import { withRetry } from '@/utils/retry'
import { API_BASE_URL, USE_BACKEND_API, snakeToCamel, camelToSnake } from '@/api/client'

// ============================================
// Type Definitions
// ============================================

/**
 * Bounding box within an annotation.
 * All coordinates are normalized to 0-1 range.
 */
export interface BBox {
  x: number
  y: number
  width: number
  height: number
  label: string
  confidence?: number
}

/**
 * Request payload for creating a new annotation.
 */
export interface AnnotationCreateRequest {
  projectId: string
  imageId: string
  bboxes: BBox[]
  metadata?: Record<string, unknown>
}

/**
 * Request payload for updating an existing annotation.
 */
export interface AnnotationUpdateRequest {
  bboxes?: BBox[]
  metadata?: Record<string, unknown>
}

/**
 * Annotation response from the backend.
 */
export interface Annotation {
  id: string
  projectId: string
  imageId: string
  userId?: string
  bboxes: BBox[]
  metadata: Record<string, unknown>
  createdAt: string
  updatedAt: string
}

/**
 * Annotation list response.
 */
export interface AnnotationListResponse {
  annotations: Annotation[]
  total: number
}

// ============================================
// API Client Class
// ============================================

class AnnotationsApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  /**
   * Create a new annotation.
   */
  async create(request: AnnotationCreateRequest): Promise<Annotation> {
    return withRetry<Annotation>(async () => {
      if (!USE_BACKEND_API) {
        throw new Error('Backend API not enabled. Using mock data instead.')
      }

      const url = `${this.baseUrl}/annotations`

      const payload = camelToSnake(request)

      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error(`Failed to create annotation: ${response.statusText}`)
      }

      const data = await response.json()
      return this.transformAnnotation(data)
    })
  }

  /**
   * List annotations for a project, optionally filtered by image ID.
   */
  async listByProject(
    projectId: string,
    imageId?: string,
  ): Promise<AnnotationListResponse> {
    return withRetry<AnnotationListResponse>(async () => {
      if (!USE_BACKEND_API) {
        throw new Error('Backend API not enabled. Using mock data instead.')
      }

      const queryParams = new URLSearchParams()
      if (imageId) queryParams.append('image_id', imageId)

      const qs = queryParams.toString()
      const url = `${this.baseUrl}/annotations/project/${projectId}${qs ? `?${qs}` : ''}`

      const response = await fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      })

      if (!response.ok) {
        throw new Error(`Failed to list annotations: ${response.statusText}`)
      }

      const data = await response.json()

      return {
        annotations: (data.annotations || []).map(this.transformAnnotation),
        total: data.total,
      }
    })
  }

  /**
   * Get a single annotation by its ID.
   */
  async get(annotationId: string): Promise<Annotation> {
    return withRetry<Annotation>(async () => {
      if (!USE_BACKEND_API) {
        throw new Error('Backend API not enabled. Using mock data instead.')
      }

      const url = `${this.baseUrl}/annotations/${annotationId}`
      const response = await fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      })

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Annotation not found: ${annotationId}`)
        }
        throw new Error(`Failed to get annotation: ${response.statusText}`)
      }

      const data = await response.json()
      return this.transformAnnotation(data)
    })
  }

  /**
   * Update an existing annotation.
   */
  async update(
    annotationId: string,
    request: AnnotationUpdateRequest,
  ): Promise<Annotation> {
    return withRetry<Annotation>(async () => {
      if (!USE_BACKEND_API) {
        throw new Error('Backend API not enabled. Using mock data instead.')
      }

      const url = `${this.baseUrl}/annotations/${annotationId}`

      const payload = camelToSnake(request)

      const response = await fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Annotation not found: ${annotationId}`)
        }
        throw new Error(`Failed to update annotation: ${response.statusText}`)
      }

      const data = await response.json()
      return this.transformAnnotation(data)
    })
  }

  /**
   * Delete an annotation by its ID.
   */
  async delete(annotationId: string): Promise<void> {
    return withRetry<void>(async () => {
      if (!USE_BACKEND_API) {
        throw new Error('Backend API not enabled. Using mock data instead.')
      }

      const url = `${this.baseUrl}/annotations/${annotationId}`
      const response = await fetch(url, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
      })

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Annotation not found: ${annotationId}`)
        }
        throw new Error(`Failed to delete annotation: ${response.statusText}`)
      }
    })
  }

  /**
   * Transform backend annotation response to frontend format.
   * Converts snake_case keys to camelCase.
   */
  private transformAnnotation(data: Record<string, unknown>): Annotation {
    return snakeToCamel<Annotation>(data)
  }
}

// ============================================
// Export singleton instance
// ============================================

/**
 * Annotations API client singleton.
 * Use this instance for all annotation-related API calls.
 */
export const annotationsApi = new AnnotationsApiClient(API_BASE_URL)

/**
 * Export for testing.
 */
export { AnnotationsApiClient }
