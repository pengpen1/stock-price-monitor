<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4">
    <div class="max-w-7xl mx-auto">
      <!-- 顶部信息栏 -->
      <div class="bg-white rounded-xl shadow-sm p-4 mb-4">
        <div class="flex items-center justify-between">
          <!-- 左侧：股票信息 -->
          <div class="flex items-center gap-4">
            <button @click="handleBack" class="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg">
              ← 返回
            </button>
            <div>
              <div class="flex items-center gap-2">
                <h1 class="text-xl font-bold text-slate-800">{{ session?.stock_name }}</h1>
                <span class="px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-600 rounded">实盘模拟</span>
              </div>
              <span class="text-sm text-slate-500">{{ session?.stock_code }}</span>
            </div>
          </div>
          
          <!-- 中间：进度 -->
          <div class="flex-1 max-w-md mx-8">
            <div class="flex items-center justify-between text-sm text-slate-600 mb-1">
              <span>第 {{ (session?.current_day || 0) + 1 }} / {{ session?.total_days }} 天</span>
              <span>{{ currentDate }}</span>
            </div>
            <div class="h-2 bg-slate-200 rounded-full overflow-hidden">
              <div class="h-full bg-blue-500 transition-all duration-300" 
                :style="{ width: progressPercent + '%' }"></div>
            </div>
          </div>
          
          <!-- 右侧：操作按钮 -->
          <div class="flex items-center gap-2">
            <button @click="handlePause" v-if="session?.status === 'running'"
              class="px-3 py-1.5 text-sm text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200">
              暂停
            </button>
            <button @click="handleAbandon"
              class="px-3 py-1.5 text-sm text-red-600 bg-red-50 rounded-lg hover:bg-red-100">
              退出
            </button>
          </div>
        </div>
      </div>
      
      <!-- 主体内容 -->
      <div class="grid grid-cols-12 gap-4">
        <!-- 左侧：K线图 -->
        <div class="col-span-8 bg-white rounded-xl shadow-sm p-4">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-semibold text-slate-700">日K线图</h3>
            <div class="flex items-center gap-2 text-xs text-slate-500">
              <span class="flex items-center gap-1">
                <span class="w-3 h-0.5 bg-orange-500"></span> MA5
              </span>
              <span class="flex items-center gap-1">
                <span class="w-3 h-0.5 bg-blue-500"></span> MA10
              </span>
              <span class="flex items-center gap-1">
                <span class="w-3 h-0.5 bg-purple-500"></span> MA20
              </span>
            </div>
          </div>
          <div style="height: 400px;">
            <v-chart v-if="klineOption" :option="klineOption" autoresize class="w-full h-full" />
            <div v-else class="flex items-center justify-center h-full text-slate-400">
              加载中...
            </div>
          </div>
        </div>
        
        <!-- 右侧：账户信息和操作 -->
        <div class="col-span-4 space-y-4">
          <!-- 账户信息 -->
          <div class="bg-white rounded-xl shadow-sm p-4">
            <h3 class="text-sm font-semibold text-slate-700 mb-3">账户信息</h3>
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-slate-500">可用资金</span>
                <span class="font-medium text-slate-800">¥{{ formatMoney(session?.current_capital || 0) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-500">持仓数量</span>
                <span class="font-medium text-slate-800">{{ session?.position || 0 }} 股</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-500">持仓成本</span>
                <span class="font-medium text-slate-800">¥{{ (session?.cost_price || 0).toFixed(2) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-500">持仓市值</span>
                <span class="font-medium" :class="positionProfitClass">
                  ¥{{ formatMoney(positionValue) }}
                </span>
              </div>
              <hr class="border-slate-100">
              <div class="flex justify-between">
                <span class="text-slate-500">总资产</span>
                <span class="font-semibold text-lg" :class="totalProfitClass">
                  ¥{{ formatMoney(totalAssets) }}
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-500">总收益</span>
                <span class="font-medium" :class="totalProfitClass">
                  {{ totalProfitRate >= 0 ? '+' : '' }}{{ totalProfitRate.toFixed(2) }}%
                </span>
              </div>
            </div>
          </div>
          
          <!-- 当日行情 -->
          <div class="bg-white rounded-xl shadow-sm p-4">
            <h3 class="text-sm font-semibold text-slate-700 mb-3">当日行情</h3>
            <div class="grid grid-cols-2 gap-3 text-sm">
              <div>
                <span class="text-slate-500">开盘</span>
                <div class="font-medium">{{ currentDayData?.open?.toFixed(2) || '--' }}</div>
              </div>
              <div>
                <span class="text-slate-500">收盘</span>
                <div class="font-medium" :class="dayChangeClass">{{ currentDayData?.close?.toFixed(2) || '--' }}</div>
              </div>
              <div>
                <span class="text-slate-500">最高</span>
                <div class="font-medium text-red-500">{{ currentDayData?.high?.toFixed(2) || '--' }}</div>
              </div>
              <div>
                <span class="text-slate-500">最低</span>
                <div class="font-medium text-green-500">{{ currentDayData?.low?.toFixed(2) || '--' }}</div>
              </div>
            </div>
            <button @click="showMinuteModal = true" 
              class="w-full mt-3 px-3 py-2 text-sm text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100">
              查看分时图
            </button>
          </div>
          
          <!-- 交易操作 -->
          <div class="bg-white rounded-xl shadow-sm p-4">
            <h3 class="text-sm font-semibold text-slate-700 mb-3">交易操作</h3>
            
            <!-- 先选择操作类型 -->
            <div class="mb-3">
              <label class="block text-xs text-slate-500 mb-1">操作类型</label>
              <div class="grid grid-cols-3 gap-2">
                <button @click="selectedTradeType = 'buy'"
                  :class="selectedTradeType === 'buy' ? 'bg-red-500 text-white' : 'bg-red-50 text-red-600'"
                  class="px-3 py-2 text-sm font-medium rounded-lg transition-colors">
                  买入
                </button>
                <button @click="selectedTradeType = 'sell'"
                  :class="selectedTradeType === 'sell' ? 'bg-green-500 text-white' : 'bg-green-50 text-green-600'"
                  class="px-3 py-2 text-sm font-medium rounded-lg transition-colors">
                  卖出
                </button>
                <button @click="selectedTradeType = 'skip'"
                  :class="selectedTradeType === 'skip' ? 'bg-slate-500 text-white' : 'bg-slate-100 text-slate-600'"
                  class="px-3 py-2 text-sm font-medium rounded-lg transition-colors">
                  跳过
                </button>
              </div>
            </div>
            
            <!-- 交易数量（买入/卖出时显示） -->
            <div v-show="selectedTradeType !== 'skip'" class="mb-3">
              <label class="block text-xs text-slate-500 mb-1">
                交易数量（股）
                <span class="text-slate-400">
                  - 可{{ selectedTradeType === 'buy' ? '买' : '卖' }}: {{ maxTradeQuantity }}股
                </span>
              </label>
              <div class="flex gap-2">
                <input type="number" v-model.number="tradeQuantity" :step="100" min="100" :max="maxTradeQuantity"
                  class="flex-1 px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-blue-400">
                <button @click="setMaxQuantity" class="px-2 py-1 text-xs text-blue-600 bg-blue-50 rounded hover:bg-blue-100">
                  全部
                </button>
                <button @click="setHalfQuantity" class="px-2 py-1 text-xs text-blue-600 bg-blue-50 rounded hover:bg-blue-100">
                  一半
                </button>
              </div>
            </div>
            
            <!-- 交易理由（买入/卖出时显示） -->
            <div v-show="selectedTradeType !== 'skip'" class="mb-4">
              <label class="block text-xs text-slate-500 mb-1">操作理由</label>
              <textarea v-model="tradeReason" rows="2" placeholder="请输入操作理由..."
                class="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-blue-400 resize-none"></textarea>
            </div>
            
            <!-- 确认按钮 -->
            <button @click="executeTrade(selectedTradeType)" :disabled="!canExecuteTrade || trading"
              :class="confirmButtonClass"
              class="w-full px-3 py-2.5 text-sm font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              {{ trading ? '处理中...' : confirmButtonText }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- 交易记录 -->
      <div class="mt-4 bg-white rounded-xl shadow-sm p-4">
        <h3 class="text-sm font-semibold text-slate-700 mb-3">交易记录</h3>
        <div v-if="session?.trades?.length" class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-left text-slate-500 border-b border-slate-100">
                <th class="pb-2 font-medium">日期</th>
                <th class="pb-2 font-medium">操作</th>
                <th class="pb-2 font-medium">价格</th>
                <th class="pb-2 font-medium">数量</th>
                <th class="pb-2 font-medium">理由</th>
                <th class="pb-2 font-medium">剩余资金</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="trade in session.trades" :key="trade.day" class="border-b border-slate-50">
                <td class="py-2">{{ trade.date }}</td>
                <td class="py-2">
                  <span :class="tradeTypeClass(trade.type)" class="px-2 py-0.5 text-xs font-medium rounded">
                    {{ tradeTypeText(trade.type) }}
                  </span>
                </td>
                <td class="py-2">{{ trade.type !== 'skip' ? '¥' + trade.price.toFixed(2) : '-' }}</td>
                <td class="py-2">{{ trade.type !== 'skip' ? trade.quantity + '股' : '-' }}</td>
                <td class="py-2 max-w-xs truncate" :title="trade.reason">{{ trade.reason || '-' }}</td>
                <td class="py-2">¥{{ formatMoney(trade.capital_after) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center text-slate-400 py-4">
          暂无交易记录
        </div>
      </div>
    </div>
    
    <!-- 分时图弹窗 -->
    <SimulationMinuteModal v-model:visible="showMinuteModal" 
      :session-id="sessionId" :date="currentDate" :stock-name="session?.stock_name || ''" />
    
    <!-- 结算弹窗 -->
    <SimulationResultModal v-model:visible="showResultModal" 
      :session="session" :kline-data="klineData" @close="handleResultClose" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { CandlestickChart, BarChart, LineChart, ScatterChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, DataZoomComponent, MarkPointComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getSimulationSession, getSimulationKline, executeSimulationTrade, pauseSimulation, abandonSimulation } from '../api'
import type { SimulationSession } from '../api'
import SimulationMinuteModal from './SimulationMinuteModal.vue'
import SimulationResultModal from './SimulationResultModal.vue'

use([CanvasRenderer, CandlestickChart, BarChart, LineChart, ScatterChart, GridComponent, TooltipComponent, DataZoomComponent, MarkPointComponent])

const props = defineProps<{
  sessionId: string
}>()

const emit = defineEmits(['back', 'complete'])

const session = ref<SimulationSession | null>(null)
const klineData = ref<any[]>([])
const currentDayData = ref<any>(null)
const loading = ref(true)
const trading = ref(false)

const tradeQuantity = ref(100)
const tradeReason = ref('')

const showMinuteModal = ref(false)
const showResultModal = ref(false)

// 计算属性
const progressPercent = computed(() => {
  if (!session.value) return 0
  return ((session.value.current_day) / session.value.total_days) * 100
})

const currentDate = computed(() => currentDayData.value?.date || '')

const currentPrice = computed(() => currentDayData.value?.close || 0)

const positionValue = computed(() => {
  if (!session.value) return 0
  return session.value.position * currentPrice.value
})

const totalAssets = computed(() => {
  if (!session.value) return 0
  return session.value.current_capital + positionValue.value
})

const totalProfitRate = computed(() => {
  if (!session.value) return 0
  return ((totalAssets.value - session.value.initial_capital) / session.value.initial_capital) * 100
})

const positionProfitClass = computed(() => {
  if (!session.value || session.value.position === 0) return 'text-slate-800'
  const profit = currentPrice.value - session.value.cost_price
  return profit >= 0 ? 'text-red-500' : 'text-green-500'
})

const totalProfitClass = computed(() => {
  return totalProfitRate.value >= 0 ? 'text-red-500' : 'text-green-500'
})

const dayChangeClass = computed(() => {
  if (!currentDayData.value) return ''
  return currentDayData.value.close >= currentDayData.value.open ? 'text-red-500' : 'text-green-500'
})

// 当前选择的操作类型
const selectedTradeType = ref<'buy' | 'sell' | 'skip'>('skip')

// 根据操作类型计算最大可交易数量
const maxTradeQuantity = computed(() => {
  if (!session.value || !currentDayData.value) return 0
  if (selectedTradeType.value === 'buy') {
    // 买入：根据可用资金计算
    return Math.floor(session.value.current_capital / currentDayData.value.close / 100) * 100
  } else if (selectedTradeType.value === 'sell') {
    // 卖出：根据持仓计算
    return session.value.position
  }
  return 0
})

// 是否可以执行交易
const canExecuteTrade = computed(() => {
  if (selectedTradeType.value === 'skip') return true
  if (!session.value || !currentDayData.value) return false
  
  if (selectedTradeType.value === 'buy') {
    const cost = currentDayData.value.close * tradeQuantity.value
    return cost <= session.value.current_capital && tradeQuantity.value >= 100
  } else if (selectedTradeType.value === 'sell') {
    return session.value.position >= tradeQuantity.value && tradeQuantity.value >= 100
  }
  return false
})

// 确认按钮样式
const confirmButtonClass = computed(() => {
  switch (selectedTradeType.value) {
    case 'buy': return 'bg-red-500 text-white hover:bg-red-600'
    case 'sell': return 'bg-green-500 text-white hover:bg-green-600'
    default: return 'bg-slate-500 text-white hover:bg-slate-600'
  }
})

// 确认按钮文字
const confirmButtonText = computed(() => {
  switch (selectedTradeType.value) {
    case 'buy': return `确认买入 ${tradeQuantity.value} 股`
    case 'sell': return `确认卖出 ${tradeQuantity.value} 股`
    default: return '确认跳过'
  }
})

const canBuy = computed(() => {
  if (!session.value || !currentDayData.value) return false
  const cost = currentDayData.value.close * tradeQuantity.value
  return cost <= session.value.current_capital && tradeQuantity.value >= 100
})

const canSell = computed(() => {
  if (!session.value) return false
  return session.value.position >= tradeQuantity.value && tradeQuantity.value >= 100
})

// 方法
const formatMoney = (val: number) => {
  return val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const tradeTypeClass = (type: string) => {
  switch (type) {
    case 'buy': return 'bg-red-100 text-red-600'
    case 'sell': return 'bg-green-100 text-green-600'
    default: return 'bg-slate-100 text-slate-600'
  }
}

const tradeTypeText = (type: string) => {
  switch (type) {
    case 'buy': return '买入'
    case 'sell': return '卖出'
    default: return '跳过'
  }
}

// 设置最大数量
const setMaxQuantity = () => {
  tradeQuantity.value = maxTradeQuantity.value
}

// 设置一半数量
const setHalfQuantity = () => {
  tradeQuantity.value = Math.floor(maxTradeQuantity.value / 2 / 100) * 100
}

const setMaxBuy = () => {
  if (!session.value || !currentDayData.value) return
  const maxShares = Math.floor(session.value.current_capital / currentDayData.value.close / 100) * 100
  tradeQuantity.value = maxShares
}

const setHalfBuy = () => {
  if (!session.value || !currentDayData.value) return
  const halfShares = Math.floor(session.value.current_capital / 2 / currentDayData.value.close / 100) * 100
  tradeQuantity.value = halfShares
}

const loadData = async () => {
  loading.value = true
  try {
    // 获取K线数据
    const klineRes = await getSimulationKline(props.sessionId)
    if (klineRes.status === 'success') {
      klineData.value = klineRes.kline || []
      currentDayData.value = klineRes.current_day
      session.value = klineRes.session
      
      // 检查是否已完成
      if (session.value?.status === 'completed') {
        showResultModal.value = true
      }
    }
  } catch (e) {
    console.error('加载数据失败:', e)
  } finally {
    loading.value = false
  }
}

const executeTrade = async (type: 'buy' | 'sell' | 'skip') => {
  if (!session.value || !currentDayData.value) return
  
  // 验证
  if (type === 'buy' && !canBuy.value) {
    alert('资金不足或数量无效')
    return
  }
  if (type === 'sell' && !canSell.value) {
    alert('持仓不足或数量无效')
    return
  }
  if ((type === 'buy' || type === 'sell') && !tradeReason.value.trim()) {
    alert('请输入操作理由')
    return
  }
  
  trading.value = true
  try {
    const res = await executeSimulationTrade({
      session_id: props.sessionId,
      trade_type: type,
      price: currentDayData.value.close,
      quantity: type === 'skip' ? 0 : tradeQuantity.value,
      reason: tradeReason.value.trim() || (type === 'skip' ? '观望' : ''),
      current_date: currentDayData.value.date
    })
    
    if (res.status === 'success') {
      session.value = res.session
      tradeReason.value = ''
      
      // 检查是否完成
      if (res.session.status === 'completed') {
        showResultModal.value = true
      } else {
        // 加载下一天数据
        await loadData()
      }
    } else {
      alert(res.message || '操作失败')
    }
  } catch (e: any) {
    alert(e.message || '操作失败')
  } finally {
    trading.value = false
  }
}

const handlePause = async () => {
  if (!confirm('确定要暂停模拟吗？您可以稍后继续。')) return
  
  try {
    const res = await pauseSimulation(props.sessionId)
    if (res.status === 'success') {
      emit('back')
    }
  } catch (e) {
    console.error('暂停失败:', e)
  }
}

const handleAbandon = async () => {
  if (!confirm('确定要退出模拟吗？当前进度将被保存，您可以查看结算结果。')) return
  
  try {
    const res = await abandonSimulation(props.sessionId)
    if (res.status === 'success') {
      showResultModal.value = true
    }
  } catch (e) {
    console.error('退出失败:', e)
  }
}

const handleBack = () => {
  if (session.value?.status === 'running') {
    handlePause()
  } else {
    emit('back')
  }
}

const handleResultClose = () => {
  showResultModal.value = false
  emit('complete')
}

// K线图配置
const klineOption = computed(() => {
  if (!klineData.value.length) return null
  
  const dates = klineData.value.map(d => d.date?.substring(5) || '')
  const ohlc = klineData.value.map(d => [d.open, d.close, d.low, d.high])
  const volumes = klineData.value.map(d => ({
    value: d.volume,
    itemStyle: { color: d.close >= d.open ? 'rgba(255,77,79,0.7)' : 'rgba(82,196,26,0.7)' }
  }))
  
  // 计算均线
  const calcMA = (period: number) => {
    const result: (number | null)[] = []
    for (let i = 0; i < klineData.value.length; i++) {
      if (i < period - 1) {
        result.push(null)
      } else {
        let sum = 0
        for (let j = 0; j < period; j++) {
          sum += klineData.value[i - j].close
        }
        result.push(sum / period)
      }
    }
    return result
  }
  
  // 交易标记点
  const tradeMarks = (session.value?.trades || []).map(trade => {
    const idx = klineData.value.findIndex(k => k.date === trade.date)
    if (idx === -1) return null
    const k = klineData.value[idx]
    return {
      value: [dates[idx], trade.type === 'buy' ? k.low * 0.99 : k.high * 1.01],
      symbol: trade.type === 'buy' ? 'triangle' : (trade.type === 'sell' ? 'triangle' : 'circle'),
      symbolRotate: trade.type === 'sell' ? 180 : 0,
      symbolSize: trade.type === 'skip' ? 8 : 16,
      itemStyle: { 
        color: trade.type === 'buy' ? '#ef4444' : (trade.type === 'sell' ? '#22c55e' : '#94a3b8')
      },
      label: {
        show: trade.type !== 'skip',
        formatter: trade.type === 'buy' ? 'B' : 'S',
        color: '#fff',
        fontSize: 10
      }
    }
  }).filter(Boolean)
  
  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    grid: [
      { left: 50, right: 50, top: 30, height: '55%' },
      { left: 50, right: 50, top: '72%', height: '18%' }
    ],
    xAxis: [
      { type: 'category', data: dates, gridIndex: 0, axisLabel: { show: false } },
      { type: 'category', data: dates, gridIndex: 1, axisLabel: { fontSize: 10 } }
    ],
    yAxis: [
      { type: 'value', scale: true, gridIndex: 0, position: 'right', axisLabel: { fontSize: 10 } },
      { type: 'value', scale: true, gridIndex: 1, axisLabel: { show: false } }
    ],
    dataZoom: [{ type: 'inside', xAxisIndex: [0, 1], start: 50, end: 100 }],
    series: [
      { name: 'K线', type: 'candlestick', data: ohlc, itemStyle: { color: '#ff4d4f', color0: '#52c41a', borderColor: '#ff4d4f', borderColor0: '#52c41a' } },
      { name: 'MA5', type: 'line', data: calcMA(5), smooth: true, symbol: 'none', lineStyle: { color: '#ff9800', width: 1 } },
      { name: 'MA10', type: 'line', data: calcMA(10), smooth: true, symbol: 'none', lineStyle: { color: '#2196f3', width: 1 } },
      { name: 'MA20', type: 'line', data: calcMA(20), smooth: true, symbol: 'none', lineStyle: { color: '#9c27b0', width: 1 } },
      { name: '成交量', type: 'bar', data: volumes, xAxisIndex: 1, yAxisIndex: 1 },
      { name: '交易', type: 'scatter', data: tradeMarks, xAxisIndex: 0, yAxisIndex: 0 }
    ]
  }
})

onMounted(() => {
  loadData()
})
</script>
