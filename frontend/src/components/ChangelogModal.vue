<template>
  <div v-if="visible" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm" @click.self="close">
    <div class="bg-white rounded-xl shadow-2xl w-[500px] max-h-[80vh] flex flex-col overflow-hidden">
      <!-- 头部 -->
      <div class="flex justify-between items-center p-4 border-b border-slate-100 bg-gradient-to-r from-blue-500 to-blue-600">
        <div class="flex items-center gap-2">
          <span class="text-2xl">📋</span>
          <h3 class="text-lg font-semibold text-white">更新日志</h3>
        </div>
        <button @click="close" class="text-white/80 hover:text-white transition-colors p-1 rounded hover:bg-white/10">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 内容 -->
      <div class="flex-1 overflow-auto p-6">
        <!-- 当前版本 -->
        <div class="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-100">
          <div class="flex items-center gap-2 mb-1">
            <span class="px-2 py-0.5 bg-blue-500 text-white text-xs rounded-full">当前版本</span>
            <span class="text-lg font-bold text-blue-600">V{{ currentVersion }}</span>
          </div>
          <p class="text-sm text-slate-500">发布日期: {{ releaseDate }}</p>
        </div>

        <!-- 版本列表 -->
        <div class="relative">
          <!-- 时间线竖线 -->
          <div class="absolute left-[7px] top-2 bottom-2 w-0.5 bg-slate-200"></div>
          
          <div class="space-y-6">
            <div v-for="version in changelog" :key="version.version" class="relative pl-6">
              <!-- 时间线圆点 -->
              <div class="absolute left-0 top-1 w-4 h-4 rounded-full bg-white border-2 border-blue-500 z-10"></div>
              <div class="mb-2">
                <span class="text-base font-semibold text-slate-800">V{{ version.version }}</span>
                <span class="ml-2 text-xs text-slate-400">{{ version.date }}</span>
              </div>
              <ul class="space-y-1.5">
                <li v-for="(item, idx) in version.changes" :key="idx" class="flex items-start gap-2 text-sm text-slate-600">
                  <span :class="getTypeClass(item.type)">{{ getTypeIcon(item.type) }}</span>
                  <span>{{ item.text }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部 -->
      <div class="p-4 border-t border-slate-100 bg-slate-50 text-center">
        <p class="text-xs text-slate-400">感谢使用股票监控助手 ❤️</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  visible: boolean
}>()

const emit = defineEmits(['update:visible'])

const currentVersion = '1.0.3'
const releaseDate = '2025-12-15'

// 更新日志数据
const changelog = ref([
  {
    version: '1.0.3',
    date: '2025-12-15',
    changes: [
      { type: 'feature', text: '交易记录功能，支持记录买入/卖出/做T操作及原因' },
      { type: 'feature', text: 'K 线图交易标记，直观展示历史操作点位' },
      { type: 'feature', text: 'AI 分析自动记录，支持查看历史分析和信号' },
      { type: 'feature', text: 'AI 结构化输出，自动提取看涨/谨慎/看跌信号' },
      { type: 'feature', text: '精准分析自动计算持仓成本和数量' },
      { type: 'feature', text: '精准分析趋势预测图，展示未来5日价格走势' },
      { type: 'improve', text: '精准分析新增技术面数据：换手率、量比、振幅、均线' },
      { type: 'improve', text: '精准分析新增基本面数据：市盈率、市净率、市值、行业' },
      { type: 'improve', text: '精准分析新增市场情绪：北向资金、融资融券、龙虎榜' },
      { type: 'improve', text: '操作列下拉菜单，界面更简洁' },
    ]
  },
  {
    version: '1.0.2',
    date: '2025-12-12',
    changes: [
      { type: 'feature', text: '大盘指数分时图，直观查看大盘走势' },
      { type: 'feature', text: 'AI 分析 Prompt 完整展示，支持查看和复制' },
      { type: 'feature', text: '配置导入导出功能，轻松备份和迁移设置' },
    ]
  },
  {
    version: '1.0.1',
    date: '2025-12-11',
    changes: [
      { type: 'feature', text: 'AI 智能分析功能，支持 Gemini/GPT/Claude 多模型' },
      { type: 'feature', text: '代理配置支持，解决国内访问问题' },
      { type: 'feature', text: '成交量数据增强，价量配合分析' },
      { type: 'feature', text: '更新日志和使用手册页面' },
      { type: 'fix', text: '修复大盘指数数据显示问题' },
      { type: 'fix', text: '修复 AI 配置持久化问题' },
      { type: 'improve', text: '优化错误提示，更友好的用户体验' },
      { type: 'improve', text: 'AI 请求添加重试机制' },
    ]
  },
  {
    version: '1.0.0',
    date: '2025-12-10',
    changes: [
      { type: 'feature', text: '股票实时行情监控' },
      { type: 'feature', text: '大盘指数展示（上证、深证、创业板、沪深300）' },
      { type: 'feature', text: '股票分组管理和拖拽排序' },
      { type: 'feature', text: '价格预警功能（止盈/止损/涨跌幅）' },
      { type: 'feature', text: '系统托盘和悬浮窗' },
      { type: 'feature', text: '股票详情页（分时图、K线图、资金流向）' },
      { type: 'feature', text: 'PushPlus 和钉钉推送通知' },
      { type: 'feature', text: '中英文双语支持' },
    ]
  }
])

const close = () => {
  emit('update:visible', false)
}

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'feature': return '✨'
    case 'fix': return '🐛'
    case 'improve': return '⚡'
    default: return '📌'
  }
}

const getTypeClass = (type: string) => {
  switch (type) {
    case 'feature': return 'text-green-500'
    case 'fix': return 'text-red-500'
    case 'improve': return 'text-blue-500'
    default: return 'text-slate-500'
  }
}
</script>
