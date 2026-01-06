// 参数最多为一个，如果是复杂数据使用对象进行扩展
// renderer->main
export interface RenderChannel {
  "show-notification": (data: { title: string; body: string }) => void;
  "close-float-window": () => void;
  "update-tray": (data: string) => void;
  "update-tray-icon": (data: {
    change: string;
    price: string;
    name: string;
    open?: string;
    high?: string;
    low?: string;
    pre_close?: string;
  }) => void;
}

// main->renderer
export interface MainChannel {
  "stock-data-updated": (data: any) => void;
}
