<script setup lang="ts">
/**
 * Root Application Component
 * 
 * Design Philosophy:
 * - 移除侧边栏，以项目为中心的交互模式
 * - 简洁的布局：仅标题栏 + 全宽内容区
 * - 用户从项目列表进入具体项目工作区
 * 
 * The layout uses a flex-based structure to ensure proper sizing
 * and prevent scrollbar issues in the frameless Electron window.
 */

import { onMounted } from 'vue'
import { useAppStore } from '@/store/app'
import { useTheme } from '@/composables/useTheme'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppErrorBoundary from '@/components/layout/AppErrorBoundary.vue'

const appStore = useAppStore()
const { currentTheme } = useTheme()

onMounted(() => {
  console.log('EvoLabeler app mounted', { theme: currentTheme.value })
})
</script>

<template>
  <div class="app-container">
    <!-- Custom Title Bar -->
    <AppHeader />
    
    <!-- Main Content Area (Full Width) -->
    <main class="app-main">
      <AppErrorBoundary>
        <router-view v-slot="{ Component, route }">
          <transition
            name="page"
            mode="out-in"
            appear
          >
            <component :is="Component" :key="route.path" />
          </transition>
        </router-view>
      </AppErrorBoundary>
    </main>
  </div>
</template>

<style scoped lang="scss">
.app-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--color-bg);
  
  // 主题切换动画
  transition: background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.app-main {
  flex: 1;
  overflow: hidden;
  position: relative;
  background-color: var(--color-bg);
  
  // 主题切换动画
  transition: background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

// Page transition styles
.page-enter-active,
.page-leave-active {
  transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>

