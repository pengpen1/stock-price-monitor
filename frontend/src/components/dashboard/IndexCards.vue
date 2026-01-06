<!--
  IndexCards.vue
  大盘指数卡片组件
  显示上证、深证、创业板、沪深300指数
-->
<template>
  <div class="mb-4 grid grid-cols-4 gap-3">
    <div
      v-for="idx in indexList"
      :key="idx.code"
      class="group relative cursor-pointer overflow-hidden rounded-xl border border-slate-100 bg-white p-4 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg"
      @click="$emit('openDetail', idx.code)"
    >
      <!-- 背景装饰 -->
      <div
        class="absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
        :class="
          parseFloat(idx.change_percent) >= 0
            ? 'bg-linear-to-br from-red-50/50 to-transparent'
            : 'bg-linear-to-br from-green-50/50 to-transparent'
        "
      ></div>
      <!-- 左侧装饰条 -->
      <div
        class="absolute top-0 bottom-0 left-0 w-1 rounded-l-xl"
        :class="
          parseFloat(idx.change_percent) >= 0
            ? 'bg-linear-to-b from-red-400 to-red-500'
            : 'bg-linear-to-b from-green-400 to-green-500'
        "
      ></div>
      <div class="relative">
        <div class="mb-1.5 text-xs font-medium text-slate-500">
          {{ idx.name }}
        </div>
        <div class="flex items-baseline gap-2">
          <span class="text-xl font-bold tracking-tight" :class="getIndexClass(idx.change_percent)">
            {{ idx.price }}
          </span>
          <span
            class="rounded px-1.5 py-0.5 text-xs font-semibold"
            :class="
              parseFloat(idx.change_percent) >= 0
                ? 'bg-red-50 text-red-600'
                : 'bg-green-50 text-green-600'
            "
          >
            {{ parseFloat(idx.change_percent) >= 0 ? "+" : "" }}{{ idx.change_percent }}%
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  indexList: any[]
}>()

defineEmits<{
  openDetail: [code: string]
}>()

const getIndexClass = (changePercent: string) => {
  const value = parseFloat(changePercent || "0")
  if (value > 0) return "text-red-500"
  if (value < 0) return "text-green-500"
  return "text-slate-800"
}
</script>
