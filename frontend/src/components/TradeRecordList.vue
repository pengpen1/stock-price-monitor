<template>
  <div v-if="visible" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm" @click.self="close">
    <div class="bg-white rounded-xl shadow-2xl w-[700px] max-h-[85vh] flex flex-col overflow-hidden">
      <!-- 头部 -->
      <div class="flex justify-between items-center p-4 border-b border-slate-100 bg-gradient-to-r from-blue-500 to-blue-600">
        <div class="flex items-center gap-2">
          <h3 class="text-lg font-semibold text-white">交易记录</h3>
          <span class="text-white/70 text-sm">{{ stockCode }}</span>
        </div>
        <div class="flex items-center gap-2">
          <button @click="openAddModal" class="px-3 py-1.5 bg-white/20 text-white rounded-lg hover:bg-white/30 transition-colors text-sm">
            + 添加记录
          </button>
          <button @click="close" class="text-white/80 hover:text-white transition-colors p-1 rounded hover:bg-white/10">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- 记录列表 -->
      <div class="flex-1 overflow-auto p-4">
        <div v-if="loading" class="flex items-center justify-center py-16 text-slate-400">
          加载中...
        </div>
        <div v-else-if="records.length === 0" class="flex flex-col items-center justify-center py-16 text-slate-400">
          <p>暂无交易记录</p>
          <button @click="openAddModal" class="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm">
            添加第一条记录
          </button>
        </div>
        <div v-else class="space-y-3">
          <div 
            v-for="record in records" 
            :key="record.id"
            class="bg-slate-50 rounded-lg p-4 hover:bg-slate-100 transition-colors"
          >
            <div class="flex items-start justify-between">
              <div class="flex items-center gap-3">
                <!-- 交易类型标签 -->
                <span :class="[
                  'px-2.5 py-1 rounded-md text-sm font-bold',
                  record.type === 'B' ? 'bg-red-100 text-red-600' :
                  record.type === 'S' ? 'bg-green-100 text-green-600' :
                  'bg-blue-100 text-blue-600'
                ]">
                  {{ typeLabels[record.type] }}
                </span>
                <div>
                  <div class="font-medium text-slate-800">
                    ¥{{ record.price.toFixed(2) }} × {{ record.quantity }}手
                  </div>
                  <div class="text-xs text-slate-400">{{ record.trade_time }}</div>
                </div>
              </div>
              <!-- 操作按钮 -->
              <div class="flex items-center gap-1">
                <button @click="editRecord(record)" class="p-1.5 text-slate-400 hover:text-blue-500 hover:bg-blue-50 rounded transition-colors" title="编辑">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button @click="confirmDelete(record)" class="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors" title="删除">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
            <!-- 操作原因 -->
            <div class="mt-2 text-sm text-slate-600 bg-white rounded p-2 border border-slate-100">
              {{ record.reason }}
            </div>
          </div>
        </div>
      </div>

      <!-- 底部统计 -->
      <div v-if="records.length > 0" class="p-4 border-t border-slate-100 bg-slate-50">
        <div class="flex justify-between text-sm text-slate-500">
          <span>共 {{ records.length }} 条记录</span>
          <span>
            买入 {{ buyCount }} 次 · 卖出 {{ sellCount }} 次 · 做T {{ tCount }} 次
          </span>
        </div>
      </div>
    </div>
  </div>

  <!-- 添加/编辑弹窗 -->
  <TradeRecordModal 
    v-model:visible="showEditModal" 
    :stock-code="stockCode"
    :edit-record="editingRecord"
    @saved="loadRecords"
  />
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { getStockTradeRecords, deleteTradeRecord, type TradeRecord } from '../api'
import TradeRecordModal from './TradeRecordModal.vue'

const props = defineProps<{
  visible: boolean
  stockCode: string
}>()

const emit = defineEmits(['update:visible'])

const loading = ref(false)
const records = ref<TradeRecord[]>([])
const showEditModal = ref(false)
const editingRecord = ref<TradeRecord | null>(null)

const typeLabels: Record<string, string> = {
  'B': '买入 B',
  'S': '卖出 S',
  'T': '做T'
}

// 统计
const buyCount = computed(() => records.value.filter(r => r.type === 'B').length)
const sellCount = computed(() => records.value.filter(r => r.type === 'S').length)
const tCount = computed(() => records.value.filter(r => r.type === 'T').length)

// 监听弹窗打开
watch(() => props.visible, (val) => {
  if (val) {
    loadRecords()
  }
})

const loadRecords = async () => {
  loading.value = true
  try {
    const res = await getStockTradeRecords(props.stockCode)
    if (res.status === 'success') {
      records.value = res.records || []
    }
  } catch (e) {
    console.error('加载交易记录失败:', e)
  } finally {
    loading.value = false
  }
}

const close = () => {
  emit('update:visible', false)
}

const openAddModal = () => {
  editingRecord.value = null
  showEditModal.value = true
}

const editRecord = (record: TradeRecord) => {
  editingRecord.value = record
  showEditModal.value = true
}

const confirmDelete = async (record: TradeRecord) => {
  if (confirm(`确定删除这条交易记录吗？\n${typeLabels[record.type]} ¥${record.price} × ${record.quantity}手`)) {
    try {
      await deleteTradeRecord(record.id)
      loadRecords()
    } catch (e) {
      console.error('删除失败:', e)
    }
  }
}
</script>
