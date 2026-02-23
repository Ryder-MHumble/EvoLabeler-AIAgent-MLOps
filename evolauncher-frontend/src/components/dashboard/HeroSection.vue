<script setup lang="ts">
/**
 * HeroSection - 仪表盘顶部 Hero 区域
 * 包含标题、描述、CTA按钮和系统指标
 *
 * TODO: The `metrics` prop currently receives static mock data from the parent
 * (DashboardView). In the future this should be replaced with live data from
 * the backend stats API (e.g., a dedicated `/api/v1/system/metrics` endpoint)
 * so the hero section reflects real-time system telemetry.
 */

import { Icon } from '@iconify/vue'
import type { SystemMetric } from '@/mock/systemMetrics'

defineProps<{
  metrics: SystemMetric[]
}>()

const emit = defineEmits<{
  (e: 'create-project'): void
  (e: 'open-copilot'): void
}>()

const trendIcon = (trend: SystemMetric['trend']) => {
  switch (trend) {
    case 'up': return 'ph:arrow-up-right'
    case 'down': return 'ph:arrow-down-right'
    default: return 'ph:minus'
  }
}
</script>

<template>
  <div class="hero-section">
    <div class="hero-background">
      <div class="hero-glow hero-glow-1"></div>
      <div class="hero-glow hero-glow-2"></div>
      <div class="hero-glow hero-glow-3"></div>
    </div>
    
    <div class="hero-content">
      <div class="hero-text">
        <div class="hero-badge">
          <Icon icon="ph:sparkle-fill" :width="16" />
          <span>基于多智能体的自进化遥感影像目标检测 MLOps 引擎</span>
        </div>
        <h1 class="hero-title">
          <span class="hero-title-main">EvoLabeler</span>
          <span class="hero-title-sub">自进化智能标注系统</span>
        </h1>
        <p class="hero-subtitle">
          基于 <strong>IDEATE</strong> 框架的创新型 MLOps 系统，通过多智能体协作实现遥感影像目标检测的完全自动化闭环。
          集成主动学习、半监督学习与LLM驱动决策，让AI训练更智能、更高效。
        </p>
      </div>

      <div class="hero-actions">
        <button @click="emit('create-project')" class="hero-cta-premium">
          <span class="cta-bg"></span>
          <span class="cta-content">
            <Icon icon="ph:plus-circle" :width="22" />
            <span>{{ $t('dashboard.createProject') }}</span>
            <Icon icon="ph:arrow-right" :width="18" />
          </span>
          <span class="cta-shine"></span>
        </button>
        
        <button @click="emit('open-copilot')" class="hero-cta-secondary">
          <Icon icon="ph:robot" :width="20" />
          <span>协同工作区</span>
        </button>
      </div>
    </div>
    
    <!-- Quick Stats -->
    <div class="hero-stats">
      <div v-for="metric in metrics" :key="metric.id" class="hero-stat-item metric-card">
        <div class="hero-stat-icon">
          <Icon 
            :icon="metric.id === 'active-loops' ? 'ph:arrows-clockwise-fill' : 
                   metric.id === 'uncertainty-drop' ? 'ph:chart-line-down-fill' : 
                   metric.id === 'auto-labeled' ? 'ph:tag-fill' : 
                   'ph:gauge-fill'" 
            :width="24" 
          />
        </div>
        <div class="hero-stat-content">
          <div class="hero-stat-value">
            {{ metric.value.toLocaleString() }}
            <span v-if="metric.unit">{{ metric.unit }}</span>
          </div>
          <div class="hero-stat-label">{{ metric.label }}</div>
          <div class="hero-stat-trend" :class="metric.trend">
            <Icon :icon="trendIcon(metric.trend)" :width="14" />
            <span v-if="metric.delta !== 0">
              {{ metric.trend === 'down' ? '-' : '+' }}{{ metric.delta }}{{ metric.unit }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.hero-section {
  position: relative;
  padding: clamp(32px, 5vw, 48px) clamp(24px, 3vw, 40px);
  margin-bottom: 32px;
  overflow: hidden;
  border-radius: 32px;
  background: linear-gradient(135deg, 
    rgba(74, 105, 255, 0.05) 0%,
    rgba(138, 43, 226, 0.05) 100%
  );
  
  .dark & {
    background: linear-gradient(135deg, 
      rgba(15, 23, 42, 0.6) 0%,
      rgba(30, 41, 59, 0.4) 100%
    );
  }
  
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background: 
      radial-gradient(circle at 20% 50%, rgba(74, 105, 255, 0.15) 0%, transparent 50%),
      radial-gradient(circle at 80% 80%, rgba(138, 43, 226, 0.15) 0%, transparent 50%),
      radial-gradient(circle at 40% 20%, rgba(16, 185, 129, 0.1) 0%, transparent 50%);
    background-size: 200% 200%;
    animation: waveMove 15s ease-in-out infinite;
    opacity: 0.6;
    
    .dark & {
      background: 
        radial-gradient(circle at 20% 50%, rgba(96, 165, 250, 0.2) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(167, 139, 250, 0.2) 0%, transparent 50%),
        radial-gradient(circle at 40% 20%, rgba(16, 185, 129, 0.15) 0%, transparent 50%);
      opacity: 0.4;
    }
  }
  
  &::after {
    content: '';
    position: absolute;
    inset: 0;
    background: 
      radial-gradient(circle at 60% 30%, rgba(74, 105, 255, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 30% 70%, rgba(138, 43, 226, 0.1) 0%, transparent 50%);
    background-size: 300% 300%;
    animation: waveMove 20s ease-in-out infinite reverse;
    opacity: 0.4;
    
    .dark & { opacity: 0.3; }
  }
}

@keyframes waveMove {
  0%, 100% { background-position: 0% 50%, 100% 50%, 50% 0%; }
  50% { background-position: 100% 50%, 0% 50%, 50% 100%; }
}

.hero-background {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.hero-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.5;
  animation: float 25s ease-in-out infinite;
  
  &.hero-glow-1 {
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(74, 105, 255, 0.4), transparent 70%);
    top: -300px;
    left: -150px;
    animation-name: float1;
  }
  
  &.hero-glow-2 {
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(138, 43, 226, 0.3), transparent 70%);
    bottom: -250px;
    right: -100px;
    animation-name: float2;
    animation-delay: -8s;
  }
  
  &.hero-glow-3 {
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(16, 185, 129, 0.25), transparent 70%);
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    animation-name: pulse;
    animation-delay: -16s;
  }
}

