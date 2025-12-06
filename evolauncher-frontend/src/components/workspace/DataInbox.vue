<script setup lang="ts">
/**
 * DataInbox Component
 * 
 * 左侧数据流面板 - 显示 Incoming、Pending、Library 三个分类的图像列表
 * 支持动画和交互
 */

import { computed, ref } from 'vue'
import { Icon } from '@iconify/vue'
import { useMissionStore } from '@/store/mission'
import type { DataStreamCategory, ImageTask } from '@/api/types'

const missionStore = useMissionStore()

// 当前选中的分类
const activeCategory = ref<DataStreamCategory>('incoming')

// 分类配置
const categories: Array<{ key: DataStreamCategory; label: string; icon: string }> = [
  { key: 'incoming', label: '新到达', icon: 'ph:arrow-down-circle' },
  { key: 'pending', label: '待确认', icon: 'ph:clock' },
  { key: 'library', label: '已归档', icon: 'ph:archive' }
]

// 当前分类的图像列表
const currentImages = computed(() => {
  return missionStore.getImageStreamByCategory(activeCategory.value)
})

// 选择图像
const handleImageClick = (image: ImageTask) => {
  missionStore.selectImage(image.id)
}

// 获取置信度颜色
const getConfidenceColor = (confidence: number) => {
  if (confidence >= 0.8) return 'text-emerald-500'
  if (confidence >= 0.6) return 'text-yellow-500'
  return 'text-orange-500'
}

// 获取置信度边框颜色
const getConfidenceBorderColor = (confidence: number) => {
  if (confidence >= 0.8) return 'border-emerald-500'
  if (confidence >= 0.6) return 'border-yellow-500'
  return 'border-orange-500'
}

// 获取来源标签颜色
const getSourceColor = (source: ImageTask['source']) => {
  switch (source) {
    case 'crawler':
      return 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30'
    case 'agent_recommended':
      return 'bg-purple-500/20 text-purple-400 border-purple-500/30'
    case 'manual':
      return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
    default:
      return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
  }
}
</script>

<template>
  <div class="data-inbox">
    <!-- 优化后的分类标签 - 更紧凑的统计面板 -->
    <div class="category-tabs">
      <div
        v-for="category in categories"
        :key="category.key"
        @click="activeCategory = category.key"
        :class="[
          'category-tab-compact',
          { 'active': activeCategory === category.key }
        ]"
      >
        <span class="tab-label">{{ category.label }}</span>
        <span class="tab-count">{{ missionStore.streamStats[category.key] }}</span>
      </div>
    </div>

    <!-- 图像列表 -->
    <div class="image-list">
      <div
        v-for="image in currentImages"
        :key="image.id"
        @click="handleImageClick(image)"
        :class="[
          'image-item',
          getConfidenceBorderColor(image.confidence),
          { 'active': missionStore.currentImage?.id === image.id }
        ]"
      >
        <!-- 缩略图 -->
        <div class="image-thumbnail">
          <img
            :src="image.thumbnailUrl || image.url"
            :alt="`Image ${image.id}`"
            class="thumbnail-image"
          />
          
          <!-- 置信度指示器 -->
          <div class="confidence-badge" :class="getConfidenceColor(image.confidence)">
            {{ Math.round(image.confidence * 100) }}%
          </div>
          
          <!-- 来源标签 -->
          <div class="source-badge" :class="getSourceColor(image.source)">
            <Icon
              :icon="image.source === 'crawler' ? 'ph:globe' : 
                     image.source === 'agent_recommended' ? 'ph:robot' : 
                     'ph:hand'"
              :width="12"
            />
          </div>
        </div>

        <!-- 图像信息 -->
        <div class="image-info">
          <div class="image-id">{{ image.id }}</div>
          <div class="image-meta">
            <span class="bbox-count">
              <Icon icon="ph:square" :width="14" />
              {{ image.boundingBoxes.length }}
            </span>
            <span class="image-time">
              {{ new Date(image.createdAt).toLocaleTimeString() }}
            </span>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="currentImages.length === 0" class="empty-state">
        <Icon icon="ph:image" :width="48" />
        <p>暂无图像</p>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.data-inbox {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
  border-radius: 16px;
  overflow: hidden;
}

.category-tabs {
  display: flex;
  gap: 6px;
  padding: 10px;
  background: var(--color-surface-elevated);
  border-bottom: 1px solid var(--color-border);
}

.category-tab-compact {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  padding: 8px 6px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: transparent;
  border: 2px solid transparent;
  
  .tab-label {
    font-size: 11px;
    font-weight: 500;
    color: var(--color-text-tertiary);
    white-space: nowrap;
  }
  
  .tab-count {
    font-size: 16px;
    font-weight: 700;
    color: var(--color-text-secondary);
  }
  
  &:hover {
    background: rgba(74, 105, 255, 0.05);
    border-color: rgba(74, 105, 255, 0.2);
    
    .tab-label {
      color: var(--color-text-secondary);
    }
    
    .tab-count {
      color: var(--color-primary);
    }
  }
  
  &.active {
    background: linear-gradient(135deg, rgba(74, 105, 255, 0.1), rgba(138, 43, 226, 0.1));
    border-color: rgba(74, 105, 255, 0.3);
    
    .tab-label {
      color: var(--color-primary);
      font-weight: 600;
    }
    
    .tab-count {
      color: var(--color-primary);
      font-size: 18px;
    }
  }
}

.category-count {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  background: rgba(74, 105, 255, 0.1);
  color: var(--color-primary);
  font-weight: 600;
}

.image-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  @include custom-scrollbar;
}

.image-item {
  position: relative;
  border: 2px solid var(--color-border);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: var(--color-surface-elevated);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    border-color: var(--color-primary);
  }
  
  &.active {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgba(74, 105, 255, 0.2);
  }
  
  &.border-emerald-500 {
    border-color: #10b981;
  }
  
  &.border-yellow-500 {
    border-color: #eab308;
  }
  
  &.border-orange-500 {
    border-color: #f97316;
  }
}

.image-thumbnail {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: var(--color-bg);
}

.thumbnail-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
  
  .image-item:hover & {
    transform: scale(1.05);
  }
}

.confidence-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  color: white;
}

.source-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 4px 6px;
  border-radius: 6px;
  font-size: 10px;
  border: 1px solid;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-info {
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.image-id {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-primary);
  font-family: 'Monaco', 'Courier New', monospace;
}

.image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.bbox-count {
  display: flex;
  align-items: center;
  gap: 4px;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--color-text-tertiary);
  padding: 40px 20px;
  
  p {
    margin: 0;
    font-size: 14px;
  }
}
</style>


