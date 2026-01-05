import { app, BrowserWindow, ipcMain, Tray, Menu, shell, nativeImage, screen, Notification } from 'electron'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { spawn, ChildProcess } from 'node:child_process'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// 单实例锁：确保只有一个应用实例运行
const gotTheLock = app.requestSingleInstanceLock()

if (!gotTheLock) {
  // 如果获取不到锁，说明已有实例在运行，直接退出
  app.quit()
}

// 用户数据目录（localStorage 会自动持久化到这里）
const userDataPath = app.getPath('userData')

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
let backendProcess: ChildProcess | null = null  // 后端进程

const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']

// 启动后端服务
function startBackend() {
  if (!app.isPackaged) {
    // 开发模式下不自动启动后端
    console.log('开发模式，请手动启动后端服务')
    return
  }

  // 打包后的后端 exe 路径
  const backendPath = path.join(process.resourcesPath, 'backend')
  const binaryName = process.platform === 'win32' ? 'stock-monitor-backend.exe' : 'stock-monitor-backend'
  const backendExe = path.join(backendPath, binaryName)

  console.log('启动后端服务:', backendExe)
  console.log('工作目录:', backendPath)

  // 启动后端 exe
  backendProcess = spawn(backendExe, [], {
    cwd: backendPath,
    stdio: ['ignore', 'pipe', 'pipe'],
    windowsHide: false  // 显示控制台窗口方便调试，正式版可改为 true
  })

  backendProcess.stdout?.on('data', (data) => {
    console.log(`[后端] ${data}`)
  })

  backendProcess.stderr?.on('data', (data) => {
    console.error(`[后端错误] ${data}`)
  })

  backendProcess.on('close', (code) => {
    console.log(`后端进程退出，代码: ${code}`)
    // 如果后端意外退出且应用未在退出中，尝试重启
    if (code !== 0 && !appWithFlags.isQuitting) {
      console.log('后端意外退出，3秒后尝试重启...')
      setTimeout(startBackend, 3000)
    }
  })

  backendProcess.on('error', (err) => {
    console.error('启动后端失败:', err)
  })
}

// 停止后端服务
function stopBackend() {
  if (backendProcess) {
    console.log('停止后端服务...')
    // Windows 下需要强制终止
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', String(backendProcess.pid), '/f', '/t'])
    } else {
      backendProcess.kill()
    }
    backendProcess = null
  }
}

// 悬浮窗配置
const FLOAT_WIN_WIDTH = 200
const FLOAT_WIN_HEIGHT = 150
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
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  // 加载悬浮窗页面
  if (VITE_DEV_SERVER_URL) {
    floatWin.loadURL(`${VITE_DEV_SERVER_URL}#/float`)
    // 开发模式下打开悬浮窗的 DevTools 用于调试
    // floatWin.webContents.openDevTools({ mode: 'detach' })
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

function createWindow(): BrowserWindow {
  const browserWindow = new BrowserWindow({
    width: 1200,
    height: 750,
    minWidth: 1000,
    minHeight: 600,
    icon: getTrayIconPath(),
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      sandbox: false,
      nodeIntegration: false,
      contextIsolation: true,
    },
  })

  // 更新全局 win 引用
  win = browserWindow

  browserWindow.setMenuBarVisibility(false)

  browserWindow.webContents.on('did-finish-load', () => {
    browserWindow.webContents.send('main-process-message', (new Date).toLocaleString())
  })

  if (VITE_DEV_SERVER_URL) {
    browserWindow.loadURL(VITE_DEV_SERVER_URL)
    browserWindow.webContents.openDevTools()
  } else {
    browserWindow.loadFile(path.join(process.env.DIST || '', 'index.html'))
  }

  browserWindow.webContents.on('did-fail-load', (_event, errorCode, errorDescription) => {
    console.log('窗口加载失败:', errorCode, errorDescription)
    if (errorCode === -102) {
      setTimeout(() => {
        if (!browserWindow.isDestroyed() && VITE_DEV_SERVER_URL) {
          browserWindow.loadURL(VITE_DEV_SERVER_URL)
        }
      }, 1000)
    }
  })

  // 最小化时隐藏到托盘
  browserWindow.on('minimize', () => {
    browserWindow.hide()
  })

  // 关闭按钮点击时隐藏到托盘
  browserWindow.on('close', (event: Electron.Event) => {
    if (!appWithFlags.isQuitting) {
      event.preventDefault()
      browserWindow.hide()
    }
  })

  browserWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  return browserWindow
}

// IPC: 更新托盘提示文本
ipcMain.on('update-tray', (_event, text: string) => {
  if (tray) {
    tray.setToolTip(text)
  }
})

