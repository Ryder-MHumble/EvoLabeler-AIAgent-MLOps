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

// Generate placeholder image URLs (using picsum.photos for demo)
const getPlaceholderImage = (seed: number) => {
  return `https://picsum.photos/seed/${seed}/400/300`
}

export const mockProjects: Project[] = [
  {
    id: '1',
    name: 'Wildlife Classification',
    imageCount: 1250,
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-01-20T14:22:00Z',
    status: 'completed',
    thumbnailUrl: getPlaceholderImage(101),
    description: 'Automated labeling for wildlife species identification',
    accuracy: 94.5
  },
  {
    id: '2',
    name: 'Medical Imaging Dataset',
    imageCount: 3420,
    createdAt: '2024-01-18T09:15:00Z',
    updatedAt: '2024-01-22T16:45:00Z',
    status: 'training',
    thumbnailUrl: getPlaceholderImage(202),
    description: 'X-ray and CT scan annotation project',
    accuracy: 87.2
  },
  {
    id: '3',
    name: 'Urban Traffic Analysis',
    imageCount: 8750,
    createdAt: '2024-01-20T13:20:00Z',
    updatedAt: '2024-01-23T11:30:00Z',
    status: 'labeling',
    thumbnailUrl: getPlaceholderImage(303),
    description: 'Vehicle and pedestrian detection in city environments'
  },
  {
    id: '4',
    name: 'Product Catalog',
    imageCount: 542,
    createdAt: '2024-01-22T08:45:00Z',
    updatedAt: '2024-01-22T08:45:00Z',
    status: 'idle',
    thumbnailUrl: getPlaceholderImage(404),
    description: 'E-commerce product categorization'
  },
  {
    id: '5',
    name: 'Satellite Imagery',
    imageCount: 15600,
    createdAt: '2024-01-10T07:00:00Z',
    updatedAt: '2024-01-24T19:15:00Z',
    status: 'completed',
    thumbnailUrl: getPlaceholderImage(505),
    description: 'Land use classification from satellite data',
    accuracy: 91.8
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

