<template>
  <div v-if="visible" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm" @click.self="close">
    <div class="bg-white rounded-xl shadow-2xl w-[450px] max-h-[80vh] flex flex-col overflow-hidden">
      <!-- 头部 -->
      <div class="flex justify-between items-center p-4 border-b border-slate-100 bg-gradient-to-r from-blue-500 to-blue-600">
        <h3 class="text-lg font-semibold text-white">{{ isEdit ? '编辑交易记录' : '添加交易记录' }}</h3>
        <button @click="close" class="text-white/80 hover:text-white transition-colors p-1 rounded hover:bg-white/10">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 表单内容 -->
      <div class="flex-1 overflow-auto p-6 space-y-4">
        <!-- 交易类型 -->
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">交易类型</label>
          <div class="flex gap-2">
            <button 
              v-for="t in tradeTypes" :key="t.value"
              @click="form.type = t.value"
              :class="[
                'flex-1 py-2 px-4 rounded-lg font-medium transition-all',
                form.type === t.value 
                  ? t.activeClass 
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              ]"
            >
              {{ t.label }}
            </button>
          </div>
        </div>

        <!-- 买入/卖出价格（非做T模式） -->
        <div v-if="form.type !== 'T'">
          <label class="block text-sm font-medium text-slate-700 mb-2">成交价格</label>
          <div class="relative">
            <span class="absolute left-3 top-2.5 text-slate-400">¥</span>
            <input 
              v-model.number="form.price" 
              type="number" 
              step="0.01"
              class="w-full border border-slate-200 rounded-lg pl-8 pr-3 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
              placeholder="0.00"
            >
          </div>
        </div>

        <!-- 做T模式：买入和卖出价格 -->
        <div v-if="form.type === 'T'" class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">买入价格</label>
            <div class="relative">
              <span class="absolute left-3 top-2.5 text-slate-400">¥</span>
              <input 
                v-model.number="form.buy_price" 
                type="number" 
                step="0.01"
                class="w-full border border-slate-200 rounded-lg pl-8 pr-3 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                placeholder="0.00"
              >
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-2">卖出价格</label>
            <div class="relative">
              <span class="absolute left-3 top-2.5 text-slate-400">¥</span>
              <input 
                v-model.number="form.sell_price" 
                type="number" 
                step="0.01"
                class="w-full border border-slate-200 rounded-lg pl-8 pr-3 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                placeholder="0.00"
              >
            </div>
          </div>
        </div>

        <!-- 做T盈亏提示 -->
        <div v-if="form.type === 'T' && form.buy_price > 0 && form.sell_price > 0" class="text-sm">
          <span :class="tProfit >= 0 ? 'text-red-500' : 'text-green-500'">
            做T {{ tProfit >= 0 ? '盈利' : '亏损' }}: ¥{{ Math.abs(tProfit).toFixed(2) }}/手
          </span>
        </div>

        <!-- 手数 -->
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">手数（1手=100股）</label>
          <input 
            v-model.number="form.quantity" 
            type="number"
            class="w-full border border-slate-200 rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            placeholder="0"
          >
        </div>

        <!-- 交易时间 -->
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">交易时间</label>
          <input 
            v-model="form.trade_time" 
            type="datetime-local"
            class="w-full border border-slate-200 rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          >
        </div>

        <!-- 操作原因 -->
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">操作原因</label>
          <textarea 
            v-model="form.reason" 
            rows="3"
            class="w-full border border-slate-200 rounded-lg px-3 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none"
            placeholder="记录你的交易逻辑和原因..."
          ></textarea>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="p-4 border-t border-slate-100 bg-slate-50 flex justify-end gap-3">
        <button @click="close" class="px-4 py-2 text-slate-600 hover:bg-slate-200 rounded-lg transition-colors">
          取消
        </button>
        <button 
          @click="submit" 
          :disabled="!isValid || loading"
          class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ loading ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { addTradeRecord, updateTradeRecord, type TradeRecord } from '../api'

