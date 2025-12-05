<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
    <!-- 头部区域 -->
    <div class="max-w-6xl mx-auto">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-slate-800">{{ t('title') }}</h1>
        <div class="flex items-center gap-2">
          <button 
            @click="toggleLanguage" 
            class="px-4 py-2 text-sm text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
          >
            {{ currentLang === 'en' ? '中文' : 'English' }}
          </button>
          <button 
            @click="$emit('openSettings')" 
            class="px-4 py-2 text-sm text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
          >
            ⚙️ {{ t('settings') }}
          </button>
        </div>
      </div>

      <!-- 添加股票卡片 -->
      <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-4 mb-6">
        <div class="flex gap-3">
          <input 
            v-model="newStockCode" 
            :placeholder="t('placeholder')" 
            @keyup.enter="handleAddStock" 
            :disabled="loading"
            class="flex-1 px-4 py-3 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all disabled:bg-slate-50 disabled:cursor-not-allowed"
          />
          <button 
            @click="handleAddStock" 
            :disabled="loading"
            class="px-6 py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 disabled:bg-blue-300 disabled:cursor-not-allowed transition-colors"
          >
            {{ loading ? t('adding') : t('add') }}
          </button>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="errorMsg" class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-6 text-sm">
        {{ errorMsg }}
      </div>

      <!-- 股票列表卡片 -->
      <div class="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        <table class="w-full">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100">
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">{{ t('col_code') }}</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">{{ t('col_name') }}</th>
              <th class="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">{{ t('col_price') }}</th>
              <th class="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">{{ t('col_change') }}</th>
              <th class="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">{{ t('col_high') }}</th>
              <th class="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">{{ t('col_low') }}</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">{{ t('col_time') }}</th>
              <th class="px-4 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider">{{ t('col_action') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr 
              v-for="stock in stockData" 
              :key="stock.code"
              class="hover:bg-slate-50 transition-colors"
            >
              <td class="px-4 py-4 text-sm font-mono text-slate-700">{{ stock.code }}</td>
              <td class="px-4 py-4 text-sm font-medium text-slate-800">{{ stock.name }}</td>
              <td class="px-4 py-4 text-sm text-right font-semibold" :class="getPriceClass(stock.change_percent)">
                {{ stock.price }}
              </td>
              <td class="px-4 py-4 text-sm text-right font-medium" :class="getPriceClass(stock.change_percent)">
                <span class="inline-flex items-center gap-1">
                  <span v-if="parseFloat(stock.change_percent) > 0">↑</span>
                  <span v-else-if="parseFloat(stock.change_percent) < 0">↓</span>
                  {{ stock.change_percent }}%
                </span>
              </td>
              <td class="px-4 py-4 text-sm text-right text-slate-600">{{ stock.high }}</td>
              <td class="px-4 py-4 text-sm text-right text-slate-600">{{ stock.low }}</td>
              <td class="px-4 py-4 text-sm text-slate-500">{{ stock.time }}</td>
              <td class="px-4 py-4 text-center">
                <button 
                  @click="handleRemoveStock(stock.code)"
                  class="px-3 py-1.5 text-xs text-slate-500 border border-slate-200 rounded-md hover:bg-red-50 hover:text-red-500 hover:border-red-200 transition-colors"
                >
                  {{ t('remove') }}
                </button>
              </td>
            </tr>
            <!-- 空状态 -->
            <tr v-if="stockData.length === 0">
              <td colspan="8" class="px-4 py-12 text-center text-slate-400 text-sm">
                {{ t('empty') }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 底部状态栏 -->
      <div class="mt-4 text-center text-xs text-slate-400">
        {{ t('auto_refresh') }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { getStocks, addStock, removeStock, getSettings } from '../api';

// 响应式状态
const newStockCode = ref('');
const stockData = ref<any[]>([]);
const loading = ref(false);
const errorMsg = ref('');
const refreshInterval = ref(5); // 默认刷新间隔（秒）
type Lang = 'en' | 'zh';
const currentLang = ref<Lang>('zh'); // 默认中文
let intervalId: ReturnType<typeof setInterval> | null = null;

// 多语言翻译配置
const translations: Record<Lang, Record<string, string>> = {
  en: {
    title: 'Stock Monitor',
    placeholder: 'Stock Code (e.g., 600519)',
    add: 'Add',
    adding: 'Adding...',
    remove: 'Remove',
    empty: 'No stocks monitored. Add one to start.',
    col_code: 'Code',
    col_name: 'Name',
    col_price: 'Price',
    col_change: 'Change',
    col_high: 'High',
    col_low: 'Low',
    col_time: 'Time',
    col_action: 'Action',
    auto_refresh: 'Auto-refreshing every {interval} seconds',
    settings: 'Settings'
  },
  zh: {
    title: '股票监控助手',
    placeholder: '股票代码 (如 600519)',
    add: '添加',
    adding: '添加中...',
    remove: '删除',
    empty: '暂无监控股票，请添加。',
    col_code: '代码',
    col_name: '名称',
    col_price: '当前价',
    col_change: '涨跌幅',
    col_high: '最高',
    col_low: '最低',
    col_time: '时间',
    col_action: '操作',
    auto_refresh: '每 {interval} 秒自动刷新',
    settings: '设置'
  }
};

// 翻译函数
const t = (key: string) => {
  const text = translations[currentLang.value][key] || key;
  // 替换 {interval} 占位符
  return text.replace('{interval}', String(refreshInterval.value));
};

// 切换语言
const toggleLanguage = () => {
  currentLang.value = currentLang.value === 'en' ? 'zh' : 'en';
};

// 根据涨跌幅返回样式类
const getPriceClass = (changePercent: string) => {
  const value = parseFloat(changePercent);
  if (value > 0) return 'text-red-500'; // 中国股市：红涨
  if (value < 0) return 'text-green-500'; // 绿跌
  return 'text-slate-600';
};

// 更新托盘提示信息
const updateTray = () => {
  if (stockData.value.length > 0) {
    // 在托盘提示中显示前3只股票
    const summary = stockData.value.slice(0, 3).map(s => `${s.name}: ${s.price} (${s.change_percent}%)`).join('\n');
    (window as any).ipcRenderer?.send('update-tray', summary);
  } else {
    (window as any).ipcRenderer?.send('update-tray', 'Stock Monitor');
  }
};

// 获取股票数据
const fetchData = async () => {
  try {
    const res = await getStocks();
    stockData.value = Object.values(res.data);
    updateTray();
  } catch (error) {
    console.error("获取股票数据失败:", error);
  }
};

// 添加股票
const handleAddStock = async () => {
  if (!newStockCode.value) return;
  loading.value = true;
  errorMsg.value = '';
  try {
    const res = await addStock(newStockCode.value);
    if (res.status === 'error') {
      errorMsg.value = res.message;
    } else {
      newStockCode.value = '';
      await fetchData();
    }
  } catch (e) {
    console.error(e);
    errorMsg.value = "添加股票失败，请检查后端连接。";
  } finally {
    loading.value = false;
  }
};

// 删除股票
const handleRemoveStock = async (code: string) => {
  await removeStock(code);
  fetchData();
};

// 加载设置并启动定时刷新
const loadSettingsAndStart = async () => {
  try {
    const res = await getSettings();
    if (res.status === 'success' && res.settings?.refresh_interval) {
      refreshInterval.value = res.settings.refresh_interval;
    }
  } catch (e) {
    console.error('加载设置失败，使用默认值:', e);
  }
  
  // 启动定时刷新
  fetchData();
  intervalId = setInterval(fetchData, refreshInterval.value * 1000);
};

// 组件挂载时加载设置并启动
onMounted(() => {
  loadSettingsAndStart();
});

// 组件卸载时清理定时器
onUnmounted(() => {
  if (intervalId) clearInterval(intervalId);
});
</script>
