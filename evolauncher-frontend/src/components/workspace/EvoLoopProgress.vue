<script setup lang="ts">
/**
 * EvoLoopProgress - EvoLoop 迭代进度条
 *
 * 水平进度组件，显示 EvoLoop 自进化轮次。
 * 每个圆圈代表一轮，用连接线串联。
 */

import { ref, onMounted, watch, nextTick } from 'vue'
import gsap from 'gsap'
import type { EvoRound } from '@/api/models'

const props = withDefaults(
  defineProps<{
    rounds: EvoRound[]
    maxRounds?: number
    currentRound: number
  }>(),
  {
    maxRounds: 5,
  },
)

const containerRef = ref<HTMLElement | null>(null)

/**
 * Map a round status string to a visual state.
 */
function roundState(round: EvoRound): 'completed' | 'running' | 'failed' | 'future' {
  if (round.wasRolledBack) return 'failed'
  if (round.status === 'completed') return 'completed'
  if (round.status === 'running' || round.status === 'in_progress') return 'running'
  if (round.status === 'failed' || round.status === 'error') return 'failed'
  return 'future'
}

/**
 * Get the status label for display.
 */
function statusLabel(round: EvoRound): string {
  if (round.wasRolledBack) return '已回滚'
  const map: Record<string, string> = {
    completed: '完成',
    running: '运行中',
    in_progress: '运行中',
    pending: '等待中',
    failed: '失败',
    error: '失败',
    skipped: '已跳过',
  }
  return map[round.status] || round.status
}

/**
 * Latest continuation reason text.
 */
function latestReason(): string {
  if (props.rounds.length === 0) return ''
  const sorted = [...props.rounds].sort((a, b) => b.roundNumber - a.roundNumber)
  return sorted[0]?.continueReason || ''
}

/**
 * Number of nodes to show (at least maxRounds, or however many rounds exist).
 */
function nodeCount(): number {
  return Math.max(props.maxRounds, props.rounds.length)
}

/**
 * Get the round data for a given 1-indexed node position, or undefined if not yet reached.
 */
function getRound(index: number): EvoRound | undefined {
  return props.rounds.find((r) => r.roundNumber === index)
}

// GSAP entrance animation
function animateEntrance() {
  if (!containerRef.value) return
  const nodes = containerRef.value.querySelectorAll('.round-node')
  const lines = containerRef.value.querySelectorAll('.connector-line')

  gsap.fromTo(
    nodes,
    { scale: 0, opacity: 0 },
    {
      scale: 1,
      opacity: 1,
      duration: 0.4,
      stagger: 0.08,
      ease: 'back.out(1.7)',
    },
  )
  gsap.fromTo(
    lines,
    { scaleX: 0, opacity: 0 },
    {
      scaleX: 1,
      opacity: 1,
      duration: 0.3,
      stagger: 0.06,
      ease: 'power2.out',
      delay: 0.1,
    },
  )
}

onMounted(() => {
  nextTick(() => animateEntrance())
})

watch(
  () => props.rounds.length,
  () => {
    nextTick(() => animateEntrance())
  },
)
</script>

<template>
  <div ref="containerRef" class="evo-loop-progress">
    <!-- Empty state -->
    <div v-if="rounds.length === 0" class="empty-state">
      <span class="empty-text">等待 EvoLoop 启动...</span>
    </div>

    <!-- Progress track -->
    <template v-else>
      <div class="progress-track">
        <template v-for="i in nodeCount()" :key="i">
          <!-- Connector line (not before the first node) -->
          <div
            v-if="i > 1"
            class="connector-line"
            :class="{
              'line-completed': getRound(i - 1) && roundState(getRound(i - 1)!) === 'completed',
              'line-active': getRound(i - 1) && roundState(getRound(i - 1)!) === 'running',
            }"
          />

          <!-- Round node -->
          <div class="round-node-wrapper">
            <div
              class="round-node"
              :class="{
                'state-completed': getRound(i) && roundState(getRound(i)!) === 'completed',
                'state-running': getRound(i) && roundState(getRound(i)!) === 'running',
                'state-failed': getRound(i) && roundState(getRound(i)!) === 'failed',
                'state-future': !getRound(i),
              }"
            >
              <span class="round-number">{{ i }}</span>
            </div>

            <!-- Info below the circle -->
            <div class="round-info">
              <template v-if="getRound(i)">
                <span class="round-status" :class="`status-${roundState(getRound(i)!)}`">
                  {{ statusLabel(getRound(i)!) }}
                </span>
                <span v-if="getRound(i)!.outputImageCount > 0" class="round-images">
                  {{ getRound(i)!.outputImageCount }} 张
                </span>
                <span
                  v-if="roundState(getRound(i)!) === 'completed'"
                  class="round-continue"
                >
                  {{ getRound(i)!.shouldContinue ? '继续' : '停止' }}
                </span>
              </template>
              <template v-else>
                <span class="round-status status-future">待执行</span>
              </template>
            </div>
          </div>
        </template>
      </div>

      <!-- Latest reason text -->
      <div v-if="latestReason()" class="reason-text">
        <span class="reason-label">决策原因：</span>
        {{ latestReason() }}
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">
.evo-loop-progress {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 16px 20px;
  min-height: 80px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
}

.empty-text {
  font-size: 13px;
  color: var(--color-text-tertiary);
  font-style: italic;
}

.progress-track {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 0;
  padding: 4px 0;
}

.connector-line {
  width: clamp(30px, 4vw, 60px);
  height: 3px;
  background: #94A3B8;
  border-radius: 2px;
  margin-top: 16px;
  transform-origin: left center;
  flex-shrink: 0;

  &.line-completed {
    background: #10B981;
  }

  &.line-active {
    background: linear-gradient(90deg, #10B981, #4A69FF);
  }
}

.round-node-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 56px;
  flex-shrink: 0;
}

.round-node {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 13px;
  border: 2px solid transparent;
  transition: all 0.3s ease;

  &.state-completed {
    background: #10B981;
    color: #fff;
    border-color: #10B981;
  }

  &.state-running {
    background: #4A69FF;
    color: #fff;
    border-color: #4A69FF;
    animation: pulse-ring 1.5s ease-out infinite;
    box-shadow: 0 0 0 0 rgba(74, 105, 255, 0.4);
  }

  &.state-failed {
    background: #EF4444;
    color: #fff;
    border-color: #EF4444;
  }

  &.state-future {
    background: var(--color-surface-elevated, #f1f5f9);
    color: #94A3B8;
    border-color: #94A3B8;
  }
}

@keyframes pulse-ring {
  0% {
    box-shadow: 0 0 0 0 rgba(74, 105, 255, 0.4);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(74, 105, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(74, 105, 255, 0);
  }
}

.round-number {
  line-height: 1;
}

.round-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 6px;
  gap: 2px;
}

.round-status {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;

  &.status-completed {
    color: #10B981;
  }

  &.status-running {
    color: #4A69FF;
  }

  &.status-failed {
    color: #EF4444;
  }

  &.status-future {
    color: #94A3B8;
  }
}

.round-images {
  font-size: 10px;
  color: var(--color-text-tertiary);
}

.round-continue {
  font-size: 9px;
  color: var(--color-text-tertiary);
  font-weight: 500;
}

.reason-text {
  margin-top: 10px;
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  padding-top: 8px;
  border-top: 1px solid var(--color-border);
}

.reason-label {
  font-weight: 600;
  color: var(--color-text-primary);
}
</style>
