<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import ProjectStageRail from '@/components/project-workspace/ProjectStageRail.vue'
import { useProjectJourneyStore } from '@/store/projectJourney'

const route = useRoute()
const router = useRouter()
const journeyStore = useProjectJourneyStore()

const projectId = computed(() => String(route.params.id || ''))
const autoLaunchConsumed = ref('')

const tabs = [
  { name: 'ProjectOverview', label: 'Overview', segment: 'overview' },
  { name: 'ProjectAnnotate', label: 'Annotate', segment: 'annotate' },
  { name: 'ProjectTrain', label: 'Train', segment: 'train' },
]

const currentTab = computed(() => String(route.name || 'ProjectOverview'))
const stageClass = computed(() => `stage-${journeyStore.stage}`)

const openRecommended = () => {
  router.push({
    name:
      journeyStore.nextRecommendedAction.to === 'annotate'
        ? 'ProjectAnnotate'
        : journeyStore.nextRecommendedAction.to === 'train'
          ? 'ProjectTrain'
          : 'ProjectOverview',
    params: { id: projectId.value },
  })
}

watch(
  projectId,
  async (id) => {
    if (!id) return
    await journeyStore.initializeProject(id)
    if (route.query.launch === '1' && autoLaunchConsumed.value !== id) {
      autoLaunchConsumed.value = id
      journeyStore.startLaunchDemo()
    }
  },
  { immediate: true },
)
</script>

<template>
  <div class="project-shell">
    <header class="project-shell-header">
      <div class="header-main">
        <div class="project-chip" :class="stageClass">
          <Icon icon="ph:stack" :width="16" />
          <span>{{ journeyStore.stage }}</span>
        </div>
        <div class="project-title-block">
          <h1>{{ journeyStore.project?.name || '项目工作台' }}</h1>
          <p>{{ journeyStore.narrative }}</p>
        </div>
      </div>

      <div class="header-side">
        <div class="stat-card">
          <span class="stat-label">Queue</span>
          <strong>{{ journeyStore.queueSummary.total }}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">mAP50</span>
          <strong>{{ journeyStore.trainSummary.latestMap50 }}%</strong>
        </div>
        <el-button type="primary" size="large" @click="openRecommended">
          <span>{{ journeyStore.nextRecommendedAction.label }}</span>
        </el-button>
      </div>
    </header>

    <ProjectStageRail
      :stages="journeyStore.stageList"
      :current-stage="journeyStore.stage"
    />

    <nav class="project-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.name"
        class="project-tab"
        :class="{ active: currentTab === tab.name }"
        @click="router.push({ name: tab.name, params: { id: projectId } })"
      >
        {{ tab.label }}
      </button>
    </nav>

    <section class="project-shell-content">
      <router-view />
    </section>
  </div>
</template>

<style scoped lang="scss">
.project-shell {
  height: 100%;
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: auto;
  @include custom-scrollbar;
}

.project-shell-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: stretch;
  padding: 20px 22px;
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(248, 250, 252, 0.86), rgba(255, 255, 255, 0.98));
  border: 1px solid var(--color-border);

  .dark & {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.88), rgba(30, 41, 59, 0.86));
  }
}

.header-main {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}

.project-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  width: fit-content;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.1);
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

.project-title-block {
  h1 {
    margin: 0;
    font-size: 30px;
    line-height: 1.1;
    color: var(--color-text-primary);
  }

  p {
    margin: 8px 0 0;
    max-width: 720px;
    color: var(--color-text-secondary);
    line-height: 1.6;
  }
}

.header-side {
  display: flex;
  align-items: stretch;
  gap: 12px;
}

.stat-card {
  min-width: 96px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 10px 12px;
  border-radius: 18px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);

  strong {
    font-size: 22px;
    color: var(--color-text-primary);
  }
}

.stat-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text-tertiary);
}

.project-tabs {
  display: inline-flex;
  gap: 8px;
}

.project-tab {
  padding: 10px 16px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text-secondary);
  font-weight: 600;
  cursor: pointer;

  &.active {
    color: white;
    background: var(--color-primary);
    border-color: var(--color-primary);
  }
}

.project-shell-content {
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

@media (max-width: 1120px) {
  .project-shell-header {
    flex-direction: column;
  }

  .header-side {
    flex-wrap: wrap;
  }
}
</style>
