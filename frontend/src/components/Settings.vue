<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
    <div class="max-w-2xl mx-auto">
      <!-- 头部 -->
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-3">
          <button 
            @click="$emit('back')" 
            class="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
          >
            ← 返回
          </button>
          <h1 class="text-2xl font-bold text-slate-800">设置</h1>
        </div>
      </div>

      <!-- 设置表单 -->
      <div class="space-y-6">
        <!-- 基础设置 -->
        <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
          <h2 class="text-lg font-semibold text-slate-700 mb-4">基础设置</h2>
          
          <div class="space-y-4">
            <!-- 刷新间隔 -->
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2">
                数据刷新间隔（秒）
              </label>
              <input 
                v-model.number="settings.refresh_interval" 
                type="number" 
                min="1" 
                max="60"
                class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p class="text-xs text-slate-400 mt-1">建议 3-10 秒，过快可能被限流</p>
            </div>

            <!-- 预警冷却时间 -->
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2">
                预警冷却时间（秒）
              </label>
              <input 
                v-model.number="settings.alert_cooldown" 
                type="number" 
                min="60" 
                max="3600"
                class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p class="text-xs text-slate-400 mt-1">同一股票触发预警后的冷却时间，避免重复推送</p>
            </div>
          </div>
        </div>

        <!-- 推送设置 -->
        <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
          <h2 class="text-lg font-semibold text-slate-700 mb-4">消息推送</h2>
          
          <div class="space-y-4">
            <!-- PushPlus Token -->
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2">
                PushPlus Token
                <a 
                  href="https://www.pushplus.plus/" 
                  target="_blank" 
                  class="text-blue-500 text-xs ml-2 hover:underline"
                >
                  获取 Token →
                </a>
              </label>
              <input 
                v-model="settings.pushplus_token" 
                type="text" 
                placeholder="请输入 PushPlus Token"
                class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p class="text-xs text-slate-400 mt-1">用于微信推送预警消息</p>
            </div>

            <!-- 钉钉 Webhook -->
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2">
                钉钉机器人 Webhook
              </label>
              <input 
                v-model="settings.dingtalk_webhook" 
                type="text" 
                placeholder="请输入钉钉机器人 Webhook URL"
                class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p class="text-xs text-slate-400 mt-1">用于钉钉群推送预警消息</p>
            </div>
          </div>
        </div>

        <!-- 保存按钮 -->
        <div class="flex justify-end gap-3">
          <button 
            @click="resetSettings"
            class="px-6 py-2 text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
          >
            重置
          </button>
          <button 
            @click="saveSettings"
            :disabled="saving"
            class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-blue-300 transition-colors"
          >
            {{ saving ? '保存中...' : '保存设置' }}
          </button>
        </div>

        <!-- 提示信息 -->
        <div v-if="message" :class="messageClass" class="p-4 rounded-lg text-sm">
          {{ message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getSettings, updateSettings } from '../api'

const emit = defineEmits(['back'])

// 设置数据
const settings = ref({
  refresh_interval: 5,
  alert_cooldown: 300,
  pushplus_token: '',
  dingtalk_webhook: '',
})

const saving = ref(false)
const message = ref('')
const messageType = ref<'success' | 'error'>('success')

const messageClass = computed(() => {
  return messageType.value === 'success' 
    ? 'bg-green-50 text-green-600 border border-green-200'
    : 'bg-red-50 text-red-600 border border-red-200'
})

// 加载设置
const loadSettings = async () => {
  try {
    const res = await getSettings()
    if (res.status === 'success') {
      settings.value = { ...settings.value, ...res.settings }
    }
  } catch (e) {
    console.error('加载设置失败:', e)
  }
}

// 保存设置
const saveSettings = async () => {
  saving.value = true
  message.value = ''
  
  try {
    const res = await updateSettings(settings.value)
    if (res.status === 'success') {
      messageType.value = 'success'
      message.value = '设置已保存'
    } else {
      throw new Error(res.message || '保存失败')
    }
  } catch (e: any) {
    messageType.value = 'error'
    message.value = e.message || '保存设置失败，请检查后端连接'
  } finally {
    saving.value = false
    // 3秒后清除消息
    setTimeout(() => { message.value = '' }, 3000)
  }
}

// 重置设置
const resetSettings = () => {
  settings.value = {
    refresh_interval: 5,
    alert_cooldown: 300,
    pushplus_token: '',
    dingtalk_webhook: '',
  }
}

onMounted(() => {
  loadSettings()
})
</script>
