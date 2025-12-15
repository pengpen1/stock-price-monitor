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
  type: 'B' | 'S' | 'T';  // 买入/卖出/做T
  price: number;
  quantity: number;
  reason: string;
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

// 添加交易记录
export const addTradeRecord = async (data: {
  stock_code: string;
  type: 'B' | 'S' | 'T';
  price: number;
  quantity: number;
  reason: string;
  trade_time?: string;
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

export default api;
