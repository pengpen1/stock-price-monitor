<!--
  Dashboard.vue
  首页主组件 - 股票监控主界面
  包含大盘指数、股票列表、预警、分组等功能
-->
<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
    <div class="mx-auto max-w-6xl">
      <!-- 头部区域 -->
      <div class="mb-5 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div
            class="flex h-10 w-10 items-center justify-center rounded-xl shadow-lg shadow-blue-500/20"
          >
            <img src="../assets/stock.png" class="opacity-90" alt="stock" />
          </div>
          <h1
            class="bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-2xl font-bold text-transparent"
          >
            {{ $t("dashboard.title") }}
          </h1>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="$emit('openJournal')"
            class="cursor-pointer rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-600 transition-all duration-200 hover:shadow-sm"
            title="交易日志"
          >
            📝
          </button>
          <button
            @click="$emit('openNotes')"
            class="cursor-pointer rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-600 transition-all duration-200 hover:shadow-sm"
            title="笔记"
          >
            📓
          </button>
          <button
            @click="showUserGuide = true"
            class="cursor-pointer rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-600 transition-all duration-200 hover:shadow-sm"
            title="使用手册"
          >
            📖
          </button>
          <button
            @click="showChangelog = true"
            class="cursor-pointer rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-600 transition-all duration-200 hover:shadow-sm"
            title="更新日志"
          >
            📋
          </button>
          <button
            @click="$emit('openSettings')"
            class="cursor-pointer rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-600 transition-all duration-200 hover:shadow-sm"
          >
            ⚙️
          </button>
        </div>
      </div>

      <!-- 大盘指数 -->
      <IndexCards :index-list="indexList" @open-detail="openIndexDetail" />

      <!-- 添加股票 -->
      <div class="mb-4 flex gap-2">
        <div class="relative flex-1">
          <span class="absolute top-1/2 left-3 -translate-y-1/2 text-slate-400">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </span>
          <input
            v-model="newStockCode"
            :placeholder="$t('dashboard.placeholder')"
            @keyup.enter="handleAddStock"
            :disabled="loading"
            class="w-full rounded-lg border border-slate-200 bg-white py-2 pr-3 pl-9 text-sm transition-all duration-200 placeholder:text-slate-400 focus:ring-2 focus:ring-blue-500/70 focus:outline-none"
          />
        </div>
        <button
          @click="handleAddStock"
          :disabled="loading"
          class="flex min-w-[72px] items-center justify-center gap-1.5 rounded-lg bg-gradient-to-r from-blue-500 to-blue-600 px-5 py-2 text-sm font-medium text-white transition-all duration-200 hover:from-blue-600 hover:to-blue-700 hover:shadow-md hover:shadow-blue-500/20 disabled:cursor-not-allowed disabled:from-blue-300 disabled:to-blue-400"
        >
          <svg
            v-if="loading"
            class="h-3.5 w-3.5 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            ></circle>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <span>{{ loading ? $t("dashboard.adding") : $t("dashboard.add") }}</span>
        </button>
      </div>

      <!-- 错误提示 -->
      <div
        v-if="errorMsg"
        class="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600"
      >
        {{ errorMsg }}
      </div>

      <!-- 预警通知 -->
      <div v-if="alertNotifications.length > 0" class="mb-4 space-y-2">
        <div
          v-for="(alert, idx) in alertNotifications"
          :key="idx"
          class="flex justify-between rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800"
        >
          <div>
            <div class="font-medium">{{ alert.name }} ({{ alert.code }})</div>
            <div v-for="msg in alert.messages" :key="msg" class="text-amber-600">
              {{ msg }}
            </div>
          </div>
          <button @click="dismissAlert(idx)" class="text-amber-400 hover:text-amber-600">✕</button>
        </div>
      </div>

      <!-- 分组和排序工具栏 -->
      <div class="mb-3 flex items-center justify-between px-1">
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-slate-500">分组:</span>
          <button
            @click="currentGroup = ''"
            :class="
              !currentGroup
                ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-sm shadow-blue-500/20'
                : 'border border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:bg-slate-50'
            "
            class="rounded-lg px-3.5 py-1.5 text-xs font-medium transition-all duration-200"
          >
            全部
          </button>
          <button
            v-for="g in groupList"
            :key="g"
            @click="currentGroup = g"
            @contextmenu="showGroupContextMenu($event, g)"
            :class="
              currentGroup === g
                ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-sm shadow-blue-500/20'
                : 'border border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:bg-slate-50'
            "
            class="rounded-lg px-3.5 py-1.5 text-xs font-medium transition-all duration-200"
          >
            {{ g }}
          </button>
          <button
            @click="showAddGroupModal = true"
            class="rounded-lg border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-medium text-blue-500 transition-all duration-200 hover:border-blue-200 hover:bg-blue-100"
          >
            + 新建
          </button>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-slate-500">排序:</span>
          <select
            v-model="sortBy"
            class="cursor-pointer rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs transition-all duration-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-500/30 focus:outline-none"
          >
            <option value="">默认</option>
            <option value="change_desc">涨幅↓</option>
            <option value="change_asc">涨幅↑</option>
          </select>
        </div>
      </div>

      <!-- 股票列表 -->
      <StockTable
        :stocks="filteredStocks"
        :alerts="alerts"
        :stock-groups="stockGroups"
        :focused-stock="focusedStock"
        :sort-icon="sortIcon"
        :more-menu-code="moreMenuCode"
        @toggle-sort="toggleSort"
        @drag-start="handleDragStart"
        @drop="handleDrop"
        @context-menu="showContextMenu"
        @set-focus="handleSetFocus"
        @open-a-i="openAIModal"
        @open-alert="openAlertModal"
        @toggle-more="toggleMoreMenu"
        @add-trade="openQuickTradeRecord"
        @remove="handleRemoveStock"
        @open-detail="(code) => $emit('openDetail', code)"
      />

      <!-- 底部语录 -->
      <div class="relative mt-4 h-6 overflow-hidden">
        <transition name="quote-fade" mode="out-in">
          <div
            :key="currentQuoteIndex"
            class="flex items-center justify-center gap-2 text-center text-xs text-slate-400"
          >
            <span class="text-slate-300">💡</span>
            <span>{{ stockQuotes[currentQuoteIndex] }}</span>
          </div>
        </transition>
      </div>
    </div>

    <!-- 右键菜单 -->
    <ContextMenus
      :stock-menu="contextMenu"
      :group-menu="groupContextMenu"
      :group-list="groupList"
      :stock-groups="stockGroups"
      @action="handleContextAction"
      @delete-group="handleDeleteGroup"
    />

    <!-- 弹窗组件 -->
    <AlertModal
      :visible="showAlertModal"
      :stock="currentAlertStock"
      :alerts="alerts"
      @close="showAlertModal = false"
      @save="saveAlert"
    />
    <GroupModal
      :visible="showAddGroupModal"
      :pending-stock="pendingGroupStock"
      @close="closeAddGroupModal"
      @add="addGroup"
    />
    <AIAnalysisModal v-model:visible="showAiModal" :stock-code="aiStockCode" :type="aiType" />
    <ChangelogModal v-model:visible="showChangelog" />
    <UserGuideModal v-model:visible="showUserGuide" />
    <IndexDetailModal v-model:visible="showIndexDetail" :index-code="currentIndexCode" />
    <TradeRecordModal v-model:visible="showQuickTradeModal" :stock-code="quickTradeStockCode" />
  </div>
