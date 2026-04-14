import type {
  BoundingBox,
  ImageAnalysisSummary,
  ImageTask,
  Mission,
  QueueState,
} from '@/api/types'
import type {
  EvoRound,
  MetricsHistoryEntry,
  ModelHealthResponse,
  ModelVersion,
} from '@/api/models'
import type { YoloLossData } from '@/components/workspace/types'
import type { JobStatus, JobStep } from '@/mock/jobStatus'
import type { Project } from '@/mock/projects'
import { mockImageStream } from '@/api/mocks/mock_stream'
import { getProjectConfig } from '@/mock/projectWorkspaceData'

export type ProjectStage =
  | 'draft'
  | 'seed'
  | 'annotate'
  | 'train'
  | 'loop'
  | 'completed'

export type DemoChapterKey =
  | 'project_initialized'
  | 'seed_data_processing'
  | 'copilot_annotation'
  | 'round_1_training'
  | 'active_learning_loop'

export interface ProjectAction {
  label: string
  description: string
  to: 'overview' | 'annotate' | 'train'
}

export interface ActivityItem {
  id: string
  timestamp: string
  title: string
  detail: string
  tone: 'info' | 'success' | 'warning' | 'loop'
}

export interface WorkItem extends ImageTask {
  projectId: string
  queueState: QueueState
  readyForCompletion: boolean
  analysis: ImageAnalysisSummary
}

export interface QueueSummary {
  total: number
  ready: number
  review: number
  imported: number
  done: number
  completionRate: number
}

export interface TrainSummary {
  headline: string
  currentRound: number
  maxRounds: number
  activeVersion: string
  bestVersion: string
  latestMap50: number
  precision: number
  recall: number
}

export interface JourneyTrainState {
  jobStatus: JobStatus | null
  lossData: YoloLossData
  evoRounds: EvoRound[]
  modelVersions: ModelVersion[]
  healthReport: ModelHealthResponse | null
  metricsHistory: MetricsHistoryEntry[]
}

export interface JourneySnapshot {
  stage: ProjectStage
  headline: string
  narrative: string
  nextRecommendedAction: ProjectAction
  workItems: WorkItem[]
  currentWorkItemId?: string
  recentActivity: ActivityItem[]
  train: JourneyTrainState
}

export interface LaunchDemoChapter {
  key: DemoChapterKey
  label: string
  durationMs: number
  progress: number
  snapshot: JourneySnapshot
}

export interface ProjectJourneySeed {
  project: Project
  mission: Mission
  finalSnapshot: JourneySnapshot
  launchDemo: LaunchDemoChapter[]
}

const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T

const stageOrder: ProjectStage[] = ['draft', 'seed', 'annotate', 'train', 'loop', 'completed']

const stageLabels: Record<ProjectStage, string> = {
  draft: '项目初始化',
  seed: '种子数据整理',
  annotate: '协同标注',
  train: '首轮训练',
  loop: '主动学习回流',
  completed: '结果沉淀',
}

const queueStateMap: QueueState[] = ['review', 'ready', 'review', 'done', 'imported', 'ready']

const chapterLabels: Record<DemoChapterKey, string> = {
  project_initialized: 'Project Initialized',
  seed_data_processing: 'Seed Data Processing',
  copilot_annotation: 'CoPilot Annotation',
  round_1_training: 'Round-1 Training',
  active_learning_loop: 'Active Learning Loop',
}

const queueStatusFromState = (queueState: QueueState): ImageTask['status'] => {
  switch (queueState) {
    case 'ready':
      return 'pending'
    case 'review':
      return 'incoming'
    case 'imported':
      return 'pending'
    case 'done':
      return 'confirmed'
    default:
      return 'incoming'
  }
}

const mapProjectStatusToStage = (project: Project): ProjectStage => {
  if (project.id.startsWith('proj-')) {
    return 'loop'
  }

  switch (project.status) {
    case 'idle':
      return 'draft'
    case 'labeling':
      return 'annotate'
    case 'training':
      return 'train'
    case 'completed':
      return 'completed'
    default:
      return 'draft'
  }
}

const timestampAt = (offsetMinutes: number) =>
  new Date(Date.now() - offsetMinutes * 60_000).toISOString()

