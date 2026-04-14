<script setup lang="ts">
import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useMissionStore } from '@/store/mission'
import { useProjectJourneyStore } from '@/store/projectJourney'

const missionStore = useMissionStore()
const journeyStore = useProjectJourneyStore()

const currentItem = computed(() => missionStore.currentWorkItem)

const pendingCount = computed(() =>
  currentItem.value?.boundingBoxes.filter((bbox) => bbox.status !== 'confirmed').length || 0,
)

const confirmAndNext = () => {
  if (!currentItem.value) return
  const processedId = currentItem.value.id
  missionStore.completeCurrentImage()
  journeyStore.syncQueueSummary()
  journeyStore.refreshActivity(
    '样本已确认并推进下一张',
    `${processedId} 已转入已完成队列。`,
  )
}

const sendToReview = () => {
  if (!currentItem.value) return
  const processedId = currentItem.value.id
  missionStore.markCurrentForReview()
  journeyStore.syncQueueSummary()
  journeyStore.refreshActivity(
    '样本被标记为复核',
    `${processedId} 已回到需要复核分组。`,
  )
}
</script>

<template>
  <aside class="review-panel">
    <div class="review-header">
      <div>
        <p class="review-kicker">Inspector</p>
        <h3 class="review-title">当前审阅上下文</h3>
      </div>
      <div v-if="currentItem" class="confidence-badge">
        {{ Math.round(currentItem.confidence * 100) }}%
      </div>
    </div>

    <div v-if="currentItem" class="review-content">
      <section class="info-card">
        <div class="info-row">
          <span>当前样本</span>
          <strong>{{ currentItem.id }}</strong>
        </div>
        <div class="info-row">
          <span>队列状态</span>
          <strong>{{ currentItem.queueState }}</strong>
        </div>
        <div class="info-row">
          <span>待确认框</span>
          <strong>{{ pendingCount }}</strong>
        </div>
      </section>

      <section class="analysis-card">
        <header class="card-header">
          <Icon icon="ph:robot" :width="16" />
          <span>AI 理由</span>
        </header>
        <ul class="reason-list">
          <li v-for="reason in currentItem.analysis.reasons" :key="reason">{{ reason }}</li>
        </ul>
        <p class="recommended-action">{{ currentItem.analysis.recommendedAction }}</p>
      </section>

      <section class="tag-card">
        <header class="card-header">
          <Icon icon="ph:warning-circle" :width="16" />
          <span>风险与标签</span>
        </header>
        <div class="tag-row">
          <el-tag size="small" :type="currentItem.analysis.riskLevel === 'high' ? 'danger' : currentItem.analysis.riskLevel === 'medium' ? 'warning' : 'success'">
            {{ currentItem.analysis.riskLevel }}
          </el-tag>
          <el-tag
            v-for="tag in currentItem.analysis.tags || []"
            :key="tag"
            size="small"
            effect="plain"
          >
            {{ tag }}
          </el-tag>
        </div>
      </section>

      <div class="action-stack">
        <el-button type="primary" size="large" @click="confirmAndNext">
          <Icon icon="ph:check-circle" :width="18" />
          <span>确认并下一张</span>
        </el-button>
        <el-button size="large" plain @click="sendToReview">
          <Icon icon="ph:arrow-counter-clockwise" :width="18" />
          <span>标记复核</span>
        </el-button>
      </div>
    </div>

    <div v-else class="empty-state">
      <Icon icon="ph:selection" :width="32" />
      <p>选择一个样本后，这里会显示审阅理由与动作建议。</p>
    </div>
  </aside>
</template>

<style scoped lang="scss">
.review-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px;
  border-radius: 20px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}

.review-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.review-kicker {
  margin: 0 0 4px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-tertiary);
}

.review-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.confidence-badge {
  padding: 7px 10px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.14), rgba(52, 211, 153, 0.14));
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 700;
}

.review-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-card,
.analysis-card,
.tag-card {
  padding: 14px;
  border-radius: 16px;
  background: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
}

.info-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  font-size: 13px;
  color: var(--color-text-secondary);

  + .info-row {
    margin-top: 10px;
  }

  strong {
    color: var(--color-text-primary);
    font-weight: 700;
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.reason-list {
  margin: 0;
  padding-left: 18px;
  color: var(--color-text-secondary);
  font-size: 13px;
  line-height: 1.6;
}

.recommended-action {
  margin: 10px 0 0;
  color: var(--color-text-tertiary);
  font-size: 12px;
  line-height: 1.5;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.action-stack {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  text-align: center;
  color: var(--color-text-secondary);
}
</style>
