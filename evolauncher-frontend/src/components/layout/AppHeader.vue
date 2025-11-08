<script setup lang="ts">
/**
 * Custom Application Header / Title Bar
 * 
 * 设计理念（macOS风格）：
 * - 双层结构：顶部窗口控制条 + 下方应用标题栏
 * - 窗口控制条独立，避免遮挡logo和其他元素
 * - 完全响应式，小窗口时优雅降级
 * 
 * 布局结构：
 * ┌─────────────────────────────────────┐
 * │ ● ● ●          (控制条)              │ 22px
 * ├─────────────────────────────────────┤
 * │ ← Logo  Title    [功能按钮]         │ 48px
 * └─────────────────────────────────────┘
 */

import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import ThemeToggle from '@/components/common/ThemeToggle.vue'
import { useAppStore } from '@/store/app'
import type { ElectronAPI } from '@/types/electron'

const { locale, t } = useI18n()
const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const isMaximized = ref(false)
const electronAPI = ref<ElectronAPI | null>(null)
const isElectron = computed(() => electronAPI.value !== null)
let unsubscribeWindowState: (() => void) | null = null

// 是否显示返回按钮（非首页时显示）
const showBackButton = computed(() => {
  return route.path !== '/dashboard'
})

// 当前页面标题
const pageTitle = computed(() => {
  if (route.meta?.title) {
    return String(route.meta.title)
  }
  return ''
})

// Window control functions with error handling
const minimizeWindow = () => {
  try {
    electronAPI.value?.minimizeWindow()
  } catch (error) {
    console.error('Failed to minimize window:', error)
  }
}

const maximizeWindow = async () => {
  if (!electronAPI.value) return
  
  try {
    electronAPI.value.maximizeWindow()
    // Check maximized state after a brief delay
    setTimeout(async () => {
      if (electronAPI.value) {
        isMaximized.value = await electronAPI.value.isMaximized()
      }
    }, 100)
  } catch (error) {
    console.error('Failed to maximize window:', error)
  }
}

const closeWindow = () => {
  try {
    electronAPI.value?.closeWindow()
  } catch (error) {
    console.error('Failed to close window:', error)
  }
}

const changeLanguage = (lang: string) => {
  try {
    locale.value = lang
    appStore.setLocale(lang)
  } catch (error) {
    console.error('Failed to change language:', error)
  }
}

const goBack = () => {
  try {
    router.push('/dashboard')
  } catch (error) {
    console.error('Failed to navigate back:', error)
  }
}

const goHome = () => {
  try {
    if (route.path !== '/dashboard') {
      router.push('/dashboard')
    }
  } catch (error) {
    console.error('Failed to navigate home:', error)
  }
}

onMounted(async () => {
  // Check if running in Electron
  if (typeof window !== 'undefined' && window.electronAPI) {
    electronAPI.value = window.electronAPI
    try {
      isMaximized.value = await window.electronAPI.isMaximized()
      unsubscribeWindowState = electronAPI.value.onWindowStateChange?.((state) => {
        isMaximized.value = state.isMaximized
      })
    } catch (error) {
      console.error('Failed to initialize window state:', error)
    }
  }
})

onBeforeUnmount(() => {
  unsubscribeWindowState?.()
  unsubscribeWindowState = null
})
</script>

<template>
  <div class="app-header-container">
    <!-- macOS风格窗口控制条 -->
    <div v-if="isElectron" class="window-control-bar draggable">
      <div class="traffic-lights non-draggable">
        <button
          class="traffic-light close"
          @click="closeWindow"
          :aria-label="t('common.close')"
          :title="t('common.close')"
        >
          <Icon icon="ph:x" :width="10" />
        </button>
        
        <button
          class="traffic-light minimize"
          @click="minimizeWindow"
          :aria-label="t('common.minimize')"
          :title="t('common.minimize')"
        >
          <Icon icon="ph:minus" :width="10" />
        </button>
        
        <button
          class="traffic-light maximize"
          @click="maximizeWindow"
          :aria-label="t('common.maximize')"
          :title="t('common.maximize')"
        >
          <Icon
            :icon="isMaximized ? 'ph:arrows-in' : 'ph:arrows-out'"
            :width="10"
          />
        </button>
      </div>
    </div>

    <!-- 应用标题栏 -->
    <header class="app-header draggable">
      <!-- Left Section: Back Button + Logo -->
      <div class="header-left non-draggable">
        <!-- 返回按钮（仅非首页显示） -->
        <button
          v-if="showBackButton"
          class="back-button"
          @click="goBack"
          :aria-label="t('common.back')"
          :title="t('common.back')"
        >
          <Icon icon="ph:arrow-left" :width="20" />
        </button>
        
        <!-- Logo Section -->
        <button class="logo-section" @click="goHome" :title="t('app.name')">
          <Icon icon="ph:cube-fill" :width="24" class="logo-icon" />
          <span class="app-name">{{ t('app.name') }}</span>
        </button>
        
        <!-- 页面标题（小屏幕隐藏） -->
        <span v-if="pageTitle" class="page-title">{{ t(pageTitle) }}</span>
      </div>
      
      <!-- Center Section: 预留搜索栏位置 -->
      <div class="header-center">
        <!-- 可在此添加全局搜索功能 -->
      </div>
      
      <!-- Right Section: Controls -->
      <div class="header-right non-draggable">
        <!-- Language Selector -->
        <el-dropdown @command="changeLanguage" trigger="click">
          <button class="header-button" :aria-label="t('common.language')" :title="t('common.language')">
            <Icon icon="ph:translate" :width="20" />
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="en">
                <Icon icon="circle-flags:us" :width="16" class="mr-2" />
                English
              </el-dropdown-item>
              <el-dropdown-item command="zh-CN">
                <Icon icon="circle-flags:cn" :width="16" class="mr-2" />
                中文
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        
        <!-- Theme Toggle -->
        <ThemeToggle />
      </div>
    </header>
  </div>
