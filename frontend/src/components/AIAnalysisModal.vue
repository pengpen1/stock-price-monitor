<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
  >
    <div
      class="flex max-h-[90vh] w-3/4 max-w-4xl transform flex-col overflow-hidden rounded-xl border border-gray-700 bg-gray-900 shadow-2xl transition-all"
    >
      <!-- Header -->
      <div class="flex items-center justify-between border-b border-gray-700 bg-gray-800 p-4">
        <h3 class="text-lg font-semibold text-white">
          {{ stockCode }} · {{ type === "fast" ? "快速分析" : "精准分析" }}
        </h3>
        <button
          @click="close"
          class="rounded p-1 text-gray-400 transition-colors hover:bg-gray-700 hover:text-white"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-auto p-6 text-gray-200">
        <!-- Error: No Config -->
        <div v-if="!hasConfig" class="py-16 text-center">
          <div class="inline-block max-w-md rounded-lg bg-red-900/20 p-6 text-red-200">
            <h4 class="mb-2 text-lg font-semibold">未配置 AI API Key</h4>
            <p class="mb-4 text-sm text-red-200/70">
              请前往设置页面配置大模型 API Key (Gemini, GPT, Claude等) 后再使用此功能。
            </p>
            <button
              @click="close"
              class="rounded bg-red-800 px-5 py-2 text-white transition-colors hover:bg-red-700"
            >
              关闭
            </button>
          </div>
        </div>

        <!-- Input Form (Precise Mode) -->
        <div v-else-if="step === 'input'" class="mx-auto max-w-2xl space-y-6 py-4">
          <div class="rounded-lg border border-gray-700/50 bg-gray-800/50 p-6">
            <h4 class="mb-4 text-base font-medium text-gray-200">基础数据</h4>
            <div class="grid grid-cols-2 gap-6">
              <div>
                <label class="mb-2 block text-sm font-medium text-gray-400">持仓成本</label>
                <div class="relative">
                  <span class="absolute top-2.5 left-3 text-gray-500">¥</span>
                  <input
                    v-model="inputs.costPrice"
                    type="number"
                    class="w-full rounded-lg border border-gray-600 bg-gray-900 py-2.5 pr-3 pl-8 text-white transition-all outline-none focus:border-transparent focus:ring-2 focus:ring-blue-500"
                    placeholder="0.00"
                  />
                </div>
              </div>
              <div>
                <label class="mb-2 block text-sm font-medium text-gray-400">持仓数量</label>
                <input
                  v-model="inputs.position"
                  type="number"
                  class="w-full rounded-lg border border-gray-600 bg-gray-900 px-3 py-2.5 text-white transition-all outline-none focus:border-transparent focus:ring-2 focus:ring-blue-500"
                  placeholder="0"
                />
              </div>
              <div>
                <label class="mb-2 block text-sm font-medium text-gray-400">止盈位 (默认20%)</label>
                <input
                  v-model="inputs.takeProfit"
                  type="text"
                  class="w-full rounded-lg border border-gray-600 bg-gray-900 px-3 py-2.5 text-white transition-all outline-none focus:border-transparent focus:ring-2 focus:ring-blue-500"
                  placeholder="自动计算"
                />
              </div>
              <div>
                <label class="mb-2 block text-sm font-medium text-gray-400">止损位 (默认20%)</label>
                <input
                  v-model="inputs.stopLoss"
                  type="text"
                  class="w-full rounded-lg border border-gray-600 bg-gray-900 px-3 py-2.5 text-white transition-all outline-none focus:border-transparent focus:ring-2 focus:ring-blue-500"
                  placeholder="自动计算"
                />
              </div>
            </div>
          </div>

          <div class="rounded-lg border border-gray-700/50 bg-gray-800/50 p-6">
            <h4 class="mb-4 text-base font-medium text-gray-200">补充信息</h4>
            <label class="mb-2 block text-sm font-medium text-gray-400"
              >附加材料 (新闻/政策/个人想法)</label
            >
            <textarea
              v-model="inputs.extraText"
              rows="4"
              class="w-full rounded-lg border border-gray-600 bg-gray-900 px-4 py-3 text-white transition-all outline-none focus:border-transparent focus:ring-2 focus:ring-purple-500"
              placeholder="请输入任何可能影响走势的额外信息..."
            ></textarea>
          </div>

          <div class="flex justify-end pt-2">
            <button
              @click="startAnalysis"
              class="rounded-lg bg-blue-600 px-6 py-2.5 font-medium text-white transition-colors hover:bg-blue-500"
            >
              开始分析
            </button>
          </div>
        </div>

        <!-- Loading -->
        <div v-else-if="step === 'loading'" class="flex flex-col items-center justify-center py-32">
          <div class="relative mb-6 h-16 w-16">
            <div class="absolute inset-0 rounded-full border-3 border-gray-600"></div>
            <div
              class="absolute inset-0 animate-spin rounded-full border-3 border-t-blue-500"
            ></div>
          </div>
          <h4 class="mb-2 text-lg font-medium text-white">正在分析中</h4>
          <p class="text-sm text-gray-400">通过 {{ config?.provider }} 获取分析结果...</p>
        </div>

        <!-- Result -->
        <div v-else-if="step === 'result'" class="space-y-4">
          <!-- Prompt 消息流展示 -->
          <div
            v-if="promptText"
            class="overflow-hidden rounded-lg border border-gray-700/50 bg-gray-800/50"
          >
            <div
              @click="showPrompt = !showPrompt"
              class="flex cursor-pointer items-center justify-between px-4 py-3 transition-colors hover:bg-gray-700/30"
            >
              <div class="flex items-center gap-2">
                <span class="text-sm text-gray-400">📝 prompt</span>
                <span class="text-xs text-gray-500">({{ promptText.length }} 字符)</span>
              </div>
              <div class="flex items-center gap-2">
                <button
                  @click.stop="copyPrompt"
                  class="rounded border border-blue-500/50 px-2 py-1 text-xs text-blue-400 transition-colors hover:bg-blue-500/20"
                >
                  复制
                </button>
                <span class="text-sm text-gray-500">{{ showPrompt ? "▼" : "▶" }}</span>
              </div>
            </div>
            <div v-if="showPrompt" class="border-t border-gray-700/50">
              <pre
                class="max-h-64 overflow-auto p-4 font-mono text-xs whitespace-pre-wrap text-gray-300"
                >{{ promptText }}</pre
              >
            </div>
          </div>

          <!-- 预测趋势图（仅精准分析） -->
          <div
            v-if="type === 'precise' && prediction.length > 0"
            class="mb-4 rounded-lg border border-gray-700/50 bg-gray-800/50 p-4"
          >
            <div class="mb-3 flex items-center justify-between">
              <h4 class="text-sm font-medium text-gray-300">未来5日趋势预测</h4>
              <span class="text-xs text-gray-500">基于AI分析，仅供参考</span>
            </div>
            <div ref="predictionChartRef" class="h-64 w-full"></div>
          </div>

          <!-- 分析结果 -->
          <MarkdownView :source="result"></MarkdownView>
          <div class="flex justify-end pt-4">
            <button
              @click="step = 'input'"
              v-if="type === 'precise'"
              class="mr-3 rounded border border-blue-500 px-4 py-2 text-blue-400 transition-colors hover:bg-blue-500/10"
            >
              重新调整参数
            </button>
            <button
              @click="
                showPrompt = false
                step = 'loading'
                startAnalysis()
              "
              class="rounded bg-blue-600 px-4 py-2 text-white transition-colors hover:bg-blue-500"
            >
              重新生成
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, nextTick } from "vue"
import { marked } from "marked"
import * as echarts from "echarts"
import { analyzeStock, getSettings, getStockPosition } from "../api"
import MarkdownView from "./markdown/MarkdownView.vue"

