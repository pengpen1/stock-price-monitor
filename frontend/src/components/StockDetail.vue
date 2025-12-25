<!--
  StockDetail.vue
  股票详情页面组件
  包含分时图、K线图、资金流向、AI分析等功能
-->
<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
    <div class="max-w-6xl mx-auto">
      <!-- 头部 -->
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-4">
          <button @click="$emit('back')" class="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg">
            ← {{ $t('common.back') }}
          </button>
          <div>
            <h1 class="text-2xl font-bold text-slate-800">{{ stockInfo.name || code }}</h1>
            <span class="text-sm text-slate-500">{{ code }}</span>
          </div>
        </div>
        <div class="text-right">
          <div class="flex items-center gap-2 mb-1 justify-end">
            <!-- 实盘模拟下拉菜单 -->
            <div class="relative" ref="simMenuRef">
              <button @click="showSimMenu = !showSimMenu"
                class="px-3 py-1.5 text-xs font-medium bg-blue-50 text-blue-600 border border-blue-200 rounded-md hover:bg-blue-100 hover:border-blue-300 transition-all flex items-center gap-1 whitespace-nowrap">
                实盘模拟
                <span class="text-[10px]">▼</span>
              </button>
              <div v-if="showSimMenu" class="absolute right-0 top-full mt-1 bg-white rounded-lg shadow-lg border border-slate-200 py-1 z-20 min-w-[130px]">
                <button @click="openSimulationConfig" class="w-full px-3 py-2 text-left text-sm text-blue-600 hover:bg-blue-50 whitespace-nowrap">
                  + 新建模拟
                </button>
                <button @click="openSimulationList" class="w-full px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-50 whitespace-nowrap">
                  模拟记录
                </button>
              </div>
            </div>
            <!-- 复盘记录下拉菜单 -->
            <div class="relative" ref="recordMenuRef">
              <button @click="showRecordMenu = !showRecordMenu"
                class="px-3 py-1.5 text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200 rounded-md hover:bg-slate-200 hover:border-slate-300 transition-all flex items-center gap-1 whitespace-nowrap">
                复盘记录
                <span class="text-[10px]">▼</span>
              </button>
              <div v-if="showRecordMenu" class="absolute right-0 top-full mt-1 bg-white rounded-lg shadow-lg border border-slate-200 py-1 z-20 min-w-[130px]">
                <button @click="openTradeRecords" class="w-full px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-50 whitespace-nowrap">
                  交易记录
                </button>
                <button @click="openAIRecords" class="w-full px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-50 whitespace-nowrap">
                  AI分析历史
                </button>
                <hr class="my-1 border-slate-100">
                <button @click="openAddTradeRecord" class="w-full px-3 py-2 text-left text-sm text-blue-600 hover:bg-blue-50 whitespace-nowrap">
                  + 添加交易
                </button>
              </div>
            </div>
            <button @click="openAIModal('fast')"
              class="px-3 py-1.5 text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200 rounded-md hover:bg-slate-200 hover:border-slate-300 transition-all">
              快速分析
            </button>
            <button @click="openAIModal('precise')"
              class="px-3 py-1.5 text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200 rounded-md hover:bg-slate-200 hover:border-slate-300 transition-all">
              精准分析
            </button>
          </div>
          <div class="text-3xl font-bold" :class="priceClass">{{ stockInfo.price || '--' }}</div>
          <div class="text-sm" :class="priceClass">
            {{ changeSign }}{{ stockInfo.change_percent || '0.00' }}%
          </div>
        </div>
      </div>

      <!-- 基本信息卡片 -->
      <StockInfoCards :stock-info="stockInfo" :limit-up-price="limitUpPrice" :limit-down-price="limitDownPrice" />

      <!-- 图表区域 -->
      <div class="bg-white rounded-xl shadow-sm mb-6">
        <div class="flex border-b border-slate-100">
          <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
            :class="activeTab === tab.key ? 'text-blue-500 border-b-2 border-blue-500' : 'text-slate-500'"
            class="px-6 py-3 text-sm font-medium transition-colors">
            {{ $t(`detail.${tab.key}`) }}
          </button>
        </div>
        <div class="p-4" style="height: 480px;">
          <div v-if="loading" class="flex items-center justify-center h-full text-slate-400">
            {{ $t('common.loading') }}
          </div>
          <v-chart v-else-if="chartOption" :option="chartOption" autoresize class="w-full h-full"
            @datazoom="handleDataZoom" />
        </div>
      </div>

      <!-- 资金流向 -->
      <MoneyFlowCard :money-flow-data="moneyFlowData" />
    </div>

    <!-- 弹窗组件 -->
    <AIAnalysisModal v-model:visible="showAiModal" :stock-code="code" :type="aiType" />
    <TradeRecordList v-model:visible="showTradeRecordList" :stock-code="code" @openJournal="$emit('openJournal')" />
    <TradeRecordModal v-model:visible="showAddTradeRecord" :stock-code="code" @saved="onTradeRecordSaved" />
    <AIRecordList v-model:visible="showAIRecordList" :stock-code="code" />
    <SimulationConfigModal v-model:visible="showSimConfigModal" 
      :stock-code="code" 
      :stock-name="stockInfo.name || code"
      :current-price="stockInfo.price || '0'"
      :price-change="parseFloat(stockInfo.change_percent || '0')"
      @start="onSimulationStart" />
    <SimulationListModal v-model:visible="showSimListModal" 
      :stock-code="code"
      @resume="onSimulationResume"
      @view="onSimulationView" />
  </div>
