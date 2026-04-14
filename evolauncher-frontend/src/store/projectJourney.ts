import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { Project } from '@/mock/projects'
import {
  buildQueueSummary,
  buildTrainSummary,
  createProjectJourneySeed,
  type DemoChapterKey,
  type LaunchDemoChapter,
  type ProjectAction,
  type ProjectJourneySeed,
  type ProjectStage,
  type JourneySnapshot,
} from '@/mock/projectJourney'
import { fetchProjectById, type Project as ProjectCard } from '@/mock/projects'
import { useMissionStore } from '@/store/mission'
import { useWorkspaceStore } from '@/store/workspace'

type DemoPlayback = 'idle' | 'playing' | 'paused' | 'completed'

interface LaunchDemoState {
  active: boolean
  chapterKey: DemoChapterKey | null
  progress: number
  playback: DemoPlayback
}

const fallbackProject = (projectId: string): ProjectCard => ({
  id: projectId,
  name: '新建进化项目',
  description: '统一项目工作台正在为该项目准备演示上下文。',
  status: 'idle',
  imageCount: 24,
  accuracy: 0,
  thumbnailUrl: '',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
})

export const useProjectJourneyStore = defineStore('projectJourney', () => {
  const missionStore = useMissionStore()
  const workspaceStore = useWorkspaceStore()

  const project = ref<Project | null>(null)
  const journeySeed = ref<ProjectJourneySeed | null>(null)
  const stage = ref<ProjectStage>('draft')
  const headline = ref('')
  const narrative = ref('')
  const nextRecommendedAction = ref<ProjectAction>({
    label: '查看项目',
    description: '进入统一项目工作台。',
    to: 'overview',
  })
  const recentActivity = ref<JourneySnapshot['recentActivity']>([])
  const launchDemo = ref<LaunchDemoState>({
    active: false,
    chapterKey: null,
    progress: 0,
    playback: 'idle',
  })

  let chapterTimer: ReturnType<typeof setTimeout> | null = null
  let currentChapterIndex = -1
  let chapterStartedAt = 0
  let remainingMs = 0

  const queueSummary = computed(() => buildQueueSummary(missionStore.imageStream))
  const trainSummary = computed(() =>
    buildTrainSummary({
      stage: stage.value,
      headline: headline.value,
      narrative: narrative.value,
      nextRecommendedAction: nextRecommendedAction.value,
      workItems: missionStore.imageStream,
      currentWorkItemId: missionStore.currentWorkItem?.id,
      recentActivity: recentActivity.value,
      train: workspaceStore.getTrainState(),
    }),
  )

  const stageList = computed(() => [
    { key: 'draft' as const, label: 'Init' },
    { key: 'seed' as const, label: 'Seed' },
    { key: 'annotate' as const, label: 'Annotate' },
    { key: 'train' as const, label: 'Train' },
    { key: 'loop' as const, label: 'Loop' },
    { key: 'completed' as const, label: 'Complete' },
  ])

  const currentChapter = computed<LaunchDemoChapter | null>(() => {
    if (!journeySeed.value || currentChapterIndex < 0) return null
    return journeySeed.value.launchDemo[currentChapterIndex] || null
  })

  const clearDemoTimer = () => {
    if (chapterTimer) {
      clearTimeout(chapterTimer)
      chapterTimer = null
    }
  }

  const applySnapshot = (snapshot: JourneySnapshot) => {
    stage.value = snapshot.stage
    headline.value = snapshot.headline
    narrative.value = snapshot.narrative
    nextRecommendedAction.value = snapshot.nextRecommendedAction
    recentActivity.value = snapshot.recentActivity
    missionStore.hydrateProjectMission(
      journeySeed.value?.mission || missionStore.currentMission!,
      snapshot.workItems,
      snapshot.recentActivity,
    )
    if (snapshot.currentWorkItemId) {
      missionStore.selectImage(snapshot.currentWorkItemId)
    }
    workspaceStore.applyDemoWorkspace(snapshot.train)
  }

  const finishDemo = () => {
    clearDemoTimer()
    if (journeySeed.value) {
      applySnapshot(journeySeed.value.finalSnapshot)
    }
    launchDemo.value = {
      active: false,
      chapterKey: currentChapter.value?.key || 'active_learning_loop',
      progress: 100,
      playback: 'completed',
    }
    currentChapterIndex = journeySeed.value ? journeySeed.value.launchDemo.length - 1 : -1
    remainingMs = 0
  }

  const scheduleNextChapter = (durationMs: number) => {
    clearDemoTimer()
    chapterStartedAt = Date.now()
    remainingMs = durationMs
    chapterTimer = setTimeout(() => {
      if (!journeySeed.value) return
      if (currentChapterIndex >= journeySeed.value.launchDemo.length - 1) {
        finishDemo()
        return
      }

      currentChapterIndex += 1
      const chapter = journeySeed.value.launchDemo[currentChapterIndex]
      launchDemo.value = {
        active: true,
        chapterKey: chapter.key,
        progress: chapter.progress,
        playback: 'playing',
      }
      applySnapshot(chapter.snapshot)
      scheduleNextChapter(chapter.durationMs)
    }, durationMs)
  }

  const initializeProject = async (projectId: string) => {
    const loadedProject = (await fetchProjectById(projectId).catch(() => undefined)) || fallbackProject(projectId)
    project.value = loadedProject
    journeySeed.value = createProjectJourneySeed(loadedProject)
    currentChapterIndex = journeySeed.value.launchDemo.length - 1
    applySnapshot(journeySeed.value.finalSnapshot)
    launchDemo.value = {
      active: false,
      chapterKey: null,
      progress: 0,
      playback: 'idle',
    }
  }

  const startLaunchDemo = () => {
    if (!journeySeed.value) return
    clearDemoTimer()
    currentChapterIndex = 0
    const chapter = journeySeed.value.launchDemo[currentChapterIndex]
    launchDemo.value = {
      active: true,
      chapterKey: chapter.key,
      progress: chapter.progress,
      playback: 'playing',
    }
    applySnapshot(chapter.snapshot)
    scheduleNextChapter(chapter.durationMs)
  }

  const pauseLaunchDemo = () => {
    if (!launchDemo.value.active || launchDemo.value.playback !== 'playing') return
    clearDemoTimer()
    remainingMs = Math.max(300, remainingMs - (Date.now() - chapterStartedAt))
    launchDemo.value = {
      ...launchDemo.value,
      playback: 'paused',
    }
  }

  const resumeLaunchDemo = () => {
    if (!launchDemo.value.active || launchDemo.value.playback !== 'paused') return
    launchDemo.value = {
      ...launchDemo.value,
      playback: 'playing',
    }
    scheduleNextChapter(remainingMs || currentChapter.value?.durationMs || 900)
  }

  const replayLaunchDemo = () => {
    startLaunchDemo()
  }

  const skipLaunchDemo = () => {
    finishDemo()
  }

  const refreshActivity = (title: string, detail: string) => {
    recentActivity.value = [
      {
        id: `activity-${Date.now()}`,
        timestamp: new Date().toISOString(),
        title,
        detail,
        tone: 'info',
      },
      ...recentActivity.value.slice(0, 5),
    ]
    missionStore.setAgentLogsFromActivities(recentActivity.value)
  }

  const syncQueueSummary = () => {
    recentActivity.value = [
      {
        id: `queue-${Date.now()}`,
        timestamp: new Date().toISOString(),
        title: '协同队列已更新',
        detail: `当前 Ready ${queueSummary.value.ready} / Review ${queueSummary.value.review} / Imported ${queueSummary.value.imported}。`,
        tone: 'loop',
      },
      ...recentActivity.value.slice(0, 5),
    ]
    missionStore.setAgentLogsFromActivities(recentActivity.value)
  }

  return {
    project,
    stage,
    headline,
    narrative,
    nextRecommendedAction,
    recentActivity,
    queueSummary,
    trainSummary,
    stageList,
    launchDemo,
    currentChapter,
    initializeProject,
    startLaunchDemo,
    pauseLaunchDemo,
    resumeLaunchDemo,
    replayLaunchDemo,
    skipLaunchDemo,
    refreshActivity,
    syncQueueSummary,
  }
})
