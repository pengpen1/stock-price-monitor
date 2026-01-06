<!--
  DashboardView.vue
  首页视图 - 股票监控主界面
  包含大盘指数、股票列表、预警等功能
-->
<script setup lang="ts">
import { useRouter } from "vue-router"
import Dashboard from "@/components/Dashboard.vue"
import type { SimulationSession } from "@/api"

const router = useRouter()

const openSettings = () => router.push("/settings")
const openDetail = (code: string) => router.push(`/stock/${code}`)
const openJournal = () => router.push("/journal")
const openNotes = () => router.push("/notes")
</script>

<template>
  <Dashboard
    @openSettings="openSettings"
    @openDetail="openDetail"
    @openJournal="openJournal"
    @openNotes="openNotes"
  />
</template>
