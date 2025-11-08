<script setup lang="ts">
import { ref, h, onErrorCaptured } from 'vue'
import { Icon } from '@iconify/vue'

/**
 * Application-wide error boundary.
 * Captures render/runtime errors and displays a graceful fallback.
 * Design intent: surface issues without breaking the Electron shell.
 */

const error = ref<Error | null>(null)

const resetError = () => {
  error.value = null
}

onErrorCaptured((err) => {
  error.value = err instanceof Error ? err : new Error('Unknown renderer error')
  return false
})
</script>

<template>
  <div v-if="error" class="error-boundary">
    <div class="error-card">
      <div class="error-icon">
        <Icon icon="ph:warning-circle-duotone" :width="48" />
      </div>
      <h2>Oops, something went wrong.</h2>
      <p>
        The UI recovered gracefully. Details are sent to the developer console for inspection.
      </p>
      <code class="error-message">{{ error.message }}</code>
      <el-button type="primary" @click="resetError">
        Try Again
      </el-button>
    </div>
  </div>
  <slot v-else></slot>
</template>

<style scoped lang="scss">
.error-boundary {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100%;
  padding: $spacing-3xl;
  background: var(--color-bg);
}

.error-card {
  max-width: 480px;
  width: 100%;
  background: var(--color-surface);
  border-radius: $radius-2xl;
  padding: $spacing-2xl;
  text-align: center;
  box-shadow: $shadow-lg;
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.error-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  margin: 0 auto $spacing-sm;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

h2 {
  font-size: $font-size-2xl;
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
  margin: 0;
}

p {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  margin: 0;
}

.error-message {
  display: block;
  padding: $spacing-sm;
  background: rgba(239, 68, 68, 0.08);
  border-radius: $radius-md;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: $font-size-xs;
  color: #EF4444;
}
</style>

