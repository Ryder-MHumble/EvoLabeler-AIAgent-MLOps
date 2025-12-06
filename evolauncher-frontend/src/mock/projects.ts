import { withRetry } from '@/utils/retry'

/**
 * Mock Project Data
 * 
 * Simulates backend data for project cards.
 * In production, this would be replaced by API calls to the backend.
 * 
 * Design Intent: Provide realistic test data that showcases the UI's
 * ability to handle various project states and metadata.
 */

export interface Project {
  id: string
  name: string
  imageCount: number
  createdAt: string
  updatedAt: string
  status: 'idle' | 'training' | 'labeling' | 'completed'
  thumbnailUrl: string
  description?: string
  accuracy?: number
}

/**
 * 使用 Unsplash 提供更具代表性的图片
 * 每个项目的图片都与其主题相关
 */
export const mockProjects: Project[] = [
  {
    id: '1',
    name: '海上风电平台检测',
    imageCount: 3420,
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-01-20T14:22:00Z',
    status: 'completed',
    // 海上风力发电机组图像
    thumbnailUrl: 'https://images.unsplash.com/photo-1532601224476-15c79f2f7a51?w=400&h=300&fit=crop',
    description: '基于卫星影像的海上风电平台自动检测与标注',
    accuracy: 94.5
  },
  {
    id: '2',
    name: '建筑物提取',
    imageCount: 8750,
    createdAt: '2024-01-18T09:15:00Z',
    updatedAt: '2024-01-22T16:45:00Z',
    status: 'training',
    // 城市建筑鸟瞰图
    thumbnailUrl: 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=400&h=300&fit=crop',
    description: '高分辨率遥感影像中的建筑物轮廓提取与分类',
    accuracy: 87.2
  },
  {
    id: '3',
    name: '农田边界识别',
    imageCount: 1250,
    createdAt: '2024-01-20T13:20:00Z',
    updatedAt: '2024-01-23T11:30:00Z',
    status: 'labeling',
    // 农田航拍图
    thumbnailUrl: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400&h=300&fit=crop',
    description: '多光谱遥感影像的农田边界自动识别与面积计算'
  },
  {
    id: '4',
    name: '道路网络提取',
    imageCount: 5420,
    createdAt: '2024-01-22T08:45:00Z',
    updatedAt: '2024-01-22T08:45:00Z',
    status: 'idle',
    // 高速公路交叉口鸟瞰图
    thumbnailUrl: 'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=400&h=300&fit=crop',
    description: '卫星影像中的道路网络自动提取与矢量化'
  },
  {
    id: '5',
    name: '土地利用分类',
    imageCount: 15600,
    createdAt: '2024-01-10T07:00:00Z',
    updatedAt: '2024-01-24T19:15:00Z',
    status: 'completed',
    // 卫星遥感影像 - 多种地类
    thumbnailUrl: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&h=300&fit=crop',
    description: '基于多时相遥感影像的土地利用/覆盖分类',
    accuracy: 91.8
  },
  {
    id: '6',
    name: '船舶目标检测',
    imageCount: 2800,
    createdAt: '2024-01-25T11:20:00Z',
    updatedAt: '2024-01-26T15:30:00Z',
    status: 'training',
    // 港口船舶航拍图
    thumbnailUrl: 'https://images.unsplash.com/photo-1605281317010-fe5ffe798166?w=400&h=300&fit=crop',
    description: '港口和海域卫星影像中的船舶目标自动检测',
    accuracy: 82.3
  }
]

/**
 * Simulate API delay for realistic loading states
 */
export const fetchProjects = (): Promise<Project[]> => {
  return withRetry<Project[]>(() => {
    return new Promise((resolve, reject) => {
      // Simulate network delay of 1-2 seconds
      const delay = 1000 + Math.random() * 1000

      setTimeout(() => {
        // 15% chance to simulate transient failure to exercise retry logic
        if (Math.random() < 0.15) {
          reject(new Error('Mock network error: failed to fetch projects'))
          return
        }

        resolve(mockProjects)
      }, delay)
    })
  })
}

/**
 * Get project by ID
 */
export const fetchProjectById = (id: string): Promise<Project | undefined> => {
  return withRetry<Project | undefined>(() => {
    return new Promise((resolve, reject) => {
      const delay = 500 + Math.random() * 500
      setTimeout(() => {
        const project = mockProjects.find((p) => p.id === id)
        if (!project) {
          reject(new Error(`Project with id ${id} not found`))
          return
        }
        resolve(project)
      }, delay)
    })
  })
}
