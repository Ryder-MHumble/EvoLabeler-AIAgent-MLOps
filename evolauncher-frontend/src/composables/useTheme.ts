import { ref, watch, onMounted } from 'vue'

/**
 * Theme Management Composable
 * 
 * Provides a reactive theme system with:
 * - Persistent theme preference (localStorage)
 * - System theme detection
 * - Smooth transitions between themes
 * - Auto-apply theme on mount
 * 
 * Design Intent: The theme toggle should feel instant and satisfying.
 * We add a brief 'preload' class removal to enable smooth CSS transitions
 * only after the initial theme is applied, preventing flash on page load.
 */

export type Theme = 'light' | 'dark' | 'auto'

const THEME_STORAGE_KEY = 'evolabeler-theme'

export function useTheme() {
  const currentTheme = ref<Theme>('auto')
  const isDark = ref(false)

  /**
   * Get system theme preference
   */
  const getSystemTheme = (): 'light' | 'dark' => {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark'
    }
    return 'light'
  }

  /**
   * Apply theme to DOM
   * Adds/removes 'dark' class on html element
   */
  const applyTheme = (theme: Theme) => {
    const root = document.documentElement
    
    let shouldBeDark = false
    
    if (theme === 'auto') {
      shouldBeDark = getSystemTheme() === 'dark'
    } else {
      shouldBeDark = theme === 'dark'
    }
    
    if (shouldBeDark) {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    
    isDark.value = shouldBeDark
  }

  /**
   * Set theme and persist to localStorage
   */
  const setTheme = (theme: Theme) => {
    currentTheme.value = theme
    localStorage.setItem(THEME_STORAGE_KEY, theme)
    applyTheme(theme)
  }

  /**
   * Toggle between light and dark
   * (Auto mode cycles through light -> dark -> light)
   */
  const toggleTheme = () => {
    if (currentTheme.value === 'light') {
      setTheme('dark')
    } else if (currentTheme.value === 'dark') {
      setTheme('light')
    } else {
      // If auto, switch to opposite of current system
      setTheme(isDark.value ? 'light' : 'dark')
    }
  }

  /**
   * Load saved theme or use auto
   */
  const loadTheme = () => {
    const saved = localStorage.getItem(THEME_STORAGE_KEY) as Theme | null
    const theme = saved || 'auto'
    currentTheme.value = theme
    applyTheme(theme)
  }

  // Watch for system theme changes when in auto mode
  onMounted(() => {
    // Load theme immediately to prevent flash
    loadTheme()
    
    // Remove preload class after a brief delay to enable smooth transitions
    // This prevents the transition animation from playing on initial page load
    setTimeout(() => {
      document.documentElement.classList.remove('preload')
    }, 100)

    // Listen for system theme changes
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      
      const handleChange = () => {
        if (currentTheme.value === 'auto') {
          applyTheme('auto')
        }
      }
      
      // Modern API
      if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', handleChange)
      } else {
        // Fallback for older browsers
        mediaQuery.addListener(handleChange)
      }
    }
  })

  // Watch theme changes
  watch(currentTheme, (newTheme) => {
    applyTheme(newTheme)
  })

  return {
    currentTheme,
    isDark,
    setTheme,
    toggleTheme
  }
}

