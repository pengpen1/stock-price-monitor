<template>
  <Teleport to="body">
    <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center">
      <!-- 遮罩 -->
      <div class="absolute inset-0 bg-black/50" @click="close"></div>

      <!-- 弹窗内容 -->
      <div class="relative max-h-[90vh] w-[420px] overflow-hidden rounded-2xl bg-white shadow-2xl">
        <!-- 头部 -->
        <div class="border-b border-slate-100 px-6 py-4">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-slate-800">实盘模拟</h3>
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
          <p class="mt-1 text-sm text-slate-500">基于历史数据进行模拟交易练习</p>
        </div>

        <!-- 内容 -->
        <div class="space-y-5 px-6 py-5">
          <!-- 股票信息 -->
          <div class="rounded-lg bg-slate-50 p-4">
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium text-slate-800">{{ stockName }}</div>
                <div class="text-sm text-slate-500">{{ stockCode }}</div>
              </div>
              <div class="text-right">
                <div
                  class="text-lg font-semibold"
                  :class="priceChange >= 0 ? 'text-red-500' : 'text-green-500'"
                >
                  {{ currentPrice }}
                </div>
                <div class="text-sm" :class="priceChange >= 0 ? 'text-red-500' : 'text-green-500'">
                  {{ priceChange >= 0 ? "+" : "" }}{{ priceChange }}%
                </div>
              </div>
            </div>
          </div>

          <!-- 模拟天数 -->
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">
              模拟天数：<span class="font-semibold text-blue-600">{{ totalDays }}</span>
              个交易日
            </label>
            <input
              type="range"
              v-model.number="totalDays"
              min="7"
              max="50"
              step="1"
              class="h-2 w-full cursor-pointer appearance-none rounded-lg bg-slate-200 accent-blue-500"
            />
            <div class="mt-1 flex justify-between text-xs text-slate-400">
              <span>7天</span>
              <span>50天</span>
            </div>
          </div>

          <!-- 初始资金 -->
          <div>
            <label class="mb-2 block text-sm font-medium text-slate-700">初始资金</label>
            <div class="grid grid-cols-3 gap-2">
              <button
                v-for="amount in capitalOptions"
                :key="amount"
                @click="initialCapital = amount"
                :class="
                  initialCapital === amount
                    ? 'border-blue-500 bg-blue-500 text-white'
                    : 'border-slate-200 bg-white text-slate-700 hover:border-blue-300'
                "
                class="rounded-lg border px-3 py-2 text-sm font-medium transition-colors"
              >
                {{ formatCapital(amount) }}
              </button>
            </div>
          </div>

          <!-- 说明 -->
          <div class="rounded-lg border border-amber-200 bg-amber-50 p-3">
            <div class="flex gap-2">
              <svg
                class="mt-0.5 h-5 w-5 flex-shrink-0 text-amber-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <div class="text-sm text-amber-800">
                <p class="mb-1 font-medium">模拟规则</p>
                <ul class="space-y-0.5 text-xs text-amber-700">
                  <li>• 时间将回到 {{ totalDays }} 个交易日前</li>
                  <li>• 每天可选择买入、卖出或跳过</li>
                  <li>• 结束后 AI 将对您的操作进行评分</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部按钮 -->
        <div class="flex gap-3 border-t border-slate-100 px-6 py-4">
          <button
            @click="close"
            class="flex-1 rounded-lg bg-slate-100 px-4 py-2.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-200"
          >
            取消
          </button>
          <button
            @click="startSimulation"
            :disabled="loading"
            class="flex-1 rounded-lg bg-blue-500 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-600 disabled:opacity-50"
          >
            {{ loading ? "创建中..." : "开始模拟" }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed } from "vue"
import { createSimulation } from "../api"

const props = defineProps<{
  visible: boolean
  stockCode: string
  stockName: string
  currentPrice: string
  priceChange: number
}>()

const emit = defineEmits(["update:visible", "start"])

const totalDays = ref(20)
const initialCapital = ref(1000000)
const loading = ref(false)

const capitalOptions = [500000, 1000000, 2000000]

const formatCapital = (amount: number) => {
  if (amount >= 10000) {
    return amount / 10000 + "万"
  }
  return amount.toString()
}

const close = () => {
  emit("update:visible", false)
}

const startSimulation = async () => {
  loading.value = true
  try {
    const res = await createSimulation({
      stock_code: props.stockCode,
      stock_name: props.stockName,
      total_days: totalDays.value,
      initial_capital: initialCapital.value,
    })

    if (res.status === "success") {
      emit("start", res.session)
      close()
    } else {
      alert(res.message || "创建失败")
    }
  } catch (e: any) {
    alert(e.message || "创建失败")
  } finally {
    loading.value = false
  }
}
</script>
