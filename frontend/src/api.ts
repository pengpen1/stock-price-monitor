import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
});

export const getStocks = async () => {
  const response = await api.get('/stocks');
  return response.data;
};

export const addStock = async (code: string) => {
  const response = await api.post(`/stocks/${code}`);
  return response.data;
};

export const removeStock = async (code: string) => {
  const response = await api.delete(`/stocks/${code}`);
  return response.data;
};

// 获取设置
export const getSettings = async () => {
  const response = await api.get('/settings');
  return response.data;
};

// 更新设置
export const updateSettings = async (settings: Record<string, any>) => {
  const response = await api.post('/settings', settings);
  return response.data;
};

// 重新排序股票
export const reorderStocks = async (stocks: string[]) => {
  const response = await api.post('/stocks/reorder', { stocks });
  return response.data;
};

// 设置重点关注
export const setFocusedStock = async (code: string) => {
  const response = await api.post(`/stocks/focus/${code}`);
  return response.data;
};

// 设置股票分组
export const setStockGroup = async (code: string, group: string) => {
  const response = await api.post(`/stocks/group/${code}`, { group });
  return response.data;
};

// 获取所有分组
export const getGroups = async () => {
  const response = await api.get('/groups');
  return response.data;
};

// 添加新分组
export const addGroupApi = async (group: string) => {
  const response = await api.post('/groups', { group });
  return response.data;
};

// 删除分组
export const deleteGroupApi = async (group: string, deleteStocks: boolean = false) => {
  const response = await api.delete(`/groups/${encodeURIComponent(group)}`, { params: { delete_stocks: deleteStocks } });
  return response.data;
};

// 设置股票预警
export const setAlert = async (code: string, alertConfig: Record<string, any>) => {
  const response = await api.post(`/alerts/${code}`, alertConfig);
  return response.data;
};

// 移除股票预警
export const removeAlert = async (code: string) => {
  const response = await api.delete(`/alerts/${code}`);
  return response.data;
};

// 获取触发的预警
export const getTriggeredAlerts = async () => {
  const response = await api.get('/alerts/triggered');
  return response.data;
};

// 获取股票详情（分时、K线、资金流向）
export const getStockDetail = async (code: string) => {
  const response = await api.get(`/stock/${code}/detail`);
  return response.data;
};

// 获取分时数据
export const getMinuteData = async (code: string) => {
  const response = await api.get(`/stock/${code}/minute`);
  return response.data;
};

// 获取K线数据
export const getKlineData = async (code: string, period = 'day', count = 120) => {
  const response = await api.get(`/stock/${code}/kline`, { params: { period, count } });
  return response.data;
};

// 获取资金流向
export const getMoneyFlow = async (code: string) => {
  const response = await api.get(`/stock/${code}/money-flow`);
  return response.data;
};

// 获取大盘指数详情
export const getIndexDetail = async (code: string) => {
  const response = await api.get(`/index/${code}/detail`);
  return response.data;
};

// 获取市场涨跌统计
export const getMarketStats = async () => {
  const response = await api.get('/market/stats');
  return response.data;
};

// 获取涨跌统计历史
export const getMarketStatsHistory = async (days: number = 30) => {
  const response = await api.get('/market/stats/history', { params: { days } });
  return response.data;
};

// 获取 AI 模型列表
export const getAIModels = async (provider: string, apiKey: string, proxy?: string) => {
  const response = await api.post('/ai/models', {
    provider,
    api_key: apiKey,
    proxy: proxy || null
  });
  return response.data;
};

// AI 分析
export const analyzeStock = async (
  code: string,
  type: 'fast' | 'precise',
  provider: string,
  apiKey: string,
  model: string,
  inputs: Record<string, any> = {},
  proxy?: string
) => {
  const response = await api.post('/analyze', {
    code,
    type,
    provider,
    api_key: apiKey,
    model,
    proxy: proxy || null,
    inputs
  });
  return response.data;
};

// ========== 数据导入导出 ==========

// 导入配置数据
export const importData = async (data: {
  stocks?: Record<string, any>;
  settings?: Record<string, any>;
  alerts?: Record<string, any>;
}) => {
  const response = await api.post('/data/import', data);
  return response.data;
};

