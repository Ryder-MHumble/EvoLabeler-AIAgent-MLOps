/**
 * WebSocket Client Utility
 *
 * Pre-built WebSocket client for real-time communication with the backend.
 * Supports auto-reconnect with exponential backoff and heartbeat ping.
 *
 * NOTE: Backend WebSocket endpoints do not exist yet. This client is built
 * ahead of time so it can be integrated once the server-side WS layer is ready.
 *
 * Usage:
 * ```typescript
 * import { createWebSocket } from '@/api/websocket'
 *
 * const ws = createWebSocket('training-progress')
 * ws.onMessage((data) => console.log('Received:', data))
 * ws.onError((err) => console.error('WS error:', err))
 * ws.connect()
 *
 * // Later...
 * ws.disconnect()
 * ```
 */

import { WS_BASE_URL } from '@/api/client'

// ============================================
// Types
// ============================================

export type MessageHandler = (data: unknown) => void
export type ErrorHandler = (event: Event) => void
export type CloseHandler = (event: CloseEvent) => void

// ============================================
// WebSocket Client
// ============================================

/**
 * Managed WebSocket connection with auto-reconnect and heartbeat.
 */
export class EvoWebSocket {
  private baseUrl: string
  private channel: string
  private socket: WebSocket | null = null

  // Reconnection state
  private reconnectAttempts = 0
  private readonly maxReconnectRetries = 5
  private readonly initialReconnectDelay = 1000 // 1 second
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null

  // Heartbeat state
  private readonly heartbeatInterval = 30_000 // 30 seconds
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null

  // Callbacks
  private messageHandlers: MessageHandler[] = []
  private errorHandlers: ErrorHandler[] = []
  private closeHandlers: CloseHandler[] = []

  // Intentional disconnect flag (to suppress auto-reconnect)
  private intentionalDisconnect = false

  constructor(baseUrl: string, channel: string) {
    this.baseUrl = baseUrl
    this.channel = channel
  }

  /**
   * Open the WebSocket connection to the configured channel.
   * If already connected, this is a no-op.
   */
  connect(): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      return
    }

    this.intentionalDisconnect = false
    this.reconnectAttempts = 0

    this.createConnection()
  }

  /**
   * Gracefully close the WebSocket connection.
   * Stops heartbeat, clears reconnect timer, and closes the socket.
   */
  disconnect(): void {
    this.intentionalDisconnect = true
    this.cleanup()

    if (this.socket) {
      this.socket.close(1000, 'Client disconnected')
      this.socket = null
    }
  }

  /**
   * Register a handler for incoming messages.
   * The handler receives the parsed JSON payload.
   */
  onMessage(handler: MessageHandler): void {
    this.messageHandlers.push(handler)
  }

  /**
   * Register a handler for connection errors.
   */
  onError(handler: ErrorHandler): void {
    this.errorHandlers.push(handler)
  }

  /**
   * Register a handler for connection close events.
   */
  onClose(handler: CloseHandler): void {
    this.closeHandlers.push(handler)
  }

  /**
   * Whether the socket is currently open.
   */
  get isConnected(): boolean {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN
  }

  // ============================================
  // Private Methods
  // ============================================

  private createConnection(): void {
    const url = `${this.baseUrl}/${this.channel}`

    try {
      this.socket = new WebSocket(url)
    } catch (err) {
      console.error(`[EvoWebSocket] Failed to create WebSocket for channel "${this.channel}":`, err)
      this.scheduleReconnect()
      return
    }

    this.socket.onopen = () => {
      console.info(`[EvoWebSocket] Connected to channel "${this.channel}"`)
      this.reconnectAttempts = 0
      this.startHeartbeat()
    }

    this.socket.onmessage = (event: MessageEvent) => {
      let data: unknown
      try {
        data = JSON.parse(event.data)
      } catch {
        data = event.data
      }

      for (const handler of this.messageHandlers) {
        try {
          handler(data)
        } catch (err) {
          console.error('[EvoWebSocket] Message handler error:', err)
        }
      }
    }

    this.socket.onerror = (event: Event) => {
      console.error(`[EvoWebSocket] Error on channel "${this.channel}"`, event)
      for (const handler of this.errorHandlers) {
        try {
          handler(event)
        } catch (err) {
          console.error('[EvoWebSocket] Error handler error:', err)
        }
      }
    }

    this.socket.onclose = (event: CloseEvent) => {
      console.info(
        `[EvoWebSocket] Connection closed for channel "${this.channel}" (code=${event.code})`,
      )

      this.stopHeartbeat()

      for (const handler of this.closeHandlers) {
        try {
          handler(event)
        } catch (err) {
          console.error('[EvoWebSocket] Close handler error:', err)
        }
      }

      if (!this.intentionalDisconnect) {
        this.scheduleReconnect()
      }
    }
  }

  /**
   * Schedule an auto-reconnect attempt with exponential backoff.
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectRetries) {
      console.warn(
        `[EvoWebSocket] Max reconnect retries (${this.maxReconnectRetries}) reached for channel "${this.channel}". Giving up.`,
      )
      return
    }

    const delay = this.initialReconnectDelay * Math.pow(2, this.reconnectAttempts)
    this.reconnectAttempts++

    console.info(
      `[EvoWebSocket] Reconnecting to "${this.channel}" in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectRetries})`,
    )

    this.reconnectTimer = setTimeout(() => {
      this.createConnection()
    }, delay)
  }

  /**
   * Start sending heartbeat pings at a fixed interval.
   */
  private startHeartbeat(): void {
    this.stopHeartbeat()

    this.heartbeatTimer = setInterval(() => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        try {
          this.socket.send(JSON.stringify({ type: 'ping' }))
        } catch {
          // Socket may have closed between check and send; reconnect will handle it.
        }
      }
    }, this.heartbeatInterval)
  }

  /**
   * Stop the heartbeat timer.
   */
  private stopHeartbeat(): void {
    if (this.heartbeatTimer !== null) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  /**
   * Clean up all timers.
   */
  private cleanup(): void {
    this.stopHeartbeat()

    if (this.reconnectTimer !== null) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }
}

// ============================================
// Factory Function
// ============================================

/**
 * Create a new EvoWebSocket instance for the given channel.
 *
 * @param channel - WebSocket channel name (appended to the WS base URL)
 * @returns A new EvoWebSocket instance (not yet connected -- call `.connect()`)
 */
export function createWebSocket(channel: string): EvoWebSocket {
  return new EvoWebSocket(WS_BASE_URL, channel)
}
