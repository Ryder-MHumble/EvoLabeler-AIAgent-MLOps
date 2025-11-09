<script setup lang="ts">
/**
 * 项目创建向导 - 现代化设计
 * 
 * 设计理念：
 * - 大尺寸沉浸式体验
 * - 渐变背景和玻璃态效果
 * - 流畅的动画过渡
 * - 现代化的进度指示器
 */

import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Icon } from '@iconify/vue'
import { ElMessage } from 'element-plus'
import gsap from 'gsap'

const { t } = useI18n()

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'created': [project: any]
}>()

// 当前步骤（0-3）
const currentStep = ref(0)
const wizardContent = ref<HTMLElement | null>(null)

// 表单数据
const formData = ref({
  // 步骤1: 基础信息
  name: '',
  description: '',
  
  // 步骤2: 数据准备
  uploadedFiles: [] as File[],
  
  // 步骤3: 模型配置
  modelSeries: 'tda-yolo', // 默认TDA-YOLO
  modelSize: 'small',
  customWeights: null as File | null,
  
  // 步骤4: 高级设置
  batchSize: 16,
  learningRate: 0.001,
  maxIterations: 100
})

// 模型系列选项
const modelSeriesOptions = [
  { value: 'tda-yolo', label: 'TDA-YOLO 系列', badge: '推荐', icon: 'ph:star-fill' },
  { value: 'yolov5', label: 'YOLOv5 系列', icon: 'ph:cube' },
  { value: 'yolov6', label: 'YOLOv6 系列', icon: 'ph:cube' },
  { value: 'yolov7', label: 'YOLOv7 系列', icon: 'ph:cube' },
  { value: 'yolov8', label: 'YOLOv8 系列', icon: 'ph:cube' },
  { value: 'yolov9', label: 'YOLOv9 系列', icon: 'ph:cube' },
  { value: 'yolov10', label: 'YOLOv10 系列', icon: 'ph:cube' },
  { value: 'yolo11', label: 'YOLO11 系列', icon: 'ph:cube' }
]

// 模型规模选项
const modelSizeOptions = [
  { value: 'nano', label: 'Nano', desc: '超轻量 · 快速推理', icon: 'ph:feather' },
  { value: 'small', label: 'Small', desc: '轻量级 · 性能平衡', icon: 'ph:lightning' },
  { value: 'medium', label: 'Medium', desc: '中等 · 精度优先', icon: 'ph:chart-line-up' },
  { value: 'large', label: 'Large', desc: '高精度 · 资源充足', icon: 'ph:trophy' },
  { value: 'xlarge', label: 'XLarge', desc: '超高精度 · 专业级', icon: 'ph:crown' }
]

// 步骤配置
const steps = [
  { title: '基础信息', subtitle: '数据准备', icon: 'ph:info', desc: '项目名称与描述' },
  { title: '上传数据', subtitle: '模型配置', icon: 'ph:database', desc: '训练数据集' },
  { title: '模型选择', subtitle: '确认创建', icon: 'ph:brain', desc: 'YOLO系列模型' },
  { title: '完成创建', subtitle: '', icon: 'ph:check-circle', desc: '配置确认' }
]

// 文件上传引用
const fileInputRef = ref<HTMLInputElement | null>(null)
const weightsInputRef = ref<HTMLInputElement | null>(null)

// 当前步骤是否可以进入下一步
const canProceed = computed(() => {
  switch (currentStep.value) {
    case 0:
      return formData.value.name.trim().length > 0
    case 1:
      return formData.value.uploadedFiles.length > 0
    case 2:
      return true
    case 3:
      return true
    default:
      return false
  }
})

// 是否是最后一步
const isLastStep = computed(() => currentStep.value === steps.length - 1)

// 进度百分比
const progressPercent = computed(() => {
  return ((currentStep.value + 1) / steps.length) * 100
})

// 创建状态
const isCreating = ref(false)

