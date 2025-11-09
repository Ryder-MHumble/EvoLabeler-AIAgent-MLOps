import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

// Import global styles
import '@/assets/styles/base.scss'

// Import locale messages - 固定使用中文
import zhCN from '@/locales/zh-CN.json'

/**
 * Application Initialization
 * 
 * Design Intent: Create a clean, modular initialization process.
 * All global configurations are centralized here for easy maintenance.
 */

// Add preload class to prevent transition flash on initial load
// This will be removed by useTheme composable after theme is applied
document.documentElement.classList.add('preload')

// Create Vue app instance
const app = createApp(App)

// Setup Pinia for state management
const pinia = createPinia()
app.use(pinia)

// Setup Vue Router
app.use(router)

// Setup i18n for internationalization - 固定使用中文
const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages: {
    'zh-CN': zhCN
  }
})
app.use(i18n)

// Setup Element Plus
app.use(ElementPlus)

// Mount the app
app.mount('#app')

