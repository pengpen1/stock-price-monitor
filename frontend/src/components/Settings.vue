<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
    <div class="mx-auto max-w-2xl">
      <!-- 头部 -->
      <div class="mb-6 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <button
            @click="$emit('back')"
            class="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700"
          >
            ← {{ $t("common.back") }}
          </button>
          <h1 class="text-2xl font-bold text-slate-800">
            {{ $t("settings.title") }}
          </h1>
        </div>
      </div>

      <!-- 设置表单 -->
      <div class="space-y-6">
        <!-- 基础设置 -->
        <div class="rounded-xl border border-slate-100 bg-white p-6 shadow-sm">
          <h2 class="mb-4 text-lg font-semibold text-slate-700">
            {{ $t("settings.basic") }}
          </h2>

          <div class="space-y-4">
            <!-- 刷新间隔 -->
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-600">
                {{ $t("settings.refresh_interval") }}
              </label>
              <input
                v-model.number="settings.refresh_interval"
                type="number"
                min="1"
                max="60"
                class="w-full rounded-lg border border-slate-200 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
              <p class="mt-1 text-xs text-slate-400">
                {{ $t("settings.refresh_hint") }}
              </p>
            </div>

            <!-- 预警冷却时间 -->
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-600">
                {{ $t("settings.alert_cooldown") }}
              </label>
              <input
                v-model.number="settings.alert_cooldown"
                type="number"
                min="60"
                max="3600"
                class="w-full rounded-lg border border-slate-200 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
              <p class="mt-1 text-xs text-slate-400">
                {{ $t("settings.alert_cooldown_hint") }}
              </p>
            </div>
          </div>
        </div>

        <!-- AI 设置 -->
        <div class="rounded-xl border border-slate-100 bg-white p-6 shadow-sm">
          <h2 class="mb-4 text-lg font-semibold text-slate-700">
            {{ $t("settings.ai_config") }}
          </h2>
          <div class="space-y-4">
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-600">{{
                $t("settings.ai_provider")
              }}</label>
              <select
                v-model="aiConfig.provider"
                @change="onProviderChange"
                class="w-full rounded-lg border border-slate-200 bg-white px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                <option value="openai">OpenAI (GPT)</option>
                <option value="gemini">Google Gemini</option>
                <option value="claude">Anthropic Claude</option>
              </select>
            </div>
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-600">API Key</label>
              <input
                v-model="aiConfig.apiKey"
                type="password"
                class="w-full rounded-lg border border-slate-200 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="sk-..."
              />
            </div>
            <div v-if="aiConfig.provider === 'openai'">
              <label class="mb-2 block text-sm font-medium text-slate-600"
                >自定义 API地址 (可选)</label
              >
              <input
                v-model="aiConfig.baseUrl"
                type="text"
                class="w-full rounded-lg border border-slate-200 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="https://api.openai.com"
              />
              <p class="mt-1 text-xs text-slate-400">
                如果使用中转服务或兼容接口(如DeepSeek/Kimi)，请填写相应的 Base URL
              </p>
            </div>
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-600">代理地址 (可选)</label>
              <input
                v-model="aiConfig.proxy"
                type="text"
                class="w-full rounded-lg border border-slate-200 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                placeholder="http://127.0.0.1:10808"
              />
              <p class="mt-1 text-xs text-slate-400">国内访问 Google/OpenAI/Claude 需要配置代理</p>
              <details class="mt-2 text-xs text-slate-500">
                <summary class="cursor-pointer hover:text-slate-700">如何获取代理地址？</summary>
                <div class="mt-2 space-y-1 rounded-lg bg-slate-50 p-3">
                  <p>
                    <strong>V2RayN:</strong> 主界面底部状态栏查看 "本地:[mixed:端口]"，如
                    <code class="rounded bg-slate-200 px-1">http://127.0.0.1:10808</code>
                  </p>
                  <p>
                    <strong>Clash:</strong> 设置中查看 HTTP 端口，通常为
                    <code class="rounded bg-slate-200 px-1">http://127.0.0.1:7890</code>
                  </p>
                  <p><strong>系统代理:</strong> Windows 设置 → 网络 → 代理 → 查看地址和端口</p>
                </div>
              </details>
            </div>
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-600">{{
                $t("settings.ai_model")
              }}</label>
              <div class="flex gap-2">
                <select
                  v-if="modelList.length > 0"
                  v-model="aiConfig.model"
                  class="flex-1 rounded-lg border border-slate-200 bg-white px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                >
                  <option v-for="m in modelList" :key="m.id" :value="m.id">
                    {{ m.name }}
                  </option>
                </select>
                <input
                  v-else
                  v-model="aiConfig.model"
                  type="text"
                  class="flex-1 rounded-lg border border-slate-200 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  placeholder="e.g. gpt-4o, gemini-pro"
                />
                <button
                  @click="fetchModels"
                  :disabled="!aiConfig.apiKey || loadingModels"
                  class="rounded-lg bg-slate-100 px-4 py-2 text-sm whitespace-nowrap text-slate-600 transition-colors hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {{ loadingModels ? "加载中..." : "获取模型" }}
                </button>
              </div>
              <p v-if="modelError" class="mt-1 text-xs text-red-500">
                {{ modelError }}
              </p>
              <p v-else class="mt-1 text-xs text-slate-400">
                填写 API Key 后点击"获取模型"自动加载可用模型列表
              </p>
            </div>
          </div>
        </div>

        <!-- 推送设置 -->
        <div class="rounded-xl border border-slate-100 bg-white p-6 shadow-sm">
          <h2 class="mb-4 text-lg font-semibold text-slate-700">
            {{ $t("settings.push_settings") }}
          </h2>

          <div class="space-y-4">
            <!-- PushPlus Token -->
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-600">
                {{ $t("settings.pushplus_token") }}
                <a
                  href="https://www.pushplus.plus/"
                  target="_blank"
                  class="ml-2 text-xs text-blue-500 hover:underline"
                >
                  {{ $t("settings.get_token") }}
                </a>
              </label>
              <input
                v-model="settings.pushplus_token"
                type="text"
                :placeholder="$t('settings.pushplus_placeholder')"
                class="w-full rounded-lg border border-slate-200 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
              <p class="mt-1 text-xs text-slate-400">
                {{ $t("settings.pushplus_hint") }}
              </p>
            </div>

            <!-- 钉钉 Webhook -->
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-600">
                {{ $t("settings.dingtalk_webhook") }}
              </label>
              <input
                v-model="settings.dingtalk_webhook"
                type="text"
                :placeholder="$t('settings.dingtalk_placeholder')"
                class="w-full rounded-lg border border-slate-200 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
              <p class="mt-1 text-xs text-slate-400">
                {{ $t("settings.dingtalk_hint") }}
              </p>
            </div>
          </div>
        </div>

        <!-- 数据管理 -->
        <div class="rounded-xl border border-slate-100 bg-white p-6 shadow-sm">
          <h2 class="mb-4 text-lg font-semibold text-slate-700">数据管理</h2>

          <div class="space-y-4">
            <!-- 数据存储路径 -->
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-600">数据存储路径</label>
              <div class="flex gap-2">
                <input
                  v-model="dataPath.current"
                  type="text"
                  class="flex-1 rounded-lg border border-slate-200 px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  placeholder="留空使用默认路径"
                />
                <button
                  @click="applyDataPath"
                  :disabled="savingPath"
                  class="rounded-lg bg-slate-100 px-4 py-2 text-sm whitespace-nowrap text-slate-600 transition-colors hover:bg-slate-200 disabled:opacity-50"
                >
                  {{ savingPath ? "保存中..." : "应用" }}
                </button>
                <button
                  @click="resetDataPath"
                  class="px-4 py-2 text-sm whitespace-nowrap text-slate-500 transition-colors hover:text-slate-700"
                >
                  恢复默认
                </button>
              </div>
              <p class="mt-1 text-xs text-slate-400">
                默认路径: {{ dataPath.default || "加载中..." }}
                <span v-if="dataPath.isCustom" class="ml-2 text-blue-500"
                  >(当前使用自定义路径)</span
                >
              </p>
            </div>

            <!-- 导入导出 -->
            <div>
              <label class="mb-2 block text-sm font-medium text-slate-600">配置导入/导出</label>
              <div class="flex gap-2">
                <button
                  @click="handleExport"
                  :disabled="exporting"
                  class="rounded-lg bg-green-500 px-4 py-2 text-sm text-white transition-colors hover:bg-green-600 disabled:opacity-50"
                >
                  {{ exporting ? "导出中..." : "导出配置" }}
                </button>
                <label
                  class="cursor-pointer rounded-lg bg-blue-500 px-4 py-2 text-sm text-white transition-colors hover:bg-blue-600"
                >
                  导入配置
                  <input type="file" accept=".json" @change="handleImport" class="hidden" />
                </label>
              </div>
              <p class="mt-1 text-xs text-slate-400">
                导出/导入股票列表、分组、设置、预警配置（不含 API Key）
              </p>
            </div>
          </div>
        </div>

        <!-- 保存按钮 -->
        <div class="flex justify-end gap-3">
          <button
            @click="resetSettings"
            class="rounded-lg border border-slate-200 px-6 py-2 text-slate-600 transition-colors hover:bg-slate-50"
          >
            {{ $t("common.reset") }}
          </button>
          <button
            @click="saveSettings"
            :disabled="saving"
            class="rounded-lg bg-blue-500 px-6 py-2 text-white transition-colors hover:bg-blue-600 disabled:bg-blue-300"
          >
            {{ saving ? $t("common.saving") : $t("common.save_settings") }}
          </button>
        </div>

        <!-- 提示信息 -->
        <div v-if="message" :class="messageClass" class="rounded-lg p-4 text-sm">
          {{ message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { useI18n } from "vue-i18n"
import {
  getSettings,
  updateSettings,
  getAIModels,
  exportData,
  importData,
  getDataPath,
  setDataPath,
} from "../api"

const { t } = useI18n()
const emit = defineEmits(["back"])

// 设置数据
const settings = ref({
  refresh_interval: 5,
  alert_cooldown: 300,
  pushplus_token: "",
  dingtalk_webhook: "",
})

const aiConfig = ref({
  provider: "openai",
  apiKey: "",
  model: "",
  proxy: "",
  baseUrl: "",
})

// 模型列表相关
const modelList = ref<{ id: string; name: string }[]>([])
const loadingModels = ref(false)
const modelError = ref("")

const saving = ref(false)
const message = ref("")
const messageType = ref<"success" | "error">("success")

// 数据路径相关
const dataPath = ref({
  current: "",
  default: "",
  isCustom: false,
})
const savingPath = ref(false)
const exporting = ref(false)

const messageClass = computed(() => {
  return messageType.value === "success"
    ? "bg-green-50 text-green-600 border border-green-200"
    : "bg-red-50 text-red-600 border border-red-200"
})

// 保存各提供商的配置缓存
const providerConfigs = ref<Record<string, any>>({})
const previousProvider = ref("")

// 加载设置
const loadSettings = async () => {
  try {
    const res = await getSettings()
    if (res.status === "success") {
      const s = res.settings
      // 基础设置
      settings.value = {
        refresh_interval: s.refresh_interval ?? 5,
        alert_cooldown: s.alert_cooldown ?? 300,
        pushplus_token: s.pushplus_token ?? "",
        dingtalk_webhook: s.dingtalk_webhook ?? "",
      }

      // 加载提供商配置缓存
      if (s.provider_configs) {
        providerConfigs.value = s.provider_configs
      }

      // AI 配置（从后端加载）
      aiConfig.value = {
        provider: s.ai_provider ?? "gemini",
        apiKey: s.ai_api_key ?? "",
        model: s.ai_model ?? "",
        proxy: s.ai_proxy ?? "",
        baseUrl: s.ai_base_url ?? "",
      }

      // 初始化当前提供商
      previousProvider.value = aiConfig.value.provider

      // 确保当前配置也保存到缓存中（如果是第一次加载）
      if (!providerConfigs.value[aiConfig.value.provider]) {
        saveCurrentToConfig(aiConfig.value.provider)
      }
    }
  } catch (e) {
    console.error("加载设置失败:", e)
  }
}

// 保存设置
const saveSettings = async () => {
  saving.value = true
  message.value = ""

  try {
    // 合并基础设置和 AI 配置，一起保存到后端
    saveCurrentToConfig(aiConfig.value.provider) // 保存当前编辑的状态到缓存

    // 确保当前使用的配置也是最新的
    const currentConfig = providerConfigs.value[aiConfig.value.provider] || {}

    const allSettings = {
      ...settings.value,
      ai_provider: aiConfig.value.provider,
      ai_api_key: aiConfig.value.apiKey,
      ai_model: aiConfig.value.model,
      ai_proxy: aiConfig.value.proxy,
      ai_base_url: aiConfig.value.baseUrl,
      provider_configs: providerConfigs.value, // 保存所有提供商的配置
    }

    const res = await updateSettings(allSettings)
    if (res.status === "success") {
      messageType.value = "success"
      message.value = t("common.settings_saved")
    } else {
      throw new Error(res.message || "保存失败")
    }
  } catch (e: any) {
    messageType.value = "error"
    message.value = e.message || t("common.save_failed")
  } finally {
    saving.value = false
    // 3秒后清除消息
    setTimeout(() => {
      message.value = ""
    }, 3000)
  }
}

// 重置设置
const resetSettings = () => {
  settings.value = {
    refresh_interval: 5,
    alert_cooldown: 300,
    pushplus_token: "",
    dingtalk_webhook: "",
  }

  aiConfig.value = {
    provider: "gemini",
    apiKey: "",
    model: "",
    proxy: "",
    baseUrl: "",
  }
  modelList.value = []
}

// 保存当前配置到缓存
const saveCurrentToConfig = (provider: string) => {
  if (!provider) return
  providerConfigs.value[provider] = {
    apiKey: aiConfig.value.apiKey,
    model: aiConfig.value.model,
    proxy: aiConfig.value.proxy,
    baseUrl: aiConfig.value.baseUrl,
  }
}

// 从缓存加载配置
const loadFromConfig = (provider: string) => {
  const config = providerConfigs.value[provider]
  if (config) {
    aiConfig.value.apiKey = config.apiKey || ""
    aiConfig.value.model = config.model || ""
    aiConfig.value.proxy = config.proxy || ""
    aiConfig.value.baseUrl = config.baseUrl || ""
  } else {
    // 如果没有缓存，清空输入框
    aiConfig.value.apiKey = ""
    aiConfig.value.model = ""
    // proxy 尽量保留? 还是清空? 一般代理是通用的，但在这种设计下还是分开存吧，或者让用户自己决定
    // 这里选择清空，保证隔离
    aiConfig.value.proxy = ""
    aiConfig.value.baseUrl = ""
  }
}

// 切换提供商
const onProviderChange = () => {
  // 1. 保存旧提供商的配置
  if (previousProvider.value) {
    // 注意：此时 aiConfig.value 中的数据其实是旧的吗？
    // 不，v-model 绑定的 apiKey 等字段还没变，但是 provider 已经是新的了
    // 哎呀不对，v-model 是绑定在 input 上的。
    // 当 select change 时，aiConfig.provider 变了。
    // 但是 apiKey input 的 value 还是屏幕上显示的那些（也就是旧 provider 的 key）。
    // 所以此时保存 previousProvider 对应的应该是当前的 input 值。
    // 是的，因为 input 还没被重新赋值。
    // 等等，Vue 的响应式更新...
    // 如果我在 change 事件中执行，此时 dom 可能还没更新？或者数据只是刚变？
    // 只要我还没调用 `loadFromConfig(newProvider)` 来覆盖 aiConfig 的其他字段，
    // 那么 aiConfig.apiKey 依然是旧的值。
    // 所以：保存旧值 -> 加载新值 -> 更新 previous

    // 这里有个问题：因为 provider 已经变了，如果我调用 saveCurrentToConfig(previousProvider.value)，
    // 它会读取 aiConfig.apiKey (旧值)，存入 providerConfigs[old]。这是对的。
    saveCurrentToConfig(previousProvider.value)
  }

  // 2. 加载新提供商的配置
  loadFromConfig(aiConfig.value.provider)

  // 3. 更新 previous
  previousProvider.value = aiConfig.value.provider

  // 4. 清空模型列表
  modelList.value = []
  modelError.value = ""
}

// 获取模型列表
const fetchModels = async () => {
  if (!aiConfig.value.apiKey) return

  loadingModels.value = true
  modelError.value = ""

  try {
    const res = await getAIModels(
      aiConfig.value.provider,
      aiConfig.value.apiKey,
      aiConfig.value.proxy || undefined,
      aiConfig.value.baseUrl || undefined,
    )
    if (res.status === "success" && res.models?.length > 0) {
      modelList.value = res.models
      // 如果当前没有选中模型，自动选第一个
      if (!aiConfig.value.model) {
        aiConfig.value.model = res.models[0].id
      }
    } else {
      modelError.value = res.message || "未获取到可用模型"
    }
  } catch (e: any) {
    modelError.value = e.message || "获取模型列表失败，请检查网络或代理配置"
  } finally {
    loadingModels.value = false
  }
}

// 加载数据路径
const loadDataPath = async () => {
  try {
    const res = await getDataPath()
    if (res.status === "success") {
      dataPath.value = {
        current: res.is_custom ? res.current_path : "",
        default: res.default_path,
        isCustom: res.is_custom,
      }
    }
  } catch (e) {
    console.error("加载数据路径失败:", e)
  }
}

// 应用数据路径
const applyDataPath = async () => {
  savingPath.value = true
  try {
    const res = await setDataPath(dataPath.value.current)
    if (res.status === "success") {
      messageType.value = "success"
      message.value = res.message
      await loadDataPath()
    } else {
      throw new Error(res.message)
    }
  } catch (e: any) {
    messageType.value = "error"
    message.value = e.message || "设置路径失败"
  } finally {
    savingPath.value = false
    setTimeout(() => {
      message.value = ""
    }, 3000)
  }
}

// 恢复默认路径
const resetDataPath = async () => {
  dataPath.value.current = ""
  await applyDataPath()
}

// 导出配置
const handleExport = async () => {
  exporting.value = true
  try {
    const res = await exportData()
    if (res.status === "success") {
      // 移除敏感信息
      const data = res.data
      if (data.settings) {
        delete data.settings.ai_api_key
      }

      // 下载 JSON 文件
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `stock-monitor-config-${new Date().toISOString().slice(0, 10)}.json`
      a.click()
      URL.revokeObjectURL(url)

      messageType.value = "success"
      message.value = "配置已导出"
    }
  } catch (e: any) {
    messageType.value = "error"
    message.value = e.message || "导出失败"
  } finally {
    exporting.value = false
    setTimeout(() => {
      message.value = ""
    }, 3000)
  }
}

// 导入配置
const handleImport = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  try {
    const text = await file.text()
    const data = JSON.parse(text)

    // 确认导入
    if (!confirm("导入将覆盖当前配置，是否继续？")) {
      input.value = ""
      return
    }

    const res = await importData({
      stocks: data.stocks,
      settings: data.settings,
      alerts: data.alerts,
    })

    if (res.status === "success") {
      messageType.value = "success"
      message.value = res.message
      // 重新加载设置
      await loadSettings()
    } else {
      throw new Error(res.message)
    }
  } catch (e: any) {
    messageType.value = "error"
    message.value = e.message || "导入失败，请检查文件格式"
  } finally {
    input.value = ""
    setTimeout(() => {
      message.value = ""
    }, 3000)
  }
}

onMounted(() => {
  loadSettings()
  loadDataPath()
})
</script>