// 预测数据类型
interface PredictionItem {
  date: string
  price: number
  change_pct: number
}

const props = defineProps<{
  visible: boolean
  stockCode: string
  type: "fast" | "precise"
}>()

const emit = defineEmits(["update:visible"])

const step = ref<"input" | "loading" | "result">("input")
const inputs = ref({
  costPrice: "",
  position: "",
  takeProfit: "",
  stopLoss: "",
  extraText: "",
})
const result = ref("")
const promptText = ref("") // 保存发送给大模型的 prompt
const showPrompt = ref(false) // 是否展开 prompt
const config = ref<{
  provider: string
  apiKey: string
  model: string
  proxy?: string
  baseUrl?: string
} | null>(null)
const prediction = ref<PredictionItem[]>([]) // 预测数据
const currentPrice = ref(0) // 当前价格
const predictionChartRef = ref<HTMLElement | null>(null) // 图表容器
let predictionChart: echarts.ECharts | null = null // 图表实例

const hasConfig = computed(() => !!config.value?.apiKey)

const renderedResult = computed(() => {
  return marked.parse(result.value)
})

watch(
  () => props.visible,
  async (newVal) => {
    if (newVal) {
      await loadConfig()
      result.value = ""
      promptText.value = ""
      showPrompt.value = false

      // 如果没有配置，就不进行后续判断了
      if (!config.value?.apiKey) {
        return
      }

      if (props.type === "fast") {
        step.value = "loading"
        startAnalysis()
      } else {
        step.value = "input"
        // 精准分析时自动加载持仓数据
        await loadPosition()
      }
    }
  },
)

