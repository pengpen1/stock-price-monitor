<!--
  AlertModal.vue
  预警设置弹窗组件
-->
<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click.self="$emit('close')"
  >
    <div class="w-96 rounded-xl bg-white p-6 shadow-xl">
      <h3 class="mb-4 text-lg font-semibold text-slate-800">预警设置 - {{ stock?.name }}</h3>
      <div class="space-y-4">
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-600">止盈价格</label>
          <input
            v-model="form.take_profit"
            type="number"
            step="0.01"
            placeholder="价格达到时提醒"
            class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-600">止损价格</label>
          <input
            v-model="form.stop_loss"
            type="number"
            step="0.01"
            placeholder="价格跌至时提醒"
            class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-600">涨跌幅预警 (%)</label>
          <input
            v-model="form.change_alert"
            type="number"
            step="0.1"
            placeholder="涨跌幅达到时提醒"
            class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>
        <div class="flex items-center gap-2">
          <input v-model="form.enabled" type="checkbox" id="alert-enabled" class="h-4 w-4" />
          <label for="alert-enabled" class="text-sm text-slate-600">启用预警</label>
        </div>
      </div>
      <div class="mt-6 flex justify-end gap-3">
        <button
          @click="$emit('close')"
          class="rounded-lg border border-slate-200 px-4 py-2 text-slate-600 hover:bg-slate-50"
        >
          取消
        </button>
        <button
          @click="handleSave"
          class="rounded-lg bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
        >
          保存
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue"

const props = defineProps<{
  visible: boolean
  stock: any
  alerts: Record<string, any>
}>()

const emit = defineEmits<{
  close: []
  save: [code: string, form: any]
}>()

const form = ref({
  take_profit: "",
  stop_loss: "",
  change_alert: "",
  enabled: true,
})

// 打开时加载已有配置
watch(
  () => props.visible,
  (val) => {
    if (val && props.stock) {
      const existing = props.alerts[props.stock.code]
      form.value = {
        take_profit: existing?.take_profit || "",
        stop_loss: existing?.stop_loss || "",
        change_alert: existing?.change_alert || "",
        enabled: existing?.enabled ?? true,
      }
    }
  },
)

const handleSave = () => {
  if (props.stock) {
    emit("save", props.stock.code, { ...form.value })
    emit("close")
  }
}
</script>
