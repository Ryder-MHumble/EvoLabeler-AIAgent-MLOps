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
    displayName: 'Inference Agent',
    description: 'Runs the base detector and produces uncertainty estimates for active learning.',
    status: 'running',
    mood: 'stable',
    confidence: 0.92,
    throughput: 420,
    lastTask: 'Batch inference on Sentinel-2 imagery',
    nextAction: 'Publish uncertainty heatmap',
    metrics: {
      processed: 1280,
      queued: 360,
      successRate: 0.97
    }
  },
  {
    id: 'agent-analysis',
    name: 'AnalysisAgent',
    displayName: 'Analysis Agent',
    description: 'Combines LLM + VLM reasoning to plan the next acquisition cycle.',
    status: 'running',
    mood: 'alert',
    confidence: 0.88,
    throughput: 260,
    lastTask: 'Semantic clustering for coastal imagery',
    nextAction: 'Synthesize keyword prompts for MCP tools',
    metrics: {
      processed: 760,
      queued: 120,
      successRate: 0.9
    }
  },
  {
    id: 'agent-acquisition',
    name: 'AcquisitionAgent',
    displayName: 'Acquisition Agent',
    description: 'Harvests new samples, applies auto-labeling and quality filtering.',
    status: 'running',
    mood: 'stable',
    confidence: 0.86,
    throughput: 310,
    lastTask: 'Playwright crawler - high-altitude ports dataset',
    nextAction: 'Trigger quality gate via MCP::quality_guardian',
    metrics: {
      processed: 540,
      queued: 210,
      successRate: 0.93
    }
  },
  {
    id: 'agent-training',
    name: 'TrainingAgent',
    displayName: 'Training Agent',
    description: 'Curates datasets, tunes configs and supervises the training loop.',
    status: 'waiting',
    mood: 'stable',
    confidence: 0.94,
    throughput: 180,
    lastTask: 'Generated adaptive YOLO training config',
    nextAction: 'Warm restart with pseudo-labeled batch',
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

