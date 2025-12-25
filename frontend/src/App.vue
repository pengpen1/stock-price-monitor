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
})
</script>

<template>
  <router-view />
</template>
