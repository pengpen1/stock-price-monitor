<template>
  <div class="h-screen flex flex-col bg-slate-50">
    <!-- 顶部标题栏 -->
    <div class="bg-white border-b border-slate-200 px-4 py-3 flex items-center gap-3">
      <button @click="handleBack"
        class="p-2 text-slate-500 hover:bg-slate-100 rounded-lg transition-colors">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h1 class="text-lg font-semibold text-slate-800">笔记</h1>
    </div>

    <!-- 主内容区 -->
    <div class="flex-1 flex overflow-hidden">
      <!-- 左侧笔记列表 -->
      <div class="w-72 bg-white border-r border-slate-200 flex flex-col">
        <!-- 顶部操作栏 -->
        <div class="p-3 border-b border-slate-200 flex items-center gap-2">
          <button @click="showCreateModal = true"
            class="flex-1 px-3 py-2 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 transition-colors">
            新建笔记
          </button>
          <button @click="handleConvert" :disabled="!currentNote"
            class="px-3 py-2 text-sm border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
            title="转换为交易记录">
            转换
          </button>
        </div>

        <!-- 笔记列表 -->
        <div class="flex-1 overflow-auto">
          <div v-if="notes.length === 0" class="p-4 text-center text-slate-400 text-sm">
            暂无笔记，点击上方按钮创建
          </div>
          <div v-for="note in notes" :key="note.filename"
            @click="selectNote(note.filename)"
            :class="[
              'p-3 border-b border-slate-100 cursor-pointer transition-colors',
              currentNote === note.filename ? 'bg-blue-50 border-l-2 border-l-blue-500' : 'hover:bg-slate-50'
            ]">
            <div class="font-medium text-slate-800 truncate">{{ note.filename }}</div>
            <div class="text-xs text-slate-400 mt-1">{{ note.updated_at }}</div>
            <div class="text-xs text-slate-500 mt-1 truncate">{{ note.preview }}</div>
          </div>
        </div>
      </div>

      <!-- 右侧编辑区 -->
      <div class="flex-1 flex flex-col">
        <!-- 编辑器顶部栏 -->
        <div v-if="currentNote" class="p-3 border-b border-slate-200 flex items-center justify-between bg-white">
          <div class="flex items-center gap-2">
            <span class="font-medium text-slate-700">{{ currentNote }}.md</span>
            <span v-if="isDirty" class="text-xs text-orange-500">未保存</span>
            <span v-else-if="lastSaved" class="text-xs text-slate-400">已保存</span>
          </div>
          <div class="flex items-center gap-2">
            <button @click="togglePreview"
              :class="['px-3 py-1.5 text-sm rounded transition-colors', isPreview ? 'bg-blue-100 text-blue-600' : 'hover:bg-slate-100']">
              {{ isPreview ? '编辑' : '预览' }}
            </button>
            <button @click="saveNote" :disabled="!isDirty"
              class="px-3 py-1.5 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed">
              保存
            </button>
            <button @click="confirmDelete"
              class="px-3 py-1.5 text-sm text-red-500 hover:bg-red-50 rounded">
              删除
            </button>
          </div>
        </div>

        <!-- 编辑器/预览区 -->
        <div class="flex-1 overflow-hidden">
          <div v-if="!currentNote" class="h-full flex items-center justify-center text-slate-400">
            选择或创建一个笔记开始编辑
          </div>
          <div v-else class="h-full">
            <!-- 预览模式 -->
            <div v-if="isPreview" class="h-full overflow-auto p-6 prose prose-slate max-w-none" v-html="renderedContent"></div>
            <!-- 编辑模式 -->
            <textarea v-else v-model="content" @input="onContentChange"
              class="w-full h-full p-6 resize-none outline-none font-mono text-sm leading-relaxed"
              placeholder="开始写笔记...支持 Markdown 格式"></textarea>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建笔记弹窗 -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showCreateModal = false">
      <div class="bg-white rounded-lg shadow-xl w-96 p-6">
        <h3 class="text-lg font-semibold mb-4">新建笔记</h3>
        <input v-model="newNoteName" type="text" placeholder="输入笔记名称"
          class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          @keyup.enter="createNote">
        <div class="flex justify-end gap-2 mt-4">
          <button @click="showCreateModal = false" class="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg">取消</button>
          <button @click="createNote" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">创建</button>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showDeleteModal = false">
      <div class="bg-white rounded-lg shadow-xl w-96 p-6">
        <h3 class="text-lg font-semibold mb-2">确认删除</h3>
        <p class="text-slate-600 mb-4">确定要删除笔记「{{ currentNote }}」吗？此操作不可恢复。</p>
        <div class="flex justify-end gap-2">
          <button @click="showDeleteModal = false" class="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg">取消</button>
          <button @click="deleteNote" class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600">删除</button>
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { marked } from 'marked'
import ConvertTradeModal from './ConvertTradeModal.vue'
import { listNotes, getNote, createNoteApi, updateNoteApi, deleteNoteApi } from '../api'

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
const content = ref('')
const originalContent = ref('')
const isDirty = computed(() => content.value !== originalContent.value)
const lastSaved = ref(false)
const isPreview = ref(false)
const isLoading = ref(false)

// 弹窗状态
const showCreateModal = ref(false)
const showDeleteModal = ref(false)
const showConvertModal = ref(false)
const newNoteName = ref('')

// 自动保存定时器
let autoSaveTimer: ReturnType<typeof setTimeout> | null = null

// 渲染 Markdown
const renderedContent = computed(() => {
  return marked(content.value || '')
})

// 加载笔记列表
const loadNotes = async () => {
  try {
    const res = await listNotes()
    if (res.status === 'success') {
      notes.value = res.notes
    }
  } catch (e) {
    console.error('加载笔记列表失败:', e)
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
    if (res.status === 'success') {
      currentNote.value = filename
      content.value = res.content
      originalContent.value = res.content
      lastSaved.value = false
      isPreview.value = false
    }
  } catch (e) {
    console.error('加载笔记失败:', e)
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
    if (res.status === 'success') {
      showCreateModal.value = false
      newNoteName.value = ''
      await loadNotes()
      // 自动选中新创建的笔记
      await selectNote(name)
    } else {
      alert(res.message || '创建失败')
    }
  } catch (e) {
    console.error('创建笔记失败:', e)
  }
}

// 保存笔记
const saveNote = async () => {
  if (!currentNote.value || !isDirty.value) return
  
  try {
    const res = await updateNoteApi(currentNote.value, content.value)
    if (res.status === 'success') {
      originalContent.value = content.value
      lastSaved.value = true
      // 刷新列表以更新预览
      await loadNotes()
    }
  } catch (e) {
    console.error('保存笔记失败:', e)
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
    if (res.status === 'success') {
      showDeleteModal.value = false
      currentNote.value = null
      content.value = ''
      originalContent.value = ''
      await loadNotes()
    }
  } catch (e) {
    console.error('删除笔记失败:', e)
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
    alert('请先选择一个有内容的笔记')
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
  emit('back')
}

// 监听快捷键
const handleKeydown = (e: KeyboardEvent) => {
  // Ctrl+S 保存
  if (e.ctrlKey && e.key === 's') {
    e.preventDefault()
    saveNote()
  }
}

// 初始化
onMounted(() => {
  loadNotes()
  window.addEventListener('keydown', handleKeydown)
})

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }
})

// 清理
watch(() => currentNote.value, () => {
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }
})
</script>
