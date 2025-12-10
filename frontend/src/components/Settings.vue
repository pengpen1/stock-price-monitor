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
            ← {{ $t('common.back') }}
          </button>
          <h1 class="text-2xl font-bold text-slate-800">{{ $t('settings.title') }}</h1>
        </div>
      </div>

      <!-- 设置表单 -->
      <div class="space-y-6">
        <!-- 基础设置 -->
        <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
          <h2 class="text-lg font-semibold text-slate-700 mb-4">{{ $t('settings.basic') }}</h2>
          
          <div class="space-y-4">
            <!-- 刷新间隔 -->
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2">
                {{ $t('settings.refresh_interval') }}
              </label>
              <input 
                v-model.number="settings.refresh_interval" 
                type="number" 
                min="1" 
                max="60"
                class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p class="text-xs text-slate-400 mt-1">{{ $t('settings.refresh_hint') }}</p>
            </div>

            <!-- 预警冷却时间 -->
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2">
                {{ $t('settings.alert_cooldown') }}
              </label>
              <input 
                v-model.number="settings.alert_cooldown" 
                type="number" 
                min="60" 
                max="3600"
                class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p class="text-xs text-slate-400 mt-1">{{ $t('settings.alert_cooldown_hint') }}</p>
            </div>
          </div>
        </div>

        <!-- 推送设置 -->
        <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
          <h2 class="text-lg font-semibold text-slate-700 mb-4">{{ $t('settings.push_settings') }}</h2>
          
          <div class="space-y-4">
            <!-- PushPlus Token -->
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2">
                {{ $t('settings.pushplus_token') }}
                <a 
                  href="https://www.pushplus.plus/" 
                  target="_blank" 
                  class="text-blue-500 text-xs ml-2 hover:underline"
                >
                  {{ $t('settings.get_token') }}
                </a>
              </label>
              <input 
                v-model="settings.pushplus_token" 
                type="text" 
                :placeholder="$t('settings.pushplus_placeholder')"
                class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p class="text-xs text-slate-400 mt-1">{{ $t('settings.pushplus_hint') }}</p>
            </div>

            <!-- 钉钉 Webhook -->
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2">
                {{ $t('settings.dingtalk_webhook') }}
              </label>
              <input 
                v-model="settings.dingtalk_webhook" 
                type="text" 
                :placeholder="$t('settings.dingtalk_placeholder')"
                class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p class="text-xs text-slate-400 mt-1">{{ $t('settings.dingtalk_hint') }}</p>
            </div>
          </div>
        </div>

        <!-- 保存按钮 -->
        <div class="flex justify-end gap-3">
          <button 
            @click="resetSettings"
            class="px-6 py-2 text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
          >
            {{ $t('common.reset') }}
          </button>
          <button 
            @click="saveSettings"
            :disabled="saving"
            class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-blue-300 transition-colors"
          >
            {{ saving ? $t('common.saving') : $t('common.save_settings') }}
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
import { useI18n } from 'vue-i18n'
import { getSettings, updateSettings } from '../api'

const { t } = useI18n()
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
      message.value = t('common.settings_saved')
    } else {
      throw new Error(res.message || '保存失败')
    }
  } catch (e: any) {
    messageType.value = 'error'
    message.value = e.message || t('common.save_failed')
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
