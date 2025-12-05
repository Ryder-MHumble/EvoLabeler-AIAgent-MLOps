/**
 * Projects API Client
 * 
 * This module provides type-safe API calls for project management.
 * Currently configured to use mock data, but ready to be connected
 * to the backend API once it's fully tested.
 * 
 * Usage:
 * ```typescript
 * import { projectsApi } from '@/api/projects'
 * 
 * // List projects
 * const projects = await projectsApi.list({ page: 1, pageSize: 20 })
 * 
 * // Get project details
 * const project = await projectsApi.get('proj_001')
 * 
 * // Create project
 * const newProject = await projectsApi.create({
 *   projectId: 'proj_new_001',
 *   name: 'My New Project',
 *   description: 'Project description'
 * })
 * ```
 */

import { withRetry } from '@/utils/retry'

// ============================================
// Type Definitions
// ============================================

/**
 * Project status enumeration
 */
export type ProjectStatus = 'idle' | 'training' | 'labeling' | 'completed'

/**
 * Project interface matching backend schema
 */
export interface Project {
  id: string                    // Internal UUID
  projectId: string             // Human-readable identifier
  name: string
  description?: string
  status: ProjectStatus
  imageCount: number
  accuracy?: number             // 0-100
  thumbnailUrl?: string
  metadata: Record<string, any>
  createdAt: string             // ISO 8601 timestamp
  updatedAt: string             // ISO 8601 timestamp
}

/**
 * Project creation request
 */
export interface ProjectCreateRequest {
  projectId: string
  name: string
  description?: string
  thumbnailUrl?: string
  metadata?: Record<string, any>
}

/**
 * Project update request
 */
export interface ProjectUpdateRequest {
  name?: string
  description?: string
  status?: ProjectStatus
  imageCount?: number
  accuracy?: number
  thumbnailUrl?: string
  metadata?: Record<string, any>
}

/**
 * Project list query parameters
 */
