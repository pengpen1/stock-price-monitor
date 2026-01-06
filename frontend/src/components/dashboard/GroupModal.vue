<!--
  GroupModal.vue
  新建分组弹窗组件
-->
<template>
  <div
    v-if="visible"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click.self="$emit('close')"
  >
    <div class="w-80 rounded-xl bg-white p-6 shadow-xl">
      <h3 class="mb-4 text-lg font-semibold text-slate-800">新建分组</h3>
      <p v-if="pendingStock" class="mb-2 text-xs text-slate-500">创建后将把当前股票移动到此分组</p>
      <input
        v-model="groupName"
        placeholder="输入分组名称"
        @keyup.enter="handleAdd"
        class="mb-4 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
      />
      <div class="flex justify-end gap-3">
        <button
          @click="$emit('close')"
          class="rounded-lg border border-slate-200 px-4 py-2 text-slate-600 hover:bg-slate-50"
        >
          取消
        </button>
        <button
          @click="handleAdd"
          class="rounded-lg bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
        >
          确定
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue"

const props = defineProps<{
  visible: boolean
  pendingStock?: string | null
}>()

const emit = defineEmits<{
  close: []
  add: [name: string, pendingStock?: string]
}>()

const groupName = ref("")

watch(
  () => props.visible,
  (val) => {
    if (!val) groupName.value = ""
  },
)

const handleAdd = () => {
  if (groupName.value.trim()) {
    emit("add", groupName.value.trim(), props.pendingStock || undefined)
    emit("close")
  }
}
</script>
