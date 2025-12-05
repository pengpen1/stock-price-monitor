<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Dashboard from './components/Dashboard.vue'
import FloatWindow from './components/FloatWindow.vue'

// 根据 hash 判断显示哪个组件
const isFloatWindow = ref(false)

onMounted(() => {
  // 检查 URL hash 判断是否是悬浮窗
  isFloatWindow.value = window.location.hash === '#/float'
  
  // 监听 hash 变化
  window.addEventListener('hashchange', () => {
    isFloatWindow.value = window.location.hash === '#/float'
  })
})
</script>

<template>
  <!-- 悬浮窗模式 -->
  <FloatWindow v-if="isFloatWindow" />
  <!-- 主窗口模式 -->
  <Dashboard v-else />
</template>
