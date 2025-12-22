<template>
  <Teleport to="body">
    <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center">
      <!-- 遮罩 -->
      <div class="absolute inset-0 bg-black/50" @click="close"></div>
      
      <!-- 弹窗内容 -->
      <div class="relative bg-white rounded-2xl shadow-2xl w-[420px] max-h-[90vh] overflow-hidden">
        <!-- 头部 -->
        <div class="px-6 py-4 border-b border-slate-100">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-slate-800">实盘模拟</h3>
            <button @click="close" class="p-1 text-slate-400 hover:text-slate-600 rounded">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <p class="text-sm text-slate-500 mt-1">基于历史数据进行模拟交易练习</p>
        </div>
        
        <!-- 内容 -->
        <div class="px-6 py-5 space-y-5">
          <!-- 股票信息 -->
          <div class="bg-slate-50 rounded-lg p-4">
            <div class="flex items-center justify-between">
              <div>
                <div class="font-medium text-slate-800">{{ stockName }}</div>
                <div class="text-sm text-slate-500">{{ stockCode }}</div>
              </div>
              <div class="text-right">
                <div class="text-lg font-semibold" :class="priceChange >= 0 ? 'text-red-500' : 'text-green-500'">
                  {{ currentPrice }}
                </div>
                <div class="text-sm" :class="priceChange >= 0 ? 'text-red-500' : 'text-green-500'">
                  {{ priceChange >= 0 ? '+' : '' }}{{ priceChange }}%
                </div>
              </div>
            </div>
          </div>
          
          <!-- 模拟天数 -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">
              模拟天数：<span class="text-blue-600 font-semibold">{{ totalDays }}</span> 个交易日
            </label>
            <input type="range" v-model.number="totalDays" min="7" max="50" step="1"
              class="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-500">
            <div class="flex justify-between text-xs text-slate-400 mt-1">
              <span>7天</span>
              <span>50天</span>
            </div>
          </div>
          
          <!-- 初始资金 -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">初始资金</label>
            <div class="grid grid-cols-3 gap-2">
              <button v-for="amount in capitalOptions" :key="amount"
                @click="initialCapital = amount"
                :class="initialCapital === amount 
                  ? 'bg-blue-500 text-white border-blue-500' 
                  : 'bg-white text-slate-700 border-slate-200 hover:border-blue-300'"
                class="px-3 py-2 text-sm font-medium border rounded-lg transition-colors">
                {{ formatCapital(amount) }}
              </button>
            </div>
          </div>
          
          <!-- 说明 -->
          <div class="bg-amber-50 border border-amber-200 rounded-lg p-3">
            <div class="flex gap-2">
              <svg class="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <div class="text-sm text-amber-800">
                <p class="font-medium mb-1">模拟规则</p>
                <ul class="text-xs space-y-0.5 text-amber-700">
                  <li>• 时间将回到 {{ totalDays }} 个交易日前</li>
                  <li>• 每天可选择买入、卖出或跳过</li>
                  <li>• 结束后 AI 将对您的操作进行评分</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 底部按钮 -->
        <div class="px-6 py-4 border-t border-slate-100 flex gap-3">
          <button @click="close" 
            class="flex-1 px-4 py-2.5 text-sm font-medium text-slate-700 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors">
            取消
          </button>
          <button @click="startSimulation" :disabled="loading"
            class="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-blue-500 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50">
            {{ loading ? '创建中...' : '开始模拟' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { createSimulation } from '../api'

const props = defineProps<{
  visible: boolean
  stockCode: string
  stockName: string
  currentPrice: string
  priceChange: number
}>()

const emit = defineEmits(['update:visible', 'start'])

const totalDays = ref(20)
const initialCapital = ref(1000000)
const loading = ref(false)

const capitalOptions = [500000, 1000000, 2000000]

const formatCapital = (amount: number) => {
  if (amount >= 10000) {
    return (amount / 10000) + '万'
  }
  return amount.toString()
}

const close = () => {
  emit('update:visible', false)
}

const startSimulation = async () => {
  loading.value = true
  try {
    const res = await createSimulation({
      stock_code: props.stockCode,
      stock_name: props.stockName,
      total_days: totalDays.value,
      initial_capital: initialCapital.value
    })
    
    if (res.status === 'success') {
      emit('start', res.session)
      close()
    } else {
      alert(res.message || '创建失败')
    }
  } catch (e: any) {
    alert(e.message || '创建失败')
  } finally {
    loading.value = false
  }
}
</script>
