<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import ProjectLaunchDemoCard from '@/components/project-workspace/ProjectLaunchDemoCard.vue'
import ProjectActivityDrawer from '@/components/project-workspace/ProjectActivityDrawer.vue'
import { useProjectJourneyStore } from '@/store/projectJourney'

const router = useRouter()
const route = useRoute()
const journeyStore = useProjectJourneyStore()

const openNextAction = () => {
  router.push({
    name:
      journeyStore.nextRecommendedAction.to === 'annotate'
        ? 'ProjectAnnotate'
        : journeyStore.nextRecommendedAction.to === 'train'
          ? 'ProjectTrain'
          : 'ProjectOverview',
    params: { id: route.params.id },
  })
}
</script>

<template>
  <div class="overview-view">
    <ProjectLaunchDemoCard
      :active="journeyStore.launchDemo.active"
      :playback="journeyStore.launchDemo.playback"
      :progress="journeyStore.launchDemo.progress"
      :chapter-label="journeyStore.currentChapter?.label || 'Launch Demo Ready'"
      :headline="journeyStore.headline"
      :narrative="journeyStore.narrative"
      @pause="journeyStore.pauseLaunchDemo()"
      @resume="journeyStore.resumeLaunchDemo()"
      @skip="journeyStore.skipLaunchDemo()"
      @replay="journeyStore.replayLaunchDemo()"
    />

    <section class="overview-grid">
      <article class="hero-card">
        <p class="card-kicker">Current Stage</p>
        <h2>{{ journeyStore.headline }}</h2>
        <p>{{ journeyStore.narrative }}</p>

        <div class="hero-actions">
          <el-button type="primary" size="large" @click="openNextAction">
            <span>{{ journeyStore.nextRecommendedAction.label }}</span>
          </el-button>
          <el-button size="large" plain @click="journeyStore.replayLaunchDemo()">
            <Icon icon="ph:arrow-clockwise" :width="18" />
            <span>重新播放演示</span>
          </el-button>
        </div>
      </article>

      <article class="summary-card">
        <p class="card-kicker">Queue Snapshot</p>
        <div class="summary-grid">
          <div class="summary-metric">
            <strong>{{ journeyStore.queueSummary.ready }}</strong>
            <span>立即确认</span>
          </div>
          <div class="summary-metric">
            <strong>{{ journeyStore.queueSummary.review }}</strong>
            <span>需要复核</span>
          </div>
          <div class="summary-metric">
            <strong>{{ journeyStore.queueSummary.imported }}</strong>
            <span>导入校验</span>
          </div>
          <div class="summary-metric">
            <strong>{{ journeyStore.queueSummary.done }}</strong>
            <span>已完成</span>
          </div>
        </div>
      </article>

      <article class="summary-card">
        <p class="card-kicker">Model Snapshot</p>
        <div class="summary-grid">
          <div class="summary-metric">
            <strong>{{ journeyStore.trainSummary.currentRound }}</strong>
            <span>当前轮次</span>
          </div>
          <div class="summary-metric">
            <strong>{{ journeyStore.trainSummary.latestMap50 }}%</strong>
            <span>mAP50</span>
          </div>
          <div class="summary-metric">
            <strong>{{ journeyStore.trainSummary.precision }}%</strong>
            <span>Precision</span>
          </div>
          <div class="summary-metric">
            <strong>{{ journeyStore.trainSummary.recall }}%</strong>
            <span>Recall</span>
          </div>
        </div>
      </article>
    </section>

    <ProjectActivityDrawer :activities="journeyStore.recentActivity" />
  </div>
</template>

<style scoped lang="scss">
.overview-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.overview-grid {
  display: grid;
  grid-template-columns: 1.35fr 1fr 1fr;
  gap: 16px;
}

.hero-card,
.summary-card {
  padding: 20px;
  border-radius: 22px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}

.card-kicker {
  margin: 0 0 8px;
  font-size: 11px;
  letter-spacing: 0.08em;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--color-text-tertiary);
}

.hero-card {
  h2 {
    margin: 0;
    font-size: 26px;
    color: var(--color-text-primary);
  }

  p:last-of-type {
    margin: 12px 0 0;
    color: var(--color-text-secondary);
    line-height: 1.7;
  }
}

.hero-actions {
  display: flex;
  gap: 12px;
  margin-top: 18px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.summary-metric {
  padding: 14px;
  border-radius: 18px;
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border);

  strong {
    display: block;
    font-size: 28px;
    line-height: 1;
    color: var(--color-text-primary);
  }

  span {
    display: block;
    margin-top: 8px;
    color: var(--color-text-secondary);
    font-size: 12px;
  }
}

@media (max-width: 1200px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }

  .hero-actions {
    flex-wrap: wrap;
  }
}
</style>