const buildAnalysis = (confidence: number, queueState: QueueState, projectName: string): ImageAnalysisSummary => {
  const riskLevel =
    confidence >= 0.84 ? 'low' : confidence >= 0.68 ? 'medium' : 'high'

  const reasons =
    queueState === 'ready'
      ? ['多目标边界清晰', '置信度稳定', '建议直接确认进入训练集']
      : queueState === 'imported'
        ? ['检测到外部导入标注', '建议先做一轮格式与类别复核']
        : queueState === 'done'
          ? ['样本已归档', '可作为下一轮训练的稳定参考']
          : ['存在阴影与复杂背景', '建议人工复核后再入库']

  return {
    riskLevel,
    reasons,
    recommendedAction:
      queueState === 'ready'
        ? `确认后推进 ${projectName} 的下一张样本`
        : queueState === 'imported'
          ? '检查导入框与类别映射'
          : queueState === 'done'
            ? '继续处理下一批高价值样本'
            : '人工确认或标记误检',
    tags:
      queueState === 'imported'
        ? ['导入样本', '待校验']
        : queueState === 'done'
          ? ['训练样本', '已归档']
          : ['在线协同', '高频队列'],
  }
}

const cloneBoxes = (boxes: BoundingBox[], projectId: string, itemIndex: number, queueState: QueueState) =>
  boxes.map((bbox, bboxIndex) => ({
    ...bbox,
    id: `${projectId}-bbox-${itemIndex}-${bboxIndex}`,
    status: queueState === 'done' || queueState === 'imported' ? 'confirmed' : bbox.status,
  }))

const buildWorkItems = (project: Project): WorkItem[] => {
  return mockImageStream.slice(0, 6).map((item, index) => {
    const queueState = queueStateMap[index] || 'review'
    const boxes = cloneBoxes(item.boundingBoxes, project.id, index, queueState)
    const confidence = Number((item.confidence + index * 0.02).toFixed(2))
    const readyForCompletion =
      queueState === 'ready' ||
      queueState === 'done' ||
      boxes.every((bbox) => bbox.status === 'confirmed')

    return {
      ...clone(item),
      id: `${project.id}-work-${index + 1}`,
      projectId: project.id,
      queueState,
      status: queueStatusFromState(queueState),
      confidence,
      createdAt: timestampAt(70 - index * 8),
      confirmedAt: queueState === 'done' ? timestampAt(12) : undefined,
      boundingBoxes: boxes,
      readyForCompletion,
      analysis: buildAnalysis(confidence, queueState, project.name),
      agentComment: item.agentComment || `EvoLabeler 正在为 ${project.name} 聚合可训练样本。`,
    }
  })
}

const summarizeQueue = (workItems: WorkItem[]): QueueSummary => {
  const ready = workItems.filter((item) => item.queueState === 'ready').length
  const review = workItems.filter((item) => item.queueState === 'review').length
  const imported = workItems.filter((item) => item.queueState === 'imported').length
  const done = workItems.filter((item) => item.queueState === 'done').length
  const total = workItems.length

  return {
    total,
    ready,
    review,
    imported,
    done,
    completionRate: total > 0 ? Math.round((done / total) * 100) : 0,
  }
}

const buildLossData = (epochCount: number, baseLoss: number): YoloLossData => {
  const epochs = Array.from({ length: Math.max(epochCount, 1) }, (_, index) => index + 1)

  const boxLoss = epochs.map((epoch) => {
    const decay = Math.exp(-epoch / 48) * baseLoss
    const wobble = Math.sin(epoch / 7) * 0.0018
    return Number(Math.max(0.008, baseLoss * 0.18 + decay + wobble).toFixed(4))
  })
  const clsLoss = epochs.map((epoch) => {
    const decay = Math.exp(-epoch / 55) * baseLoss * 0.72
    const wobble = Math.sin(epoch / 9) * 0.0012
    return Number(Math.max(0.006, baseLoss * 0.12 + decay + wobble).toFixed(4))
  })
  const objLoss = epochs.map((epoch) => {
    const decay = Math.exp(-epoch / 60) * baseLoss * 0.55
    const wobble = Math.cos(epoch / 11) * 0.0008
    return Number(Math.max(0.004, baseLoss * 0.08 + decay + wobble).toFixed(4))
  })
  const valLoss = epochs.map((epoch, index) =>
    Number((boxLoss[index] + clsLoss[index] + objLoss[index] + 0.01 - epoch / 20_000).toFixed(4)),
  )

  return {
    epochs,
    boxLoss,
    clsLoss,
    objLoss,
    totalLoss: boxLoss.map((value, index) =>
      Number((value + clsLoss[index] + objLoss[index]).toFixed(4)),
    ),
    valLoss,
  }
}

