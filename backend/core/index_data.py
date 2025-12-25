"""
大盘指数数据获取模块

本文件负责获取大盘指数相关数据：
1. 主要指数实时数据（上证、深证、创业板、沪深300）
2. 市场涨跌家数统计
3. 指数分时数据
4. 指数K线数据

数据源：
- 新浪财经：指数实时行情
- 东方财富：涨跌统计、分时、K线
"""

import requests
from typing import Dict, List
from datetime import datetime


class IndexDataFetcher:
    """
    大盘指数数据获取器
    """
    
    # 主要指数代码
    INDEX_CODES = ["sh000001", "sz399001", "sz399006", "sh000300"]  # 上证、深证、创业板、沪深300
    
    def __init__(self):
        """初始化"""
        self.sina_headers = {
            "Referer": "https://finance.sina.com.cn/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.eastmoney_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def fetch_index_data(self) -> Dict[str, dict]:
        """
        获取大盘指数实时数据
        
        Returns:
            指数数据字典 {code: {name, price, change_percent, ...}}
        """
        result = {}
        
        try:
            codes_str = ",".join(self.INDEX_CODES)
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
                if len(fields) < 6:
                    continue
                
                # 指数数据格式：名称,今开,昨收,当前点位,最高,最低,成交量,成交额,...
                name = fields[0]
                today_open = float(fields[1]) if fields[1] else 0
                pre_close = float(fields[2]) if fields[2] else 0
                price = float(fields[3]) if fields[3] else 0
                high = float(fields[4]) if fields[4] else 0
                low = float(fields[5]) if fields[5] else 0
                volume = fields[6] if len(fields) > 6 else "0"
                amount = fields[7] if len(fields) > 7 else "0"
                
                if price == 0:
                    price = pre_close
                
                change_percent = 0.0
                if pre_close > 0:
                    change_percent = (price - pre_close) / pre_close * 100
                
                result[code_part] = {
                    "code": code_part,
                    "name": name,
                    "price": f"{price:.2f}",
                    "change_percent": f"{change_percent:.2f}",
                    "pre_close": f"{pre_close:.2f}",
                    "open": f"{today_open:.2f}",
                    "high": f"{high:.2f}",
                    "low": f"{low:.2f}",
                    "volume": volume,
                    "amount": amount
                }
        except Exception as e:
            print(f"获取大盘指数失败: {e}")
        
        return result
    
    def fetch_market_stats(self) -> Dict:
        """
        获取市场涨跌家数统计
        
        Returns:
            涨跌统计 {rise_count, fall_count, flat_count, limit_up, limit_down, update_time}
        """
        result = {
            "rise_count": 0,
            "fall_count": 0,
            "flat_count": 0,
            "limit_up": 0,
            "limit_down": 0,
            "update_time": datetime.now().strftime("%H:%M:%S")
        }
        
        try:
            # 获取A股总数
            url = "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=1&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f3"
            resp = requests.get(
                url, 
                headers=self.eastmoney_headers, 
                timeout=5, 
                proxies={"http": None, "https": None}
            )
            data = resp.json()
            total = data.get("data", {}).get("total", 0)
            
            # 获取上涨股票数量
            url_up = "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=1&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f3&fid=f3&filter=(f3>0)"
            resp_up = requests.get(
                url_up, 
                headers=self.eastmoney_headers, 
                timeout=5, 
                proxies={"http": None, "https": None}
            )
            rise_count = resp_up.json().get("data", {}).get("total", 0)
            
            # 获取下跌股票数量
            url_down = "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=1&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f3&fid=f3&filter=(f3<0)"
            resp_down = requests.get(
                url_down, 
                headers=self.eastmoney_headers, 
                timeout=5, 
                proxies={"http": None, "https": None}
            )
            fall_count = resp_down.json().get("data", {}).get("total", 0)
            
            # 获取涨停数量
            url_limit_up = "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=1&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f3&fid=f3&filter=(f3>=9.9)"
            resp_limit_up = requests.get(
                url_limit_up, 
                headers=self.eastmoney_headers, 
                timeout=5, 
                proxies={"http": None, "https": None}
            )
            limit_up = resp_limit_up.json().get("data", {}).get("total", 0)
            
            # 获取跌停数量
            url_limit_down = "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=1&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f3&fid=f3&filter=(f3<=-9.9)"
            resp_limit_down = requests.get(
                url_limit_down, 
                headers=self.eastmoney_headers, 
                timeout=5, 
                proxies={"http": None, "https": None}
            )
            limit_down = resp_limit_down.json().get("data", {}).get("total", 0)
            
            flat_count = total - rise_count - fall_count
            if flat_count < 0:
                flat_count = 0
            
            result = {
                "rise_count": rise_count,
                "fall_count": fall_count,
                "flat_count": flat_count,
                "limit_up": limit_up,
                "limit_down": limit_down,
                "update_time": datetime.now().strftime("%H:%M:%S")
            }
            print(f"涨跌统计: 涨{rise_count} 跌{fall_count} 平{flat_count} 涨停{limit_up} 跌停{limit_down}")
            
        except Exception as e:
            print(f"获取市场涨跌统计失败: {e}")
        
        return result
    
    def get_market_stats_history(self, days: int = 30) -> dict:
        """
        获取涨跌家数历史数据
        
        Args:
            days: 天数
            
        Returns:
            {"status": "success/error", "data": [...], "message": "..."}
        """
        try:
            url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.000001&fields1=f1,f2,f3,f4,f5&fields2=f51,f52,f53,f54,f55,f56,f57&klt=101&fqt=0&end=20500101&lmt={days}"
            
            resp = requests.get(
                url, 
                headers=self.eastmoney_headers, 
                timeout=10, 
                proxies={"http": None, "https": None}
            )
            data = resp.json()
            
            result = []
            if data.get("data") and data["data"].get("klines"):
                for line in data["data"]["klines"]:
                    parts = line.split(",")
                    if len(parts) >= 7:
                        result.append({
                            "date": parts[0],
                            "close": float(parts[2]),
                            "change_pct": float(parts[5]) if parts[5] else 0,
                            "volume": int(float(parts[6])) if parts[6] else 0
                        })
            return {"status": "success", "data": result[-days:]}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_index_minute_data(self, code: str) -> dict:
        """
        获取指数分时数据
        
        Args:
            code: 指数代码
            
        Returns:
            {"status": "success/error", "data": [...], "message": "..."}
        """
        try:
            # 转换代码格式
            if code.startswith("sh"):
                secid = f"1.{code[2:]}"
            else:
                secid = f"0.{code[2:]}"
            
            url = f"https://push2.eastmoney.com/api/qt/stock/trends2/get?secid={secid}&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11&fields2=f51,f52,f53,f54,f55,f56,f57,f58&iscr=0&ndays=2"
            
            resp = requests.get(
                url, 
                headers=self.eastmoney_headers, 
                timeout=10, 
                proxies={"http": None, "https": None}
            )
            data = resp.json()
            
            result = []
            if data.get("data") and data["data"].get("trends"):
                pre_close = data["data"].get("preClose", 0)
                for line in data["data"]["trends"]:
                    parts = line.split(",")
                    if len(parts) >= 6:
                        time_str = parts[0]
                        date_part = time_str[:10] if len(time_str) >= 10 else ""
                        time_part = time_str[-5:] if len(time_str) >= 5 else ""
                        price = float(parts[2]) if parts[2] else 0
                        result.append({
                            "date": date_part,
                            "time": time_part,
                            "price": price,
                            "avg_price": float(parts[3]) if parts[3] else 0,
                            "volume": int(float(parts[5])) if parts[5] else 0,
                            "pre_close": pre_close
                        })
            return {"status": "success", "data": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_index_kline_data(self, code: str, days: int = 60) -> dict:
        """
        获取指数K线数据
        
        Args:
            code: 指数代码
            days: 天数
            
        Returns:
            {"status": "success/error", "data": [...], "message": "..."}
        """
        try:
            if code.startswith("sh"):
                secid = f"1.{code[2:]}"
            else:
                secid = f"0.{code[2:]}"
            
            url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&fields1=f1,f2,f3,f4,f5&fields2=f51,f52,f53,f54,f55,f56,f57&klt=101&fqt=0&end=20500101&lmt={days}"
            
            resp = requests.get(
                url, 
                headers=self.eastmoney_headers, 
                timeout=10, 
                proxies={"http": None, "https": None}
            )
            data = resp.json()
            
            result = []
            if data.get("data") and data["data"].get("klines"):
                for line in data["data"]["klines"]:
                    parts = line.split(",")
                    if len(parts) >= 7:
                        result.append({
                            "date": parts[0],
                            "open": float(parts[1]),
                            "close": float(parts[2]),
                            "high": float(parts[3]),
                            "low": float(parts[4]),
                            "volume": int(float(parts[5])),
                            "amount": float(parts[6])
                        })
            return {"status": "success", "data": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_index_detail(self, code: str, index_data: Dict, market_stats: Dict) -> dict:
        """
        获取大盘指数详情（分时、K线、涨跌统计历史）
        
        Args:
            code: 指数代码
            index_data: 当前指数数据
            market_stats: 当前市场统计
            
        Returns:
            完整的指数详情
        """
        code = code if code.startswith("sh") or code.startswith("sz") else f"sh{code}"
        basic = index_data.get(code, {})
        minute = self.get_index_minute_data(code)
        kline = self.get_index_kline_data(code, days=60)
        stats_history = self.get_market_stats_history(30)
        
        return {
            "status": "success",
            "basic": basic,
            "minute": minute.get("data", []),
            "kline": kline.get("data", []),
            "stats_history": stats_history.get("data", []),
            "current_stats": market_stats
        }


# 创建全局实例
index_data_fetcher = IndexDataFetcher()