// 加载持仓数据
const loadPosition = async () => {
  try {
    const res = await getStockPosition(props.stockCode)
    if (res && res.position > 0) {
      inputs.value.costPrice = res.cost_price.toString()
      inputs.value.position = (res.position * 100).toString() // 手数转股数
    } else {
      // 没有持仓记录，清空
      inputs.value.costPrice = ""
      inputs.value.position = ""
    }
  } catch (e) {
    console.error("加载持仓数据失败:", e)
  }
}

// 从后端加载 AI 配置
const loadConfig = async () => {
  try {
    const res = await getSettings()
    if (res.status === "success" && res.settings?.ai_api_key) {
      config.value = {
        provider: res.settings.ai_provider || "gemini",
        apiKey: res.settings.ai_api_key || "",
        model: res.settings.ai_model || "",
        proxy: res.settings.ai_proxy || "",
        baseUrl: res.settings.ai_base_url || "",
      }
    } else {
      config.value = null
    }
  } catch (e) {
    console.error("加载 AI 配置失败:", e)
    config.value = null
  }
}

const close = () => {
  emit("update:visible", false)
}

const startAnalysis = async () => {
  step.value = "loading"
  prediction.value = []

  try {
    if (!config.value) return

    const analysisInputs = {
      cost_price: inputs.value.costPrice,
      position: inputs.value.position,
      take_profit: inputs.value.takeProfit || "20%",
      stop_loss: inputs.value.stopLoss || "20%",
      extra_text: inputs.value.extraText,
    }

    const res = await analyzeStock(
      props.stockCode,
      props.type,
      config.value.provider,
      config.value.apiKey,
      config.value.model,
      props.type === "precise" ? analysisInputs : {},
      config.value.proxy,
      config.value.baseUrl,
    )

    if (res.status === "success") {
      result.value = res.result
      promptText.value = res.prompt || ""
      prediction.value = res.prediction || []
      currentPrice.value = res.current_price || 0
      step.value = "result"

      // 渲染预测图表
      if (props.type === "precise" && prediction.value.length > 0) {
        await nextTick()
        renderPredictionChart()
      }
    } else {
      result.value = `**分析失败**: ${res.message}`
      promptText.value = ""
      prediction.value = []
      step.value = "result"
    }
  } catch (e: any) {
    result.value = `**发生错误**: ${e.message || "未知错误"}`
    promptText.value = ""
    prediction.value = []
    step.value = "result"
  }
}

