<script setup lang="ts">
import { Icon } from '@iconify/vue'

defineProps<{
  active: boolean
  progress: number
  playback: 'idle' | 'playing' | 'paused' | 'completed'
  chapterLabel: string
  headline: string
  narrative: string
}>()

const emit = defineEmits<{
  pause: []
  resume: []
  skip: []
  replay: []
}>()
</script>

<template>
  <div class="launch-demo-card" :class="{ active }">
    <div class="demo-header">
      <div>
        <div class="demo-badge">
          <Icon icon="ph:rocket-launch" :width="16" />
          <span>Launch Demo</span>
        </div>
        <h3 class="demo-title">{{ chapterLabel }}</h3>
        <p class="demo-subtitle">{{ headline }}</p>
      </div>

      <div class="demo-actions">
        <el-button
          v-if="active && playback === 'playing'"
          size="small"
          @click="emit('pause')"
        >
          <Icon icon="ph:pause" :width="16" />
          <span>暂停</span>
        </el-button>
        <el-button
          v-else-if="active && playback === 'paused'"
          size="small"
          @click="emit('resume')"
        >
          <Icon icon="ph:play" :width="16" />
          <span>继续</span>
        </el-button>
        <el-button v-if="active" size="small" text @click="emit('skip')">
          <span>跳过</span>
        </el-button>
        <el-button v-if="!active" size="small" type="primary" plain @click="emit('replay')">
          <Icon icon="ph:arrow-clockwise" :width="16" />
          <span>回放</span>
        </el-button>
      </div>
    </div>

    <div class="demo-progress">
      <div class="progress-meta">
        <span>{{ active ? '演示进行中' : '演示已结束' }}</span>
        <span>{{ progress }}%</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
      </div>
    </div>

    <p class="demo-narrative">{{ narrative }}</p>
  </div>
</template>

<style scoped lang="scss">
.launch-demo-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px 20px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.92));
  color: white;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.22);
}

.demo-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.demo-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(96, 165, 250, 0.14);
  color: #bfdbfe;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.demo-title {
  margin: 10px 0 4px;
  font-size: 22px;
  font-weight: 700;
}

.demo-subtitle,
.demo-narrative {
  margin: 0;
  color: rgba(226, 232, 240, 0.88);
  line-height: 1.6;
}

.demo-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.demo-progress {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: rgba(191, 219, 254, 0.82);
}

.progress-track {
  width: 100%;
  height: 10px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.2);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #3b82f6, #34d399);
  transition: width 0.45s ease;
}

@media (max-width: 900px) {
  .demo-header {
    flex-direction: column;
  }
}
</style>
