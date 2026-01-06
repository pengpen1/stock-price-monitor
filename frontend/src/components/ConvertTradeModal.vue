<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click.self="$emit('close')"
  >
    <div class="flex max-h-[80vh] w-[700px] flex-col rounded-lg bg-white shadow-xl">
      <!-- 标题栏 -->
      <div class="flex items-center justify-between border-b border-slate-200 p-4">
        <h3 class="text-lg font-semibold">转换为交易记录</h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-600">
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

      <!-- 内容区 -->
      <div class="flex-1 overflow-auto p-4">
        <!-- 步骤1: 选择 AI 配置 -->
        <div v-if="step === 1" class="space-y-4">
          <p class="text-sm text-slate-600">
            使用 AI 分析笔记内容，自动提取交易记录。请确认 AI 配置：
          </p>

          <div class="space-y-3 rounded-lg bg-slate-50 p-4">
            <div class="flex items-center gap-2">
              <span class="w-20 text-sm text-slate-500">AI 服务:</span>
              <span class="text-sm font-medium">{{ settings.ai_provider || "未配置" }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="w-20 text-sm text-slate-500">模型:</span>
              <span class="text-sm font-medium">{{ settings.ai_model || "未配置" }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="w-20 text-sm text-slate-500">API Key:</span>
              <span class="text-sm font-medium">{{
                settings.ai_api_key ? "已配置" : "未配置"
              }}</span>
            </div>
          </div>

          <div v-if="!settings.ai_provider || !settings.ai_api_key" class="text-sm text-red-500">
            请先在设置中配置 AI 服务
          </div>
        </div>

        <!-- 步骤2: 分析中 -->
        <div v-else-if="step === 2" class="flex flex-col items-center justify-center py-12">
          <div class="mb-4 h-10 w-10 animate-spin rounded-full border-b-2 border-blue-500"></div>
          <p class="text-slate-600">正在分析笔记内容...</p>
        </div>

        <!-- 步骤3: 确认结果 -->
        <div v-else-if="step === 3" class="space-y-4">
          <div v-if="extractedTrades.length === 0" class="py-8 text-center text-slate-500">
            未从笔记中识别到交易记录
          </div>

          <div v-else>
            <p class="mb-3 text-sm text-slate-600">
              识别到 {{ extractedTrades.length }} 条交易记录，请确认后导入：
            </p>

            <!-- 交易记录列表 -->
            <div class="max-h-[300px] space-y-2 overflow-auto">
              <div
                v-for="(trade, idx) in extractedTrades"
                :key="idx"
                class="flex items-center gap-3 rounded-lg bg-slate-50 p-3"
              >
                <input type="checkbox" v-model="selectedTrades" :value="idx" class="rounded" />
                <div class="flex-1">
                  <div class="flex items-center gap-2">
                    <span
                      :class="[
                        'rounded px-2 py-0.5 text-xs',
                        trade.type === 'B'
                          ? 'bg-red-100 text-red-600'
                          : trade.type === 'S'
                            ? 'bg-green-100 text-green-600'
                            : 'bg-blue-100 text-blue-600',
                      ]"
                    >
                      {{ trade.type === "B" ? "买入" : trade.type === "S" ? "卖出" : "做T" }}
                    </span>
                    <span class="font-medium">{{ trade.stock_name || trade.stock_code }}</span>
                    <span class="text-sm text-slate-400">{{ trade.stock_code }}</span>
                  </div>
                  <div class="mt-1 text-sm text-slate-500">
                    {{ trade.date }} {{ trade.time }} | 价格: {{ trade.price }} | 数量:
                    {{ trade.quantity }}股
                  </div>
                  <div class="mt-1 truncate text-xs text-slate-400">
                    {{ trade.reason }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 摘要 -->
            <div v-if="summary" class="mt-4 rounded-lg bg-blue-50 p-3">
              <p class="text-sm text-blue-700">{{ summary }}</p>
            </div>
          </div>
        </div>

        <!-- 步骤4: 导入中 -->
        <div v-else-if="step === 4" class="flex flex-col items-center justify-center py-12">
          <div class="mb-4 h-10 w-10 animate-spin rounded-full border-b-2 border-blue-500"></div>
          <p class="text-slate-600">正在导入交易记录...</p>
        </div>

        <!-- 步骤5: 完成 -->
        <div v-else-if="step === 5" class="py-8 text-center">
          <div class="mb-4 text-5xl text-green-500">✓</div>
          <p class="text-lg font-medium">导入完成</p>
          <p class="mt-2 text-slate-500">成功导入 {{ importedCount }} 条交易记录</p>
        </div>

        <!-- 错误状态 -->
        <div v-if="error" class="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
          {{ error }}
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="flex justify-end gap-2 border-t border-slate-200 p-4">
        <button
          @click="$emit('close')"
          class="rounded-lg px-4 py-2 text-slate-600 hover:bg-slate-100"
        >
          {{ step === 5 ? "关闭" : "取消" }}
        </button>

        <button
          v-if="step === 1"
          @click="startAnalysis"
          :disabled="!settings.ai_provider || !settings.ai_api_key"
          class="rounded-lg bg-blue-500 px-4 py-2 text-white hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-50"
        >
          开始分析
        </button>

        <button
          v-else-if="step === 3 && extractedTrades.length > 0"
          @click="importTrades"
          :disabled="selectedTrades.length === 0"
          class="rounded-lg bg-blue-500 px-4 py-2 text-white hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-50"
        >
          导入选中 ({{ selectedTrades.length }})
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue"
import { getSettings, convertNoteToTrades, addTradeRecord } from "../api"

const props = defineProps<{
  content: string
}>()

const emit = defineEmits<{
  close: []
  converted: []
}>()

// 状态
const step = ref(1) // 1=配置确认, 2=分析中, 3=确认结果, 4=导入中, 5=完成
const settings = ref<Record<string, any>>({})
const extractedTrades = ref<any[]>([])
const selectedTrades = ref<number[]>([])
const summary = ref("")
const error = ref("")
const importedCount = ref(0)

// 加载设置
const loadSettings = async () => {
  try {
    const res = await getSettings()
    if (res.status === "success" && res.settings) {
      settings.value = res.settings
    }
  } catch (e) {
    console.error("加载设置失败:", e)
  }
}

// 开始分析
const startAnalysis = async () => {
  error.value = ""
  step.value = 2

  try {
    const res = await convertNoteToTrades({
      content: props.content,
      provider: settings.value.ai_provider,
      api_key: settings.value.ai_api_key,
      model: settings.value.ai_model,
      proxy: settings.value.ai_proxy,
    })

    if (res.status === "success") {
      extractedTrades.value = res.trades || []
      summary.value = res.summary || ""
      // 默认全选
      selectedTrades.value = extractedTrades.value.map((_, i) => i)
      step.value = 3
    } else {
      error.value = res.message || "分析失败"
      step.value = 1
    }
  } catch (e: any) {
    error.value = e.message || "分析失败"
    step.value = 1
  }
}

// 格式化股票代码（添加前缀）
const formatStockCode = (code: string): string => {
  // 如果已经有前缀，直接返回小写
  if (code.toLowerCase().startsWith("sz") || code.toLowerCase().startsWith("sh")) {
    return code.toLowerCase()
  }
  // 根据代码规则添加前缀
  const numCode = code.replace(/\D/g, "")
  if (numCode.startsWith("6")) {
    return `sh${numCode}`
  } else {
    return `sz${numCode}`
  }
}

// 导入交易记录
const importTrades = async () => {
  step.value = 4
  error.value = ""
  importedCount.value = 0

  try {
    for (const idx of selectedTrades.value) {
      const trade = extractedTrades.value[idx]

      // 构建交易时间
      const tradeTime = `${trade.date} ${trade.time || "09:30"}`

      // 格式化股票代码
      const stockCode = formatStockCode(trade.stock_code)

      // 添加交易记录
      await addTradeRecord({
        stock_code: stockCode,
        stock_name: trade.stock_name,
        type: trade.type,
        price: trade.price,
        quantity: trade.quantity,
        reason: trade.reason || "",
        trade_time: tradeTime,
      })

      importedCount.value++
    }

    step.value = 5
    emit("converted")
  } catch (e: any) {
    error.value = e.message || "导入失败"
    step.value = 3
  }
}

onMounted(() => {
  loadSettings()
})
</script>