// 获取数据存储路径
export const getDataPath = async () => {
  const response = await api.get('/data/path');
  return response.data;
};

// 设置数据存储路径
export const setDataPath = async (path: string) => {
  const response = await api.post('/data/path', { path });
  return response.data;
};

// 导出配置数据
export const exportData = async () => {
  const response = await api.get('/data/export');
  return response.data;
};

// ========== 交易记录 API ==========

// 交易记录类型
export interface TradeRecord {
  id: string;
  stock_code: string;
  stock_name?: string;
  type: 'B' | 'S' | 'T';  // 买入/卖出/做T
  price: number;
  quantity: number;
  reason: string;
  mood: 'calm' | 'anxious' | 'panic' | 'fear' | 'excited';  // 心态
  level: 1 | 2 | 3;  // 交易分级
  trade_time: string;
  created_at: string;
}

// AI 分析记录类型
export interface AIRecord {
  id: string;
  stock_code: string;
  signal: 'bullish' | 'cautious' | 'bearish';
  summary: string;
  full_result: string;
  analysis_type: 'fast' | 'precise';
  model: string;
  datetime: string;
}

// 交易风格分析类型
export interface TradeStyleAnalysis {
  total_records: number;
  mood_stats: Record<string, number>;
  level_stats: Record<number, number>;
  level_profit: Record<number, { win: number; lose: number }>;
  mood_profit: Record<string, { win: number; lose: number }>;
  level_win_rate: Record<number, number>;
  mood_win_rate: Record<string, number>;
}

// 添加交易记录
export const addTradeRecord = async (data: {
  stock_code: string;
  stock_name?: string;
  type: 'B' | 'S' | 'T';
  price: number;
  quantity: number;
  reason: string;
  trade_time?: string;
  mood?: string;
  level?: number;
}) => {
  const response = await api.post('/records/trade', data);
  return response.data;
};

// 更新交易记录
export const updateTradeRecord = async (recordId: string, data: {
  type?: 'B' | 'S' | 'T';
  price?: number;
  quantity?: number;
  reason?: string;
  trade_time?: string;
  mood?: string;
  level?: number;
  stock_name?: string;
}) => {
  const response = await api.put(`/records/trade/${recordId}`, data);
  return response.data;
};

// 删除交易记录
export const deleteTradeRecord = async (recordId: string) => {
  const response = await api.delete(`/records/trade/${recordId}`);
  return response.data;
};

// 获取交易记录
export const getTradeRecords = async (stockCode?: string, limit: number = 100) => {
  const params: Record<string, any> = { limit };
  if (stockCode) params.stock_code = stockCode;
  const response = await api.get('/records/trade', { params });
  return response.data;
};

// 获取指定股票的交易记录
export const getStockTradeRecords = async (stockCode: string, limit: number = 100) => {
  const response = await api.get(`/records/trade/${stockCode}`, { params: { limit } });
  return response.data;
};

// 获取 AI 分析记录
export const getAIRecords = async (stockCode?: string, limit: number = 50) => {
  const params: Record<string, any> = { limit };
  if (stockCode) params.stock_code = stockCode;
  const response = await api.get('/records/ai', { params });
  return response.data;
};

// 获取指定股票的 AI 分析记录
export const getStockAIRecords = async (stockCode: string, limit: number = 50) => {
  const response = await api.get(`/records/ai/${stockCode}`, { params: { limit } });
  return response.data;
};

// 获取持仓计算结果
export const getStockPosition = async (stockCode: string) => {
  const response = await api.get(`/records/position/${stockCode}`);
  return response.data;
};

// ========== 实盘模拟 API ==========

// 模拟会话类型
export interface SimulationSession {
  id: string;
  stock_code: string;
  stock_name: string;
  start_date: string;
  end_date: string;
  current_day: number;
  total_days: number;
  initial_capital: number;
  current_capital: number;
  position: number;
  cost_price: number;
  status: 'running' | 'paused' | 'completed' | 'abandoned';
  trades: SimulationTrade[];
  kline_start_idx: number;
  created_at: string;
  updated_at: string;
  final_price?: number;           // 最终价格
  final_profit_rate?: number;     // 最终收益率
}

