<template>
  <div class="float-container" @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave" @dblclick="showMainWindow">
    <!-- 标题栏（可拖拽区域） -->
    <div class="title-bar">
      <span class="title">stock price monitor</span>
      <button class="close-btn" @click.stop="handleClose">×</button>
    </div>

    <!-- 股票列表 -->
    <div class="stock-list">
      <div v-for="stock in displayStocks" :key="stock.code" class="stock-item">
        <span class="stock-name">{{ stock.name }}</span>
        <span class="stock-price" :class="getPriceClass(stock.change_percent)">
          {{ stock.price }}
        </span>
        <span class="stock-change" :class="getPriceClass(stock.change_percent)">
          {{ getChangeIcon(stock.change_percent) }}{{ stock.change_percent }}%
        </span>
      </div>

      <!-- 空状态 -->
      <div v-if="displayStocks.length === 0" class="empty-state">
        暂无监控股票
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { getStocks } from '../api'

interface StockData {
  code: string
  name: string
  price: string
  change_percent: string
}

const stockData = ref<StockData[]>([])
const isHovered = ref(false)
let intervalId: ReturnType<typeof setInterval> | null = null

// 最多显示3只股票
const displayStocks = computed(() => stockData.value.slice(0, 3))

// 获取涨跌样式类
const getPriceClass = (changePercent: string) => {
  const value = parseFloat(changePercent)
  if (value > 0) return 'up'
  if (value < 0) return 'down'
  return ''
}

// 获取涨跌图标
const getChangeIcon = (changePercent: string) => {
  const value = parseFloat(changePercent)
  if (value > 0) return '↑'
  if (value < 0) return '↓'
  return ''
}

// 鼠标进入
const handleMouseEnter = () => {
  isHovered.value = true
}

// 鼠标离开
const handleMouseLeave = () => {
  isHovered.value = false
}

// 显示主窗口
const showMainWindow = () => {
  (window as any).ipcRenderer?.send('show-main-window')
}

// 关闭悬浮窗
const handleClose = () => {
  console.log('点击关闭按钮')
  try {
    const ipc = (window as any).ipcRenderer
    if (ipc && ipc.send) {
      ipc.send('close-float-window')
      console.log('已发送关闭消息')
    } else {
      console.error('ipcRenderer 不可用')
    }
  } catch (e) {
    console.error('关闭悬浮窗失败:', e)
  }
}

// 获取股票数据
const fetchData = async () => {
  try {
    const res = await getStocks()
    stockData.value = Object.values(res.data) as StockData[]

    // 同时更新托盘提示
    if (stockData.value.length > 0) {
      const summary = stockData.value.slice(0, 3)
        .map(s => `${s.name}: ${s.price} (${s.change_percent}%)`)
        .join('\n')
        ; (window as any).ipcRenderer?.send('update-tray', summary)
    }
  } catch (error) {
    console.error('获取股票数据失败:', error)
  }
}

onMounted(() => {
  fetchData()
  intervalId = setInterval(fetchData, 2000)
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
})
</script>

<style scoped>
.float-container {
  width: 100%;
  height: 100%;
  background: rgba(30, 30, 30, 0.95);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color: #fff;
}

/* 标题栏 - 可拖拽 */
.title-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  background: rgba(50, 50, 50, 0.9);
  -webkit-app-region: drag;
  /* 允许拖拽 */
  cursor: move;
}

.title {
  font-size: 12px;
  font-weight: 500;
  color: #ccc;
}

.close-btn {
  width: 18px;
  height: 18px;
  border: none;
  background: transparent;
  color: #888;
  font-size: 16px;
  cursor: pointer;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  -webkit-app-region: no-drag;
  /* 关闭按钮不可拖拽 */
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e81123;
  color: #fff;
}

/* 股票列表 */
.stock-list {
  padding: 8px;
}

.stock-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 4px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.stock-item:last-child {
  border-bottom: none;
}

.stock-name {
  font-size: 12px;
  color: #ddd;
  flex: 4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 80px;
}

.stock-price {
  font-size: 13px;
  font-weight: 600;
  margin: 0 4px;
  min-width: 60px;
  text-align: right;
}

.stock-change {
  font-size: 11px;
  min-width: 60px;
  text-align: right;
}

/* 涨跌颜色 */
.up {
  color: #ff4d4f;
}

.down {
  color: #52c41a;
}

/* 空状态 */
.empty-state {
  text-align: center;
  color: #666;
  font-size: 12px;
  padding: 20px 0;
}
</style>