</template>

<script setup lang="ts">
/**
 * 股票详情组件逻辑
 * 数据加载、图表渲染、弹窗控制
 */
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, CandlestickChart, BarChart, ScatterChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, DataZoomComponent, MarkLineComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getStockDetail, getKlineData, getStockTradeRecords, type TradeRecord, type SimulationSession } from '@/api'
import { useStockChart } from '@/composables/useStockChart'
import AIAnalysisModal from './AIAnalysisModal.vue'
import TradeRecordList from './TradeRecordList.vue'
import TradeRecordModal from './TradeRecordModal.vue'
import AIRecordList from './AIRecordList.vue'
import SimulationConfigModal from './SimulationConfigModal.vue'
import SimulationListModal from './SimulationListModal.vue'
import StockInfoCards from './detail/StockInfoCards.vue'
import MoneyFlowCard from './detail/MoneyFlowCard.vue'

// 注册 ECharts 组件
use([CanvasRenderer, LineChart, CandlestickChart, BarChart, ScatterChart, GridComponent, TooltipComponent, DataZoomComponent, MarkLineComponent, LegendComponent])

const props = defineProps<{ code: string }>()
const emit = defineEmits(['back', 'startSimulation', 'viewSimulation', 'openJournal'])

// ========== 数据状态 ==========
const loading = ref(true)
const stockInfo = ref<any>({})
const minuteData = ref<any[]>([])
const klineData = ref<any[]>([])
const moneyFlowData = ref<any[]>([])
const activeTab = ref('minute')
const tradeRecords = ref<TradeRecord[]>([])

// ========== 图表 Composable ==========
const { 
  getMinuteChartOption, 
  getKlineChartOption, 
  handleDataZoom, 
  resetZoomState,
  markFirstLoadDone 
} = useStockChart(minuteData, klineData, stockInfo, tradeRecords)

// ========== 弹窗状态 ==========
const showAiModal = ref(false)
const aiType = ref<'fast' | 'precise'>('fast')
const showRecordMenu = ref(false)
const recordMenuRef = ref<HTMLElement | null>(null)
const showTradeRecordList = ref(false)
const showAddTradeRecord = ref(false)
const showAIRecordList = ref(false)
const showSimMenu = ref(false)
const simMenuRef = ref<HTMLElement | null>(null)
const showSimConfigModal = ref(false)
const showSimListModal = ref(false)

// ========== 计算属性 ==========
const tabs = [
  { key: 'minute' },
  { key: 'day' },
  { key: 'week' },
  { key: 'month' },
]

const limitUpPrice = computed(() => {
  const preClose = parseFloat(stockInfo.value.pre_close || '0')
  if (preClose <= 0) return '--'
  const code = props.code
  let limitRate = 0.1
  if (code.startsWith('sh688') || code.startsWith('sz300') || code.startsWith('688') || code.startsWith('300')) {
    limitRate = 0.2
  }
  return (preClose * (1 + limitRate)).toFixed(2)
})

