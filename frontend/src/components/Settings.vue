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
        
        <!-- AI 设置 -->
        <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
          <h2 class="text-lg font-semibold text-slate-700 mb-4">{{ $t('settings.ai_config') }}</h2>
          <div class="space-y-4">
             <div>
               <label class="block text-sm font-medium text-slate-600 mb-2">{{ $t('settings.ai_provider') }}</label>
               <select v-model="aiConfig.provider" @change="onProviderChange" class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white">
                 <option value="openai">OpenAI (GPT)</option>
                 <option value="gemini">Google Gemini</option>
                 <option value="claude">Anthropic Claude</option>
               </select>
             </div>
             <div>
               <label class="block text-sm font-medium text-slate-600 mb-2">API Key</label>
               <input v-model="aiConfig.apiKey" type="password" class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="sk-..." />
             </div>
             <div>
               <label class="block text-sm font-medium text-slate-600 mb-2">代理地址 (可选)</label>
               <input v-model="aiConfig.proxy" type="text" class="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="http://127.0.0.1:10808" />
               <p class="text-xs text-slate-400 mt-1">国内访问 Google/OpenAI/Claude 需要配置代理</p>
               <details class="mt-2 text-xs text-slate-500">
                 <summary class="cursor-pointer hover:text-slate-700">如何获取代理地址？</summary>
                 <div class="mt-2 p-3 bg-slate-50 rounded-lg space-y-1">
                   <p><strong>V2RayN:</strong> 主界面底部状态栏查看 "本地:[mixed:端口]"，如 <code class="bg-slate-200 px-1 rounded">http://127.0.0.1:10808</code></p>
                   <p><strong>Clash:</strong> 设置中查看 HTTP 端口，通常为 <code class="bg-slate-200 px-1 rounded">http://127.0.0.1:7890</code></p>
                   <p><strong>系统代理:</strong> Windows 设置 → 网络 → 代理 → 查看地址和端口</p>
                 </div>
               </details>
             </div>
             <div>
               <label class="block text-sm font-medium text-slate-600 mb-2">{{ $t('settings.ai_model') }}</label>
               <div class="flex gap-2">
                 <select v-if="modelList.length > 0" v-model="aiConfig.model" class="flex-1 px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white">
                   <option v-for="m in modelList" :key="m.id" :value="m.id">{{ m.name }}</option>
                 </select>
                 <input v-else v-model="aiConfig.model" type="text" class="flex-1 px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g. gpt-4o, gemini-pro" />
                 <button 
                   @click="fetchModels" 
                   :disabled="!aiConfig.apiKey || loadingModels"
                   class="px-4 py-2 bg-slate-100 text-slate-600 rounded-lg hover:bg-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm whitespace-nowrap"
                 >
                   {{ loadingModels ? '加载中...' : '获取模型' }}
                 </button>
               </div>
               <p v-if="modelError" class="text-xs text-red-500 mt-1">{{ modelError }}</p>
               <p v-else class="text-xs text-slate-400 mt-1">填写 API Key 后点击"获取模型"自动加载可用模型列表</p>
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
import { getSettings, updateSettings, getAIModels } from '../api'

const { t } = useI18n()
const emit = defineEmits(['back'])

// 设置数据
const settings = ref({
  refresh_interval: 5,
  alert_cooldown: 300,
  pushplus_token: '',
  dingtalk_webhook: '',
})

const aiConfig = ref({
  provider: 'openai',
  apiKey: '',
  model: '',
  proxy: ''
})

// 模型列表相关
const modelList = ref<{id: string, name: string}[]>([])
const loadingModels = ref(false)
const modelError = ref('')

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
      const s = res.settings
      // 基础设置
      settings.value = {
        refresh_interval: s.refresh_interval ?? 5,
        alert_cooldown: s.alert_cooldown ?? 300,
        pushplus_token: s.pushplus_token ?? '',
        dingtalk_webhook: s.dingtalk_webhook ?? '',
      }
      // AI 配置（从后端加载）
      aiConfig.value = {
        provider: s.ai_provider ?? 'gemini',
        apiKey: s.ai_api_key ?? '',
        model: s.ai_model ?? '',
        proxy: s.ai_proxy ?? '',
      }
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
    // 合并基础设置和 AI 配置，一起保存到后端
    const allSettings = {
      ...settings.value,
      ai_provider: aiConfig.value.provider,
      ai_api_key: aiConfig.value.apiKey,
      ai_model: aiConfig.value.model,
      ai_proxy: aiConfig.value.proxy,
    }
    
    const res = await updateSettings(allSettings)
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
  
  aiConfig.value = {
    provider: 'gemini',
    apiKey: '',
    model: '',
    proxy: ''
  }
  modelList.value = []
}

// 切换提供商时清空模型列表
const onProviderChange = () => {
  modelList.value = []
  aiConfig.value.model = ''
  modelError.value = ''
}

// 获取模型列表
const fetchModels = async () => {
  if (!aiConfig.value.apiKey) return
  
  loadingModels.value = true
  modelError.value = ''
  
  try {
    const res = await getAIModels(
      aiConfig.value.provider, 
      aiConfig.value.apiKey,
      aiConfig.value.proxy || undefined
    )
    if (res.status === 'success' && res.models?.length > 0) {
      modelList.value = res.models
      // 如果当前没有选中模型，自动选第一个
      if (!aiConfig.value.model) {
        aiConfig.value.model = res.models[0].id
      }
    } else {
      modelError.value = res.message || '未获取到可用模型'
    }
  } catch (e: any) {
    modelError.value = e.message || '获取模型列表失败，请检查网络或代理配置'
  } finally {
    loadingModels.value = false
  }
}

onMounted(() => {
  loadSettings()
})
</script>
