<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Dashboard from './components/Dashboard.vue'
import FloatWindow from './components/FloatWindow.vue'
import Settings from './components/Settings.vue'

// 页面状态
type Page = 'dashboard' | 'settings'
const currentPage = ref<Page>('dashboard')
const isFloatWindow = ref(false)

// 切换到设置页
const openSettings = () => {
  currentPage.value = 'settings'
}

// 返回主页
const backToDashboard = () => {
  currentPage.value = 'dashboard'
}

onMounted(() => {
  // 检查 URL hash 判断是否是悬浮窗
  isFloatWindow.value = window.location.hash === '#/float'
  
  window.addEventListener('hashchange', () => {
    isFloatWindow.value = window.location.hash === '#/float'
  })
})
</script>

<template>
  <!-- 悬浮窗模式 -->
  <FloatWindow v-if="isFloatWindow" />
  <!-- 主窗口模式 -->
  <template v-else>
    <Settings v-if="currentPage === 'settings'" @back="backToDashboard" />
    <Dashboard v-else @openSettings="openSettings" />
  </template>
</template>
