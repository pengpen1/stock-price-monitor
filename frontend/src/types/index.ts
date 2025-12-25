/**
 * 通用类型定义
 * 集中管理应用中使用的 TypeScript 类型
 */

// ========== 股票相关类型 ==========

/** 股票基本信息 */
export interface StockInfo {
  code: string;
  name: string;
  price: number;
  change_percent: number;
  volume: number;
  amount: number;
  high: number;
  low: number;
  open: number;
  pre_close: number;
  group?: string;
  focused?: boolean;
}

/** 指数信息 */
export interface IndexInfo {
  code: string;
  name: string;
  price: number;
  change_percent: number;
}

/** K线数据 */
export interface KlineData {
  date: string;
  open: number;
  close: number;
  high: number;
  low: number;
  volume: number;
  amount?: number;
}

/** 分时数据 */
export interface MinuteData {
  time: string;
  date: string;
  price: number;
  avg_price?: number;
  volume: number;
}

/** 资金流向数据 */
export interface MoneyFlowData {
  time: string;
  main_in: number;
  big_in: number;
  mid_in: number;
  small_in: number;
  super_in: number;
}

// ========== 交易记录类型 ==========

/** 交易类型 */
export type TradeType = "B" | "S" | "T"; // 买入/卖出/做T

/** 心态类型 */
export type MoodType = "calm" | "anxious" | "panic" | "fear" | "excited";

/** 交易记录 */
export interface TradeRecord {
  id: string;
  stock_code: string;
  stock_name?: string;
  type: TradeType;
  price: number;
  quantity: number;
  reason: string;
  mood: MoodType;
  level: 1 | 2 | 3;
  trade_time: string;
  created_at: string;
}

// ========== AI 分析类型 ==========

/** AI 信号类型 */
export type AISignal = "bullish" | "cautious" | "bearish";

/** AI 分析记录 */
export interface AIRecord {
  id: string;
  stock_code: string;
  signal: AISignal;
  summary: string;
  full_result: string;
  analysis_type: "fast" | "precise";
  model: string;
  datetime: string;
}

/** AI 预测数据 */
export interface AIPrediction {
  date: string;
  price: number;
  change_pct: number;
}

// ========== 模拟交易类型 ==========

/** 模拟会话状态 */
export type SimulationStatus = "running" | "paused" | "completed" | "abandoned";

/** 模拟交易记录 */
export interface SimulationTrade {
  day: number;
  date: string;
  type: "buy" | "sell" | "skip";
  price: number;
  quantity: number;
  reason: string;
  capital_after: number;
  position_after: number;
  auto?: boolean;
}

/** 模拟会话 */
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
  status: SimulationStatus;
  trades: SimulationTrade[];
  kline_start_idx: number;
  created_at: string;
  updated_at: string;
  final_price?: number;
  final_profit_rate?: number;
}

// ========== 笔记类型 ==========

/** 笔记元信息 */
export interface NoteMeta {
  filename: string;
  created_at: string;
  updated_at: string;
  preview: string;
  size: number;
}

// ========== 预警类型 ==========

/** 预警配置 */
export interface AlertConfig {
  take_profit?: number;
  stop_loss?: number;
  price_above?: number;
  price_below?: number;
  change_above?: number;
  change_below?: number;
}

/** 触发的预警 */
export interface TriggeredAlert {
  code: string;
  name: string;
  type: string;
  message: string;
  time: string;
}
