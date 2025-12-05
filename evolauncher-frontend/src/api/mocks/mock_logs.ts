/**
 * Mock Agent Logs
 * 
 * 模拟 Agent 的思考过程日志
 * 展示 Agent 的每一步决策和分析
 */

import type { AgentLog } from '../types'

/**
 * 生成模拟日志
 */
const generateLogs = (): AgentLog[] => {
  const now = Date.now()
  const logs: AgentLog[] = []

  // 添加一些历史日志
  logs.push({
    id: `log-${now - 5000}`,
    timestamp: new Date(now - 5000).toISOString(),
    level: 'info',
    category: 'Perception',
    message: '正在分析批次 #42...',
    metadata: { batchId: 'batch-42', imageCount: 10 }
  })

  logs.push({
    id: `log-${now - 4000}`,
    timestamp: new Date(now - 4000).toISOString(),
    level: 'info',
    category: 'Decision',
    message: 'img_882 置信度较低。请求人工审核。',
    metadata: { imageId: 'img-882', confidence: 0.55 }
  })

  logs.push({
    id: `log-${now - 3000}`,
    timestamp: new Date(now - 3000).toISOString(),
    level: 'success',
    category: 'Action',
    message: '在 Google Earth 发现了 10 张疑似图片，置信度 60%-80%',
    metadata: { source: 'google_earth', count: 10, confidenceRange: [0.6, 0.8] }
  })

  logs.push({
    id: `log-${now - 2000}`,
    timestamp: new Date(now - 2000).toISOString(),
    level: 'info',
    category: 'Perception',
    message: '识别出独特的阴影模式，典型的风机特征',
    metadata: { pattern: 'shadow_pattern', confidence: 0.68 }
  })

  logs.push({
    id: `log-${now - 1000}`,
    timestamp: new Date(now - 1000).toISOString(),
    level: 'info',
    category: 'Decision',
    message: '样本 +1，模型对"风机叶片"的理解已更新',
    metadata: { sampleCount: 20, modelUpdate: true }
  })

  return logs
}

/**
 * 当前日志列表
 */
let currentLogs: AgentLog[] = generateLogs()

/**
 * 获取所有日志
 */
export const fetchAgentLogs = async (): Promise<AgentLog[]> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([...currentLogs])
    }, 200)
  })
}

/**
 * 创建日志流 - 模拟实时日志推送
 */
export const createAgentLogStream = (
  callback: (log: AgentLog) => void,
  interval: number = 3000
): () => void => {
  const logTemplates = [
    {
      level: 'info' as const,
      category: 'Perception',
      messages: [
        '正在分析图像特征...',
        '检测到海洋背景，存在人造金属结构...',
        '分析批次 #43...',
        '计算置信度分数...'
      ]
    },
    {
      level: 'info' as const,
      category: 'Decision',
      messages: [
        '置信度低，请求人工审核',
        '置信度高，建议自动确认',
        '检测到新样本，加入训练队列',
        '样本质量评估完成'
      ]
    },
    {
      level: 'success' as const,
      category: 'Action',
      messages: [
        '已抓取 5 张新图片',
        '模型微调训练完成',
        '知识库已更新',
        '标注任务已完成'
      ]
    },
    {
      level: 'warning' as const,
      category: 'Decision',
      messages: [
        '图像质量较低，需要进一步验证',
        '检测到异常模式，建议人工检查',
        '置信度波动较大'
      ]
    }
  ]

  let logIndex = 0

  const timer = setInterval(() => {
    const template = logTemplates[Math.floor(Math.random() * logTemplates.length)]
    const message = template.messages[Math.floor(Math.random() * template.messages.length)]
    
    const newLog: AgentLog = {
      id: `log-${Date.now()}-${Math.random()}`,
      timestamp: new Date().toISOString(),
      level: template.level,
      category: template.category,
      message: `[${template.category}] ${message}`
    }

    // 添加到当前日志列表
    currentLogs.push(newLog)
    
    // 保持最多 100 条日志
    if (currentLogs.length > 100) {
      currentLogs = currentLogs.slice(-100)
    }

    // 调用回调
    callback(newLog)
    
    logIndex++
  }, interval)

  // 返回清理函数
  return () => {
    clearInterval(timer)
  }
}

/**
 * 清除所有日志
 */
export const clearAgentLogs = (): void => {
  currentLogs = []
}


