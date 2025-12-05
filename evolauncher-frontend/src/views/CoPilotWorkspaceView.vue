<script setup lang="ts">
/**
 * CoPilot Workspace View
 * 
 * "任务指挥官" 工作区视图
 * 集成 DataInbox、SmartCanvas、AgentPanel 和 LiveTerminal
 */

import { onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMissionStore } from '@/store/mission'
import DataInbox from '@/components/workspace/DataInbox.vue'
import SmartCanvas from '@/components/workspace/SmartCanvas.vue'
import AgentPanel from '@/components/workspace/AgentPanel.vue'
import LiveTerminal from '@/components/workspace/LiveTerminal.vue'

const route = useRoute()
const missionStore = useMissionStore()

// 初始化
onMounted(async () => {
  // 加载任务列表
  await missionStore.loadMissions()
  
  // 如果有任务，选择第一个
  if (missionStore.missions.length > 0) {
    await missionStore.selectMission(missionStore.missions[0].id)
  }
})

onUnmounted(() => {
  // 清理
  missionStore.stopLogStream()
})
</script>

<template>
  <div class="copilot-workspace">
    <!-- 三列布局 -->
    <div class="workspace-layout">
      <!-- 左侧：数据流 -->
      <div class="workspace-left">
        <DataInbox />
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
  padding-bottom: 30px; // 为底部终端留出空间
  overflow: hidden;
}

.workspace-layout {
  flex: 1;
  display: grid;
  grid-template-columns: minmax(200px, 280px) minmax(400px, 1fr) minmax(250px, 320px);
  gap: 12px;
  padding: 12px;
  min-height: 0;
  overflow: hidden;
  
  // 中等屏幕：调整列宽
  @media (max-width: 1600px) {
    grid-template-columns: minmax(180px, 240px) minmax(350px, 1fr) minmax(220px, 280px);
    gap: 10px;
    padding: 10px;
  }
  
  // 小屏幕：堆叠布局
  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
    grid-template-rows: minmax(200px, 300px) 1fr minmax(200px, 300px);
    gap: 8px;
    padding: 8px;
    
    .workspace-left {
      grid-row: 1;
      min-height: 200px;
      max-height: 300px;
    }
    
    .workspace-center {
      grid-row: 2;
      min-height: 400px;
    }
    
    .workspace-right {
      grid-row: 3;
      min-height: 200px;
      max-height: 300px;
    }
  }
  
  // 超小屏幕
  @media (max-width: 768px) {
    grid-template-rows: minmax(150px, 250px) 1fr minmax(150px, 250px);
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

.workspace-left {
  // 左侧可调整宽度
  max-width: 100%;
}

.workspace-center {
  // 中间自适应
  min-width: 0;
  flex: 1;
}

.workspace-right {
  // 右侧可调整宽度
  max-width: 100%;
}
</style>


