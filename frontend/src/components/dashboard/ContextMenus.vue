<!--
  ContextMenus.vue
  右键菜单组件（股票右键菜单 + 分组右键菜单）
-->
<template>
  <!-- 股票右键菜单 -->
  <div
    v-if="stockMenu.show"
    class="fixed z-50 min-w-32 rounded-lg border border-slate-200 bg-white py-1 shadow-xl"
    :style="{ left: stockMenu.x + 'px', top: stockMenu.y + 'px' }"
    @click.stop
  >
    <button
      @click="$emit('action', 'top')"
      class="w-full px-4 py-2 text-left text-sm hover:bg-slate-50"
    >
      📌 置顶
    </button>
    <button
      @click="$emit('action', 'bottom')"
      class="w-full px-4 py-2 text-left text-sm hover:bg-slate-50"
    >
      📍 置底
    </button>
    <div class="my-1 border-t border-slate-100"></div>
    <div class="px-4 py-2 text-xs text-slate-400">移动到分组</div>
    <button
      @click="$emit('action', 'group', '')"
      class="w-full px-4 py-2 text-left text-sm hover:bg-slate-50"
    >
      无分组
    </button>
    <button
      v-for="g in groupList"
      :key="g"
      @click="$emit('action', 'group', g)"
      class="w-full px-4 py-2 text-left text-sm hover:bg-slate-50"
    >
      {{ g }}
      <span v-if="stockGroups[stockMenu.stock?.code] === g" class="text-blue-500">✓</span>
    </button>
    <button
      @click="$emit('action', 'newGroup')"
      class="w-full px-4 py-2 text-left text-sm text-blue-500 hover:bg-blue-50"
    >
      + 新建分组
    </button>
    <div class="my-1 border-t border-slate-100"></div>
    <button
      @click="$emit('action', 'delete')"
      class="w-full px-4 py-2 text-left text-sm text-red-500 hover:bg-red-50"
    >
      🗑️ 删除
    </button>
  </div>

  <!-- 分组右键菜单 -->
  <div
    v-if="groupMenu.show"
    class="fixed z-50 min-w-40 rounded-lg border border-slate-200 bg-white py-1 shadow-xl"
    :style="{ left: groupMenu.x + 'px', top: groupMenu.y + 'px' }"
    @click.stop
  >
    <div class="border-b border-slate-100 px-4 py-2 text-xs text-slate-400">
      {{ groupMenu.group }}
    </div>
    <button
      @click="$emit('deleteGroup', false)"
      class="w-full px-4 py-2 text-left text-sm hover:bg-slate-50"
    >
      🗑️ 删除分组
    </button>
    <button
      @click="$emit('deleteGroup', true)"
      class="w-full px-4 py-2 text-left text-sm text-red-500 hover:bg-red-50"
    >
      ⚠️ 删除分组及股票
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  stockMenu: { show: boolean; x: number; y: number; stock: any }
  groupMenu: { show: boolean; x: number; y: number; group: string }
  groupList: string[]
  stockGroups: Record<string, string>
}>()

defineEmits<{
  action: [action: string, param?: string]
  deleteGroup: [deleteStocks: boolean]
}>()
</script>
