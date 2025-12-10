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
          <div class="text-3xl font-bold" :class="priceClass">{{ stockInfo.price || '--' }}</div>
          <div class="text-sm" :class="priceClass">
            {{ changeSign }}{{ stockInfo.change_percent || '0.00' }}%
          </div>
        </div>
      </div>

      <!-- 基本信息卡片 -->
      <div class="grid grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-xl p-4 shadow-sm">
          <div class="text-xs text-slate-500">{{ $t('detail.open') }}</div>
          <div class="text-lg font-semibold text-slate-800">{{ stockInfo.open || '--' }}</div>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-sm">
          <div class="text-xs text-slate-500">{{ $t('detail.pre_close') }}</div>
          <div class="text-lg font-semibold text-slate-800">{{ stockInfo.pre_close || '--' }}</div>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-sm">
          <div class="text-xs text-slate-500">{{ $t('detail.high') }}</div>
          <div class="text-lg font-semibold text-red-500">{{ stockInfo.high || '--' }}</div>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-sm">
          <div class="text-xs text-slate-500">{{ $t('detail.low') }}</div>
          <div class="text-lg font-semibold text-green-500">{{ stockInfo.low || '--' }}</div>
        </div>
      </div>

      <!-- 图表切换 -->
      <div class="bg-white rounded-xl shadow-sm mb-6">
        <div class="flex border-b border-slate-100">
          <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
            :class="activeTab === tab.key ? 'text-blue-500 border-b-2 border-blue-500' : 'text-slate-500'"
            class="px-6 py-3 text-sm font-medium transition-colors">
            {{ $t(`detail.${tab.key}`) }}
          </button>
        </div>
        
        <!-- 图表容器 -->
        <div class="p-4" style="height: 450px;">
          <div v-if="loading" class="flex items-center justify-center h-full text-slate-400">
            {{ $t('common.loading') }}
          </div>
          <v-chart v-else-if="chartOption" :option="chartOption" autoresize class="w-full h-full" />
        </div>
      </div>

      <!-- 资金流向 -->
      <div v-if="moneyFlowData.length > 0" class="bg-white rounded-xl shadow-sm p-4">
        <h3 class="text-sm font-semibold text-slate-700 mb-4">{{ $t('detail.money_flow') }}</h3>
        <div class="grid grid-cols-3 gap-4">
          <div class="text-center">
            <div class="text-xs text-slate-500">{{ $t('detail.main_net_flow') }}</div>
            <div class="text-lg font-semibold" :class="mainNetFlow >= 0 ? 'text-red-500' : 'text-green-500'">
              {{ formatMoney(mainNetFlow) }}
            </div>
          </div>
          <div class="text-center">
            <div class="text-xs text-slate-500">{{ $t('detail.big_net_flow') }}</div>
            <div class="text-lg font-semibold" :class="bigNetFlow >= 0 ? 'text-red-500' : 'text-green-500'">
              {{ formatMoney(bigNetFlow) }}
            </div>
          </div>
          <div class="text-center">
            <div class="text-xs text-slate-500">{{ $t('detail.small_net_flow') }}</div>
            <div class="text-lg font-semibold" :class="smallNetFlow >= 0 ? 'text-red-500' : 'text-green-500'">
              {{ formatMoney(smallNetFlow) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, CandlestickChart, BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, DataZoomComponent, MarkLineComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getStockDetail, getKlineData } from '../api'

use([CanvasRenderer, LineChart, CandlestickChart, BarChart, GridComponent, TooltipComponent, DataZoomComponent, MarkLineComponent])

const { t } = useI18n()
const props = defineProps<{ code: string }>()
const emit = defineEmits(['back'])

const loading = ref(true)
const stockInfo = ref<any>({})
const minuteData = ref<any[]>([])
const klineData = ref<any[]>([])
const moneyFlowData = ref<any[]>([])
const activeTab = ref('minute')

// 轮询定时器
let refreshTimer: ReturnType<typeof setInterval> | null = null
const REFRESH_INTERVAL = 5000 // 5秒刷新一次

const tabs = [
  { key: 'minute' },
  { key: 'day' },
  { key: 'week' },
  { key: 'month' },
]

const priceClass = computed(() => {
  const change = parseFloat(stockInfo.value.change_percent || '0')
  return change >= 0 ? 'text-red-500' : 'text-green-500'
})

const changeSign = computed(() => {
  const change = parseFloat(stockInfo.value.change_percent || '0')
  return change >= 0 ? '+' : ''
})

// 资金流向计算
const mainNetFlow = computed(() => {
  if (!moneyFlowData.value.length) return 0
  const last = moneyFlowData.value[moneyFlowData.value.length - 1]
  return (last?.big_in || 0) + (last?.super_in || 0)
})

const bigNetFlow = computed(() => {
  if (!moneyFlowData.value.length) return 0
  const last = moneyFlowData.value[moneyFlowData.value.length - 1]
  return last?.big_in || 0
})

const smallNetFlow = computed(() => {
  if (!moneyFlowData.value.length) return 0
  const last = moneyFlowData.value[moneyFlowData.value.length - 1]
  return last?.small_in || 0
})

const formatMoney = (val: number) => {
  if (Math.abs(val) >= 100000000) return (val / 100000000).toFixed(2) + t('detail.yi')
  if (Math.abs(val) >= 10000) return (val / 10000).toFixed(2) + t('detail.wan')
  return val.toFixed(2)
}

// 查找日期分割点索引（昨天和今天的分界）
const findDateSplitIndex = () => {
  if (minuteData.value.length < 2) return -1
  
  for (let i = 1; i < minuteData.value.length; i++) {
    const prevDate = minuteData.value[i - 1].date
    const currDate = minuteData.value[i].date
    // 如果日期不同，说明这是分割点
    if (prevDate && currDate && prevDate !== currDate) {
      return i
    }
  }
  return -1
}

// 图表配置
const chartOption = computed(() => {
  if (activeTab.value === 'minute') {
    return getMinuteChartOption()
  } else {
    return getKlineChartOption()
  }
})

const getMinuteChartOption = () => {
  if (!minuteData.value.length) return null
  const times = minuteData.value.map(d => d.time)
  const prices = minuteData.value.map(d => d.price)
  const volumes = minuteData.value.map((d, idx) => {
    // 判断涨跌颜色：与前一个价格比较
    const prevPrice = idx > 0 ? minuteData.value[idx - 1].price : d.price
    return {
      value: d.volume || 0,
      itemStyle: { color: d.price >= prevPrice ? '#ff4d4f' : '#52c41a' }
    }
  })
  const preClose = parseFloat(stockInfo.value.pre_close || '0')
  
  // 查找日期分割点
  const splitIndex = findDateSplitIndex()
  const splitTime = splitIndex > 0 ? times[splitIndex] : null
  
  // 构建 markLine 数据
  const markLineData: any[] = [
    { yAxis: preClose, lineStyle: { color: '#999', type: 'dashed', width: 1 } }
  ]
  
  // 如果有日期分割点，添加垂直分割线
  if (splitTime) {
    markLineData.push({
      xAxis: splitTime,
      lineStyle: { color: '#3b82f6', type: 'dashed', width: 1 },
      label: { 
        show: true, 
        formatter: '今日',
        position: 'start',
        color: '#3b82f6',
        fontSize: 10
      }
    })
  }
  
  return {
    tooltip: { 
      trigger: 'axis',
      formatter: (params: any) => {
        const priceData = params.find((p: any) => p.seriesName === '价格')
        const volData = params.find((p: any) => p.seriesName === '成交量')
        if (!priceData) return ''
        let html = `<div style="font-size:12px">${priceData.axisValue}</div>`
        html += `<div>价格: <span style="color:${priceData.value >= preClose ? '#ff4d4f' : '#52c41a'}">${priceData.value}</span></div>`
        if (volData) {
          html += `<div>成交量: ${formatVolume(volData.value)}</div>`
        }
        return html
      }
    },
    grid: [
      { left: 60, right: 20, top: 20, height: '55%' },
      { left: 60, right: 20, top: '70%', height: '20%' }
    ],
    xAxis: [
      { type: 'category', data: times, gridIndex: 0, axisLabel: { show: false }, boundaryGap: false },
      { type: 'category', data: times, gridIndex: 1, axisLabel: { fontSize: 10 }, boundaryGap: false }
    ],
    yAxis: [
      { 
        type: 'value', 
        scale: true,
        gridIndex: 0,
        splitLine: { lineStyle: { type: 'dashed' } },
        axisLabel: { fontSize: 10 }
      },
      { 
        type: 'value', 
        scale: true,
        gridIndex: 1,
        splitLine: { show: false },
        axisLabel: { show: false }
      }
    ],
    dataZoom: [{ type: 'inside', xAxisIndex: [0, 1] }],
    series: [
      {
        name: '价格',
        type: 'line',
        data: prices,
        smooth: true,
        symbol: 'none',
        xAxisIndex: 0,
        yAxisIndex: 0,
        lineStyle: { color: prices[prices.length - 1] >= preClose ? '#ff4d4f' : '#52c41a', width: 1.5 },
        areaStyle: { 
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: prices[prices.length - 1] >= preClose ? 'rgba(255,77,79,0.3)' : 'rgba(82,196,26,0.3)' },
              { offset: 1, color: 'rgba(255,255,255,0)' }
            ]
          }
        },
        markLine: {
          silent: true,
          symbol: 'none',
          data: markLineData
        }
      },
      {
        name: '成交量',
        type: 'bar',
        data: volumes,
        xAxisIndex: 1,
        yAxisIndex: 1,
        barWidth: '60%'
      }
    ]
  }
}

