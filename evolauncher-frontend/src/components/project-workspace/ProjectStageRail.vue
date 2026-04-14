<script setup lang="ts">
defineProps<{
  stages: Array<{ key: string; label: string }>
  currentStage: string
}>()
</script>

<template>
  <div class="stage-rail">
    <div
      v-for="(stage, index) in stages"
      :key="stage.key"
      class="stage-node"
      :class="{ active: stage.key === currentStage }"
    >
      <div class="node-dot">{{ index + 1 }}</div>
      <div class="node-label">{{ stage.label }}</div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.stage-rail {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 10px;
}

.stage-node {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid var(--color-border);
  min-width: 0;

  .dark & {
    background: rgba(30, 41, 59, 0.55);
  }

  &.active {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(16, 185, 129, 0.12));
    border-color: rgba(59, 130, 246, 0.28);
  }
}

.node-dot {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: var(--color-surface-elevated);
  color: var(--color-text-secondary);
  font-size: 12px;
  font-weight: 700;
}

.active .node-dot {
  background: var(--color-primary);
  color: white;
}

.node-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.active .node-label {
  color: var(--color-text-primary);
}

@media (max-width: 960px) {
  .stage-rail {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