</template>

<script setup lang="ts">
/**
 * Dashboard 主组件逻辑
 * 使用 useDashboard composable 管理核心数据
 */
import { ref, onMounted, onUnmounted } from "vue"
import { useDashboard } from "@/composables/useDashboard"
import IndexCards from "./dashboard/IndexCards.vue"
import StockTable from "./dashboard/StockTable.vue"
import AlertModal from "./dashboard/AlertModal.vue"
import GroupModal from "./dashboard/GroupModal.vue"
import ContextMenus from "./dashboard/ContextMenus.vue"
import AIAnalysisModal from "./AIAnalysisModal.vue"
import ChangelogModal from "./ChangelogModal.vue"
import UserGuideModal from "./UserGuideModal.vue"
import TradeRecordModal from "./TradeRecordModal.vue"
import IndexDetailModal from "./IndexDetailModal.vue"

defineEmits(["openSettings", "openDetail", "openJournal", "openNotes"])

// ========== 使用 Composable ==========
const {
  newStockCode,
  loading,
  errorMsg,
  alertNotifications,
  focusedStock,
  currentGroup,
  sortBy,
  groupList,
  alerts,
  stockGroups,
  indexList,
  sortIcon,
  filteredStocks,
  toggleSort,
  handleAddStock,
  handleRemoveStock,
  handleDragStart,
  handleDrop,
  addGroup,
  deleteGroup,
  moveStockToGroup,
  moveStockToTop,
  moveStockToBottom,
  saveAlert,
  dismissAlert,
  handleSetFocus,
  startRefresh,
  stopRefresh,
} = useDashboard()

