/**
 * 设置 Store
 * 管理应用设置和 AI 配置
 */
import { defineStore } from "pinia"
import { ref, watch } from "vue"
import { getSettings, updateSettings, getAIModels } from "@/api"

// AI 配置接口
export interface AIConfig {
  provider: string
  apiKey: string
  model: string
  proxy: string
}

// 模型信息接口
export interface ModelInfo {
  id: string
  name: string
}

export const useSettingsStore = defineStore("settings", () => {
  // 基础设置
  const refreshInterval = ref(3)
  const alertCooldown = ref(300)

  // AI 配置
  const aiConfig = ref<AIConfig>({
    provider: "gemini",
    apiKey: "",
    model: "",
    proxy: "",
  })

  // 模型列表
  const modelList = ref<ModelInfo[]>([])
  const loadingModels = ref(false)
  const modelError = ref("")

  // 从后端加载设置
  const loadSettings = async () => {
    try {
      const data = await getSettings()
      refreshInterval.value = data.refresh_interval || 3
      alertCooldown.value = data.alert_cooldown || 300

      if (data.ai_config) {
        aiConfig.value = {
          provider: data.ai_config.provider || "gemini",
          apiKey: data.ai_config.api_key || "",
          model: data.ai_config.model || "",
          proxy: data.ai_config.proxy || "",
        }
      }
    } catch (e) {
      console.error("加载设置失败:", e)
    }
  }

  // 保存设置到后端
  const saveSettings = async () => {
    try {
      await updateSettings({
        refresh_interval: refreshInterval.value,
        alert_cooldown: alertCooldown.value,
        ai_config: {
          provider: aiConfig.value.provider,
          api_key: aiConfig.value.apiKey,
          model: aiConfig.value.model,
          proxy: aiConfig.value.proxy,
        },
      })
    } catch (e) {
      console.error("保存设置失败:", e)
    }
  }

  // 获取模型列表
  const fetchModels = async () => {
    if (!aiConfig.value.apiKey) {
      modelError.value = "请先输入 API Key"
      return
    }

    loadingModels.value = true
    modelError.value = ""

    try {
      const res = await getAIModels(
        aiConfig.value.provider,
        aiConfig.value.apiKey,
        aiConfig.value.proxy || undefined,
      )

      if (res.status === "success") {
        modelList.value = res.models || []
        if (modelList.value.length > 0 && !aiConfig.value.model) {
          aiConfig.value.model = modelList.value[0].id
        }
      } else {
        modelError.value = res.message || "获取模型列表失败"
      }
    } catch (e: any) {
      modelError.value = e.message || "网络错误"
    } finally {
      loadingModels.value = false
    }
  }

  // 切换 provider 时清空模型列表
  const onProviderChange = () => {
    modelList.value = []
    aiConfig.value.model = ""
  }

  // 监听设置变化自动保存
  watch([refreshInterval, alertCooldown, aiConfig], saveSettings, {
    deep: true,
  })

  return {
    refreshInterval,
    alertCooldown,
    aiConfig,
    modelList,
    loadingModels,
    modelError,
    loadSettings,
    saveSettings,
    fetchModels,
    onProviderChange,
  }
})