// 模拟交易记录类型
export interface SimulationTrade {
  day: number;
  date: string;
  type: 'buy' | 'sell' | 'skip';
  price: number;
  quantity: number;
  reason: string;
  capital_after: number;
  position_after: number;
  auto?: boolean;  // 是否自动交易（如自动清仓）
}

// 模拟结果类型
export interface SimulationResult {
  final_capital: number;
  profit_rate: number;
  win_rate: number;
  max_drawdown: number;
  total_trades: number;
  position_value: number;
}

// AI评分结果类型
export interface SimulationAIResult {
  score: number;
  grade: string;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  analysis: string;
}

// 创建模拟会话
export const createSimulation = async (data: {
  stock_code: string;
  stock_name: string;
  total_days: number;
  initial_capital?: number;
}) => {
  const response = await api.post('/simulation/create', data);
  return response.data;
};

// 获取模拟会话列表
export const getSimulationSessions = async (stockCode?: string, status?: string, limit: number = 50) => {
  const params: Record<string, any> = { limit };
  if (stockCode) params.stock_code = stockCode;
  if (status) params.status = status;
  const response = await api.get('/simulation/sessions', { params });
  return response.data;
};

// 获取模拟会话详情
export const getSimulationSession = async (sessionId: string) => {
  const response = await api.get(`/simulation/${sessionId}`);
  return response.data;
};

// 获取模拟会话的K线数据
export const getSimulationKline = async (sessionId: string) => {
  const response = await api.get(`/simulation/${sessionId}/kline`);
  return response.data;
};

// 获取模拟会话某天的分时数据
export const getSimulationMinute = async (sessionId: string, date: string) => {
  const response = await api.get(`/simulation/${sessionId}/minute/${date}`);
  return response.data;
};

// 执行模拟交易
export const executeSimulationTrade = async (data: {
  session_id: string;
  trade_type: 'buy' | 'sell' | 'skip';
  price?: number;
  quantity?: number;
  reason?: string;
  current_date?: string;
}) => {
  const response = await api.post('/simulation/trade', data);
  return response.data;
};

// 暂停模拟
export const pauseSimulation = async (sessionId: string) => {
  const response = await api.post(`/simulation/${sessionId}/pause`);
  return response.data;
};

// 继续模拟
export const resumeSimulation = async (sessionId: string) => {
  const response = await api.post(`/simulation/${sessionId}/resume`);
  return response.data;
};

// 放弃模拟
export const abandonSimulation = async (sessionId: string) => {
  const response = await api.post(`/simulation/${sessionId}/abandon`);
  return response.data;
};

// 删除模拟记录
export const deleteSimulation = async (sessionId: string) => {
  const response = await api.delete(`/simulation/${sessionId}`);
  return response.data;
};

// AI分析模拟结果
export const analyzeSimulation = async (data: {
  session_id: string;
  provider: string;
  api_key: string;
  model: string;
  proxy?: string;
}) => {
  const response = await api.post('/simulation/analyze', data);
  return response.data;
};

// ========== 交易风格分析 API ==========

// 获取交易风格分析
export const getTradeStyleAnalysis = async (stockCode?: string) => {
  const params: Record<string, any> = {};
  if (stockCode) params.stock_code = stockCode;
  const response = await api.get('/records/analysis', { params });
  return response.data;
};

// 获取所有有交易记录的股票代码
export const getTradeStockCodes = async () => {
  const response = await api.get('/records/stocks');
  return response.data;
};

// 导出交易记录为 Markdown
export const exportTradeRecordsMd = async (stockCode?: string) => {
  const params: Record<string, any> = {};
  if (stockCode) params.stock_code = stockCode;
  const response = await api.get('/records/export/md', { params });
  return response.data;
};

// 从 Markdown 导入交易记录
export const importTradeRecordsMd = async (content: string) => {
  const response = await api.post('/records/import/md', { content });
  return response.data;
};

export default api;
