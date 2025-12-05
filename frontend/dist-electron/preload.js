import require$$0 from "electron";
function getDefaultExportFromCjs(x) {
  return x && x.__esModule && Object.prototype.hasOwnProperty.call(x, "default") ? x["default"] : x;
}
var preload$1 = {};
var hasRequiredPreload;
function requirePreload() {
  if (hasRequiredPreload) return preload$1;
  hasRequiredPreload = 1;
  const { contextBridge, ipcRenderer } = require$$0;
  contextBridge.exposeInMainWorld("ipcRenderer", {
    // 监听主进程消息
    on: (channel, listener) => {
      ipcRenderer.on(channel, (_event, ...args) => listener(...args));
    },
    // 移除监听
    off: (channel, listener) => {
      ipcRenderer.off(channel, listener);
    },
    // 发送消息到主进程
    send: (channel, ...args) => {
      ipcRenderer.send(channel, ...args);
    },
    // 发送消息并等待响应
    invoke: (channel, ...args) => {
      return ipcRenderer.invoke(channel, ...args);
    }
  });
  console.log("Preload 脚本加载成功");
  return preload$1;
}
var preloadExports = requirePreload();
const preload = /* @__PURE__ */ getDefaultExportFromCjs(preloadExports);
export {
  preload as default
};