const buildMetricsHistory = (project: Project, stage: ProjectStage) => {
  const config = getProjectConfig(project.id)
  const rounds = stage === 'draft' ? 1 : stage === 'seed' ? 1 : stage === 'annotate' ? 1 : stage === 'train' ? 2 : 3
  const history: MetricsHistoryEntry[] = []

  for (let round = 1; round <= rounds; round += 1) {
    const progress = round / rounds
    const isLast = round === rounds
    const mAP50 = isLast
      ? Number((config.metrics.mapAt50 / 100).toFixed(3))
      : Number((0.32 + progress * 0.34).toFixed(3))
    const precision = isLast
      ? Number((config.metrics.precision / 100).toFixed(3))
      : Number((0.44 + progress * 0.28).toFixed(3))
    const recall = isLast
      ? Number((config.metrics.recall / 100).toFixed(3))
      : Number((0.36 + progress * 0.26).toFixed(3))

    history.push({
      version: `v0.${round}`,
      roundNumber: round,
      mAP50,
      mAP5095: Number((mAP50 * 0.82).toFixed(3)),
      precision,
      recall,
      valLoss: Number((0.09 - progress * 0.04).toFixed(4)),
      trainLoss: Number((0.12 - progress * 0.05).toFixed(4)),
      calibrationEce: Number((0.08 - progress * 0.03).toFixed(4)),
      isBest: isLast,
      createdAt: timestampAt(160 - round * 40),
    })
  }

  return history
}

const buildModelVersions = (projectId: string, history: MetricsHistoryEntry[]) =>
  history.map((entry, index) => ({
    id: `${projectId}-version-${index + 1}`,
    projectId,
    version: entry.version,
    roundNumber: entry.roundNumber,
    modelPath: `/models/${projectId}/${entry.version}.pt`,
    metrics: {
      mAP50: entry.mAP50,
      mAP5095: entry.mAP5095,
      precision: entry.precision,
      recall: entry.recall,
      valLoss: entry.valLoss,
      trainLoss: entry.trainLoss,
    },
    calibrationEce: entry.calibrationEce,
    isBest: entry.isBest,
    isActive: index === history.length - 1,
    createdAt: entry.createdAt,
  })) satisfies ModelVersion[]

const buildEvoRounds = (projectId: string, history: MetricsHistoryEntry[], imageCount: number) =>
  history.map((entry, index) => ({
    id: `${projectId}-round-${entry.roundNumber}`,
    roundNumber: entry.roundNumber,
    status: index === history.length - 1 ? 'running' : 'completed',
    inputImageCount: Math.max(12, Math.round(imageCount * (0.16 + index * 0.1))),
    outputImageCount: Math.max(6, Math.round(imageCount * (0.1 + index * 0.08))),
    metricsBefore:
      index === 0
        ? undefined
        : {
            mAP50: history[index - 1].mAP50,
            precision: history[index - 1].precision,
            recall: history[index - 1].recall,
          },
    metricsAfter: {
      mAP50: entry.mAP50,
      precision: entry.precision,
      recall: entry.recall,
    },
    metricsDelta:
      index === 0
        ? {
            mAP50: entry.mAP50,
            precision: entry.precision,
            recall: entry.recall,
          }
        : {
            mAP50: Number(((entry.mAP50 || 0) - (history[index - 1].mAP50 || 0)).toFixed(3)),
            precision: Number(((entry.precision || 0) - (history[index - 1].precision || 0)).toFixed(3)),
            recall: Number(((entry.recall || 0) - (history[index - 1].recall || 0)).toFixed(3)),
          },
    shouldContinue: index !== history.length - 1,
    continueReason:
      index === history.length - 1
        ? '最近一轮发现新的低置信样本，建议继续主动学习回流。'
        : '当前轮次提升明显，继续收集高价值样本。',
    dataQualityGatePassed: true,
    modelHealthReport: undefined,
    wasRolledBack: false,
    createdAt: entry.createdAt,
  })) satisfies EvoRound[]

