"""
股票数据获取模块

本文件负责从各数据源获取股票相关数据：
1. 实时行情数据（新浪财经）
2. 分时数据（新浪财经）
3. K线数据（新浪财经）
4. 资金流向数据（东方财富）
5. 额外数据（换手率、量比、均线、市盈率等）
6. 龙虎榜数据（东方财富）
7. 北向资金、融资融券数据

数据源：
- 新浪财经：实时行情、分时、K线
- 东方财富：资金流向、龙虎榜、北向资金、融资融券
"""

import re
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime


class StockDataFetcher:
    """
    股票数据获取器
    
    封装了各种股票数据的获取方法
    """
    
    def __init__(self):
        """初始化数据获取器"""
        # 通用请求头
        self.sina_headers = {
            "Referer": "https://finance.sina.com.cn/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.eastmoney_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    @staticmethod
    def normalize_code(code: str) -> str:
        """
        标准化股票代码（添加市场前缀）
        
        Args:
            code: 原始股票代码
            
        Returns:
            标准化后的代码（如 sh600000、sz000001）
        """
        code = code.lower()
        if code.startswith("sh") or code.startswith("sz") or code.startswith("bj"):
            return code
        if code.startswith("6"):
            return f"sh{code}"
        elif code.startswith("0") or code.startswith("3"):
            return f"sz{code}"
        elif code.startswith("4") or code.startswith("8"):
            return f"bj{code}"
        return code
    
    def fetch_realtime_data(self, codes: List[str]) -> Dict[str, dict]:
        """
        获取实时行情数据
        
        Args:
            codes: 股票代码列表
            
        Returns:
            股票数据字典 {code: {name, price, change_percent, ...}}
        """
        if not codes:
            return {}
        
        result = {}
        
        try:
            # 构建查询列表
            query_list = []
            for code in codes:
                code_lower = code.lower()
                if code_lower.startswith("sh") or code_lower.startswith("sz") or code_lower.startswith("bj"):
                    query_list.append(code_lower)
                else:
                    normalized = self.normalize_code(code)
                    if normalized != code:
                        query_list.append(normalized)
            
            if not query_list:
                return {}
            
            codes_str = ",".join(query_list)
            url = f"http://hq.sinajs.cn/list={codes_str}"
            
            resp = requests.get(
                url, 
                headers=self.sina_headers, 
                timeout=5, 
                proxies={"http": None, "https": None}
            )
            content = resp.content.decode('gbk')
            
            lines = content.strip().split('\n')
            for line in lines:
                if not line:
                    continue
                parts = line.split('=')
                if len(parts) < 2:
                    continue
                
                code_part = parts[0].split('_')[-1]
                data_part = parts[1].strip('"')
                if not data_part:
                    continue
                
                fields = data_part.split(',')
                if len(fields) < 30:
                    continue
                
                name = fields[0]
                pre_close = float(fields[2])
                price = float(fields[3])
                high = fields[4]
                low = fields[5]
                time_str = fields[31]
                
                change_percent = 0.0
                if pre_close > 0:
                    change_percent = (price - pre_close) / pre_close * 100
                
                result[code_part] = {
                    "code": code_part,
                    "name": name,
                    "price": f"{price:.2f}",
                    "change_percent": f"{change_percent:.2f}",
                    "high": high,
                    "low": low,
                    "open": fields[1],
                    "pre_close": f"{pre_close:.2f}",
                    "volume": fields[8],
                    "amount": fields[9],
                    "time": time_str
                }
                
        except Exception as e:
            print(f"获取实时数据失败: {e}")
        
        return result
    
    def get_minute_data(self, code: str) -> dict:
        """
        获取分时数据（昨天+今天的分钟数据，包含集合竞价）
        
        Args:
            code: 股票代码
            
        Returns:
            {"status": "success/error", "data": [...], "message": "..."}
        """
        try:
            code = self.normalize_code(code)
            url = f"https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_{code}_data=/CN_MarketDataService.getKLineData?symbol={code}&scale=1&ma=no&datalen=500"
            
            resp = requests.get(
                url, 
                headers=self.sina_headers, 
                timeout=10, 
                proxies={"http": None, "https": None}
            )
            content = resp.text
            
            match = re.search(r'\[.*\]', content)
            if match:
                data = json.loads(match.group())
                result = []
                for item in data:
                    day_str = item.get("day", "")
                    date_part = day_str[:10] if len(day_str) >= 10 else ""
                    time_part = day_str[-8:] if len(day_str) >= 8 else ""
                    result.append({
                        "date": date_part,
                        "time": time_part,
                        "price": float(item.get("close", 0)),
                        "volume": int(item.get("volume", 0)),
                        "avg_price": float(item.get("ma_price5", 0)) if item.get("ma_price5") else None
                    })
                return {"status": "success", "data": result}
            return {"status": "error", "message": "解析失败"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_history_minute_data(self, code: str, date: str) -> dict:
        """
        获取历史某一天的分时数据
        
        注意：新浪接口只能获取最近几天的分时数据
        
        Args:
            code: 股票代码
            date: 日期，格式 YYYY-MM-DD
            
        Returns:
            {"status": "success/error", "data": [...], "message": "..."}
        """
        try:
            code = self.normalize_code(code)
            url = f"https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_{code}_data=/CN_MarketDataService.getKLineData?symbol={code}&scale=1&ma=no&datalen=1000"
            
            resp = requests.get(
                url, 
                headers=self.sina_headers, 
                timeout=10, 
                proxies={"http": None, "https": None}
            )
            content = resp.text
            
            match = re.search(r'\[.*\]', content)
            if match:
                data = json.loads(match.group())
                result = []
                for item in data:
                    day_str = item.get("day", "")
                    date_part = day_str[:10] if len(day_str) >= 10 else ""
                    if date_part == date:
                        time_part = day_str[-8:] if len(day_str) >= 8 else ""
                        result.append({
                            "date": date_part,
                            "time": time_part,
                            "price": float(item.get("close", 0)),
                            "open": float(item.get("open", 0)),
                            "high": float(item.get("high", 0)),
                            "low": float(item.get("low", 0)),
                            "volume": int(item.get("volume", 0)),
                        })
                
                if result:
                    return {"status": "success", "data": result}
                return {"status": "error", "message": f"未找到 {date} 的分时数据"}
            return {"status": "error", "message": "解析失败"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_kline_data(self, code: str, period: str = "day", count: int = 120) -> dict:
        """
        获取K线数据
        
        Args:
            code: 股票代码
            period: 周期 day(日K), week(周K), month(月K)
            count: 数据条数
            
        Returns:
            {"status": "success/error", "data": [...], "message": "..."}
        """
        try:
            code = self.normalize_code(code)
            scale_map = {"day": 240, "week": 1200, "month": 7200}
            scale = scale_map.get(period, 240)
            
            url = f"https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_{code}_kline=/CN_MarketDataService.getKLineData?symbol={code}&scale={scale}&ma=no&datalen={count}"
            
            resp = requests.get(
                url, 
                headers=self.sina_headers, 
                timeout=10, 
                proxies={"http": None, "https": None}
            )
            content = resp.text
            
            match = re.search(r'\[.*\]', content)
            if match:
                data = json.loads(match.group())
                result = []
                for item in data:
                    result.append({
                        "date": item.get("day", ""),
                        "open": float(item.get("open", 0)),
                        "close": float(item.get("close", 0)),
                        "high": float(item.get("high", 0)),
                        "low": float(item.get("low", 0)),
                        "volume": int(item.get("volume", 0)),
                    })
                return {"status": "success", "data": result}
            return {"status": "error", "message": "解析失败"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_money_flow(self, code: str) -> dict:
        """
        获取资金流向数据
        
        Args:
            code: 股票代码
            
        Returns:
            {"status": "success/error", "data": [...], "message": "..."}
        """
        try:
            code = self.normalize_code(code)
            market = "1" if code.startswith("sh") else "0"
            stock_code = code[2:]
            
            # 使用 klt=101 获取日线资金流向，避免 klt=1 分时数据累加导致数值过大
            url = f"https://push2.eastmoney.com/api/qt/stock/fflow/kline/get?secid={market}.{stock_code}&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56&klt=101&lmt=30"
            
            resp = requests.get(
                url, 
                headers=self.eastmoney_headers, 
                timeout=10, 
                proxies={"http": None, "https": None}
            )
            data = resp.json()
            
            if data.get("data") and data["data"].get("klines"):
                result = []
                for line in data["data"]["klines"]:
                    parts = line.split(",")
                    if len(parts) >= 6:
                        result.append({
                            "time": parts[0],
                            "main_in": float(parts[1]),      # 主力流入
                            "small_in": float(parts[2]),     # 小单流入
                            "mid_in": float(parts[3]),       # 中单流入
                            "big_in": float(parts[4]),       # 大单流入
                            "super_in": float(parts[5]),     # 超大单流入
                        })
                return {"status": "success", "data": result}
            return {"status": "error", "message": "无数据"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_stock_extra_data(self, code: str) -> dict:
        """
        获取股票额外数据（用于精准分析）
        
        包含：换手率、量比、振幅、均线、市盈率、市净率、总市值、流通市值、所属行业
        
        Args:
            code: 股票代码
            
        Returns:
            {"status": "success/error", "data": {...}, "message": "..."}
        """
        code = self.normalize_code(code)
        market = "1" if code.startswith("sh") else "0"
        stock_code = code[2:]
        
        result = {
            "turnover_rate": None,  # 换手率
            "volume_ratio": None,   # 量比
            "amplitude": None,      # 振幅
            "pe_ratio": None,       # 市盈率
            "pb_ratio": None,       # 市净率
            "total_mv": None,       # 总市值
            "circ_mv": None,        # 流通市值
            "industry": None,       # 所属行业
            "ma5": None,            # 5日均线
            "ma10": None,           # 10日均线
            "ma20": None,           # 20日均线
            "ma60": None,           # 60日均线
            "north_flow": None,     # 北向资金
            "margin_balance": None, # 融资余额
        }
        
        try:
            # 使用东方财富接口获取详细数据
            # f162: PE(动), f164: PE(TTM), f167: PB, f168: 换手率
            url = f"https://push2.eastmoney.com/api/qt/stock/get?secid={market}.{stock_code}&fields=f43,f44,f45,f46,f47,f48,f50,f51,f52,f55,f57,f58,f60,f61,f62,f162,f164,f167,f168,f84,f85,f100,f116,f117,f162,f167,f168,f171"
            
            resp = requests.get(
                url, 
                headers=self.eastmoney_headers, 
                timeout=10, 
                proxies={"http": None, "https": None}
            )
            data = resp.json()
            
            if data.get("data"):
                d = data["data"]
                result["turnover_rate"] = d.get("f168") / 100 if d.get("f168") else None
                result["volume_ratio"] = d.get("f50") / 100 if d.get("f50") else None
                result["amplitude"] = d.get("f171") / 100 if d.get("f171") else None
                # 优先使用 PE(TTM) f164，如果没有则使用 PE(动) f162
                pe = d.get("f164") if d.get("f164") != "-" else d.get("f162")
                result["pe_ratio"] = pe / 100 if pe else None
                result["pb_ratio"] = d.get("f167") / 100 if d.get("f167") else None
                result["total_mv"] = d.get("f116")
                result["circ_mv"] = d.get("f117")
                result["industry"] = d.get("f100")
        except Exception as e:
            print(f"获取股票额外数据失败: {e}")
        
        # 计算均线数据
        try:
            kline_result = self.get_kline_data(code, "day", 60)
            kline_data = kline_result.get("data", [])
            if kline_data:
                closes = [k["close"] for k in kline_data]
                if len(closes) >= 5:
                    result["ma5"] = round(sum(closes[-5:]) / 5, 2)
                if len(closes) >= 10:
                    result["ma10"] = round(sum(closes[-10:]) / 10, 2)
                if len(closes) >= 20:
                    result["ma20"] = round(sum(closes[-20:]) / 20, 2)
                if len(closes) >= 60:
                    result["ma60"] = round(sum(closes[-60:]) / 60, 2)
        except Exception as e:
            print(f"计算均线失败: {e}")
        
        # 获取北向资金数据
        try:
            result["north_flow"] = self._get_north_flow(code)
        except Exception as e:
            print(f"获取北向资金失败: {e}")
        
        # 获取融资融券数据
        try:
            result["margin_balance"] = self._get_margin_data(code)
        except Exception as e:
            print(f"获取融资融券失败: {e}")
        
        return {"status": "success", "data": result}
    
    def _get_north_flow(self, code: str) -> Optional[List[Dict]]:
        """获取北向资金流入数据（最近5天）"""
        code = self.normalize_code(code)
        market = "1" if code.startswith("sh") else "0"
        stock_code = code[2:]
        
        try:
            url = f"https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?secid={market}.{stock_code}&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56&klt=101&lmt=5"
            
            resp = requests.get(
                url, 
                headers=self.eastmoney_headers, 
                timeout=10, 
                proxies={"http": None, "https": None}
            )
            data = resp.json()
            
            if data.get("data") and data["data"].get("klines"):
                result = []
                for line in data["data"]["klines"]:
                    parts = line.split(",")
                    if len(parts) >= 3:
                        result.append({
                            "date": parts[0],
                            "net_flow": float(parts[1]) if parts[1] != "-" else 0,
                        })
                return result
        except:
            pass
        return None
    
    def _get_margin_data(self, code: str) -> Optional[List[Dict]]:
        """获取融资融券数据"""
        code = self.normalize_code(code)
        stock_code = code[2:]
        
        try:
            url = f"https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPTA_WEB_RZRQ_GGMX&columns=ALL&filter=(SCODE%3D%22{stock_code}%22)&pageNumber=1&pageSize=5&sortTypes=-1&sortColumns=TRADE_DATE"
            
            resp = requests.get(
                url, 
                headers=self.eastmoney_headers, 
                timeout=10, 
                proxies={"http": None, "https": None}
            )
            data = resp.json()
            
            if data.get("result") and data["result"].get("data"):
                items = data["result"]["data"]
                result = []
                for item in items[:5]:
                    result.append({
                        "date": item.get("TRADE_DATE", "")[:10],
                        "rzye": item.get("RZYE"),
                        "rqye": item.get("RQYE"),
                        "rzrqye": item.get("RZRQYE"),
                    })
                return result
        except:
            pass
        return None
    
    def get_dragon_tiger(self, code: str) -> dict:
        """
        获取龙虎榜数据
        
        Args:
            code: 股票代码
            
        Returns:
            {"status": "success/error", "data": [...], "message": "..."}
        """
        code = self.normalize_code(code)
        stock_code = code[2:]
        
        try:
            url = f"https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_DAILYBILLBOARD_DETAILSNEW&columns=ALL&filter=(SECURITY_CODE%3D%22{stock_code}%22)&pageNumber=1&pageSize=5&sortTypes=-1&sortColumns=TRADE_DATE"
            
            resp = requests.get(
                url, 
                headers=self.eastmoney_headers, 
                timeout=10, 
                proxies={"http": None, "https": None}
            )
            data = resp.json()
            
            if data.get("result") and data["result"].get("data"):
                items = data["result"]["data"]
                result = []
                for item in items[:5]:
                    result.append({
                        "date": item.get("TRADE_DATE", "")[:10],
                        "reason": item.get("EXPLANATION"),
                        "close": item.get("CLOSE_PRICE"),
                        "change_pct": item.get("CHANGE_RATE"),
                        "turnover_rate": item.get("TURNOVERRATE"),
                        "net_buy": item.get("NET_BUY_AMT"),
                    })
                return {"status": "success", "data": result}
        except Exception as e:
            print(f"获取龙虎榜失败: {e}")
        return {"status": "success", "data": []}


# 创建全局实例
stock_data_fetcher = StockDataFetcher()
