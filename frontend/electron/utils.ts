import path from "node:path";

export function getTrayIconPath(): string {
  return path.join(process.env.VITE_PUBLIC || "", "stock.ico");
}