// 切换步骤（带动画）
const goToStep = (step: number) => {
  if (step < 0 || step >= steps.length) return
  
  const container = wizardContent.value
  if (!container) {
    currentStep.value = step
    return
  }
  
  const direction = step > currentStep.value ? -1 : 1
  
  gsap.to(container, {
    x: direction * 50,
    opacity: 0,
    duration: 0.3,
    ease: 'power2.in',
    onComplete: () => {
      currentStep.value = step
      gsap.fromTo(container,
        { x: -direction * 50, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.3, ease: 'power2.out' }
      )
    }
  })
}

// 下一步
const nextStep = () => {
  if (!canProceed.value) {
    ElMessage.warning('请完成当前步骤的必填项')
    return
  }
  
  if (isLastStep.value) {
    createProject()
  } else {
    goToStep(currentStep.value + 1)
  }
}

// 上一步
const previousStep = () => {
  goToStep(currentStep.value - 1)
}

// 文件上传处理
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    formData.value.uploadedFiles = Array.from(target.files)
  }
}

const triggerFileUpload = () => {
  fileInputRef.value?.click()
}

const removeFile = (index: number) => {
  formData.value.uploadedFiles.splice(index, 1)
}

// 权重文件处理
const handleWeightsSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    formData.value.customWeights = target.files[0]
  }
}

const triggerWeightsUpload = () => {
  weightsInputRef.value?.click()
}

const removeWeights = () => {
  formData.value.customWeights = null
  if (weightsInputRef.value) {
    weightsInputRef.value.value = ''
  }
}

// 创建项目
const createProject = async () => {
  isCreating.value = true
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    const project = {
      id: `proj-${Date.now()}`,
      name: formData.value.name,
      description: formData.value.description,
      status: 'idle',
      imageCount: formData.value.uploadedFiles.length,
      accuracy: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      thumbnailUrl: `https://picsum.photos/seed/${Date.now()}/400/300`,
      modelSeries: formData.value.modelSeries,
      modelSize: formData.value.modelSize
    }
    
    emit('created', project)
    emit('update:visible', false)
    
    // 重置表单
    resetForm()
  } catch (error) {
    console.error('Failed to create project:', error)
    ElMessage.error('项目创建失败')
  } finally {
    isCreating.value = false
  }
}

// 重置表单
const resetForm = () => {
  formData.value = {
    name: '',
    description: '',
    uploadedFiles: [],
    modelSeries: 'tda-yolo',
    modelSize: 'small',
    customWeights: null,
    batchSize: 16,
    learningRate: 0.001,
    maxIterations: 100
  }
  currentStep.value = 0
}

