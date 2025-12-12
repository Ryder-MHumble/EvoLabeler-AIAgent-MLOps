/**
 * Project-specific Workspace Mock Data
 * 
 * 为每个项目提供不同的模拟数据，以展示真实用户体验
 * 数据包括：训练进度、指标、损失曲线、Agent状态等
 */

import type { JobStatus, JobStep } from './jobStatus'
import type { YoloLossData } from '@/components/workspace/types'

// 项目特定配置接口
export interface ProjectWorkspaceConfig {
  id: string
  name: string
  description: string
  status: 'idle' | 'training' | 'labeling' | 'completed'
  modelArchitecture: string
  
  // 训练配置
  trainingConfig: {
    batchSize: number
    learningRate: string
    inputSize: string
    totalEpochs: number
    currentEpoch: number
  }
  
  // 硬件资源
  hardware: {
    gpuMemory: string
    gpuUsage: number
  }
  
  // 数据集
  dataset: {
    totalSamples: number
    processedSamples: number
    labelClasses: string[]
  }
  
  // 训练时间
  timing: {
    startTime: string
    epochTime: string
    estimatedRemaining: string
  }
  
  // YOLO 指标
  metrics: {
    mapAt50: number
    mapAt50_95: number
    precision: number
    recall: number
    boxLoss: number
    totalLoss: number
    trend: {
      mapAt50: number
      mapAt50_95: number
      boxLoss: number
    }
  }
  
  // 初始步骤
  initialStepIndex: number
  
  // 损失曲线特性
  lossCharacteristics: {
    convergenceSpeed: 'fast' | 'medium' | 'slow'
    noise: number
    startingLoss: number
  }
}

