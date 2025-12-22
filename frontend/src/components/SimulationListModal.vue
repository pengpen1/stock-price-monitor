<template>
  <Teleport to="body">
    <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/50" @click="close"></div>
      
      <div class="relative bg-white rounded-2xl shadow-2xl w-[600px] max-h-[80vh] overflow-hidden flex flex-col">
        <!-- 头部 -->
        <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between flex-shrink-0">
          <div>
            <h3 class="text-lg font-semibold text-slate-800">模拟记录</h3>
            <p class="text-sm text-slate-500">{{ stockCode }} 的历史模拟记录</p>
          </div>
          <button @click="close" class="p-1 text-slate-400 hover:text-slate-600 rounded">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        
        <!-- 内容 -->
        <div class="flex-1 overflow-y-auto p-4">
          <div v-if="loading" class="flex items-center justify-center py-8 text-slate-400">
            加载中...
          </div>
          
          <div v-else-if="sessions.length === 0" class="flex flex-col items-center justify-center py-12 text-slate-400">
            <svg class="w-12 h-12 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
            </svg>
            <p>暂无模拟记录</p>
          </div>
          
          <div v-else class="space-y-3">
            <div v-for="session in sessions" :key="session.id"
              class="bg-slate-50 rounded-xl p-4 hover:bg-slate-100 transition-colors">
              <div class="flex items-start justify-between mb-2">
                <div>
                  <div class="flex items-center gap-2">
                    <span class="font-medium text-slate-800">{{ session.start_date }} ~ {{ session.end_date }}</span>
                    <span :class="statusClass(session.status)" class="px-2 py-0.5 text-xs font-medium rounded">
                      {{ statusText(session.status) }}
                    </span>
                  </div>
                  <div class="text-sm text-slate-500 mt-1">
                    {{ session.total_days }}天 · 初始资金 ¥{{ formatMoney(session.initial_capital) }}
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-lg font-semibold" :class="profitClass(session)">
                    {{ profitRate(session) >= 0 ? '+' : '' }}{{ profitRate(session).toFixed(2) }}%
                  </div>
                  <div class="text-xs text-slate-500">
                    进度 {{ session.current_day }}/{{ session.total_days }}
                  </div>
                </div>
              </div>
              
              <!-- 操作按钮 -->
              <div class="flex items-center gap-2 mt-3 pt-3 border-t border-slate-200">
                <button v-if="session.status === 'paused'" @click="resumeSession(session)"
                  class="px-3 py-1.5 text-sm text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100">
                  继续模拟
                </button>
                <button v-if="session.status === 'completed' || session.status === 'abandoned'" 
                  @click="viewResult(session)"
                  class="px-3 py-1.5 text-sm text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200">
                  查看结果
                </button>
                <button @click="deleteSession(session)" 
                  class="px-3 py-1.5 text-sm text-red-600 bg-red-50 rounded-lg hover:bg-red-100 ml-auto">
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { getSimulationSessions, deleteSimulation, resumeSimulation } from '../api'
import type { SimulationSession } from '../api'

const props = defineProps<{
  visible: boolean
  stockCode: string
}>()

const emit = defineEmits(['update:visible', 'resume', 'view'])

const loading = ref(false)
const sessions = ref<SimulationSession[]>([])

const close = () => {
  emit('update:visible', false)
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getSimulationSessions(props.stockCode)
    if (res.status === 'success') {
      sessions.value = res.sessions || []
    }
  } catch (e) {
    console.error('加载模拟记录失败:', e)
  } finally {
    loading.value = false
  }
}

const formatMoney = (val: number) => {
  if (val >= 10000) {
    return (val / 10000).toFixed(0) + '万'
  }
  return val.toLocaleString('zh-CN')
}

const statusClass = (status: string) => {
  switch (status) {
    case 'running': return 'bg-blue-100 text-blue-600'
    case 'paused': return 'bg-amber-100 text-amber-600'
    case 'completed': return 'bg-green-100 text-green-600'
    case 'abandoned': return 'bg-slate-100 text-slate-600'
    default: return 'bg-slate-100 text-slate-600'
  }
}

const statusText = (status: string) => {
  switch (status) {
    case 'running': return '进行中'
    case 'paused': return '已暂停'
    case 'completed': return '已完成'
    case 'abandoned': return '已放弃'
    default: return status
  }
}

const profitRate = (session: SimulationSession) => {
  // 优先使用后端计算的最终收益率
  if (session.final_profit_rate !== undefined) {
    return session.final_profit_rate
  }
  // 进行中的会话：简单计算现金变化（不含持仓市值）
  return ((session.current_capital - session.initial_capital) / session.initial_capital) * 100
}

const profitClass = (session: SimulationSession) => {
  return profitRate(session) >= 0 ? 'text-red-500' : 'text-green-500'
}

const resumeSession = async (session: SimulationSession) => {
  try {
    const res = await resumeSimulation(session.id)
    if (res.status === 'success') {
      emit('resume', session)
      close()
    }
  } catch (e) {
    console.error('继续模拟失败:', e)
  }
}

const viewResult = (session: SimulationSession) => {
  emit('view', session)
  close()
}

const deleteSession = async (session: SimulationSession) => {
  if (!confirm('确定要删除这条模拟记录吗？')) return
  
  try {
    const res = await deleteSimulation(session.id)
    if (res.status === 'success') {
      sessions.value = sessions.value.filter(s => s.id !== session.id)
    }
  } catch (e) {
    console.error('删除失败:', e)
  }
}

watch(() => props.visible, (val) => {
  if (val) {
    loadData()
  }
})
</script>
