<script setup lang="ts">
/**
 * 项目创建向导 - 完全重构版
 * 
 * 设计理念：
 * - 沉浸式全屏体验
 * - 流畅的动画过渡
 * - 现代化的UI设计
 * - 智能的弹窗定位
 * - 响应式布局
 */

import { ref, computed, watch, nextTick } from 'vue'
import { Icon } from '@iconify/vue'
import { ElMessage } from 'element-plus'
import gsap from 'gsap'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'created': [project: any]
}>()

// 当前步骤（0-3）
const currentStep = ref(0)
const dialogRef = ref<HTMLElement | null>(null)
const contentRef = ref<HTMLElement | null>(null)

// 表单数据
const formData = ref({
  name: '',
  description: '',
  uploadedFiles: [] as File[],
  modelSeries: 'tda-yolo',
  modelSize: 'small',
  customWeights: null as File | null
})

// 模型系列选项
const modelSeriesOptions = [
  { value: 'tda-yolo', label: 'TDA-YOLO', badge: '推荐', icon: 'ph:sparkle', color: '#FFD700' },
  { value: 'yolov5', label: 'YOLOv5', icon: 'ph:cube', color: '#4A69FF' },
  { value: 'yolov6', label: 'YOLOv6', icon: 'ph:cube', color: '#7AA2F7' },
  { value: 'yolov7', label: 'YOLOv7', icon: 'ph:cube', color: '#8B5CF6' },
  { value: 'yolov8', label: 'YOLOv8', icon: 'ph:cube', color: '#10B981' },
  { value: 'yolov9', label: 'YOLOv9', icon: 'ph:cube', color: '#F59E0B' },
  { value: 'yolov10', label: 'YOLOv10', icon: 'ph:cube', color: '#EF4444' },
  { value: 'yolo11', label: 'YOLO11', icon: 'ph:cube', color: '#EC4899' }
]

// 模型规模选项
const modelSizeOptions = [
  { value: 'nano', label: 'Nano', desc: '超轻量 · 快速推理', params: '1.9M' },
  { value: 'small', label: 'Small', desc: '轻量级 · 性能平衡', params: '9.2M' },
  { value: 'medium', label: 'Medium', desc: '中等 · 精度优先', params: '25.3M' },
  { value: 'large', label: 'Large', desc: '高精度 · 资源充足', params: '43.7M' },
  { value: 'xlarge', label: 'XLarge', desc: '超高精度 · 专业级', params: '68.2M' }
]