// 关闭对话框
const handleClose = () => {
  if (!isCreating.value) {
    emit('update:visible', false)
    setTimeout(resetForm, 300)
  }
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="emit('update:visible', $event)"
    @close="handleClose"
    :close-on-click-modal="false"
    width="1200px"
    class="wizard-dialog"
    center
    append-to-body
    lock-scroll
    :close-on-press-escape="!isCreating"
  >
    <!-- 自定义header -->
    <template #header>
      <div class="wizard-header-custom">
        <div class="header-bg"></div>
        <div class="header-content">
          <div class="header-icon">
            <Icon icon="ph:sparkle" :width="32" />
          </div>
          <div class="header-text">
            <h2 class="header-title">创建进化项目</h2>
            <p class="header-subtitle">通过智能引导快速配置您的主动学习项目</p>
          </div>
        </div>
        
        <!-- 简洁进度指示器 -->
        <div class="modern-progress">
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: `${progressPercent}%` }"></div>
          </div>
          <div class="progress-steps">
            <div
              v-for="(step, index) in steps"
              :key="index"
              class="progress-step"
              :class="{ active: index === currentStep, completed: index < currentStep }"
            >
              <div class="step-circle">
                <Icon v-if="index < currentStep" icon="ph:check-bold" :width="16" />
                <span v-else class="step-number">{{ index + 1 }}</span>
              </div>
              <span class="step-title">{{ step.title }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
    
    <!-- 内容区域 -->
    <div class="wizard-body" ref="wizardContent">
      <!-- 步骤1: 基础信息 -->
      <div v-show="currentStep === 0" class="step-content">
        <div class="content-header">
          <Icon icon="ph:text-aa" :width="48" class="content-icon" />
          <h3 class="content-title">项目基础信息</h3>
          <p class="content-desc">为您的项目取一个有意义的名称，并简要描述项目目标</p>
        </div>
        
        <el-form label-position="top" class="wizard-form">
          <el-form-item label="项目名称" required>
            <el-input
              v-model="formData.name"
              placeholder="例如：海上风力发电场智能监测"
              size="large"
              clearable
              maxlength="50"
              show-word-limit
            >
              <template #prefix>
                <Icon icon="ph:folder" :width="20" />
              </template>
            </el-input>
          </el-form-item>
          
          <el-form-item label="项目描述（可选）">
            <el-input
              v-model="formData.description"
              type="textarea"
              :rows="5"
              placeholder="描述项目的应用场景、数据类型和预期目标..."
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 步骤2: 数据准备 -->
      <div v-show="currentStep === 1" class="step-content">
        <div class="content-header">
          <Icon icon="ph:images" :width="48" class="content-icon" />
          <h3 class="content-title">上传训练数据</h3>
          <p class="content-desc">选择本地图像文件作为初始训练数据集</p>
        </div>
        
        <div class="upload-zone" @click="triggerFileUpload">
          <input
            ref="fileInputRef"
            type="file"
            multiple
            accept="image/*"
            style="display: none"
            @change="handleFileSelect"
          />
          <div class="upload-icon-wrapper">
            <Icon icon="ph:cloud-arrow-up" :width="80" class="upload-icon" />
          </div>
          <h4 class="upload-title">拖拽文件到这里或点击上传</h4>
          <p class="upload-hint">支持 JPG、PNG、BMP 等常见图像格式，支持批量上传</p>
          <div v-if="formData.uploadedFiles.length > 0" class="upload-status">
            <Icon icon="ph:check-circle-fill" :width="24" />
            <span>已选择 <strong>{{ formData.uploadedFiles.length }}</strong> 个文件</span>
          </div>
        </div>
        
        <!-- 文件列表 -->
        <div v-if="formData.uploadedFiles.length > 0" class="file-grid">
          <div
            v-for="(file, index) in formData.uploadedFiles.slice(0, 12)"
            :key="index"
            class="file-card"
          >
            <div class="file-preview">
              <Icon icon="ph:file-image" :width="32" />
            </div>
            <div class="file-info">
              <span class="file-name">{{ file.name }}</span>
              <span class="file-size">{{ (file.size / 1024).toFixed(1) }} KB</span>
            </div>
            <el-button 
              type="danger" 
              text 
              circle 
              size="small" 
              @click.stop="removeFile(index)"
            >
              <Icon icon="ph:x" :width="18" />
            </el-button>
          </div>
          <div v-if="formData.uploadedFiles.length > 12" class="file-more">
            <Icon icon="ph:dots-three" :width="24" />
            <span>还有 {{ formData.uploadedFiles.length - 12 }} 个文件</span>
          </div>
        </div>
      </div>
      
      <!-- 步骤3: 模型配置 -->
      <div v-show="currentStep === 2" class="step-content">
        <div class="content-header">
          <Icon icon="ph:brain" :width="48" class="content-icon" />
          <h3 class="content-title">选择检测模型</h3>
          <p class="content-desc">根据您的需求选择合适的YOLO系列模型</p>
        </div>
        
        <!-- 模型系列选择 -->
        <div class="section-block">
          <div class="section-header">
            <Icon icon="ph:stack" :width="24" />
            <span>模型系列</span>
          </div>
          <div class="model-series-grid">
            <div
              v-for="option in modelSeriesOptions"
              :key="option.value"
              class="series-card"
              :class="{ selected: formData.modelSeries === option.value }"
              @click="formData.modelSeries = option.value"
            >
              <Icon :icon="option.icon" :width="36" class="series-icon" />
              <span class="series-label">{{ option.label }}</span>
              <el-tag v-if="option.badge" type="warning" size="small" effect="dark" class="series-badge">
                <Icon icon="ph:star-fill" :width="12" class="mr-1" />
                {{ option.badge }}
              </el-tag>
              <Icon v-if="formData.modelSeries === option.value" icon="ph:check-circle-fill" :width="24" class="series-check" />
            </div>
          </div>
        </div>
        
        <!-- 模型规模选择 -->
        <div class="section-block">
          <div class="section-header">
            <Icon icon="ph:scales" :width="24" />
            <span>模型规模</span>
          </div>
          <div class="size-list">
            <div
              v-for="size in modelSizeOptions"
              :key="size.value"
              class="size-item"
              :class="{ selected: formData.modelSize === size.value }"
              @click="formData.modelSize = size.value"
            >
              <Icon :icon="size.icon" :width="28" class="size-icon" />
              <div class="size-content">
                <span class="size-label">{{ size.label }}</span>
                <span class="size-desc">{{ size.desc }}</span>
              </div>
              <Icon v-if="formData.modelSize === size.value" icon="ph:check-circle-fill" :width="24" class="size-check" />
            </div>
          </div>
        </div>
        
        <!-- 自定义权重 -->
        <div class="section-block">
          <div class="section-header">
            <Icon icon="ph:file-arrow-up" :width="24" />
            <span>自定义权重（可选）</span>
          </div>
          <div class="weights-upload">
            <el-button
              @click="triggerWeightsUpload"
              size="large"
              style="width: 100%;"
            >
              <input
                ref="weightsInputRef"
                type="file"
                accept=".pt,.pth"
                style="display: none"
                @change="handleWeightsSelect"
              />
              <Icon icon="ph:upload" :width="20" class="mr-2" />
              {{ formData.customWeights ? formData.customWeights.name : '上传预训练权重文件（.pt / .pth）' }}
            </el-button>
            <el-button
              v-if="formData.customWeights"
              type="danger"
              text
              @click="removeWeights"
            >
              <Icon icon="ph:trash" :width="16" class="mr-1" />
              移除权重文件
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 步骤4: 确认创建 -->
      <div v-show="currentStep === 3" class="step-content">
        <div class="content-header">
          <Icon icon="ph:check-square" :width="48" class="content-icon" />
          <h3 class="content-title">确认项目配置</h3>
          <p class="content-desc">请检查以下配置信息，确认无误后即可创建项目</p>
        </div>
        
        <div class="summary-grid">
          <div class="summary-card">
            <div class="summary-header">
              <Icon icon="ph:info-fill" :width="24" />
              <span>基础信息</span>
            </div>
            <div class="summary-body">
              <div class="summary-row">
                <span class="label">项目名称</span>
                <span class="value">{{ formData.name }}</span>
              </div>
              <div v-if="formData.description" class="summary-row">
                <span class="label">项目描述</span>
                <span class="value">{{ formData.description }}</span>
              </div>
            </div>
          </div>
          
          <div class="summary-card">
            <div class="summary-header">
              <Icon icon="ph:database-fill" :width="24" />
              <span>训练数据</span>
            </div>
            <div class="summary-body">
              <div class="summary-row">
                <span class="label">图像数量</span>
                <span class="value highlight">{{ formData.uploadedFiles.length }} 张</span>
              </div>
              <div class="summary-row">
                <span class="label">总大小</span>
                <span class="value">
                  {{ (formData.uploadedFiles.reduce((sum, f) => sum + f.size, 0) / 1024 / 1024).toFixed(2) }} MB
                </span>
              </div>
            </div>
          </div>
          
          <div class="summary-card">
            <div class="summary-header">
              <Icon icon="ph:brain-fill" :width="24" />
              <span>模型配置</span>
            </div>
            <div class="summary-body">
              <div class="summary-row">
                <span class="label">模型系列</span>
                <span class="value">
                  {{ modelSeriesOptions.find(o => o.value === formData.modelSeries)?.label }}
                </span>
              </div>
              <div class="summary-row">
                <span class="label">模型规模</span>
                <span class="value">
                  {{ modelSizeOptions.find(o => o.value === formData.modelSize)?.label }}
                </span>
              </div>
              <div v-if="formData.customWeights" class="summary-row">
                <span class="label">自定义权重</span>
                <span class="value">{{ formData.customWeights.name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 底部操作栏 -->
    <template #footer>
      <div class="wizard-footer">
        <el-button
          v-if="currentStep > 0"
          @click="previousStep"
          size="large"
          :disabled="isCreating"
        >
          <Icon icon="ph:arrow-left-bold" :width="20" class="mr-2" />
          上一步
        </el-button>
        <el-button
          v-else
          @click="handleClose"
          size="large"
        >
          取消
        </el-button>
        
        <div class="footer-spacer"></div>
        
        <el-button
          type="primary"
          @click="nextStep"
          size="large"
          :disabled="!canProceed"
          :loading="isCreating"
        >
          {{ isLastStep ? (isCreating ? '创建中...' : '创建项目') : '下一步' }}
          <Icon v-if="!isLastStep && !isCreating" icon="ph:arrow-right-bold" :width="20" class="ml-2" />
          <Icon v-else-if="!isCreating" icon="ph:rocket-launch" :width="20" class="ml-2" />
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped lang="scss">
.wizard-dialog {
  :deep(.el-dialog) {
    border-radius: 24px;
    overflow: hidden;
    background: var(--color-surface);
    box-shadow: 0 24px 64px rgba(0, 0, 0, 0.4);
  }
  
  :deep(.el-dialog__header) {
    padding: 0;
    margin: 0;
  }
  
  :deep(.el-dialog__body) {
    padding: $spacing-3xl;
    min-height: 520px;
    max-height: calc(100vh - 400px);
    overflow-y: auto;
    @include custom-scrollbar;
  }
  
  :deep(.el-dialog__footer) {
    padding: $spacing-xl $spacing-3xl $spacing-2xl;
    border-top: 1px solid var(--color-border);
    background: var(--color-surface-elevated);
  }
  
  @media (max-width: 1280px) {
    :deep(.el-dialog) {
      width: 95vw !important;
    }
  }
  
  @media (max-width: 768px) {
    :deep(.el-dialog__body) {
      padding: $spacing-xl;
      min-height: 400px;
    }
    
    :deep(.el-dialog__footer) {
      padding: $spacing-lg $spacing-xl;
    }
  }
}

// 自定义Header
.wizard-header-custom {
  position: relative;
  padding: $spacing-2xl $spacing-3xl;
  overflow: hidden;
  background: linear-gradient(135deg, 
    rgba(74, 105, 255, 0.08) 0%, 
    rgba(138, 43, 226, 0.08) 100%
  );
}

.header-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at top right, 
    rgba(74, 105, 255, 0.15), 
    transparent 60%
  );
}

.header-content {
  position: relative;
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-xl;
}

.header-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #4A69FF, #7AA2F7);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 16px rgba(74, 105, 255, 0.3);
  flex-shrink: 0;
}

