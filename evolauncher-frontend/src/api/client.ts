/**
 * Shared API Client Utilities
 *
 * Provides common configuration and helper functions used by all API modules.
 * Centralizes base URL management, request handling, and case transformation
 * so individual API clients stay focused on endpoint-specific logic.
 *
 * Usage:
 * ```typescript
 * import { apiRequest, API_BASE_URL, USE_BACKEND_API, snakeToCamel, camelToSnake } from '@/api/client'
 *
 * const data = await apiRequest<MyResponse>('/projects', { method: 'GET' })
 * const camelData = snakeToCamel(snakeCaseObj)
 * ```
 */

// ============================================
// Configuration Constants
// ============================================

/**
 * Backend API base URL.
 * Defaults to local development server if not set.
 */
export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

/**
 * Feature flag to enable/disable real backend API calls.
 * When false, API clients should fall back to mock data.
 */
export const USE_BACKEND_API: boolean =
  import.meta.env.VITE_USE_BACKEND_API === 'true'

/**
 * WebSocket base URL.
 * Defaults to local development server if not set.
 */
export const WS_BASE_URL: string =
  import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/api/v1/ws'

// ============================================
// Generic API Request Function
// ============================================

/**
 * Options for apiRequest, extending standard RequestInit.
 */
export interface ApiRequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown
}

/**
 * Generic API request function.
 *
 * Prepends the base URL, sets JSON headers, validates the response,
 * and returns parsed JSON of the expected type.
 *
 * @param path - API path relative to the base URL (e.g. '/projects')
 * @param options - Fetch options. `body` will be JSON-serialized automatically.
 * @returns Parsed JSON response
 * @throws Error if the response is not ok
 */
export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const { body, headers, ...rest } = options

  const url = `${API_BASE_URL}${path}`

  const response = await fetch(url, {
    ...rest,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (!response.ok) {
    const errorText = await response.text().catch(() => response.statusText)
    throw new Error(
      `API request failed [${response.status}]: ${errorText}`,
    )
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as unknown as T
  }

  return response.json() as Promise<T>
}

// ============================================
// Case Transformation Utilities
// ============================================

/**
 * Convert a single snake_case string to camelCase.
 */
function snakeToCamelKey(key: string): string {
  return key.replace(/_([a-z0-9])/g, (_, char) => char.toUpperCase())
}

/**
 * Convert a single camelCase string to snake_case.
 */
function camelToSnakeKey(key: string): string {
  return key.replace(/[A-Z]/g, (char) => `_${char.toLowerCase()}`)
}

/**
 * Deeply transform all object keys from snake_case to camelCase.
 *
 * Handles nested objects, arrays, null, and primitives.
 * Leaves non-plain-object values (Date, etc.) untouched.
 */
export function snakeToCamel<T = unknown>(obj: unknown): T {
  if (obj === null || obj === undefined) {
    return obj as unknown as T
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => snakeToCamel(item)) as unknown as T
  }

  if (typeof obj === 'object' && obj.constructor === Object) {
    const result: Record<string, unknown> = {}
    for (const [key, value] of Object.entries(obj)) {
      result[snakeToCamelKey(key)] = snakeToCamel(value)
    }
    return result as unknown as T
  }

  return obj as unknown as T
}

/**
 * Deeply transform all object keys from camelCase to snake_case.
 *
 * Handles nested objects, arrays, null, and primitives.
 * Leaves non-plain-object values (Date, etc.) untouched.
 */
export function camelToSnake<T = unknown>(obj: unknown): T {
  if (obj === null || obj === undefined) {
    return obj as unknown as T
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => camelToSnake(item)) as unknown as T
  }

  if (typeof obj === 'object' && obj.constructor === Object) {
    const result: Record<string, unknown> = {}
    for (const [key, value] of Object.entries(obj)) {
      result[camelToSnakeKey(key)] = camelToSnake(value)
    }
    return result as unknown as T
  }

  return obj as unknown as T
}
