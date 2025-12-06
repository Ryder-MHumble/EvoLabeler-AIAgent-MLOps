<script setup lang="ts">
/**
 * EvolutionMonitor - 进化任务监视器
 * 显示工作流步骤进度
 */

import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { Icon } from '@iconify/vue'
import gsap from 'gsap'
import AnimatedCard from '@/components/common/AnimatedCard.vue'
import type { StepConfig, JobStatus } from './types'

const props = defineProps<{
  steps: StepConfig[]
  currentJob: JobStatus | null
  currentStepIndex: number
}>()

const emit = defineEmits<{
  stepChange: [index: number]
}>()

const stepsContainer = ref<HTMLElement | null>(null)
const stepHighlight = ref<HTMLElement | null>(null)

const highlightStep = (index: number) => {
  if (!stepsContainer.value || !stepHighlight.value) return

  const stepElements = stepsContainer.value.querySelectorAll('.el-step')
  const target = stepElements[index] as HTMLElement | undefined
  if (!target) return

  const containerRect = stepsContainer.value.getBoundingClientRect()
  const targetRect = target.getBoundingClientRect()
  const offsetY = targetRect.top - containerRect.top

  gsap.to(stepHighlight.value, {
    y: offsetY,
    height: targetRect.height,
    duration: 0.6,
    ease: 'power3.out'
  })

  gsap.fromTo(
    target,
    { scale: 0.98 },
    { scale: 1, duration: 0.4, ease: 'back.out(1.6)' }
  )
}

const handleResize = () => {
  requestAnimationFrame(() => highlightStep(props.currentStepIndex))
}

watch(() => props.currentStepIndex, (newIndex) => {
  nextTick(() => highlightStep(newIndex))
})

onMounted(() => {
  nextTick(() => highlightStep(props.currentStepIndex))
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <AnimatedCard class="evolution-monitor" :hoverable="false">
    <h2 class="card-title">
      <Icon icon="ph:flow-arrow" :width="22" class="title-icon" />
      {{ $t('workspace.evolutionMonitor') }}
    </h2>
    
    <div class="steps-container" ref="stepsContainer">
      <div class="steps-highlight" ref="stepHighlight"></div>

      <el-steps
        class="monitor-steps"
        direction="vertical"
        :active="currentStepIndex"
        finish-status="success"
      >
        <el-step
          v-for="(step, index) in steps"
          :key="step.key"
          :title="step.label"
          :class="{
            'is-current': currentJob && currentJob.currentStep === step.key,
            'is-complete': currentJob && steps.findIndex(s => s.key === currentJob?.currentStep) > index
          }"
        >
          <template #icon>
            <div class="step-icon-wrapper">
              <Icon :icon="step.icon" :width="16" />
            </div>
          </template>
          <template #description>
            <div class="step-description">
              <div v-if="currentJob && step.key === currentJob.currentStep" class="step-progress">
                <el-progress :percentage="currentJob.progress" :show-text="false" :stroke-width="4" />
              </div>
              <div v-else class="step-placeholder">
                <span v-if="currentJob && steps.findIndex(s => s.key === currentJob?.currentStep) > index">
                  {{ $t('workspace.completedViaResidual') }}
                </span>
                <span v-else>{{ $t('workspace.pendingExecution') }}</span>
              </div>
            </div>
          </template>
        </el-step>
      </el-steps>
    </div>
  </AnimatedCard>
</template>

<style scoped lang="scss">
.evolution-monitor {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: clamp(14px, 1.3vw, 16px);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 16px;
  flex-shrink: 0;
  
  .title-icon {
    color: var(--color-primary);
  }
}

.steps-container {
  position: relative;
  flex: 1;
  padding-left: 8px;
}

.steps-highlight {
  position: absolute;
  left: 8px;
  top: 12px;
  width: 4px;
  height: 50px;
  border-radius: 4px;
  background: linear-gradient(180deg, var(--color-primary), rgba(74, 105, 255, 0.1));
  z-index: 0;
}

:deep(.monitor-steps) {
  position: relative;
  padding-left: 16px;
}

:deep(.monitor-steps .el-step) {
  margin-bottom: 16px;
  transition: transform 0.3s ease;
}

:deep(.monitor-steps .el-step__head) {
  z-index: 1;
}

.step-icon-wrapper {
  width: clamp(28px, 2.5vw, 36px);
  height: clamp(28px, 2.5vw, 36px);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface-elevated);
  border: 2px solid var(--color-border);
  transition: all 0.3s ease;
  color: var(--color-text-secondary);
}

:deep(.monitor-steps .el-step.is-current .step-icon-wrapper) {
  background: var(--color-primary);
  color: white;
  box-shadow: 0 0 16px rgba(74, 105, 255, 0.35);
}

:deep(.monitor-steps .el-step.is-complete .step-icon-wrapper) {
  background: var(--color-success);
  color: white;
  border-color: transparent;
}

:deep(.monitor-steps .el-step__title) {
  font-weight: 600;
  font-size: clamp(12px, 1.1vw, 14px);
  color: var(--color-text-secondary);
}

:deep(.monitor-steps .el-step.is-current .el-step__title) {
  color: var(--color-text-primary);
}

.step-description {
  margin-top: 8px;
  padding-left: 8px;
}

.step-progress {
  margin-top: 6px;
}

.step-placeholder {
  font-size: clamp(10px, 0.9vw, 11px);
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
</style>

