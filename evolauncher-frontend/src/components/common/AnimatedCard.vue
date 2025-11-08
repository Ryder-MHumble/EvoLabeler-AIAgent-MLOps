<script setup lang="ts">
/**
 * Animated Card Component
 * 
 * Design Philosophy:
 * - Premium card component with smooth hover interactions
 * - Elevation changes on hover create depth perception
 * - Supports different variants for various use cases
 * - Hardware accelerated animations for smooth 60fps performance
 * 
 * Animation Details:
 * - Hover lift: Subtle upward movement with shadow increase
 * - Click feedback: Quick scale down for tactile response
 * - Border glow on hover in dark mode for premium feel
 */

import { computed } from 'vue'

interface Props {
  variant?: 'default' | 'elevated' | 'outlined'
  hoverable?: boolean
  clickable?: boolean
  padding?: string
  borderRadius?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  hoverable: true,
  clickable: false,
  padding: '1.5rem',
  borderRadius: '1rem'
})

const emit = defineEmits<{
  click: []
}>()

const cardClasses = computed(() => ({
  'card-hoverable': props.hoverable,
  'card-clickable': props.clickable,
  [`card-${props.variant}`]: true
}))

const handleClick = () => {
  if (props.clickable) {
    emit('click')
  }
}
</script>

<template>
  <div
    class="animated-card"
    :class="cardClasses"
    :style="{
      padding: padding,
      borderRadius: borderRadius
    }"
    @click="handleClick"
  >
    <slot></slot>
  </div>
</template>

<style scoped lang="scss">
.animated-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
  position: relative;
  overflow: hidden;
  
  // Hardware acceleration for smooth animations
  @include hw-accelerate;
  
  // Default variant
  &.card-default {
    box-shadow: $shadow-sm;
  }
  
  // Elevated variant - starts with more shadow
  &.card-elevated {
    box-shadow: $shadow-md;
  }
  
  // Outlined variant - emphasis on border
  &.card-outlined {
    box-shadow: none;
    border-width: 2px;
  }
  
  // Hoverable state
  &.card-hoverable:hover {
    transform: translateY(-4px);
    box-shadow: $shadow-lg;
    border-color: var(--color-primary-light);
    
    // In dark mode, add subtle glow
    .dark & {
      box-shadow: $shadow-dark-lg, 0 0 20px rgba(122, 162, 247, 0.2);
    }
  }
  
  // Clickable state
  &.card-clickable {
    cursor: pointer;
    
    &:active {
      transform: translateY(-2px) scale(0.98);
    }
  }
  
  // Subtle background shine on hover (for premium feel)
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.1),
      transparent
    );
    transition: left 0.5s ease;
    pointer-events: none;
  }
  
  &.card-hoverable:hover::before {
    left: 100%;
  }
}
</style>