// 步骤配置
const steps = [
  { 
    title: '基础信息', 
    icon: 'ph:file-text', 
    desc: '项目名称与描述',
    color: '#4A69FF'
  },
  { 
    title: '上传数据', 
    icon: 'ph:cloud-arrow-up', 
    desc: '训练数据集',
    color: '#10B981'
  },
  { 
    title: '模型选择', 
    icon: 'ph:brain', 
    desc: 'YOLO系列模型',
    color: '#8B5CF6'
  },
  { 
    title: '完成创建', 
    icon: 'ph:check-circle', 
    desc: '配置确认',
    color: '#F59E0B'
  }
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

// 创建状态
const isCreating = ref(false)

// 切换步骤（流畅动画）
const goToStep = async (step: number) => {
  if (step < 0 || step >= steps.length) return
  
  const container = contentRef.value
  if (!container) {
    currentStep.value = step
    return
  }
  
  const direction = step > currentStep.value ? 1 : -1
  
  // 淡出当前内容
  await gsap.to(container, {
    x: direction * 30,
    opacity: 0,
    duration: 0.25,
    ease: 'power2.in'
  })
  
  // 更新步骤
  currentStep.value = step
  
  // 淡入新内容
  await nextTick()
  gsap.fromTo(container,
    { x: -direction * 30, opacity: 0 },
    { 
      x: 0, 
      opacity: 1, 
      duration: 0.3, 
      ease: 'power2.out' 
    }
  )
}

// 下一步
const nextStep = async () => {
  if (!canProceed.value) {
    ElMessage.warning('请完成当前步骤的必填项')
    return
  }
  
  if (isLastStep.value) {
    await createProject()
  } else {
    await goToStep(currentStep.value + 1)
  }
}

// 上一步
const previousStep = async () => {
  await goToStep(currentStep.value - 1)
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

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer?.files) {
    formData.value.uploadedFiles = Array.from(event.dataTransfer.files)
  }
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
    customWeights: null
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

// 监听visible变化，添加入场动画
watch(() => props.visible, (newVal) => {
  if (newVal && dialogRef.value) {
    nextTick(() => {
      gsap.fromTo(dialogRef.value!,
        { scale: 0.9, opacity: 0 },
        { scale: 1, opacity: 1, duration: 0.3, ease: 'back.out(1.7)' }
      )
    })
  }
})
</script>

<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="emit('update:visible', $event)"
    @close="handleClose"
    :close-on-click-modal="true"
    width="90vw"
    :max-width="1400"
    class="wizard-dialog"
    align-center
    append-to-body
    lock-scroll
    :close-on-press-escape="!isCreating"
    destroy-on-close
  >
    <template #header>
      <div class="wizard-header">
        <div class="header-top">
          <div class="header-icon-wrapper">
            <Icon icon="ph:rocket-launch" :width="24" />
          </div>
          <div class="header-text">
            <h2 class="header-title">创建进化项目</h2>
          </div>
        </div>
        
        <!-- 步骤指示器 - 简化版，去掉重复的进度条 -->
        <div class="steps-indicator">
          <div
            v-for="(step, index) in steps"
            :key="index"
            class="step-indicator"
            :class="{ 
              active: index === currentStep, 
              completed: index < currentStep 
            }"
          >
            <div class="step-connector" v-if="index > 0">
              <div 
                class="connector-line" 
                :class="{ filled: index <= currentStep }"
              ></div>
            </div>
            <div class="step-circle" :style="{ 
              '--step-color': step.color 
            }">
              <Icon 
                v-if="index < currentStep" 
                icon="ph:check-bold" 
                :width="16" 
              />
              <Icon 
                v-else 
                :icon="step.icon" 
                :width="16" 
              />
            </div>
            <span class="step-label">{{ step.title }}</span>
          </div>
        </div>
      </div>n
    </template>
    
    <!-- 内容区域 -->
    <div class="wizard-content" ref="contentRef">
      <!-- 步骤1: 基础信息 -->
      <div v-show="currentStep === 0" class="step-panel">
        <div class="step-header-compact">
          <h3 class="step-title-compact">项目基础信息</h3>
          <p class="step-desc-compact">为您的项目取一个有意义的名称，并简要描述项目目标</p>
        </div>
        
        <div class="form-container">
          <div class="form-group">
            <label class="form-label">
              <span class="required">*</span>
              项目名称
            </label>
            <el-input
              v-model="formData.name"
              placeholder="例如：海上风力发电场智能监测"
              size="large"
              clearable
              maxlength="50"
              show-word-limit
              class="form-input"
            >
              <template #prefix>
                <Icon icon="ph:folder" :width="20" />
              </template>
            </el-input>
          </div>
          
          <div class="form-group">
            <label class="form-label">项目描述（可选）</label>
            <el-input
              v-model="formData.description"
              type="textarea"
              :rows="6"
              placeholder="描述项目的应用场景、数据类型和预期目标..."
              maxlength="200"
              show-word-limit
              class="form-textarea"
            />
          </div>
        </div>
      </div>
      
      <!-- 步骤2: 数据准备 -->
      <div v-show="currentStep === 1" class="step-panel">
        <div class="step-header-compact">
          <h3 class="step-title-compact">上传训练数据</h3>
          <p class="step-desc-compact">选择本地图像文件作为初始训练数据集</p>
        </div>
        
        <div class="upload-section">
          <div class="upload-zone" @click="triggerFileUpload" @dragover.prevent @drop.prevent="handleDrop">
            <input
              ref="fileInputRef"
              type="file"
              multiple
              accept="image/*"
              style="display: none"
              @change="handleFileSelect"
            />
            <div class="upload-icon-wrapper">
              <Icon icon="ph:cloud-arrow-up" :width="64" />
            </div>
            <h4 class="upload-title">拖拽文件到这里或点击上传</h4>
            <p class="upload-hint">支持 JPG、PNG、BMP 等常见图像格式，支持批量上传</p>
            <div v-if="formData.uploadedFiles.length > 0" class="upload-status">
              <Icon icon="ph:check-circle-fill" :width="20" />
              <span>已选择 <strong>{{ formData.uploadedFiles.length }}</strong> 个文件</span>
            </div>
          </div>
          
          <!-- 文件列表 -->
          <div v-if="formData.uploadedFiles.length > 0" class="file-list">
            <div
              v-for="(file, index) in formData.uploadedFiles.slice(0, 12)"
              :key="index"
              class="file-item"
            >
              <div class="file-icon">
                <Icon icon="ph:file-image" :width="24" />
              </div>
              <div class="file-details">
                <span class="file-name">{{ file.name }}</span>
                <span class="file-size">{{ (file.size / 1024).toFixed(1) }} KB</span>
              </div>
              <button 
                class="file-remove"
                @click.stop="removeFile(index)"
              >
                <Icon icon="ph:x" :width="18" />
              </button>
            </div>
            <div v-if="formData.uploadedFiles.length > 12" class="file-more">
              <Icon icon="ph:dots-three" :width="20" />
              <span>还有 {{ formData.uploadedFiles.length - 12 }} 个文件</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 步骤3: 模型配置 -->
      <div v-show="currentStep === 2" class="step-panel">
        <div class="step-header-compact">
          <h3 class="step-title-compact">选择检测模型</h3>
          <p class="step-desc-compact">根据您的需求选择合适的YOLO系列模型</p>
        </div>
        
        <!-- 模型系列选择 - 高级设计 -->
        <div class="model-section-premium">
          <div class="section-header-premium">
            <div class="section-icon-premium">
              <Icon icon="ph:stack" :width="22" />
            </div>
            <div class="section-header-text">
              <h4 class="section-title-premium">模型系列</h4>
              <p class="section-subtitle-premium">选择您需要的YOLO检测模型系列</p>
            </div>
          </div>
          <div class="model-grid-premium">
            <div
              v-for="option in modelSeriesOptions"
              :key="option.value"
              class="model-card-premium"
              :class="{ selected: formData.modelSeries === option.value }"
              @click="formData.modelSeries = option.value"
              :style="{ '--model-color': option.color }"
            >
              <div class="model-card-bg"></div>
              <div class="model-card-content">
                <div class="model-icon-premium">
                  <Icon :icon="option.icon" :width="32" />
                </div>
                <div class="model-info-premium">
                  <span class="model-name-premium">{{ option.label }}</span>
                  <div v-if="option.badge" class="model-badge-premium">
                    <Icon icon="ph:star-fill" :width="10" />
                    <span>{{ option.badge }}</span>
                  </div>
                </div>
                <div v-if="formData.modelSeries === option.value" class="model-selected-indicator">
                  <Icon icon="ph:check-circle-fill" :width="26" />
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 模型规模选择 - 高级设计 -->
        <div class="model-section-premium">
          <div class="section-header-premium">
            <div class="section-icon-premium">
              <Icon icon="ph:scales" :width="22" />
            </div>
            <div class="section-header-text">
              <h4 class="section-title-premium">模型规模</h4>
              <p class="section-subtitle-premium">根据您的硬件资源选择合适的参数量</p>
            </div>
          </div>
          <div class="size-list-premium">
            <div
              v-for="size in modelSizeOptions"
              :key="size.value"
              class="size-card-premium"
              :class="{ selected: formData.modelSize === size.value }"
              @click="formData.modelSize = size.value"
            >
              <div class="size-card-left">
                <div class="size-icon-premium">
                  <Icon icon="ph:lightning-fill" :width="26" />
                </div>
                <div class="size-info-premium">
                  <div class="size-label-row">
                    <span class="size-label-premium">{{ size.label }}</span>
                    <span class="size-params-premium">{{ size.params }}</span>
                  </div>
                  <span class="size-desc-premium">{{ size.desc }}</span>
                </div>
              </div>
              <div v-if="formData.modelSize === size.value" class="size-selected-indicator">
                <Icon icon="ph:check-circle-fill" :width="24" />
              </div>
            </div>
          </div>
        </div>
        
        <!-- 自定义权重 - 高级设计 -->
        <div class="model-section-premium">
          <div class="section-header-premium">
            <div class="section-icon-premium">
              <Icon icon="ph:file-arrow-up" :width="22" />
            </div>
            <div class="section-header-text">
              <h4 class="section-title-premium">自定义权重（可选）</h4>
              <p class="section-subtitle-premium">上传您自己的预训练权重文件</p>
            </div>
          </div>
          <div class="weights-upload-premium">
            <el-button
              @click="triggerWeightsUpload"
              size="large"
              class="weights-button-premium"
            >
              <input
                ref="weightsInputRef"
                type="file"
                accept=".pt,.pth"
                style="display: none"
                @change="handleWeightsSelect"
              />
              <Icon icon="ph:upload" :width="20" />
              <span>{{ formData.customWeights ? formData.customWeights.name : '选择权重文件（.pt / .pth）' }}</span>
            </el-button>
            <el-button
              v-if="formData.customWeights"
              type="danger"
              text
              @click="removeWeights"
              class="weights-remove-premium"
            >
              <Icon icon="ph:trash" :width="18" />
              <span>移除</span>
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 步骤4: 确认创建 -->
      <div v-show="currentStep === 3" class="step-panel">
        <div class="step-header-compact">
          <h3 class="step-title-compact">确认项目配置</h3>
          <p class="step-desc-compact">请检查以下配置信息，确认无误后即可创建项目</p>
        </div>
        
        <div class="summary-container">
          <div class="summary-card">
            <div class="summary-header">
              <Icon icon="ph:info-fill" :width="20" />
              <span>基础信息</span>
            </div>
            <div class="summary-content">
              <div class="summary-item">
                <span class="summary-label">项目名称</span>
                <span class="summary-value">{{ formData.name }}</span>
              </div>
              <div v-if="formData.description" class="summary-item">
                <span class="summary-label">项目描述</span>
                <span class="summary-value">{{ formData.description }}</span>
              </div>
            </div>
          </div>
          
          <div class="summary-card">
            <div class="summary-header">
              <Icon icon="ph:database-fill" :width="20" />
              <span>训练数据</span>
            </div>
            <div class="summary-content">
              <div class="summary-item">
                <span class="summary-label">图像数量</span>
                <span class="summary-value highlight">{{ formData.uploadedFiles.length }} 张</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">总大小</span>
                <span class="summary-value">
                  {{ (formData.uploadedFiles.reduce((sum, f) => sum + f.size, 0) / 1024 / 1024).toFixed(2) }} MB
                </span>
              </div>
            </div>
          </div>
          
          <div class="summary-card">
            <div class="summary-header">
              <Icon icon="ph:brain-fill" :width="20" />
              <span>模型配置</span>
            </div>
            <div class="summary-content">
              <div class="summary-item">
                <span class="summary-label">模型系列</span>
                <span class="summary-value">
                  {{ modelSeriesOptions.find(o => o.value === formData.modelSeries)?.label }}
                </span>
              </div>
              <div class="summary-item">
                <span class="summary-label">模型规模</span>
                <span class="summary-value">
                  {{ modelSizeOptions.find(o => o.value === formData.modelSize)?.label }}
                </span>
              </div>
              <div v-if="formData.customWeights" class="summary-item">
                <span class="summary-label">自定义权重</span>
                <span class="summary-value">{{ formData.customWeights.name }}</span>
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
          class="footer-button"
        >
          <Icon icon="ph:arrow-left" :width="18" />
          <span>上一步</span>
        </el-button>
        <el-button
          v-else
          @click="handleClose"
          size="large"
          class="footer-button"
        >
          <span>取消</span>
        </el-button>
        
        <div class="footer-spacer"></div>
        
        <el-button
          type="primary"
          @click="nextStep"
          size="large"
          :disabled="!canProceed"
          :loading="isCreating"
          class="footer-button primary"
        >
          <span>{{ isLastStep ? (isCreating ? '创建中...' : '创建项目') : '下一步' }}</span>
          <Icon 
            v-if="!isLastStep && !isCreating" 
            icon="ph:arrow-right" 
            :width="18" 
          />
          <Icon 
            v-else-if="!isCreating" 
            icon="ph:rocket-launch" 
            :width="18" 
          />
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped lang="scss">
// 弹窗基础样式
.wizard-dialog {
  :deep(.el-dialog) {
    margin: 5vh auto !important;
    border-radius: 20px;
    overflow: hidden;
    background: var(--color-surface);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    
    .dark & {
      background: rgba(15, 23, 42, 0.98);
      backdrop-filter: blur(20px);
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
    }
    height: 90vh;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }
  
  :deep(.el-dialog__header) {
    padding: 0;
    margin: 0;
    border-bottom: 1px solid var(--color-border);
    flex-shrink: 0;
  }
  
  :deep(.el-dialog__body) {
    padding: $spacing-3xl;
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    min-height: 0;
    max-height: calc(90vh - 200px);
    background: transparent;
    @include custom-scrollbar;
    
    .dark & {
      background: transparent;
    }
  }
  
  :deep(.el-dialog__footer) {
    padding: $spacing-xl $spacing-3xl;
    border-top: 1px solid var(--color-border);
    background: var(--color-surface-elevated);
    flex-shrink: 0;
  }
  
  :deep(.el-dialog__headerbtn) {
    top: $spacing-lg;
    right: $spacing-lg;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease;
    color: var(--color-text-secondary);
    
    &:hover {
      background: rgba(0, 0, 0, 0.1);
      color: var(--color-text-primary);
      transform: rotate(90deg);
    }
    
    .dark & {
      background: rgba(255, 255, 255, 0.1);
      
      &:hover {
        background: rgba(255, 255, 255, 0.2);
      }
    }
  }
  
  :deep(.el-dialog__mask) {
    background: rgba(0, 0, 0, 0.5);
    
    .dark & {
      background: rgba(0, 0, 0, 0.7);
    }
  }
  
  // 响应式
  @media (max-width: 1280px) {
    :deep(.el-dialog) {
      width: 95vw !important;
    }
  }
  
  @media (max-width: 768px) {
    :deep(.el-dialog__body) {
      padding: $spacing-xl;
    }
    
    :deep(.el-dialog__footer) {
      padding: $spacing-lg $spacing-xl;
    }
  }
}

