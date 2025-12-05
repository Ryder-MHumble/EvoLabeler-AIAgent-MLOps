/**
 * Mock Data Stream
 * 
 * 模拟 Agent 抓取回来的图像数据流
 * 包含不同来源、不同置信度的图像
 */

import type { ImageTask, BoundingBox } from '../types'

/**
 * 生成模拟的边界框（遥感影像场景）
 */
const generateBoundingBoxes = (count: number, baseConfidence: number): BoundingBox[] => {
  const labels = ['海上风电平台', '风机叶片', '支撑结构', '建筑物', '道路', '农田', '船舶']
  return Array.from({ length: count }, (_, i) => ({
    id: `bbox-${Date.now()}-${i}`,
    x: Math.random() * 0.6,
    y: Math.random() * 0.6,
    width: 0.15 + Math.random() * 0.25,
    height: 0.15 + Math.random() * 0.25,
    confidence: baseConfidence + (Math.random() - 0.5) * 0.2,
    label: labels[i % labels.length],
    status: 'pending' as const
  }))
}

/**
 * 模拟图像数据流
 */
export const mockImageStream: ImageTask[] = [
  {
    id: 'img-001',
    url: 'https://picsum.photos/seed/offshore1/800/600',
    thumbnailUrl: 'https://picsum.photos/seed/offshore1/200/150',
    source: 'crawler',
    status: 'incoming',
    confidence: 0.72,
    boundingBoxes: generateBoundingBoxes(2, 0.72).map((bbox, i) => ({
      ...bbox,
      label: i === 0 ? '海上风电平台' : '风机叶片'
    })),
    agentComment: '检测到海洋背景，存在人造金属结构，疑似海上风电平台。置信度中等，建议人工确认。',
    createdAt: new Date(Date.now() - 300000).toISOString()
  },
  {
    id: 'img-002',
    url: 'https://picsum.photos/seed/offshore2/800/600',
    thumbnailUrl: 'https://picsum.photos/seed/offshore2/200/150',
    source: 'crawler',
    status: 'pending',
    confidence: 0.85,
    boundingBoxes: generateBoundingBoxes(3, 0.85).map((bbox, i) => ({
      ...bbox,
      label: ['海上风电平台', '风机叶片', '支撑结构'][i] || '风机叶片'
    })),
    agentComment: '清晰的离岸平台结构，包含多个风机。阴影模式符合典型的风电平台特征。',
    createdAt: new Date(Date.now() - 600000).toISOString()
  },
  {
    id: 'img-003',
    url: 'https://picsum.photos/seed/offshore3/800/600',
    thumbnailUrl: 'https://picsum.photos/seed/offshore3/200/150',
    source: 'agent_recommended',
    status: 'pending',
    confidence: 0.68,
    boundingBoxes: generateBoundingBoxes(1, 0.68).map(bbox => ({
      ...bbox,
      label: '海上风电平台'
    })),
    agentComment: '识别出独特的阴影模式，典型的风电平台特征。但图像质量较低，需要进一步验证。',
    createdAt: new Date(Date.now() - 900000).toISOString()
  },
  {
    id: 'img-004',
    url: 'https://picsum.photos/seed/offshore4/800/600',
    thumbnailUrl: 'https://picsum.photos/seed/offshore4/200/150',
    source: 'manual',
    status: 'confirmed',
    confidence: 1.0,
    boundingBoxes: [
      {
        id: 'bbox-confirmed-1',
        x: 0.3,
        y: 0.2,
        width: 0.4,
        height: 0.5,
        confidence: 1.0,
        label: '海上风电平台',
        status: 'confirmed'
      }
    ],
    agentComment: '已确认标注。海上风电平台样本质量高，已加入训练集。',
    createdAt: new Date(Date.now() - 1200000).toISOString(),
    confirmedAt: new Date(Date.now() - 600000).toISOString()
  },
  {
    id: 'img-005',
    url: 'https://picsum.photos/seed/offshore5/800/600',
    thumbnailUrl: 'https://picsum.photos/seed/offshore5/200/150',
    source: 'crawler',
    status: 'incoming',
    confidence: 0.55,
    boundingBoxes: generateBoundingBoxes(1, 0.55).map(bbox => ({
      ...bbox,
      label: '疑似风电平台'
    })),
    agentComment: '置信度较低。可能是误检，建议人工审核。',
    createdAt: new Date(Date.now() - 180000).toISOString()
  },
  {
    id: 'img-006',
    url: 'https://picsum.photos/seed/offshore6/800/600',
    thumbnailUrl: 'https://picsum.photos/seed/offshore6/200/150',
    source: 'crawler',
    status: 'pending',
    confidence: 0.78,
    boundingBoxes: generateBoundingBoxes(2, 0.78).map((bbox, i) => ({
      ...bbox,
      label: i === 0 ? '海上风电平台' : '风机叶片'
    })),
    agentComment: '在 Google Earth 发现 10 张疑似图片，置信度 60%-80%，请确认。',
    createdAt: new Date(Date.now() - 1500000).toISOString()
  },
  {
    id: 'img-007',
    url: 'https://picsum.photos/seed/offshore7/800/600',
    thumbnailUrl: 'https://picsum.photos/seed/offshore7/200/150',
    source: 'manual',
    status: 'archived',
    confidence: 1.0,
    boundingBoxes: [
      {
        id: 'bbox-archived-1',
        x: 0.25,
        y: 0.3,
        width: 0.5,
        height: 0.4,
        confidence: 1.0,
        label: '海上风电平台',
        status: 'confirmed'
      }
    ],
    agentComment: '已归档。样本 +1，模型对"海上风电平台"的理解已更新。',
    createdAt: new Date(Date.now() - 3600000).toISOString(),
    confirmedAt: new Date(Date.now() - 3000000).toISOString()
  }
]

/**
 * 获取数据流
 */
export const fetchImageStream = async (category?: 'incoming' | 'pending' | 'library'): Promise<ImageTask[]> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      if (category === 'incoming') {
        resolve(mockImageStream.filter(img => img.status === 'incoming'))
      } else if (category === 'pending') {
        resolve(mockImageStream.filter(img => img.status === 'pending'))
      } else if (category === 'library') {
        resolve(mockImageStream.filter(img => img.status === 'confirmed' || img.status === 'archived'))
      } else {
        resolve(mockImageStream)
      }
    }, 300)
  })
}

/**
 * 更新图像任务状态
 */
export const updateImageTaskStatus = async (
  id: string,
  status: ImageTask['status']
): Promise<ImageTask> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const task = mockImageStream.find(img => img.id === id)
      if (task) {
        task.status = status
        if (status === 'confirmed' || status === 'archived') {
          task.confirmedAt = new Date().toISOString()
          // 将所有边界框标记为已确认
          task.boundingBoxes.forEach(bbox => {
            bbox.status = 'confirmed'
          })
        }
        resolve(task)
      } else {
        throw new Error(`Image task ${id} not found`)
      }
    }, 200)
  })
}

/**
 * 更新边界框状态
 */
export const updateBoundingBox = async (
  imageId: string,
  bboxId: string,
  updates: Partial<BoundingBox>
): Promise<BoundingBox> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const task = mockImageStream.find(img => img.id === imageId)
      if (task) {
        const bbox = task.boundingBoxes.find(b => b.id === bboxId)
        if (bbox) {
          Object.assign(bbox, updates)
          resolve(bbox)
        } else {
          throw new Error(`Bounding box ${bboxId} not found`)
        }
      } else {
        throw new Error(`Image task ${imageId} not found`)
      }
    }, 200)
  })
}


