/**
 * 格式化工具函数
 * 数字、日期、金额等格式化方法
 */

/**
 * 格式化成交量（转换为万/亿）
 */
export function formatVolume(vol: number): string {
  if (vol >= 100000000) {
    return `${(vol / 100000000).toFixed(2)}亿`
  } else if (vol >= 10000) {
    return `${(vol / 10000).toFixed(2)}万`
  }
  return vol.toString()
}

/**
 * 格式化金额（转换为万/亿）
 */
export function formatAmount(amount: number): string {
  if (amount >= 100000000) {
    return `${(amount / 100000000).toFixed(2)}亿`
  } else if (amount >= 10000) {
    return `${(amount / 10000).toFixed(2)}万`
  }
  return amount.toFixed(2)
}

/**
 * 格式化百分比
 */
export function formatPercent(value: number, decimals = 2): string {
  const sign = value >= 0 ? "+" : ""
  return `${sign}${value.toFixed(decimals)}%`
}

/**
 * 格式化价格
 */
export function formatPrice(price: number, decimals = 2): string {
  return price.toFixed(decimals)
}

/**
 * 格式化日期时间
 */
export function formatDateTime(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, "0")
  const day = String(d.getDate()).padStart(2, "0")
  const hour = String(d.getHours()).padStart(2, "0")
  const minute = String(d.getMinutes()).padStart(2, "0")
  return `${year}-${month}-${day} ${hour}:${minute}`
}

/**
 * 格式化日期
 */
export function formatDate(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, "0")
  const day = String(d.getDate()).padStart(2, "0")
  return `${year}-${month}-${day}`
}

/**
 * 格式化时间
 */
export function formatTime(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date
  const hour = String(d.getHours()).padStart(2, "0")
  const minute = String(d.getMinutes()).padStart(2, "0")
  return `${hour}:${minute}`
}