// Header - 精简版
.wizard-header {
  padding: $spacing-lg $spacing-3xl;
  background: var(--color-surface-elevated);
}

.header-top {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-lg;
}

.header-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #4A69FF, #7AA2F7);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 2px 8px rgba(74, 105, 255, 0.3);
  flex-shrink: 0;
}

.header-text {
  flex: 1;
}

.header-title {
  font-size: $font-size-xl;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  margin: 0;
}

// 步骤指示器 - 去掉重复的进度条
.steps-indicator {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: $spacing-xs;
  position: relative;
}

.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-xs;
  flex: 1;
  position: relative;
  z-index: 1;
}

.step-connector {
  position: absolute;
  left: -50%;
  top: 20px;
  width: 100%;
  height: 2px;
  z-index: 0;
}

.connector-line {
  width: 100%;
  height: 100%;
  background: var(--color-border);
  transition: all 0.4s ease;
  
  &.filled {
    background: linear-gradient(90deg, var(--color-success) 0%, var(--color-primary) 100%);
  }
}

.step-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid var(--color-border);
  background: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 2;
  color: var(--color-text-tertiary);
  
  .step-indicator.completed & {
    background: var(--color-success);
    border-color: var(--color-success);
    color: white;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
  }
  
  .step-indicator.active & {
    background: var(--step-color, var(--color-primary));
    border-color: var(--step-color, var(--color-primary));
    color: white;
    box-shadow: 0 0 0 4px rgba(74, 105, 255, 0.15), 0 4px 12px rgba(74, 105, 255, 0.3);
    transform: scale(1.1);
  }
}