// 每个项目的独立配置数据
export const projectWorkspaceConfigs: Record<string, ProjectWorkspaceConfig> = {
  '1': {
    id: '1',
    name: '海上风电平台检测',
    description: '基于卫星影像的海上风电平台自动检测与标注',
    status: 'completed',
    modelArchitecture: 'TDA-YOLOv8n',
    trainingConfig: {
      batchSize: 32,
      learningRate: '5.00e-3',
      inputSize: '1024x1024',
      totalEpochs: 300,
      currentEpoch: 300
    },
    hardware: {
      gpuMemory: '10.5GB / 12GB',
      gpuUsage: 85
    },
    dataset: {
      totalSamples: 3420,
      processedSamples: 3420,
      labelClasses: ['风电平台', '风机叶片', '支撑结构', '海上作业船']
    },
    timing: {
      startTime: '昨天 14:30',
      epochTime: '42s',
      estimatedRemaining: '已完成'
    },
    metrics: {
      mapAt50: 94.5,
      mapAt50_95: 78.2,
      precision: 92.3,
      recall: 89.7,
      boxLoss: 0.0089,
      totalLoss: 0.0234,
      trend: { mapAt50: 0.8, mapAt50_95: 0.5, boxLoss: -0.002 }
    },
    initialStepIndex: 5,
    lossCharacteristics: {
      convergenceSpeed: 'fast',
      noise: 0.001,
      startingLoss: 0.05
    }
  },
  
  '2': {
    id: '2',
    name: '建筑物提取',
    description: '高分辨率遥感影像中的建筑物轮廓提取与分类',
    status: 'training',
    modelArchitecture: 'YOLOv8n',
    trainingConfig: {
      batchSize: 16,
      learningRate: '1.00e-2',
      inputSize: '640x640',
      totalEpochs: 300,
      currentEpoch: 2
    },
    hardware: {
      gpuMemory: '8.2GB / 12GB',
      gpuUsage: 90
    },
    dataset: {
      totalSamples: 8750,
      processedSamples: 193,
      labelClasses: ['住宅楼', '商业建筑', '工业厂房', '公共设施', '在建工地']
    },
    timing: {
      startTime: '4:19:04 PM',
      epochTime: '55s',
      estimatedRemaining: '4h 8m'
    },
    metrics: {
      mapAt50: 18.7,
      mapAt50_95: 10.4,
      precision: 45.1,
      recall: 35.5,
      boxLoss: 0.1178,
      totalLoss: 0.2521,
      trend: { mapAt50: 3.7, mapAt50_95: 2.4, boxLoss: -0.038 }
    },
    initialStepIndex: 2,
    lossCharacteristics: {
      convergenceSpeed: 'medium',
      noise: 0.003,
      startingLoss: 0.12
    }
  },
  
  '3': {
    id: '3',
    name: '农田边界识别',
    description: '多光谱遥感影像的农田边界自动识别与面积计算',
    status: 'labeling',
    modelArchitecture: 'YOLOv9s',
    trainingConfig: {
      batchSize: 24,
      learningRate: '8.00e-3',
      inputSize: '800x800',
      totalEpochs: 200,
      currentEpoch: 0
    },
    hardware: {
      gpuMemory: '6.8GB / 12GB',
      gpuUsage: 45
    },
    dataset: {
      totalSamples: 1250,
      processedSamples: 542,
      labelClasses: ['水田', '旱田', '果园', '温室', '休耕地']
    },
    timing: {
      startTime: '-',
      epochTime: '-',
      estimatedRemaining: '待训练'
    },
    metrics: {
      mapAt50: 0,
      mapAt50_95: 0,
      precision: 0,
      recall: 0,
      boxLoss: 0,
      totalLoss: 0,
      trend: { mapAt50: 0, mapAt50_95: 0, boxLoss: 0 }
    },
    initialStepIndex: 1,
    lossCharacteristics: {
      convergenceSpeed: 'slow',
      noise: 0.002,
      startingLoss: 0.15
    }
  },
  
  '4': {
    id: '4',
    name: '道路网络提取',
    description: '卫星影像中的道路网络自动提取与矢量化',
    status: 'idle',
    modelArchitecture: 'YOLOv8m',
    trainingConfig: {
      batchSize: 12,
      learningRate: '1.00e-3',
      inputSize: '768x768',
      totalEpochs: 250,
      currentEpoch: 0
    },
    hardware: {
      gpuMemory: '0GB / 12GB',
      gpuUsage: 0
    },
    dataset: {
      totalSamples: 5420,
      processedSamples: 0,
      labelClasses: ['高速公路', '主干道', '支路', '乡村道路', '桥梁']
    },
    timing: {
      startTime: '-',
      epochTime: '-',
      estimatedRemaining: '-'
    },
    metrics: {
      mapAt50: 0,
      mapAt50_95: 0,
      precision: 0,
      recall: 0,
      boxLoss: 0,
      totalLoss: 0,
      trend: { mapAt50: 0, mapAt50_95: 0, boxLoss: 0 }
    },
    initialStepIndex: 0,
    lossCharacteristics: {
      convergenceSpeed: 'medium',
      noise: 0.002,
      startingLoss: 0.10
    }
  },
  
  '5': {
    id: '5',
    name: '土地利用分类',
    description: '基于多时相遥感影像的土地利用/覆盖分类',
    status: 'completed',
    modelArchitecture: 'TDA-YOLOv8l',
    trainingConfig: {
      batchSize: 8,
      learningRate: '2.00e-3',
      inputSize: '1280x1280',
      totalEpochs: 400,
      currentEpoch: 400
    },
    hardware: {
      gpuMemory: '11.2GB / 12GB',
      gpuUsage: 78
    },
    dataset: {
      totalSamples: 15600,
      processedSamples: 15600,
      labelClasses: ['森林', '水体', '农田', '城镇', '草地', '裸地', '湿地']
    },
    timing: {
      startTime: '前天 07:15',
      epochTime: '68s',
      estimatedRemaining: '已完成'
    },
    metrics: {
      mapAt50: 91.8,
      mapAt50_95: 74.6,
      precision: 89.2,
      recall: 87.4,
      boxLoss: 0.0102,
      totalLoss: 0.0298,
      trend: { mapAt50: 0.3, mapAt50_95: 0.2, boxLoss: -0.001 }
    },
    initialStepIndex: 5,
    lossCharacteristics: {
      convergenceSpeed: 'slow',
      noise: 0.0015,
      startingLoss: 0.08
    }
  },
  
  '6': {
    id: '6',
    name: '船舶目标检测',
    description: '港口和海域卫星影像中的船舶目标自动检测',
    status: 'training',
    modelArchitecture: 'YOLOv10n',
    trainingConfig: {
      batchSize: 20,
      learningRate: '1.50e-2',
      inputSize: '512x512',
      totalEpochs: 150,
      currentEpoch: 87
    },
    hardware: {
      gpuMemory: '7.4GB / 12GB',
      gpuUsage: 92
    },
    dataset: {
      totalSamples: 2800,
      processedSamples: 1624,
      labelClasses: ['货轮', '油轮', '渔船', '客轮', '军舰', '帆船']
    },
    timing: {
      startTime: '今天 10:45',
      epochTime: '38s',
      estimatedRemaining: '40m'
    },
    metrics: {
      mapAt50: 82.3,
      mapAt50_95: 65.8,
      precision: 79.5,
      recall: 76.2,
      boxLoss: 0.0245,
      totalLoss: 0.0567,
      trend: { mapAt50: 1.2, mapAt50_95: 0.9, boxLoss: -0.008 }
    },
    initialStepIndex: 2,
    lossCharacteristics: {
      convergenceSpeed: 'fast',
      noise: 0.002,
      startingLoss: 0.09
    }
  }
}

