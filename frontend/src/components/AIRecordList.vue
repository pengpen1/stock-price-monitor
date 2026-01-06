<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    @click.self="close"
  >
    <div
      class="flex max-h-[85vh] w-[750px] flex-col overflow-hidden rounded-xl border border-gray-700 bg-gray-900 shadow-2xl"
    >
      <!-- 头部 -->
      <div class="flex items-center justify-between border-b border-gray-700 bg-gray-800 p-4">
        <div class="flex items-center gap-2">
          <h3 class="text-lg font-semibold text-white">AI 分析历史</h3>
          <span class="text-sm text-gray-400">{{ stockCode }}</span>
        </div>
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

      <!-- 记录列表 -->
      <div class="flex-1 overflow-auto p-4">
        <div v-if="loading" class="flex items-center justify-center py-16 text-gray-400">
          加载中...
        </div>
        <div
          v-else-if="records.length === 0"
          class="flex flex-col items-center justify-center py-16 text-gray-400"
        >
          <p>暂无 AI 分析记录</p>
          <p class="mt-1 text-sm">进行快速分析或精准分析后会自动保存</p>
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="record in records"
            :key="record.id"
            class="hover:bg-gray-750 cursor-pointer rounded-lg bg-gray-800 p-4 transition-colors"
            @click="toggleExpand(record.id)"
          >
            <div class="flex items-start justify-between">
              <div class="flex items-center gap-3">
                <!-- 信号标签 -->
                <span
                  :class="[
                    'rounded-md px-2.5 py-1 text-sm font-bold whitespace-nowrap',
                    signalStyles[record.signal],
                  ]"
                >
                  {{ signalLabels[record.signal] }}
                </span>
                <div>
                  <div class="text-gray-200">{{ record.summary }}</div>
                  <div class="mt-1 text-xs text-gray-500">
                    {{ record.datetime }} ·
                    {{ record.analysis_type === "fast" ? "快速分析" : "精准分析" }}
                    · {{ record.model }}
                  </div>
                </div>
              </div>
              <!-- 展开图标 -->
              <span class="text-sm text-gray-500">
                {{ expandedId === record.id ? "▼" : "▶" }}
              </span>
            </div>

            <!-- 展开的完整分析 -->
            <div v-if="expandedId === record.id" class="mt-4 border-t border-gray-700 pt-4">
              <div
                class="rendered-markdown max-h-64 overflow-auto text-sm text-gray-300"
                v-html="renderMarkdown(record.full_result)"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部统计 -->
      <div v-if="records.length > 0" class="border-t border-gray-700 bg-gray-800 p-4">
        <div class="flex justify-between text-sm text-gray-400">
          <span>共 {{ records.length }} 条分析记录</span>
          <span>
            看涨 {{ bullishCount }} · 谨慎 {{ cautiousCount }} · 看跌
            {{ bearishCount }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue"
import { marked } from "marked"
import { getStockAIRecords, type AIRecord } from "../api"

const props = defineProps<{
  visible: boolean
  stockCode: string
}>()

const emit = defineEmits(["update:visible"])

const loading = ref(false)
const records = ref<AIRecord[]>([])
const expandedId = ref<string | null>(null)

const signalLabels: Record<string, string> = {
  bullish: "看涨",
  cautious: "谨慎",
  bearish: "看跌",
}

const signalStyles: Record<string, string> = {
  bullish: "bg-red-900/50 text-red-300",
  cautious: "bg-yellow-900/50 text-yellow-300",
  bearish: "bg-green-900/50 text-green-300",
}

// 统计
const bullishCount = computed(() => records.value.filter((r) => r.signal === "bullish").length)
const cautiousCount = computed(() => records.value.filter((r) => r.signal === "cautious").length)
const bearishCount = computed(() => records.value.filter((r) => r.signal === "bearish").length)

// 监听弹窗打开
watch(
  () => props.visible,
  (val) => {
    if (val) {
      loadRecords()
      expandedId.value = null
    }
  },
)

const loadRecords = async () => {
  loading.value = true
  try {
    const res = await getStockAIRecords(props.stockCode)
    if (res.status === "success") {
      records.value = res.records || []
    }
  } catch (e) {
    console.error("加载 AI 分析记录失败:", e)
  } finally {
    loading.value = false
  }
}

const close = () => {
  emit("update:visible", false)
}

const toggleExpand = (id: string) => {
  expandedId.value = expandedId.value === id ? null : id
}

const renderMarkdown = (text: string) => {
  return marked.parse(text)
}
</script>

<style scoped>
.rendered-markdown :deep(h1),
.rendered-markdown :deep(h2),
.rendered-markdown :deep(h3) {
  color: #e5e7eb;
  margin-top: 0.5rem;
  margin-bottom: 0.25rem;
}
.rendered-markdown :deep(p) {
  margin-bottom: 0.5rem;
}
.rendered-markdown :deep(ul),
.rendered-markdown :deep(ol) {
  padding-left: 1.5rem;
  margin-bottom: 0.5rem;
}
.rendered-markdown :deep(code) {
  background-color: #374151;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}
</style>
