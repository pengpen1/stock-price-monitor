<template>
  <Teleport to="body">
    <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/50" @click="close"></div>

      <div class="relative max-h-[80vh] w-[700px] overflow-hidden rounded-2xl bg-white shadow-2xl">
        <!-- 头部 -->
        <div class="flex items-center justify-between border-b border-slate-100 px-6 py-4">
          <div>
            <h3 class="text-lg font-semibold text-slate-800">{{ stockName }} 分时图</h3>
            <p class="text-sm text-slate-500">{{ date }}</p>
          </div>
          <button @click="close" class="rounded p-1 text-slate-400 hover:text-slate-600">
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <!-- 图表 -->
        <div class="p-4" style="height: 400px">
          <div v-if="loading" class="flex h-full items-center justify-center text-slate-400">
            加载中...
          </div>
          <div v-else-if="error" class="flex h-full items-center justify-center text-amber-500">
            {{ error }}
          </div>
          <v-chart v-else-if="chartOption" :option="chartOption" autoresize class="h-full w-full" />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue"
import { use } from "echarts/core"
import { CanvasRenderer } from "echarts/renderers"
import { LineChart, BarChart } from "echarts/charts"
import { GridComponent, TooltipComponent } from "echarts/components"
import VChart from "vue-echarts"
import { getSimulationMinute } from "../api"

use([CanvasRenderer, LineChart, BarChart, GridComponent, TooltipComponent])

const props = defineProps<{
  visible: boolean
  sessionId: string
  date: string
  stockName: string
}>()

const emit = defineEmits(["update:visible"])

const loading = ref(false)
const error = ref("")
const minuteData = ref<any[]>([])

const close = () => {
  emit("update:visible", false)
}

const loadData = async () => {
  if (!props.date || !props.sessionId) return

  loading.value = true
  error.value = ""

  try {
    const res = await getSimulationMinute(props.sessionId, props.date)
    if (res.status === "success") {
      minuteData.value = res.data || []
      if (minuteData.value.length === 0) {
        error.value = "暂无分时数据"
      }
    } else {
      error.value = res.message || "加载失败"
    }
  } catch (e: any) {
    error.value = e.message || "加载失败"
  } finally {
    loading.value = false
  }
}

const chartOption = computed(() => {
  if (!minuteData.value.length) return null

  const times = minuteData.value.map((d) => d.time?.substring(0, 5) || "")
  const prices = minuteData.value.map((d) => d.price)
  const volumes = minuteData.value.map((d, idx) => {
    const prevPrice = idx > 0 ? minuteData.value[idx - 1].price : d.price
    return {
      value: d.volume || 0,
      itemStyle: {
        color: d.price >= prevPrice ? "rgba(255,77,79,0.7)" : "rgba(82,196,26,0.7)",
      },
    }
  })

  // 计算开盘价作为基准
  const openPrice = minuteData.value[0]?.open || minuteData.value[0]?.price || 0
  const lastPrice = prices[prices.length - 1]
  const isUp = lastPrice >= openPrice

  return {
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross" },
    },
    grid: [
      { left: 50, right: 50, top: 30, height: "55%" },
      { left: 50, right: 50, top: "72%", height: "18%" },
    ],
    xAxis: [
      {
        type: "category",
        data: times,
        gridIndex: 0,
        axisLabel: { show: false },
        boundaryGap: false,
      },
      {
        type: "category",
        data: times,
        gridIndex: 1,
        axisLabel: { fontSize: 10, interval: Math.floor(times.length / 6) },
        boundaryGap: false,
      },
    ],
    yAxis: [
      {
        type: "value",
        scale: true,
        gridIndex: 0,
        position: "right",
        axisLabel: { fontSize: 10 },
      },
      { type: "value", scale: true, gridIndex: 1, axisLabel: { show: false } },
    ],
    series: [
      {
        name: "价格",
        type: "line",
        data: prices,
        smooth: true,
        symbol: "none",
        lineStyle: { color: isUp ? "#ff4d4f" : "#52c41a", width: 1.5 },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: isUp ? "rgba(255,77,79,0.2)" : "rgba(82,196,26,0.2)",
              },
              { offset: 1, color: "rgba(255,255,255,0)" },
            ],
          },
        },
      },
      {
        name: "成交量",
        type: "bar",
        data: volumes,
        xAxisIndex: 1,
        yAxisIndex: 1,
        barWidth: "70%",
      },
    ],
  }
})

watch(
  () => props.visible,
  (val) => {
    if (val) {
      loadData()
    }
  },
)
</script>