// 获取项目配置（带默认值回退）
export const getProjectConfig = (projectId: string): ProjectWorkspaceConfig => {
  return projectWorkspaceConfigs[projectId] || projectWorkspaceConfigs['2']
}

// 根据项目配置生成损失数据
export const generateProjectLossData = (config: ProjectWorkspaceConfig): YoloLossData => {
  const currentEpoch = Math.min(config.trainingConfig.currentEpoch, 100)
  const epochs = Array.from({ length: currentEpoch || 1 }, (_, i) => i + 1)
  
  const { convergenceSpeed, noise, startingLoss } = config.lossCharacteristics
  const decayRate = convergenceSpeed === 'fast' ? 40 : convergenceSpeed === 'medium' ? 25 : 15
  
  const boxLoss = epochs.map((_, i) => {
    const decay = Math.exp(-i / decayRate) * startingLoss * 0.8
    const noiseVal = (Math.random() - 0.5) * noise
    return Math.max(0.008, startingLoss * 0.15 + decay + noiseVal)
  })
  
  const clsLoss = epochs.map((_, i) => {
    const decay = Math.exp(-i / (decayRate * 1.2)) * startingLoss * 0.6
    const noiseVal = (Math.random() - 0.5) * noise * 0.8
    return Math.max(0.005, startingLoss * 0.1 + decay + noiseVal)
  })
  
  const objLoss = epochs.map((_, i) => {
    const decay = Math.exp(-i / (decayRate * 0.8)) * startingLoss * 0.5
    const noiseVal = (Math.random() - 0.5) * noise * 0.6
    return Math.max(0.004, startingLoss * 0.08 + decay + noiseVal)
  })
  
  const totalLoss = epochs.map((_, i) => boxLoss[i] + clsLoss[i] + objLoss[i])
  const valLoss = totalLoss.map((loss) => Math.max(0.02, loss * 1.15 + (Math.random() - 0.4) * noise * 2))
  
  return { epochs, boxLoss, clsLoss, objLoss, totalLoss, valLoss }
}

