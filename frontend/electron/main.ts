import { app, BrowserWindow, ipcMain, Tray, Menu, shell, nativeImage, screen } from 'electron'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// 使用类型转换来添加自定义属性，避免 TS 错误
const appWithFlags = app as unknown as { isQuitting: boolean } & typeof app
appWithFlags.isQuitting = false

// 构建后的目录结构
process.env.DIST = path.join(__dirname, '../dist')
process.env.VITE_PUBLIC = app.isPackaged 
  ? process.env.DIST 
  : path.join(process.env.DIST, '../public')

let win: BrowserWindow | null = null
let floatWin: BrowserWindow | null = null  // 悬浮窗
let tray: Tray | null = null

const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']

// 悬浮窗配置
const FLOAT_WIN_WIDTH = 180
const FLOAT_WIN_HEIGHT = 120
const EDGE_MARGIN = 0  // 吸边时距离屏幕边缘的距离
const EDGE_THRESHOLD = 20  // 触发吸边的阈值

// 获取托盘图标路径
function getTrayIconPath(): string {
  return path.join(process.env.VITE_PUBLIC || '', 'stock.ico')
}

// 创建悬浮窗
function createFloatWindow() {
  if (floatWin) return
  
  const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize
  
  floatWin = new BrowserWindow({
    width: FLOAT_WIN_WIDTH,
    height: FLOAT_WIN_HEIGHT,
    x: screenWidth - FLOAT_WIN_WIDTH - 20,  // 默认右下角
    y: screenHeight - FLOAT_WIN_HEIGHT - 20,
    frame: false,           // 无边框
    transparent: true,      // 透明背景
    alwaysOnTop: true,      // 始终置顶
    skipTaskbar: true,      // 不在任务栏显示
    resizable: false,       // 不可调整大小
    hasShadow: false,       // 无阴影
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  // 加载悬浮窗页面
  if (VITE_DEV_SERVER_URL) {
    floatWin.loadURL(`${VITE_DEV_SERVER_URL}#/float`)
    // 开发模式下打开悬浮窗的 DevTools 用于调试
    floatWin.webContents.openDevTools({ mode: 'detach' })
  } else {
    floatWin.loadFile(path.join(process.env.DIST || '', 'index.html'), { hash: '/float' })
  }
  
  // 检查 preload 是否加载成功
  floatWin.webContents.on('did-finish-load', () => {
    console.log('悬浮窗页面加载完成')
  })

  // 鼠标进入时取消半透明
  floatWin.on('focus', () => {
    floatWin?.setOpacity(1)
  })

  // 鼠标离开后变半透明
  floatWin.on('blur', () => {
    floatWin?.setOpacity(0.7)
  })

  // 拖拽结束后检测吸边
  floatWin.on('moved', () => {
    if (!floatWin) return
    
    const [x, y] = floatWin.getPosition()
    const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize
    
    let newX = x
    let newY = y
    
    // 左边吸边
    if (x < EDGE_THRESHOLD) {
      newX = EDGE_MARGIN
    }
    // 右边吸边
    if (x + FLOAT_WIN_WIDTH > screenWidth - EDGE_THRESHOLD) {
      newX = screenWidth - FLOAT_WIN_WIDTH - EDGE_MARGIN
    }
    // 上边吸边
    if (y < EDGE_THRESHOLD) {
      newY = EDGE_MARGIN
    }
    // 下边吸边
    if (y + FLOAT_WIN_HEIGHT > screenHeight - EDGE_THRESHOLD) {
      newY = screenHeight - FLOAT_WIN_HEIGHT - EDGE_MARGIN
    }
    
    // 如果位置有变化，执行吸边动画
    if (newX !== x || newY !== y) {
      floatWin.setPosition(newX, newY, true)
    }
  })

  floatWin.on('closed', () => {
    floatWin = null
  })

  // 初始状态半透明
  floatWin.setOpacity(0.7)
  
  console.log('悬浮窗创建成功')
}

// 创建托盘图标
function createTray() {
  if (tray) return
  
  const iconPath = getTrayIconPath()
  console.log('创建托盘图标，路径:', iconPath)
  
  try {
    const trayIcon = nativeImage.createFromPath(iconPath)
    
    if (trayIcon.isEmpty()) {
      console.error('托盘图标加载失败')
      return
    }
    
    tray = new Tray(trayIcon)
    
    // 创建托盘右键菜单
    const contextMenu = Menu.buildFromTemplate([
      { label: '显示主窗口', click: () => win?.show() },
      { 
        label: '显示悬浮窗', 
        click: () => {
          if (floatWin) {
            floatWin.show()
          } else {
            createFloatWindow()
          }
        }
      },
      { type: 'separator' },
      { 
        label: '退出', 
        click: () => {
          appWithFlags.isQuitting = true
          app.quit()
        }
      }
    ])
    
    tray.setToolTip('股票监控助手')
    tray.setContextMenu(contextMenu)
    
    // 单击托盘图标显示/隐藏主窗口
    tray.on('click', () => {
      if (win) {
        if (win.isVisible()) {
          win.hide()
        } else {
          win.show()
          win.focus()
        }
      }
    })
    
    console.log('托盘图标创建成功')
  } catch (error) {
    console.error('创建托盘图标失败:', error)
  }
}

function createWindow() {
  win = new BrowserWindow({
    width: 1000,
    height: 700,
    icon: getTrayIconPath(),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      sandbox: false,
      nodeIntegration: false,
      contextIsolation: true,
    },
  })

  win.setMenuBarVisibility(false)

  win.webContents.on('did-finish-load', () => {
    win?.webContents.send('main-process-message', (new Date).toLocaleString())
  })

  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL)
    win.webContents.openDevTools()
  } else {
    win.loadFile(path.join(process.env.DIST || '', 'index.html'))
  }

  win.webContents.on('did-fail-load', (_event, errorCode, errorDescription) => {
    console.log('窗口加载失败:', errorCode, errorDescription)
    if (errorCode === -102) {
      setTimeout(() => {
        if (win && VITE_DEV_SERVER_URL) {
          win.loadURL(VITE_DEV_SERVER_URL)
        }
      }, 1000)
    }
  })

  // 最小化时隐藏到托盘
  win.on('minimize', (event: Electron.Event) => {
    event.preventDefault()
    win?.hide()
  })

  // 关闭按钮点击时隐藏到托盘
  win.on('close', (event: Electron.Event) => {
    if (!appWithFlags.isQuitting) {
      event.preventDefault()
      win?.hide()
    }
  })

  win.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })
}

// IPC: 更新托盘提示文本
ipcMain.on('update-tray', (_event, text: string) => {
  if (tray) {
    tray.setToolTip(text)
  }
})

// IPC: 更新悬浮窗数据
ipcMain.on('update-float-window', (_event, data: any) => {
  if (floatWin && !floatWin.isDestroyed()) {
    floatWin.webContents.send('stock-data-update', data)
  }
})

// IPC: 关闭悬浮窗
ipcMain.on('close-float-window', () => {
  console.log('收到关闭悬浮窗请求')
  if (floatWin && !floatWin.isDestroyed()) {
    floatWin.close()
    floatWin = null
    console.log('悬浮窗已关闭')
  }
})

// IPC: 开始拖拽悬浮窗
ipcMain.on('float-window-drag', () => {
  // 这个由渲染进程的 -webkit-app-region: drag 处理
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
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
  createTray()
  createWindow()
  createFloatWindow()  // 启动时自动创建悬浮窗
})
