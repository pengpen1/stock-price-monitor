<!--
  SettingsView.vue
  设置页面视图
  包含基础设置、AI 配置、数据导入导出等
-->
<script setup lang="ts">
import { useRouter } from "vue-router"
import Settings from "@/components/Settings.vue"

const router = useRouter()

const goBack = () => router.push("/")
</script>

<template>
  <Settings @back="goBack" />
</template>
