const { contextBridge, ipcRenderer } = require('electron')

// 暴露 ipcRenderer 到渲染进程
contextBridge.exposeInMainWorld('ipcRenderer', {
  // 监听主进程消息
  on: (channel: string, listener: (...args: any[]) => void) => {
    ipcRenderer.on(channel, (_event: any, ...args: any[]) => listener(...args))
  },
  // 移除监听
  off: (channel: string, listener: (...args: any[]) => void) => {
    ipcRenderer.off(channel, listener)
  },
  // 发送消息到主进程
  send: (channel: string, ...args: any[]) => {
    ipcRenderer.send(channel, ...args)
  },
  // 发送消息并等待响应
  invoke: (channel: string, ...args: any[]) => {
    return ipcRenderer.invoke(channel, ...args)
  },
})

console.log('Preload 脚本加载成功')