.step-label {
  font-size: $font-size-xs;
  font-weight: $font-weight-medium;
  color: var(--color-text-secondary);
  transition: all 0.3s ease;
  margin-top: 4px;
  
  .step-indicator.active & {
    color: var(--step-color, var(--color-primary));
    font-weight: $font-weight-bold;
  }
  
  .step-indicator.completed & {
    color: var(--color-success);
  }
}

// 内容区域
.wizard-content {
  min-height: 400px;
  max-height: calc(90vh - 300px);
  overflow-y: auto;
  @include custom-scrollbar;
}

.step-panel {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 精简的步骤标题
.step-header-compact {
  margin-bottom: $spacing-xl;
  padding-bottom: $spacing-md;
  border-bottom: 1px solid var(--color-border);
}

.step-title-compact {
  font-size: $font-size-xl;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  margin: 0 0 $spacing-xs 0;
}

.step-desc-compact {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  margin: 0;
}

// 表单
.form-container {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: $spacing-xl;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.form-label {
  font-size: $font-size-base;
  font-weight: $font-weight-semibold;
  color: var(--color-text-primary);
  
  .required {
    color: var(--color-danger);
    margin-right: 4px;
  }
}

.form-input,
.form-textarea {
  :deep(.el-input__inner),
  :deep(.el-textarea__inner) {
    font-size: $font-size-base;
    border-radius: 12px;
    background: var(--color-surface-elevated);
    border-color: var(--color-border);
    color: var(--color-text-primary);
    
    .dark & {
      background: rgba(30, 41, 59, 0.6) !important;
      border-color: rgba(255, 255, 255, 0.15) !important;
      color: rgba(255, 255, 255, 0.9) !important;
    }
    
    &::placeholder {
      color: var(--color-text-tertiary);
      
      .dark & {
        color: rgba(255, 255, 255, 0.4) !important;
      }
    }
    
    &:focus {
      background: var(--color-surface);
      border-color: var(--color-primary);
      
      .dark & {
        background: rgba(30, 41, 59, 0.8) !important;
        border-color: rgba(96, 165, 250, 0.6) !important;
        color: rgba(255, 255, 255, 0.95) !important;
      }
    }
  }
  
  :deep(.el-input__wrapper) {
    .dark & {
      background: rgba(30, 41, 59, 0.6) !important;
      box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.15) inset !important;
    }
  }
}

// 上传区域
.upload-section {
  max-width: 900px;
  margin: 0 auto;
}

.upload-zone {
  border: 3px dashed var(--color-border);
  border-radius: 20px;
  padding: $spacing-3xl;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--color-surface-elevated);
  margin-bottom: $spacing-xl;
  
  .dark & {
    background: rgba(30, 41, 59, 0.3);
    border-color: rgba(255, 255, 255, 0.15);
  }
  
  &:hover {
    border-color: var(--color-primary);
    background: rgba(74, 105, 255, 0.03);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(74, 105, 255, 0.15);
    
    .dark & {
      background: rgba(96, 165, 250, 0.08);
      box-shadow: 0 8px 24px rgba(96, 165, 250, 0.2);
    }
  }
}

