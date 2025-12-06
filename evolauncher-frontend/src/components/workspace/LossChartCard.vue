<script setup lang="ts">
/**
 * LossChartCard - YOLO训练损失曲线
 * 可拖动滚动的实时损失曲线图
 */

import { ref, onMounted, onUnmounted } from 'vue'
import { Icon } from '@iconify/vue'
import AnimatedCard from '@/components/common/AnimatedCard.vue'
import type { YoloLossData } from './types'

const props = defineProps<{
  lossData: YoloLossData
}>()

const chartScrollRef = ref<HTMLElement | null>(null)
const isDragging = ref(false)
const dragStart = ref({ x: 0, scrollLeft: 0 })

const handleMouseDown = (e: MouseEvent) => {
  if (!chartScrollRef.value) return
  isDragging.value = true
  dragStart.value = {
    x: e.pageX - chartScrollRef.value.offsetLeft,
    scrollLeft: chartScrollRef.value.scrollLeft
  }
  chartScrollRef.value.style.cursor = 'grabbing'
}

const handleMouseMove = (e: MouseEvent) => {
  if (!isDragging.value || !chartScrollRef.value) return
  e.preventDefault()
  const x = e.pageX - chartScrollRef.value.offsetLeft
  const walk = (x - dragStart.value.x) * 2
  chartScrollRef.value.scrollLeft = dragStart.value.scrollLeft - walk
}

const handleMouseUp = () => {
  isDragging.value = false
  if (chartScrollRef.value) {
    chartScrollRef.value.style.cursor = 'grab'
  }
}

onMounted(() => {
  if (chartScrollRef.value) {
    chartScrollRef.value.scrollLeft = chartScrollRef.value.scrollWidth
  }
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
})

// 暴露方法给父组件
defineExpose({
  scrollToEnd: () => {
    if (chartScrollRef.value) {
      chartScrollRef.value.scrollLeft = chartScrollRef.value.scrollWidth
    }
  }
})
</script>