// 格式化成交量
const formatVolume = (vol: number) => {
  if (vol >= 100000000) return (vol / 100000000).toFixed(2) + '亿'
  if (vol >= 10000) return (vol / 10000).toFixed(0) + '万'
  return vol.toString()
}

const getKlineChartOption = () => {
  if (!klineData.value.length) return null
  const dates = klineData.value.map(d => d.date)
  const ohlc = klineData.value.map(d => [d.open, d.close, d.low, d.high])
  const volumes = klineData.value.map((d) => ({
    value: d.volume,
    itemStyle: { color: d.close >= d.open ? '#ff4d4f' : '#52c41a' }
  }))
  
  return {
    tooltip: { 
      trigger: 'axis', 
      axisPointer: { type: 'cross' },
      formatter: (params: any) => {
        const kData = params.find((p: any) => p.seriesType === 'candlestick')
        const volData = params.find((p: any) => p.seriesType === 'bar')
        if (!kData) return ''
        const [open, close, low, high] = kData.data
        const isUp = close >= open
        const color = isUp ? '#ff4d4f' : '#52c41a'
        let html = `<div style="font-size:12px;margin-bottom:4px">${kData.axisValue}</div>`
        html += `<div>开: <span style="color:${color}">${open}</span></div>`
        html += `<div>收: <span style="color:${color}">${close}</span></div>`
        html += `<div>高: <span style="color:#ff4d4f">${high}</span></div>`
        html += `<div>低: <span style="color:#52c41a">${low}</span></div>`
        if (volData) {
          html += `<div>成交量: ${formatVolume(volData.value)}</div>`
        }
        return html
      }
    },
    grid: [
      { left: 60, right: 20, top: 20, height: '55%' },
      { left: 60, right: 20, top: '70%', height: '20%' }
    ],
    xAxis: [
      { type: 'category', data: dates, gridIndex: 0, axisLabel: { show: false } },
      { type: 'category', data: dates, gridIndex: 1, axisLabel: { fontSize: 10 } }
    ],
    yAxis: [
      { type: 'value', scale: true, gridIndex: 0, splitLine: { lineStyle: { type: 'dashed' } } },
      { type: 'value', scale: true, gridIndex: 1, splitLine: { show: false }, axisLabel: { show: false } }
    ],
    dataZoom: [{ type: 'inside', xAxisIndex: [0, 1] }],
    series: [
      {
        type: 'candlestick',
        data: ohlc,
        xAxisIndex: 0,
        yAxisIndex: 0,
        itemStyle: { color: '#ff4d4f', color0: '#52c41a', borderColor: '#ff4d4f', borderColor0: '#52c41a' }
      },
      {
        type: 'bar',
        data: volumes,
        xAxisIndex: 1,
        yAxisIndex: 1
      }
    ]
  }
}