.upload-icon-wrapper {
  display: inline-block;
  padding: $spacing-xl;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(74, 105, 255, 0.1), rgba(138, 43, 226, 0.1));
  margin-bottom: $spacing-lg;
  color: var(--color-primary);
  
  .dark & {
    background: linear-gradient(135deg, rgba(96, 165, 250, 0.15), rgba(167, 139, 250, 0.15));
  }
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
  gap: $spacing-xs;
  margin-top: $spacing-lg;
  padding: $spacing-sm $spacing-lg;
  background: rgba(16, 185, 129, 0.1);
  border-radius: $radius-full;
  color: var(--color-success);
  font-size: $font-size-sm;
  font-weight: $font-weight-medium;
  
  .dark & {
    background: rgba(16, 185, 129, 0.15);
  }
}

// 文件列表
.file-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: $spacing-md;
  max-height: 300px;
  overflow-y: auto;
  @include custom-scrollbar;
}

.file-item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-md;
  background: var(--color-surface-elevated);
  border-radius: 12px;
  border: 1px solid var(--color-border);
  transition: all 0.2s ease;
  
  .dark & {
    background: rgba(30, 41, 59, 0.4);
    border-color: rgba(255, 255, 255, 0.1);
  }
  
  &:hover {
    border-color: var(--color-primary);
    transform: translateY(-2px);
    box-shadow: $shadow-md;
    
    .dark & {
      background: rgba(30, 41, 59, 0.6);
    }
  }
}

