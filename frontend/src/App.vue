<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Dashboard from './components/Dashboard.vue'
import FloatWindow from './components/FloatWindow.vue'
import Settings from './components/Settings.vue'
import StockDetail from './components/StockDetail.vue'
import SimulationPage from './components/SimulationPage.vue'
import TradeJournalPage from './components/TradeJournalPage.vue'
import NotesPage from './components/NotesPage.vue'
import type { SimulationSession } from './api'

// 页面状态
type Page = 'dashboard' | 'settings' | 'detail' | 'simulation' | 'journal' | 'notes'
const currentPage = ref<Page>('dashboard')
const isFloatWindow = ref(false)
const detailCode = ref('')
const simulationSessionId = ref('')

const openSettings = () => { currentPage.value = 'settings' }
const backToDashboard = () => { currentPage.value = 'dashboard' }

// 打开股票详情
const openStockDetail = (code: string) => {
  detailCode.value = code
  currentPage.value = 'detail'
}

// 开始/继续模拟
const startSimulation = (session: SimulationSession) => {
  simulationSessionId.value = session.id
  currentPage.value = 'simulation'
}

// 查看模拟结果（也进入模拟页面，会自动显示结果弹窗）
const viewSimulation = (session: SimulationSession) => {
  simulationSessionId.value = session.id
  currentPage.value = 'simulation'
}

// 模拟完成或返回
const onSimulationBack = () => {
  currentPage.value = 'detail'
}

const onSimulationComplete = () => {
  currentPage.value = 'detail'
}

// 打开交易日志页面
const openJournal = () => {
  journalFromPage.value = currentPage.value  // 记录来源页面
  currentPage.value = 'journal'
}

// 从交易日志返回（根据来源页面返回）
const journalFromPage = ref<Page>('dashboard')
const onJournalBack = () => {
  currentPage.value = journalFromPage.value === 'detail' ? 'detail' : 'dashboard'
}

// 打开笔记页面
const openNotes = () => {
  currentPage.value = 'notes'
}

// 从笔记页面返回
const onNotesBack = () => {
  currentPage.value = 'dashboard'
}

onMounted(() => {
  isFloatWindow.value = window.location.hash === '#/float'
  window.addEventListener('hashchange', () => {
    isFloatWindow.value = window.location.hash === '#/float'
  })
})
</script>

<template>
  <FloatWindow v-if="isFloatWindow" />
  <template v-else>
    <Settings v-if="currentPage === 'settings'" @back="backToDashboard" />
    <StockDetail v-else-if="currentPage === 'detail'" :code="detailCode" 
      @back="backToDashboard" 
      @startSimulation="startSimulation"
      @viewSimulation="viewSimulation"
      @openJournal="openJournal" />
    <SimulationPage v-else-if="currentPage === 'simulation'" 
      :session-id="simulationSessionId"
      @back="onSimulationBack"
      @complete="onSimulationComplete" />
    <TradeJournalPage v-else-if="currentPage === 'journal'" @back="onJournalBack" />
    <NotesPage v-else-if="currentPage === 'notes'" @back="onNotesBack" />
    <Dashboard v-else @openSettings="openSettings" @openDetail="openStockDetail" @openJournal="openJournal" @openNotes="openNotes" />
  </template>
</template>
