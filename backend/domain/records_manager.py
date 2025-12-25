"""
交易记录管理器

本文件负责管理用户的交易记录和 AI 分析记录：
1. 交易记录的增删改查
2. AI 分析记录的存储和查询
3. 持仓计算（根据交易记录计算成本和数量）
4. 交易风格分析
5. 数据导入导出（Markdown 格式）

数据存储：
- trade_records.json: 交易记录
- ai_records.json: AI 分析记录
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class RecordsManager:
    """
    交易记录管理器
    
    管理用户的交易记录和 AI 分析记录
    """
    
    def __init__(self, data_dir: Path):
        """
        初始化记录管理器
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = data_dir
        self.records_file = data_dir / "records.json"
        self.trade_records: List[Dict] = []
        self.ai_records: List[Dict] = []
        self._load_data()
    
    def _load_data(self):
        """从文件加载数据"""
        if self.records_file.exists():
            try:
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.trade_records = data.get('trade_records', [])
                    self.ai_records = data.get('ai_records', [])
                    print(f"已加载 {len(self.trade_records)} 条交易记录, {len(self.ai_records)} 条AI分析记录")
            except Exception as e:
                print(f"加载记录数据失败: {e}")
    
    def _save_data(self):
        """保存数据到文件"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.records_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'trade_records': self.trade_records,
                    'ai_records': self.ai_records
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存记录数据失败: {e}")
    
    # ========== 交易记录管理 ==========
    
    def add_trade_record(
        self,
        stock_code: str,
        trade_type: str,
        price: float,
        quantity: int,
        reason: str,
        trade_time: str = None,
        mood: str = "calm",
        level: int = 2,
        stock_name: str = None
    ) -> Dict:
        """
        添加交易记录
        
        Args:
            stock_code: 股票代码
            trade_type: 交易类型 B=买入 S=卖出 T=做T
            price: 成交价格
            quantity: 成交数量（股）
            reason: 交易原因
            trade_time: 交易时间（可选，默认当前时间）
            mood: 交易时心态 calm/anxious/panic/fear/excited
            level: 重要程度 1/2/3
            stock_name: 股票名称（可选）
            
        Returns:
            {"status": "success/error", "record": {...}, "message": "..."}
        """
        record = {
            "id": str(uuid.uuid4()),
            "stock_code": stock_code,
            "stock_name": stock_name or "",
            "type": trade_type,
            "price": price,
            "quantity": quantity,
            "reason": reason,
            "trade_time": trade_time or datetime.now().strftime("%Y-%m-%d %H:%M"),
            "mood": mood,
            "level": level,
            "created_at": datetime.now().isoformat()
        }
        
        self.trade_records.append(record)
        self._save_data()
        
        return {"status": "success", "record": record, "message": "交易记录添加成功"}
    
    def update_trade_record(self, record_id: str, updates: Dict) -> Dict:
        """
        更新交易记录
        
        Args:
            record_id: 记录 ID
            updates: 要更新的字段
            
        Returns:
            {"status": "success/error", "record": {...}, "message": "..."}
        """
        for record in self.trade_records:
            if record["id"] == record_id:
                # 更新允许的字段
                allowed_fields = ["type", "price", "quantity", "reason", "trade_time", "mood", "level", "stock_name"]
                for key, value in updates.items():
                    if key in allowed_fields:
                        record[key] = value
                record["updated_at"] = datetime.now().isoformat()
                self._save_data()
                return {"status": "success", "record": record, "message": "更新成功"}
        
        return {"status": "error", "message": "记录不存在"}
    
    def delete_trade_record(self, record_id: str) -> Dict:
        """
        删除交易记录
        
        Args:
            record_id: 记录 ID
            
        Returns:
            {"status": "success/error", "message": "..."}
        """
        for i, record in enumerate(self.trade_records):
            if record["id"] == record_id:
                deleted = self.trade_records.pop(i)
                self._save_data()
                return {"status": "success", "deleted": deleted, "message": "删除成功"}
        
        return {"status": "error", "message": "记录不存在"}
    
    def get_trade_records(self, stock_code: str = None, limit: int = 100) -> Dict:
        """
        获取交易记录
        
        Args:
            stock_code: 股票代码（可选，不传则返回所有）
            limit: 返回数量限制
            
        Returns:
            {"status": "success", "records": [...]}
        """
        records = self.trade_records
        
        if stock_code:
            # 支持模糊匹配（带前缀或不带前缀）
            records = [r for r in records if 
                      r["stock_code"] == stock_code or
                      r["stock_code"].endswith(stock_code) or
                      stock_code.endswith(r["stock_code"])]
        
        # 按交易时间倒序
        records = sorted(records, key=lambda x: x.get("trade_time", ""), reverse=True)
        
        return {"status": "success", "records": records[:limit]}
    
    def get_trade_records_for_analysis(self, stock_code: str, limit: int = 10) -> List[Dict]:
        """
        获取用于 AI 分析的交易记录（简化格式）
        
        Args:
            stock_code: 股票代码
            limit: 返回数量限制
            
        Returns:
            交易记录列表
        """
        result = self.get_trade_records(stock_code, limit)
        records = result.get("records", [])
        
        # 返回简化格式
        return [{
            "trade_time": r["trade_time"],
            "type": r["type"],
            "price": r["price"],
            "quantity": r["quantity"],
            "reason": r["reason"]
        } for r in records]
    
    # ========== AI 分析记录管理 ==========
    
    def add_ai_record(
        self,
        stock_code: str,
        signal: str,
        summary: str,
        full_result: str,
        analysis_type: str,
        model: str
    ) -> Dict:
        """
        添加 AI 分析记录
        
        Args:
            stock_code: 股票代码
            signal: 分析信号 bullish/cautious/bearish
            summary: 一句话摘要
            full_result: 完整分析结果
            analysis_type: 分析类型 fast/precise
            model: 使用的模型
            
        Returns:
            {"status": "success", "record": {...}}
        """
        record = {
            "id": str(uuid.uuid4()),
            "stock_code": stock_code,
            "signal": signal,
            "summary": summary,
            "full_result": full_result,
            "analysis_type": analysis_type,
            "model": model,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        self.ai_records.append(record)
        
        # 只保留最近 200 条 AI 记录
        if len(self.ai_records) > 200:
            self.ai_records = self.ai_records[-200:]
        
        self._save_data()
        return {"status": "success", "record": record}
    
    def get_ai_records(self, stock_code: str = None, limit: int = 50) -> Dict:
        """
        获取 AI 分析记录
        
        Args:
            stock_code: 股票代码（可选）
            limit: 返回数量限制
            
        Returns:
            {"status": "success", "records": [...]}
        """
        records = self.ai_records
        
        if stock_code:
            records = [r for r in records if 
                      r["stock_code"] == stock_code or
                      r["stock_code"].endswith(stock_code) or
                      stock_code.endswith(r["stock_code"])]
        
        # 按时间倒序
        records = sorted(records, key=lambda x: x.get("datetime", ""), reverse=True)
        
        return {"status": "success", "records": records[:limit]}
    
    def get_ai_records_for_analysis(self, stock_code: str, limit: int = 5) -> List[Dict]:
        """
        获取用于 AI 分析的历史记录（简化格式）
        
        Args:
            stock_code: 股票代码
            limit: 返回数量限制
            
        Returns:
            AI 分析记录列表
        """
        result = self.get_ai_records(stock_code, limit)
        records = result.get("records", [])
        
        return [{
            "datetime": r["datetime"],
            "signal": r["signal"],
            "summary": r["summary"]
        } for r in records]
    
    # ========== 持仓计算 ==========
    
    def calculate_position(self, stock_code: str) -> Dict:
        """
        根据交易记录计算持仓成本和数量
        
        使用加权平均法计算成本
        
        Args:
            stock_code: 股票代码
            
        Returns:
            {"status": "success", "position": {...}}
        """
        result = self.get_trade_records(stock_code, 1000)
        records = result.get("records", [])
        
        # 按时间正序处理
        records = sorted(records, key=lambda x: x.get("trade_time", ""))
        
        position = 0  # 当前持仓数量
        total_cost = 0  # 总成本
        
        for record in records:
            trade_type = record["type"]
            price = record["price"]
            quantity = record["quantity"]
            
            if trade_type == "B":  # 买入
                total_cost += price * quantity
                position += quantity
            elif trade_type == "S":  # 卖出
                if position > 0:
                    # 按比例减少成本
                    cost_per_share = total_cost / position
                    total_cost -= cost_per_share * quantity
                    position -= quantity
            elif trade_type == "T":  # 做T（当天买卖，不影响持仓成本）
                pass
        
        # 计算平均成本
        avg_cost = total_cost / position if position > 0 else 0
        
        return {
            "status": "success",
            "position": {
                "stock_code": stock_code,
                "quantity": position,
                "avg_cost": round(avg_cost, 3),
                "total_cost": round(total_cost, 2)
            }
        }
    
    # ========== 交易风格分析 ==========
    
    def get_trade_style_analysis(self, stock_code: str = None) -> Dict:
        """
        分析交易风格
        
        Args:
            stock_code: 股票代码（可选）
            
        Returns:
            {"status": "success", "analysis": {...}}
        """
        result = self.get_trade_records(stock_code, 1000)
        records = result.get("records", [])
        
        if not records:
            return {"status": "success", "analysis": None, "message": "无交易记录"}
        
        # 统计各类数据
        buy_count = sum(1 for r in records if r["type"] == "B")
        sell_count = sum(1 for r in records if r["type"] == "S")
        t_count = sum(1 for r in records if r["type"] == "T")
        
        # 心态统计
        mood_stats = {}
        for r in records:
            mood = r.get("mood", "calm")
            mood_stats[mood] = mood_stats.get(mood, 0) + 1
        
        # 计算胜率（简单计算：卖出价 > 买入价）
        win_count = 0
        total_trades = 0
        buy_price = 0
        
        sorted_records = sorted(records, key=lambda x: x.get("trade_time", ""))
        for r in sorted_records:
            if r["type"] == "B":
                buy_price = r["price"]
            elif r["type"] == "S" and buy_price > 0:
                total_trades += 1
                if r["price"] > buy_price:
                    win_count += 1
        
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        
        return {
            "status": "success",
            "analysis": {
                "total_records": len(records),
                "buy_count": buy_count,
                "sell_count": sell_count,
                "t_count": t_count,
                "mood_stats": mood_stats,
                "win_rate": round(win_rate, 2),
                "completed_trades": total_trades
            }
        }
    
    def get_all_stock_codes(self) -> List[str]:
        """
        获取所有有交易记录的股票代码
        
        Returns:
            股票代码列表
        """
        codes = set()
        for record in self.trade_records:
            codes.add(record["stock_code"])
        return list(codes)
    
    # ========== 导入导出 ==========
    
    def export_to_markdown(self, stock_code: str = None) -> str:
        """
        导出交易记录为 Markdown 格式
        
        Args:
            stock_code: 股票代码（可选）
            
        Returns:
            Markdown 格式的交易记录
        """
        result = self.get_trade_records(stock_code, 1000)
        records = result.get("records", [])
        
        if not records:
            return "# 交易记录\n\n暂无交易记录"
        
        lines = ["# 交易记录\n"]
        lines.append(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        lines.append("| 时间 | 股票 | 类型 | 价格 | 数量 | 原因 | 心态 |")
        lines.append("|---|---|---|---|---|---|---|")
        
        type_map = {"B": "买入", "S": "卖出", "T": "做T"}
        mood_map = {"calm": "平静", "anxious": "焦虑", "panic": "恐慌", "fear": "恐惧", "excited": "兴奋"}
        
        for r in records:
            type_str = type_map.get(r["type"], r["type"])
            mood_str = mood_map.get(r.get("mood", "calm"), r.get("mood", ""))
            stock_name = r.get("stock_name", r["stock_code"])
            lines.append(
                f"| {r['trade_time']} | {stock_name} | {type_str} | {r['price']} | {r['quantity']} | {r['reason']} | {mood_str} |"
            )
        
        return "\n".join(lines)
    
    def import_from_markdown(self, content: str) -> Dict:
        """
        从 Markdown 格式导入交易记录
        
        Args:
            content: Markdown 内容
            
        Returns:
            {"status": "success/error", "imported": 数量, "message": "..."}
        """
        import re
        
        # 解析表格行
        lines = content.strip().split("\n")
        imported = 0
        
        type_map = {"买入": "B", "卖出": "S", "做T": "T"}
        mood_map = {"平静": "calm", "焦虑": "anxious", "恐慌": "panic", "恐惧": "fear", "兴奋": "excited"}
        
        for line in lines:
            if not line.startswith("|") or "---" in line or "时间" in line:
                continue
            
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 6:
                try:
                    trade_time = parts[0]
                    stock_name = parts[1]
                    trade_type = type_map.get(parts[2], parts[2])
                    price = float(parts[3])
                    quantity = int(parts[4])
                    reason = parts[5]
                    mood = mood_map.get(parts[6], "calm") if len(parts) > 6 else "calm"
                    
                    # 尝试从股票名称提取代码
                    code_match = re.search(r'\d{6}', stock_name)
                    stock_code = code_match.group() if code_match else stock_name
                    
                    self.add_trade_record(
                        stock_code=stock_code,
                        trade_type=trade_type,
                        price=price,
                        quantity=quantity,
                        reason=reason,
                        trade_time=trade_time,
                        mood=mood,
                        stock_name=stock_name
                    )
                    imported += 1
                except Exception as e:
                    print(f"导入行失败: {line}, 错误: {e}")
                    continue
        
        return {"status": "success", "imported": imported, "message": f"成功导入 {imported} 条记录"}
