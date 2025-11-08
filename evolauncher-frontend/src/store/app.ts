import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * Global Application State Store
 * 
 * Manages app-wide state like theme, language, sidebar state, etc.
 * This store is separate from domain-specific stores (projects, jobs, etc.)
 */

export const useAppStore = defineStore('app', () => {
  // Sidebar state
  const sidebarCollapsed = ref(false)
  const sidebarWidth = ref(240)

  // Language
  const locale = ref('en')

  // Loading states
  const isLoading = ref(false)

  // Notifications
  const notifications = ref<Array<{
    id: string
    type: 'success' | 'error' | 'warning' | 'info'
    message: string
    timestamp: number
  }>>([])

  // Actions
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
    sidebarWidth.value = sidebarCollapsed.value ? 64 : 240
  }

  const setSidebarCollapsed = (collapsed: boolean) => {
    sidebarCollapsed.value = collapsed
    sidebarWidth.value = collapsed ? 64 : 240
  }

  const setLocale = (newLocale: string) => {
    locale.value = newLocale
    localStorage.setItem('evolabeler-locale', newLocale)
  }

  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  const addNotification = (
    type: 'success' | 'error' | 'warning' | 'info',
    message: string
  ) => {
    const id = `notif-${Date.now()}-${Math.random()}`
    notifications.value.push({
      id,
      type,
      message,
      timestamp: Date.now()
    })

    // Auto-remove after 5 seconds
    setTimeout(() => {
      removeNotification(id)
    }, 5000)
  }

  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  return {
    // State
    sidebarCollapsed,
    sidebarWidth,
    locale,
    isLoading,
    notifications,
    
    // Actions
    toggleSidebar,
    setSidebarCollapsed,
    setLocale,
    setLoading,
    addNotification,
    removeNotification
  }
})

