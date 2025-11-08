import { app, BrowserWindow, ipcMain } from 'electron'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// The built directory structure
//
// ├─┬─┬ dist
// │ │ └── index.html
// │ │
// │ ├─┬ dist-electron
// │ │ ├── main/main.js
// │ │ └── preload/preload.js
// │
const DIST_PATH = path.join(__dirname, '../dist')
const PRELOAD_DIST = path.join(__dirname, 'preload.js')

process.env.DIST = DIST_PATH
process.env.DIST_ELECTRON = __dirname
process.env.VITE_PUBLIC = app.isPackaged ? process.env.DIST : path.join(process.env.DIST, '../public')

let win: BrowserWindow | null

const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']

function createWindow() {
  const preloadPath = app.isPackaged
    ? PRELOAD_DIST
    : path.join(process.cwd(), 'dist-electron/preload.js')

  win = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    show: false, // Don't show until ready-to-show event
    // Frameless window for custom title bar - creates a sleek, modern look
    frame: false,
    // Transparent allows for custom styling without traditional window chrome
    transparent: true,
    // Rounded corners for a softer, more premium aesthetic
    roundedCorners: true,
    backgroundColor: '#00000000', // Fully transparent background
    webPreferences: {
      preload: preloadPath,
      nodeIntegration: false,
      contextIsolation: true,
      // Enable web security
      webSecurity: true
    },
    // macOS specific: Create a window with vibrancy effect for native feel
    ...(process.platform === 'darwin' ? {
      titleBarStyle: 'hiddenInset',
      vibrancy: 'under-window'
    } : {})
  })

  // Implement smooth window animations on show
  win.once('ready-to-show', () => {
    win?.show()
    // Open DevTools in development (attached to the main window)
    if (VITE_DEV_SERVER_URL && process.env.NODE_ENV !== 'production') {
      win?.webContents.openDevTools({ mode: 'detach' })
    }
  })

  // Load the app
  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL)
  } else {
    win.loadFile(path.join(process.env.DIST!, 'index.html'))
  }

  const emitWindowState = () => {
    if (win) {
      win.webContents.send('window-state-changed', {
        isMaximized: win.isMaximized()
      })
    }
  }

  win.on('maximize', emitWindowState)
  win.on('unmaximize', emitWindowState)
  win.on('restore', emitWindowState)
  win.on('resized', emitWindowState)

  setImmediate(() => emitWindowState())
}

ipcMain.on('window-minimize', () => {
  win?.minimize()
})

ipcMain.on('window-maximize', () => {
  if (!win) return

  if (win.isMaximized()) {
    win.unmaximize()
  } else {
    win.maximize()
  }

  win.webContents.send('window-state-changed', {
    isMaximized: win.isMaximized()
  })
})

ipcMain.on('window-close', () => {
  win?.close()
})

ipcMain.handle('window-is-maximized', () => {
  return win?.isMaximized()
})

// App lifecycle
app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
  // On macOS, apps typically stay active until the user quits explicitly
  if (process.platform !== 'darwin') {
    app.quit()
  }
  win = null
})

app.on('activate', () => {
  // On macOS, re-create window when dock icon is clicked and no windows are open
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