const buildHealthReport = (project: Project, versions: ModelVersion[]): ModelHealthResponse => {
  const latestVersion = versions[versions.length - 1]
  const overallStatus = project.status === 'completed' ? 'healthy' : 'warning'

  return {
    projectId: project.id,
    activeVersion: latestVersion?.version,
    bestVersion: versions.find((version) => version.isBest)?.version,
    healthReport: {
      overallStatus,
      recommendation:
        overallStatus === 'healthy'
          ? '当前模型表现稳定，建议把注意力放到新增高价值样本上。'
          : '模型仍在持续提升，建议在下一轮中优先处理低置信样本。',
      checks: [
        {
          name: 'label-drift',
          passed: true,
          severity: 'info',
          message: '最新标注分布与历史轮次保持一致。',
        },
        {
          name: 'calibration',
          passed: overallStatus === 'healthy',
          severity: overallStatus === 'healthy' ? 'info' : 'warning',
          message:
            overallStatus === 'healthy'
              ? '置信度校准稳定。'
              : '建议继续用高价值样本优化边界样本校准。',
        },
      ],
    },
  }
}

const stageToJobStep = (stage: ProjectStage): JobStep => {
  switch (stage) {
    case 'draft':
      return 'initialization'
    case 'seed':
      return 'data_preparation'
    case 'annotate':
      return 'data_preparation'
    case 'train':
      return 'model_training'
    case 'loop':
      return 'active_learning'
    case 'completed':
      return 'completed'
    default:
      return 'initialization'
  }
}

const buildJobStatus = (project: Project, stage: ProjectStage, history: MetricsHistoryEntry[]): JobStatus | null => {
  if (stage === 'draft') {
    return null
  }

  const config = getProjectConfig(project.id)
  const latest = history[history.length - 1]
  const currentEpoch =
    stage === 'seed'
      ? 6
      : stage === 'annotate'
        ? 24
        : stage === 'train'
          ? Math.max(42, config.trainingConfig.currentEpoch || 42)
          : stage === 'loop'
            ? Math.max(88, config.trainingConfig.currentEpoch || 88)
            : config.trainingConfig.totalEpochs

  return {
    id: `${project.id}-job`,
    projectId: project.id,
    currentStep: stageToJobStep(stage),
    progress: stage === 'completed' ? 100 : stage === 'loop' ? 84 : stage === 'train' ? 62 : stage === 'annotate' ? 36 : 18,
    status: stage === 'completed' ? 'completed' : 'running',
    startedAt: timestampAt(180),
    estimatedCompletion: timestampAt(-35),
    metrics: {
      accuracy: latest?.mAP50,
      loss: latest?.trainLoss,
      samplesProcessed: Math.round(project.imageCount * 0.72),
      totalSamples: project.imageCount,
    },
    yoloMetrics: {
      mAP50: latest?.mAP50 || 0.24,
      mAP5095: latest?.mAP5095 || 0.18,
      precision: latest?.precision || 0.46,
      recall: latest?.recall || 0.39,
      boxLoss: latest?.trainLoss || 0.063,
      clsLoss: Number(((latest?.trainLoss || 0.063) * 0.62).toFixed(4)),
      objLoss: Number(((latest?.trainLoss || 0.063) * 0.41).toFixed(4)),
      currentEpoch,
      totalEpochs: config.trainingConfig.totalEpochs,
      batchSize: config.trainingConfig.batchSize,
      learningRate: Number(config.trainingConfig.learningRate),
      gpuMemory: config.hardware.gpuMemory,
      gpuUtilization: config.hardware.gpuUsage,
      epochTime: Number.parseInt(config.timing.epochTime, 10) || 48,
      eta: config.timing.estimatedRemaining || '28m',
    },
    logs: [
      `[${stageLabels[stage]}] ${project.name} 正在推进当前阶段。`,
      `mAP50 ${(latest?.mAP50 || 0.24) * 100}% / Precision ${(latest?.precision || 0.46) * 100}%`,
    ],
  }
}

const buildTrainState = (project: Project, stage: ProjectStage): JourneyTrainState => {
  const config = getProjectConfig(project.id)
  const history = buildMetricsHistory(project, stage)
  const versions = buildModelVersions(project.id, history)
  const rounds = buildEvoRounds(project.id, history, project.imageCount)
  const lossEpochs =
    stage === 'draft'
      ? 1
      : stage === 'seed'
        ? 8
        : stage === 'annotate'
          ? 24
          : stage === 'train'
            ? 72
            : stage === 'loop'
              ? 120
              : config.trainingConfig.totalEpochs

  return {
    jobStatus: buildJobStatus(project, stage, history),
    lossData: buildLossData(lossEpochs, Math.max(config.lossCharacteristics.startingLoss, 0.05)),
    evoRounds: rounds,
    modelVersions: versions,
    healthReport: buildHealthReport(project, versions),
    metricsHistory: history,
  }
}

