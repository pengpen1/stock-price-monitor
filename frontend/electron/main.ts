import { app, BrowserWindow, ipcMain, Tray, Menu, shell } from 'electron'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// Use type casting for custom properties to avoid TS errors
const appWithFlags = app as unknown as { isQuitting: boolean } & typeof app
appWithFlags.isQuitting = false

// The built directory structure
//
// ├─┬ dist
// │ ├─┬ electron
// │ │ ├── main.js
// │ │ └── preload.js
// │ ├── index.html
// │ ...
// ├─┬ dist-electron
// │ ├── main.js
// │ └── preload.js
//
process.env.DIST = path.join(__dirname, '../dist')
process.env.VITE_PUBLIC = app.isPackaged ? process.env.DIST : path.join(process.env.DIST, '../public')

let win: BrowserWindow | null
let tray: Tray | null = null

const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']

function createWindow() {
  win = new BrowserWindow({
    icon: path.join(process.env.VITE_PUBLIC || '', 'vite.svg'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      sandbox: false,
      nodeIntegration: true, // Optional: enable if you need node in renderer (not recommended but helpful for debugging)
      contextIsolation: true,
    },
  })

  // Hide the menu bar
  win.setMenuBarVisibility(false)

  // Test active push message to Renderer-process.
  win.webContents.on('did-finish-load', () => {
    win?.webContents.send('main-process-message', (new Date).toLocaleString())
  })

  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL)
    win.webContents.openDevTools()
  } else {
    // win.loadFile('dist/index.html')
    win.loadFile(path.join(process.env.DIST || '', 'index.html'))
  }

  // Handle loading failures (e.g. if Vite isn't ready yet)
  win.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.log('Failed to load window:', errorCode, errorDescription);
    if (errorCode === -102) { // ERR_CONNECTION_REFUSED
      setTimeout(() => {
        if (win && VITE_DEV_SERVER_URL) {
          console.log('Retrying load URL...');
          win.loadURL(VITE_DEV_SERVER_URL);
        }
      }, 1000);
    }
  });

  // 最小化到托盘行为
  win.on('minimize', () => {
    if (win) {
      win.hide()
    }
  })

  // 关闭到托盘行为（点击关闭按钮时隐藏而不是退出）
  win.on('close', (event) => {
    if (!appWithFlags.isQuitting && win) {
      event.preventDefault()
      win.hide()
    }
  })

  win.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })
}

// IPC for updating tray tooltip
ipcMain.on('update-tray', (_event, text) => {
  if (tray) {
    tray.setToolTip(text)
  }
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
    win = null
  }
})

app.on('before-quit', () => {
  appWithFlags.isQuitting = true
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

app.whenReady().then(() => {
  createWindow()
  
  // 创建托盘图标
  // Windows 托盘需要合适格式的图标，这里使用 nativeImage 创建
  const { nativeImage } = require('electron')
  
  // 创建一个 32x32 的股票图标（绿色上涨箭头样式）
  // 这是一个简单但清晰的 PNG 图标 base64
  const iconBase64 = 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGRSURBVFiF7ZY9TsNAEIW/WYcGiQKJgoKWgoqOI3AEjkBJRUVFR8cROAJHoKOipKKgoECiQPyIxGbHBRvFJN7sxnZCwZNW8u7svJl9s7MrGGKIIf4rZNAOAJRSM8AHYBzYBJ6BZ+DRGPPRr5+BC1BKzQKPwBjwBrwCr8A7cAOcGmMu+vVVcAGllAJugXFgGXgCXoAP4Bm4Bk6MMef9+iu4gFJqHLgDJoAV4AF4AT6BZ+AKODbGnPXrM3cBpdQEcA9MAqvAPfAKfAFPwCVwZIw57ddv7gJKqUngAZgC1oA74A34Bh6BC+DIGHPSr+/cBZRSU8AjMA2sA7fAO/ADPAAXwKEx5rhf/7kLKKWmgSdgBlgHboAP4Bd4AM6BQ2PMUb/+cxdQSs0AT8AssAFcAx/AL3APnAEHxpjDfmPkLqCUmgWegTlgE7gCPoE/4A44BfaNMQf9xsldQCk1BzwDC8AWcAl8AX/ALXACHBhj9vuNlbuAUmoeeAEWgW3gAvgG/oAb4BjYN8bs9RsijCH+Nf4AYcnkMPJB3REAAAAASUVORK5CYII='
  
  let trayIcon = nativeImage.createFromDataURL(`data:image/png;base64,${iconBase64}`)
  
  // 调整图标大小以适应托盘（Windows 托盘通常使用 16x16）
  trayIcon = trayIcon.resize({ width: 16, height: 16 })
  
  tray = new Tray(trayIcon)
  
  // 创建托盘右键菜单
  const contextMenu = Menu.buildFromTemplate([
    { label: '显示主窗口', click: () => win?.show() },
    { type: 'separator' },
    { label: '退出', click: () => {
        appWithFlags.isQuitting = true
        app.quit() 
      } 
    }
  ])
  
  tray.setToolTip('股票监控助手')
  tray.setContextMenu(contextMenu)
  
  // 点击托盘图标切换窗口显示/隐藏
  tray.on('click', () => {
    if (win?.isVisible()) {
      win.hide()
    } else {
      win?.show()
    }
  })
})
