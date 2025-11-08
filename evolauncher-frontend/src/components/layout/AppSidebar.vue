<script setup lang="ts">
/**
 * Application Sidebar Navigation
 * 
 * Design Philosophy:
 * - Clean, minimal navigation with clear active states
 * - Smooth expand/collapse animation
 * - Icon-first design for collapsed state
 * - Clear visual feedback on hover and active states
 * 
 * UX Features:
 * - Active route highlighting
 * - Tooltip support when collapsed
 * - Keyboard navigation support
 */

import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import { useAppStore } from '@/store/app'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const { t } = useI18n()

interface NavItem {
  name: string
  path: string
  icon: string
  label: string
}

const navItems = computed<NavItem[]>(() => [
  {
    name: 'Dashboard',
    path: '/dashboard',
    icon: 'ph:squares-four-fill',
    label: t('nav.dashboard')
  },
  {
    name: 'Workspace',
    path: '/workspace',
    icon: 'ph:desktop-fill',
    label: t('nav.workspace')
  }
])

const isActive = (path: string) => {
  return route.path === path
}

const navigateTo = (path: string) => {
  router.push(path)
}

const toggleSidebar = () => {
  appStore.toggleSidebar()
}
</script>

<template>
  <aside
    class="app-sidebar"
    :class="{ collapsed: appStore.sidebarCollapsed }"
    :style="{ width: `${appStore.sidebarWidth}px` }"
  >
    <!-- Sidebar Header with Toggle -->
    <div class="sidebar-header">
      <button
        class="toggle-button non-draggable"
        @click="toggleSidebar"
        :aria-label="appStore.sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      >
        <Icon
          :icon="appStore.sidebarCollapsed ? 'ph:caret-right' : 'ph:caret-left'"
          :width="20"
        />
      </button>
    </div>
    
    <!-- Navigation Items -->
    <nav class="sidebar-nav">
      <button
        v-for="item in navItems"
        :key="item.path"
        class="nav-item non-draggable"
        :class="{ active: isActive(item.path) }"
        @click="navigateTo(item.path)"
        :aria-label="item.label"
      >
        <Icon :icon="item.icon" :width="24" class="nav-icon" />
        <transition name="label-fade">
          <span v-if="!appStore.sidebarCollapsed" class="nav-label">
            {{ item.label }}
          </span>
        </transition>
      </button>
    </nav>
  </aside>
</template>

<style scoped lang="scss">
.app-sidebar {
  height: 100%;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
  flex-shrink: 0;
  overflow: hidden;
  position: relative;
  z-index: $z-fixed;
}

// Sidebar Header
.sidebar-header {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: $spacing-sm $spacing-md;
  border-bottom: 1px solid var(--color-border);
}

.toggle-button {
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
  
  &:hover {
    background: var(--color-surface-elevated);
    color: var(--color-text-primary);
    transform: scale(1.05);
  }
  
  &:active {
    transform: scale(0.95);
  }
}

// Navigation
.sidebar-nav {
  flex: 1;
  padding: $spacing-md $spacing-sm;
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
  overflow-y: auto;
  @include custom-scrollbar;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  padding: $spacing-md;
  border-radius: $radius-lg;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--color-text-secondary);
  font-size: $font-size-base;
  font-weight: $font-weight-medium;
  text-align: left;
  transition: all $transition-base;
  position: relative;
  overflow: hidden;
  white-space: nowrap;
  
  // Hover effect: slight background + lift
  &:hover {
    background: var(--color-surface-elevated);
    color: var(--color-text-primary);
    transform: translateX(4px);
    
    .nav-icon {
      transform: scale(1.1);
    }
  }
  
  // Active state: primary color + glow
  &.active {
    color: var(--color-primary);
    background: rgba(74, 105, 255, 0.1);
    
    .dark & {
      background: rgba(122, 162, 247, 0.15);
    }
    
    // Subtle glow effect for active item
    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 50%;
      transform: translateY(-50%);
      width: 3px;
      height: 60%;
      background: var(--color-primary);
      border-radius: 0 $radius-sm $radius-sm 0;
    }
  }
  
  // When sidebar is collapsed, center the icon
  .collapsed & {
    justify-content: center;
    padding: $spacing-md $spacing-sm;
  }
}

.nav-icon {
  flex-shrink: 0;
  transition: transform $transition-base;
}

.nav-label {
  flex: 1;
  transition: opacity $transition-fast;
}

// Label fade animation
.label-fade-enter-active,
.label-fade-leave-active {
  transition: opacity 0.2s ease;
}

.label-fade-enter-from,
.label-fade-leave-to {
  opacity: 0;
}
</style>

