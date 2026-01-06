import { ipcRenderer, type IpcRendererEvent } from "electron"
import type { MainChannel, RenderChannel } from "./channels"

export const ipcRendererApi = {
  invoke<T extends keyof RenderChannel>(ch: T, ...data: Parameters<RenderChannel[T]>) {
    return ipcRenderer.invoke(ch, ...data) as Promise<Awaited<ReturnType<RenderChannel[T]>>>
  },

  send<T extends keyof RenderChannel>(ch: T, ...data: Parameters<RenderChannel[T]>) {
    ipcRenderer.send(ch, ...data)
  },

  on<T extends keyof MainChannel>(ch: T, handler: MainChannel[T]) {
    // @ts-expect-error ignore
    const fn = (_e: IpcRendererEvent, data) => {
      handler(data)
    }
    ipcRenderer.addListener(ch, fn)
    return () => {
      ipcRenderer.removeListener(ch, fn)
    }
  },
}

export type IpcRendererApi = typeof ipcRendererApi
