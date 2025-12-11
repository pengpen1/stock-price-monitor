import { app as a, ipcMain as b, Notification as L, BrowserWindow as E, shell as z, nativeImage as F, Tray as Q, Menu as G, screen as j } from "electron";
import c from "node:path";
import { fileURLToPath as N } from "node:url";
import { spawn as H } from "node:child_process";
const P = c.dirname(N(import.meta.url)), q = a.getPath("userData"), m = a;
m.isQuitting = !1;
process.env.DIST = c.join(P, "../dist");
process.env.VITE_PUBLIC = a.isPackaged ? process.env.DIST : c.join(process.env.DIST, "../public");
let n = null, o = null, r = null, f = null;
const w = process.env.VITE_DEV_SERVER_URL;
function M() {
  if (!a.isPackaged) {
    console.log("开发模式，请手动启动后端服务");
    return;
  }
  const i = c.join(process.resourcesPath, "backend"), t = c.join(i, "stock-monitor-backend.exe");
  console.log("启动后端服务:", t), console.log("工作目录:", i), f = H(t, [], {
    cwd: i,
    stdio: ["ignore", "pipe", "pipe"],
    windowsHide: !1
    // 显示控制台窗口方便调试，正式版可改为 true
  }), f.stdout?.on("data", (e) => {
    console.log(`[后端] ${e}`);
  }), f.stderr?.on("data", (e) => {
    console.error(`[后端错误] ${e}`);
  }), f.on("close", (e) => {
    console.log(`后端进程退出，代码: ${e}`), e !== 0 && !m.isQuitting && (console.log("后端意外退出，3秒后尝试重启..."), setTimeout(M, 3e3));
  }), f.on("error", (e) => {
    console.error("启动后端失败:", e);
  });
}
function X() {
  f && (console.log("停止后端服务..."), process.platform === "win32" ? H("taskkill", ["/pid", String(f.pid), "/f", "/t"]) : f.kill(), f = null);
}
const k = 200, I = 150, _ = 0, D = 20;
function v() {
  return c.join(process.env.VITE_PUBLIC || "", "stock.ico");
}
function V() {
  if (o) return;
  const { width: i, height: t } = j.getPrimaryDisplay().workAreaSize;
  o = new E({
    width: k,
    height: I,
    x: i - k - 20,
    // 默认右下角
    y: t - I - 20,
    frame: !1,
    // 无边框
    transparent: !0,
    // 透明背景
    alwaysOnTop: !0,
    // 始终置顶
    skipTaskbar: !0,
    // 不在任务栏显示
    resizable: !1,
    // 不可调整大小
    hasShadow: !1,
    // 无阴影
    webPreferences: {
      preload: c.join(P, "preload.cjs"),
      contextIsolation: !0,
      nodeIntegration: !1
    }
  }), w ? o.loadURL(`${w}#/float`) : o.loadFile(c.join(process.env.DIST || "", "index.html"), { hash: "/float" }), o.webContents.on("did-finish-load", () => {
    console.log("悬浮窗页面加载完成");
  }), o.on("focus", () => {
    o?.setOpacity(1);
  }), o.on("blur", () => {
    o?.setOpacity(0.7);
  }), o.on("moved", () => {
    if (!o) return;
    const [e, d] = o.getPosition(), { width: T, height: s } = j.getPrimaryDisplay().workAreaSize;
    let l = e, g = d;
    e < D && (l = _), e + k > T - D && (l = T - k - _), d < D && (g = _), d + I > s - D && (g = s - I - _), (l !== e || g !== d) && o.setPosition(l, g, !0);
  }), o.on("closed", () => {
    o = null;
  }), o.setOpacity(0.7), console.log("悬浮窗创建成功");
}
function Y() {
  if (r) return;
  const i = v();
  console.log("创建托盘图标，路径:", i);
  try {
    const t = F.createFromPath(i);
    if (t.isEmpty()) {
      console.error("托盘图标加载失败");
      return;
    }
    r = new Q(t);
    const e = G.buildFromTemplate([
      { label: "显示主窗口", click: () => n?.show() },
      {
        label: "显示悬浮窗",
        click: () => {
          o ? o.show() : V();
        }
      },
      { type: "separator" },
      {
        label: "退出",
        click: () => {
          m.isQuitting = !0, a.quit();
        }
      }
    ]);
    r.setToolTip("股票监控助手"), r.setContextMenu(e), r.on("click", () => {
      n && (n.isVisible() ? n.hide() : (n.show(), n.focus()));
    }), console.log("托盘图标创建成功");
  } catch (t) {
    console.error("创建托盘图标失败:", t);
  }
}
function U() {
  n = new E({
    width: 1200,
    height: 750,
    minWidth: 1e3,
    minHeight: 600,
    icon: v(),
    webPreferences: {
      preload: c.join(P, "preload.cjs"),
      sandbox: !1,
      nodeIntegration: !1,
      contextIsolation: !0
    }
  }), n.setMenuBarVisibility(!1), n.webContents.on("did-finish-load", () => {
    n?.webContents.send("main-process-message", (/* @__PURE__ */ new Date()).toLocaleString());
  }), w ? (n.loadURL(w), n.webContents.openDevTools()) : n.loadFile(c.join(process.env.DIST || "", "index.html")), n.webContents.on("did-fail-load", (i, t, e) => {
    console.log("窗口加载失败:", t, e), t === -102 && setTimeout(() => {
      n && w && n.loadURL(w);
    }, 1e3);
  }), n.on("minimize", () => {
    n?.hide();
  }), n.on("close", (i) => {
    m.isQuitting || (i.preventDefault(), n?.hide());
  }), n.webContents.setWindowOpenHandler((i) => (z.openExternal(i.url), { action: "deny" }));
}
b.on("update-tray", (i, t) => {
  r && r.setToolTip(t);
});
b.on("update-tray-icon", (i, t) => {
  if (r)
    try {
      const e = parseFloat(t.change), d = e >= 0, T = d ? "+" : "", s = 16, l = Buffer.alloc(s * s * 4), g = { b: 40, g: 40, r: 40, a: 255 }, x = d ? { b: 79, g: 77, r: 255, a: 255 } : { b: 26, g: 196, r: 82, a: 255 }, C = 10, $ = Math.min(Math.abs(e), C), R = Math.max(2, Math.round($ / C * (s - 4)));
      for (let p = 0; p < s; p++)
        for (let h = 0; h < s; h++) {
          const y = (p * s + h) * 4;
          let u = g;
          const S = 8, W = (s - S) / 2, O = W + S;
          if (h >= W && h < O)
            if (d) {
              const A = s - 2 - R;
              p >= A && p < s - 2 && (u = x);
            } else
              p >= 2 && p < 2 + R && (u = x);
          p === Math.floor(s / 2) && h >= 1 && h < s - 1 && (u = { b: 100, g: 100, r: 100, a: 255 }), l[y] = u.b, l[y + 1] = u.g, l[y + 2] = u.r, l[y + 3] = u.a;
        }
      const B = F.createFromBuffer(l, {
        width: s,
        height: s
      });
      r.setImage(B), r.setToolTip(`${t.name}: ${t.price} (${T}${e.toFixed(2)}%)`);
    } catch (e) {
      console.error("更新托盘图标失败:", e);
    }
});
b.on("update-float-window", (i, t) => {
  o && !o.isDestroyed() && o.webContents.send("stock-data-update", t);
});
b.on("close-float-window", () => {
  console.log("收到关闭悬浮窗请求"), o && !o.isDestroyed() && (o.close(), o = null, console.log("悬浮窗已关闭"));
});
b.on("show-notification", (i, t) => {
  if (L.isSupported()) {
    const e = new L({
      title: t.title,
      body: t.body,
      icon: v()
    });
    e.on("click", () => {
      n && (n.show(), n.focus());
    }), e.show(), console.log("系统通知已发送:", t.title);
  }
});
a.on("window-all-closed", () => {
  process.platform !== "darwin" && a.quit();
});
a.on("before-quit", () => {
  m.isQuitting = !0, X();
});
a.on("activate", () => {
  E.getAllWindows().length === 0 && U();
});
a.whenReady().then(() => {
  console.log("应用启动，用户数据目录:", q), M(), Y(), U(), V();
});
