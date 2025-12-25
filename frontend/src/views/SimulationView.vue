<!--
  SimulationView.vue
  实盘模拟页面视图
  基于历史K线数据进行模拟交易练习
-->
<script setup lang="ts">
import { useRouter, useRoute } from "vue-router";
import SimulationPage from "@/components/SimulationPage.vue";

const router = useRouter();
const route = useRoute();

// 从路由获取会话ID
const sessionId = route.params.sessionId as string;

const goBack = () => router.back();
const onComplete = () => router.back();
</script>

<template>
  <SimulationPage
    :session-id="sessionId"
    @back="goBack"
    @complete="onComplete"
  />
</template>
