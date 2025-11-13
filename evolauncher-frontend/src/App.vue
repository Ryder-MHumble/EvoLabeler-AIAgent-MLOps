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
  position: relative;
  
  // 动态渐变背景
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(
      135deg,
      rgba(74, 105, 255, 0.03) 0%,
      rgba(138, 43, 226, 0.03) 50%,
      rgba(74, 105, 255, 0.03) 100%
    );
    background-size: 200% 200%;
    animation: gradientShift 15s ease infinite;
    z-index: 0;
    pointer-events: none;
  }
  
  .dark &::before {
    background: linear-gradient(
      135deg,
      rgba(96, 165, 250, 0.05) 0%,
      rgba(167, 139, 250, 0.05) 50%,
      rgba(96, 165, 250, 0.05) 100%
    );
    background-size: 200% 200%;
  }
  
  // 主题切换动画
  transition: background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes gradientShift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.app-main {
  flex: 1;
  overflow: hidden;
  position: relative;
  z-index: 1;
  background-color: transparent;
  
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

