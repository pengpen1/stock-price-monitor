<template>
  <div v-if="visible" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm">
    <div class="bg-white rounded-xl w-4/5 max-w-5xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
      <!-- 头部 -->
      <div class="flex justify-between items-center p-4 border-b border-slate-200 bg-slate-50">
        <div class="flex items-center gap-4">
          <h3 class="text-lg font-semibold text-slate-800">{{ indexInfo.name || '大盘指数' }}</h3>
          <span class="text-2xl font-bold" :class="getPriceClass(indexInfo.change_percent)">
            {{ indexInfo.price }}
          </span>
          <span class="text-sm" :class="getPriceClass(indexInfo.change_percent)">
            {{ parseFloat(indexInfo.change_percent || '0') >= 0 ? '+' : '' }}{{ indexInfo.change_percent }}%
          </span>
        </div>
        <button @click="close" class="text-slate-400 hover:text-slate-600 p-1 rounded hover:bg-slate-200">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 内容区 -->
      <div class="flex-1 overflow-auto p-4">
        <div v-if="loading" class="flex items-center justify-center py-20">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span class="ml-3 text-slate-500">加载中...</span>
        </div>

        <div v-else class="space-y-4">
          <!-- 基本信息 -->
          <div class="grid grid-cols-4 gap-3 text-sm">
            <div class="bg-slate-50 rounded-lg p-3">
              <div class="text-slate-500 text-xs">今开</div>
              <div class="font-semibold">{{ indexInfo.open }}</div>
            </div>
            <div class="bg-slate-50 rounded-lg p-3">
              <div class="text-slate-500 text-xs">昨收</div>
              <div class="font-semibold">{{ indexInfo.pre_close }}</div>
            </div>
            <div class="bg-slate-50 rounded-lg p-3">
              <div class="text-slate-500 text-xs">最高</div>
              <div class="font-semibold text-red-500">{{ indexInfo.high }}</div>
            </div>
            <div class="bg-slate-50 rounded-lg p-3">
              <div class="text-slate-500 text-xs">最低</div>
              <div class="font-semibold text-green-500">{{ indexInfo.low }}</div>
            </div>
            <!-- <div class="bg-slate-50 rounded-lg p-3">
              <div class="text-slate-500 text-xs">上涨家数</div>
              <div class="font-semibold text-red-500">{{ currentStats.rise_count || 0 }}</div>
            </div>
            <div class="bg-slate-50 rounded-lg p-3">
              <div class="text-slate-500 text-xs">下跌家数</div>
              <div class="font-semibold text-green-500">{{ currentStats.fall_count || 0 }}</div>
            </div> -->
          </div>

          <!-- 分时图 -->
          <div class="bg-white border border-slate-200 rounded-lg p-4">
            <h4 class="text-sm font-semibold text-slate-700 mb-3">分时走势</h4>
            <div ref="minuteChartRef" class="h-64"></div>
          </div>

          <!-- K线图 -->
          <div class="bg-white border border-slate-200 rounded-lg p-4">
            <h4 class="text-sm font-semibold text-slate-700 mb-3">近期走势（日K）</h4>
            <div ref="klineChartRef" class="h-64"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick, watchEffect } from 'vue';
import * as echarts from 'echarts';
import { getIndexDetail } from '../api';

const props = defineProps<{
  visible: boolean;
  indexCode: string;
}>();

const emit = defineEmits(['update:visible']);

const loading = ref(false);
const indexInfo = ref<any>({});
const minuteData = ref<any[]>([]);
const klineData = ref<any[]>([]);
const currentStats = ref<any>({});

const minuteChartRef = ref<HTMLElement | null>(null);
const klineChartRef = ref<HTMLElement | null>(null);

let minuteChart: echarts.ECharts | null = null;
let klineChart: echarts.ECharts | null = null;

const getPriceClass = (changePercent: string) => {
  const value = parseFloat(changePercent || '0');
  if (value > 0) return 'text-red-500';
  if (value < 0) return 'text-green-500';
  return 'text-slate-600';
};

const close = () => {
  emit('update:visible', false);
};

// 数据加载完成标记
const dataLoaded = ref(false);

// 加载数据
const loadData = async () => {
  if (!props.indexCode) return;
  
  loading.value = true;
  dataLoaded.value = false;
  
  try {
    const res = await getIndexDetail(props.indexCode);
    console.log('接口返回数据:', res);
    
    if (res.status === 'success') {
      indexInfo.value = res.basic || {};
      minuteData.value = res.minute || [];
      klineData.value = res.kline || [];
      currentStats.value = res.current_stats || {};
      
      console.log('分时数据条数:', minuteData.value.length);
      console.log('K线数据条数:', klineData.value.length);
    }
  } catch (e) {
    console.error('加载大盘详情失败:', e);
  } finally {
    loading.value = false;
    dataLoaded.value = true;
  }
};