const buildRecentActivity = (project: Project, stage: ProjectStage, workItems: WorkItem[], train: JourneyTrainState): ActivityItem[] => {
  const latestMap = train.metricsHistory[train.metricsHistory.length - 1]?.mAP50 || 0
  const queueSummary = summarizeQueue(workItems)

  return [
    {
      id: `${project.id}-activity-1`,
      timestamp: timestampAt(5),
      title: stage === 'annotate' ? '协同标注正在处理高价值样本' : '项目状态已同步到统一工作台',
      detail: `当前待处理 ${queueSummary.ready + queueSummary.review + queueSummary.imported} 张，已完成 ${queueSummary.done} 张。`,
      tone: 'info',
    },
    {
      id: `${project.id}-activity-2`,
      timestamp: timestampAt(14),
      title: '模型摘要已刷新',
      detail: `最新 mAP50 为 ${(latestMap * 100).toFixed(1)}%，训练版本 ${train.modelVersions.at(-1)?.version || 'v0.1'} 已准备就绪。`,
      tone: 'success',
    },
    {
      id: `${project.id}-activity-3`,
      timestamp: timestampAt(24),
      title: '主动学习建议继续下一轮',
      detail: '低置信样本与导入样本已形成可复核批次，建议继续进入 Annotate。',
      tone: 'loop',
    },
  ]
}

export const buildTrainSummary = (snapshot: JourneySnapshot): TrainSummary => {
  const latestHistory = snapshot.train.metricsHistory[snapshot.train.metricsHistory.length - 1]
  const activeVersion = snapshot.train.modelVersions.find((version) => version.isActive)?.version || 'v0.1'
  const bestVersion = snapshot.train.modelVersions.find((version) => version.isBest)?.version || activeVersion

  return {
    headline: snapshot.narrative,
    currentRound: snapshot.train.evoRounds.length,
    maxRounds: Math.max(snapshot.train.evoRounds.length + 1, 5),
    activeVersion,
    bestVersion,
    latestMap50: Number((((latestHistory?.mAP50 || 0) * 100)).toFixed(1)),
    precision: Number((((latestHistory?.precision || 0) * 100)).toFixed(1)),
    recall: Number((((latestHistory?.recall || 0) * 100)).toFixed(1)),
  }
}

const buildAction = (stage: ProjectStage): ProjectAction => {
  switch (stage) {
    case 'draft':
      return {
        label: '进入总览',
        description: '确认项目初始化信息与演示准备状态。',
        to: 'overview',
      }
    case 'seed':
      return {
        label: '查看数据队列',
        description: '确认种子样本已进入统一队列。',
        to: 'overview',
      }
    case 'annotate':
      return {
        label: '继续标注',
        description: '优先清理需要人工确认的高价值样本。',
        to: 'annotate',
      }
    case 'train':
      return {
        label: '查看训练进展',
        description: '进入 Train 观察曲线、轮次和版本变化。',
        to: 'train',
      }
    case 'loop':
      return {
        label: '进入下一轮协同标注',
        description: '模型已经完成一轮训练，开始处理回流样本。',
        to: 'annotate',
      }
    case 'completed':
      return {
        label: '复盘训练结果',
        description: '查看最佳版本、历史指标与模型健康度。',
        to: 'train',
      }
    default:
      return {
        label: '查看项目',
        description: '进入统一项目工作台。',
        to: 'overview',
      }
  }
}

const buildMission = (project: Project, stage: ProjectStage): Mission => ({
  id: `mission-${project.id}`,
  name: project.name,
  description: project.description,
  status:
    stage === 'completed'
      ? 'completed'
      : stage === 'train' || stage === 'loop'
        ? 'training'
        : stage === 'annotate'
          ? 'labeling'
          : 'scouting',
  progress: stageOrder.indexOf(stage) * 20,
  seedImages: [],
  createdAt: project.createdAt,
  updatedAt: project.updatedAt,
  metadata: {
    stage,
    imageCount: project.imageCount,
  },
})