// 加载详情数据
const loadData = async (showLoading = true) => {
  if (showLoading) loading.value = true
  try {
    const res = await getStockDetail(props.code)
    if (res.status === 'success') {
      stockInfo.value = res.basic || {}
      minuteData.value = res.minute || []
      klineData.value = res.kline || []
      moneyFlowData.value = res.money_flow || []
    }
  } catch (e) {
    console.error('加载数据失败:', e)
  } finally {
    loading.value = false
  }
}

// 切换 K 线周期时重新加载数据
const loadKlineData = async (period: string) => {
  if (period === 'minute') return // 分时数据已加载
  
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

// 开始轮询刷新
const startRefresh = () => {
  stopRefresh()
  refreshTimer = setInterval(() => {
    if (activeTab.value === 'minute') {
      // 分时图：刷新全部数据
      loadData(false)
    } else {
      // K线图：刷新K线数据
      loadKlineData(activeTab.value)
    }
  }, REFRESH_INTERVAL)
}

// 停止轮询
const stopRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 监听 tab 切换
watch(activeTab, (newTab) => {
  if (newTab !== 'minute') {
    loadKlineData(newTab)
  }
})

onMounted(() => {
  loadData()
  startRefresh()
})

onUnmounted(() => {
  stopRefresh()
})

watch(() => props.code, () => {
  loadData()
})
</script>