.header-text {
  flex: 1;
}

.header-title {
  font-size: $font-size-2xl;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
}

.header-subtitle {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  margin: 0;
}

// 简洁进度指示器
.modern-progress {
  position: relative;
}

.progress-track {
  position: relative;
  height: 4px;
  background: rgba(74, 105, 255, 0.15);
  border-radius: 2px;
  margin-bottom: $spacing-lg;
  overflow: hidden;
}

.progress-fill {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background: linear-gradient(90deg, #4A69FF 0%, #7AA2F7 100%);
  border-radius: 2px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 12px rgba(74, 105, 255, 0.5);
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  gap: $spacing-sm;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-sm;
  flex: 1;
  padding: $spacing-sm;
  border-radius: $radius-md;
  transition: all 0.3s ease;
  
  &.completed {
    .step-circle {
      background: var(--color-success);
      border-color: var(--color-success);
      color: white;
    }
    
    .step-title {
      color: var(--color-success);
    }
  }
  
  &.active {
    background: rgba(74, 105, 255, 0.05);
    
    .step-circle {
      background: var(--color-primary);
      border-color: var(--color-primary);
      color: white;
      box-shadow: 0 0 0 4px rgba(74, 105, 255, 0.2);
      transform: scale(1.1);
    }
    
    .step-title {
      color: var(--color-primary);
      font-weight: $font-weight-bold;
    }
  }
}

.step-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid var(--color-border);
  background: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.step-number {
  font-size: $font-size-base;
  font-weight: $font-weight-bold;
  color: var(--color-text-tertiary);
}

.step-title {
  font-size: $font-size-sm;
  font-weight: $font-weight-medium;
  color: var(--color-text-secondary);
  transition: all 0.3s ease;
  text-align: center;
}

// 内容区域
.wizard-body {
  min-height: 480px;
}

.step-content {
  animation: fadeSlideIn 0.4s ease;
}

@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.content-header {
  text-align: center;
  margin-bottom: $spacing-3xl;
}

.content-icon {
  display: inline-block;
  padding: $spacing-lg;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(74, 105, 255, 0.1), rgba(138, 43, 226, 0.1));
  color: var(--color-primary);
  margin-bottom: $spacing-lg;
}

