<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
    <div class="max-w-6xl mx-auto">
      <!-- 头部区域 -->
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-slate-800">{{ $t('dashboard.title') }}</h1>
        <div class="flex items-center gap-2">
          <button @click="toggleLanguage" class="px-4 py-2 text-sm text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
            {{ locale === 'en' ? '中文' : 'English' }}
          </button>
          <button @click="$emit('openSettings')" class="px-4 py-2 text-sm text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
            ⚙️ {{ $t('common.settings') }}
          </button>
        </div>
      </div>

      <!-- 添加股票卡片 - 优化后的输入框 -->
      <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-5 mb-6">
        <div class="flex gap-3">
          <div class="relative flex-1">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </span>
            <input v-model="newStockCode" :placeholder="$t('dashboard.placeholder')" @keyup.enter="handleAddStock" :disabled="loading"
              class="w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white focus:border-transparent transition-all disabled:bg-slate-100 placeholder:text-slate-400" />
          </div>
          <button @click="handleAddStock" :disabled="loading"
            class="px-8 py-3.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl font-medium hover:from-blue-600 hover:to-blue-700 disabled:from-blue-300 disabled:to-blue-400 transition-all shadow-sm hover:shadow-md active:scale-[0.98]">
            {{ loading ? $t('dashboard.adding') : $t('dashboard.add') }}
          </button>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="errorMsg" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-6 text-sm">
        {{ errorMsg }}
      </div>

      <!-- 预警通知 -->
      <div v-if="alertNotifications.length > 0" class="mb-6 space-y-2">
        <div v-for="(alert, idx) in alertNotifications" :key="idx" 
          class="bg-amber-50 border border-amber-200 text-amber-800 px-4 py-3 rounded-lg text-sm flex justify-between items-start">
          <div>
            <div class="font-medium">{{ alert.name }} ({{ alert.code }})</div>
            <div v-for="msg in alert.messages" :key="msg" class="text-amber-600">{{ msg }}</div>
          </div>
          <button @click="dismissAlert(idx)" class="text-amber-400 hover:text-amber-600">✕</button>
        </div>
      </div>

      <!-- 股票列表卡片 -->
      <div class="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        <table class="w-full">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100">
              <th class="px-2 py-3 w-8"></th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{{ $t('dashboard.col_code') }}</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{{ $t('dashboard.col_name') }}</th>
              <th class="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase">{{ $t('dashboard.col_price') }}</th>
              <th class="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase">{{ $t('dashboard.col_change') }}</th>
              <th class="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase">{{ $t('dashboard.col_high') }}</th>
              <th class="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase">{{ $t('dashboard.col_low') }}</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">{{ $t('dashboard.col_time') }}</th>
              <th class="px-4 py-3 text-center text-xs font-semibold text-slate-500 uppercase">{{ $t('dashboard.col_action') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="(stock, index) in stockData" :key="stock.code" 
              class="hover:bg-slate-50 transition-colors cursor-pointer"
              draggable="true"
              @dragstart="handleDragStart(index)"
              @dragover.prevent="handleDragOver(index)"
              @drop="handleDrop(index)"
              @dragend="handleDragEnd"
              @click="handleRowClick(stock.code, $event)">
              <!-- 拖拽手柄 -->
              <td class="px-2 py-4 cursor-move text-slate-300 hover:text-slate-500" @click.stop>
                <span class="text-lg">⋮⋮</span>
              </td>
              <td class="px-4 py-4 text-sm font-mono text-slate-700">
                {{ stock.code }}
                <span v-if="alerts[stock.code]?.enabled" class="ml-1 text-amber-500" title="已设置预警">🔔</span>
              </td>
              <td class="px-4 py-4 text-sm font-medium text-slate-800">{{ stock.name }}</td>
              <td class="px-4 py-4 text-sm text-right font-semibold" :class="getPriceClass(stock.change_percent)">
                {{ stock.price }}
              </td>
              <td class="px-4 py-4 text-sm text-right font-medium" :class="getPriceClass(stock.change_percent)">
                <span class="inline-flex items-center gap-1">
                  <span v-if="parseFloat(stock.change_percent) > 0">↑</span>
                  <span v-else-if="parseFloat(stock.change_percent) < 0">↓</span>
                  {{ stock.change_percent }}%
                </span>
              </td>
              <td class="px-4 py-4 text-sm text-right text-slate-600">{{ stock.high }}</td>
              <td class="px-4 py-4 text-sm text-right text-slate-600">{{ stock.low }}</td>
              <td class="px-4 py-4 text-sm text-slate-500">{{ stock.time }}</td>
              <td class="px-4 py-4 text-center" @click.stop>
                <div class="flex items-center justify-center gap-2">
                  <button @click="handleSetFocus(stock.code)" 
                    :class="focusedStock === stock.code ? 'bg-amber-100 text-amber-600 border-amber-300' : 'text-slate-400 border-slate-200 hover:bg-amber-50 hover:text-amber-500'"
                    class="px-2 py-1 text-xs border rounded transition-colors" :title="$t('dashboard.focus')">
                    ⭐
                  </button>
                  <button @click="openAlertModal(stock)" class="px-2 py-1 text-xs text-blue-500 border border-blue-200 rounded hover:bg-blue-50 transition-colors">
                    {{ $t('dashboard.alert') }}
                  </button>
                  <button @click="handleRemoveStock(stock.code)" class="px-2 py-1 text-xs text-slate-500 border border-slate-200 rounded hover:bg-red-50 hover:text-red-500 transition-colors">
                    {{ $t('dashboard.remove') }}
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="stockData.length === 0">
              <td colspan="9" class="px-4 py-12 text-center text-slate-400 text-sm">{{ $t('dashboard.empty') }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 底部状态栏 -->
      <div class="mt-4 text-center text-xs text-slate-400">
        {{ $t('dashboard.auto_refresh', { interval: refreshInterval }) }}
      </div>
    </div>

    <!-- 预警设置弹窗 -->
    <div v-if="showAlertModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="closeAlertModal">
      <div class="bg-white rounded-xl shadow-xl w-96 p-6">
        <h3 class="text-lg font-semibold text-slate-800 mb-4">
          {{ $t('dashboard.alert_settings') }} - {{ currentAlertStock?.name }}
        </h3>
        
        <div class="space-y-4">
          <!-- 止盈价 -->
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1">{{ $t('dashboard.take_profit') }}</label>
            <input v-model="alertForm.take_profit" type="number" step="0.01" :placeholder="$t('dashboard.take_profit_hint')"
              class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          
          <!-- 止损价 -->
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1">{{ $t('dashboard.stop_loss') }}</label>
            <input v-model="alertForm.stop_loss" type="number" step="0.01" :placeholder="$t('dashboard.stop_loss_hint')"
              class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          
          <!-- 涨跌幅预警 -->
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1">{{ $t('dashboard.change_alert') }}</label>
            <input v-model="alertForm.change_alert" type="number" step="0.1" :placeholder="$t('dashboard.change_alert_hint')"
              class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          
          <!-- 启用开关 -->
          <div class="flex items-center gap-2">
            <input v-model="alertForm.enabled" type="checkbox" id="alert-enabled" class="w-4 h-4 text-blue-500" />
            <label for="alert-enabled" class="text-sm text-slate-600">{{ $t('dashboard.enable_alert') }}</label>
          </div>
        </div>
        
        <div class="flex justify-end gap-3 mt-6">
          <button @click="closeAlertModal" class="px-4 py-2 text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50">
            {{ $t('common.cancel') }}
          </button>
          <button @click="saveAlert" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
            {{ $t('common.save') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { getStocks, addStock, removeStock, getSettings, reorderStocks, setAlert, getTriggeredAlerts, setFocusedStock } from '../api'

const { locale } = useI18n()
const emit = defineEmits(['openSettings', 'openDetail'])

// 响应式状态
const newStockCode = ref('')
const stockData = ref<any[]>([])
const alerts = ref<Record<string, any>>({})
const loading = ref(false)
const errorMsg = ref('')
const refreshInterval = ref(5)
const alertNotifications = ref<any[]>([])
const focusedStock = ref<string | null>(null)

let intervalId: ReturnType<typeof setInterval> | null = null
let alertCheckId: ReturnType<typeof setInterval> | null = null

// 拖拽状态
const dragIndex = ref<number | null>(null)
const dragOverIndex = ref<number | null>(null)

// 预警弹窗状态
const showAlertModal = ref(false)
const currentAlertStock = ref<any>(null)
const alertForm = ref({
  take_profit: '',
  stop_loss: '',
  change_alert: '',
  enabled: true,
})

// 切换语言
const toggleLanguage = () => {
  locale.value = locale.value === 'en' ? 'zh' : 'en'
}

const getPriceClass = (changePercent: string) => {
  const value = parseFloat(changePercent)
  if (value > 0) return 'text-red-500'
  if (value < 0) return 'text-green-500'
  return 'text-slate-600'
}

// 拖拽排序
const handleDragStart = (index: number) => { dragIndex.value = index }
const handleDragOver = (index: number) => { dragOverIndex.value = index }
const handleDragEnd = () => { dragIndex.value = null; dragOverIndex.value = null }

const handleDrop = async (index: number) => {
  if (dragIndex.value === null || dragIndex.value === index) return
  
  const items = [...stockData.value]
  const [removed] = items.splice(dragIndex.value, 1)
  items.splice(index, 0, removed)
  stockData.value = items
  
  // 保存新顺序
  const newOrder = items.map(s => s.code)
  await reorderStocks(newOrder)
}

// 预警弹窗
const openAlertModal = (stock: any) => {
  currentAlertStock.value = stock
  const existing = alerts.value[stock.code]
  alertForm.value = {
    take_profit: existing?.take_profit || '',
    stop_loss: existing?.stop_loss || '',
    change_alert: existing?.change_alert || '',
    enabled: existing?.enabled ?? true,
  }
  showAlertModal.value = true
}

const closeAlertModal = () => {
  showAlertModal.value = false
  currentAlertStock.value = null
}

const saveAlert = async () => {
  if (!currentAlertStock.value) return
  await setAlert(currentAlertStock.value.code, alertForm.value)
  alerts.value[currentAlertStock.value.code] = { ...alertForm.value }
  closeAlertModal()
}

const dismissAlert = (index: number) => {
  alertNotifications.value.splice(index, 1)
}

// 更新托盘（文字提示）
const updateTray = () => {
  if (stockData.value.length > 0) {
    const summary = stockData.value.slice(0, 3).map(s => `${s.name}: ${s.price} (${s.change_percent}%)`).join('\n')
    ;(window as any).ipcRenderer?.send('update-tray', summary)
  }
}

// 更新托盘图标（显示重点关注股票的涨跌幅）
const updateTrayIcon = (focusedData: any) => {
  if (focusedData) {
    ;(window as any).ipcRenderer?.send('update-tray-icon', {
      change: focusedData.change_percent,
      price: focusedData.price,
      name: focusedData.name
    })
  }
}

// 设置重点关注
const handleSetFocus = async (code: string) => {
  await setFocusedStock(code)
  focusedStock.value = code
  // 立即更新托盘图标
  const stock = stockData.value.find(s => s.code === code)
  if (stock) {
    updateTrayIcon(stock)
  }
}

// 点击行打开详情
const handleRowClick = (code: string, event: MouseEvent) => {
  // 避免点击按钮时触发
  if ((event.target as HTMLElement).closest('button')) return
  emit('openDetail', code)
}

// 获取数据
const fetchData = async () => {
  try {
    const res = await getStocks()
    // 按照 stocks 顺序排列 data
    const orderedData = res.stocks.map((code: string) => res.data[code]).filter(Boolean)
    stockData.value = orderedData
    alerts.value = res.alerts || {}
    focusedStock.value = res.focused_stock || (res.stocks.length > 0 ? res.stocks[0] : null)
    
    updateTray()
    // 更新托盘图标
    if (res.focused_data) {
      updateTrayIcon(res.focused_data)
    }
  } catch (error) {
    console.error("获取数据失败:", error)
  }
}

// 检查预警
const checkAlerts = async () => {
  try {
    const res = await getTriggeredAlerts()
    if (res.alerts?.length > 0) {
      alertNotifications.value.push(...res.alerts)
      
      // 发送系统通知
      for (const alert of res.alerts) {
        const title = `📈 ${alert.name} 预警触发`
        const body = alert.messages.join('\n') + `\n当前价: ${alert.price}`
        ;(window as any).ipcRenderer?.showNotification(title, body)
      }
    }
  } catch (e) {
    console.error("检查预警失败:", e)
  }
}

const handleAddStock = async () => {
  if (!newStockCode.value) return
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await addStock(newStockCode.value)
    if (res.status === 'error') {
      errorMsg.value = res.message
    } else {
      newStockCode.value = ''
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
  fetchData()
}

const loadSettingsAndStart = async () => {
  try {
    const res = await getSettings()
    if (res.status === 'success' && res.settings?.refresh_interval) {
      refreshInterval.value = res.settings.refresh_interval
    }
  } catch (e) {
    console.error('加载设置失败:', e)
  }
  
  fetchData()
  intervalId = setInterval(fetchData, refreshInterval.value * 1000)
  alertCheckId = setInterval(checkAlerts, 3000)
}

onMounted(() => { loadSettingsAndStart() })
onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
  if (alertCheckId) clearInterval(alertCheckId)
})
</script>
