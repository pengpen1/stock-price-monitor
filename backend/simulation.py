"""
实盘模拟模块
- 模拟会话管理
- 历史数据获取
- AI 评分分析
"""
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path


class SimulationManager:
    """实盘模拟管理器"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.simulations_file = data_dir / "simulations.json"
        self.sessions: List[Dict] = []
        self._load_data()
    
    def _load_data(self):
        """加载模拟数据"""
        if self.simulations_file.exists():
            try:
                with open(self.simulations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sessions = data.get('sessions', [])
                    print(f"已加载 {len(self.sessions)} 条模拟记录")
            except Exception as e:
                print(f"加载模拟数据失败: {e}")
    
    def _save_data(self):
        """保存模拟数据"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.simulations_file, 'w', encoding='utf-8') as f:
                json.dump({'sessions': self.sessions}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存模拟数据失败: {e}")
    
    def create_session(self, stock_code: str, stock_name: str, total_days: int,
                       initial_capital: float, kline_data: List[Dict]) -> Dict:
        """
        创建模拟会话
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            total_days: 模拟天数
            initial_capital: 初始资金
            kline_data: K线数据（用于确定日期范围）
        """
        if len(kline_data) < total_days + 1:
            return {"status": "error", "message": f"历史数据不足，需要至少 {total_days + 1} 天数据"}
        
        # 从倒数第二天开始（留最后一天作为结算参考）
        # 模拟范围：kline_data[-(total_days+1)] 到 kline_data[-2]
        start_idx = len(kline_data) - total_days - 1
        end_idx = len(kline_data) - 1
        
        start_date = kline_data[start_idx]['date']
        end_date = kline_data[end_idx - 1]['date']  # 最后一个交易日
        
        session = {
            "id": str(uuid.uuid4()),
            "stock_code": stock_code,
            "stock_name": stock_name,
            "start_date": start_date,
            "end_date": end_date,
            "current_day": 0,
            "total_days": total_days,
            "initial_capital": initial_capital,
            "current_capital": initial_capital,
            "position": 0,
            "cost_price": 0,
            "status": "running",
            "trades": [],
            "kline_start_idx": start_idx,  # K线起始索引
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.sessions.append(session)
        self._save_data()
        
        return {"status": "success", "session": session}
    
    def get_session(self, session_id: str) -> Dict:
        """获取模拟会话"""
        for session in self.sessions:
            if session["id"] == session_id:
                return {"status": "success", "session": session}
        return {"status": "error", "message": "会话不存在"}
    
    def get_sessions(self, stock_code: str = None, status: str = None, limit: int = 50) -> Dict:
        """获取模拟会话列表"""
        sessions = self.sessions
        
        if stock_code:
            sessions = [s for s in sessions if s["stock_code"] == stock_code
                       or s["stock_code"].endswith(stock_code)
                       or stock_code.endswith(s["stock_code"])]
        
        if status:
            sessions = [s for s in sessions if s["status"] == status]
        
        # 按更新时间倒序
        sessions = sorted(sessions, key=lambda x: x.get("updated_at", ""), reverse=True)
        
        return {"status": "success", "sessions": sessions[:limit], "total": len(sessions)}
    
    def execute_trade(self, session_id: str, trade_type: str, price: float,
                      quantity: int, reason: str, current_date: str) -> Dict:
        """
        执行交易
        Args:
            session_id: 会话ID
            trade_type: 交易类型 buy/sell/skip
            price: 成交价格
            quantity: 股数（100的倍数）
            reason: 交易理由
            current_date: 当前日期
        """
        session = None
        for s in self.sessions:
            if s["id"] == session_id:
                session = s
                break
        
        if not session:
            return {"status": "error", "message": "会话不存在"}
        
        if session["status"] != "running":
            return {"status": "error", "message": "会话已结束或暂停"}
        
        # 计算交易
        if trade_type == "buy":
            cost = price * quantity
            if cost > session["current_capital"]:
                return {"status": "error", "message": "资金不足"}
            
            # 更新持仓成本（加权平均）
            total_cost = session["cost_price"] * session["position"] + cost
            session["position"] += quantity
            session["cost_price"] = total_cost / session["position"] if session["position"] > 0 else 0
            session["current_capital"] -= cost
            
        elif trade_type == "sell":
            if quantity > session["position"]:
                return {"status": "error", "message": "持仓不足"}
            
            session["position"] -= quantity
            session["current_capital"] += price * quantity
            
            # 清仓时重置成本
            if session["position"] == 0:
                session["cost_price"] = 0
        
        # 记录交易
        trade = {
            "day": session["current_day"],
            "date": current_date,
            "type": trade_type,
            "price": price,
            "quantity": quantity,
            "reason": reason,
            "capital_after": session["current_capital"],
            "position_after": session["position"]
        }
        session["trades"].append(trade)
        
        # 进入下一天
        session["current_day"] += 1
        session["updated_at"] = datetime.now().isoformat()
        
        # 检查是否结束
        if session["current_day"] >= session["total_days"]:
            session["status"] = "completed"
            # 保存最终价格用于计算收益（由API层传入）
            session["final_price"] = price
        
        self._save_data()
        
        return {"status": "success", "session": session, "trade": trade}
    
    def pause_session(self, session_id: str) -> Dict:
        """暂停会话"""
        for session in self.sessions:
            if session["id"] == session_id:
                if session["status"] == "running":
                    session["status"] = "paused"
                    session["updated_at"] = datetime.now().isoformat()
                    self._save_data()
                    return {"status": "success", "session": session}
                return {"status": "error", "message": "会话状态不允许暂停"}
        return {"status": "error", "message": "会话不存在"}
    
    def resume_session(self, session_id: str) -> Dict:
        """继续会话"""
        for session in self.sessions:
            if session["id"] == session_id:
                if session["status"] == "paused":
                    session["status"] = "running"
                    session["updated_at"] = datetime.now().isoformat()
                    self._save_data()
                    return {"status": "success", "session": session}
                return {"status": "error", "message": "会话状态不允许继续"}
        return {"status": "error", "message": "会话不存在"}
    
    def abandon_session(self, session_id: str) -> Dict:
        """放弃会话"""
        for session in self.sessions:
            if session["id"] == session_id:
                session["status"] = "abandoned"
                session["updated_at"] = datetime.now().isoformat()
                self._save_data()
                return {"status": "success", "session": session}
        return {"status": "error", "message": "会话不存在"}
    
    def complete_session(self, session_id: str, final_price: float) -> Dict:
        """
        完成模拟会话，自动清仓并计算最终收益
        Args:
            session_id: 会话ID
            final_price: 最终价格（用于计算持仓市值和自动清仓）
        """
        for session in self.sessions:
            if session["id"] == session_id:
                # 保存最终价格
                session["final_price"] = final_price
                
                # 如果还有持仓，自动清仓
                if session["position"] > 0:
                    auto_sell_amount = session["position"] * final_price
                    session["current_capital"] += auto_sell_amount
                    
                    # 记录自动清仓交易
                    auto_trade = {
                        "day": session["current_day"],
                        "date": session.get("end_date", ""),
                        "type": "sell",
                        "price": final_price,
                        "quantity": session["position"],
                        "reason": "模拟结束自动清仓",
                        "capital_after": session["current_capital"],
                        "position_after": 0,
                        "auto": True  # 标记为自动交易
                    }
                    session["trades"].append(auto_trade)
                    session["position"] = 0
                    session["cost_price"] = 0
                
                # 计算最终收益率
                profit_rate = ((session["current_capital"] - session["initial_capital"]) 
                              / session["initial_capital"] * 100)
                session["final_profit_rate"] = round(profit_rate, 2)
                
                session["updated_at"] = datetime.now().isoformat()
                self._save_data()
                return {"status": "success", "session": session}
        return {"status": "error", "message": "会话不存在"}
    
    def delete_session(self, session_id: str) -> Dict:
        """删除会话"""
        for i, session in enumerate(self.sessions):
            if session["id"] == session_id:
                deleted = self.sessions.pop(i)
                self._save_data()
                return {"status": "success", "deleted": deleted}
        return {"status": "error", "message": "会话不存在"}
    
    def calculate_result(self, session: Dict, final_price: float) -> Dict:
        """
        计算模拟结果
        Args:
            session: 会话数据
            final_price: 最终价格（用于计算持仓市值）
        """
        # 计算最终资产
        position_value = session["position"] * final_price
        final_capital = session["current_capital"] + position_value
        initial_capital = session["initial_capital"]
        
        # 收益率
        profit_rate = (final_capital - initial_capital) / initial_capital * 100
        
        # 计算胜率和最大回撤
        trades = [t for t in session["trades"] if t["type"] != "skip"]
        win_count = 0
        total_trades = 0
        
        # 简单计算：卖出时盈利算赢
        buy_price = 0
        for trade in session["trades"]:
            if trade["type"] == "buy":
                buy_price = trade["price"]
            elif trade["type"] == "sell" and buy_price > 0:
                total_trades += 1
                if trade["price"] > buy_price:
                    win_count += 1
        
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        
        # 计算最大回撤
        max_capital = initial_capital
        max_drawdown = 0
        for trade in session["trades"]:
            capital = trade["capital_after"]
            if capital > max_capital:
                max_capital = capital
            drawdown = (max_capital - capital) / max_capital * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return {
            "final_capital": round(final_capital, 2),
            "profit_rate": round(profit_rate, 2),
            "win_rate": round(win_rate, 2),
            "max_drawdown": round(max_drawdown, 2),
            "total_trades": len(trades),
            "position_value": round(position_value, 2)
        }
    
    def format_for_ai_analysis(self, session: Dict, kline_data: List[Dict], 
                               result: Dict) -> str:
        """
        格式化数据用于 AI 分析
        """
        # 获取模拟期间的K线数据
        start_idx = session.get("kline_start_idx", 0)
        end_idx = start_idx + session["total_days"] + 1
        sim_kline = kline_data[start_idx:end_idx]
        
        prompt = f"""请对以下股票模拟交易进行评分和分析：

## 基本信息
- 股票：{session['stock_name']}（{session['stock_code']}）
- 模拟周期：{session['start_date']} 至 {session['end_date']}（{session['total_days']}个交易日）
- 初始资金：{session['initial_capital']:,.0f}元

## 交易结果
- 最终资产：{result['final_capital']:,.0f}元
- 收益率：{result['profit_rate']:.2f}%
- 胜率：{result['win_rate']:.2f}%
- 最大回撤：{result['max_drawdown']:.2f}%
- 交易次数：{result['total_trades']}次

## K线数据（模拟期间）
日期 | 开盘 | 收盘 | 最高 | 最低 | 涨跌幅
"""
        for k in sim_kline:
            change = ((k['close'] - k['open']) / k['open'] * 100) if k['open'] > 0 else 0
            prompt += f"{k['date']} | {k['open']:.2f} | {k['close']:.2f} | {k['high']:.2f} | {k['low']:.2f} | {change:+.2f}%\n"
        
        prompt += "\n## 交易记录\n"
        for trade in session["trades"]:
            if trade["type"] == "skip":
                prompt += f"- {trade['date']}：跳过（{trade['reason']}）\n"
            elif trade["type"] == "buy":
                prompt += f"- {trade['date']}：买入 {trade['quantity']}股 @ {trade['price']:.2f}元（{trade['reason']}）\n"
            else:
                prompt += f"- {trade['date']}：卖出 {trade['quantity']}股 @ {trade['price']:.2f}元（{trade['reason']}）\n"
        
        prompt += """
## 请按以下JSON格式返回评分结果：
```json
{
  "score": 75,
  "grade": "B",
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["不足1", "不足2"],
  "suggestions": ["建议1", "建议2"],
  "analysis": "详细分析文字..."
}
```

评分标准：
- S级(90-100)：优秀的交易策略，风险控制得当
- A级(80-89)：良好的交易表现，有小幅改进空间
- B级(70-79)：中等水平，需要改进部分策略
- C级(60-69)：及格水平，存在明显问题
- D级(0-59)：需要大幅改进

请综合考虑：收益率、胜率、最大回撤、交易时机、仓位管理、风险控制等因素。
"""
        return prompt
