<!--
  GroupModal.vue
  新建分组弹窗组件
-->
<template>
  <div
    v-if="visible"
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    @click.self="$emit('close')"
  >
    <div class="bg-white rounded-xl shadow-xl w-80 p-6">
      <h3 class="text-lg font-semibold text-slate-800 mb-4">新建分组</h3>
      <p v-if="pendingStock" class="text-xs text-slate-500 mb-2">
        创建后将把当前股票移动到此分组
      </p>
      <input
        v-model="groupName"
        placeholder="输入分组名称"
        @keyup.enter="handleAdd"
        class="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
      />
      <div class="flex justify-end gap-3">
        <button @click="$emit('close')" class="px-4 py-2 text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50">
          取消
        </button>
        <button @click="handleAdd" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
          确定
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  visible: boolean
  pendingStock?: string | null
}>()

const emit = defineEmits<{
  close: []
  add: [name: string, pendingStock?: string]
}>()

const groupName = ref('')

watch(() => props.visible, (val) => {
  if (!val) groupName.value = ''
})

const handleAdd = () => {
  if (groupName.value.trim()) {
    emit('add', groupName.value.trim(), props.pendingStock || undefined)
    emit('close')
  }
}
</script>
