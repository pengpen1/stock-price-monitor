import { BrowserWindow, ipcMain, nativeImage, Notification, app, shell, Tray, Menu, screen } from "electron";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";
const ipcMainApi = {
  handle(ch, fn) {
    ipcMain.handle(ch, (_e, data) => fn(data));
  },
  on(ch, fn) {
    const handle = (_e, data) => {
      fn(data);
    };
    ipcMain.on(ch, handle);
    return () => {
      ipcMain.off(ch, handle);
    };
  },
  send(ch, ...data) {
    const windows = BrowserWindow.getAllWindows();
    for (const w of windows) {
      w.webContents.send(ch, ...data);
    }
  }
};
function getTrayIconPath$1() {
  return path.join(process.env.VITE_PUBLIC || "", "stock.ico");
}
function setupIpcMainHandle({ tray: tray2, floatWin: floatWin2, win: win2 }) {
  ipcMainApi.handle("update-tray", (data) => {
    if (tray2) {
      tray2.setToolTip(data);
    }
  });
  ipcMainApi.handle("update-tray-icon", (data) => {
    if (!tray2) return;
    try {
      const change = parseFloat(data.change);
      const isUp = change >= 0;
      const sign = isUp ? "+" : "";
      const size = 16;
      const pixels = Buffer.alloc(size * size * 4);
      const bgColor = { b: 40, g: 40, r: 40, a: 255 };
      const upColor = { b: 79, g: 77, r: 255, a: 255 };
      const downColor = { b: 26, g: 196, r: 82, a: 255 };
      const barColor = isUp ? upColor : downColor;
      const maxChange = 10;
      const absChange = Math.min(Math.abs(change), maxChange);
      const barHeight = Math.max(
        2,
        Math.round(absChange / maxChange * (size - 4))
      );
      for (let y = 0; y < size; y++) {
        for (let x = 0; x < size; x++) {
          const offset = (y * size + x) * 4;
          let color = bgColor;
          const barWidth = 8;
          const barLeft = (size - barWidth) / 2;
          const barRight = barLeft + barWidth;
          if (x >= barLeft && x < barRight) {
            if (isUp) {
              const barTop = size - 2 - barHeight;
              if (y >= barTop && y < size - 2) {
                color = barColor;
              }
            } else {
              if (y >= 2 && y < 2 + barHeight) {
                color = barColor;
              }
            }
          }
          if (y === Math.floor(size / 2) && x >= 1 && x < size - 1) {
            color = { b: 100, g: 100, r: 100, a: 255 };
          }
          pixels[offset] = color.b;
          pixels[offset + 1] = color.g;
          pixels[offset + 2] = color.r;
          pixels[offset + 3] = color.a;
        }
      }
      const icon = nativeImage.createFromBuffer(pixels, {
        width: size,
        height: size
      });
      tray2.setImage(icon);
      tray2.setToolTip(
        `${data.name}: ${data.price} (${sign}${change.toFixed(2)}%)`
      );
    } catch (e) {
      console.error("更新托盘图标失败:", e);
    }
  });
  ipcMainApi.handle("close-float-window", () => {
    console.log("收到关闭悬浮窗请求");
    if (floatWin2 && !floatWin2.isDestroyed()) {
      floatWin2.close();
      console.log("悬浮窗已关闭");
    }
  });
  ipcMainApi.handle("show-notification", (data) => {
    if (Notification.isSupported()) {
      const notification = new Notification({
        title: data.title,
        body: data.body,
        icon: getTrayIconPath$1()
      });
      notification.on("click", () => {
        if (win2) {
          win2.show();
          win2.focus();
        }
      });
      notification.show();
      console.log("系统通知已发送:", data.title);
    }
  });
}
const __dirname$1 = path.dirname(fileURLToPath(import.meta.url));
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  app.quit();
}
const userDataPath = app.getPath("userData");
const appWithFlags = app;
appWithFlags.isQuitting = false;
process.env.DIST = path.join(__dirname$1, "../dist");
process.env.VITE_PUBLIC = app.isPackaged ? process.env.DIST : path.join(process.env.DIST, "../public");
let win = null;
let floatWin = null;
let tray = null;
let backendProcess = null;
const VITE_DEV_SERVER_URL = process.env["VITE_DEV_SERVER_URL"];
function startBackend() {
  if (!app.isPackaged) {
    console.log("开发模式，请手动启动后端服务");
    return;
  }
  const backendPath = path.join(process.resourcesPath, "backend");
  const binaryName = process.platform === "win32" ? "stock-monitor-backend.exe" : "stock-monitor-backend";
  const backendExe = path.join(backendPath, binaryName);
  console.log("启动后端服务:", backendExe);
  console.log("工作目录:", backendPath);
  backendProcess = spawn(backendExe, [], {
    cwd: backendPath,
    stdio: ["ignore", "pipe", "pipe"],
    windowsHide: false
    // 显示控制台窗口方便调试，正式版可改为 true
  });
  backendProcess.stdout?.on("data", (data) => {
    console.log(`[后端] ${data}`);
  });
  backendProcess.stderr?.on("data", (data) => {
    console.error(`[后端错误] ${data}`);
  });
  backendProcess.on("close", (code) => {
    console.log(`后端进程退出，代码: ${code}`);
    if (code !== 0 && !appWithFlags.isQuitting) {
      console.log("后端意外退出，3秒后尝试重启...");
      setTimeout(startBackend, 3e3);
    }
  });
  backendProcess.on("error", (err) => {
    console.error("启动后端失败:", err);
  });
}
function stopBackend() {
  if (backendProcess) {
    console.log("停止后端服务...");
    if (process.platform === "win32") {
      spawn("taskkill", ["/pid", String(backendProcess.pid), "/f", "/t"]);
    } else {
      backendProcess.kill();
    }
    backendProcess = null;
  }
}
const FLOAT_WIN_WIDTH = 200;
const FLOAT_WIN_HEIGHT = 150;
const EDGE_MARGIN = 0;
const EDGE_THRESHOLD = 20;
function getTrayIconPath() {
  return path.join(process.env.VITE_PUBLIC || "", "stock.ico");
}
function createFloatWindow() {
  if (floatWin) return;
  const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize;
  floatWin = new BrowserWindow({
    width: FLOAT_WIN_WIDTH,
    height: FLOAT_WIN_HEIGHT,
    x: screenWidth - FLOAT_WIN_WIDTH - 20,
    // 默认右下角
    y: screenHeight - FLOAT_WIN_HEIGHT - 20,
    frame: false,
    // 无边框
    transparent: true,
    // 透明背景
    alwaysOnTop: true,
    // 始终置顶
    skipTaskbar: true,
    // 不在任务栏显示
    resizable: false,
    // 不可调整大小
    hasShadow: false,
    // 无阴影
    webPreferences: {
      preload: path.join(__dirname$1, "preload.mjs"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });
  if (VITE_DEV_SERVER_URL) {
    floatWin.loadURL(`${VITE_DEV_SERVER_URL}#/float`);
  } else {
    floatWin.loadFile(path.join(process.env.DIST || "", "index.html"), { hash: "/float" });
  }
  floatWin.webContents.on("did-finish-load", () => {
    console.log("悬浮窗页面加载完成");
  });
  floatWin.on("focus", () => {
    floatWin?.setOpacity(1);
  });
  floatWin.on("blur", () => {
    floatWin?.setOpacity(0.7);
  });
  floatWin.on("moved", () => {
    if (!floatWin) return;
    const [x, y] = floatWin.getPosition();
    const { width: screenWidth2, height: screenHeight2 } = screen.getPrimaryDisplay().workAreaSize;
    let newX = x;
    let newY = y;
    if (x < EDGE_THRESHOLD) {
      newX = EDGE_MARGIN;
    }
    if (x + FLOAT_WIN_WIDTH > screenWidth2 - EDGE_THRESHOLD) {
      newX = screenWidth2 - FLOAT_WIN_WIDTH - EDGE_MARGIN;
    }
    if (y < EDGE_THRESHOLD) {
      newY = EDGE_MARGIN;
    }
    if (y + FLOAT_WIN_HEIGHT > screenHeight2 - EDGE_THRESHOLD) {
      newY = screenHeight2 - FLOAT_WIN_HEIGHT - EDGE_MARGIN;
    }
    if (newX !== x || newY !== y) {
      floatWin.setPosition(newX, newY, true);
    }
  });
  floatWin.on("closed", () => {
    floatWin = null;
  });
  floatWin.setOpacity(0.7);
  console.log("悬浮窗创建成功");
}
function createTray() {
  if (tray) return;
  const iconPath = getTrayIconPath();
  console.log("创建托盘图标，路径:", iconPath);
  try {
    const trayIcon = nativeImage.createFromPath(iconPath);
    if (trayIcon.isEmpty()) {
      console.error("托盘图标加载失败");
      return;
    }
    tray = new Tray(trayIcon);
    const contextMenu = Menu.buildFromTemplate([
      { label: "显示主窗口", click: () => win?.show() },
      {
        label: "显示悬浮窗",
        click: () => {
          if (floatWin) {
            floatWin.show();
          } else {
            createFloatWindow();
          }
        }
      },
      { type: "separator" },
      {
        label: "退出",
        click: () => {
          appWithFlags.isQuitting = true;
          app.quit();
        }
      }
    ]);
    tray.setToolTip("股票监控助手");
    tray.setContextMenu(contextMenu);
    tray.on("click", () => {
      if (win) {
        if (win.isVisible()) {
          win.hide();
        } else {
          win.show();
          win.focus();
        }
      }
    });
    console.log("托盘图标创建成功");
  } catch (error) {
    console.error("创建托盘图标失败:", error);
  }
}
function createWindow() {
  const browserWindow = new BrowserWindow({
    width: 1200,
    height: 750,
    minWidth: 1e3,
    minHeight: 600,
    icon: getTrayIconPath(),
    webPreferences: {
      preload: path.join(__dirname$1, "preload.mjs"),
      sandbox: false,
      nodeIntegration: false,
      contextIsolation: true
    }
  });
  win = browserWindow;
  browserWindow.setMenuBarVisibility(false);
  browserWindow.webContents.on("did-finish-load", () => {
    browserWindow.webContents.send("main-process-message", (/* @__PURE__ */ new Date()).toLocaleString());
  });
  if (VITE_DEV_SERVER_URL) {
    browserWindow.loadURL(VITE_DEV_SERVER_URL);
    browserWindow.webContents.openDevTools();
  } else {
    browserWindow.loadFile(path.join(process.env.DIST || "", "index.html"));
  }
  browserWindow.webContents.on("did-fail-load", (_event, errorCode, errorDescription) => {
    console.log("窗口加载失败:", errorCode, errorDescription);
    if (errorCode === -102) {
      setTimeout(() => {
        if (!browserWindow.isDestroyed() && VITE_DEV_SERVER_URL) {
          browserWindow.loadURL(VITE_DEV_SERVER_URL);
        }
      }, 1e3);
    }
  });
  browserWindow.on("minimize", () => {
    browserWindow.hide();
  });
  browserWindow.on("close", (event) => {
    if (!appWithFlags.isQuitting) {
      event.preventDefault();
      browserWindow.hide();
    }
  });
  browserWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url);
    return { action: "deny" };
  });
  return browserWindow;
}
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
app.on("second-instance", () => {
  if (win) {
    if (win.isMinimized()) win.restore();
    if (!win.isVisible()) win.show();
    win.focus();
  }
});
app.on("before-quit", () => {
  appWithFlags.isQuitting = true;
  stopBackend();
});
app.on("activate", () => {
  if (win) {
    if (win.isMinimized()) win.restore();
    if (!win.isVisible()) win.show();
    win.focus();
  } else if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
app.whenReady().then(() => {
  console.log("应用启动，用户数据目录:", userDataPath);
  startBackend();
  createTray();
  createWindow();
  createFloatWindow();
  setupIpcMainHandle({ tray, floatWin, win });
});
