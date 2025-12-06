/**
 * Mock Job Status Data
 * 
 * Simulates real-time job progress updates from the backend.
 * Creates a stream of status updates to demonstrate dynamic UI updates.
 * 
 * Design Intent: Show how the application handles evolving job states,
 * enabling realistic testing of progress indicators and step transitions.
 * 
 * YOLO Training Metrics:
 * - mAP (mean Average Precision)
 * - Precision / Recall
 * - Box Loss / Class Loss / Object Loss
 * - IoU (Intersection over Union)
 */

export type JobStep = 
  | 'initialization'
  | 'data_preparation'
  | 'model_training'
  | 'active_learning'
  | 'inference'
  | 'completed'

export interface YoloMetrics {
  // Detection metrics
  mAP50: number      // mAP at IoU=0.5
  mAP5095: number    // mAP at IoU=0.5:0.95
  precision: number  // 精确率
  recall: number     // 召回率
  
  // Loss components
  boxLoss: number    // 边界框损失
  clsLoss: number    // 分类损失
  objLoss: number    // 目标置信度损失
  
  // Training info
  currentEpoch: number
  totalEpochs: number
  batchSize: number
  learningRate: number
  
  // Hardware
  gpuMemory: string
  gpuUtilization: number
  
  // Time
  epochTime: number  // seconds per epoch
  eta: string        // estimated time of arrival
}

export interface JobStatus {
  id: string
  projectId: string
  currentStep: JobStep
  progress: number // 0-100
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed'
  startedAt: string
  estimatedCompletion?: string
  metrics?: {
    accuracy?: number
    loss?: number
    samplesProcessed?: number
    totalSamples?: number
  }
  yoloMetrics?: YoloMetrics
  logs: string[]
}

const stepSequence: JobStep[] = [
  'initialization',
  'data_preparation',
  'model_training',
  'active_learning',
  'inference',
  'completed'
]

/**
 * Generate realistic YOLO metrics based on training progress
 */
const generateYoloMetrics = (step: number, progress: number): YoloMetrics => {
  const totalProgress = (step * 100 + progress) / 600 // 0 to 1
  
  // Simulate realistic training curves
  const epochProgress = Math.floor(totalProgress * 300) // max 300 epochs
  const currentEpoch = Math.max(1, epochProgress)
  
  // mAP typically starts low and increases with training
  const basemAP50 = 0.15
  const maxmAP50 = 0.92
  const mAP50 = basemAP50 + (maxmAP50 - basemAP50) * (1 - Math.exp(-totalProgress * 4)) + (Math.random() - 0.5) * 0.02
  
  const basemAP5095 = 0.08
  const maxmAP5095 = 0.68
  const mAP5095 = basemAP5095 + (maxmAP5095 - basemAP5095) * (1 - Math.exp(-totalProgress * 3.5)) + (Math.random() - 0.5) * 0.015
  
  // Precision and Recall
  const precision = 0.45 + 0.48 * (1 - Math.exp(-totalProgress * 3)) + (Math.random() - 0.5) * 0.03
  const recall = 0.35 + 0.55 * (1 - Math.exp(-totalProgress * 2.5)) + (Math.random() - 0.5) * 0.04
  
  // Losses decrease over time
  const boxLoss = Math.max(0.02, 0.12 * Math.exp(-totalProgress * 3) + (Math.random() - 0.5) * 0.005)
  const clsLoss = Math.max(0.01, 0.08 * Math.exp(-totalProgress * 3.5) + (Math.random() - 0.5) * 0.003)
  const objLoss = Math.max(0.01, 0.06 * Math.exp(-totalProgress * 4) + (Math.random() - 0.5) * 0.002)
  
  // Learning rate schedule (cosine decay)
  const baseLR = 0.01
  const minLR = 0.0001
  const learningRate = minLR + (baseLR - minLR) * 0.5 * (1 + Math.cos(Math.PI * totalProgress))
  
  return {
    mAP50: Math.min(0.95, Math.max(0.1, mAP50)),
    mAP5095: Math.min(0.75, Math.max(0.05, mAP5095)),
    precision: Math.min(0.98, Math.max(0.3, precision)),
    recall: Math.min(0.98, Math.max(0.25, recall)),
    boxLoss,
    clsLoss,
    objLoss,
    currentEpoch,
    totalEpochs: 300,
    batchSize: 16,
    learningRate,
    gpuMemory: '8.2GB / 12GB',
    gpuUtilization: 85 + Math.random() * 10,
    epochTime: 45 + Math.random() * 10,
    eta: formatETA((300 - currentEpoch) * 50)
  }
}

/**
 * Format ETA in human readable format
 */