<template>
  <AnimatedCard class="loss-chart-card" :hoverable="false">
    <div class="chart-header">
      <h2 class="card-title">
        <Icon icon="ph:chart-line" :width="18" class="title-icon" />
        YOLO训练损失曲线
      </h2>
      <div class="chart-legend">
        <div class="legend-item">
          <span class="legend-dot box"></span>
          <span class="legend-label">Box</span>
          <span class="legend-value">{{ lossData.boxLoss[lossData.boxLoss.length - 1]?.toFixed(4) }}</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot cls"></span>
          <span class="legend-label">Cls</span>
          <span class="legend-value">{{ lossData.clsLoss[lossData.clsLoss.length - 1]?.toFixed(4) }}</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot obj"></span>
          <span class="legend-label">Obj</span>
          <span class="legend-value">{{ lossData.objLoss[lossData.objLoss.length - 1]?.toFixed(4) }}</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot val"></span>
          <span class="legend-label">Val</span>
          <span class="legend-value">{{ lossData.valLoss[lossData.valLoss.length - 1]?.toFixed(4) }}</span>
        </div>
      </div>
    </div>
    
    <div class="chart-area">
      <!-- 固定Y轴 -->
      <div class="chart-y-axis">
        <svg viewBox="0 0 40 180" preserveAspectRatio="none">
          <text x="35" y="15" text-anchor="end">0.12</text>
          <text x="35" y="55" text-anchor="end">0.09</text>
          <text x="35" y="95" text-anchor="end">0.06</text>
          <text x="35" y="135" text-anchor="end">0.03</text>
          <text x="35" y="175" text-anchor="end">0.00</text>
          <line x1="38" y1="10" x2="38" y2="175" stroke="var(--color-border)" stroke-width="1" />
        </svg>
      </div>
      
      <!-- 可滚动图表区域 -->
      <div 
        ref="chartScrollRef"
        class="chart-scroll"
        @mousedown="handleMouseDown"
      >
        <div class="chart-canvas" :style="{ width: `${Math.max(lossData.epochs.length * 8, 600)}px` }">
          <svg 
            :viewBox="`0 0 ${Math.max(lossData.epochs.length * 8, 600)} 180`" 
            class="chart-svg" 
            preserveAspectRatio="none"
          >
            <!-- 背景渐变 -->
            <defs>
              <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:#4A69FF;stop-opacity:0.15" />
                <stop offset="100%" style="stop-color:#4A69FF;stop-opacity:0.02" />
              </linearGradient>
            </defs>
            
            <!-- 网格线 -->
            <g class="grid-lines">
              <line v-for="i in 5" :key="`h${i}`" 
                x1="0" :y1="10 + (i - 1) * 40" 
                :x2="Math.max(lossData.epochs.length * 8, 600)" :y2="10 + (i - 1) * 40" 
                stroke="var(--color-border)" stroke-width="1" opacity="0.2" />
              <g v-for="i in Math.floor(lossData.epochs.length / 10)" :key="`v${i}`">
                <line :x1="i * 80" y1="10" :x2="i * 80" y2="170" 
                  stroke="var(--color-border)" stroke-width="1" opacity="0.15" />
                <text :x="i * 80" y="180" text-anchor="middle" 
                  fill="var(--color-text-tertiary)" font-size="9">{{ i * 10 }}</text>
              </g>
            </g>
            
            <!-- Box Loss 区域填充 -->
            <path
              :d="`M 0,170 ${lossData.epochs.map((_, i) => 
                `L ${i * 8},${170 - (lossData.boxLoss[i] / 0.12) * 155}`
              ).join(' ')} L ${lossData.epochs.length * 8},170 Z`"
              fill="url(#chartGradient)"
            />
            
            <!-- 各损失曲线 -->
            <polyline
              :points="lossData.epochs.map((_, i) => 
                `${i * 8},${170 - (lossData.boxLoss[i] / 0.12) * 155}`
              ).join(' ')"
              fill="none" stroke="#4A69FF" stroke-width="2" 
              stroke-linecap="round" stroke-linejoin="round"
            />
            <polyline
              :points="lossData.epochs.map((_, i) => 
                `${i * 8},${170 - (lossData.clsLoss[i] / 0.12) * 155}`
              ).join(' ')"
              fill="none" stroke="#8B5CF6" stroke-width="2" 
              stroke-linecap="round" stroke-linejoin="round"
            />
            <polyline
              :points="lossData.epochs.map((_, i) => 
                `${i * 8},${170 - (lossData.objLoss[i] / 0.12) * 155}`
              ).join(' ')"
              fill="none" stroke="#F59E0B" stroke-width="2" 
              stroke-linecap="round" stroke-linejoin="round"
            />
            <polyline
              :points="lossData.epochs.map((_, i) => 
                `${i * 8},${170 - (lossData.valLoss[i] / 0.12) * 155}`
              ).join(' ')"
              fill="none" stroke="#10B981" stroke-width="2" 
              stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="6,4"
            />
            
            <line x1="0" y1="170" :x2="lossData.epochs.length * 8" y2="170" 
              stroke="var(--color-border)" stroke-width="1" />
          </svg>
        </div>
      </div>
    </div>
    
    <div class="chart-x-label">
      <span>Epoch</span>
    </div>
  </AnimatedCard>
</template>

<style scoped lang="scss">
.loss-chart-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 200px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-shrink: 0;
  flex-wrap: wrap;
  gap: 10px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: clamp(13px, 1.2vw, 16px);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
  
  .title-icon { color: var(--color-primary); }
}

.chart-legend {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: clamp(10px, 0.9vw, 12px);
}

.legend-dot {
  width: 10px;
  height: 3px;
  border-radius: 2px;
  
  &.box { background: #4A69FF; }
  &.cls { background: #8B5CF6; }
  &.obj { background: #F59E0B; }
  &.val { background: transparent; border-top: 2px dashed #10B981; }
}

.legend-label {
  color: var(--color-text-tertiary);
  font-weight: 500;
}

.legend-value {
  color: var(--color-text-secondary);
  font-weight: 600;
  font-family: 'Monaco', monospace;
  font-size: 10px;
}

.chart-area {
  display: flex;
  flex: 1;
  min-height: 120px;
  position: relative;
}

.chart-y-axis {
  width: 42px;
  height: 100%;
  flex-shrink: 0;
  background: var(--color-surface);
  z-index: 2;
  
  svg {
    width: 100%;
    height: 100%;
  }
  
  text {
    font-size: 9px;
    fill: var(--color-text-tertiary);
  }
}

.chart-scroll {
  flex: 1;
  height: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  cursor: grab;
  
  &:active { cursor: grabbing; }
  
  &::-webkit-scrollbar {
    height: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: var(--color-surface-elevated);
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(74, 105, 255, 0.4);
    border-radius: 3px;
    
    &:hover { background: rgba(74, 105, 255, 0.6); }
  }
}

.chart-canvas {
  height: 100%;
  min-width: 100%;
}

.chart-svg {
  height: 100%;
  display: block;
}

.chart-x-label {
  display: flex;
  justify-content: center;
  padding-top: 4px;
  padding-left: 40px;
  flex-shrink: 0;
  
  span {
    font-size: clamp(10px, 0.9vw, 12px);
    color: var(--color-text-tertiary);
    font-weight: 500;
  }
}
</style>

