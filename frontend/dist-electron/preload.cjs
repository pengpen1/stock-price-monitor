const { contextBridge, ipcRenderer } = require('electron')

// 暴露 ipcRenderer 到渲染进程
contextBridge.exposeInMainWorld('ipcRenderer', {
  // 监听主进程消息
  on: (channel, listener) => {
    ipcRenderer.on(channel, (_event, ...args) => listener(...args))
  },
  // 移除监听
  off: (channel, listener) => {
    ipcRenderer.off(channel, listener)
  },
  // 发送消息到主进程
  send: (channel, ...args) => {
    ipcRenderer.send(channel, ...args)
  },
  // 发送消息并等待响应
  invoke: (channel, ...args) => {
    return ipcRenderer.invoke(channel, ...args)
  },
})

console.log('Preload 脚本加载成功')