export interface ProjectListParams {
  page?: number
  pageSize?: number
  statusFilter?: ProjectStatus
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

/**
 * Project list response
 */
export interface ProjectListResponse {
  projects: Project[]
  total: number
  page: number
  pageSize: number
}

/**
 * Project statistics response
 */
export interface ProjectStats {
  totalProjects: number
  activeProjects: number
  completedProjects: number
  totalImages: number
  averageAccuracy?: number
}

// ============================================
// API Configuration
// ============================================

/**
 * Backend API base URL
 * TODO: Move to environment variables
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

/**
 * Enable/disable API calls
 * Set to true once backend is fully tested
 */
const USE_BACKEND_API = import.meta.env.VITE_USE_BACKEND_API === 'true' || false

// ============================================
// API Client Class
// ============================================

class ProjectsApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  /**
   * List projects with pagination and filtering
   */
  async list(params: ProjectListParams = {}): Promise<ProjectListResponse> {
    return withRetry<ProjectListResponse>(async () => {
      if (!USE_BACKEND_API) {
        throw new Error('Backend API not enabled. Using mock data instead.')
      }

      const queryParams = new URLSearchParams()
      if (params.page) queryParams.append('page', params.page.toString())
      if (params.pageSize) queryParams.append('page_size', params.pageSize.toString())
      if (params.statusFilter) queryParams.append('status_filter', params.statusFilter)
      if (params.sortBy) queryParams.append('sort_by', params.sortBy)
      if (params.sortOrder) queryParams.append('sort_order', params.sortOrder)

      const url = `${this.baseUrl}/projects?${queryParams.toString()}`
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`Failed to list projects: ${response.statusText}`)
      }

      const data = await response.json()
      
      // Transform snake_case to camelCase
      return {
        projects: data.projects.map(this.transformProject),
        total: data.total,
        page: data.page,
        pageSize: data.page_size,
      }
    })
  }

  /**
   * Get project by ID
   */
  async get(projectId: string): Promise<Project> {
    return withRetry<Project>(async () => {
      if (!USE_BACKEND_API) {
        throw new Error('Backend API not enabled. Using mock data instead.')
      }

      const url = `${this.baseUrl}/projects/${projectId}`
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Project not found: ${projectId}`)
        }
        throw new Error(`Failed to get project: ${response.statusText}`)
      }

      const data = await response.json()
      return this.transformProject(data)
    })
  }

  /**
   * Create a new project
   */
  async create(request: ProjectCreateRequest): Promise<Project> {
    return withRetry<Project>(async () => {
      if (!USE_BACKEND_API) {
        throw new Error('Backend API not enabled. Using mock data instead.')
      }

      const url = `${this.baseUrl}/projects`
      
      // Transform camelCase to snake_case for backend
      const payload = {
        project_id: request.projectId,
        name: request.name,
        description: request.description,
        thumbnail_url: request.thumbnailUrl,
        metadata: request.metadata || {},
      }

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        if (response.status === 409) {
          throw new Error(`Project ID already exists: ${request.projectId}`)
        }
        throw new Error(`Failed to create project: ${response.statusText}`)
      }

      const data = await response.json()
      return this.transformProject(data)
    })
  }

  /**
   * Update an existing project
   */
  async update(projectId: string, request: ProjectUpdateRequest): Promise<Project> {
    return withRetry<Project>(async () => {
      if (!USE_BACKEND_API) {
        throw new Error('Backend API not enabled. Using mock data instead.')
      }

      const url = `${this.baseUrl}/projects/${projectId}`
      
      // Transform camelCase to snake_case for backend
      const payload: Record<string, any> = {}
      if (request.name !== undefined) payload.name = request.name
      if (request.description !== undefined) payload.description = request.description
      if (request.status !== undefined) payload.status = request.status
      if (request.imageCount !== undefined) payload.image_count = request.imageCount
      if (request.accuracy !== undefined) payload.accuracy = request.accuracy
      if (request.thumbnailUrl !== undefined) payload.thumbnail_url = request.thumbnailUrl
      if (request.metadata !== undefined) payload.metadata = request.metadata

      const response = await fetch(url, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Project not found: ${projectId}`)
        }
        throw new Error(`Failed to update project: ${response.statusText}`)
      }

      const data = await response.json()
      return this.transformProject(data)
    })
  }

  /**
   * Delete a project
   */
  async delete(projectId: string): Promise<void> {
    return withRetry<void>(async () => {
      if (!USE_BACKEND_API) {
        throw new Error('Backend API not enabled. Using mock data instead.')
      }

      const url = `${this.baseUrl}/projects/${projectId}`
      const response = await fetch(url, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Project not found: ${projectId}`)
        }
        throw new Error(`Failed to delete project: ${response.statusText}`)
      }
    })
  }

  /**
   * Get project statistics
   */
  async getStats(): Promise<ProjectStats> {
    return withRetry<ProjectStats>(async () => {
      if (!USE_BACKEND_API) {
        throw new Error('Backend API not enabled. Using mock data instead.')
      }

      const url = `${this.baseUrl}/projects/stats/summary`
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`Failed to get project stats: ${response.statusText}`)
      }

      const data = await response.json()
      
      // Transform snake_case to camelCase
      return {
        totalProjects: data.total_projects,
        activeProjects: data.active_projects,
        completedProjects: data.completed_projects,
        totalImages: data.total_images,
        averageAccuracy: data.average_accuracy,
      }
    })
  }

  /**
   * Transform backend project response to frontend format
   * Converts snake_case to camelCase
   */
  private transformProject(data: any): Project {
    return {
      id: data.id,
      projectId: data.project_id,
      name: data.name,
      description: data.description,
      status: data.status,
      imageCount: data.image_count,
      accuracy: data.accuracy,
      thumbnailUrl: data.thumbnail_url,
      metadata: data.metadata || {},
      createdAt: data.created_at,
      updatedAt: data.updated_at,
    }
  }
}

// ============================================
// Export singleton instance
// ============================================

/**
 * Projects API client singleton
 * 
 * Use this instance for all project-related API calls
 */
export const projectsApi = new ProjectsApiClient(API_BASE_URL)

/**
 * Export for testing
 */
export { ProjectsApiClient }


