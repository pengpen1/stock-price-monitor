import { app, ipcMain, BrowserWindow, Tray, Menu, shell } from "electron";
import path from "node:path";
import { fileURLToPath } from "node:url";
const __dirname$1 = path.dirname(fileURLToPath(import.meta.url));
const appWithFlags = app;
appWithFlags.isQuitting = false;
process.env.DIST = path.join(__dirname$1, "../dist");
process.env.VITE_PUBLIC = app.isPackaged ? process.env.DIST : path.join(process.env.DIST, "../public");
let win;
let tray = null;
const VITE_DEV_SERVER_URL = process.env["VITE_DEV_SERVER_URL"];
function createWindow() {
  win = new BrowserWindow({
    icon: path.join(process.env.VITE_PUBLIC || "", "vite.svg"),
    webPreferences: {
      preload: path.join(__dirname$1, "preload.js"),
      sandbox: false,
      nodeIntegration: true,
      // Optional: enable if you need node in renderer (not recommended but helpful for debugging)
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
  win.webContents.on("did-fail-load", (event, errorCode, errorDescription) => {
    console.log("Failed to load window:", errorCode, errorDescription);
    if (errorCode === -102) {
      setTimeout(() => {
        if (win && VITE_DEV_SERVER_URL) {
          console.log("Retrying load URL...");
          win.loadURL(VITE_DEV_SERVER_URL);
        }
      }, 1e3);
    }
  });
  win.on("minimize", () => {
    if (win) {
      win.hide();
    }
  });
  win.on("close", (event) => {
    if (!appWithFlags.isQuitting && win) {
      event.preventDefault();
      win.hide();
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
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
    win = null;
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
  createWindow();
  const { nativeImage } = require("electron");
  const iconBase64 = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGRSURBVFiF7ZY9TsNAEIW/WYcGiQKJgoKWgoqOI3AEjkBJRUVFR8cROAJHoKOipKKgoECiQPyIxGbHBRvFJN7sxnZCwZNW8u7svJl9s7MrGGKIIf4rZNAOAJRSM8AHYBzYBJ6BZ+DRGPPRr5+BC1BKzQKPwBjwBrwCr8A7cAOcGmMu+vVVcAGllAJugXFgGXgCXoAP4Bm4Bk6MMef9+iu4gFJqHLgDJoAV4AF4AT6BZ+AKODbGnPXrM3cBpdQEcA9MAqvAPfAKfAFPwCVwZIw57ddv7gJKqUngAZgC1oA74A34Bh6BC+DIGHPSr+/cBZRSU8AjMA2sA7fAO/ADPAAXwKEx5rhf/7kLKKWmgSdgBlgHboAP4Bd4AM6BQ2PMUb/+cxdQSs0AT8AssAFcAx/AL3APnAEHxpjDfmPkLqCUmgWegTlgE7gCPoE/4A44BfaNMQf9xsldQCk1BzwDC8AWcAl8AX/ALXACHBhj9vuNlbuAUmoeeAEWgW3gAvgG/oAb4BjYN8bs9RsijCH+Nf4AYcnkMPJB3REAAAAASUVORK5CYII=";
  let trayIcon = nativeImage.createFromDataURL(`data:image/png;base64,${iconBase64}`);
  trayIcon = trayIcon.resize({ width: 16, height: 16 });
  tray = new Tray(trayIcon);
  const contextMenu = Menu.buildFromTemplate([
    { label: "显示主窗口", click: () => win?.show() },
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
    if (win?.isVisible()) {
      win.hide();
    } else {
      win?.show();
    }
  });
});
