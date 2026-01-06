<!--
  StockTable.vue
  股票列表表格组件
  支持拖拽排序、右键菜单、操作按钮
-->
<template>
  <div class="rounded-xl border border-slate-100 bg-white shadow-sm">
    <table class="w-full table-fixed">
      <thead>
        <tr class="border-b border-slate-100 bg-linear-to-r from-slate-50 to-slate-100/50">
          <th class="w-8 px-1 py-3.5"></th>
          <th
            class="w-24 px-2 py-3.5 text-left text-xs font-semibold tracking-wider text-slate-500 uppercase"
          >
            代码
          </th>
          <th
            class="w-20 px-2 py-3.5 text-left text-xs font-semibold tracking-wider text-slate-500 uppercase"
          >
            名称
          </th>
          <th
            class="w-20 px-2 py-3.5 text-right text-xs font-semibold tracking-wider text-slate-500 uppercase"
          >
            当前价
          </th>
          <th
            class="w-20 cursor-pointer px-2 py-3.5 text-right text-xs font-semibold tracking-wider text-slate-500 uppercase transition-colors hover:text-blue-500"
            @click="$emit('toggleSort')"
          >
            涨跌幅 {{ sortIcon }}
          </th>
          <th
            class="w-16 px-2 py-3.5 text-right text-xs font-semibold tracking-wider text-slate-500 uppercase"
          >
            最高
          </th>
          <th
            class="w-16 px-2 py-3.5 text-right text-xs font-semibold tracking-wider text-slate-500 uppercase"
          >
            最低
          </th>
          <th
            class="w-20 px-2 py-3.5 text-right text-xs font-semibold tracking-wider text-slate-500 uppercase"
          >
            成交额
          </th>
          <th
            class="w-16 px-2 py-3.5 text-left text-xs font-semibold tracking-wider text-slate-500 uppercase"
          >
            分组
          </th>
          <th
            class="w-28 px-2 py-3.5 text-center text-xs font-semibold tracking-wider text-slate-500 uppercase"
          >
            操作
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-50">
        <tr
          v-for="(stock, index) in stocks"
          :key="stock.code"
          class="group cursor-pointer transition-all duration-200 hover:bg-gradient-to-r hover:from-slate-50 hover:to-transparent"
          draggable="true"
          @dragstart="$emit('dragStart', index, $event)"
          @dragover.prevent
          @drop="$emit('drop', index)"
          @click="handleRowClick(stock.code, $event)"
          @contextmenu.prevent="$emit('contextMenu', $event, stock)"
        >
          <td class="cursor-move px-1 py-3.5" @click.stop>
            <span
              class="text-sm font-bold text-slate-300 transition-colors group-hover:text-slate-500"
              >⋮⋮</span
            >
          </td>
          <td class="px-2 py-3.5 font-mono text-xs text-slate-600">
            {{ stock.code }}
            <span v-if="alerts[stock.code]?.enabled" class="ml-0.5 text-amber-500">🔔</span>
          </td>
          <td class="truncate px-2 py-3.5 text-sm font-medium text-slate-800">
            {{ stock.name }}
          </td>
          <td
            class="px-2 py-3.5 text-right text-sm font-bold tabular-nums"
            :class="getPriceClass(stock.change_percent)"
          >
            {{ stock.price }}
          </td>
          <td class="px-2 py-3.5 text-right tabular-nums">
            <span
              class="inline-flex items-center gap-0.5 rounded-md px-2 py-0.5 text-sm font-semibold"
              :class="
                parseFloat(stock.change_percent) > 0
                  ? 'bg-red-50 text-red-600'
                  : parseFloat(stock.change_percent) < 0
                    ? 'bg-green-50 text-green-600'
                    : 'bg-slate-50 text-slate-600'
              "
            >
              <span v-if="parseFloat(stock.change_percent) > 0">↑</span>
              <span v-else-if="parseFloat(stock.change_percent) < 0">↓</span>
              {{ stock.change_percent }}%
            </span>
          </td>
          <td class="px-2 py-3.5 text-right text-sm text-slate-600 tabular-nums">
            {{ stock.high }}
          </td>
          <td class="px-2 py-3.5 text-right text-sm text-slate-600 tabular-nums">
            {{ stock.low }}
          </td>
          <td class="px-2 py-3.5 text-right text-xs text-slate-500">
            {{ formatAmount(stock.amount) }}
          </td>
          <td class="px-2 py-3.5 text-xs text-slate-500">
            <span
              v-if="stockGroups[stock.code]"
              class="rounded-md border border-blue-100 bg-gradient-to-r from-blue-50 to-indigo-50 px-2 py-1 font-medium text-blue-600"
            >
              {{ stockGroups[stock.code] }}
            </span>
          </td>
          <td class="px-2 py-3.5 text-center" @click.stop>
            <div class="flex items-center justify-center gap-1.5">
              <button
                @click="$emit('setFocus', stock.code)"
                :class="
                  focusedStock === stock.code
                    ? 'border-amber-300 bg-amber-100 text-amber-600 shadow-sm'
                    : 'border-slate-200 text-slate-400 hover:border-amber-200 hover:bg-amber-50 hover:text-amber-500'
                "
                class="rounded-lg border px-2 py-1 text-xs transition-all duration-200"
              >
                ⭐
              </button>
              <button
                @click="$emit('openAI', stock, 'fast')"
                class="rounded-lg border border-purple-200 bg-purple-50 px-2 py-1 text-xs font-medium text-purple-500 transition-all duration-200 hover:border-purple-300 hover:bg-purple-100"
                title="快速AI分析"
              >
                AI
              </button>
              <button
                @click="$emit('openAlert', stock)"
                class="rounded-lg border border-blue-200 bg-blue-50 px-2 py-1 text-xs text-blue-500 transition-all duration-200 hover:border-blue-300 hover:bg-blue-100"
              >
                预警
              </button>
              <!-- 更多操作 -->
              <div class="relative">
                <button
                  @click.stop="$emit('toggleMore', stock.code)"
                  class="rounded-lg border border-slate-200 bg-slate-50 px-2 py-1 text-xs text-slate-500 transition-all duration-200 hover:border-slate-300 hover:bg-slate-100"
                >
                  ···
                </button>
                <div
                  v-if="moreMenuCode === stock.code"
                  class="absolute top-full right-0 z-30 mt-1 min-w-[100px] rounded-xl border border-slate-200 bg-white py-1.5 shadow-xl"
                >
                  <button
                    @click="$emit('addTrade', stock)"
                    class="w-full px-4 py-2 text-left text-xs text-slate-700 transition-colors hover:bg-slate-50"
                  >
                    添加交易
                  </button>
                  <button
                    @click="$emit('remove', stock.code)"
                    class="w-full px-4 py-2 text-left text-xs text-red-500 transition-colors hover:bg-red-50"
                  >
                    删除
                  </button>
                </div>
              </div>
            </div>
          </td>
        </tr>
        <tr v-if="stocks.length === 0">
          <td colspan="10" class="px-4 py-12 text-center text-sm text-slate-400">
            {{ $t("dashboard.empty") }}
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
  openAI: [stock: any, type: "fast" | "precise"]
  openAlert: [stock: any]
  toggleMore: [code: string]
  addTrade: [stock: any]
  remove: [code: string]
  openDetail: [code: string]
}>()

const getPriceClass = (changePercent: string) => {
  const value = parseFloat(changePercent)
  if (value > 0) return "text-red-500"
  if (value < 0) return "text-green-500"
  return "text-slate-600"
}

const formatAmount = (amount: string) => {
  const val = parseFloat(amount || "0")
  if (val >= 100000000) return (val / 100000000).toFixed(2) + "亿"
  if (val >= 10000) return (val / 10000).toFixed(0) + "万"
  return val.toFixed(0)
}

const handleRowClick = (code: string, event: MouseEvent) => {
  if ((event.target as HTMLElement).closest("button")) return
  emit("openDetail", code)
}
</script>