// 渲染预测趋势图
const renderPredictionChart = () => {
  if (!predictionChartRef.value || prediction.value.length === 0) return

  // 销毁旧图表
  if (predictionChart) {
    predictionChart.dispose()
  }

  predictionChart = echarts.init(predictionChartRef.value)

  // 构建数据：当前价格 + 预测价格
  const dates = ["今日", ...prediction.value.map((p) => p.date.slice(5))] // MM-DD 格式
  const prices = [currentPrice.value, ...prediction.value.map((p) => p.price)]
  const changes = [0, ...prediction.value.map((p) => p.change_pct)]

  // 计算价格范围
  const minPrice = Math.min(...prices) * 0.98
  const maxPrice = Math.max(...prices) * 1.02

  // 判断整体趋势
  const lastPrice = prices[prices.length - 1]
  const isUp = lastPrice > currentPrice.value
  const lineColor = isUp ? "#22c55e" : "#ef4444"
  const areaColorStart = isUp ? "rgba(34, 197, 94, 0.3)" : "rgba(239, 68, 68, 0.3)"
  const areaColorEnd = isUp ? "rgba(34, 197, 94, 0.05)" : "rgba(239, 68, 68, 0.05)"

  const option: echarts.EChartsOption = {
    backgroundColor: "transparent",
    grid: {
      left: 60,
      right: 20,
      top: 30,
      bottom: 40,
    },
    tooltip: {
      trigger: "axis",
      backgroundColor: "rgba(30, 41, 59, 0.95)",
      borderColor: "#475569",
      textStyle: { color: "#e2e8f0" },
      formatter: (params: any) => {
        const idx = params[0].dataIndex
        const price = prices[idx]
        const change = changes[idx]
        const changeStr = change >= 0 ? `+${change.toFixed(2)}%` : `${change.toFixed(2)}%`
        const changeColor = change >= 0 ? "#22c55e" : "#ef4444"

        if (idx === 0) {
          return `<div style="font-size:12px">
                        <div style="margin-bottom:4px;color:#94a3b8">当前价格</div>
                        <div style="font-size:16px;font-weight:bold">¥${price.toFixed(2)}</div>
                    </div>`
        }

        return `<div style="font-size:12px">
                    <div style="margin-bottom:4px;color:#94a3b8">${prediction.value[idx - 1].date}</div>
                    <div style="font-size:16px;font-weight:bold">¥${price.toFixed(2)}</div>
                    <div style="color:${changeColor};margin-top:4px">预估涨跌: ${changeStr}</div>
                </div>`
      },
    },
    xAxis: {
      type: "category",
      data: dates,
      axisLine: { lineStyle: { color: "#475569" } },
      axisLabel: { color: "#94a3b8", fontSize: 11 },
      axisTick: { show: false },
    },
    yAxis: {
      type: "value",
      min: minPrice,
      max: maxPrice,
      axisLine: { show: false },
      axisLabel: {
        color: "#94a3b8",
        fontSize: 11,
        formatter: (v: number) => `¥${v.toFixed(2)}`,
      },
      splitLine: { lineStyle: { color: "#334155", type: "dashed" } },
    },
    series: [
      {
        type: "line",
        data: prices,
        smooth: true,
        symbol: "circle",
        symbolSize: 8,
        lineStyle: { color: lineColor, width: 3 },
        itemStyle: {
          color: lineColor,
          borderColor: "#1e293b",
          borderWidth: 2,
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: areaColorStart },
            { offset: 1, color: areaColorEnd },
          ]),
        },
        markLine: {
          silent: true,
          symbol: "none",
          lineStyle: { color: "#64748b", type: "dashed", width: 1 },
          data: [{ yAxis: currentPrice.value, label: { show: false } }],
        },
      },
    ],
  }

  predictionChart.setOption(option)
}

// 组件卸载时销毁图表
watch(
  () => props.visible,
  (val) => {
    if (!val && predictionChart) {
      predictionChart.dispose()
      predictionChart = null
    }
  },
)

// 复制 prompt 到剪贴板
const copyPrompt = async () => {
  try {
    await navigator.clipboard.writeText(promptText.value)
    // 可以添加一个提示
  } catch (e) {
    console.error("复制失败:", e)
  }
}
</script>
