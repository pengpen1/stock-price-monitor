import axios from 'axios';
const api = axios.create({
    baseURL: 'http://127.0.0.1:8000',
});
export const getStocks = async () => {
    const response = await api.get('/stocks');
    return response.data;
};
export const addStock = async (code) => {
    const response = await api.post(`/stocks/${code}`);
    return response.data;
};
export const removeStock = async (code) => {
    const response = await api.delete(`/stocks/${code}`);
    return response.data;
};
// 获取设置
export const getSettings = async () => {
    const response = await api.get('/settings');
    return response.data;
};
// 更新设置
export const updateSettings = async (settings) => {
    const response = await api.post('/settings', settings);
    return response.data;
};
// 重新排序股票
export const reorderStocks = async (stocks) => {
    const response = await api.post('/stocks/reorder', { stocks });
    return response.data;
};
// 设置重点关注
export const setFocusedStock = async (code) => {
    const response = await api.post(`/stocks/focus/${code}`);
    return response.data;
};
// 设置股票分组
export const setStockGroup = async (code, group) => {
    const response = await api.post(`/stocks/group/${code}`, { group });
    return response.data;
};
// 获取所有分组
export const getGroups = async () => {
    const response = await api.get('/groups');
    return response.data;
};
// 添加新分组
export const addGroupApi = async (group) => {
    const response = await api.post('/groups', { group });
    return response.data;
};
// 删除分组
export const deleteGroupApi = async (group, deleteStocks = false) => {
    const response = await api.delete(`/groups/${encodeURIComponent(group)}`, { params: { delete_stocks: deleteStocks } });
    return response.data;
};
// 设置股票预警
export const setAlert = async (code, alertConfig) => {
    const response = await api.post(`/alerts/${code}`, alertConfig);
    return response.data;
};
// 移除股票预警
export const removeAlert = async (code) => {
    const response = await api.delete(`/alerts/${code}`);
    return response.data;
};
// 获取触发的预警
export const getTriggeredAlerts = async () => {
    const response = await api.get('/alerts/triggered');
    return response.data;
};
// 获取股票详情（分时、K线、资金流向）
export const getStockDetail = async (code) => {
    const response = await api.get(`/stock/${code}/detail`);
    return response.data;
};
// 获取分时数据
export const getMinuteData = async (code) => {
    const response = await api.get(`/stock/${code}/minute`);
    return response.data;
};
// 获取K线数据
export const getKlineData = async (code, period = 'day', count = 120) => {
    const response = await api.get(`/stock/${code}/kline`, { params: { period, count } });
    return response.data;
};
// 获取资金流向
export const getMoneyFlow = async (code) => {
    const response = await api.get(`/stock/${code}/money-flow`);
    return response.data;
};
// 获取 AI 模型列表
export const getAIModels = async (provider, apiKey, proxy) => {
    const response = await api.post('/ai/models', {
        provider,
        api_key: apiKey,
        proxy: proxy || null
    });
    return response.data;
};

// AI 分析
export const analyzeStock = async (code, type, provider, apiKey, model, inputs = {}, proxy) => {
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
export default api;
