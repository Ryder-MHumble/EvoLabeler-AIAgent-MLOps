/**
 * Workspace 模块类型定义
 */

import type { JobStatus, JobStep } from '@/mock/jobStatus'
import type { AgentStatus } from '@/mock/agents'
import type { McpToolStatus } from '@/mock/mcpTools'

// 步骤配置
export interface StepConfig {
  key: JobStep
  label: string
  icon: string
}

// YOLO 损失数据
export interface YoloLossData {
  epochs: number[]
  boxLoss: number[]
  clsLoss: number[]
  objLoss: number[]
  totalLoss: number[]
  valLoss: number[]
}

// 项目信息
export interface ProjectInfo {
  id: string | string[]
  name: string
  status: 'idle' | 'training' | 'completed' | 'paused'
}

// 导出常用类型
export type { JobStatus, JobStep, AgentStatus, McpToolStatus }

