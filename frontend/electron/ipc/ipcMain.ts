import { BrowserWindow, ipcMain, IpcMainEvent } from "electron";
import type { MainChannel, RenderChannel } from "./channels";

export const ipcMainApi = {
  handle<T extends keyof RenderChannel>(ch: T, fn: RenderChannel[T]) {
    ipcMain.handle(ch, (_e, data) => fn(data));
  },

  on<T extends keyof RenderChannel>(ch: T, fn: RenderChannel[T]) {
    // @ts-ignore
    const handle = (_e: IpcMainEvent, data) => {
      fn(data);
    };
    ipcMain.on(ch, handle);
    return () => {
      ipcMain.off(ch, handle);
    };
  },

  send<T extends keyof MainChannel>(
    ch: T,
    ...data: Parameters<MainChannel[T]>
  ) {
    const windows = BrowserWindow.getAllWindows();
    for (const w of windows) {
      w.webContents.send(ch, ...data);
    }
  },
};
