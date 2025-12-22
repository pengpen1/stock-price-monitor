<template>
  <Teleport to="body">
    <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black/50"></div>
      
      <div class="relative bg-white rounded-2xl shadow-2xl w-[900px] max-h-[90vh] overflow-hidden flex flex-col">
        <!-- 头部 -->
        <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between flex-shrink-0">
          <div>
            <h3 class="text-lg font-semibold text-slate-800">模拟结算</h3>
            <p class="text-sm text-slate-500">{{ session?.stock_name }} · {{ session?.start_date }} 至 {{ session?.end_date }}</p>
          </div>
          <button @click="close" class="p-1 text-slate-400 hover:text-slate-600 rounded">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        
        <!-- 内容 -->
        <div class="flex-1 overflow-y-auto p-6">
          <!-- 结果概览 -->
          <div class="grid grid-cols-4 gap-4 mb-6">
            <div class="bg-slate-50 rounded-xl p-4 text-center">
              <div class="text-sm text-slate-500 mb-1">最终资产</div>
              <div class="text-xl font-bold" :class="profitClass">
                ¥{{ formatMoney(result?.final_capital || 0) }}
              </div>
            </div>
            <div class="bg-slate-50 rounded-xl p-4 text-center">
              <div class="text-sm text-slate-500 mb-1">收益率</div>
              <div class="text-xl font-bold" :class="profitClass">
                {{ (result?.profit_rate || 0) >= 0 ? '+' : '' }}{{ (result?.profit_rate || 0).toFixed(2) }}%
              </div>
            </div>
            <div class="bg-slate-50 rounded-xl p-4 text-center">
              <div class="text-sm text-slate-500 mb-1">胜率</div>
              <div class="text-xl font-bold text-slate-800">
                {{ (result?.win_rate || 0).toFixed(1) }}%
              </div>
            </div>
            <div class="bg-slate-50 rounded-xl p-4 text-center">
              <div class="text-sm text-slate-500 mb-1">最大回撤</div>
              <div class="text-xl font-bold text-amber-500">
                {{ (result?.max_drawdown || 0).toFixed(2) }}%
              </div>
            </div>
          </div>
          
          <!-- AI 评分 -->
          <div class="mb-6">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-semibold text-slate-700">AI 评分分析</h4>
              <button v-if="!aiResult && !analyzing" @click="requestAIAnalysis"
                class="px-3 py-1.5 text-sm text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100">
                获取 AI 评分
              </button>
            </div>
            
            <div v-if="analyzing" class="bg-slate-50 rounded-xl p-6 text-center">
              <div class="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-2"></div>
              <p class="text-slate-500">AI 正在分析您的交易...</p>
            </div>
            
            <div v-else-if="aiResult" class="bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl p-5">
              <!-- 评分展示 -->
              <div class="flex items-center gap-6 mb-4">
                <div class="w-24 h-24 rounded-full flex items-center justify-center text-3xl font-bold"
                  :class="gradeColorClass">
                  {{ aiResult.grade }}
                </div>
                <div>
                  <div class="text-3xl font-bold text-slate-800 mb-1">{{ aiResult.score }} 分</div>
                  <div class="text-sm text-slate-500">综合评分</div>
                </div>
              </div>
              
              <!-- 优缺点 -->
              <div class="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <h5 class="text-sm font-medium text-green-600 mb-2">✓ 优点</h5>
                  <ul class="text-sm text-slate-600 space-y-1">
                    <li v-for="(s, i) in aiResult.strengths" :key="i">• {{ s }}</li>
                  </ul>
                </div>
                <div>
                  <h5 class="text-sm font-medium text-red-600 mb-2">✗ 不足</h5>
                  <ul class="text-sm text-slate-600 space-y-1">
                    <li v-for="(w, i) in aiResult.weaknesses" :key="i">• {{ w }}</li>
                  </ul>
                </div>
              </div>
              
              <!-- 建议 -->
              <div class="mb-4">
                <h5 class="text-sm font-medium text-blue-600 mb-2">💡 建议</h5>
                <ul class="text-sm text-slate-600 space-y-1">
                  <li v-for="(s, i) in aiResult.suggestions" :key="i">• {{ s }}</li>
                </ul>
              </div>
              
              <!-- 详细分析 -->
              <div v-if="aiResult.analysis" class="bg-white rounded-lg p-3">
                <h5 class="text-sm font-medium text-slate-700 mb-2">详细分析</h5>
                <p class="text-sm text-slate-600 whitespace-pre-wrap">{{ aiResult.analysis }}</p>
              </div>
            </div>
            
            <!-- 未获取AI评分时显示 -->
            <div v-else class="bg-slate-50 rounded-xl p-6">
              <div class="text-center text-slate-400 mb-4">
                点击上方按钮获取 AI 评分分析
              </div>
              
              <!-- 显示Prompt供用户复制 -->
              <div v-if="aiPrompt" class="mt-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-xs text-slate-500">或复制以下 Prompt 到其他 AI 工具：</span>
                  <button @click="copyPrompt" class="text-xs text-blue-600 hover:text-blue-700">
                    {{ promptCopied ? '已复制 ✓' : '复制 Prompt' }}
                  </button>
                </div>
                <div class="bg-white border border-slate-200 rounded-lg p-3 max-h-40 overflow-y-auto">
                  <pre class="text-xs text-slate-600 whitespace-pre-wrap font-mono">{{ aiPrompt }}</pre>
                </div>
              </div>
              <button v-else @click="generatePrompt" class="w-full mt-2 text-xs text-slate-500 hover:text-slate-700">
                点击生成 Prompt
              </button>
            </div>
          </div>
          
          <!-- 交易明细 -->
          <div>
            <h4 class="text-sm font-semibold text-slate-700 mb-3">交易明细</h4>
            <div class="bg-slate-50 rounded-xl overflow-hidden">
              <table class="w-full text-sm">
                <thead>
                  <tr class="text-left text-slate-500 bg-slate-100">
                    <th class="px-4 py-2 font-medium">日期</th>
                    <th class="px-4 py-2 font-medium">操作</th>
                    <th class="px-4 py-2 font-medium">价格</th>
                    <th class="px-4 py-2 font-medium">数量</th>
                    <th class="px-4 py-2 font-medium">理由</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="trade in session?.trades" :key="trade.day" class="border-t border-slate-200">
                    <td class="px-4 py-2">{{ trade.date }}</td>
                    <td class="px-4 py-2">
                      <span :class="tradeTypeClass(trade.type)" class="px-2 py-0.5 text-xs font-medium rounded">
                        {{ tradeTypeText(trade.type) }}
                      </span>
                    </td>
                    <td class="px-4 py-2">{{ trade.type !== 'skip' ? '¥' + trade.price.toFixed(2) : '-' }}</td>
                    <td class="px-4 py-2">{{ trade.type !== 'skip' ? trade.quantity + '股' : '-' }}</td>
                    <td class="px-4 py-2 max-w-xs truncate" :title="trade.reason">{{ trade.reason || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        
        <!-- 底部 -->
        <div class="px-6 py-4 border-t border-slate-100 flex justify-end flex-shrink-0">
          <button @click="close"
            class="px-6 py-2.5 text-sm font-medium text-white bg-blue-500 rounded-lg hover:bg-blue-600">
            完成
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { analyzeSimulation, getSettings } from '../api'
import type { SimulationSession, SimulationResult, SimulationAIResult } from '../api'

const props = defineProps<{
  visible: boolean
  session: SimulationSession | null
  klineData: any[]
}>()

const emit = defineEmits(['update:visible', 'close'])

const analyzing = ref(false)
const result = ref<SimulationResult | null>(null)
const aiResult = ref<SimulationAIResult | null>(null)
const aiPrompt = ref('')
const promptCopied = ref(false)

const close = () => {
  emit('update:visible', false)
  emit('close')
}

const profitClass = computed(() => {
  return (result.value?.profit_rate || 0) >= 0 ? 'text-red-500' : 'text-green-500'
})

const gradeColorClass = computed(() => {
  const grade = aiResult.value?.grade || ''
  switch (grade) {
    case 'S': return 'bg-gradient-to-br from-yellow-400 to-amber-500 text-white'
    case 'A': return 'bg-gradient-to-br from-green-400 to-emerald-500 text-white'
    case 'B': return 'bg-gradient-to-br from-blue-400 to-blue-500 text-white'
    case 'C': return 'bg-gradient-to-br from-orange-400 to-orange-500 text-white'
    default: return 'bg-gradient-to-br from-slate-400 to-slate-500 text-white'
  }
})

const formatMoney = (val: number) => {
  return val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const tradeTypeClass = (type: string) => {
  switch (type) {
    case 'buy': return 'bg-red-100 text-red-600'
    case 'sell': return 'bg-green-100 text-green-600'
    default: return 'bg-slate-100 text-slate-600'
  }
}

const tradeTypeText = (type: string) => {
  switch (type) {
    case 'buy': return '买入'
    case 'sell': return '卖出'
    default: return '跳过'
  }
}

// 计算本地结果
const calculateLocalResult = () => {
  if (!props.session || !props.klineData.length) return
  
  const session = props.session
  // 获取最后一天的收盘价
  const lastKline = props.klineData[props.klineData.length - 1]
  const finalPrice = lastKline?.close || 0
  
  const positionValue = session.position * finalPrice
  const finalCapital = session.current_capital + positionValue
  const profitRate = ((finalCapital - session.initial_capital) / session.initial_capital) * 100
  
  // 计算胜率
  const trades = session.trades.filter(t => t.type !== 'skip')
  let winCount = 0
  let totalTrades = 0
  let buyPrice = 0
  
  for (const trade of session.trades) {
    if (trade.type === 'buy') {
      buyPrice = trade.price
    } else if (trade.type === 'sell' && buyPrice > 0) {
      totalTrades++
      if (trade.price > buyPrice) winCount++
    }
  }
  
  const winRate = totalTrades > 0 ? (winCount / totalTrades) * 100 : 0
  
  // 计算最大回撤（基于总资产，需要结合K线数据计算每天的持仓市值）
  let maxDrawdown = 0
  if (props.klineData.length > 0 && session.trades.length > 0) {
    // 构建每天的资产快照
    let currentCash = session.initial_capital
    let currentPosition = 0
    let maxTotalAsset = session.initial_capital
    let tradeIndex = 0
    
    // 获取模拟期间的K线
    const startIdx = session.kline_start_idx || 0
    const simKlines = props.klineData.slice(Math.max(0, startIdx - (props.klineData.length - session.total_days)))
    
    for (let i = 0; i < simKlines.length && tradeIndex < session.trades.length; i++) {
      const kline = simKlines[i]
      const trade = session.trades[tradeIndex]
      
      // 检查这一天是否有交易
      if (trade && kline.date === trade.date) {
        currentCash = trade.capital_after
        currentPosition = trade.position_after
        tradeIndex++
      }
      
      // 计算当天收盘时的总资产
      const totalAsset = currentCash + currentPosition * kline.close
      
      if (totalAsset > maxTotalAsset) {
        maxTotalAsset = totalAsset
      }
      
      // 计算回撤
      const drawdown = ((maxTotalAsset - totalAsset) / maxTotalAsset) * 100
      if (drawdown > maxDrawdown) {
        maxDrawdown = drawdown
      }
    }
  }
  
  result.value = {
    final_capital: finalCapital,
    profit_rate: profitRate,
    win_rate: winRate,
    max_drawdown: maxDrawdown,
    total_trades: trades.length,
    position_value: positionValue
  }
}

const requestAIAnalysis = async () => {
  if (!props.session) return
  
  analyzing.value = true
  try {
    // 获取 AI 配置
    const settingsRes = await getSettings()
    const settings = settingsRes.settings || {}
    
    if (!settings.ai_api_key) {
      alert('请先在设置中配置 AI API Key')
      // 生成 Prompt 供用户复制
      generatePrompt()
      return
    }
    
    const res = await analyzeSimulation({
      session_id: props.session.id,
      provider: settings.ai_provider || 'gemini',
      api_key: settings.ai_api_key,
      model: settings.ai_model || '',
      proxy: settings.ai_proxy || undefined
    })
    
    if (res.status === 'success') {
      if (res.result) {
        result.value = res.result
      }
      if (res.ai_result) {
        aiResult.value = res.ai_result
      } else if (res.error) {
        alert('AI 分析失败: ' + res.error + '\n\n已生成 Prompt，您可以复制到其他 AI 工具使用')
        generatePrompt()
      }
    } else {
      alert(res.message || 'AI 分析失败')
      generatePrompt()
    }
  } catch (e: any) {
    alert(e.message || 'AI 分析失败' + '\n\n已生成 Prompt，您可以复制到其他 AI 工具使用')
    generatePrompt()
  } finally {
    analyzing.value = false
  }
}

// 生成 AI 评分 Prompt
const generatePrompt = () => {
  if (!props.session || !result.value) return
  
  const session = props.session
  const r = result.value
  
  let prompt = `请对以下股票模拟交易进行评分和分析：

## 基本信息
- 股票：${session.stock_name}（${session.stock_code}）
- 模拟周期：${session.start_date} 至 ${session.end_date}（${session.total_days}个交易日）
- 初始资金：${session.initial_capital.toLocaleString()}元

## 交易结果
- 最终资产：${r.final_capital.toLocaleString()}元
- 收益率：${r.profit_rate.toFixed(2)}%
- 胜率：${r.win_rate.toFixed(2)}%
- 最大回撤：${r.max_drawdown.toFixed(2)}%
- 交易次数：${r.total_trades}次

## K线数据（模拟期间）
日期 | 开盘 | 收盘 | 最高 | 最低 | 涨跌幅
`
  
  // 添加K线数据
  for (const k of props.klineData.slice(-session.total_days - 5)) {
    const change = k.open > 0 ? ((k.close - k.open) / k.open * 100) : 0
    prompt += `${k.date} | ${k.open.toFixed(2)} | ${k.close.toFixed(2)} | ${k.high.toFixed(2)} | ${k.low.toFixed(2)} | ${change >= 0 ? '+' : ''}${change.toFixed(2)}%\n`
  }
  
  prompt += `\n## 交易记录\n`
  for (const trade of session.trades) {
    if (trade.type === 'skip') {
      prompt += `- ${trade.date}：跳过（${trade.reason}）\n`
    } else if (trade.type === 'buy') {
      prompt += `- ${trade.date}：买入 ${trade.quantity}股 @ ${trade.price.toFixed(2)}元（${trade.reason}）\n`
    } else {
      prompt += `- ${trade.date}：卖出 ${trade.quantity}股 @ ${trade.price.toFixed(2)}元（${trade.reason}）\n`
    }
  }
  
  prompt += `
## 请按以下JSON格式返回评分结果：
\`\`\`json
{
  "score": 75,
  "grade": "B",
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["不足1", "不足2"],
  "suggestions": ["建议1", "建议2"],
  "analysis": "详细分析文字..."
}
\`\`\`

评分标准：
- S级(90-100)：优秀的交易策略，风险控制得当
- A级(80-89)：良好的交易表现，有小幅改进空间
- B级(70-79)：中等水平，需要改进部分策略
- C级(60-69)：及格水平，存在明显问题
- D级(0-59)：需要大幅改进

请综合考虑：收益率、胜率、最大回撤、交易时机、仓位管理、风险控制等因素。`

  aiPrompt.value = prompt
}

// 复制 Prompt
const copyPrompt = async () => {
  try {
    await navigator.clipboard.writeText(aiPrompt.value)
    promptCopied.value = true
    setTimeout(() => {
      promptCopied.value = false
    }, 2000)
  } catch (e) {
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = aiPrompt.value
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    promptCopied.value = true
    setTimeout(() => {
      promptCopied.value = false
    }, 2000)
  }
}

watch(() => props.visible, (val) => {
  if (val) {
    calculateLocalResult()
    aiResult.value = null
    aiPrompt.value = ''
    promptCopied.value = false
  }
})
</script>
