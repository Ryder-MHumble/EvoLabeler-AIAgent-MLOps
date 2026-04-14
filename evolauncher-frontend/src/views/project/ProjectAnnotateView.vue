<script setup lang="ts">
import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import SmartCanvas from '@/components/workspace/SmartCanvas.vue'
import ProjectActivityDrawer from '@/components/project-workspace/ProjectActivityDrawer.vue'
import ProjectQueuePanel from '@/components/project-workspace/ProjectQueuePanel.vue'
import ProjectReviewInspector from '@/components/project-workspace/ProjectReviewInspector.vue'
import { useMissionStore } from '@/store/mission'
import { useProjectJourneyStore } from '@/store/projectJourney'

const missionStore = useMissionStore()
const journeyStore = useProjectJourneyStore()

const pendingWork = computed(
  () => journeyStore.queueSummary.ready + journeyStore.queueSummary.review + journeyStore.queueSummary.imported,
)
</script>

<template>
  <div class="annotate-view">
    <section class="annotate-banner">
      <div>
        <p class="banner-kicker">Mission Cockpit</p>
        <h2>统一协同标注台</h2>
        <p>当前主路径是“确认并下一张”，不再让用户在多套页面和数据状态之间来回切换。</p>
      </div>

      <div class="banner-stats">
        <div class="banner-stat">
          <Icon icon="ph:list-checks" :width="18" />
          <div>
            <strong>{{ pendingWork }}</strong>
            <span>待处理样本</span>
          </div>
        </div>
        <div class="banner-stat">
          <Icon icon="ph:check-circle" :width="18" />
          <div>
            <strong>{{ journeyStore.queueSummary.done }}</strong>
            <span>已完成</span>
          </div>
        </div>
      </div>
    </section>

    <section class="annotate-layout">
      <ProjectQueuePanel class="queue-column" />
      <SmartCanvas class="canvas-column" />
      <ProjectReviewInspector class="review-column" />
    </section>

    <ProjectActivityDrawer :activities="journeyStore.recentActivity" />
  </div>
</template>

<style scoped lang="scss">
.annotate-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
}

.annotate-banner {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  padding: 18px 20px;
  border-radius: 22px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.07), rgba(16, 185, 129, 0.08));
  border: 1px solid rgba(59, 130, 246, 0.14);

  h2 {
    margin: 0;
    font-size: 24px;
    color: var(--color-text-primary);
  }

  p:last-child {
    margin: 8px 0 0;
    color: var(--color-text-secondary);
    line-height: 1.6;
  }
}

.banner-kicker {
  margin: 0 0 6px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-tertiary);
}

.banner-stats {
  display: flex;
  gap: 12px;
}

.banner-stat {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 130px;
  padding: 12px 14px;
  border-radius: 18px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);

  strong {
    display: block;
    color: var(--color-text-primary);
    font-size: 22px;
    line-height: 1;
  }

  span {
    font-size: 12px;
    color: var(--color-text-secondary);
  }
}

.annotate-layout {
  min-height: 640px;
  display: grid;
  grid-template-columns: minmax(280px, 320px) minmax(0, 1fr) minmax(300px, 340px);
  gap: 16px;
}

.queue-column,
.canvas-column,
.review-column {
  min-width: 0;
  min-height: 0;
}

@media (max-width: 1320px) {
  .annotate-layout {
    grid-template-columns: 1fr;
    grid-auto-rows: minmax(260px, auto);
  }

  .annotate-banner {
    flex-direction: column;
    align-items: flex-start;
  }

  .banner-stats {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>