</template>

<style scoped lang="scss">
// macOS风格窗口控制条
.window-control-bar {
  height: 22px;
  display: flex;
  align-items: center;
  padding: 0 $spacing-sm;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-light);
  position: relative;
  z-index: $z-sticky + 1;
  flex-shrink: 0;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

// macOS风格交通灯按钮
.traffic-lights {
  display: flex;
  gap: 8px;
  align-items: center;
}

.traffic-light {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all $transition-fast;
  position: relative;
  
  // 隐藏图标，悬停时显示
  svg {
    opacity: 0;
    transition: opacity $transition-fast;
  }
  
  &:hover svg {
    opacity: 1;
  }
  
  &:active {
    transform: scale(0.9);
  }
  
  // 关闭按钮（红色）
  &.close {
    background: #FF5F57;
    
    &:hover {
      background: #FF4D43;
      
      svg {
        color: rgba(0, 0, 0, 0.6);
      }
    }
  }
  
  // 最小化按钮（黄色）
  &.minimize {
    background: #FFBD2E;
    
    &:hover {
      background: #FFB01E;
      
      svg {
        color: rgba(0, 0, 0, 0.6);
      }
    }
  }
  
  // 最大化按钮（绿色）
  &.maximize {
    background: #28C840;
    
    &:hover {
      background: #1FB836;
      
      svg {
        color: rgba(0, 0, 0, 0.6);
      }
    }
  }
}

// 应用标题栏
.app-header {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 $spacing-md;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--color-border);
  position: relative;
  z-index: $z-sticky;
  flex-shrink: 0;
  transition: all 0.3s ease;
  
  // macOS风格：为窗口控制按钮预留空间，避免重叠
  padding-left: 80px;
  
  // 响应式设计
  @media (max-width: 768px) {
    padding-right: $spacing-sm;
  }
}

.header-left,
.header-center,
.header-right {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.header-left {
  flex: 0 0 auto;
  min-width: 0;
  // 确保不与窗口控制按钮重叠
  position: relative;
}

.header-center {
  flex: 1;
  justify-content: center;
  min-width: 0;
}

.header-right {
  flex: 0 0 auto;
  margin-left: auto;
}

// Back Button
.back-button {
  width: 36px;
  height: 36px;
  border-radius: $radius-md;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  transition: all $transition-base;
  flex-shrink: 0; // 防止被压缩
  
  &:hover {
    background: var(--color-surface-elevated);
    color: var(--color-primary);
    transform: translateX(-2px);
  }
  
  &:active {
    transform: translateX(-2px) scale(0.95);
  }
}

// Logo Section
.logo-section {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-xs $spacing-sm;
  border-radius: $radius-md;
  transition: all $transition-base;
  background: transparent;
  border: none;
  cursor: pointer;
  flex-shrink: 0; // 防止被压缩
  
  &:hover {
    background-color: var(--color-surface-elevated);
    
    .logo-icon {
      transform: rotate(10deg) scale(1.1);
    }
  }
  
  &:active {
    transform: scale(0.95);
  }
}

.logo-icon {
  color: var(--color-primary);
  transition: transform $transition-base;
}

.app-name {
  font-size: $font-size-base;
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
  letter-spacing: -0.01em;
  white-space: nowrap;
  transition: color 0.3s ease;
  
  // 小屏幕隐藏应用名称
  @media (max-width: 640px) {
    display: none;
  }
}

// Page Title
.page-title {
  font-size: $font-size-sm;
  color: var(--color-text-tertiary);
  margin-left: $spacing-sm;
  white-space: nowrap;
  transition: color 0.3s ease;
  
  // 小屏幕隐藏页面标题
  @media (max-width: 1024px) {
    display: none;
  }
}

// Header Buttons
.header-button {
  width: 40px;
  height: 40px;
  border-radius: $radius-md;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  transition: all $transition-base;
  flex-shrink: 0;
  
  &:hover {
    background: var(--color-surface-elevated);
    color: var(--color-text-primary);
    transform: scale(1.05);
  }
  
  &:active {
    transform: scale(0.95);
  }
}

// Utility classes
.mr-2 {
  margin-right: $spacing-xs;
}
</style>
