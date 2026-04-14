<script setup lang="ts">
import { computed, ref } from 'vue'
import { Icon } from '@iconify/vue'
import type { ActivityItem } from '@/mock/projectJourney'

const props = defineProps<{
  activities: ActivityItem[]
}>()

const expanded = ref(false)

const latest = computed(() => props.activities[0])

const toneIcon = (tone: ActivityItem['tone']) => {
  switch (tone) {
    case 'success':
      return 'ph:check-circle'
    case 'warning':
      return 'ph:warning'
    case 'loop':
      return 'ph:arrows-clockwise'
    default:
      return 'ph:info'
  }
}
</script>

<template>
  <div class="activity-drawer" :class="{ expanded }">
    <button class="drawer-summary" @click="expanded = !expanded">
      <div class="summary-left">
        <Icon :icon="toneIcon(latest?.tone || 'info')" :width="18" />
        <div>
          <strong>{{ latest?.title || '最近活动' }}</strong>
          <span>{{ latest?.detail || '等待新的系统事件…' }}</span>
        </div>
      </div>
      <Icon :icon="expanded ? 'ph:caret-down' : 'ph:caret-up'" :width="18" />
    </button>

    <div v-if="expanded" class="drawer-list">
      <div v-for="activity in activities" :key="activity.id" class="activity-row">
        <div class="activity-time">{{ new Date(activity.timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) }}</div>
        <div class="activity-content">
          <strong>{{ activity.title }}</strong>
          <span>{{ activity.detail }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.activity-drawer {
  border-radius: 18px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.drawer-summary {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 14px 18px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--color-text-primary);
}

.summary-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;

  strong,
  span {
    display: block;
    text-align: left;
  }

  strong {
    font-size: 13px;
  }

  span {
    font-size: 12px;
    color: var(--color-text-secondary);
    margin-top: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.drawer-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0 18px 18px;
}

.activity-row {
  display: grid;
  grid-template-columns: 64px minmax(0, 1fr);
  gap: 12px;
  padding-top: 10px;
  border-top: 1px solid var(--color-border);
}

.activity-time {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-tertiary);
}

.activity-content {
  display: flex;
  flex-direction: column;
  gap: 4px;

  strong {
    font-size: 13px;
    color: var(--color-text-primary);
  }

  span {
    font-size: 12px;
    color: var(--color-text-secondary);
    line-height: 1.5;
  }
}
</style>