@keyframes float1 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(40px, -40px) scale(1.15); }
  66% { transform: translate(-30px, 30px) scale(0.9); }
}

@keyframes float2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(-35px, 35px) scale(1.1); }
  66% { transform: translate(40px, -25px) scale(0.95); }
}

@keyframes pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
  50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.3; }
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 32px;
  margin-bottom: 32px;
  
  @media (max-width: 1024px) {
    flex-direction: column;
    text-align: center;
    align-items: center;
  }
}

.hero-text {
  flex: 1;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(74, 105, 255, 0.1);
  border: 1px solid rgba(74, 105, 255, 0.2);
  border-radius: 50px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 16px;
  backdrop-filter: blur(8px);
  
  .dark & {
    background: rgba(96, 165, 250, 0.15);
    border-color: rgba(96, 165, 250, 0.3);
  }
}

.hero-title {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 0 0 12px 0;
  line-height: 1.2;
  max-width: 700px;
}

.hero-title-main {
  font-size: clamp(36px, 6vw, 72px);
  font-weight: 900;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: linear-gradient(135deg, #4A69FF 0%, #7AA2F7 30%, #8B5CF6 60%, #10B981 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  background-size: 200% 200%;
  animation: gradientShift 8s ease infinite;
  letter-spacing: -0.02em;
  text-shadow: 0 0 40px rgba(74, 105, 255, 0.3);
  
  .dark & {
    background: linear-gradient(135deg, #60A5FA 0%, #7AA2F7 30%, #A78BFA 60%, #34D399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
}

.hero-title-sub {
  font-size: clamp(18px, 2.5vw, 24px);
  font-weight: 600;
  color: var(--color-text-secondary);
  letter-spacing: 0.05em;
  margin-top: -8px;
}

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.hero-subtitle {
  font-size: clamp(14px, 1.5vw, 18px);
  color: var(--color-text-secondary);
  margin: 0;
  max-width: 600px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  
  @media (max-width: 1024px) {
    flex-direction: column;
    width: 100%;
  }
}

.hero-cta-premium {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 16px 32px;
  font-size: 18px;
  font-weight: 700;
  border-radius: 50px;
  border: none;
  cursor: pointer;
  overflow: hidden;
  background: linear-gradient(135deg, #4A69FF 0%, #7AA2F7 50%, #8B5CF6 100%);
  color: white;
  box-shadow: 0 8px 24px rgba(74, 105, 255, 0.4);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1;
  
  .cta-bg {
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, #5B7CFF 0%, #8BB3FF 50%, #9C6CFF 100%);
    opacity: 0;
    transition: opacity 0.4s ease;
  }
  
  .cta-content {
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .cta-shine {
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(
      45deg,
      transparent 30%,
      rgba(255, 255, 255, 0.3) 50%,
      transparent 70%
    );
    transform: translateX(-100%) translateY(-100%) rotate(45deg);
    transition: transform 0.6s ease;
  }
  
  &:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 16px 40px rgba(74, 105, 255, 0.5);
    
    .cta-bg { opacity: 1; }
    .cta-shine { transform: translateX(100%) translateY(100%) rotate(45deg); }
  }
  
  &:active {
    transform: translateY(-1px) scale(0.98);
  }
  
  .dark & {
    background: linear-gradient(135deg, #60A5FA 0%, #7AA2F7 50%, #A78BFA 100%);
    box-shadow: 0 8px 24px rgba(96, 165, 250, 0.4);
    
    &:hover { box-shadow: 0 16px 40px rgba(96, 165, 250, 0.6); }
  }
}

.hero-cta-secondary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 16px 32px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 50px;
  border: 2px solid var(--color-primary);
  background: transparent;
  color: var(--color-primary);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover {
    background: var(--color-primary);
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(74, 105, 255, 0.3);
  }
  
  &:active { transform: translateY(0); }
  
  @media (max-width: 1024px) {
    width: 100%;
    justify-content: center;
  }
}

.hero-stats {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.hero-stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  .dark & {
    background: rgba(30, 41, 59, 0.6);
    border-color: rgba(255, 255, 255, 0.1);
  }
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
  }
}

.hero-stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 18px;
  background: linear-gradient(135deg, #4A69FF, #7AA2F7);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 8px 20px rgba(74, 105, 255, 0.3);
}

.hero-stat-content {
  flex: 1;
}

.hero-stat-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-text-primary);
  line-height: 1;
  margin-bottom: 4px;
  
  span {
    font-size: 14px;
    margin-left: 4px;
    color: var(--color-text-secondary);
  }
}

.hero-stat-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  font-weight: 500;
  margin-bottom: 4px;
  line-height: 1.4;
}

.hero-stat-trend {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  
  &.up { color: #10B981; }
  &.down { color: #EF4444; }
  &.steady { color: var(--color-text-tertiary); }
}
</style>

