import type { IpcRendererApi } from "../electron/ipc/ipcRenderer"
declare global {
  interface Window {
    ipcRendererApi: IpcRendererApi
  }
}
