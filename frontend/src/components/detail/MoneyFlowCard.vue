<!--
  MoneyFlowCard.vue
  资金流向卡片组件
  显示主力、大单、散户资金净流入
-->
<template>
  <div v-if="moneyFlowData.length > 0" class="bg-white rounded-xl shadow-sm p-4">
    <h3 class="text-sm font-semibold text-slate-700 mb-4">{{ $t('detail.money_flow') }}</h3>
    <div class="grid grid-cols-3 gap-4">
      <div class="text-center">
        <div class="text-xs text-slate-500">{{ $t('detail.main_net_flow') }}</div>
        <div class="text-lg font-semibold" :class="mainNetFlow >= 0 ? 'text-red-500' : 'text-green-500'">
          {{ formatMoney(mainNetFlow) }}
        </div>
      </div>
      <div class="text-center">
        <div class="text-xs text-slate-500">{{ $t('detail.big_net_flow') }}</div>
        <div class="text-lg font-semibold" :class="bigNetFlow >= 0 ? 'text-red-500' : 'text-green-500'">
          {{ formatMoney(bigNetFlow) }}
        </div>
      </div>
      <div class="text-center">
        <div class="text-xs text-slate-500">{{ $t('detail.small_net_flow') }}</div>
        <div class="text-lg font-semibold" :class="smallNetFlow >= 0 ? 'text-red-500' : 'text-green-500'">
          {{ formatMoney(smallNetFlow) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps<{
  moneyFlowData: any[]
}>()

// 资金流向计算
const mainNetFlow = computed(() => {
  if (!props.moneyFlowData.length) return 0
  const last = props.moneyFlowData[props.moneyFlowData.length - 1]
  return (last?.big_in || 0) + (last?.super_in || 0)
})

const bigNetFlow = computed(() => {
  if (!props.moneyFlowData.length) return 0
  const last = props.moneyFlowData[props.moneyFlowData.length - 1]
  return last?.big_in || 0
})

const smallNetFlow = computed(() => {
  if (!props.moneyFlowData.length) return 0
  const last = props.moneyFlowData[props.moneyFlowData.length - 1]
  return last?.small_in || 0
})

const formatMoney = (val: number) => {
  if (Math.abs(val) >= 100000000) return (val / 100000000).toFixed(2) + t('detail.yi')
  if (Math.abs(val) >= 10000) return (val / 10000).toFixed(2) + t('detail.wan')
  return val.toFixed(2)
}
</script>
