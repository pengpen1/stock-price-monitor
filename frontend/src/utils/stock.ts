/**
 * 股票相关工具函数
 * 涨跌颜色、涨停价计算等
 */

/**
 * 获取涨跌颜色 class
 */
export function getPriceClass(changePercent: number | string): string {
  const change = typeof changePercent === "string" ? parseFloat(changePercent) : changePercent
  if (change > 0) return "text-red-500"
  if (change < 0) return "text-green-500"
  return "text-slate-500"
}

/**
 * 获取涨跌背景色 class
 */
export function getPriceBgClass(changePercent: number | string): string {
  const change = typeof changePercent === "string" ? parseFloat(changePercent) : changePercent
  if (change > 0) return "bg-red-50 text-red-600"
  if (change < 0) return "bg-green-50 text-green-600"
  return "bg-slate-50 text-slate-600"
}

/**
 * 计算涨停价（A股10%，科创板/创业板20%）
 */
export function calcLimitUpPrice(preClose: number, code: string): number {
  const rate = isKCBOrCYB(code) ? 0.2 : 0.1
  return Math.round(preClose * (1 + rate) * 100) / 100
}

/**
 * 计算跌停价
 */
export function calcLimitDownPrice(preClose: number, code: string): number {
  const rate = isKCBOrCYB(code) ? 0.2 : 0.1
  return Math.round(preClose * (1 - rate) * 100) / 100
}

/**
 * 判断是否是科创板或创业板
 */
export function isKCBOrCYB(code: string): boolean {
  // 科创板：688开头，创业板：300开头
  return code.startsWith("688") || code.startsWith("300")
}

/**
 * 标准化股票代码（添加市场前缀）
 */
export function normalizeStockCode(code: string): string {
  // 已有前缀
  if (code.startsWith("sh") || code.startsWith("sz")) {
    return code
  }

  // 上海：6开头
  if (code.startsWith("6")) {
    return `sh${code}`
  }

  // 深圳：0、3开头
  if (code.startsWith("0") || code.startsWith("3")) {
    return `sz${code}`
  }

  return code
}

/**
 * 获取纯数字股票代码
 */
export function getStockCodeNumber(code: string): string {
  return code.replace(/^(sh|sz)/, "")
}
