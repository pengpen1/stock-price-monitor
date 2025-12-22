"""
复盘记录管理模块
- 交易记录（买入/卖出/做T）
- AI 分析记录
"""
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class RecordsManager:
    """交易记录和 AI 分析记录管理器"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.records_file = data_dir / "records.json"
        self.trade_records: List[Dict] = []  # 交易记录
        self.ai_records: List[Dict] = []  # AI 分析记录
        self._load_data()
    
    def _load_data(self):
        """加载记录数据"""
        if self.records_file.exists():
            try:
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.trade_records = data.get('trade_records', [])
                    self.ai_records = data.get('ai_records', [])
                    print(f"已加载 {len(self.trade_records)} 条交易记录, {len(self.ai_records)} 条 AI 分析记录")
            except Exception as e:
                print(f"加载记录数据失败: {e}")
    
    def _save_data(self):
        """保存记录数据"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.records_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'trade_records': self.trade_records,
                    'ai_records': self.ai_records
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存记录数据失败: {e}")
    
    # ========== 交易记录 CRUD ==========
    
    def add_trade_record(self, stock_code: str, trade_type: str, price: float, 
                         quantity: int, reason: str, trade_time: str = None,
                         mood: str = None, level: int = None, stock_name: str = None) -> Dict:
        """
        添加交易记录
        Args:
            stock_code: 股票代码
            trade_type: 交易类型 B(买入)/S(卖出)/T(做T)
            price: 成交价格
            quantity: 手数
            reason: 操作原因
            trade_time: 交易时间（可选，默认当前时间）
            mood: 当前心态（calm/anxious/panic/fear/excited）
            level: 交易分级（1/2/3）
            stock_name: 股票名称
        """
        record = {
            "id": str(uuid.uuid4()),
            "stock_code": stock_code,
            "stock_name": stock_name or "",
            "type": trade_type.upper(),  # B/S/T
            "price": price,
            "quantity": quantity,
            "reason": reason,
            "mood": mood or "calm",  # 默认平静
            "level": level or 2,  # 默认二级交易
            "trade_time": trade_time or datetime.now().strftime("%Y-%m-%d %H:%M"),
            "created_at": datetime.now().isoformat()
        }
        self.trade_records.append(record)
        self._save_data()
        return {"status": "success", "record": record}
    
    def update_trade_record(self, record_id: str, updates: Dict) -> Dict:
        """更新交易记录"""
        for record in self.trade_records:
            if record["id"] == record_id:
                # 只允许更新特定字段
                allowed_fields = ["type", "price", "quantity", "reason", "trade_time", "mood", "level", "stock_name"]
                for field in allowed_fields:
                    if field in updates:
                        record[field] = updates[field]
                record["updated_at"] = datetime.now().isoformat()
                self._save_data()
                return {"status": "success", "record": record}
        return {"status": "error", "message": "记录不存在"}
    
    def delete_trade_record(self, record_id: str) -> Dict:
        """删除交易记录"""
        for i, record in enumerate(self.trade_records):
            if record["id"] == record_id:
                deleted = self.trade_records.pop(i)
                self._save_data()
                return {"status": "success", "deleted": deleted}
        return {"status": "error", "message": "记录不存在"}
    
    def get_trade_records(self, stock_code: str = None, limit: int = 100) -> Dict:
        """
        获取交易记录
        Args:
            stock_code: 股票代码（可选，不传则返回所有）
            limit: 返回数量限制
        """
        records = self.trade_records
        if stock_code:
            # 支持带前缀和不带前缀的代码匹配
            records = [r for r in records if r["stock_code"] == stock_code 
                      or r["stock_code"].endswith(stock_code) 
                      or stock_code.endswith(r["stock_code"])]
        
        # 按交易时间倒序
        records = sorted(records, key=lambda x: x.get("trade_time", ""), reverse=True)
        return {"status": "success", "records": records[:limit], "total": len(records)}
    
    # ========== AI 分析记录 ==========
    
    def add_ai_record(self, stock_code: str, signal: str, summary: str, 
                      full_result: str, analysis_type: str, model: str) -> Dict:
        """
        添加 AI 分析记录
        Args:
            stock_code: 股票代码
            signal: 信号 bullish(看涨)/cautious(谨慎)/bearish(看跌)
            summary: 简短原因（50字内）
            full_result: 完整分析结果
            analysis_type: 分析类型 fast/precise
            model: 使用的模型
        """
        record = {
            "id": str(uuid.uuid4()),
            "stock_code": stock_code,
            "signal": signal,  # bullish/cautious/bearish
            "summary": summary[:100],  # 限制长度
            "full_result": full_result,
            "analysis_type": analysis_type,
            "model": model,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "created_at": datetime.now().isoformat()
        }
        self.ai_records.append(record)
        self._save_data()
        return {"status": "success", "record": record}
    
    def get_ai_records(self, stock_code: str = None, limit: int = 50) -> Dict:
        """
        获取 AI 分析记录
        Args:
            stock_code: 股票代码（可选）
            limit: 返回数量限制
        """
        records = self.ai_records
        if stock_code:
            records = [r for r in records if r["stock_code"] == stock_code 
                      or r["stock_code"].endswith(stock_code) 
                      or stock_code.endswith(r["stock_code"])]
        
        # 按时间倒序
        records = sorted(records, key=lambda x: x.get("datetime", ""), reverse=True)
        return {"status": "success", "records": records[:limit], "total": len(records)}
    
    def get_ai_records_for_analysis(self, stock_code: str, limit: int = 5) -> List[Dict]:
        """
        获取用于精准分析的历史 AI 记录（简化版，用于发送给模型）
        """
        result = self.get_ai_records(stock_code, limit)
        records = result.get("records", [])
        # 返回简化的记录，只包含关键信息
        return [{
            "datetime": r["datetime"],
            "signal": r["signal"],
            "summary": r["summary"]
        } for r in records]
    
    def get_trade_records_for_analysis(self, stock_code: str, limit: int = 10) -> List[Dict]:
        """
        获取用于精准分析的交易记录（简化版，用于发送给模型）
        """
        result = self.get_trade_records(stock_code, limit)
        records = result.get("records", [])
        return [{
            "trade_time": r["trade_time"],
            "type": r["type"],
            "price": r["price"],
            "quantity": r["quantity"],
            "reason": r["reason"]
        } for r in records]
    
    def calculate_position(self, stock_code: str) -> Dict:
        """
        根据交易记录计算当前持仓成本和数量
        使用移动加权平均法计算成本
        返回: {"cost_price": 成本价, "position": 持仓手数, "total_cost": 总成本}
        """
        result = self.get_trade_records(stock_code, 1000)  # 获取所有记录
        records = result.get("records", [])
        
        if not records:
            return {"cost_price": 0, "position": 0, "total_cost": 0}
        
        # 按时间正序排列
        records = sorted(records, key=lambda x: x.get("trade_time", ""))
        
        position = 0  # 当前持仓手数
        total_cost = 0  # 总成本
        
        for r in records:
            trade_type = r.get("type", "")
            price = r.get("price", 0)
            quantity = r.get("quantity", 0)
            
            if trade_type == "B":  # 买入
                # 增加持仓，更新总成本
                total_cost += price * quantity * 100  # 1手=100股
                position += quantity
            elif trade_type == "S":  # 卖出
                if position > 0:
                    # 减少持仓，按比例减少成本
                    sell_quantity = min(quantity, position)
                    cost_per_share = total_cost / (position * 100) if position > 0 else 0
                    total_cost -= cost_per_share * sell_quantity * 100
                    position -= sell_quantity
            elif trade_type == "T":  # 做T
                # 做T不改变持仓数量，但可能影响成本
                # 从reason中解析买卖价格
                reason = r.get("reason", "")
                import re
                buy_match = re.search(r'买入[:：](\d+\.?\d*)', reason)
                sell_match = re.search(r'卖出[:：](\d+\.?\d*)', reason)
                if buy_match and sell_match:
                    buy_price = float(buy_match.group(1))
                    sell_price = float(sell_match.group(1))
                    # 做T盈亏影响成本
                    t_profit = (sell_price - buy_price) * quantity * 100
                    total_cost -= t_profit  # 盈利降低成本，亏损增加成本
        
        # 计算成本价
        cost_price = total_cost / (position * 100) if position > 0 else 0
        
        return {
            "cost_price": round(cost_price, 3),
            "position": position,
            "total_cost": round(total_cost, 2)
        }
    
    # ========== 数据导出导入 ==========
    
    def export_records(self) -> Dict:
        """导出所有记录"""
        return {
            "trade_records": self.trade_records,
            "ai_records": self.ai_records
        }
    
    def import_records(self, data: Dict) -> Dict:
        """导入记录（合并模式）"""
        imported_trade = 0
        imported_ai = 0
        
        # 导入交易记录
        if "trade_records" in data:
            existing_ids = {r["id"] for r in self.trade_records}
            for record in data["trade_records"]:
                if record.get("id") not in existing_ids:
                    self.trade_records.append(record)
                    imported_trade += 1
        
        # 导入 AI 记录
        if "ai_records" in data:
            existing_ids = {r["id"] for r in self.ai_records}
            for record in data["ai_records"]:
                if record.get("id") not in existing_ids:
                    self.ai_records.append(record)
                    imported_ai += 1
        
        self._save_data()
        return {
            "status": "success",
            "imported_trade_records": imported_trade,
            "imported_ai_records": imported_ai
        }

    # ========== 交易风格分析 ==========
    
    def get_trade_style_analysis(self, stock_code: str = None) -> Dict:
        """
        获取交易风格分析
        Args:
            stock_code: 股票代码（可选，不传则分析所有）
        """
        result = self.get_trade_records(stock_code, 1000)
        records = result.get("records", [])
        
        if not records:
            return {"status": "success", "analysis": None}
        
        # 心态分布统计
        mood_stats = {"calm": 0, "anxious": 0, "panic": 0, "fear": 0, "excited": 0}
        # 分级统计
        level_stats = {1: 0, 2: 0, 3: 0}
        # 分级盈亏统计
        level_profit = {1: {"win": 0, "lose": 0}, 2: {"win": 0, "lose": 0}, 3: {"win": 0, "lose": 0}}
        # 心态盈亏统计
        mood_profit = {m: {"win": 0, "lose": 0} for m in mood_stats.keys()}
        
        # 按股票分组计算盈亏
        stock_trades = {}
        for r in records:
            code = r.get("stock_code", "")
            if code not in stock_trades:
                stock_trades[code] = []
            stock_trades[code].append(r)
        
        # 统计每笔交易
        for r in records:
            mood = r.get("mood", "calm")
            level = r.get("level", 2)
            trade_type = r.get("type", "")
            
            # 心态统计
            if mood in mood_stats:
                mood_stats[mood] += 1
            
            # 分级统计
            if level in level_stats:
                level_stats[level] += 1
        
        # 计算每只股票的盈亏情况
        for code, trades in stock_trades.items():
            trades = sorted(trades, key=lambda x: x.get("trade_time", ""))
            buy_price = 0
            buy_mood = "calm"
            buy_level = 2
            
            for t in trades:
                if t["type"] == "B":
                    buy_price = t["price"]
                    buy_mood = t.get("mood", "calm")
                    buy_level = t.get("level", 2)
                elif t["type"] == "S" and buy_price > 0:
                    # 判断盈亏
                    is_win = t["price"] > buy_price
                    
                    # 分级盈亏
                    if buy_level in level_profit:
                        if is_win:
                            level_profit[buy_level]["win"] += 1
                        else:
                            level_profit[buy_level]["lose"] += 1
                    
                    # 心态盈亏
                    if buy_mood in mood_profit:
                        if is_win:
                            mood_profit[buy_mood]["win"] += 1
                        else:
                            mood_profit[buy_mood]["lose"] += 1
                    
                    buy_price = 0
        
        # 计算各分级胜率
        level_win_rate = {}
        for level, stats in level_profit.items():
            total = stats["win"] + stats["lose"]
            level_win_rate[level] = round(stats["win"] / total * 100, 1) if total > 0 else 0
        
        # 计算各心态胜率
        mood_win_rate = {}
        for mood, stats in mood_profit.items():
            total = stats["win"] + stats["lose"]
            mood_win_rate[mood] = round(stats["win"] / total * 100, 1) if total > 0 else 0
        
        return {
            "status": "success",
            "analysis": {
                "total_records": len(records),
                "mood_stats": mood_stats,
                "level_stats": level_stats,
                "level_profit": level_profit,
                "mood_profit": mood_profit,
                "level_win_rate": level_win_rate,
                "mood_win_rate": mood_win_rate
            }
        }
    
    # ========== MD 导出导入 ==========
    
    def export_to_markdown(self, stock_code: str = None) -> str:
        """
        导出交易记录为 Markdown 格式
        """
        result = self.get_trade_records(stock_code, 1000)
        records = result.get("records", [])
        
        if not records:
            return "# 交易日志\n\n暂无交易记录"
        
        # 按时间正序排列
        records = sorted(records, key=lambda x: x.get("trade_time", ""))
        
        # 心态映射
        mood_map = {
            "calm": "😌 平静",
            "anxious": "😰 焦虑",
            "panic": "😱 慌张",
            "fear": "😨 恐惧",
            "excited": "🤩 亢奋"
        }
        
        # 分级映射
        level_map = {
            1: "⭐ 一级（85%+）",
            2: "⭐⭐ 二级（70%+）",
            3: "⭐⭐⭐ 三级（凑热闹）"
        }
        
        # 类型映射
        type_map = {"B": "买入", "S": "卖出", "T": "做T"}
        
        md = "# 交易日志\n\n"
        md += f"> 导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        md += f"> 记录数量：{len(records)} 条\n\n"
        md += "---\n\n"
        
        current_date = ""
        for r in records:
            trade_date = r.get("trade_time", "")[:10]
            
            # 日期分组
            if trade_date != current_date:
                current_date = trade_date
                md += f"## {current_date}\n\n"
            
            stock_name = r.get("stock_name", "") or r.get("stock_code", "")
            stock_code_str = r.get("stock_code", "")
            trade_type = type_map.get(r.get("type", ""), r.get("type", ""))
            price = r.get("price", 0)
            quantity = r.get("quantity", 0)
            reason = r.get("reason", "")
            mood = mood_map.get(r.get("mood", "calm"), r.get("mood", ""))
            level = level_map.get(r.get("level", 2), str(r.get("level", "")))
            trade_time = r.get("trade_time", "")[-5:] if len(r.get("trade_time", "")) > 5 else ""
            
            md += f"### {stock_name}（{stock_code_str}）- {trade_type}\n\n"
            md += f"- **时间**：{r.get('trade_time', '')}\n"
            md += f"- **价格**：¥{price:.2f}\n"
            md += f"- **数量**：{quantity} 手\n"
            md += f"- **心态**：{mood}\n"
            md += f"- **分级**：{level}\n"
            md += f"- **理由**：{reason}\n\n"
        
        return md
    
    def import_from_markdown(self, md_content: str) -> Dict:
        """
        从 Markdown 格式导入交易记录
        """
        import re
        
        imported = 0
        errors = []
        
        # 心态反向映射
        mood_reverse = {
            "平静": "calm", "焦虑": "anxious", "慌张": "panic",
            "恐惧": "fear", "亢奋": "excited"
        }
        
        # 分级反向映射
        level_reverse = {"一级": 1, "二级": 2, "三级": 3}
        
        # 类型反向映射
        type_reverse = {"买入": "B", "卖出": "S", "做T": "T"}
        
        # 解析每个交易块
        # 匹配格式：### 股票名（代码）- 类型
        pattern = r'###\s+(.+?)（(.+?)）\s*-\s*(\S+)\s*\n([\s\S]*?)(?=###|$)'
        matches = re.findall(pattern, md_content)
        
        for match in matches:
            try:
                stock_name = match[0].strip()
                stock_code = match[1].strip()
                trade_type_str = match[2].strip()
                content = match[3]
                
                # 解析字段
                time_match = re.search(r'\*\*时间\*\*[：:]\s*(.+)', content)
                price_match = re.search(r'\*\*价格\*\*[：:]\s*[¥￥]?([\d.]+)', content)
                quantity_match = re.search(r'\*\*数量\*\*[：:]\s*(\d+)', content)
                mood_match = re.search(r'\*\*心态\*\*[：:]\s*[^\s]*\s*(\S+)', content)
                level_match = re.search(r'\*\*分级\*\*[：:]\s*[^\s]*\s*(\S+)', content)
                reason_match = re.search(r'\*\*理由\*\*[：:]\s*(.+)', content)
                
                if not all([time_match, price_match, quantity_match]):
                    errors.append(f"解析失败：{stock_name} - 缺少必要字段")
                    continue
                
                trade_time = time_match.group(1).strip()
                price = float(price_match.group(1))
                quantity = int(quantity_match.group(1))
                
                # 解析心态
                mood = "calm"
                if mood_match:
                    mood_str = mood_match.group(1).strip()
                    for k, v in mood_reverse.items():
                        if k in mood_str:
                            mood = v
                            break
                
                # 解析分级
                level = 2
                if level_match:
                    level_str = level_match.group(1).strip()
                    for k, v in level_reverse.items():
                        if k in level_str:
                            level = v
                            break
                
                # 解析类型
                trade_type = "B"
                for k, v in type_reverse.items():
                    if k in trade_type_str:
                        trade_type = v
                        break
                
                reason = reason_match.group(1).strip() if reason_match else ""
                
                # 添加记录
                self.add_trade_record(
                    stock_code=stock_code,
                    trade_type=trade_type,
                    price=price,
                    quantity=quantity,
                    reason=reason,
                    trade_time=trade_time,
                    mood=mood,
                    level=level,
                    stock_name=stock_name
                )
                imported += 1
                
            except Exception as e:
                errors.append(f"解析错误：{str(e)}")
        
        return {
            "status": "success",
            "imported": imported,
            "errors": errors
        }
    
    def get_all_stock_codes(self) -> List[str]:
        """获取所有有交易记录的股票代码"""
        codes = set()
        for r in self.trade_records:
            code = r.get("stock_code", "")
            if code:
                codes.add(code)
        return sorted(list(codes))
