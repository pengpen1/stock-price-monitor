/**
 * 股票 Store
 * 管理股票列表、分组、预警等数据
 */
import { defineStore } from "pinia"
import { ref } from "vue"
import { getStocks, addStock, removeStock, reorderStocks, setFocusedStock } from "@/api"

// 股票信息接口
export interface StockInfo {
  code: string
  name: string
  price: number
  change_percent: number
  volume: number
  amount: number
  high: number
  low: number
  open: number
  pre_close: number
  group?: string
  focused?: boolean
}

// 指数信息接口
export interface IndexInfo {
  code: string
  name: string
  price: number
  change_percent: number
}

export const useStockStore = defineStore("stock", () => {
  // 股票列表
  const stocks = ref<Record<string, StockInfo>>({})
  const stockOrder = ref<string[]>([])

  // 指数数据
  const indexData = ref<Record<string, IndexInfo>>({})

  // 分组
  const groups = ref<string[]>([])

  // 加载状态
  const loading = ref(false)
  const lastUpdate = ref<Date | null>(null)

  // 加载股票数据
  const loadStocks = async () => {
    loading.value = true
    try {
      const data = await getStocks()
      stocks.value = data.stocks || {}
      stockOrder.value = data.order || Object.keys(data.stocks || {})
      indexData.value = data.index || {}
      groups.value = data.groups || []
      lastUpdate.value = new Date()
    } catch (e) {
      console.error("加载股票数据失败:", e)
    } finally {
      loading.value = false
    }
  }

  // 添加股票
  const addStockCode = async (code: string) => {
    try {
      const res = await addStock(code)
      if (res.status === "success") {
        await loadStocks()
      }
      return res
    } catch (e: any) {
      return { status: "error", message: e.message }
    }
  }

  // 删除股票
  const removeStockCode = async (code: string) => {
    try {
      const res = await removeStock(code)
      if (res.status === "success") {
        await loadStocks()
      }
      return res
    } catch (e: any) {
      return { status: "error", message: e.message }
    }
  }

  // 重新排序
  const reorder = async (newOrder: string[]) => {
    stockOrder.value = newOrder
    try {
      await reorderStocks(newOrder)
    } catch (e) {
      console.error("保存排序失败:", e)
    }
  }

  // 设置重点关注
  const setFocus = async (code: string) => {
    try {
      await setFocusedStock(code)
      await loadStocks()
    } catch (e) {
      console.error("设置关注失败:", e)
    }
  }

  return {
    stocks,
    stockOrder,
    indexData,
    groups,
    loading,
    lastUpdate,
    loadStocks,
    addStockCode,
    removeStockCode,
    reorder,
    setFocus,
  }
})