// IPC: 更新托盘图标（绘制 K 线柱状图）
ipcMain.on('update-tray-icon', (_event, data: {
  change: string;
  price: string;
  name: string;
  open?: string;
  high?: string;
  low?: string;
  pre_close?: string;
}) => {
  if (!tray) return

  try {
    const change = parseFloat(data.change)
    const isUp = change >= 0
    const sign = isUp ? '+' : ''

    const size = 16
    // BGRA 格式（Windows 使用 BGRA）
    const pixels = Buffer.alloc(size * size * 4)

    // 颜色定义 (BGRA 格式)
    const bgColor = { b: 40, g: 40, r: 40, a: 255 }      // 深灰背景
    const upColor = { b: 79, g: 77, r: 255, a: 255 }     // 红色（涨）
    const downColor = { b: 26, g: 196, r: 82, a: 255 }   // 绿色（跌）
    const barColor = isUp ? upColor : downColor

    // 计算柱状图高度（基于涨跌幅，最大 10%）
    const maxChange = 10
    const absChange = Math.min(Math.abs(change), maxChange)
    const barHeight = Math.max(2, Math.round((absChange / maxChange) * (size - 4)))

    // 绘制像素
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const offset = (y * size + x) * 4

        // 默认背景色
        let color = bgColor

        // 绘制柱状图（居中，宽度 8px）
        const barWidth = 8
        const barLeft = (size - barWidth) / 2
        const barRight = barLeft + barWidth

        if (x >= barLeft && x < barRight) {
          if (isUp) {
            // 涨：从底部向上
            const barTop = size - 2 - barHeight
            if (y >= barTop && y < size - 2) {
              color = barColor
            }
          } else {
            // 跌：从顶部向下
            if (y >= 2 && y < 2 + barHeight) {
              color = barColor
            }
          }
        }

        // 绘制中线（昨收位置）
        if (y === Math.floor(size / 2) && x >= 1 && x < size - 1) {
          color = { b: 100, g: 100, r: 100, a: 255 } // 灰色中线
        }

        pixels[offset] = color.b
        pixels[offset + 1] = color.g
        pixels[offset + 2] = color.r
        pixels[offset + 3] = color.a
      }
    }

    const icon = nativeImage.createFromBuffer(pixels, {
      width: size,
      height: size,
    })

    tray.setImage(icon)
    tray.setToolTip(`${data.name}: ${data.price} (${sign}${change.toFixed(2)}%)`)

  } catch (e) {
    console.error('更新托盘图标失败:', e)
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

// IPC: 显示主窗口
ipcMain.on('show-main-window', () => {
  if (win) {
    if (win.isMinimized()) win.restore()
    if (!win.isVisible()) win.show()
    win.focus()
  } else {
    createWindow()
  }
})

// IPC: 显示股票详情
ipcMain.on('show-stock-detail', (_event, code: string) => {
  if (win) {
    if (win.isMinimized()) win.restore()
    if (!win.isVisible()) win.show()
    win.focus()
    // 发送消息给渲染进程导航
    win.webContents.send('navigate-to-stock', code)
  } else {
    const newWin = createWindow()
    // 等待窗口创建完成后发送导航消息
    newWin.webContents.on('did-finish-load', () => {
      newWin.webContents.send('navigate-to-stock', code)
    })
  }
})

// IPC: 发送系统通知
ipcMain.on('show-notification', (_event, data: { title: string; body: string }) => {
  if (Notification.isSupported()) {
    const notification = new Notification({
      title: data.title,
      body: data.body,
      icon: getTrayIconPath(),
    })

    // 点击通知时显示主窗口
    notification.on('click', () => {
      if (win) {
        win.show()
        win.focus()
      }
    })

    notification.show()
    console.log('系统通知已发送:', data.title)
  }
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// 当第二个实例启动时，聚焦到已有窗口
app.on('second-instance', () => {
  if (win) {
    if (win.isMinimized()) win.restore()
    if (!win.isVisible()) win.show()
    win.focus()
  }
})

app.on('before-quit', () => {
  appWithFlags.isQuitting = true
  stopBackend()  // 退出前停止后端服务
})

app.on('activate', () => {
  if (win) {
    if (win.isMinimized()) win.restore()
    if (!win.isVisible()) win.show()
    win.focus()
  } else if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

app.whenReady().then(() => {
  console.log('应用启动，用户数据目录:', userDataPath)

  // 启动后端服务（仅打包后生效）
  startBackend()

  createTray()
  createWindow()
  createFloatWindow()  // 启动时自动创建悬浮窗
})
