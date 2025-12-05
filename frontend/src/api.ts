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

export default api;
