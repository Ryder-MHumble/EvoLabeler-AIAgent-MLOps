<script setup lang="ts">
/**
 * CoPilot Workspace View - 智能标注工作台
 * 
 * 模块化重构版本：
 * - WorkspaceHeader: 顶部状态栏
 * - DataInbox: 数据流面板
 * - SmartCanvas: 智能画布
 * - AgentPanel: Agent 面板
 * - LiveTerminal: 实时终端
 */

import { onMounted, onUnmounted, computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useMissionStore } from '@/store/mission'

// 子组件
import WorkspaceHeader from '@/components/copilot/WorkspaceHeader.vue'
import DataInbox from '@/components/workspace/DataInbox.vue'
import SmartCanvas from '@/components/workspace/SmartCanvas.vue'
import AgentPanel from '@/components/workspace/AgentPanel.vue'
import LiveTerminal from '@/components/workspace/LiveTerminal.vue'

const missionStore = useMissionStore()

// 标注进度统计
const annotationProgress = computed(() => {
  const stats = missionStore.streamStats
  const total = stats.incoming + stats.pending + stats.library
  const completed = stats.library
  return {
    total,
    completed,
    pending: stats.pending,
    incoming: stats.incoming,
    percentage: total > 0 ? Math.round((completed / total) * 100) : 0
  }
})

// 初始化
onMounted(async () => {
  await missionStore.loadMissions()
  
  if (missionStore.missions.length > 0) {
    await missionStore.selectMission(missionStore.missions[0].id)
  }
})

onUnmounted(() => {
  missionStore.stopLogStream()
})
</script>

<template>
  <div class="copilot-workspace">
    <!-- 顶部状态栏 -->
    <WorkspaceHeader 
      project-name="海上风电平台检测项目"
      project-badge="YOLO标注"
      :progress="annotationProgress"
    />

    <!-- 主工作区三列布局 -->
    <div class="workspace-layout">
      <!-- 左侧：数据流面板 -->
      <div class="workspace-left">
        <div class="panel-wrapper">
          <div class="panel-header-mini">
            <Icon icon="ph:images-square" :width="16" />
            <span>数据队列</span>
          </div>
          <DataInbox />
        </div>
      </div>

      <!-- 中间：智能画布 -->
      <div class="workspace-center">
        <SmartCanvas />
      </div>

      <!-- 右侧：Agent 面板 -->
      <div class="workspace-right">
        <AgentPanel />
      </div>
    </div>

    <!-- 底部：实时终端 -->
    <LiveTerminal />
  </div>
</template>

<style scoped lang="scss">
.copilot-workspace {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
  position: relative;
  padding-bottom: 30px;
  overflow: hidden;
}

// 主工作区布局
.workspace-layout {
  flex: 1;
  display: grid;
  grid-template-columns: minmax(200px, 260px) minmax(400px, 1fr) minmax(260px, 320px);
  gap: 10px;
  padding: 10px;
  min-height: 0;
  overflow: hidden;
  
  @media (max-width: 1600px) {
    grid-template-columns: minmax(180px, 230px) minmax(350px, 1fr) minmax(230px, 280px);
    gap: 8px;
    padding: 8px;
  }
  
  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
    grid-template-rows: minmax(180px, 280px) 1fr minmax(200px, 280px);
    gap: 8px;
    padding: 8px;
    
    .workspace-left {
      grid-row: 1;
      min-height: 180px;
      max-height: 280px;
    }
    
    .workspace-center {
      grid-row: 2;
      min-height: 350px;
    }
    
    .workspace-right {
      grid-row: 3;
      min-height: 200px;
      max-height: 280px;
    }
  }
  
  @media (max-width: 768px) {
    grid-template-rows: minmax(150px, 220px) 1fr minmax(150px, 220px);
    gap: 6px;
    padding: 6px;
  }
}

.workspace-left,
.workspace-center,
.workspace-right {
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-radius: 12px;
  overflow: hidden;
}

.panel-header-mini {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: var(--color-surface-elevated);
  border-bottom: 1px solid var(--color-border);
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
  flex-shrink: 0;
  
  svg {
    color: var(--color-primary);
  }
}

.workspace-left {
  max-width: 100%;
  
  :deep(.data-inbox) {
    flex: 1;
    min-height: 0;
    border-radius: 0;
    background: transparent;
  }
}

.workspace-center {
  min-width: 0;
  flex: 1;
}

.workspace-right {
  max-width: 100%;
}
</style>
