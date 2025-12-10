import time
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime
import os
from pathlib import Path

# 配置文件路径
CONFIG_DIR = Path(__file__).parent / "data"
STOCKS_FILE = CONFIG_DIR / "stocks.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
ALERTS_FILE = CONFIG_DIR / "alerts.json"

# 默认设置
DEFAULT_SETTINGS = {
    "refresh_interval": 5,
    "pushplus_token": "",
    "dingtalk_webhook": "",
    "alert_cooldown": 300,
}

class StockMonitor:
    def __init__(self):
        # 禁用代理
        for k in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "all_proxy", "ALL_PROXY"]:
            os.environ.pop(k, None)
        os.environ["NO_PROXY"] = "*"
        os.environ["no_proxy"] = "*"
        print("代理设置已清除")

        self.running = False
        self.stocks: List[str] = []
        self.data: Dict[str, dict] = {}
        self.settings: Dict = DEFAULT_SETTINGS.copy()
        self.alerts: Dict[str, dict] = {}
        self.alert_cooldowns: Dict[str, float] = {}
        self.triggered_alerts: List[dict] = []
        # 重点关注的股票代码
        self.focused_stock: Optional[str] = None
        
        self._load_data()
    
    def _ensure_data_dir(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_data(self):
        """从本地文件加载数据"""
        self._ensure_data_dir()
        
        # 加载股票列表和重点关注
        if STOCKS_FILE.exists():
            try:
                with open(STOCKS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.stocks = data.get('stocks', [])
                    self.focused_stock = data.get('focused_stock')
                    print(f"已加载 {len(self.stocks)} 只股票, 重点关注: {self.focused_stock}")
            except Exception as e:
                print(f"加载股票列表失败: {e}")
        
        # 加载设置
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
                    print("已加载设置")
            except Exception as e:
                print(f"加载设置失败: {e}")
        
        # 加载预警配置
        if ALERTS_FILE.exists():
            try:
                with open(ALERTS_FILE, 'r', encoding='utf-8') as f:
                    self.alerts = json.load(f)
                    print(f"已加载 {len(self.alerts)} 个预警配置")
            except Exception as e:
                print(f"加载预警配置失败: {e}")
    
    def _save_stocks(self):
        self._ensure_data_dir()
        try:
            with open(STOCKS_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'stocks': self.stocks,
                    'focused_stock': self.focused_stock
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存股票列表失败: {e}")
    
    def _save_settings(self):
        self._ensure_data_dir()
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def _save_alerts(self):
        self._ensure_data_dir()
        try:
            with open(ALERTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.alerts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存预警配置失败: {e}")
    
    # ========== 设置相关 ==========
    def get_settings(self):
        return {"status": "success", "settings": self.settings}
    
    def update_settings(self, new_settings: Dict):
        self.settings.update(new_settings)
        self._save_settings()
        return {"status": "success", "message": "设置已更新", "settings": self.settings}

    # ========== 股票管理 ==========
    def add_stock(self, code: str):
        if code not in self.stocks:
            self.stocks.append(code)
            self._save_stocks()
            return {"status": "success", "message": f"已添加 {code}"}
        return {"status": "error", "message": "股票已存在"}

    def remove_stock(self, code: str):
        removed = False
        if code in self.stocks:
            self.stocks.remove(code)
            removed = True
        else:
            for s in self.stocks[:]:
                if s.endswith(code) or code.endswith(s):
                    self.stocks.remove(s)
                    removed = True
                    break
        
        # 清理数据和预警
        if code in self.data:
            del self.data[code]
        if code in self.alerts:
            del self.alerts[code]
            self._save_alerts()
        
        keys_to_remove = [k for k in self.data.keys() if k.endswith(code) or code.endswith(k)]
        for k in keys_to_remove:
            del self.data[k]
        
        if removed:
            self._save_stocks()
            return {"status": "success", "message": f"已删除 {code}"}
        return {"status": "error", "message": "股票不存在"}

    def reorder_stocks(self, new_order: List[str]):
        """重新排序股票列表"""
        self.stocks = new_order
        self._save_stocks()
        return {"status": "success", "message": "排序已更新"}

    def get_stocks(self):
        # 获取重点关注的股票（默认第一个）
        focused = self.focused_stock
        if not focused and self.stocks:
            focused = self.stocks[0]
        
        # 获取重点关注股票的数据
        focused_data = None
        if focused and focused in self.data:
            focused_data = self.data[focused]
        
        return {
            "stocks": self.stocks,
            "data": self.data,
            "alerts": self.alerts,
            "focused_stock": focused,
            "focused_data": focused_data
        }
    
    def set_focused_stock(self, code: str):
        """设置重点关注的股票"""
        self.focused_stock = code
        self._save_stocks()
        return {"status": "success", "message": f"已设置 {code} 为重点关注"}

    # ========== 预警管理 ==========
    def set_alert(self, code: str, alert_config: dict):
        """设置股票预警"""
        self.alerts[code] = {
            "take_profit": alert_config.get("take_profit"),  # 止盈价
            "stop_loss": alert_config.get("stop_loss"),      # 止损价
            "change_alert": alert_config.get("change_alert"), # 涨跌幅预警(%)
            "enabled": alert_config.get("enabled", True),
        }
        self._save_alerts()
        return {"status": "success", "message": f"已设置 {code} 的预警"}
    
    def remove_alert(self, code: str):
        """移除股票预警"""
        if code in self.alerts:
            del self.alerts[code]
            self._save_alerts()
            return {"status": "success", "message": f"已移除 {code} 的预警"}
        return {"status": "error", "message": "预警不存在"}
    
    def get_triggered_alerts(self):
        """获取触发的预警"""
        alerts = self.triggered_alerts.copy()
        self.triggered_alerts.clear()
        return {"status": "success", "alerts": alerts}
    
    def _check_alerts(self, code: str, stock_data: dict):
        """检查是否触发预警"""
        if code not in self.alerts:
            return
        
        alert_config = self.alerts[code]
        if not alert_config.get("enabled", True):
            return
        
        # 检查冷却时间
        now = time.time()
        cooldown = self.settings.get("alert_cooldown", 300)
        if code in self.alert_cooldowns:
            if now - self.alert_cooldowns[code] < cooldown:
                return
        
        price = float(stock_data["price"])
        change = float(stock_data["change_percent"])
        triggered = []
        
        # 止盈检查
        take_profit = alert_config.get("take_profit")
        if take_profit and price >= float(take_profit):
            triggered.append(f"🎯 止盈触发: 当前价 {price} >= 止盈价 {take_profit}")
        
        # 止损检查
        stop_loss = alert_config.get("stop_loss")
        if stop_loss and price <= float(stop_loss):
            triggered.append(f"⚠️ 止损触发: 当前价 {price} <= 止损价 {stop_loss}")
        
        # 涨跌幅检查
        change_alert = alert_config.get("change_alert")
        if change_alert and abs(change) >= float(change_alert):
            direction = "涨" if change > 0 else "跌"
            triggered.append(f"📊 异动提醒: {direction}幅 {change}% >= {change_alert}%")
        
        if triggered:
            self.alert_cooldowns[code] = now
            alert_info = {
                "code": code,
                "name": stock_data.get("name", code),
                "price": price,
                "change": change,
                "messages": triggered,
                "time": datetime.now().strftime("%H:%M:%S"),
            }
            self.triggered_alerts.append(alert_info)
            print(f"预警触发: {alert_info}")
            self._send_notification(alert_info)
    
    def _send_notification(self, alert_info: dict):
        """发送推送通知"""
        title = f"股票预警 - {alert_info['name']}"
        content = "\n".join(alert_info["messages"])
        content += f"\n当前价: {alert_info['price']} | 涨跌幅: {alert_info['change']}%"
        
        # PushPlus 推送
        token = self.settings.get("pushplus_token")
        if token:
            try:
                requests.post(
                    "http://www.pushplus.plus/send",
                    json={"token": token, "title": title, "content": content},
                    timeout=5
                )
            except Exception as e:
                print(f"PushPlus 推送失败: {e}")
        
        # 钉钉推送
        webhook = self.settings.get("dingtalk_webhook")
        if webhook:
            try:
                requests.post(
                    webhook,
                    json={"msgtype": "text", "text": {"content": f"{title}\n{content}"}},
                    timeout=5
                )
            except Exception as e:
                print(f"钉钉推送失败: {e}")

    # ========== 数据获取 ==========
    def fetch_data(self):
        if not self.stocks:
            return
        
        try:
            query_list = []
            for code in self.stocks:
                if code.startswith("sh") or code.startswith("sz") or code.startswith("bj"):
                    query_list.append(code)
                else:
                    if code.startswith("6"):
                        query_list.append(f"sh{code}")
                    elif code.startswith("0") or code.startswith("3"):
                        query_list.append(f"sz{code}")
                    elif code.startswith("4") or code.startswith("8"):
                        query_list.append(f"bj{code}")
                    else:
                        query_list.append(code)

            codes_str = ",".join(query_list)
            url = f"http://hq.sinajs.cn/list={codes_str}"
            headers = {
                "Referer": "https://finance.sina.com.cn/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            resp = requests.get(url, headers=headers, timeout=5, proxies={"http": None, "https": None})
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
                
                stock_data = {
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
                
                if code_part not in self.stocks:
                    raw_code = code_part[2:]
                    if raw_code in self.stocks:
                        self.stocks.remove(raw_code)
                        self.stocks.append(code_part)
                        self._save_stocks()
                
                self.data[code_part] = stock_data
                
                # 检查预警
                self._check_alerts(code_part, stock_data)
                
        except Exception as e:
            print(f"获取数据失败: {e}")

    def _normalize_code(self, code: str) -> str:
        """标准化股票代码（添加市场前缀）"""
        if code.startswith("sh") or code.startswith("sz") or code.startswith("bj"):
            return code
        if code.startswith("6"):
            return f"sh{code}"
        elif code.startswith("0") or code.startswith("3"):
            return f"sz{code}"
        elif code.startswith("4") or code.startswith("8"):
            return f"bj{code}"
        return code

    def get_minute_data(self, code: str) -> dict:
        """获取分时数据（昨天+今天的分钟数据，包含集合竞价）"""
        try:
            code = self._normalize_code(code)
            # 获取480条数据（约2天的分时数据，包含集合竞价时段）
            url = f"https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_{code}_data=/CN_MarketDataService.getKLineData?symbol={code}&scale=1&ma=no&datalen=500"
            headers = {
                "Referer": "https://finance.sina.com.cn/",
                "User-Agent": "Mozilla/5.0"
            }
            resp = requests.get(url, headers=headers, timeout=10, proxies={"http": None, "https": None})
            content = resp.text
            
            # 解析 JSONP 响应
            import re
            match = re.search(r'\[.*\]', content)
            if match:
                import json
                data = json.loads(match.group())
                # 返回分时数据：日期、时间、价格、成交量
                result = []
                for item in data:
                    day_str = item.get("day", "")
                    # day_str 格式: "2024-12-10 09:30:00"
                    date_part = day_str[:10] if len(day_str) >= 10 else ""
                    time_part = day_str[-8:] if len(day_str) >= 8 else ""
                    result.append({
                        "date": date_part,  # 日期部分，用于区分昨天和今天
                        "time": time_part,  # 时间部分 HH:MM:SS
                        "price": float(item.get("close", 0)),
                        "volume": int(item.get("volume", 0)),
                        "avg_price": float(item.get("ma_price5", 0)) if item.get("ma_price5") else None
                    })
                return {"status": "success", "data": result}
            return {"status": "error", "message": "解析失败"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_kline_data(self, code: str, period: str = "day", count: int = 120) -> dict:
        """
        获取K线数据
        period: day(日K), week(周K), month(月K)
        """
        try:
            code = self._normalize_code(code)
            scale_map = {"day": 240, "week": 1200, "month": 7200}
            scale = scale_map.get(period, 240)
            
            url = f"https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_{code}_kline=/CN_MarketDataService.getKLineData?symbol={code}&scale={scale}&ma=no&datalen={count}"
            headers = {
                "Referer": "https://finance.sina.com.cn/",
                "User-Agent": "Mozilla/5.0"
            }
            resp = requests.get(url, headers=headers, timeout=10, proxies={"http": None, "https": None})
            content = resp.text
            
            import re
            match = re.search(r'\[.*\]', content)
            if match:
                import json
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
        """获取资金流向数据"""
        try:
            code = self._normalize_code(code)
            # 使用东方财富资金流向接口
            market = "1" if code.startswith("sh") else "0"
            stock_code = code[2:]
            url = f"https://push2.eastmoney.com/api/qt/stock/fflow/kline/get?secid={market}.{stock_code}&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56&klt=1&lmt=0"
            
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10, proxies={"http": None, "https": None})
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

    def get_stock_detail(self, code: str) -> dict:
        """获取股票详细信息（包含分时、K线、资金流向）"""
        code = self._normalize_code(code)
        basic = self.data.get(code, {})
        minute = self.get_minute_data(code)
        kline = self.get_kline_data(code, "day", 60)
        money_flow = self.get_money_flow(code)
        
        return {
            "status": "success",
            "basic": basic,
            "minute": minute.get("data", []),
            "kline": kline.get("data", []),
            "money_flow": money_flow.get("data", [])
        }

    def start(self):
        self.running = True
        print("监控已启动")
        while self.running:
            if self.stocks:
                self.fetch_data()
            time.sleep(self.settings.get("refresh_interval", 5))
    
    def stop(self):
        self.running = False
        print("监控已停止")
