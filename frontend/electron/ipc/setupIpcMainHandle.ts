import {
  type BrowserWindow,
  type Tray,
  Notification,
  nativeImage,
} from "electron";
import { ipcMainApi } from "./ipcMain";
import { getTrayIconPath } from "../utils";

interface Context {
  tray: Tray;
  floatWin: BrowserWindow;
  win: BrowserWindow;
}
export function setupIpcMainHandle({ tray, floatWin, win }: Context) {
  // IPC: 更新托盘提示文本
  ipcMainApi.handle("update-tray", (data) => {
    if (tray) {
      tray.setToolTip(data);
    }
  });
  // IPC: 更新托盘图标（绘制 K 线柱状图）
  ipcMainApi.handle("update-tray-icon", (data) => {
    if (!tray) return;

    try {
      const change = parseFloat(data.change);
      const isUp = change >= 0;
      const sign = isUp ? "+" : "";

      const size = 16;
      // BGRA 格式（Windows 使用 BGRA）
      const pixels = Buffer.alloc(size * size * 4);

      // 颜色定义 (BGRA 格式)
      const bgColor = { b: 40, g: 40, r: 40, a: 255 }; // 深灰背景
      const upColor = { b: 79, g: 77, r: 255, a: 255 }; // 红色（涨）
      const downColor = { b: 26, g: 196, r: 82, a: 255 }; // 绿色（跌）
      const barColor = isUp ? upColor : downColor;

      // 计算柱状图高度（基于涨跌幅，最大 10%）
      const maxChange = 10;
      const absChange = Math.min(Math.abs(change), maxChange);
      const barHeight = Math.max(
        2,
        Math.round((absChange / maxChange) * (size - 4))
      );

      // 绘制像素
      for (let y = 0; y < size; y++) {
        for (let x = 0; x < size; x++) {
          const offset = (y * size + x) * 4;

          // 默认背景色
          let color = bgColor;

          // 绘制柱状图（居中，宽度 8px）
          const barWidth = 8;
          const barLeft = (size - barWidth) / 2;
          const barRight = barLeft + barWidth;

          if (x >= barLeft && x < barRight) {
            if (isUp) {
              // 涨：从底部向上
              const barTop = size - 2 - barHeight;
              if (y >= barTop && y < size - 2) {
                color = barColor;
              }
            } else {
              // 跌：从顶部向下
              if (y >= 2 && y < 2 + barHeight) {
                color = barColor;
              }
            }
          }

          // 绘制中线（昨收位置）
          if (y === Math.floor(size / 2) && x >= 1 && x < size - 1) {
            color = { b: 100, g: 100, r: 100, a: 255 }; // 灰色中线
          }

          pixels[offset] = color.b;
          pixels[offset + 1] = color.g;
          pixels[offset + 2] = color.r;
          pixels[offset + 3] = color.a;
        }
      }

      const icon = nativeImage.createFromBuffer(pixels, {
        width: size,
        height: size,
      });

      tray.setImage(icon);
      tray.setToolTip(
        `${data.name}: ${data.price} (${sign}${change.toFixed(2)}%)`
      );
    } catch (e) {
      console.error("更新托盘图标失败:", e);
    }
  });
  // IPC: 更新悬浮窗数据
  // ipcMain.on("update-float-window", (_event, data: any) => {
  //   if (floatWin && !floatWin.isDestroyed()) {
  //     floatWin.webContents.send("stock-data-update", data);
  //   }
  // });

  // IPC: 关闭悬浮窗
  // ipcMain.on("close-float-window", () => {
  //   console.log("收到关闭悬浮窗请求");
  //   if (floatWin && !floatWin.isDestroyed()) {
  //     floatWin.close();
  //     floatWin = null;
  //     console.log("悬浮窗已关闭");
  //   }
  // });
  ipcMainApi.handle("close-float-window", () => {
    console.log("收到关闭悬浮窗请求");
    if (floatWin && !floatWin.isDestroyed()) {
      floatWin.close();
      // TODO
      // floatWin = null;
      console.log("悬浮窗已关闭");
    }
  });

  // IPC: 发送系统通知
  ipcMainApi.handle("show-notification", (data) => {
    if (Notification.isSupported()) {
      const notification = new Notification({
        title: data.title,
        body: data.body,
        icon: getTrayIconPath(),
      });

      // 点击通知时显示主窗口
      notification.on("click", () => {
        if (win) {
          win.show();
          win.focus();
        }
      });

      notification.show();
      console.log("系统通知已发送:", data.title);
    }
  });
}
