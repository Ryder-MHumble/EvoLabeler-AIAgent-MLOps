<script setup lang="ts">
import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import EvolutionMonitor from '@/components/workspace/EvolutionMonitor.vue'
import EvoLoopProgress from '@/components/workspace/EvoLoopProgress.vue'
import LossChartCard from '@/components/workspace/LossChartCard.vue'
import MetricsHistoryChart from '@/components/workspace/MetricsHistoryChart.vue'
import ModelHealthCard from '@/components/workspace/ModelHealthCard.vue'
import ModelVersionsPanel from '@/components/workspace/ModelVersionsPanel.vue'
import YoloMetricsCard from '@/components/workspace/YoloMetricsCard.vue'
import ProjectActivityDrawer from '@/components/project-workspace/ProjectActivityDrawer.vue'
import { useWorkspaceStore } from '@/store/workspace'
import { useProjectJourneyStore } from '@/store/projectJourney'

const workspaceStore = useWorkspaceStore()
const journeyStore = useProjectJourneyStore()

const steps = [
  { key: 'initialization', label: '初始化', icon: 'ph:gear' },
  { key: 'data_preparation', label: '数据准备', icon: 'ph:database' },
  { key: 'model_training', label: '模型训练', icon: 'ph:brain' },
  { key: 'active_learning', label: '主动学习', icon: 'ph:arrows-clockwise' },
  { key: 'inference', label: '推理验证', icon: 'ph:lightning' },
  { key: 'completed', label: '完成', icon: 'ph:check-circle' },
] as const

const currentStepIndex = computed(() => {
  const currentStep = workspaceStore.jobStatus?.currentStep
  const index = steps.findIndex((step) => step.key === currentStep)
  return index === -1 ? 0 : index
})
</script>

<template>
  <div class="train-view">
    <section class="train-banner">
      <div>
        <p class="banner-kicker">Train Narrative</p>
        <h2>{{ journeyStore.trainSummary.headline }}</h2>
        <p>统一训练面板以确定性演示脚本驱动，Overview / Annotate / Train 看到的是同一份项目状态。</p>
      </div>

      <div class="train-summary">
        <div class="summary-pill">
          <span>Active</span>
          <strong>{{ journeyStore.trainSummary.activeVersion }}</strong>
        </div>
        <div class="summary-pill">
          <span>Best</span>
          <strong>{{ journeyStore.trainSummary.bestVersion }}</strong>
        </div>
      </div>
    </section>

    <EvoLoopProgress
      :rounds="workspaceStore.evoRounds"
      :current-round="workspaceStore.currentRound"
      :max-rounds="5"
    />

    <section class="train-grid">
      <EvolutionMonitor
        :steps="steps"
        :current-job="workspaceStore.jobStatus"
        :current-step-index="currentStepIndex"
      />

      <div class="center-stack">
        <YoloMetricsCard :current-job="workspaceStore.jobStatus" />
        <LossChartCard :loss-data="workspaceStore.lossData" />
      </div>

      <div class="right-stack">
        <ModelHealthCard
          :health-report="workspaceStore.healthReport"
          :is-loading="workspaceStore.isLoading"
        />
        <ModelVersionsPanel
          :versions="workspaceStore.modelVersions"
          :is-loading="workspaceStore.isLoading"
          @rollback="workspaceStore.rollbackModel"
        />
      </div>
    </section>

    <MetricsHistoryChart
      :history="workspaceStore.metricsHistory"
      :is-loading="workspaceStore.isLoading"
    />

    <ProjectActivityDrawer :activities="journeyStore.recentActivity" />
  </div>
</template>

<style scoped lang="scss">
.train-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.train-banner {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  padding: 18px 20px;
  border-radius: 22px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(30, 41, 59, 0.88));
  color: white;

  h2 {
    margin: 0;
    font-size: 24px;
  }

  p:last-child {
    margin: 8px 0 0;
    color: rgba(226, 232, 240, 0.84);
    line-height: 1.6;
  }
}

.banner-kicker {
  margin: 0 0 6px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(191, 219, 254, 0.82);
}

.train-summary {
  display: flex;
  gap: 10px;
}

.summary-pill {
  min-width: 110px;
  padding: 12px 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.08);

  span,
  strong {
    display: block;
  }

  span {
    font-size: 11px;
    text-transform: uppercase;
    color: rgba(191, 219, 254, 0.82);
  }

  strong {
    margin-top: 6px;
    font-size: 18px;
  }
}

.train-grid {
  display: grid;
  grid-template-columns: minmax(260px, 320px) minmax(0, 1fr) minmax(280px, 340px);
  gap: 16px;
}

.center-stack,
.right-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

@media (max-width: 1320px) {
  .train-grid {
    grid-template-columns: 1fr;
  }

  .train-banner {
    flex-direction: column;
    align-items: flex-start;
  }

  .train-summary {
    flex-wrap: wrap;
  }
}
</style>
