/**
 * API Type Definitions
 * 
 * 定义 "任务指挥官" 故事中的核心数据类型
 * 这些类型用于描述 Mission、ImageTask、Agent 分析结果等
 */

/**
 * 任务状态枚举
 */
export type MissionStatus = 'idle' | 'scouting' | 'training' | 'labeling' | 'completed'

/**
 * 任务 (Mission) - 代表一个完整的标注任务
 */
export interface Mission {
  id: string
  name: string
  description?: string
  status: MissionStatus
  progress: number // 0-100
  seedImages: string[] // 种子图片 URL 列表
  createdAt: string
  updatedAt: string
  metadata?: Record<string, any>
}

/**
 * 图像任务状态
 */
export type ImageTaskStatus = 'incoming' | 'pending' | 'confirmed' | 'archived'

/**
 * 图像来源
 */
export type ImageSource = 'crawler' | 'manual' | 'agent_recommended'

/**
 * 边界框 (BoundingBox) - 用于标注目标对象
 */
export interface BoundingBox {
  id: string
  x: number // 左上角 x 坐标 (0-1 归一化)
  y: number // 左上角 y 坐标 (0-1 归一化)
  width: number // 宽度 (0-1 归一化)
  height: number // 高度 (0-1 归一化)
  confidence: number // 置信度 (0-1)
  label?: string // 标签名称
  status: 'pending' | 'confirmed' // 待确认或已确认
}

/**
 * 图像任务 (ImageTask) - 代表一张待处理或已处理的图像
 */
export interface ImageTask {
  id: string
  url: string
  thumbnailUrl?: string
  source: ImageSource
  status: ImageTaskStatus
  confidence: number // Agent 的总体置信度 (0-1)
  boundingBoxes: BoundingBox[]
  agentComment?: string // Agent 的分析评论
  createdAt: string
  confirmedAt?: string
}

/**
 * Agent 日志级别
 */
export type AgentLogLevel = 'info' | 'warning' | 'error' | 'success'

/**
 * Agent 日志 (AgentLog) - 代表 Agent 的思考过程
 */
export interface AgentLog {
  id: string
  timestamp: string
  level: AgentLogLevel
  category: string // 如 'Perception', 'Decision', 'Action'
  message: string
  metadata?: Record<string, any>
}

/**
 * Agent 分析结果 - VLM 对当前图像的分析
 */
export interface AgentAnalysis {
  imageId: string
  confidence: number // 总体置信度
  detectedObjects: Array<{
    label: string
    confidence: number
    description: string
  }>
  sceneDescription: string // 场景描述
  recommendations?: string[] // Agent 的建议
}

/**
 * 数据流分类
 */
export type DataStreamCategory = 'incoming' | 'pending' | 'library'

/**
 * 数据流统计
 */
export interface DataStreamStats {
  incoming: number
  pending: number
  library: number
  total: number
}


