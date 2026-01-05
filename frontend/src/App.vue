<!--
  App.vue
  应用根组件
  使用 Vue Router 管理页面导航
-->
<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  // 检查是否是悬浮窗模式
  if (window.location.hash === '#/float') {
    router.replace('/float')
  }

  // 监听主进程的导航请求
  const ipc = (window as any).ipcRenderer
  if (ipc) {
    ipc.on('navigate-to-stock', (code: string) => {
      console.log('收到导航请求:', code)
      // 如果当前已经在该股票详情页，不重复跳转
      if (router.currentRoute.value.name === 'StockDetail' &&
        router.currentRoute.value.params.code === code) {
        return
      }
      router.push(`/stock/${code}`)
    })
  }
})
</script>

<template>
  <router-view />
</template>
