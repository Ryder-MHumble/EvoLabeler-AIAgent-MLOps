export interface RetryOptions {
  retries?: number
  initialDelay?: number
  maxDelay?: number
  factor?: number
}

/**
 * Generic promise retry helper with exponential backoff.
 * Ensures network resilience to align with robustness requirements.
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  {
    retries = 3,
    initialDelay = 250,
    maxDelay = 2000,
    factor = 2
  }: RetryOptions = {}
): Promise<T> {
  let attempt = 0
  let delay = initialDelay
  let lastError: unknown

  while (attempt <= retries) {
    try {
      return await fn()
    } catch (error) {
      lastError = error
      if (attempt === retries) {
        break
      }

      await new Promise((resolve) => setTimeout(resolve, delay))
      delay = Math.min(delay * factor, maxDelay)
      attempt += 1
    }
  }

  throw lastError
}