const formatETA = (seconds: number): string => {
  if (seconds < 60) return `${Math.round(seconds)}s`
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`
  const hours = Math.floor(seconds / 3600)
  const mins = Math.round((seconds % 3600) / 60)
  return `${hours}h ${mins}m`
}

/**
 * Generate a realistic job status
 */
const createJobStatus = (step: number, progress: number): JobStatus => {
  const currentStep = stepSequence[Math.min(step, stepSequence.length - 1)]
  const yoloMetrics = generateYoloMetrics(step, progress)
  
  return {
    id: 'job-demo-001',
    projectId: '2',
    currentStep,
    progress,
    status: step >= stepSequence.length - 1 ? 'completed' : 'running',
    startedAt: new Date(Date.now() - 3600000).toISOString(),
    estimatedCompletion: new Date(Date.now() + 1800000).toISOString(),
    metrics: {
      accuracy: yoloMetrics.mAP50,
      loss: yoloMetrics.boxLoss + yoloMetrics.clsLoss + yoloMetrics.objLoss,
      samplesProcessed: Math.floor((progress / 100) * 3420),
      totalSamples: 3420
    },
    yoloMetrics,
    logs: generateLogs(currentStep, progress, yoloMetrics)
  }
}

/**
 * Generate realistic log messages based on current step
 */
const generateLogs = (step: JobStep, progress: number, metrics: YoloMetrics): string[] => {
  const logs: string[] = []
  
  switch (step) {
    case 'initialization':
      logs.push('[INFO] YOLO训练任务初始化')
      logs.push('[INFO] 加载配置文件: yolov8n.yaml')
      if (progress > 30) logs.push('[INFO] 分配GPU资源: NVIDIA RTX 4090')
      if (progress > 60) logs.push('[INFO] 初始化分布式训练环境')
      break
    case 'data_preparation':
      logs.push('[INFO] 加载数据集: ./datasets/offshore_wind')
      logs.push('[INFO] 图像预处理: 640x640 resize')
      if (progress > 40) logs.push('[INFO] 数据增强: mosaic, hsv, flip')
      if (progress > 70) logs.push('[INFO] 创建训练/验证集划分: 80/20')
      break
    case 'model_training':
      logs.push(`[INFO] Epoch ${metrics.currentEpoch}/${metrics.totalEpochs}`)
      logs.push(`[INFO] mAP@50: ${(metrics.mAP50 * 100).toFixed(1)}%`)
      logs.push(`[INFO] Box Loss: ${metrics.boxLoss.toFixed(4)}, Cls Loss: ${metrics.clsLoss.toFixed(4)}`)
      if (progress > 50) logs.push(`[INFO] 学习率: ${metrics.learningRate.toExponential(2)}`)
      break
    case 'active_learning':
      logs.push('[INFO] 主动学习：选择高不确定性样本')
      logs.push('[INFO] 查询标注池获取新标签')
      if (progress > 30) logs.push('[INFO] 使用新样本更新模型')
      if (progress > 70) logs.push('[INFO] 收敛准则满足')
      break
    case 'inference':
      logs.push('[INFO] 在未标注数据上运行推理')
      logs.push(`[INFO] 已处理 ${Math.floor(progress * 34.2)}/3420 张图像`)
      if (progress > 80) logs.push('[INFO] 生成置信度分数')
      break
    case 'completed':
      logs.push('[SUCCESS] 训练任务完成!')
      logs.push(`[INFO] 最终 mAP@50: ${(metrics.mAP50 * 100).toFixed(1)}%`)
      logs.push('[INFO] 模型已保存: best.pt, last.pt')
      break
  }
  
  return logs
}

/**
 * Create a job status stream that updates over time
 */
export const createJobStatusStream = (
  callback: (status: JobStatus) => void,
  interval: number = 2000
): () => void => {
  let step = 0
  let progress = 0
  let timer: number
  
  const update = () => {
    // Increment progress
    progress += Math.random() * 10 + 5
    
    // Move to next step when progress exceeds 100
    if (progress >= 100 && step < stepSequence.length - 1) {
      step++
      progress = 0
    }
    
    // Cap progress at 100
    progress = Math.min(progress, 100)
    
    // Generate and emit status
    const status = createJobStatus(step, progress)
    callback(status)
    
    // Stop when completed
    if (step >= stepSequence.length - 1 && progress >= 100) {
      clearInterval(timer)
    }
  }
  
  // Start updates
  timer = window.setInterval(update, interval)
  
  // Initial update
  update()
  
  // Return cleanup function
  return () => {
    clearInterval(timer)
  }
}

/**
 * Get a single job status snapshot (for testing)
 */
export const fetchJobStatus = (jobId: string): Promise<JobStatus> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(createJobStatus(2, 45))
    }, 500)
  })
}
