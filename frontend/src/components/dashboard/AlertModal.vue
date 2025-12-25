<!--
  AlertModal.vue
  预警设置弹窗组件
-->
<template>
  <div
    v-if="visible"
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    @click.self="$emit('close')"
  >
    <div class="bg-white rounded-xl shadow-xl w-96 p-6">
      <h3 class="text-lg font-semibold text-slate-800 mb-4">
        预警设置 - {{ stock?.name }}
      </h3>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-600 mb-1">止盈价格</label>
          <input
            v-model="form.take_profit"
            type="number"
            step="0.01"
            placeholder="价格达到时提醒"
            class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-600 mb-1">止损价格</label>
          <input
            v-model="form.stop_loss"
            type="number"
            step="0.01"
            placeholder="价格跌至时提醒"
            class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-600 mb-1">涨跌幅预警 (%)</label>
          <input
            v-model="form.change_alert"
            type="number"
            step="0.1"
            placeholder="涨跌幅达到时提醒"
            class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div class="flex items-center gap-2">
          <input v-model="form.enabled" type="checkbox" id="alert-enabled" class="w-4 h-4" />
          <label for="alert-enabled" class="text-sm text-slate-600">启用预警</label>
        </div>
      </div>
      <div class="flex justify-end gap-3 mt-6">
        <button @click="$emit('close')" class="px-4 py-2 text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50">
          取消
        </button>
        <button @click="handleSave" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
          保存
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

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
  take_profit: '',
  stop_loss: '',
  change_alert: '',
  enabled: true,
})

// 打开时加载已有配置
watch(() => props.visible, (val) => {
  if (val && props.stock) {
    const existing = props.alerts[props.stock.code]
    form.value = {
      take_profit: existing?.take_profit || '',
      stop_loss: existing?.stop_loss || '',
      change_alert: existing?.change_alert || '',
      enabled: existing?.enabled ?? true,
    }
  }
})

const handleSave = () => {
  if (props.stock) {
    emit('save', props.stock.code, { ...form.value })
    emit('close')
  }
}
</script>
