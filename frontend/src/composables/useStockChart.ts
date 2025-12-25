/**
 * 股票图表 Composable
 * 封装分时图和K线图的配置生成逻辑
 */
import { computed, ref, type Ref } from 'vue'
import type { TradeRecord } from '@/api'

// 分时数据接口
interface MinuteData {
  time: string
  date: string
  price: number
  volume?: number
}

// K线数据接口
interface KlineData {
  date: string
  open: number
  close: number
  high: number
  low: number
  volume: number
}

// 格式化成交量
export const formatVolume = (vol: number): string => {
  if (vol >= 100000000) return (vol / 100000000).toFixed(2) + '亿'
  if (vol >= 10000) return (vol / 10000).toFixed(0) + '万'
  if (vol >= 1000) return (vol / 1000).toFixed(1) + '千'
  return vol.toString()
}

export function useStockChart(
  minuteData: Ref<MinuteData[]>,
  klineData: Ref<KlineData[]>,
  stockInfo: Ref<any>,
  tradeRecords: Ref<TradeRecord[]>
) {
  // 用户缩放状态
  const userZoomState = ref<{ start: number; end: number } | null>(null)
  const isFirstLoad = ref(true)

  // 查找今天数据的起始索引
  const findTodayStartIndex = (): number => {
    if (minuteData.value.length < 2) return 0
    let lastSplitIndex = 0
    for (let i = 1; i < minuteData.value.length; i++) {
      const prevDate = minuteData.value[i - 1].date
      const currDate = minuteData.value[i].date
      if (prevDate && currDate && prevDate !== currDate) {
        lastSplitIndex = i
      }
    }
    return lastSplitIndex
  }

  // 计算均价线数据
  const calcAvgPrices = (): number[] => {
    const result: number[] = []
    let totalAmount = 0
    let totalVolume = 0
    const todayStartIdx = findTodayStartIndex()

    for (let i = 0; i < minuteData.value.length; i++) {
      const d = minuteData.value[i]
      if (i >= todayStartIdx) {
        totalAmount += d.price * (d.volume || 0)
        totalVolume += d.volume || 0
        result.push(totalVolume > 0 ? totalAmount / totalVolume : d.price)
      } else {
        result.push(d.price)
      }
    }
    return result
  }

  // 计算MA均线
  const calcMA = (data: KlineData[], period: number): (number | null)[] => {
    const result: (number | null)[] = []
    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        result.push(null)
      } else {
        let sum = 0
        for (let j = 0; j < period; j++) {
          sum += data[i - j].close
        }
        result.push(sum / period)
      }
    }
    return result
  }

  // 生成交易记录标记点
  const getTradeMarkPoints = (klineList: KlineData[], dateLabels: string[]) => {
    if (!tradeRecords.value.length || !klineList.length) return []

    const points: any[] = []
    const typeConfig: Record<string, { label: string; color: string; typeLabel: string }> = {
      'B': { label: 'B', color: '#ef4444', typeLabel: '买入' },
      'S': { label: 'S', color: '#22c55e', typeLabel: '卖出' },
      'T': { label: 'T', color: '#3b82f6', typeLabel: '做T' }
    }

    for (const record of tradeRecords.value) {
      const tradeDate = record.trade_time.split(' ')[0]
      const klineIndex = klineList.findIndex(k => k.date === tradeDate)
      if (klineIndex === -1) continue

      const config = typeConfig[record.type] || typeConfig['B']
      const kline = klineList[klineIndex]
      const yValue = record.type === 'B' ? kline.low * 0.995 : kline.high * 1.005

      points.push({
        value: [dateLabels[klineIndex], yValue],
        label: config.label,
        typeLabel: config.typeLabel,
        price: record.price,
        quantity: record.quantity,
        reason: record.reason,
        tradeTime: record.trade_time,
        itemStyle: { color: config.color },
        symbol: record.type === 'B' ? 'triangle' : (record.type === 'S' ? 'triangle' : 'diamond'),
        symbolRotate: record.type === 'S' ? 180 : 0
      })
    }
    return points
  }

  // 分时图配置
  const getMinuteChartOption = () => {
    if (!minuteData.value.length) return null

    const times = minuteData.value.map(d => d.time.substring(0, 5))
    const prices = minuteData.value.map(d => d.price)
    const avgPrices = calcAvgPrices()
    const preClose = parseFloat(stockInfo.value.pre_close || '0')

    // 成交量数据
    const volumes = minuteData.value.map((d, idx) => {
      const prevPrice = idx > 0 ? minuteData.value[idx - 1].price : d.price
      return {
        value: d.volume || 0,
        itemStyle: { color: d.price >= prevPrice ? 'rgba(255,77,79,0.7)' : 'rgba(82,196,26,0.7)' }
      }
    })

    const todayStartIdx = findTodayStartIndex()
    const labelInterval = Math.floor(times.length / 8)

    // 计算显示范围
    const totalLen = times.length
    const todayDataLen = totalLen - todayStartIdx
    let startPercent = 0
    let endPercent = 100

    if (userZoomState.value) {
      startPercent = userZoomState.value.start
      endPercent = userZoomState.value.end
    } else if (isFirstLoad.value && todayStartIdx > 0 && todayDataLen < totalLen * 0.6) {
      const showStartIdx = Math.max(0, todayStartIdx - 20)
      startPercent = (showStartIdx / totalLen) * 100
    }

    // 构建 markLine 数据
    const priceMarkLine: any[] = [
      {
        yAxis: preClose,
        lineStyle: { color: '#faad14', type: 'dashed', width: 1 },
        label: { show: true, formatter: `昨收 ${preClose}`, position: 'insideEndTop', color: '#faad14', fontSize: 10 }
      }
    ]

    if (todayStartIdx > 0) {
      priceMarkLine.push({
        xAxis: todayStartIdx,
        lineStyle: { color: '#3b82f6', type: 'dashed', width: 1 },
        label: { show: true, formatter: '今日', position: 'insideEndTop', color: '#3b82f6', fontSize: 10, backgroundColor: 'rgba(255,255,255,0.9)', padding: [2, 4], borderRadius: 2 }
      })
    }

    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
        formatter: (params: any) => {
          const priceData = params.find((p: any) => p.seriesName === '价格')
          const avgData = params.find((p: any) => p.seriesName === '均价')
          const volData = params.find((p: any) => p.seriesName === '成交量')
          if (!priceData) return ''

          const idx = priceData.dataIndex
          const dateStr = minuteData.value[idx]?.date || ''
          const currentPrice = priceData.value
          const changePercent = preClose > 0 ? ((currentPrice - preClose) / preClose * 100) : 0
          const changeColor = changePercent >= 0 ? '#ff4d4f' : '#52c41a'
          const changeSign = changePercent >= 0 ? '+' : ''

          let html = `<div style="font-size:12px;color:#666">${dateStr} ${priceData.axisValue}</div>`
          html += `<div>价格: <span style="color:${changeColor};font-weight:bold">${currentPrice.toFixed(2)}</span></div>`
          html += `<div>涨跌: <span style="color:${changeColor};font-weight:bold">${changeSign}${changePercent.toFixed(2)}%</span></div>`
          if (avgData?.value) html += `<div>均价: <span style="color:#faad14">${avgData.value.toFixed(2)}</span></div>`
          if (volData) html += `<div>成交量: ${formatVolume(volData.value)}</div>`
          return html
        }
      },
      legend: { data: ['价格', '均价'], top: 5, right: 60, textStyle: { fontSize: 11 } },
      grid: [
        { left: 60, right: 60, top: 35, height: '50%' },
        { left: 60, right: 60, top: '72%', height: '18%' }
      ],
      xAxis: [
        { type: 'category', data: times, gridIndex: 0, axisLabel: { show: false }, boundaryGap: false, axisLine: { lineStyle: { color: '#e5e7eb' } }, splitLine: { show: true, lineStyle: { color: '#f3f4f6', type: 'dashed' } } },
        { type: 'category', data: times, gridIndex: 1, axisLabel: { fontSize: 10, interval: labelInterval, color: '#9ca3af' }, boundaryGap: false, axisLine: { lineStyle: { color: '#e5e7eb' } } }
      ],
      yAxis: [
        { type: 'value', scale: true, gridIndex: 0, splitLine: { lineStyle: { type: 'dashed', color: '#f3f4f6' } }, axisLabel: { fontSize: 10, color: '#9ca3af', formatter: (v: number) => v.toFixed(2) }, position: 'right' },
        { type: 'value', scale: true, gridIndex: 1, splitLine: { show: false }, axisLabel: { show: false } }
      ],
      dataZoom: [{ type: 'inside', xAxisIndex: [0, 1], start: startPercent, end: endPercent }],
      series: [
        {
          name: '价格', type: 'line', data: prices, smooth: true, symbol: 'none', xAxisIndex: 0, yAxisIndex: 0,
          lineStyle: { color: prices[prices.length - 1] >= preClose ? '#ff4d4f' : '#52c41a', width: 1.5 },
          areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: prices[prices.length - 1] >= preClose ? 'rgba(255,77,79,0.2)' : 'rgba(82,196,26,0.2)' }, { offset: 1, color: 'rgba(255,255,255,0)' }] } },
          markLine: { silent: true, symbol: 'none', data: priceMarkLine }
        },
        { name: '均价', type: 'line', data: avgPrices, smooth: true, symbol: 'none', xAxisIndex: 0, yAxisIndex: 0, lineStyle: { color: '#faad14', width: 1 } },
        { name: '成交量', type: 'bar', data: volumes, xAxisIndex: 1, yAxisIndex: 1, barWidth: '70%' }
      ]
    }
  }

  // K线图配置
  const getKlineChartOption = () => {
    if (!klineData.value.length) return null

    const dates = klineData.value.map(d => d.date.substring(5))
    const ohlc = klineData.value.map(d => [d.open, d.close, d.low, d.high])
    const volumes = klineData.value.map(d => ({
      value: d.volume,
      itemStyle: { color: d.close >= d.open ? 'rgba(255,77,79,0.7)' : 'rgba(82,196,26,0.7)' }
    }))

    const ma5 = calcMA(klineData.value, 5)
    const ma10 = calcMA(klineData.value, 10)
    const ma20 = calcMA(klineData.value, 20)
    const labelInterval = Math.floor(dates.length / 10)

    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
        formatter: (params: any) => {
          const kData = params.find((p: any) => p.seriesType === 'candlestick')
          const volData = params.find((p: any) => p.seriesName === '成交量')
          const ma5Data = params.find((p: any) => p.seriesName === 'MA5')
          const ma10Data = params.find((p: any) => p.seriesName === 'MA10')
          const ma20Data = params.find((p: any) => p.seriesName === 'MA20')
          if (!kData) return ''

          const [open, close, low, high] = kData.data
          const isUp = close >= open
          const color = isUp ? '#ff4d4f' : '#52c41a'
          const idx = kData.dataIndex
          const fullDate = klineData.value[idx]?.date || ''

          let html = `<div style="font-size:12px;color:#666;margin-bottom:4px">${fullDate}</div>`
          html += `<div>开: <span style="color:${color}">${open.toFixed(2)}</span> 收: <span style="color:${color}">${close.toFixed(2)}</span></div>`
          html += `<div>高: <span style="color:#ff4d4f">${high.toFixed(2)}</span> 低: <span style="color:#52c41a">${low.toFixed(2)}</span></div>`
          if (ma5Data?.value) html += `<div style="color:#ff9800">MA5: ${ma5Data.value.toFixed(2)}</div>`
          if (ma10Data?.value) html += `<div style="color:#2196f3">MA10: ${ma10Data.value.toFixed(2)}</div>`
          if (ma20Data?.value) html += `<div style="color:#9c27b0">MA20: ${ma20Data.value.toFixed(2)}</div>`
          if (volData) html += `<div>成交量: ${formatVolume(volData.value)}</div>`
          return html
        }
      },
      legend: { data: ['MA5', 'MA10', 'MA20'], top: 5, right: 60, textStyle: { fontSize: 11 } },
      grid: [
        { left: 60, right: 60, top: 35, height: '50%' },
        { left: 60, right: 60, top: '72%', height: '18%' }
      ],
      xAxis: [
        { type: 'category', data: dates, gridIndex: 0, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#e5e7eb' } } },
        { type: 'category', data: dates, gridIndex: 1, axisLabel: { fontSize: 10, interval: labelInterval, color: '#9ca3af' }, axisLine: { lineStyle: { color: '#e5e7eb' } } }
      ],
      yAxis: [
        { type: 'value', scale: true, gridIndex: 0, splitLine: { lineStyle: { type: 'dashed', color: '#f3f4f6' } }, axisLabel: { fontSize: 10, color: '#9ca3af', formatter: (v: number) => v.toFixed(2) }, position: 'right' },
        { type: 'value', scale: true, gridIndex: 1, splitLine: { show: false }, axisLabel: { show: false } }
      ],
      dataZoom: [{ type: 'inside', xAxisIndex: [0, 1] }],
      series: [
        { name: 'K线', type: 'candlestick', data: ohlc, xAxisIndex: 0, yAxisIndex: 0, itemStyle: { color: '#ff4d4f', color0: '#52c41a', borderColor: '#ff4d4f', borderColor0: '#52c41a' } },
        { name: 'MA5', type: 'line', data: ma5, smooth: true, symbol: 'none', xAxisIndex: 0, yAxisIndex: 0, lineStyle: { color: '#ff9800', width: 1 } },
        { name: 'MA10', type: 'line', data: ma10, smooth: true, symbol: 'none', xAxisIndex: 0, yAxisIndex: 0, lineStyle: { color: '#2196f3', width: 1 } },
        { name: 'MA20', type: 'line', data: ma20, smooth: true, symbol: 'none', xAxisIndex: 0, yAxisIndex: 0, lineStyle: { color: '#9c27b0', width: 1 } },
        { name: '成交量', type: 'bar', data: volumes, xAxisIndex: 1, yAxisIndex: 1 },
        {
          name: '交易记录', type: 'scatter', data: getTradeMarkPoints(klineData.value, dates), xAxisIndex: 0, yAxisIndex: 0, symbolSize: 20, itemStyle: { opacity: 0.9 },
          label: { show: true, formatter: (params: any) => params.data.label, fontSize: 10, fontWeight: 'bold', color: '#fff' },
          tooltip: { formatter: (params: any) => `<div style="font-size:12px"><div style="font-weight:bold;margin-bottom:4px">${params.data.typeLabel}</div><div>价格: ¥${params.data.price}</div><div>手数: ${params.data.quantity}手</div><div>时间: ${params.data.tradeTime}</div><div style="margin-top:4px;color:#666">${params.data.reason}</div></div>` }
        }
      ]
    }
  }

  // 处理缩放事件
  const handleDataZoom = (params: any) => {
    const batch = params.batch?.[0] || params
    if (batch.start !== undefined && batch.end !== undefined) {
      userZoomState.value = { start: batch.start, end: batch.end }
    }
  }

  // 重置缩放状态
  const resetZoomState = () => {
    userZoomState.value = null
    isFirstLoad.value = true
  }

  // 标记首次加载完成
  const markFirstLoadDone = () => {
    if (isFirstLoad.value) {
      isFirstLoad.value = false
    }
  }

  return {
    userZoomState,
    isFirstLoad,
    getMinuteChartOption,
    getKlineChartOption,
    handleDataZoom,
    resetZoomState,
    markFirstLoadDone
  }
}
