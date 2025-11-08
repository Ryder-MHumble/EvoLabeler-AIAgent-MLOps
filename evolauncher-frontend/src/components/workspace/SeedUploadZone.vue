<script setup lang="ts">
/**
 * Seed Upload Zone Component
 * 
 * 设计理念（基于UserMap.md）：
 * - 将上传过程游戏化，提供即时智能反馈
 * - 拖拽上传作为"点火"动作，触发整个进化链路
 * - 美观的动画和状态提示
 * 
 * 交互流程：
 * 1. 用户拖入ZIP文件
 * 2. 显示解析进度
 * 3. 解析完成后显示确认动画
 * 4. 自动触发进化引擎（无需额外点击）
 */

import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Icon } from '@iconify/vue'
import { ElMessage, ElNotification } from 'element-plus'
import gsap from 'gsap'

interface Props {
  projectId: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'upload-success': [files: File[]]
  'evolution-start': []
}>()

const { t } = useI18n()

const isDragging = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadedFiles = ref<File[]>([])

// 允许的文件类型
const ACCEPTED_TYPES = ['application/zip', 'application/x-zip-compressed']
const MAX_FILE_SIZE = 500 * 1024 * 1024 // 500MB

// 拖拽事件处理
const handleDragEnter = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = true
}

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault()
  // 只在离开组件边界时取消拖拽状态
  if (e.target === e.currentTarget) {
    isDragging.value = false
  }
}

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
}

const handleDrop = async (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false
  
  const files = Array.from(e.dataTransfer?.files || [])
  await processFiles(files)
}

// 点击上传
const fileInput = ref<HTMLInputElement | null>(null)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileInput = async (e: Event) => {
  const target = e.target as HTMLInputElement
  const files = Array.from(target.files || [])
  await processFiles(files)
}

// 文件处理逻辑
const processFiles = async (files: File[]) => {
  try {
    // 验证文件
    if (files.length === 0) {
      ElMessage.warning(t('upload.noFile'))
      return
    }
    
    if (files.length > 1) {
      ElMessage.warning(t('upload.singleFileOnly'))
      return
    }
    
    const file = files[0]
    
    // 验证文件类型
    if (!ACCEPTED_TYPES.includes(file.type) && !file.name.endsWith('.zip')) {
      ElMessage.error(t('upload.invalidType'))
      return
    }
    
    // 验证文件大小
    if (file.size > MAX_FILE_SIZE) {
      ElMessage.error(t('upload.fileTooLarge'))
      return
    }
    
    // 开始上传模拟
    isUploading.value = true
    uploadProgress.value = 0
    uploadedFiles.value = files
    
    // 模拟上传进度（实际应用中应该是真实的上传请求）
    await simulateUpload()
    
    // 上传成功动画
    await showSuccessAnimation()
    
    // 触发事件
    emit('upload-success', files)
    
    // 延迟后自动启动进化引擎
    setTimeout(() => {
      emit('evolution-start')
    }, 1000)
    
  } catch (error) {
    console.error('File processing error:', error)
    ElMessage.error(t('errors.fileUploadFailed'))
    isUploading.value = false
  }
}

// 模拟上传进度
const simulateUpload = (): Promise<void> => {
  return new Promise((resolve) => {
    const duration = 2000 // 2秒
    const interval = 50
    const step = (interval / duration) * 100
    
    const timer = setInterval(() => {
      uploadProgress.value += step
      
      if (uploadProgress.value >= 100) {
        uploadProgress.value = 100
        clearInterval(timer)
        resolve()
      }
    }, interval)
  })
}

// 成功动画
const showSuccessAnimation = async () => {
  const element = document.querySelector('.upload-zone')
  if (element) {
    await gsap.to(element, {
      scale: 1.05,
      duration: 0.3,
      ease: 'back.out',
      yoyo: true,
      repeat: 1
    })
  }
  
  ElNotification.success({
    title: t('upload.success'),
    message: t('upload.starting'),
    duration: 3000
  })
}
</script>

<template>
  <div
    class="seed-upload-zone"
    :class="{
      'is-dragging': isDragging,
      'is-uploading': isUploading
    }"
  >
    <div
      class="upload-zone"
      @dragenter="handleDragEnter"
      @dragleave="handleDragLeave"
      @dragover="handleDragOver"
      @drop="handleDrop"
      @click="triggerFileInput"
    >
      <!-- 上传图标和文本 -->
      <div v-if="!isUploading" class="upload-content">
        <div class="upload-icon-wrapper">
          <Icon
            icon="ph:upload-simple"
            :width="64"
            class="upload-icon"
          />
        </div>
        
        <h3 class="upload-title">
          {{ $t('upload.title') }}
        </h3>
        
        <p class="upload-description">
          {{ $t('upload.description') }}
        </p>
        
        <div class="upload-hint">
          <Icon icon="ph:hand-fist" :width="20" />
          <span>{{ $t('upload.dragHere') }}</span>
          <span class="text-muted">{{ $t('upload.orClick') }}</span>
        </div>
      </div>
      
      <!-- 上传进度 -->
      <div v-else class="upload-progress">
        <div class="progress-icon">
          <Icon
            icon="ph:spinner"
            :width="64"
            class="spinning"
          />
        </div>
        
        <h3 class="progress-title">
          {{ $t('upload.parsing') }}
        </h3>
        
        <el-progress
          :percentage="uploadProgress"
          :show-text="false"
          :stroke-width="6"
          class="progress-bar"
        />
        
        <p class="progress-text">
          {{ uploadProgress.toFixed(0) }}%
        </p>
      </div>
      
      <!-- 隐藏的文件输入 -->
      <input
        ref="fileInput"
        type="file"
        accept=".zip,application/zip"
        style="display: none"
        @change="handleFileInput"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.seed-upload-zone {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $spacing-3xl;
}

.upload-zone {
  width: 100%;
  max-width: 600px;
  padding: $spacing-3xl;
  border: 2px dashed var(--color-border);
  border-radius: $radius-2xl;
  background: var(--color-surface);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
  
  &:hover {
    border-color: var(--color-primary);
    background: var(--color-surface-elevated);
    transform: translateY(-2px);
    box-shadow: $shadow-lg;
  }
  
  .is-dragging & {
    border-color: var(--color-primary);
    background: var(--color-primary-light);
    opacity: 0.1;
    transform: scale(1.02);
  }
  
  .is-uploading & {
    cursor: default;
    border-style: solid;
  }
}

// Upload Content
.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: $spacing-lg;
}

.upload-icon-wrapper {
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary-light), var(--color-primary));
  border-radius: 50%;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: inherit;
    opacity: 0.3;
    animation: pulse 2s ease-in-out infinite;
  }
}

.upload-icon {
  color: white;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.2));
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.1);
    opacity: 0;
  }
}

.upload-title {
  font-size: $font-size-2xl;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  margin: 0;
}

.upload-description {
  font-size: $font-size-base;
  color: var(--color-text-secondary);
  margin: 0;
  max-width: 400px;
  line-height: 1.6;
}

.upload-hint {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  font-size: $font-size-sm;
  color: var(--color-text-tertiary);
  margin-top: $spacing-md;
  
  .text-muted {
    color: var(--color-text-tertiary);
    opacity: 0.7;
  }
}

// Upload Progress
.upload-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-lg;
}

.progress-icon {
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.progress-title {
  font-size: $font-size-xl;
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
  margin: 0;
}

.progress-bar {
  width: 100%;
  max-width: 400px;
}

.progress-text {
  font-size: $font-size-2xl;
  font-weight: $font-weight-bold;
  color: var(--color-primary);
  margin: 0;
}
</style>