const limitDownPrice = computed(() => {
  const preClose = parseFloat(stockInfo.value.pre_close || '0')
  if (preClose <= 0) return '--'
  const code = props.code
  let limitRate = 0.1
  if (code.startsWith('sh688') || code.startsWith('sz300') || code.startsWith('688') || code.startsWith('300')) {
    limitRate = 0.2
  }
  return (preClose * (1 - limitRate)).toFixed(2)
})

const priceClass = computed(() => {
  const change = parseFloat(stockInfo.value.change_percent || '0')
  return change >= 0 ? 'text-red-500' : 'text-green-500'
})

const changeSign = computed(() => {
  const change = parseFloat(stockInfo.value.change_percent || '0')
  return change >= 0 ? '+' : ''
})

const chartOption = computed(() => {
  return activeTab.value === 'minute' ? getMinuteChartOption() : getKlineChartOption()
})

// ========== 方法 ==========
const openAIModal = (type: 'fast' | 'precise') => {
  aiType.value = type
  showAiModal.value = true
}

const openSimulationConfig = () => {
  showSimMenu.value = false
  showSimConfigModal.value = true
}

const openSimulationList = () => {
  showSimMenu.value = false
  showSimListModal.value = true
}

const onSimulationStart = (session: SimulationSession) => emit('startSimulation', session)
const onSimulationResume = (session: SimulationSession) => emit('startSimulation', session)
const onSimulationView = (session: SimulationSession) => emit('viewSimulation', session)

const openTradeRecords = () => {
  showRecordMenu.value = false
  showTradeRecordList.value = true
}

const openAIRecords = () => {
  showRecordMenu.value = false
  showAIRecordList.value = true
}

const openAddTradeRecord = () => {
  showRecordMenu.value = false
  showAddTradeRecord.value = true
}

const onTradeRecordSaved = () => loadTradeRecords()

const loadTradeRecords = async () => {
  try {
    const res = await getStockTradeRecords(props.code)
    if (res.status === 'success') {
      tradeRecords.value = res.records || []
    }
  } catch (e) {
    console.error('加载交易记录失败:', e)
  }
}

const handleClickOutside = (e: MouseEvent) => {
  if (recordMenuRef.value && !recordMenuRef.value.contains(e.target as Node)) {
    showRecordMenu.value = false
  }
  if (simMenuRef.value && !simMenuRef.value.contains(e.target as Node)) {
    showSimMenu.value = false
  }
}

// ========== 数据加载 ==========
let refreshTimer: ReturnType<typeof setInterval> | null = null
const REFRESH_INTERVAL = 5000

const loadData = async (showLoading = true) => {
  if (showLoading) loading.value = true
  try {
    const res = await getStockDetail(props.code)
    if (res.status === 'success') {
      stockInfo.value = res.basic || {}
      minuteData.value = res.minute || []
      klineData.value = res.kline || []
      moneyFlowData.value = res.money_flow || []
      markFirstLoadDone()
    }
  } catch (e) {
    console.error('加载数据失败:', e)
  } finally {
    loading.value = false
  }
}

const loadKlineData = async (period: string) => {
  if (period === 'minute') return
  loading.value = true
  try {
    const res = await getKlineData(props.code, period, 120)
    if (res.status === 'success') {
      klineData.value = res.data || []
    }
  } catch (e) {
    console.error('加载K线数据失败:', e)
  } finally {
    loading.value = false
  }
}

const startRefresh = () => {
  stopRefresh()
  refreshTimer = setInterval(() => {
    if (activeTab.value === 'minute') {
      loadData(false)
    }
  }, REFRESH_INTERVAL)
}

const stopRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// ========== 生命周期 ==========
watch(activeTab, (newTab) => {
  resetZoomState()
  if (newTab !== 'minute') {
    loadKlineData(newTab)
  }
})

watch(() => props.code, () => loadData())

onMounted(() => {
  loadData()
  loadTradeRecords()
  startRefresh()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  stopRefresh()
  document.removeEventListener('click', handleClickOutside)
})
</script>
