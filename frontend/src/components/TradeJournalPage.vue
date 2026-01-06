<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4">
    <div class="mx-auto max-w-7xl">
      <!-- 顶部 -->
      <div class="mb-4 rounded-xl bg-white p-4 shadow-sm">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <button
              @click="$emit('back')"
              class="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-700"
            >
              ← 返回
            </button>
            <h1 class="text-xl font-bold text-slate-800">交易日志</h1>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="showAnalysis = !showAnalysis"
              :class="showAnalysis ? 'bg-blue-500 text-white' : 'bg-slate-100 text-slate-600'"
              class="rounded-lg px-3 py-1.5 text-sm font-medium transition-all hover:opacity-90"
            >
              📊 风格分析
            </button>
            <button
              @click="exportMd"
              class="rounded-lg bg-slate-100 px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-200"
            >
              📤 导出 MD
            </button>
            <button
              @click="showImportModal = true"
              class="rounded-lg bg-slate-100 px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-200"
            >
              📥 导入 MD
            </button>
          </div>
        </div>
      </div>

      <div class="flex gap-4">
        <!-- 左侧：股票筛选 -->
        <div class="w-48 flex-shrink-0">
          <div class="rounded-xl bg-white p-3 shadow-sm">
            <h3 class="mb-3 text-sm font-semibold text-slate-700">股票筛选</h3>
            <div class="space-y-1">
              <button
                @click="selectedStock = ''"
                :class="
                  selectedStock === ''
                    ? 'border-blue-200 bg-blue-50 text-blue-600'
                    : 'hover:bg-slate-50'
                "
                class="w-full rounded-lg border border-transparent px-3 py-2 text-left text-sm transition-colors"
              >
                全部股票
              </button>
              <button
                v-for="code in stockCodes"
                :key="code"
                @click="selectedStock = code"
                :class="
                  selectedStock === code
                    ? 'border-blue-200 bg-blue-50 text-blue-600'
                    : 'hover:bg-slate-50'
                "
                class="w-full truncate rounded-lg border border-transparent px-3 py-2 text-left text-sm transition-colors"
              >
                {{ code }}
              </button>
            </div>
          </div>
        </div>

        <!-- 右侧：内容区 -->
        <div class="flex-1 space-y-4">
          <!-- 风格分析面板 -->
          <div v-if="showAnalysis && analysis" class="rounded-xl bg-white p-4 shadow-sm">
            <h3 class="mb-4 text-sm font-semibold text-slate-700">交易风格分析</h3>
            <div class="grid grid-cols-3 gap-4">
              <!-- 分级统计 -->
              <div class="rounded-lg bg-slate-50 p-4">
                <h4 class="mb-3 text-xs text-slate-500">交易分级分布</h4>
                <div class="space-y-2">
                  <div
                    v-for="(count, level) in analysis.level_stats"
                    :key="level"
                    class="flex items-center gap-2"
                  >
                    <span class="w-20 text-sm">{{ levelLabels[level] }}</span>
                    <div class="h-4 flex-1 overflow-hidden rounded-full bg-slate-200">
                      <div
                        class="h-full rounded-full bg-blue-500"
                        :style="{
                          width: (count / analysis.total_records) * 100 + '%',
                        }"
                      ></div>
                    </div>
                    <span class="w-8 text-xs text-slate-500">{{ count }}</span>
                  </div>
                </div>
                <div class="mt-3 border-t border-slate-200 pt-3">
                  <h5 class="mb-2 text-xs text-slate-500">各级胜率</h5>
                  <div class="flex gap-4 text-sm">
                    <span v-for="(rate, level) in analysis.level_win_rate" :key="level">
                      {{ levelLabels[level] }}:
                      <span
                        class="font-medium"
                        :class="rate >= 50 ? 'text-red-500' : 'text-green-500'"
                        >{{ rate }}%</span
                      >
                    </span>
                  </div>
                </div>
              </div>

              <!-- 心态统计 -->
              <div class="rounded-lg bg-slate-50 p-4">
                <h4 class="mb-3 text-xs text-slate-500">心态分布</h4>
                <div class="space-y-2">
                  <div
                    v-for="(count, mood) in analysis.mood_stats"
                    :key="mood"
                    class="flex items-center gap-2"
                  >
                    <span class="w-16 text-sm">{{ moodLabels[mood] }}</span>
                    <div class="h-4 flex-1 overflow-hidden rounded-full bg-slate-200">
                      <div
                        class="h-full rounded-full"
                        :class="moodColors[mood]"
                        :style="{
                          width: (count / analysis.total_records) * 100 + '%',
                        }"
                      ></div>
                    </div>
                    <span class="w-8 text-xs text-slate-500">{{ count }}</span>
                  </div>
                </div>
              </div>

              <!-- 心态胜率 -->
              <div class="rounded-lg bg-slate-50 p-4">
                <h4 class="mb-3 text-xs text-slate-500">心态与胜率关系</h4>
                <div class="space-y-2">
                  <div
                    v-for="(rate, mood) in analysis.mood_win_rate"
                    :key="mood"
                    class="flex items-center justify-between"
                  >
                    <span class="text-sm">{{ moodLabels[mood] }}</span>
                    <span
                      class="font-medium"
                      :class="rate >= 50 ? 'text-red-500' : 'text-green-500'"
                      >{{ rate }}%</span
                    >
                  </div>
                </div>
                <div class="mt-3 border-t border-slate-200 pt-3 text-xs text-slate-500">
                  💡 保持平静心态通常能获得更好的交易结果
                </div>
              </div>
            </div>
          </div>

          <!-- 交易记录列表 -->
          <div class="rounded-xl bg-white shadow-sm">
            <div class="border-b border-slate-100 p-4">
              <div class="flex items-center justify-between">
                <h3 class="text-sm font-semibold text-slate-700">
                  交易记录
                  <span class="font-normal text-slate-400">({{ filteredRecords.length }}条)</span>
                </h3>
              </div>
            </div>

            <div v-if="loading" class="p-8 text-center text-slate-400">加载中...</div>
            <div v-else-if="filteredRecords.length === 0" class="p-8 text-center text-slate-400">
              暂无交易记录
            </div>
            <div v-else class="divide-y divide-slate-100">
              <div
                v-for="record in filteredRecords"
                :key="record.id"
                class="p-4 transition-colors hover:bg-slate-50"
              >
                <div class="flex items-start gap-4">
                  <!-- 左侧：类型标识 -->
                  <div
                    :class="typeColors[record.type]"
                    class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg text-sm font-bold text-white"
                  >
                    {{ record.type }}
                  </div>

                  <!-- 中间：主要信息 -->
                  <div class="min-w-0 flex-1">
                    <div class="mb-1 flex items-center gap-2">
                      <span class="font-medium text-slate-800">{{
                        record.stock_name || record.stock_code
                      }}</span>
                      <span class="text-xs text-slate-400">{{ record.stock_code }}</span>
                      <span
                        :class="levelBadgeClass[record.level || 2]"
                        class="rounded px-1.5 py-0.5 text-xs"
                      >
                        {{ levelLabels[record.level || 2] }}
                      </span>
                      <span class="rounded bg-slate-100 px-1.5 py-0.5 text-xs">
                        {{ moodEmojis[record.mood || "calm"] }}
                        {{ moodLabels[record.mood || "calm"] }}
                      </span>
                    </div>
                    <div class="mb-1 text-sm text-slate-600">
                      ¥{{ record.price.toFixed(2) }} × {{ record.quantity }}手
                      <span class="mx-2 text-slate-400">|</span>
                      {{ record.trade_time }}
                    </div>
                    <div class="line-clamp-2 text-sm text-slate-500">
                      {{ record.reason }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 导入弹窗 -->
    <Teleport to="body">
      <div v-if="showImportModal" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/50" @click="showImportModal = false"></div>
        <div
          class="relative flex max-h-[85vh] w-[700px] flex-col overflow-hidden rounded-2xl bg-white shadow-2xl"
        >
          <div class="flex items-center justify-between border-b border-slate-100 px-6 py-4">
            <h3 class="text-lg font-semibold text-slate-800">导入 Markdown</h3>
            <button
              @click="showImportModal = false"
              class="p-1 text-slate-400 hover:text-slate-600"
            >
              ✕
            </button>
          </div>
          <div class="flex-1 space-y-4 overflow-auto p-6">
            <!-- 格式说明 -->
            <div class="rounded-lg bg-slate-50 p-4 text-sm">
              <div class="mb-2 font-medium text-slate-700">📋 导入格式说明</div>
              <div class="space-y-1 text-slate-500">
                <p>请使用以下格式（与导出格式一致）：</p>
                <pre
                  class="mt-2 overflow-x-auto rounded border border-slate-200 bg-white p-3 font-mono text-xs"
                >
### 股票名（股票代码）- 买入/卖出/做T

- **时间**：2025-01-01 10:30
- **价格**：¥10.50
- **数量**：10 手
- **心态**：😌 平静
- **分级**：⭐ 一级（85%+）
- **理由**：看好后市走势</pre
                >
                <p class="mt-2 text-xs text-slate-400">💡 提示：可以先导出一份作为模板参考</p>
              </div>
            </div>
            <textarea
              v-model="importContent"
              rows="12"
              placeholder="粘贴 Markdown 内容..."
              class="w-full resize-none rounded-lg border border-slate-200 px-3 py-2 font-mono text-sm focus:border-blue-400 focus:outline-none"
            ></textarea>
          </div>
          <div class="flex justify-end gap-3 border-t border-slate-100 px-6 py-4">
            <button
              @click="showImportModal = false"
              class="rounded-lg bg-slate-100 px-4 py-2 text-slate-600 hover:bg-slate-200"
            >
              取消
            </button>
            <button
              @click="importMd"
              :disabled="!importContent.trim()"
              class="rounded-lg bg-blue-500 px-4 py-2 text-white hover:bg-blue-600 disabled:opacity-50"
            >
              导入
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import {
  getTradeRecords,
  getTradeStockCodes,
  getTradeStyleAnalysis,
  exportTradeRecordsMd,
  importTradeRecordsMd,
  type TradeRecord,
  type TradeStyleAnalysis,
} from "../api"

const emit = defineEmits(["back"])

const loading = ref(true)
const records = ref<TradeRecord[]>([])
const stockCodes = ref<string[]>([])
const selectedStock = ref("")
const showAnalysis = ref(false)
const analysis = ref<TradeStyleAnalysis | null>(null)

const showImportModal = ref(false)
const importContent = ref("")

// 标签映射
const levelLabels: Record<number, string> = { 1: "一级", 2: "二级", 3: "三级" }
const moodLabels: Record<string, string> = {
  calm: "平静",
  anxious: "焦虑",
  uneasy: "不安",
  panic: "慌张",
  fear: "恐惧",
  excited: "亢奋",
}
const moodEmojis: Record<string, string> = {
  calm: "😌",
  anxious: "😰",
  uneasy: "😟",
  panic: "😱",
  fear: "😨",
  excited: "🤩",
}
const moodColors: Record<string, string> = {
  calm: "bg-blue-500",
  anxious: "bg-yellow-500",
  uneasy: "bg-amber-500",
  panic: "bg-orange-500",
  fear: "bg-red-500",
  excited: "bg-purple-500",
}
const typeColors: Record<string, string> = {
  B: "bg-red-500",
  S: "bg-green-500",
  T: "bg-blue-500",
}
const levelBadgeClass: Record<number, string> = {
  1: "bg-green-100 text-green-600",
  2: "bg-blue-100 text-blue-600",
  3: "bg-orange-100 text-orange-600",
}

// 筛选后的记录
const filteredRecords = computed(() => {
  if (!selectedStock.value) return records.value
  return records.value.filter(
    (r) => r.stock_code === selectedStock.value || r.stock_code.endsWith(selectedStock.value),
  )
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const [recordsRes, codesRes] = await Promise.all([
      getTradeRecords(undefined, 1000),
      getTradeStockCodes(),
    ])
    if (recordsRes.status === "success") {
      records.value = recordsRes.records || []
    }
    if (codesRes.status === "success") {
      stockCodes.value = codesRes.codes || []
    }
  } catch (e) {
    console.error("加载数据失败:", e)
  } finally {
    loading.value = false
  }
}

// 加载分析数据
const loadAnalysis = async () => {
  try {
    const res = await getTradeStyleAnalysis(selectedStock.value || undefined)
    if (res.status === "success") {
      analysis.value = res.analysis
    }
  } catch (e) {
    console.error("加载分析失败:", e)
  }
}

// 导出 MD
const exportMd = async () => {
  try {
    const res = await exportTradeRecordsMd(selectedStock.value || undefined)
    if (res.status === "success") {
      const blob = new Blob([res.content], { type: "text/markdown" })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `交易日志_${selectedStock.value || "全部"}_${new Date().toISOString().slice(0, 10)}.md`
      a.click()
      URL.revokeObjectURL(url)
    }
  } catch (e) {
    console.error("导出失败:", e)
  }
}

// 导入 MD
const importMd = async () => {
  if (!importContent.value.trim()) return
  try {
    const res = await importTradeRecordsMd(importContent.value)
    if (res.status === "success") {
      alert(`成功导入 ${res.imported} 条记录`)
      showImportModal.value = false
      importContent.value = ""
      loadData()
    }
  } catch (e) {
    console.error("导入失败:", e)
  }
}

onMounted(() => {
  loadData()
  loadAnalysis()
})
</script>
