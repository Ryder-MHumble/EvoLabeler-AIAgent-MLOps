<script setup lang="ts">
import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useMissionStore } from '@/store/mission'
import type { QueueState } from '@/api/types'

const missionStore = useMissionStore()

const groups: Array<{ key: QueueState; label: string; icon: string; tone: string }> = [
  { key: 'ready', label: '立即确认', icon: 'ph:lightning', tone: 'ready' },
  { key: 'review', label: '需要复核', icon: 'ph:eye', tone: 'review' },
  { key: 'imported', label: '导入校验', icon: 'ph:folder-open', tone: 'imported' },
  { key: 'done', label: '已完成', icon: 'ph:check-circle', tone: 'done' },
]

const summary = computed(() => missionStore.streamStats)
</script>

<template>
  <aside class="queue-panel">
    <div class="queue-header">
      <div>
        <p class="queue-kicker">Action Queue</p>
        <h3 class="queue-title">协同任务队列</h3>
      </div>
      <div class="queue-total">{{ summary.total }}</div>
    </div>

    <div class="queue-groups">
      <section
        v-for="group in groups"
        :key="group.key"
        class="queue-group"
        :class="group.tone"
      >
        <header class="group-header">
          <div class="group-label">
            <Icon :icon="group.icon" :width="16" />
            <span>{{ group.label }}</span>
          </div>
          <span class="group-count">{{ missionStore.getImageStreamByQueue(group.key).length }}</span>
        </header>

        <div class="group-items">
          <button
            v-for="item in missionStore.getImageStreamByQueue(group.key)"
            :key="item.id"
            class="queue-item"
            :class="{ active: missionStore.currentWorkItem?.id === item.id }"
            @click="missionStore.selectImage(item.id)"
          >
            <img :src="item.thumbnailUrl || item.url" :alt="item.id" class="item-thumb" />
            <div class="item-body">
              <span class="item-title">{{ item.id }}</span>
              <span class="item-subtitle">
                {{ Math.round(item.confidence * 100) }}% · {{ item.boundingBoxes.length }} 框
              </span>
              <span class="item-action">{{ item.analysis.recommendedAction }}</span>
            </div>
          </button>

          <div v-if="missionStore.getImageStreamByQueue(group.key).length === 0" class="empty-row">
            当前分组暂无样本
          </div>
        </div>
      </section>
    </div>
  </aside>
</template>

<style scoped lang="scss">
.queue-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px;
  border-radius: 20px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.queue-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.queue-kicker {
  margin: 0 0 4px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-tertiary);
}

.queue-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.queue-total {
  min-width: 42px;
  height: 42px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.16), rgba(52, 211, 153, 0.16));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary);
}

.queue-groups {
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-right: 4px;
  @include custom-scrollbar;
}

.queue-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px;
  border-radius: 16px;
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
}

.group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.group-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.group-count {
  min-width: 26px;
  text-align: center;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.12);
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 700;
}

.group-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.queue-item {
  width: 100%;
  display: grid;
  grid-template-columns: 64px minmax(0, 1fr);
  gap: 10px;
  padding: 8px;
  border-radius: 14px;
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(59, 130, 246, 0.05);
    border-color: rgba(59, 130, 246, 0.12);
  }

  &.active {
    background: rgba(59, 130, 246, 0.08);
    border-color: rgba(59, 130, 246, 0.24);
  }
}

.item-thumb {
  width: 64px;
  height: 64px;
  border-radius: 10px;
  object-fit: cover;
}

.item-body {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.item-subtitle,
.item-action,
.empty-row {
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.4;
}

.item-action {
  color: var(--color-text-tertiary);
}

.empty-row {
  padding: 6px 0 2px;
}
</style>
