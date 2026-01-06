<!--
  StockInfoCards.vue
  股票基本信息卡片组件
  显示开盘价、昨收、最高、最低、涨停、跌停价
-->
<template>
  <div class="mb-6 grid grid-cols-6 gap-3">
    <div class="rounded-xl bg-white p-3 shadow-sm">
      <div class="text-xs text-slate-500">{{ $t("detail.open") }}</div>
      <div class="text-base font-semibold text-slate-800">
        {{ stockInfo.open || "--" }}
      </div>
    </div>
    <div class="rounded-xl bg-white p-3 shadow-sm">
      <div class="text-xs text-slate-500">{{ $t("detail.pre_close") }}</div>
      <div class="text-base font-semibold text-slate-800">
        {{ stockInfo.pre_close || "--" }}
      </div>
    </div>
    <div class="rounded-xl bg-white p-3 shadow-sm">
      <div class="text-xs text-slate-500">{{ $t("detail.high") }}</div>
      <div class="text-base font-semibold text-red-500">
        {{ stockInfo.high || "--" }}
      </div>
    </div>
    <div class="rounded-xl bg-white p-3 shadow-sm">
      <div class="text-xs text-slate-500">{{ $t("detail.low") }}</div>
      <div class="text-base font-semibold text-green-500">
        {{ stockInfo.low || "--" }}
      </div>
    </div>
    <div class="rounded-xl bg-white p-3 shadow-sm">
      <div class="text-xs text-slate-500">{{ $t("detail.limit_up") }}</div>
      <div class="text-base font-semibold text-red-500">{{ limitUpPrice }}</div>
    </div>
    <div class="rounded-xl bg-white p-3 shadow-sm">
      <div class="text-xs text-slate-500">{{ $t("detail.limit_down") }}</div>
      <div class="text-base font-semibold text-green-500">
        {{ limitDownPrice }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  stockInfo: any
  limitUpPrice: string
  limitDownPrice: string
}>()
</script>
