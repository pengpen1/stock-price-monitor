<template>
  <div class="flex h-screen flex-col bg-slate-50">
    <!-- 顶部标题栏 -->
    <div class="flex items-center gap-3 border-b border-slate-200 bg-white px-4 py-3">
      <button
        @click="handleBack"
        class="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100"
      >
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M15 19l-7-7 7-7"
          />
        </svg>
      </button>
      <h1 class="text-lg font-semibold text-slate-800">笔记</h1>
    </div>

    <!-- 主内容区 -->
    <div class="flex flex-1 overflow-hidden">
      <!-- 左侧笔记列表 -->
      <div class="flex w-72 flex-col border-r border-slate-200 bg-white">
        <!-- 顶部操作栏 -->
        <div class="flex items-center gap-2 border-b border-slate-200 p-3">
          <button
            @click="showCreateModal = true"
            class="flex-1 rounded-lg bg-blue-500 px-3 py-2 text-sm text-white transition-colors hover:bg-blue-600"
          >
            新建笔记
          </button>
          <button
            @click="handleConvert"
            :disabled="!currentNote"
            class="rounded-lg border border-slate-300 px-3 py-2 text-sm hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            title="转换为交易记录"
          >
            转换
          </button>
        </div>

        <!-- 笔记列表 -->
        <div class="flex-1 overflow-auto">
          <div v-if="notes.length === 0" class="p-4 text-center text-sm text-slate-400">
            暂无笔记，点击上方按钮创建
          </div>
          <div
            v-for="note in notes"
            :key="note.filename"
            @click="selectNote(note.filename)"
            :class="[
              'cursor-pointer border-b border-slate-100 p-3 transition-colors',
              currentNote === note.filename
                ? 'border-l-2 border-l-blue-500 bg-blue-50'
                : 'hover:bg-slate-50',
            ]"
          >
            <div class="truncate font-medium text-slate-800">
              {{ note.filename }}
            </div>
            <div class="mt-1 text-xs text-slate-400">{{ note.updated_at }}</div>
            <div class="mt-1 truncate text-xs text-slate-500">
              {{ note.preview }}
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧编辑区 -->
      <div class="flex flex-1 flex-col">
        <!-- 编辑器顶部栏 -->
        <div
          v-if="currentNote"
          class="flex items-center justify-between border-b border-slate-200 bg-white p-3"
        >
          <div class="flex items-center gap-2">
            <span class="font-medium text-slate-700">{{ currentNote }}.md</span>
            <span v-if="isDirty" class="text-xs text-orange-500">未保存</span>
            <span v-else-if="lastSaved" class="text-xs text-slate-400">已保存</span>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="togglePreview"
              :class="[
                'rounded px-3 py-1.5 text-sm transition-colors',
                isPreview ? 'bg-blue-100 text-blue-600' : 'hover:bg-slate-100',
              ]"
            >
              {{ isPreview ? "编辑" : "预览" }}
            </button>
            <button
              @click="saveNote"
              :disabled="!isDirty"
              class="rounded bg-blue-500 px-3 py-1.5 text-sm text-white hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              保存
            </button>
            <button
              @click="confirmDelete"
              class="rounded px-3 py-1.5 text-sm text-red-500 hover:bg-red-50"
            >
              删除
            </button>
          </div>
        </div>

        <!-- 编辑器/预览区 -->
        <div class="flex-1 overflow-hidden">
          <div v-if="!currentNote" class="flex h-full items-center justify-center text-slate-400">
            选择或创建一个笔记开始编辑
          </div>
          <div v-else class="h-full">
            <!-- 预览模式 -->
            <div
              v-if="isPreview"
              class="prose prose-slate h-full max-w-none overflow-auto p-6"
              v-html="renderedContent"
            ></div>
            <!-- 编辑模式 -->
            <textarea
              v-else
              v-model="content"
              @input="onContentChange"
              class="h-full w-full resize-none p-6 font-mono text-sm leading-relaxed outline-none"
              placeholder="开始写笔记...支持 Markdown 格式"
            ></textarea>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建笔记弹窗 -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="showCreateModal = false"
    >
      <div class="w-96 rounded-lg bg-white p-6 shadow-xl">
        <h3 class="mb-4 text-lg font-semibold">新建笔记</h3>
        <input
          v-model="newNoteName"
          type="text"
          placeholder="输入笔记名称"
          class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-transparent focus:ring-2 focus:ring-blue-500"
          @keyup.enter="createNote"
        />
        <div class="mt-4 flex justify-end gap-2">
          <button
            @click="showCreateModal = false"
            class="rounded-lg px-4 py-2 text-slate-600 hover:bg-slate-100"
          >
            取消
          </button>
          <button
            @click="createNote"
            class="rounded-lg bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
          >
            创建
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div
      v-if="showDeleteModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="showDeleteModal = false"
    >
      <div class="w-96 rounded-lg bg-white p-6 shadow-xl">
        <h3 class="mb-2 text-lg font-semibold">确认删除</h3>
        <p class="mb-4 text-slate-600">确定要删除笔记「{{ currentNote }}」吗？此操作不可恢复。</p>
        <div class="flex justify-end gap-2">
          <button
            @click="showDeleteModal = false"
            class="rounded-lg px-4 py-2 text-slate-600 hover:bg-slate-100"
          >
            取消
          </button>
          <button
            @click="deleteNote"
            class="rounded-lg bg-red-500 px-4 py-2 text-white hover:bg-red-600"
          >
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 转换交易记录弹窗 -->
    <ConvertTradeModal
      v-if="showConvertModal"
      :content="content"
      @close="showConvertModal = false"
      @converted="onTradesConverted"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from "vue"
