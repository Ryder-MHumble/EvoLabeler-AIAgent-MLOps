import { withRetry } from '@/utils/retry'

export type AgentMood = 'stable' | 'alert' | 'critical'

export interface AgentStatus {
  id: string
  name: 'InferenceAgent' | 'AnalysisAgent' | 'AcquisitionAgent' | 'TrainingAgent'
  displayName: string
  description: string
  status: 'idle' | 'running' | 'paused' | 'waiting'
  mood: AgentMood
  confidence: number
  throughput: number
  lastTask: string
  nextAction: string
  metrics: {
    processed: number
    queued: number
    successRate: number
  }
}

const demoAgents: AgentStatus[] = [
  {
    id: 'agent-inference',
    name: 'InferenceAgent',
    displayName: '推理智能体',
    description: '运行基础检测器并为主动学习生成不确定性估计',
    status: 'running',
    mood: 'stable',
    confidence: 0.92,
    throughput: 420,
    lastTask: '对 Sentinel-2 影像执行批量推理',
    nextAction: '发布不确定性热力图',
    metrics: {
      processed: 1280,
      queued: 360,
      successRate: 0.97
    }
  },
  {
    id: 'agent-analysis',
    name: 'AnalysisAgent',
    displayName: '分析智能体',
    description: '结合大语言模型与视觉语言模型推理规划下一轮数据获取周期',
    status: 'running',
    mood: 'alert',
    confidence: 0.88,
    throughput: 260,
    lastTask: '对海岸影像进行语义聚类分析',
    nextAction: '为MCP工具合成关键词提示',
    metrics: {
      processed: 760,
      queued: 120,
      successRate: 0.9
    }
  },
  {
    id: 'agent-acquisition',
    name: 'AcquisitionAgent',
    displayName: '采集智能体',
    description: '收集新样本，应用自动标注和质量过滤机制',
    status: 'running',
    mood: 'stable',
    confidence: 0.86,
    throughput: 310,
    lastTask: 'Playwright爬虫 - 高海拔港口数据集',
    nextAction: '通过 MCP::quality_guardian 触发质量门控',
    metrics: {
      processed: 540,
      queued: 210,
      successRate: 0.93
    }
  },
  {
    id: 'agent-training',
    name: 'TrainingAgent',
    displayName: '训练智能体',
    description: '策划数据集，调优配置并监督训练循环',
    status: 'waiting',
    mood: 'stable',
    confidence: 0.94,
    throughput: 180,
    lastTask: '生成自适应YOLO训练配置',
    nextAction: '使用伪标签批次进行热重启',
    metrics: {
      processed: 380,
      queued: 64,
      successRate: 0.95
    }
  }
]

export const fetchAgentStatuses = (): Promise<AgentStatus[]> => {
  return withRetry(() => {
    return new Promise<AgentStatus[]>((resolve) => {
      const delay = 600 + Math.random() * 800
      setTimeout(() => {
        resolve(demoAgents)
      }, delay)
    })
  })
}

