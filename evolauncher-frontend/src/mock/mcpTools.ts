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
    description: 'Analyzes geospatial context to prioritize acquisition regions.',
    latency: 180,
    usage: 68,
    status: 'online'
  },
  {
    id: 'keyword-optimizer',
    name: 'keyword_optimizer',
    description: 'Synthesizes search prompts for the acquisition agent.',
    latency: 220,
    usage: 54,
    status: 'online'
  },
  {
    id: 'quality-guardian',
    name: 'quality_guardian',
    description: 'Ensures pseudo labels meet confidence thresholds.',
    latency: 260,
    usage: 47,
    status: 'degraded'
  },
  {
    id: 'uncertainty-oracle',
    name: 'uncertainty_oracle',
    description: 'Quantifies epistemic uncertainty for active learning.',
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