// 创建项目特定的 Job 状态流
export const createProjectJobStream = (
  projectId: string,
  callback: (status: JobStatus) => void,
  intervalMs = 2000
): (() => void) => {
  const config = getProjectConfig(projectId)
  
  const steps: JobStep[] = [
    { key: 'initialization', status: config.initialStepIndex > 0 ? 'completed' : 'running', progress: config.initialStepIndex > 0 ? 100 : 0 },
    { key: 'data_preparation', status: config.initialStepIndex > 1 ? 'completed' : config.initialStepIndex === 1 ? 'running' : 'pending', progress: config.initialStepIndex > 1 ? 100 : config.initialStepIndex === 1 ? Math.round((config.dataset.processedSamples / config.dataset.totalSamples) * 100) : 0 },
    { key: 'model_training', status: config.initialStepIndex > 2 ? 'completed' : config.initialStepIndex === 2 ? 'running' : 'pending', progress: config.initialStepIndex > 2 ? 100 : config.initialStepIndex === 2 ? Math.round((config.trainingConfig.currentEpoch / config.trainingConfig.totalEpochs) * 100) : 0 },
    { key: 'active_learning', status: config.initialStepIndex > 3 ? 'completed' : config.initialStepIndex === 3 ? 'running' : 'pending', progress: config.initialStepIndex > 3 ? 100 : 0 },
    { key: 'inference', status: config.initialStepIndex > 4 ? 'completed' : config.initialStepIndex === 4 ? 'running' : 'pending', progress: config.initialStepIndex > 4 ? 100 : 0 },
    { key: 'completed', status: config.initialStepIndex >= 5 ? 'completed' : 'pending', progress: config.initialStepIndex >= 5 ? 100 : 0 }
  ]
  
  let currentEpoch = config.trainingConfig.currentEpoch
  
  const getCurrentStep = (): string => {
    const runningStep = steps.find(s => s.status === 'running')
    return runningStep?.key || (config.status === 'completed' ? 'completed' : 'initialization')
  }
  
  const createStatus = (): JobStatus => ({
    id: `job-${projectId}-${Date.now()}`,
    projectId,
    status: config.status === 'completed' ? 'completed' : config.status === 'idle' ? 'idle' : 'running',
    currentStep: getCurrentStep(),
    steps: [...steps],
    metrics: {
      mapAt50: config.metrics.mapAt50,
      mapAt50_95: config.metrics.mapAt50_95,
      precision: config.metrics.precision,
      recall: config.metrics.recall,
      boxLoss: config.metrics.boxLoss,
      totalLoss: config.metrics.totalLoss
    },
    currentEpoch,
    totalEpochs: config.trainingConfig.totalEpochs,
    startTime: config.timing.startTime,
    estimatedRemaining: config.timing.estimatedRemaining
  })
  
  // 初始回调
  callback(createStatus())
  
  // 如果项目正在训练，模拟进度更新
  const interval = setInterval(() => {
    if (config.status === 'training' && currentEpoch < config.trainingConfig.totalEpochs) {
      currentEpoch++
      
      // 更新训练步骤进度
      const trainingStepIndex = steps.findIndex(s => s.key === 'model_training')
      if (trainingStepIndex !== -1) {
        steps[trainingStepIndex].progress = Math.round((currentEpoch / config.trainingConfig.totalEpochs) * 100)
      }
      
      // 缓慢增加指标
      config.metrics.mapAt50 = Math.min(95, config.metrics.mapAt50 + Math.random() * 0.3)
      config.metrics.mapAt50_95 = Math.min(80, config.metrics.mapAt50_95 + Math.random() * 0.2)
      config.metrics.precision = Math.min(95, config.metrics.precision + Math.random() * 0.2)
      config.metrics.recall = Math.min(92, config.metrics.recall + Math.random() * 0.2)
      config.metrics.boxLoss = Math.max(0.01, config.metrics.boxLoss - Math.random() * 0.001)
      config.metrics.totalLoss = Math.max(0.03, config.metrics.totalLoss - Math.random() * 0.002)
    }
    
    callback(createStatus())
  }, intervalMs)
  
  return () => clearInterval(interval)
}

// Agent 状态数据 - 根据项目状态调整
export const getProjectAgentStatuses = (projectId: string) => {
  const config = getProjectConfig(projectId)
  const baseStatuses = [
    {
      id: 'agent-1',
      name: '数据采集Agent',
      status: config.status === 'idle' ? 'idle' : 'active',
      lastActive: config.status === 'idle' ? '待启动' : '刚刚',
      tasksCompleted: config.dataset.processedSamples,
      icon: 'ph:database'
    },
    {
      id: 'agent-2',
      name: '标注验证Agent',
      status: config.status === 'labeling' ? 'active' : config.status === 'completed' ? 'idle' : 'idle',
      lastActive: config.status === 'labeling' ? '刚刚' : '无',
      tasksCompleted: Math.round(config.dataset.processedSamples * 0.85),
      icon: 'ph:check-square'
    },
    {
      id: 'agent-3',
      name: '模型训练Agent',
      status: config.status === 'training' ? 'active' : config.status === 'completed' ? 'idle' : 'idle',
      lastActive: config.status === 'training' ? '刚刚' : config.status === 'completed' ? '2小时前' : '无',
      tasksCompleted: config.trainingConfig.currentEpoch,
      icon: 'ph:brain'
    },
    {
      id: 'agent-4',
      name: '推理优化Agent',
      status: config.status === 'completed' ? 'idle' : 'idle',
      lastActive: config.status === 'completed' ? '1小时前' : '无',
      tasksCompleted: config.status === 'completed' ? config.dataset.totalSamples : 0,
      icon: 'ph:lightning'
    }
  ]
  
  return baseStatuses
}

