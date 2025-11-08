export interface ElectronAPI {
  minimizeWindow: () => void
  maximizeWindow: () => void
  closeWindow: () => void
  isMaximized: () => Promise<boolean>
  onWindowStateChange: (callback: (state: { isMaximized: boolean }) => void) => () => void
  platform: NodeJS.Platform
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI
  }
}

