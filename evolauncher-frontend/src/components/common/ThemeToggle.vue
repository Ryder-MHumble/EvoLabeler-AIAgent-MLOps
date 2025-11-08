<script setup lang="ts">
/**
 * Theme Toggle Component
 * 
 * Design Intent: Create a satisfying, animated toggle that clearly
 * communicates the current theme state through both icon and motion.
 * 
 * Animation Strategy:
 * - Icon rotation for visual feedback during transition
 * - Smooth color transition
 * - Hover scale effect for interactivity
 */

import { useTheme } from '@/composables/useTheme'
import { Icon } from '@iconify/vue'

const { isDark, toggleTheme } = useTheme()

const handleToggle = () => {
  toggleTheme()
}
</script>

<template>
  <button
    class="theme-toggle non-draggable"
    @click="handleToggle"
    :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
  >
    <transition name="icon-fade" mode="out-in">
      <Icon
        v-if="isDark"
        icon="ph:moon-stars-fill"
        class="theme-icon"
        :width="20"
      />
      <Icon
        v-else
        icon="ph:sun-fill"
        class="theme-icon"
        :width="20"
      />
    </transition>
  </button>
</template>

<style scoped lang="scss">
.theme-toggle {
  width: 40px;
  height: 40px;
  border-radius: $radius-md;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all $transition-base;
  color: var(--color-text-secondary);
  
  // Hover effect: subtle background + scale
  &:hover {
    background: var(--color-surface-elevated);
    color: var(--color-text-primary);
    transform: scale(1.05);
  }
  
  // Active/pressed effect: quick scale down for tactile feedback
  &:active {
    transform: scale(0.95);
  }
  
  // Focus state for accessibility
  &:focus-visible {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }
}

.theme-icon {
  transition: transform $transition-base;
}

// Icon transition animation
.icon-fade-enter-active,
.icon-fade-leave-active {
  transition: all 0.2s ease;
}

.icon-fade-enter-from {
  opacity: 0;
  transform: rotate(-90deg) scale(0.8);
}

.icon-fade-leave-to {
  opacity: 0;
  transform: rotate(90deg) scale(0.8);
}
</style>

