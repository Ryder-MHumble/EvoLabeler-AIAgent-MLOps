/**
 * 标注相关常量定义
 */

// 工具类型
export type ToolType = 'select' | 'draw' | 'pan'

// 缩放配置
export const ZOOM_CONFIG = {
  MIN: 0.25,
  MAX: 5,
  STEP: 0.25
} as const

// 标签选项
export const LABEL_OPTIONS = [
  '海上风电平台',
  '风机叶片',
  '支撑结构',
  '建筑物',
  '道路',
  '农田',
  '船舶',
  '其他'
] as const

// 置信度阈值
export const CONFIDENCE_THRESHOLDS = {
  HIGH: 0.8,
  MEDIUM: 0.6
} as const

// 置信度颜色映射
export const CONFIDENCE_COLORS = {
  HIGH: '#10b981',    // emerald
  MEDIUM: '#eab308',  // yellow
  LOW: '#f97316'      // orange
} as const

// 最小边界框尺寸（归一化坐标）
export const MIN_BBOX_SIZE = 0.02

// 调整手柄
export const RESIZE_HANDLES = ['nw', 'ne', 'sw', 'se', 'n', 's', 'e', 'w'] as const

// 日志最大条数
export const MAX_LOG_ENTRIES = 200

// 图像适应容器的缩放比例
export const IMAGE_FIT_SCALE = 0.95