.content-title {
  font-size: $font-size-2xl;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  margin: 0 0 $spacing-sm 0;
}

.content-desc {
  font-size: $font-size-base;
  color: var(--color-text-secondary);
  margin: 0;
}

// 表单样式
.wizard-form {
  max-width: 720px;
  margin: 0 auto;
  
  :deep(.el-form-item__label) {
    font-weight: $font-weight-semibold;
    color: var(--color-text-primary);
  }
  
  :deep(.el-input__inner) {
    font-size: $font-size-base;
  }
}

// 上传区域
.upload-zone {
  border: 3px dashed var(--color-border);
  border-radius: 20px;
  padding: $spacing-3xl;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--color-surface-elevated);
  margin-bottom: $spacing-xl;
  
  &:hover {
    border-color: var(--color-primary);
    background: rgba(74, 105, 255, 0.05);
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(74, 105, 255, 0.15);
  }
}

.upload-icon-wrapper {
  display: inline-block;
  padding: $spacing-xl;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(74, 105, 255, 0.15), rgba(138, 43, 226, 0.15));
  margin-bottom: $spacing-lg;
}

.upload-icon {
  color: var(--color-primary);
  display: block;
}

.upload-title {
  font-size: $font-size-xl;
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
  margin: 0 0 $spacing-sm 0;
}

