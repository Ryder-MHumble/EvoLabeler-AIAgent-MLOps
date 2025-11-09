import { withRetry } from '@/utils/retry'

export interface McpToolStatus {
  id: string
  name: string
  description: string
  latency: number
  usage: number
  status: 'online' | 'degraded' | 'offline'
}

const registry: McpToolStatus[] = [
  {
    id: 'scene-annotator',
    name: 'scene_classifier',
    description: '分析地理空间上下文以优先选择采集区域',
    latency: 180,
    usage: 68,
    status: 'online'
  },
  {
    id: 'keyword-optimizer',
    name: 'keyword_optimizer',
    description: '为采集智能体合成搜索提示词',
    latency: 220,
    usage: 54,
    status: 'online'
  },
  {
    id: 'quality-guardian',
    name: 'quality_guardian',
    description: '确保伪标签满足置信度阈值要求',
    latency: 260,
    usage: 47,
    status: 'degraded'
  },
  {
    id: 'uncertainty-oracle',
    name: 'uncertainty_oracle',
    description: '量化主动学习的认知不确定性',
    latency: 150,
    usage: 73,
    status: 'online'
  }
]

export const fetchMcpToolStatus = (): Promise<McpToolStatus[]> => {
  return withRetry(() => {
    return new Promise<McpToolStatus[]>((resolve) => {
      const delay = 400 + Math.random() * 600
      setTimeout(() => resolve(registry), delay)
    })
  })
}

