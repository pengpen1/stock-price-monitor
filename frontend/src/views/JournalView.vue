<!--
  JournalView.vue
  交易日志页面视图
  统一查看和管理所有股票的交易记录
-->
<script setup lang="ts">
import { useRouter } from "vue-router"
import TradeJournalPage from "@/components/TradeJournalPage.vue"

const router = useRouter()

const goBack = () => router.back()
</script>

<template>
  <TradeJournalPage @back="goBack" />
</template>