.upload-hint {
  font-size: $font-size-sm;
  color: var(--color-text-tertiary);
  margin: 0;
}

.upload-status {
  display: inline-flex;
  align-items: center;
  gap: $spacing-sm;
  margin-top: $spacing-lg;
  padding: $spacing-sm $spacing-lg;
  background: rgba(16, 185, 129, 0.1);
  border-radius: $radius-full;
  color: var(--color-success);
  font-size: $font-size-base;
  font-weight: $font-weight-medium;
}

// 文件网格
.file-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: $spacing-md;
  max-height: 320px;
  overflow-y: auto;
  @include custom-scrollbar;
}

.file-card {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-md;
  background: var(--color-surface-elevated);
  border-radius: $radius-lg;
  border: 1px solid var(--color-border);
  transition: all 0.3s ease;
  
  &:hover {
    border-color: var(--color-primary);
    transform: translateY(-2px);
    box-shadow: $shadow-md;
  }
}

.file-preview {
  width: 48px;
  height: 48px;
  border-radius: $radius-md;
  background: rgba(74, 105, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-name {
  font-size: $font-size-sm;
  font-weight: $font-weight-medium;
  color: var(--color-text-primary);
  @include truncate;
}

.file-size {
  font-size: $font-size-xs;
  color: var(--color-text-tertiary);
}

.file-more {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
  padding: $spacing-lg;
  background: var(--color-surface-elevated);
  border-radius: $radius-lg;
  color: var(--color-text-secondary);
  font-size: $font-size-sm;
}

// Section Block
.section-block {
  margin-bottom: $spacing-2xl;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.section-header {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  font-size: $font-size-lg;
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
  margin-bottom: $spacing-lg;
}

// 模型系列网格
.model-series-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: $spacing-lg;
  
  @media (max-width: 1024px) {
    grid-template-columns: repeat(3, 1fr);
  }
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.series-card {
  position: relative;
  padding: $spacing-xl;
  border: 2px solid var(--color-border);
  border-radius: $radius-xl;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--color-surface);
  
  &:hover {
    border-color: var(--color-primary);
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(74, 105, 255, 0.2);
  }
  
  &.selected {
    border-color: var(--color-primary);
    background: rgba(74, 105, 255, 0.08);
    box-shadow: 0 0 24px rgba(74, 105, 255, 0.25);
  }
}

.series-icon {
  display: inline-block;
  padding: $spacing-md;
  border-radius: $radius-lg;
  background: rgba(74, 105, 255, 0.1);
  color: var(--color-primary);
  margin-bottom: $spacing-md;
}

.series-label {
  display: block;
  font-size: $font-size-base;
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
}

.series-badge {
  position: absolute;
  top: $spacing-sm;
  right: $spacing-sm;
}

.series-check {
  position: absolute;
  top: $spacing-sm;
  left: $spacing-sm;
  color: var(--color-success);
}

// 规模列表
.size-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.size-item {
  display: flex;
  align-items: center;
  gap: $spacing-lg;
  padding: $spacing-lg $spacing-xl;
  border: 2px solid var(--color-border);
  border-radius: $radius-xl;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--color-surface);
  
  &:hover {
    border-color: var(--color-primary);
    transform: translateX(8px);
    box-shadow: $shadow-md;
  }
  
  &.selected {
    border-color: var(--color-primary);
    background: rgba(74, 105, 255, 0.08);
  }
}

.size-icon {
  padding: $spacing-md;
  border-radius: $radius-lg;
  background: rgba(74, 105, 255, 0.1);
  color: var(--color-primary);
  flex-shrink: 0;
}

.size-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.size-label {
  font-size: $font-size-lg;
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
}

.size-desc {
  font-size: $font-size-sm;
  color: var(--color-text-tertiary);
}

.size-check {
  color: var(--color-success);
  flex-shrink: 0;
}

// 权重上传
.weights-upload {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

// 摘要网格
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: $spacing-xl;
}

.summary-card {
  padding: $spacing-xl;
  background: var(--color-surface-elevated);
  border-radius: $radius-xl;
  border: 2px solid var(--color-border);
  transition: all 0.3s ease;
  
  &:hover {
    border-color: var(--color-primary);
    transform: translateY(-4px);
    box-shadow: $shadow-lg;
  }
}

.summary-header {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  font-size: $font-size-lg;
  font-weight: $font-weight-bold;
  color: var(--color-primary);
  margin-bottom: $spacing-lg;
  padding-bottom: $spacing-md;
  border-bottom: 2px solid var(--color-border);
}

.summary-body {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: $spacing-md;
  
  .label {
    font-size: $font-size-sm;
    color: var(--color-text-tertiary);
    flex-shrink: 0;
  }
  
  .value {
    font-size: $font-size-base;
    font-weight: $font-weight-medium;
    color: var(--color-text-primary);
    text-align: right;
    
    &.highlight {
      color: var(--color-primary);
      font-weight: $font-weight-bold;
      font-size: $font-size-lg;
    }
  }
}

// 底部操作栏
.wizard-footer {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.footer-spacer {
  flex: 1;
}

// 工具类
.mr-1 {
  margin-right: 4px;
}

.mr-2 {
  margin-right: $spacing-xs;
}

.ml-2 {
  margin-left: $spacing-xs;
}
</style>
