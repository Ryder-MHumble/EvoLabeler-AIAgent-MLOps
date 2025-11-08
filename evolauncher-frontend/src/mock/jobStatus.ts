/**
 * Mock Job Status Data
 * 
 * Simulates real-time job progress updates from the backend.
 * Creates a stream of status updates to demonstrate dynamic UI updates.
 * 
 * Design Intent: Show how the application handles evolving job states,
 * enabling realistic testing of progress indicators and step transitions.
 */

export type JobStep = 
  | 'initialization'
  | 'data_preparation'
  | 'model_training'
  | 'active_learning'
  | 'inference'
  | 'completed'

export interface JobStatus {
  id: string
  projectId: string
  currentStep: JobStep
  progress: number // 0-100
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed'
  startedAt: string
  estimatedCompletion?: string
  metrics?: {
    accuracy?: number
    loss?: number
    samplesProcessed?: number
    totalSamples?: number
  }
  logs: string[]
}

const stepSequence: JobStep[] = [
  'initialization',
  'data_preparation',
  'model_training',
  'active_learning',
  'inference',
  'completed'
]

/**
 * Generate a realistic job status
 */
const createJobStatus = (step: number, progress: number): JobStatus => {
  const currentStep = stepSequence[Math.min(step, stepSequence.length - 1)]
  
  return {
    id: 'job-demo-001',
    projectId: '2',
    currentStep,
    progress,
    status: step >= stepSequence.length - 1 ? 'completed' : 'running',
    startedAt: new Date(Date.now() - 3600000).toISOString(),
    estimatedCompletion: new Date(Date.now() + 1800000).toISOString(),
    metrics: {
      accuracy: Math.min(0.5 + (progress / 100) * 0.45, 0.95),
      loss: Math.max(2.5 - (progress / 100) * 2.0, 0.5),
      samplesProcessed: Math.floor((progress / 100) * 3420),
      totalSamples: 3420
    },
    logs: generateLogs(currentStep, progress)
  }
}

/**
 * Generate realistic log messages based on current step
 */
const generateLogs = (step: JobStep, progress: number): string[] => {
  const logs: string[] = []
  
  switch (step) {
    case 'initialization':
      logs.push('[INFO] Job initialized successfully')
      logs.push('[INFO] Loading configuration...')
      if (progress > 30) logs.push('[INFO] Allocating GPU resources...')
      if (progress > 60) logs.push('[INFO] Setting up distributed training environment...')
      break
    case 'data_preparation':
      logs.push('[INFO] Loading dataset from storage...')
      logs.push('[INFO] Preprocessing images...')
      if (progress > 40) logs.push('[INFO] Applying data augmentation...')
      if (progress > 70) logs.push('[INFO] Creating train/validation split...')
      break
    case 'model_training':
      logs.push('[INFO] Initializing neural network...')
      logs.push(`[INFO] Epoch ${Math.floor(progress / 10)}/10`)
      logs.push(`[INFO] Training accuracy: ${(0.5 + (progress / 200)).toFixed(3)}`)
      if (progress > 50) logs.push('[INFO] Validation accuracy improving...')
      break
    case 'active_learning':
      logs.push('[INFO] Selecting samples with high uncertainty...')
      logs.push('[INFO] Querying oracle for labels...')
      if (progress > 30) logs.push('[INFO] Updating model with new samples...')
      if (progress > 70) logs.push('[INFO] Convergence criteria met...')
      break
    case 'inference':
      logs.push('[INFO] Running inference on unlabeled data...')
      logs.push(`[INFO] Processed ${Math.floor(progress * 34.2)}/3420 images`)
      if (progress > 80) logs.push('[INFO] Generating confidence scores...')
      break
    case 'completed':
      logs.push('[SUCCESS] Job completed successfully!')
      logs.push('[INFO] Final accuracy: 94.5%')
      logs.push('[INFO] Results saved to database')
      break
  }
  
  return logs
}

/**
 * Create a job status stream that updates over time
 * 
 * This simulates polling the backend for job updates.
 * Returns a function to stop the updates and a callback to receive updates.
 */
export const createJobStatusStream = (
  callback: (status: JobStatus) => void,
  interval: number = 2000
): () => void => {
  let step = 0
  let progress = 0
  let timer: number
  
  const update = () => {
    // Increment progress
    progress += Math.random() * 10 + 5
    
    // Move to next step when progress exceeds 100
    if (progress >= 100 && step < stepSequence.length - 1) {
      step++
      progress = 0
    }
    
    // Cap progress at 100
    progress = Math.min(progress, 100)
    
    // Generate and emit status
    const status = createJobStatus(step, progress)
    callback(status)
    
    // Stop when completed
    if (step >= stepSequence.length - 1 && progress >= 100) {
      clearInterval(timer)
    }
  }
  
  // Start updates
  timer = window.setInterval(update, interval)
  
  // Initial update
  update()
  
  // Return cleanup function
  return () => {
    clearInterval(timer)
  }
}

/**
 * Get a single job status snapshot (for testing)
 */
export const fetchJobStatus = (jobId: string): Promise<JobStatus> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(createJobStatus(2, 45))
    }, 500)
  })
}