// 监听数据和 DOM 都准备好后渲染图表
watchEffect(() => {
  if (dataLoaded.value && !loading.value && minuteChartRef.value && minuteData.value.length > 0) {
    console.log('触发分时图渲染');
    setTimeout(() => renderMinuteChart(), 50);
  }
});

watchEffect(() => {
  if (dataLoaded.value && !loading.value && klineChartRef.value && klineData.value.length > 0) {
    console.log('触发K线图渲染');
    setTimeout(() => renderKlineChart(), 50);
  }
});

// 渲染分时图
const renderMinuteChart = () => {
  console.log('渲染分时图, ref:', minuteChartRef.value, '数据长度:', minuteData.value.length);
  
  if (!minuteChartRef.value) {
    console.log('图表容器不存在');
    return;
  }
  
  if (minuteData.value.length === 0) {
    console.log('分时数据为空');
    return;
  }
  
  if (minuteChart) {
    minuteChart.dispose();
  }
  
  minuteChart = echarts.init(minuteChartRef.value);
  
  // 只取今天的数据
  const today = minuteData.value.length > 0 ? minuteData.value[minuteData.value.length - 1].date : '';
  let todayData = minuteData.value.filter(d => d.date === today);
  
  // 如果过滤后没有数据，使用全部数据
  if (todayData.length === 0) {
    todayData = minuteData.value;
  }
  
  console.log('今天日期:', today, '数据条数:', todayData.length);
  
  const times = todayData.map(d => d.time);
  const prices = todayData.map(d => d.price);
  const avgPrices = todayData.map(d => d.avg_price);
  const preClose = todayData[0]?.pre_close || prices[0];
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const p = params[0];
        const change = ((p.value - preClose) / preClose * 100).toFixed(2);
        return `${p.axisValue}<br/>价格: ${p.value}<br/>涨跌: ${change}%`;
      }
    },
    grid: { left: 60, right: 30, top: 20, bottom: 30 },
    xAxis: {
      type: 'category',
      data: times,
      axisLabel: { fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      scale: true,
      splitLine: { lineStyle: { type: 'dashed' } },
      axisLabel: { fontSize: 10 }
    },
    series: [
      {
        name: '价格',
        type: 'line',
        data: prices,
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 1.5, color: '#3b82f6' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
            { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
          ])
        },
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { color: '#94a3b8', type: 'dashed' },
          data: [{ yAxis: preClose, label: { formatter: '昨收', fontSize: 10 } }]
        }
      },
      {
        name: '均价',
        type: 'line',
        data: avgPrices,
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 1, color: '#f59e0b', type: 'dashed' }
      }
    ]
  };
  
  minuteChart.setOption(option);
};

// 渲染K线图
const renderKlineChart = () => {
  console.log('渲染K线图, ref:', klineChartRef.value, '数据长度:', klineData.value.length);
  
  if (!klineChartRef.value) {
    console.log('K线图表容器不存在');
    return;
  }
  
  if (klineData.value.length === 0) {
    console.log('K线数据为空');
    return;
  }
  
  if (klineChart) {
    klineChart.dispose();
  }
  
  klineChart = echarts.init(klineChartRef.value);
  
  const dates = klineData.value.map(d => d.date);
  const values = klineData.value.map(d => [d.open, d.close, d.low, d.high]);
  const volumes = klineData.value.map(d => {
    const isUp = d.close >= d.open;
    return { value: d.volume, itemStyle: { color: isUp ? '#ef4444' : '#22c55e' } };
  });
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
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
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: values,
        xAxisIndex: 0,
        yAxisIndex: 0,
        itemStyle: {
          color: '#ef4444',
          color0: '#22c55e',
          borderColor: '#ef4444',
          borderColor0: '#22c55e'
        }
      },
      {
        name: '成交量',
        type: 'bar',
        data: volumes,
        xAxisIndex: 1,
        yAxisIndex: 1
      }
    ]
  };
  
  klineChart.setOption(option);
};

// 窗口大小变化时重绘图表
const handleResize = () => {
  minuteChart?.resize();
  klineChart?.resize();
};

watch(() => props.visible, (newVal) => {
  if (newVal) {
    loadData();
  } else {
    // 清理图表和数据
    dataLoaded.value = false;
    if (minuteChart) {
      minuteChart.dispose();
      minuteChart = null;
    }
    if (klineChart) {
      klineChart.dispose();
      klineChart = null;
    }
  }
});

onMounted(() => {
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (minuteChart) minuteChart.dispose();
  if (klineChart) klineChart.dispose();
});
</script>
