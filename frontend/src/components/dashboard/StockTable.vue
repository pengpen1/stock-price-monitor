<!--
  StockTable.vue
  股票列表表格组件
  支持拖拽排序、右键菜单、操作按钮
-->
<template>
  <div class="bg-white rounded-xl shadow-sm border border-slate-100">
    <table class="w-full table-fixed">
      <thead>
        <tr class="bg-gradient-to-r from-slate-50 to-slate-100/50 border-b border-slate-100">
          <th class="w-8 px-1 py-3.5"></th>
          <th class="w-24 px-2 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">代码</th>
          <th class="w-20 px-2 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">名称</th>
          <th class="w-20 px-2 py-3.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">当前价</th>
          <th class="w-20 px-2 py-3.5 text-right text-xs font-semibold text-slate-500 cursor-pointer hover:text-blue-500 transition-colors uppercase tracking-wider" @click="$emit('toggleSort')">
            涨跌幅 {{ sortIcon }}
          </th>
          <th class="w-16 px-2 py-3.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">最高</th>
          <th class="w-16 px-2 py-3.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">最低</th>
          <th class="w-20 px-2 py-3.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">成交额</th>
          <th class="w-16 px-2 py-3.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">分组</th>
          <th class="w-28 px-2 py-3.5 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider">操作</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-50">
        <tr
          v-for="(stock, index) in stocks"
          :key="stock.code"
          class="group hover:bg-gradient-to-r hover:from-slate-50 hover:to-transparent transition-all duration-200 cursor-pointer"
          draggable="true"
          @dragstart="$emit('dragStart', index, $event)"
          @dragover.prevent
          @drop="$emit('drop', index)"
          @click="handleRowClick(stock.code, $event)"
          @contextmenu.prevent="$emit('contextMenu', $event, stock)"
        >
          <td class="px-1 py-3.5 cursor-move" @click.stop>
            <span class="text-slate-300 group-hover:text-slate-500 text-sm font-bold transition-colors">⋮⋮</span>
          </td>
          <td class="px-2 py-3.5 text-xs font-mono text-slate-600">
            {{ stock.code }}
            <span v-if="alerts[stock.code]?.enabled" class="ml-0.5 text-amber-500">🔔</span>
          </td>
          <td class="px-2 py-3.5 text-sm font-medium text-slate-800 truncate">{{ stock.name }}</td>
          <td class="px-2 py-3.5 text-sm text-right font-bold tabular-nums" :class="getPriceClass(stock.change_percent)">
            {{ stock.price }}
          </td>
          <td class="px-2 py-3.5 text-right tabular-nums">
            <span
              class="inline-flex items-center gap-0.5 text-sm font-semibold px-2 py-0.5 rounded-md"
              :class="parseFloat(stock.change_percent) > 0 ? 'text-red-600 bg-red-50' :
                      parseFloat(stock.change_percent) < 0 ? 'text-green-600 bg-green-50' : 'text-slate-600 bg-slate-50'"
            >
              <span v-if="parseFloat(stock.change_percent) > 0">↑</span>
              <span v-else-if="parseFloat(stock.change_percent) < 0">↓</span>
              {{ stock.change_percent }}%
            </span>
          </td>
          <td class="px-2 py-3.5 text-sm text-right text-slate-600 tabular-nums">{{ stock.high }}</td>
          <td class="px-2 py-3.5 text-sm text-right text-slate-600 tabular-nums">{{ stock.low }}</td>
          <td class="px-2 py-3.5 text-xs text-right text-slate-500">{{ formatAmount(stock.amount) }}</td>
          <td class="px-2 py-3.5 text-xs text-slate-500">
            <span v-if="stockGroups[stock.code]" class="px-2 py-1 bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-600 rounded-md font-medium border border-blue-100">
              {{ stockGroups[stock.code] }}
            </span>
          </td>
          <td class="px-2 py-3.5 text-center" @click.stop>
            <div class="flex items-center justify-center gap-1.5">
              <button
                @click="$emit('setFocus', stock.code)"
                :class="focusedStock === stock.code
                  ? 'bg-amber-100 text-amber-600 border-amber-300 shadow-sm'
                  : 'text-slate-400 border-slate-200 hover:bg-amber-50 hover:text-amber-500 hover:border-amber-200'"
                class="px-2 py-1 text-xs border rounded-lg transition-all duration-200"
              >⭐</button>
              <button
                @click="$emit('openAI', stock, 'fast')"
                class="px-2 py-1 text-xs text-purple-500 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 hover:border-purple-300 transition-all duration-200 font-medium"
                title="快速AI分析"
              >AI</button>
              <button
                @click="$emit('openAlert', stock)"
                class="px-2 py-1 text-xs text-blue-500 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 hover:border-blue-300 transition-all duration-200"
              >预警</button>
              <!-- 更多操作 -->
              <div class="relative">
                <button
                  @click.stop="$emit('toggleMore', stock.code)"
                  class="px-2 py-1 text-xs text-slate-500 bg-slate-50 border border-slate-200 rounded-lg hover:bg-slate-100 hover:border-slate-300 transition-all duration-200"
                >···</button>
                <div
                  v-if="moreMenuCode === stock.code"
                  class="absolute right-0 top-full mt-1 bg-white rounded-xl shadow-xl border border-slate-200 py-1.5 z-30 min-w-[100px]"
                >
                  <button @click="$emit('addTrade', stock)" class="w-full px-4 py-2 text-left text-xs text-slate-700 hover:bg-slate-50 transition-colors">
                    添加交易
                  </button>
                  <button @click="$emit('remove', stock.code)" class="w-full px-4 py-2 text-left text-xs text-red-500 hover:bg-red-50 transition-colors">
                    删除
                  </button>
                </div>
              </div>
            </div>
          </td>
        </tr>
        <tr v-if="stocks.length === 0">
          <td colspan="10" class="px-4 py-12 text-center text-slate-400 text-sm">
            {{ $t('dashboard.empty') }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  stocks: any[]
  alerts: Record<string, any>
  stockGroups: Record<string, string>
  focusedStock: string | null
  sortIcon: string
  moreMenuCode: string | null
}>()

const emit = defineEmits<{
  toggleSort: []
  dragStart: [index: number, event: DragEvent]
  drop: [index: number]
  contextMenu: [event: MouseEvent, stock: any]
  setFocus: [code: string]
  openAI: [stock: any, type: 'fast' | 'precise']
  openAlert: [stock: any]
  toggleMore: [code: string]
  addTrade: [stock: any]
  remove: [code: string]
  openDetail: [code: string]
}>()

const getPriceClass = (changePercent: string) => {
  const value = parseFloat(changePercent)
  if (value > 0) return 'text-red-500'
  if (value < 0) return 'text-green-500'
  return 'text-slate-600'
}

const formatAmount = (amount: string) => {
  const val = parseFloat(amount || '0')
  if (val >= 100000000) return (val / 100000000).toFixed(2) + '亿'
  if (val >= 10000) return (val / 10000).toFixed(0) + '万'
  return val.toFixed(0)
}

const handleRowClick = (code: string, event: MouseEvent) => {
  if ((event.target as HTMLElement).closest('button')) return
  emit('openDetail', code)
}
</script>
