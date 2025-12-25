<!--
  StockDetailView.vue
  股票详情页面视图
  包含分时图、K线图、资金流向、AI分析等
-->
<script setup lang="ts">
import { useRouter, useRoute } from "vue-router";
import StockDetail from "@/components/StockDetail.vue";
import type { SimulationSession } from "@/api";

const router = useRouter();
const route = useRoute();

// 从路由获取股票代码
const code = route.params.code as string;

const goBack = () => router.push("/");

const startSimulation = (session: SimulationSession) => {
  router.push(`/simulation/${session.id}`);
};

const viewSimulation = (session: SimulationSession) => {
  router.push(`/simulation/${session.id}`);
};

const openJournal = () => router.push("/journal");
</script>

<template>
  <StockDetail
    :code="code"
    @back="goBack"
    @startSimulation="startSimulation"
    @viewSimulation="viewSimulation"
    @openJournal="openJournal"
  />
</template>