const props = defineProps<{
  visible: boolean
  stockCode: string
  editRecord?: TradeRecord | null
}>()

const emit = defineEmits(['update:visible', 'saved'])

const loading = ref(false)
const isEdit = computed(() => !!props.editRecord)

const tradeTypes: { value: 'B' | 'S' | 'T'; label: string; activeClass: string }[] = [
  { value: 'B', label: '买入 B', activeClass: 'bg-red-500 text-white' },
  { value: 'S', label: '卖出 S', activeClass: 'bg-green-500 text-white' },
  { value: 'T', label: '做T', activeClass: 'bg-blue-500 text-white' },
]

const form = ref({
  type: 'B' as 'B' | 'S' | 'T',
  price: 0,
  buy_price: 0,  // 做T买入价
  sell_price: 0, // 做T卖出价
  quantity: 1,
  trade_time: '',
  reason: ''
})

// 做T盈亏计算（每手）
const tProfit = computed(() => {
  if (form.value.type !== 'T') return 0
  return (form.value.sell_price - form.value.buy_price) * 100
})

// 表单验证
const isValid = computed(() => {
  const hasReason = form.value.reason.trim()
  const hasQuantity = form.value.quantity > 0
  
  if (form.value.type === 'T') {
    // 做T需要买入和卖出价格都填写
    return form.value.buy_price > 0 && form.value.sell_price > 0 && hasQuantity && hasReason
  }
  return form.value.price > 0 && hasQuantity && hasReason
})

// 监听弹窗打开，初始化表单
watch(() => props.visible, (val) => {
  if (val) {
    if (props.editRecord) {
      // 编辑模式 - 解析做T的买卖价格
      const record = props.editRecord
      let buyPrice = 0, sellPrice = 0
      if (record.type === 'T' && record.reason) {
        // 尝试从reason中解析买卖价格（格式：买入:xx 卖出:xx ...）
        const buyMatch = record.reason.match(/买入[:：](\d+\.?\d*)/)
        const sellMatch = record.reason.match(/卖出[:：](\d+\.?\d*)/)
        if (buyMatch) buyPrice = parseFloat(buyMatch[1])
        if (sellMatch) sellPrice = parseFloat(sellMatch[1])
      }
      form.value = {
        type: record.type,
        price: record.price,
        buy_price: buyPrice || record.price,
        sell_price: sellPrice || record.price,
        quantity: record.quantity,
        trade_time: record.trade_time.replace(' ', 'T'),
        reason: record.reason
      }
    } else {
      // 新增模式
      const now = new Date()
      const timeStr = now.toISOString().slice(0, 16)
      form.value = {
        type: 'B',
        price: 0,
        buy_price: 0,
        sell_price: 0,
        quantity: 1,
        trade_time: timeStr,
        reason: ''
      }
    }
  }
})

const close = () => {
  emit('update:visible', false)
}

const submit = async () => {
  if (!isValid.value) return
  
  loading.value = true
  try {
    // 构建提交数据
    let price = form.value.price
    let reason = form.value.reason
    
    // 做T模式：价格取平均值，reason前面加上买卖价格信息
    if (form.value.type === 'T') {
      price = (form.value.buy_price + form.value.sell_price) / 2
      const profitInfo = tProfit.value >= 0 ? `盈利${tProfit.value.toFixed(2)}元/手` : `亏损${Math.abs(tProfit.value).toFixed(2)}元/手`
      reason = `买入:${form.value.buy_price} 卖出:${form.value.sell_price} ${profitInfo} | ${form.value.reason}`
    }
    
    const data = {
      type: form.value.type,
      price,
      quantity: form.value.quantity,
      reason,
      stock_code: props.stockCode,
      trade_time: form.value.trade_time.replace('T', ' ')
    }
    
    if (isEdit.value && props.editRecord) {
      await updateTradeRecord(props.editRecord.id, data)
    } else {
      await addTradeRecord(data)
    }
    
    emit('saved')
    close()
  } catch (e) {
    console.error('保存交易记录失败:', e)
  } finally {
    loading.value = false
  }
}
</script>