// ========== 弹窗状态 ==========
const showAlertModal = ref(false)
const currentAlertStock = ref<any>(null)
const showAddGroupModal = ref(false)
const pendingGroupStock = ref<string | null>(null)
const showAiModal = ref(false)
const aiStockCode = ref("")
const aiType = ref<"fast" | "precise">("fast")
const showChangelog = ref(false)
const showUserGuide = ref(false)
const showIndexDetail = ref(false)
const currentIndexCode = ref("")
const showQuickTradeModal = ref(false)
const quickTradeStockCode = ref("")
const moreMenuCode = ref<string | null>(null)

// ========== 右键菜单 ==========
const contextMenu = ref({ show: false, x: 0, y: 0, stock: null as any })
const groupContextMenu = ref({ show: false, x: 0, y: 0, group: "" })

const showContextMenu = (e: MouseEvent, stock: any) => {
  contextMenu.value = { show: true, x: e.clientX, y: e.clientY, stock }
}

const showGroupContextMenu = (e: MouseEvent, group: string) => {
  e.preventDefault()
  groupContextMenu.value = { show: true, x: e.clientX, y: e.clientY, group }
}

const hideContextMenu = () => {
  contextMenu.value.show = false
  groupContextMenu.value.show = false
}

const handleContextAction = async (action: string, param?: string) => {
  const stock = contextMenu.value.stock
  if (!stock) return
  if (action === "top") await moveStockToTop(stock.code)
  else if (action === "bottom") await moveStockToBottom(stock.code)
  else if (action === "group") await moveStockToGroup(stock.code, param || "")
  else if (action === "newGroup") {
    pendingGroupStock.value = stock.code
    showAddGroupModal.value = true
  } else if (action === "delete") await handleRemoveStock(stock.code)
  hideContextMenu()
}

const handleDeleteGroup = async (deleteStocks: boolean) => {
  await deleteGroup(groupContextMenu.value.group, deleteStocks)
  hideContextMenu()
}

// ========== 弹窗操作 ==========
const openAlertModal = (stock: any) => {
  currentAlertStock.value = stock
  showAlertModal.value = true
}

const openAIModal = (stock: any, type: "fast" | "precise") => {
  aiStockCode.value = stock.code
  aiType.value = type
  showAiModal.value = true
}

const openIndexDetail = (code: string) => {
  currentIndexCode.value = code
  showIndexDetail.value = true
}

const openQuickTradeRecord = (stock: any) => {
  moreMenuCode.value = null
  quickTradeStockCode.value = stock.code
  showQuickTradeModal.value = true
}

const toggleMoreMenu = (code: string) => {
  moreMenuCode.value = moreMenuCode.value === code ? null : code
}

const closeAddGroupModal = () => {
  showAddGroupModal.value = false
  pendingGroupStock.value = null
}

// ========== 语录轮播 ==========
const stockQuotes = [
  "一季报披露：4月1日-4月30日",
  "中报披露：7月1日-8月31日",
  "三季报披露：10月1日-10月31日",
  "年报披露：次年1月1日-4月30日",
  "投资有风险，入市需谨慎",
  "补强不补弱，顺势而为",
  "不要和趋势作对，趋势是你最好的朋友",
  "牛市不言顶，熊市不言底",
  "在高潮时警惕，在退潮时理智",
  "高位横盘不突破，久盘必跌",
  "宁可错过，不可做错",
  "量在价先，成交量是股价的先行指标",
  "底部放量要注意，顶部放量要警惕",
  "截断亏损，让利润奔跑",
  "空仓也是一种操作",
  "卖飞光荣，套牢可耻",
  "会买的是徒弟，会卖的是师傅",
  "不要把所有鸡蛋放在一个篮子里",
  "知行合一，严格执行交易纪律",
  "市场永远是对的，错的只是自己",
]
const currentQuoteIndex = ref(0)
let quoteIntervalId: ReturnType<typeof setInterval> | null = null

// ========== 生命周期 ==========
const handleGlobalClick = () => {
  hideContextMenu()
  moreMenuCode.value = null
}

onMounted(() => {
  startRefresh()
  document.addEventListener("click", handleGlobalClick)
  quoteIntervalId = setInterval(() => {
    currentQuoteIndex.value = (currentQuoteIndex.value + 1) % stockQuotes.length
  }, 5000)
})

onUnmounted(() => {
  stopRefresh()
  if (quoteIntervalId) clearInterval(quoteIntervalId)
  document.removeEventListener("click", handleGlobalClick)
})
</script>

<style scoped>
.quote-fade-enter-active,
.quote-fade-leave-active {
  transition: all 0.5s ease;
}
.quote-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.quote-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