import { marked } from "marked"
import ConvertTradeModal from "./ConvertTradeModal.vue"
import { listNotes, getNote, createNoteApi, updateNoteApi, deleteNoteApi } from "../api"

// 事件
const emit = defineEmits<{
  back: []
}>()

// 笔记类型
interface NoteMeta {
  filename: string
  created_at: string
  updated_at: string
  preview: string
  size: number
}

// 状态
const notes = ref<NoteMeta[]>([])
const currentNote = ref<string | null>(null)
const content = ref("")
const originalContent = ref("")
const isDirty = computed(() => content.value !== originalContent.value)
const lastSaved = ref(false)
const isPreview = ref(false)
const isLoading = ref(false)

// 弹窗状态
const showCreateModal = ref(false)
const showDeleteModal = ref(false)
const showConvertModal = ref(false)
const newNoteName = ref("")

// 自动保存定时器
let autoSaveTimer: ReturnType<typeof setTimeout> | null = null

// 渲染 Markdown
const renderedContent = computed(() => {
  return marked(content.value || "")
})

// 加载笔记列表
const loadNotes = async () => {
  try {
    const res = await listNotes()
    if (res.status === "success") {
      notes.value = res.notes
    }
  } catch (e) {
    console.error("加载笔记列表失败:", e)
  }
}

// 选择笔记
const selectNote = async (filename: string) => {
  // 如果有未保存的更改，先保存
  if (isDirty.value && currentNote.value) {
    await saveNote()
  }

  try {
    isLoading.value = true
    const res = await getNote(filename)
    if (res.status === "success") {
      currentNote.value = filename
      content.value = res.content
      originalContent.value = res.content
      lastSaved.value = false
      isPreview.value = false
    }
  } catch (e) {
    console.error("加载笔记失败:", e)
  } finally {
    isLoading.value = false
  }
}

// 创建笔记
const createNote = async () => {
  const name = newNoteName.value.trim()
  if (!name) return

  try {
    const res = await createNoteApi(name)
    if (res.status === "success") {
      showCreateModal.value = false
      newNoteName.value = ""
      await loadNotes()
      // 自动选中新创建的笔记
      await selectNote(name)
    } else {
      alert(res.message || "创建失败")
    }
  } catch (e) {
    console.error("创建笔记失败:", e)
  }
}

// 保存笔记
const saveNote = async () => {
  if (!currentNote.value || !isDirty.value) return

  try {
    const res = await updateNoteApi(currentNote.value, content.value)
    if (res.status === "success") {
      originalContent.value = content.value
      lastSaved.value = true
      // 刷新列表以更新预览
      await loadNotes()
    }
  } catch (e) {
    console.error("保存笔记失败:", e)
  }
}

// 删除确认
const confirmDelete = () => {
  showDeleteModal.value = true
}

// 删除笔记
const deleteNote = async () => {
  if (!currentNote.value) return

  try {
    const res = await deleteNoteApi(currentNote.value)
    if (res.status === "success") {
      showDeleteModal.value = false
      currentNote.value = null
      content.value = ""
      originalContent.value = ""
      await loadNotes()
    }
  } catch (e) {
    console.error("删除笔记失败:", e)
  }
}

// 切换预览模式
const togglePreview = () => {
  isPreview.value = !isPreview.value
}

// 内容变化处理（自动保存）
const onContentChange = () => {
  lastSaved.value = false

  // 清除之前的定时器
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }

  // 3秒后自动保存
  autoSaveTimer = setTimeout(() => {
    if (isDirty.value) {
      saveNote()
    }
  }, 3000)
}

// 转换为交易记录
const handleConvert = () => {
  if (!currentNote.value || !content.value.trim()) {
    alert("请先选择一个有内容的笔记")
    return
  }
  showConvertModal.value = true
}

// 转换完成回调
const onTradesConverted = () => {
  showConvertModal.value = false
}

// 返回上一页
const handleBack = async () => {
  // 如果有未保存的更改，先保存
  if (isDirty.value && currentNote.value) {
    await saveNote()
  }
  emit("back")
}

// 监听快捷键
const handleKeydown = (e: KeyboardEvent) => {
  // Ctrl+S 保存
  if (e.ctrlKey && e.key === "s") {
    e.preventDefault()
    saveNote()
  }
}

// 初始化
onMounted(() => {
  loadNotes()
  window.addEventListener("keydown", handleKeydown)
})

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener("keydown", handleKeydown)
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }
})

// 清理
watch(
  () => currentNote.value,
  () => {
    if (autoSaveTimer) {
      clearTimeout(autoSaveTimer)
    }
  },
)
</script>
