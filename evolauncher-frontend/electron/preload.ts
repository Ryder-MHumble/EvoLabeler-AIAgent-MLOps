import { contextBridge, ipcRenderer } from 'electron'

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Window controls for custom title bar
  minimizeWindow: () => ipcRenderer.send('window-minimize'),
  maximizeWindow: () => ipcRenderer.send('window-maximize'),
  closeWindow: () => ipcRenderer.send('window-close'),
  isMaximized: () => ipcRenderer.invoke('window-is-maximized'),
  onWindowStateChange: (callback: (state: { isMaximized: boolean }) => void) => {
    const listener = (_event: Electron.IpcRendererEvent, state: { isMaximized: boolean }) => {
      callback(state)
    }

    ipcRenderer.on('window-state-changed', listener)

    return () => {
      ipcRenderer.removeListener('window-state-changed', listener)
    }
  },

  // Platform info
  platform: process.platform
})

// TypeScript declaration for the exposed API
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
    electronAPI: ElectronAPI
  }
}