.file-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: rgba(74, 105, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  flex-shrink: 0;
}

.file-details {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
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

.file-remove {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
  
  &:hover {
    background: rgba(239, 68, 68, 0.2);
    transform: scale(1.1);
  }
}

.file-more {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-xs;
  padding: $spacing-lg;
  color: var(--color-text-secondary);
  font-size: $font-size-sm;
}

// 模型选择 - 高级设计
.model-section-premium {
  margin-bottom: $spacing-3xl;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.section-header-premium {
  display: flex;
  align-items: flex-start;
  gap: $spacing-md;
  margin-bottom: $spacing-xl;
}

.section-icon-premium {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, 
    rgba(74, 105, 255, 0.15), 
    rgba(138, 43, 226, 0.15)
  );
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(74, 105, 255, 0.15);
  flex-shrink: 0;
  
  .dark & {
    background: linear-gradient(135deg, 
      rgba(96, 165, 250, 0.2), 
      rgba(167, 139, 250, 0.2)
    );
  }
}

.section-header-text {
  flex: 1;
}

.section-title-premium {
  font-size: $font-size-lg;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
}

.section-subtitle-premium {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  margin: 0;
}

// 模型系列网格 - 高级设计
.model-grid-premium {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: $spacing-lg;
}

.model-card-premium {
  position: relative;
  cursor: pointer;
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  
  .model-card-bg {
    position: absolute;
    inset: 0;
    background: var(--color-surface-elevated);
    border: 2px solid var(--color-border);
    border-radius: 20px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    
    .dark & {
      background: rgba(30, 41, 59, 0.4);
      border-color: rgba(255, 255, 255, 0.1);
    }
  }
  
  .model-card-content {
    position: relative;
    padding: $spacing-xl;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: $spacing-md;
    z-index: 1;
  }
  
  &:hover {
    transform: translateY(-6px);
    
    .model-card-bg {
      border-color: var(--model-color, var(--color-primary));
      box-shadow: 0 12px 32px rgba(74, 105, 255, 0.2);
      
      .dark & {
        box-shadow: 0 12px 32px rgba(96, 165, 250, 0.3);
      }
    }
    
    .model-icon-premium {
      transform: scale(1.1) rotate(5deg);
    }
  }
  
  &.selected {
    .model-card-bg {
      background: linear-gradient(135deg, 
        rgba(74, 105, 255, 0.1), 
        rgba(138, 43, 226, 0.1)
      );
      border-color: var(--model-color, var(--color-primary));
      border-width: 3px;
      box-shadow: 0 0 0 4px rgba(74, 105, 255, 0.1), 
                  0 12px 40px rgba(74, 105, 255, 0.3);
    }
    
    .model-icon-premium {
      background: linear-gradient(135deg, 
        var(--model-color, #4A69FF), 
        rgba(74, 105, 255, 0.8)
      );
      color: white;
      box-shadow: 0 8px 24px rgba(74, 105, 255, 0.4);
    }
  }
}

.model-icon-premium {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: rgba(74, 105, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--model-color, var(--color-primary));
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  
  .dark & {
    background: rgba(96, 165, 250, 0.15);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
}

.model-info-premium {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-xs;
  width: 100%;
}

.model-name-premium {
  font-size: $font-size-lg;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
}

.model-badge-premium {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: white;
  border-radius: $radius-full;
  font-size: $font-size-xs;
  font-weight: $font-weight-bold;
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.4);
}

.model-selected-indicator {
  position: absolute;
  top: $spacing-sm;
  right: $spacing-sm;
  color: var(--color-success);
  z-index: 2;
  animation: scaleIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes scaleIn {
  from {
    transform: scale(0);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

// 模型规模列表 - 高级设计
.size-list-premium {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.size-card-premium {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-xl;
  background: var(--color-surface-elevated);
  border: 2px solid var(--color-border);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  
  .dark & {
    background: rgba(30, 41, 59, 0.4);
    border-color: rgba(255, 255, 255, 0.1);
  }
  
  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: var(--color-primary);
    transform: scaleY(0);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
  
  &:hover {
    border-color: var(--color-primary);
    transform: translateX(8px);
    box-shadow: 0 8px 24px rgba(74, 105, 255, 0.15);
    
    &::before {
      transform: scaleY(1);
    }
    
    .size-icon-premium {
      transform: scale(1.1);
    }
  }
  
  &.selected {
    background: linear-gradient(135deg, 
      rgba(74, 105, 255, 0.08), 
      rgba(138, 43, 226, 0.05)
    );
    border-color: var(--color-primary);
    border-width: 3px;
    box-shadow: 0 0 0 4px rgba(74, 105, 255, 0.1), 
                0 8px 24px rgba(74, 105, 255, 0.2);
    
    &::before {
      transform: scaleY(1);
      width: 5px;
    }
  }
}

.size-card-left {
  display: flex;
  align-items: center;
  gap: $spacing-lg;
  flex: 1;
}

.size-icon-premium {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: linear-gradient(135deg, 
    rgba(74, 105, 255, 0.15), 
    rgba(138, 43, 226, 0.15)
  );
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  flex-shrink: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(74, 105, 255, 0.15);
  
  .size-card-premium.selected & {
    background: linear-gradient(135deg, #4A69FF, #7AA2F7);
    color: white;
    box-shadow: 0 6px 20px rgba(74, 105, 255, 0.3);
  }
}

.size-info-premium {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.size-label-row {
  display: flex;
  align-items: baseline;
  gap: $spacing-sm;
}

.size-label-premium {
  font-size: $font-size-lg;
  font-weight: $font-weight-bold;
  color: var(--color-text-primary);
}

.size-params-premium {
  font-size: $font-size-sm;
  font-weight: $font-weight-bold;
  color: var(--color-primary);
  background: rgba(74, 105, 255, 0.1);
  padding: 2px 8px;
  border-radius: 6px;
}

.size-desc-premium {
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
}

.size-selected-indicator {
  color: var(--color-success);
  flex-shrink: 0;
  animation: scaleIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

// 权重上传 - 高级设计
.weights-upload-premium {
  display: flex;
  gap: $spacing-md;
  align-items: center;
}

.weights-button-premium {
  flex: 1;
  height: 56px;
  border-radius: 14px;
  font-size: $font-size-base;
  font-weight: $font-weight-semibold;
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(74, 105, 255, 0.2);
  }
}

.weights-remove-premium {
  height: 56px;
  padding: 0 $spacing-lg;
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

// 摘要
.summary-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: $spacing-xl;
}

.summary-card {
  padding: $spacing-xl;
  background: var(--color-surface-elevated);
  border-radius: 16px;
  border: 2px solid var(--color-border);
  transition: all 0.3s ease;
  
  .dark & {
    background: rgba(30, 41, 59, 0.4);
    border-color: rgba(255, 255, 255, 0.1);
  }
  
  &:hover {
    border-color: var(--color-primary);
    transform: translateY(-4px);
    box-shadow: $shadow-lg;
    
    .dark & {
      background: rgba(30, 41, 59, 0.6);
    }
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

.summary-content {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: $spacing-md;
}

.summary-label {
  font-size: $font-size-sm;
  color: var(--color-text-tertiary);
  flex-shrink: 0;
}

.summary-value {
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

// Footer
.wizard-footer {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.footer-spacer {
  flex: 1;
}

.footer-button {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  padding: $spacing-md $spacing-xl;
  border-radius: 12px;
  font-weight: $font-weight-semibold;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  &:hover::before {
    opacity: 1;
  }
  
  &:not(.primary) {
    background: var(--color-surface-elevated);
    border: 1px solid var(--color-border);
    color: var(--color-text-primary);
    
    &:hover:not(:disabled) {
      background: var(--color-surface);
      border-color: var(--color-primary);
      color: var(--color-primary);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(74, 105, 255, 0.2);
    }
    
    &:active:not(:disabled) {
      transform: translateY(0);
    }
  }
  
  &.primary {
    min-width: 140px;
    background: linear-gradient(135deg, #4A69FF, #7AA2F7);
    border: none;
    color: white;
    box-shadow: 0 4px 16px rgba(74, 105, 255, 0.3);
    
    &:hover:not(:disabled) {
      background: linear-gradient(135deg, #5A79FF, #8AB2F7);
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(74, 105, 255, 0.4);
    }
    
    &:active:not(:disabled) {
      transform: translateY(0);
      box-shadow: 0 2px 8px rgba(74, 105, 255, 0.3);
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .header-main {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .steps-indicator {
    flex-wrap: wrap;
  }
  
  .step-indicator::after {
    display: none;
  }
  
  .model-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .size-grid {
    grid-template-columns: 1fr;
  }
  
  .summary-container {
    grid-template-columns: 1fr;
  }
}
</style>
