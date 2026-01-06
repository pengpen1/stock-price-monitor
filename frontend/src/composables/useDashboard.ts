/**
 * Dashboard 数据逻辑 Composable
 * 管理股票列表、分组、预警、拖拽排序等核心逻辑
 */
import { ref, computed, onMounted, onUnmounted } from "vue"
import {
  getStocks,
  addStock,
  removeStock,
  getSettings,
  reorderStocks,
  setAlert,
  getTriggeredAlerts,
  setFocusedStock,
  setStockGroup,
  addGroupApi,
  deleteGroupApi,
} from "@/api"

export function useDashboard() {
  // ========== 响应式状态 ==========
  const newStockCode = ref("")
  const stockData = ref<any[]>([])
  const stockOrder = ref<string[]>([])
  const alerts = ref<Record<string, any>>({})
  const stockGroups = ref<Record<string, string>>({})
  const indexData = ref<Record<string, any>>({})
  const loading = ref(false)
  const errorMsg = ref("")
  const refreshInterval = ref(5)
  const alertNotifications = ref<any[]>([])
  const focusedStock = ref<string | null>(null)

  // 分组和排序
  const currentGroup = ref("")
  const sortBy = ref("")
  const groupList = ref<string[]>([])

  // 拖拽状态
  const dragIndex = ref<number | null>(null)

  // 定时器
  let intervalId: ReturnType<typeof setInterval> | null = null
  let alertCheckId: ReturnType<typeof setInterval> | null = null

  // ========== 计算属性 ==========
  const indexList = computed(() => {
    const codes = ["sh000001", "sz399001", "sz399006", "sh000300"]
    return codes.map((c) => indexData.value[c]).filter(Boolean)
  })

  const sortIcon = computed(() => {
    if (sortBy.value === "change_desc") return "↓"
    if (sortBy.value === "change_asc") return "↑"
    return ""
  })

  const filteredStocks = computed(() => {
    let list = [...stockData.value]
    if (currentGroup.value) {
      list = list.filter((s) => stockGroups.value[s.code] === currentGroup.value)
    }
    if (sortBy.value === "change_desc") {
      list.sort((a, b) => parseFloat(b.change_percent) - parseFloat(a.change_percent))
    } else if (sortBy.value === "change_asc") {
      list.sort((a, b) => parseFloat(a.change_percent) - parseFloat(b.change_percent))
    }
    return list
  })

  // ========== 工具函数 ==========
  const getPriceClass = (changePercent: string) => {
    const value = parseFloat(changePercent)
    if (value > 0) return "text-red-500"
    if (value < 0) return "text-green-500"
    return "text-slate-600"
  }

  const getIndexClass = (changePercent: string) => {
    const value = parseFloat(changePercent || "0")
    if (value > 0) return "text-red-500"
    if (value < 0) return "text-green-500"
    return "text-slate-800"
  }

  const formatAmount = (amount: string) => {
    const val = parseFloat(amount || "0")
    if (val >= 100000000) return (val / 100000000).toFixed(2) + "亿"
    if (val >= 10000) return (val / 10000).toFixed(0) + "万"
    return val.toFixed(0)
  }

  const toggleSort = () => {
    if (sortBy.value === "") sortBy.value = "change_desc"
    else if (sortBy.value === "change_desc") sortBy.value = "change_asc"
    else sortBy.value = ""
  }

  // ========== 数据操作 ==========
  const fetchData = async () => {
    try {
      const res = await getStocks()
      if (stockOrder.value.length === 0) {
        stockOrder.value = res.stocks
      }
      const dataMap = res.data
      stockData.value = stockOrder.value.map((code: string) => dataMap[code]).filter(Boolean)
      alerts.value = res.alerts || {}
      stockGroups.value = res.groups || {}
      indexData.value = res.index_data || {}
      focusedStock.value = res.focused_stock || (res.stocks.length > 0 ? res.stocks[0] : null)

      const usedGroups = new Set(Object.values(stockGroups.value))
      const backendGroups = res.group_list || []
      const allGroups = new Set([...backendGroups, ...usedGroups])
      groupList.value = Array.from(allGroups) as string[]

      updateTray()
      if (res.focused_data) updateTrayIcon(res.focused_data)
    } catch (error) {
      console.error("获取数据失败:", error)
    }
  }

  const handleAddStock = async () => {
    if (!newStockCode.value) return
    loading.value = true
    errorMsg.value = ""
    try {
      const res = await addStock(newStockCode.value)
      if (res.status === "error") {
        errorMsg.value = res.message
      } else {
        const normalizedCode =
          newStockCode.value.startsWith("sh") || newStockCode.value.startsWith("sz")
            ? newStockCode.value
            : newStockCode.value.startsWith("6")
              ? `sh${newStockCode.value}`
              : `sz${newStockCode.value}`
        if (
          !stockOrder.value.includes(normalizedCode) &&
          !stockOrder.value.includes(newStockCode.value)
        ) {
          stockOrder.value.push(normalizedCode)
        }
        newStockCode.value = ""
        await fetchData()
      }
    } catch (e) {
      errorMsg.value = "添加失败，请检查后端连接"
    } finally {
      loading.value = false
    }
  }

  const handleRemoveStock = async (code: string) => {
    await removeStock(code)
    stockOrder.value = stockOrder.value.filter((c) => c !== code)
    stockData.value = stockData.value.filter((s) => s.code !== code)
  }

  // ========== 拖拽排序 ==========
  const handleDragStart = (index: number, e: DragEvent) => {
    dragIndex.value = index
    if (e.dataTransfer) e.dataTransfer.effectAllowed = "move"
  }

  const handleDrop = async (targetIndex: number) => {
    if (dragIndex.value === null || dragIndex.value === targetIndex) {
      dragIndex.value = null
      return
    }
    const list = filteredStocks.value
    const draggedStock = list[dragIndex.value]
    const newOrder = [...stockOrder.value]
    const fromIdx = newOrder.indexOf(draggedStock.code)
    const targetStock = list[targetIndex]
    const toIdx = newOrder.indexOf(targetStock.code)

    if (fromIdx !== -1 && toIdx !== -1) {
      newOrder.splice(fromIdx, 1)
      newOrder.splice(toIdx, 0, draggedStock.code)
      stockOrder.value = newOrder
      const dataMap = Object.fromEntries(stockData.value.map((s) => [s.code, s]))
      stockData.value = newOrder.map((code) => dataMap[code]).filter(Boolean)
      await reorderStocks(newOrder)
    }
    dragIndex.value = null
  }

  // ========== 分组操作 ==========
  const addGroup = async (groupName: string, pendingStockCode?: string) => {
    if (!groupName.trim()) return
    await addGroupApi(groupName)
    if (!groupList.value.includes(groupName)) {
      groupList.value.push(groupName)
    }
    if (pendingStockCode) {
      await setStockGroup(pendingStockCode, groupName)
      stockGroups.value[pendingStockCode] = groupName
    }
  }

  const deleteGroup = async (group: string, deleteStocks: boolean) => {
    const res = await deleteGroupApi(group, deleteStocks)
    if (res.status === "success") {
      groupList.value = groupList.value.filter((g) => g !== group)
      if (deleteStocks && res.deleted_stocks?.length > 0) {
        stockOrder.value = stockOrder.value.filter((c) => !res.deleted_stocks.includes(c))
        stockData.value = stockData.value.filter((s) => !res.deleted_stocks.includes(s.code))
        for (const code of res.deleted_stocks) {
          delete stockGroups.value[code]
        }
      } else {
        for (const code in stockGroups.value) {
          if (stockGroups.value[code] === group) {
            delete stockGroups.value[code]
          }
        }
      }
      if (currentGroup.value === group) {
        currentGroup.value = ""
      }
    }
  }

  const moveStockToGroup = async (stockCode: string, group: string) => {
    await setStockGroup(stockCode, group)
    if (group) {
      stockGroups.value[stockCode] = group
      if (!groupList.value.includes(group)) groupList.value.push(group)
    } else {
      delete stockGroups.value[stockCode]
    }
  }

  const moveStockToTop = async (stockCode: string) => {
    const newOrder = [stockCode, ...stockOrder.value.filter((c) => c !== stockCode)]
    stockOrder.value = newOrder
    const dataMap = Object.fromEntries(stockData.value.map((s) => [s.code, s]))
    stockData.value = newOrder.map((code) => dataMap[code]).filter(Boolean)
    await reorderStocks(newOrder)
  }

  const moveStockToBottom = async (stockCode: string) => {
    const newOrder = [...stockOrder.value.filter((c) => c !== stockCode), stockCode]
    stockOrder.value = newOrder
    const dataMap = Object.fromEntries(stockData.value.map((s) => [s.code, s]))
    stockData.value = newOrder.map((code) => dataMap[code]).filter(Boolean)
    await reorderStocks(newOrder)
  }

  // ========== 预警操作 ==========
  const saveAlert = async (stockCode: string, alertForm: any) => {
    await setAlert(stockCode, alertForm)
    alerts.value[stockCode] = { ...alertForm }
  }

  const checkAlerts = async () => {
    try {
      const res = await getTriggeredAlerts()
      if (res.alerts?.length > 0) {
        alertNotifications.value.push(...res.alerts)
        for (const alert of res.alerts) {
          const title = `📈 ${alert.name} 预警触发`
          const body = alert.messages.join("\n") + `\n当前价: ${alert.price}`
          window.ipcRendererApi.invoke("show-notification", { title, body })
        }
      }
    } catch (e) {
      console.error("检查预警失败:", e)
    }
  }

  const dismissAlert = (index: number) => {
    alertNotifications.value.splice(index, 1)
  }

  // ========== 关注操作 ==========
  const handleSetFocus = async (code: string) => {
    await setFocusedStock(code)
    focusedStock.value = code
    const stock = stockData.value.find((s) => s.code === code)
    if (stock) updateTrayIcon(stock)
  }

  // ========== 托盘更新 ==========
  const updateTray = () => {
    if (stockData.value.length > 0) {
      const summary = stockData.value
        .slice(0, 3)
        .map((s) => `${s.name}: ${s.price} (${s.change_percent}%)`)
        .join("\n")
      window.ipcRendererApi.invoke("update-tray", summary)
    }
  }

  const updateTrayIcon = (focusedData: any) => {
    if (focusedData) {
      window.ipcRendererApi.invoke("update-tray-icon", {
        change: focusedData.change_percent,
        price: focusedData.price,
        name: focusedData.name,
      })
    }
  }

  // ========== 生命周期 ==========
  const startRefresh = async () => {
    try {
      const res = await getSettings()
      if (res.status === "success" && res.settings?.refresh_interval) {
        refreshInterval.value = res.settings.refresh_interval
      }
    } catch (e) {
      console.error("加载设置失败:", e)
    }
    await fetchData()
    intervalId = setInterval(fetchData, refreshInterval.value * 1000)
    alertCheckId = setInterval(checkAlerts, 3000)
  }

  const stopRefresh = () => {
    if (intervalId) clearInterval(intervalId)
    if (alertCheckId) clearInterval(alertCheckId)
  }

  return {
    // 状态
    newStockCode,
    stockData,
    stockOrder,
    alerts,
    stockGroups,
    indexData,
    loading,
    errorMsg,
    alertNotifications,
    focusedStock,
    currentGroup,
    sortBy,
    groupList,
    dragIndex,
    // 计算属性
    indexList,
    sortIcon,
    filteredStocks,
    // 工具函数
    getPriceClass,
    getIndexClass,
    formatAmount,
    toggleSort,
    // 数据操作
    fetchData,
    handleAddStock,
    handleRemoveStock,
    // 拖拽
    handleDragStart,
    handleDrop,
    // 分组
    addGroup,
    deleteGroup,
    moveStockToGroup,
    moveStockToTop,
    moveStockToBottom,
    // 预警
    saveAlert,
    dismissAlert,
    // 关注
    handleSetFocus,
    // 生命周期
    startRefresh,
    stopRefresh,
  }
}
