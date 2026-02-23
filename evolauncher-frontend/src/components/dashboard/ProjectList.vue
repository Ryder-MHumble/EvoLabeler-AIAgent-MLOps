<script setup lang="ts">
/**
 * ProjectList - 项目列表组件
 * 包含项目网格、加载状态、空状态
 */

import { Icon } from '@iconify/vue'
import LoadingSkeleton from '@/components/common/LoadingSkeleton.vue'
import ProjectCard from './ProjectCard.vue'
import type { Project } from '@/mock/projects'

defineProps<{
  projects: Project[]
  isLoading: boolean
}>()

const emit = defineEmits<{
  (e: 'create-project'): void
  (e: 'open-project', project: Project): void
}>()
</script>

<template>
  <div class="projects-column">
    <div class="section-header-modern">
      <div class="section-header-left">
        <div class="section-icon-badge">
          <Icon icon="ph:folder-open-fill" :width="20" />
        </div>
        <div>
          <h2 class="section-title-modern">我的项目</h2>
          <p class="section-desc-modern">
            {{ projects.length > 0 ? `共 ${projects.length} 个进化项目` : '开始创建您的第一个项目' }}
          </p>
        </div>
      </div>
      <el-button text @click="emit('create-project')">
        <Icon icon="ph:plus" :width="18" />
        <span>新建</span>
      </el-button>
    </div>
    
    <!-- Loading State -->
    <div v-if="isLoading" class="projects-list">
      <LoadingSkeleton v-for="i in 6" :key="`skeleton-${i}`" variant="card" height="280px" />
    </div>
    
    <!-- Projects Grid -->
    <div v-else-if="projects.length > 0" class="projects-list">
      <ProjectCard
        v-for="project in projects"
        :key="project.id"
        :project="project"
        @click="emit('open-project', project)"
      />
    </div>
    
    <!-- Empty State -->
    <div v-else class="empty-state-modern">
      <div class="empty-illustration">
        <Icon icon="ph:folder-open" :width="80" />
      </div>
      <h3 class="empty-title">{{ $t('dashboard.noProjects') }}</h3>
      <p class="empty-description">{{ $t('dashboard.noProjectsDesc') }}</p>
      <el-button type="primary" size="large" @click="emit('create-project')">
        <Icon icon="ph:plus-circle" :width="20" />
        <span>{{ $t('dashboard.createProject') }}</span>
      </el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.projects-column {
  min-width: 0;
}

.section-header-modern {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--color-border);
}

.section-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-icon-badge {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, #4A69FF, #7AA2F7);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 6px 16px rgba(74, 105, 255, 0.3);
}

.section-title-modern {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
  line-height: 1.2;
}

.section-desc-modern {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0;
}

.projects-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.empty-state-modern {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 32px;
  text-align: center;
  min-height: 400px;
  background: var(--color-surface-elevated);
  border-radius: 24px;
  border: 2px dashed var(--color-border);
}

.empty-illustration {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(74, 105, 255, 0.1), rgba(138, 43, 226, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  margin-bottom: 20px;
  
  .dark & {
    background: linear-gradient(135deg, rgba(96, 165, 250, 0.15), rgba(167, 139, 250, 0.15));
  }
}

.empty-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.empty-description {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: 20px;
  max-width: 400px;
}

.mt-4 {
  margin-top: 16px;
}
</style>

