<!--
  NotesView.vue
  笔记页面视图
  交易笔记管理，支持 AI 提取交易记录
-->
<script setup lang="ts">
import { useRouter } from "vue-router"
import NotesPage from "@/components/NotesPage.vue"

const router = useRouter()

const goBack = () => router.back()
</script>

<template>
  <NotesPage @back="goBack" />
</template>
