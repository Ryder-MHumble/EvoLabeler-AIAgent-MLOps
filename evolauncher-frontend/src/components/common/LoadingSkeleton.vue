<script setup lang="ts">
/**
 * Loading Skeleton Component
 * 
 * Design Intent: Provide elegant loading states that maintain layout
 * and reduce perceived loading time. The shimmer effect creates a
 * sense of activity and progress.
 * 
 * Usage: Display while data is being fetched to prevent layout shift
 * and improve perceived performance.
 */

interface Props {
  type?: 'text' | 'title' | 'avatar' | 'image' | 'rectangle'
  width?: string
  height?: string
  count?: number
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  width: '100%',
  height: 'auto',
  count: 1
})

const getHeight = () => {
  if (props.height !== 'auto') return props.height
  
  switch (props.type) {
    case 'title':
      return '32px'
    case 'text':
      return '20px'
    case 'avatar':
      return '48px'
    case 'image':
      return '200px'
    case 'rectangle':
      return '100px'
    default:
      return '20px'
  }
}
</script>

<template>
  <div class="skeleton-wrapper">
    <div
      v-for="i in count"
      :key="i"
      class="skeleton"
      :class="`skeleton-${type}`"
      :style="{
        width: type === 'avatar' ? getHeight() : width,
        height: getHeight()
      }"
    ></div>
  </div>
</template>

<style scoped lang="scss">
.skeleton-wrapper {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-border) 0%,
    var(--color-surface-elevated) 50%,
    var(--color-border) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: $radius-md;
  
  &.skeleton-avatar {
    border-radius: 50%;
  }
  
  &.skeleton-text {
    border-radius: $radius-sm;
  }
  
  &.skeleton-title {
    border-radius: $radius-md;
  }
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>

