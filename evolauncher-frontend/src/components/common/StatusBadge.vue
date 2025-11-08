<script setup lang="ts">
/**
 * Status Badge Component
 * 
 * Design Intent: Clear, colorful status indicators with consistent styling.
 * Each status type has a semantic color that communicates meaning instantly.
 * 
 * Features:
 * - Pulsing animation for 'running' status
 * - Icon support for enhanced communication
 * - Consistent sizing and spacing
 */

import { computed } from 'vue'
import { Icon } from '@iconify/vue'

type Status = 'idle' | 'running' | 'training' | 'labeling' | 'completed' | 'failed' | 'paused'

interface Props {
  status: Status
  showIcon?: boolean
  size?: 'small' | 'medium' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  showIcon: true,
  size: 'medium'
})

const statusConfig = computed(() => {
  const configs: Record<Status, { color: string; icon: string; label: string }> = {
    idle: {
      color: 'gray',
      icon: 'ph:minus-circle',
      label: 'Idle'
    },
    running: {
      color: 'blue',
      icon: 'ph:play-circle-fill',
      label: 'Running'
    },
    training: {
      color: 'blue',
      icon: 'ph:brain',
      label: 'Training'
    },
    labeling: {
      color: 'purple',
      icon: 'ph:tag',
      label: 'Labeling'
    },
    completed: {
      color: 'green',
      icon: 'ph:check-circle-fill',
      label: 'Completed'
    },
    failed: {
      color: 'red',
      icon: 'ph:x-circle-fill',
      label: 'Failed'
    },
    paused: {
      color: 'yellow',
      icon: 'ph:pause-circle',
      label: 'Paused'
    }
  }
  
  return configs[props.status]
})
</script>

<template>
  <div
    class="status-badge"
    :class="[
      `status-${statusConfig.color}`,
      `size-${size}`,
      { pulse: status === 'running' || status === 'training' }
    ]"
  >
    <Icon
      v-if="showIcon"
      :icon="statusConfig.icon"
      class="status-icon"
    />
    <span class="status-label">{{ statusConfig.label }}</span>
  </div>
</template>

<style scoped lang="scss">
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: $spacing-xs;
  padding: $spacing-xs $spacing-md;
  border-radius: $radius-full;
  font-weight: $font-weight-medium;
  white-space: nowrap;
  transition: all $transition-base;
  
  // Size variants
  &.size-small {
    padding: 2px $spacing-sm;
    font-size: $font-size-xs;
    
    .status-icon {
      font-size: 12px;
    }
  }
  
  &.size-medium {
    padding: $spacing-xs $spacing-md;
    font-size: $font-size-sm;
    
    .status-icon {
      font-size: 16px;
    }
  }
  
  &.size-large {
    padding: $spacing-sm $spacing-lg;
    font-size: $font-size-base;
    
    .status-icon {
      font-size: 20px;
    }
  }
  
  // Color variants
  &.status-gray {
    background: rgba(156, 163, 175, 0.15);
    color: #6B7280;
    
    .dark & {
      background: rgba(156, 163, 175, 0.2);
      color: #9CA3AF;
    }
  }
  
  &.status-blue {
    background: rgba(59, 130, 246, 0.15);
    color: #3B82F6;
    
    .dark & {
      background: rgba(122, 162, 247, 0.2);
      color: #7AA2F7;
    }
  }
  
  &.status-purple {
    background: rgba(168, 85, 247, 0.15);
    color: #A855F7;
    
    .dark & {
      background: rgba(187, 154, 247, 0.2);
      color: #BB9AF7;
    }
  }
  
  &.status-green {
    background: rgba(16, 185, 129, 0.15);
    color: #10B981;
    
    .dark & {
      background: rgba(158, 206, 106, 0.2);
      color: #9ECE6A;
    }
  }
  
  &.status-red {
    background: rgba(239, 68, 68, 0.15);
    color: #EF4444;
    
    .dark & {
      background: rgba(247, 118, 142, 0.2);
      color: #F7768E;
    }
  }
  
  &.status-yellow {
    background: rgba(245, 158, 11, 0.15);
    color: #F59E0B;
    
    .dark & {
      background: rgba(224, 175, 104, 0.2);
      color: #E0AF68;
    }
  }
  
  // Pulse animation for active states
  &.pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.status-icon {
  flex-shrink: 0;
}

.status-label {
  flex-shrink: 0;
}
</style>

