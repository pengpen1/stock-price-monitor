import { app, ipcMain, BrowserWindow, shell, nativeImage, Tray, Menu, screen } from "electron";
import path from "node:path";
import { fileURLToPath } from "node:url";
const __dirname$1 = path.dirname(fileURLToPath(import.meta.url));
const appWithFlags = app;
appWithFlags.isQuitting = false;
process.env.DIST = path.join(__dirname$1, "../dist");
process.env.VITE_PUBLIC = app.isPackaged ? process.env.DIST : path.join(process.env.DIST, "../public");
let win = null;
let floatWin = null;
let tray = null;
const VITE_DEV_SERVER_URL = process.env["VITE_DEV_SERVER_URL"];
const FLOAT_WIN_WIDTH = 180;
const FLOAT_WIN_HEIGHT = 120;
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
      preload: path.join(__dirname$1, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });
  if (VITE_DEV_SERVER_URL) {
    floatWin.loadURL(`${VITE_DEV_SERVER_URL}#/float`);
    floatWin.webContents.openDevTools({ mode: "detach" });
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
  win = new BrowserWindow({
    width: 1e3,
    height: 700,
    icon: getTrayIconPath(),
    webPreferences: {
      preload: path.join(__dirname$1, "preload.cjs"),
      sandbox: false,
      nodeIntegration: false,
      contextIsolation: true
    }
  });
  win.setMenuBarVisibility(false);
  win.webContents.on("did-finish-load", () => {
    win?.webContents.send("main-process-message", (/* @__PURE__ */ new Date()).toLocaleString());
  });
  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL);
    win.webContents.openDevTools();
  } else {
    win.loadFile(path.join(process.env.DIST || "", "index.html"));
  }
  win.webContents.on("did-fail-load", (_event, errorCode, errorDescription) => {
    console.log("窗口加载失败:", errorCode, errorDescription);
    if (errorCode === -102) {
      setTimeout(() => {
        if (win && VITE_DEV_SERVER_URL) {
          win.loadURL(VITE_DEV_SERVER_URL);
        }
      }, 1e3);
    }
  });
  win.on("minimize", (event) => {
    event.preventDefault();
    win?.hide();
  });
  win.on("close", (event) => {
    if (!appWithFlags.isQuitting) {
      event.preventDefault();
      win?.hide();
    }
  });
  win.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url);
    return { action: "deny" };
  });
}
ipcMain.on("update-tray", (_event, text) => {
  if (tray) {
    tray.setToolTip(text);
  }
});
ipcMain.on("update-float-window", (_event, data) => {
  if (floatWin && !floatWin.isDestroyed()) {
    floatWin.webContents.send("stock-data-update", data);
  }
});
ipcMain.on("close-float-window", () => {
  console.log("收到关闭悬浮窗请求");
  if (floatWin && !floatWin.isDestroyed()) {
    floatWin.close();
    floatWin = null;
    console.log("悬浮窗已关闭");
  }
});
ipcMain.on("float-window-drag", () => {
});
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
app.on("before-quit", () => {
  appWithFlags.isQuitting = true;
});
app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
app.whenReady().then(() => {
  createTray();
  createWindow();
  createFloatWindow();
});
