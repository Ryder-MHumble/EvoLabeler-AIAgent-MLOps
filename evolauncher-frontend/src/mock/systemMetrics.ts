export interface SystemMetric {
  id: string
  label: string
  value: number
  unit: string
  trend: 'up' | 'down' | 'steady'
  delta: number
  description: string
}

export const systemMetrics: SystemMetric[] = [
  {
    id: 'active-loops',
    label: '主动学习循环',
    value: 3,
    unit: '',
    trend: 'up',
    delta: 1,
    description: '残差编排架构当前追踪三个反馈循环'
  },
  {
    id: 'uncertainty-drop',
    label: '不确定性降低',
    value: 37,
    unit: '%',
    trend: 'down',
    delta: 12,
    description: '最新数据采集后整体认知不确定性已降低'
  },
  {
    id: 'auto-labeled',
    label: '自动标注样本',
    value: 9850,
    unit: '',
    trend: 'up',
    delta: 620,
    description: '质量守护者MCP工具生成的高质量伪标注'
  },
  {
    id: 'deployment-latency',
    label: '部署延迟',
    value: 450,
    unit: 'ms',
    trend: 'steady',
    delta: 5,
    description: '当前部署模型的平均推理延迟'
  }
]

