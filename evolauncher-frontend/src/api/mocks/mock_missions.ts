/**
 * Mock Missions Data
 * 
 * 故事驱动的任务数据 - "海上风电平台检测" 任务
 * 展示任务状态、进度等信息
 */

import type { Mission } from '../types'

/**
 * 模拟任务数据
 */
export const mockMissions: Mission[] = [
  {
    id: 'mission-001',
    name: '海上风电平台检测',
    description: '使用 AI Agent 自动搜索和标注全球范围内的海上风电平台',
    status: 'scouting',
    progress: 45,
    seedImages: [
      'https://picsum.photos/seed/wind1/400/300',
      'https://picsum.photos/seed/wind2/400/300',
      'https://picsum.photos/seed/wind3/400/300'
    ],
    createdAt: new Date(Date.now() - 86400000 * 2).toISOString(), // 2天前
    updatedAt: new Date().toISOString(),
    metadata: {
      targetObject: '海上风电平台',
      detectionMethod: 'VLM + 主动学习',
      expectedSamples: 1000
    }
  },
  {
    id: 'mission-002',
    name: '城市建筑识别',
    description: '识别和分类城市中的不同类型建筑',
    status: 'training',
    progress: 72,
    seedImages: [
      'https://picsum.photos/seed/building1/400/300'
    ],
    createdAt: new Date(Date.now() - 86400000 * 5).toISOString(),
    updatedAt: new Date().toISOString(),
    metadata: {
      targetObject: '建筑物',
      detectionMethod: 'YOLO + 半监督学习'
    }
  },
  {
    id: 'mission-003',
    name: '农田边界检测',
    description: '自动检测农田边界并计算面积',
    status: 'idle',
    progress: 0,
    seedImages: [],
    createdAt: new Date(Date.now() - 86400000).toISOString(),
    updatedAt: new Date(Date.now() - 86400000).toISOString(),
    metadata: {
      targetObject: '农田',
      detectionMethod: '语义分割'
    }
  }
]

/**
 * 获取所有任务
 */
export const fetchMissions = async (): Promise<Mission[]> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(mockMissions)
    }, 500)
  })
}

/**
 * 根据 ID 获取任务
 */
export const fetchMissionById = async (id: string): Promise<Mission | undefined> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const mission = mockMissions.find(m => m.id === id)
      resolve(mission)
    }, 300)
  })
}

/**
 * 更新任务状态
 */
export const updateMissionStatus = async (
  id: string,
  status: Mission['status'],
  progress?: number
): Promise<Mission> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const mission = mockMissions.find(m => m.id === id)
      if (mission) {
        mission.status = status
        if (progress !== undefined) {
          mission.progress = progress
        }
        mission.updatedAt = new Date().toISOString()
        resolve(mission)
      } else {
        throw new Error(`Mission ${id} not found`)
      }
    }, 200)
  })
}