const snapshotForStage = (project: Project, stage: ProjectStage, workItems: WorkItem[]): JourneySnapshot => {
  const transformedItems = clone(workItems).map((item, index) => {
    if (stage === 'draft') {
      return {
        ...item,
        queueState: index === 0 ? 'review' : 'imported',
        status: index === 0 ? 'incoming' : 'pending',
        readyForCompletion: false,
      }
    }

    if (stage === 'seed') {
      return {
        ...item,
        queueState: index < 2 ? 'review' : index === 2 ? 'ready' : index === 3 ? 'done' : 'imported',
        status: index === 3 ? 'confirmed' : index === 2 ? 'pending' : 'incoming',
        readyForCompletion: index === 2,
      }
    }

    if (stage === 'annotate') {
      return {
        ...item,
        queueState: index < 2 ? 'ready' : index < 4 ? 'review' : index === 4 ? 'imported' : 'done',
        status: index === 5 ? 'confirmed' : index < 2 ? 'pending' : 'incoming',
        readyForCompletion: index < 2,
      }
    }

    if (stage === 'train') {
      return {
        ...item,
        queueState: index < 2 ? 'done' : index === 2 ? 'ready' : index === 3 ? 'review' : index === 4 ? 'imported' : 'done',
        status: index === 2 ? 'pending' : index === 3 ? 'incoming' : 'confirmed',
        readyForCompletion: index === 2,
      }
    }

    if (stage === 'loop') {
      return {
        ...item,
        queueState: index === 0 ? 'ready' : index === 1 ? 'review' : index === 2 ? 'imported' : 'done',
        status: index < 3 ? (index === 0 ? 'pending' : 'incoming') : 'confirmed',
        readyForCompletion: index === 0,
      }
    }

    return {
      ...item,
      queueState: index < 4 ? 'done' : index === 4 ? 'review' : 'imported',
      status: index < 4 ? 'confirmed' : 'incoming',
      readyForCompletion: false,
    }
  })

  const train = buildTrainState(project, stage)

  return {
    stage,
    headline: `${stageLabels[stage]} · ${project.name}`,
    narrative:
      stage === 'draft'
        ? '项目壳层已就绪，系统正在准备首批数据与演示上下文。'
        : stage === 'seed'
          ? '种子样本已经进入统一工作台，系统正在建立首批协同队列。'
          : stage === 'annotate'
            ? '高价值样本已推送到协同标注台，建议优先处理可快速确认的样本。'
            : stage === 'train'
              ? '首轮训练正在推进，当前重点是观察曲线收敛与版本提升。'
              : stage === 'loop'
                ? '首轮训练结束后，系统正在把高价值低置信样本回流到 Annotate。'
                : '该项目已形成稳定版本，可继续复盘并导出结果。',
    nextRecommendedAction: buildAction(stage),
    workItems: transformedItems,
    currentWorkItemId: transformedItems.find((item) => item.queueState === 'ready')?.id || transformedItems[0]?.id,
    recentActivity: buildRecentActivity(project, stage, transformedItems, train),
    train,
  }
}

export const createProjectJourneySeed = (project: Project): ProjectJourneySeed => {
  const finalStage = mapProjectStatusToStage(project)
  const baseWorkItems = buildWorkItems(project)
  const finalSnapshot = snapshotForStage(project, finalStage, baseWorkItems)

  const chapterStages: Array<{ key: DemoChapterKey; stage: ProjectStage; durationMs: number; progress: number }> = [
    { key: 'project_initialized', stage: 'draft', durationMs: 1200, progress: 12 },
    { key: 'seed_data_processing', stage: 'seed', durationMs: 1400, progress: 32 },
    { key: 'copilot_annotation', stage: 'annotate', durationMs: 1600, progress: 58 },
    { key: 'round_1_training', stage: 'train', durationMs: 1700, progress: 78 },
    { key: 'active_learning_loop', stage: finalStage, durationMs: 1800, progress: 100 },
  ]

  return {
    project,
    mission: buildMission(project, finalStage),
    finalSnapshot,
    launchDemo: chapterStages.map((chapter) => ({
      key: chapter.key,
      label: chapterLabels[chapter.key],
      durationMs: chapter.durationMs,
      progress: chapter.progress,
      snapshot: chapter.stage === finalStage ? finalSnapshot : snapshotForStage(project, chapter.stage, baseWorkItems),
    })),
  }
}

export const buildQueueSummary = summarizeQueue

