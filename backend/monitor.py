import time
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime
import os
import sys
from pathlib import Path

def get_default_data_dir() -> Path:
    """
    获取默认数据存储目录
    - 打包后：使用用户数据目录 %APPDATA%/stock-monitor（Windows）或 ~/.stock-monitor（Mac/Linux）
    - 开发模式：使用项目目录下的 data 文件夹
    """
    if getattr(sys, 'frozen', False):
        # 打包后，使用用户数据目录
        if sys.platform == 'win32':
            base = Path(os.environ.get('APPDATA', os.path.expanduser('~')))
        else:
            base = Path.home()
        data_dir = base / 'stock-monitor' / 'data'
    else:
        # 开发模式，使用项目目录
        data_dir = Path(__file__).parent / "data"
    return data_dir

def get_config_file() -> Path:
    """获取全局配置文件路径（存储自定义数据路径等）"""
    if getattr(sys, 'frozen', False):
        if sys.platform == 'win32':
            base = Path(os.environ.get('APPDATA', os.path.expanduser('~')))
        else:
            base = Path.home()
        return base / 'stock-monitor' / 'config.json'
    else:
        return Path(__file__).parent / "config.json"

def load_custom_data_path() -> Optional[str]:
    """从全局配置加载自定义数据路径"""
    config_file = get_config_file()
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('data_path')
        except:
            pass
    return None

def save_custom_data_path(path: str):
    """保存自定义数据路径到全局配置"""
    config_file = get_config_file()
    config_file.parent.mkdir(parents=True, exist_ok=True)
    config = {}
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            pass
    config['data_path'] = path
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def get_data_dir() -> Path:
    """获取实际使用的数据目录（优先使用自定义路径）"""
    custom_path = load_custom_data_path()
    if custom_path and Path(custom_path).exists():
        return Path(custom_path)
    return get_default_data_dir()

# 配置文件路径（初始化时设置，后续可能动态更新）
CONFIG_DIR = get_data_dir()
STOCKS_FILE = CONFIG_DIR / "stocks.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
ALERTS_FILE = CONFIG_DIR / "alerts.json"

# 默认设置
DEFAULT_SETTINGS = {
    "refresh_interval": 5,
    "pushplus_token": "",
    "dingtalk_webhook": "",
    "alert_cooldown": 300,
    # AI 配置
    "ai_provider": "gemini",
    "ai_api_key": "",
    "ai_model": "",
    "ai_proxy": "",
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
        # 股票分组: {code: group_name}
        self.stock_groups: Dict[str, str] = {}
        # 分组列表
        self.group_list: List[str] = []
        # 大盘指数数据
        self.index_data: Dict[str, dict] = {}
        # 大盘指数代码
        self.index_codes = ["sh000001", "sz399001", "sz399006", "sh000300"]  # 上证、深证、创业板、沪深300
        # 市场涨跌统计
        self.market_stats: Dict[str, any] = {}
        # 涨跌家数历史（最近30天）
        self.market_stats_history: List[Dict] = []
        
        self._load_data()
    
    def _ensure_data_dir(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        print(f"数据目录: {CONFIG_DIR}")
    
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
                    self.stock_groups = data.get('groups', {})
                    self.group_list = data.get('group_list', [])
                    print(f"已加载 {len(self.stocks)} 只股票, {len(self.group_list)} 个分组")
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
                    'focused_stock': self.focused_stock,
                    'groups': self.stock_groups,
                    'group_list': self.group_list
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
            "focused_data": focused_data,
            "groups": self.stock_groups,
            "group_list": self.group_list,
            "index_data": self.index_data
        }
    
    def set_stock_group(self, code: str, group: str):
        """设置股票分组"""
        if group:
            self.stock_groups[code] = group
            # 如果是新分组，添加到分组列表
            if group not in self.group_list:
                self.group_list.append(group)
        elif code in self.stock_groups:
            del self.stock_groups[code]
        self._save_stocks()
        return {"status": "success", "message": f"已设置 {code} 分组为 {group}"}
    
    def add_group(self, group: str):
        """添加新分组"""
        if group and group not in self.group_list:
            self.group_list.append(group)
            self._save_stocks()
            return {"status": "success", "message": f"已添加分组 {group}"}
        return {"status": "error", "message": "分组已存在或名称为空"}
    
    def get_groups(self):
        """获取所有分组"""
        return {"status": "success", "groups": self.group_list}
    
    def delete_group(self, group: str, delete_stocks: bool = False):
        """删除分组
        Args:
            group: 分组名称
            delete_stocks: 是否同时删除分组内的股票
        """
        if group not in self.group_list:
            return {"status": "error", "message": "分组不存在"}
        
        # 找出该分组下的所有股票
        stocks_in_group = [code for code, g in self.stock_groups.items() if g == group]
        
        if delete_stocks:
            # 删除分组内的所有股票
            for code in stocks_in_group:
                if code in self.stocks:
                    self.stocks.remove(code)
                if code in self.data:
                    del self.data[code]
                if code in self.alerts:
                    del self.alerts[code]
                if code in self.stock_groups:
                    del self.stock_groups[code]
            self._save_alerts()
        else:
            # 仅移除股票的分组标记
            for code in stocks_in_group:
                if code in self.stock_groups:
                    del self.stock_groups[code]
        
        # 从分组列表中移除
        self.group_list.remove(group)
        self._save_stocks()
        
        return {"status": "success", "message": f"已删除分组 {group}", "deleted_stocks": stocks_in_group if delete_stocks else []}
    
    def fetch_index_data(self):
        """获取大盘指数数据"""
        try:
            codes_str = ",".join(self.index_codes)
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
                
                self.index_data[code_part] = {
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
        
        # 同时获取市场涨跌统计
        self.fetch_market_stats()
    
    def fetch_market_stats(self):
        """获取市场涨跌家数统计"""
        try:
            # 使用东方财富涨跌分布接口
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            
            # 获取A股涨跌统计
            url = "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=1&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f3"
            resp = requests.get(url, headers=headers, timeout=5, proxies={"http": None, "https": None})
            data = resp.json()
            
            total = data.get("data", {}).get("total", 0)
            
            # 获取上涨股票数量
            url_up = "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=1&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f3&fid=f3&filter=(f3>0)"
            resp_up = requests.get(url_up, headers=headers, timeout=5, proxies={"http": None, "https": None})
            rise_count = resp_up.json().get("data", {}).get("total", 0)
            
            # 获取下跌股票数量
            url_down = "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=1&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f3&fid=f3&filter=(f3<0)"
            resp_down = requests.get(url_down, headers=headers, timeout=5, proxies={"http": None, "https": None})
            fall_count = resp_down.json().get("data", {}).get("total", 0)
            
            # 获取涨停数量
            url_limit_up = "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=1&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f3&fid=f3&filter=(f3>=9.9)"
            resp_limit_up = requests.get(url_limit_up, headers=headers, timeout=5, proxies={"http": None, "https": None})
            limit_up = resp_limit_up.json().get("data", {}).get("total", 0)
            
            # 获取跌停数量
            url_limit_down = "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=1&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f3&fid=f3&filter=(f3<=-9.9)"
            resp_limit_down = requests.get(url_limit_down, headers=headers, timeout=5, proxies={"http": None, "https": None})
            limit_down = resp_limit_down.json().get("data", {}).get("total", 0)
            
            flat_count = total - rise_count - fall_count
            if flat_count < 0:
                flat_count = 0
            
            self.market_stats = {
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
            self._fetch_market_stats_backup()
    
    def _fetch_market_stats_backup(self):
        """备用方案：使用新浪接口获取涨跌统计"""
        try:
            headers = {"Referer": "https://finance.sina.com.cn/", "User-Agent": "Mozilla/5.0"}
            # 新浪市场统计接口
            url = "https://hq.sinajs.cn/list=sh000001"
            resp = requests.get(url, headers=headers, timeout=5, proxies={"http": None, "https": None})
            # 暂时设置默认值
            self.market_stats = {
                "rise_count": 0,
                "fall_count": 0,
                "flat_count": 0,
                "limit_up": 0,
                "limit_down": 0,
                "update_time": datetime.now().strftime("%H:%M:%S")
            }
        except:
            pass
    
    def get_market_stats(self) -> dict:
        """获取市场涨跌统计"""
        return {"status": "success", "stats": self.market_stats}
    
    def get_market_stats_history(self, days: int = 30) -> dict:
        """获取涨跌家数历史数据"""
        try:
            # 使用东方财富历史数据接口
            url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.000001&fields1=f1,f2,f3,f4,f5&fields2=f51,f52,f53,f54,f55,f56,f57&klt=101&fqt=0&end=20500101&lmt={days}"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10, proxies={"http": None, "https": None})
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
    
    def get_index_detail(self, code: str) -> dict:
        """获取大盘指数详情（分时、K线、涨跌统计历史）"""
        code = code if code.startswith("sh") or code.startswith("sz") else f"sh{code}"
        basic = self.index_data.get(code, {})
        minute = self.get_index_minute_data(code)
        kline = self.get_index_kline_data(code, days=60)
        stats_history = self.get_market_stats_history(30)
        
        return {
            "status": "success",
            "basic": basic,
            "minute": minute.get("data", []),
            "kline": kline.get("data", []),
            "stats_history": stats_history.get("data", []),
            "current_stats": self.market_stats
        }
    
    def get_index_minute_data(self, code: str) -> dict:
        """获取指数分时数据"""
        try:
            # 转换代码格式
            if code.startswith("sh"):
                secid = f"1.{code[2:]}"
            else:
                secid = f"0.{code[2:]}"
            
            url = f"https://push2.eastmoney.com/api/qt/stock/trends2/get?secid={secid}&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11&fields2=f51,f52,f53,f54,f55,f56,f57,f58&iscr=0&ndays=2"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10, proxies={"http": None, "https": None})
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
        """获取指数K线数据"""
        try:
            if code.startswith("sh"):
                secid = f"1.{code[2:]}"
            else:
                secid = f"0.{code[2:]}"
            
            url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&fields1=f1,f2,f3,f4,f5&fields2=f51,f52,f53,f54,f55,f56,f57&klt=101&fqt=0&end=20500101&lmt={days}"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10, proxies={"http": None, "https": None})
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
            # 获取大盘指数
            self.fetch_index_data()
            # 获取股票数据
            if self.stocks:
                self.fetch_data()
            time.sleep(self.settings.get("refresh_interval", 5))
    
    def stop(self):
        self.running = False
        print("监控已停止")

    # ========== 数据导入导出 ==========
    def export_data(self) -> dict:
        """导出所有配置数据"""
        stocks_data = {}
        settings_data = {}
        alerts_data = {}
        
        if STOCKS_FILE.exists():
            try:
                with open(STOCKS_FILE, 'r', encoding='utf-8') as f:
                    stocks_data = json.load(f)
            except:
                pass
        
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
            except:
                pass
        
        if ALERTS_FILE.exists():
            try:
                with open(ALERTS_FILE, 'r', encoding='utf-8') as f:
                    alerts_data = json.load(f)
            except:
                pass
        
        return {
            "status": "success",
            "data": {
                "stocks": stocks_data,
                "settings": settings_data,
                "alerts": alerts_data,
                "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0.1"
            }
        }
    
    def import_data(self, stocks: Optional[Dict], settings: Optional[Dict], alerts: Optional[Dict]) -> dict:
        """导入配置数据"""
        imported = []
        
        try:
            self._ensure_data_dir()
            
            if stocks:
                with open(STOCKS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(stocks, f, ensure_ascii=False, indent=2)
                self.stocks = stocks.get('stocks', [])
                self.focused_stock = stocks.get('focused_stock')
                self.stock_groups = stocks.get('groups', {})
                self.group_list = stocks.get('group_list', [])
                imported.append('股票列表')
            
            if settings:
                with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                self.settings.update(settings)
                imported.append('设置')
            
            if alerts:
                with open(ALERTS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(alerts, f, ensure_ascii=False, indent=2)
                self.alerts = alerts
                imported.append('预警配置')
            
            return {
                "status": "success",
                "message": f"已导入: {', '.join(imported)}" if imported else "无数据导入"
            }
        except Exception as e:
            return {"status": "error", "message": f"导入失败: {str(e)}"}
    
    # ========== 数据路径管理 ==========
    def get_data_path(self) -> dict:
        """获取当前数据存储路径"""
        return {
            "status": "success",
            "current_path": str(CONFIG_DIR),
            "default_path": str(get_default_data_dir()),
            "is_custom": load_custom_data_path() is not None and load_custom_data_path() != ""
        }
    
    def set_data_path(self, new_path: str) -> dict:
        """设置自定义数据存储路径"""
        global CONFIG_DIR, STOCKS_FILE, SETTINGS_FILE, ALERTS_FILE
        
        if not new_path:
            # 清除自定义路径，恢复默认
            save_custom_data_path("")
            CONFIG_DIR = get_default_data_dir()
            STOCKS_FILE = CONFIG_DIR / "stocks.json"
            SETTINGS_FILE = CONFIG_DIR / "settings.json"
            ALERTS_FILE = CONFIG_DIR / "alerts.json"
            self._load_data()
            return {
                "status": "success",
                "message": "已恢复默认数据路径",
                "path": str(CONFIG_DIR)
            }
        
        try:
            new_dir = Path(new_path)
            new_dir.mkdir(parents=True, exist_ok=True)
            
            save_custom_data_path(new_path)
            
            CONFIG_DIR = new_dir
            STOCKS_FILE = CONFIG_DIR / "stocks.json"
            SETTINGS_FILE = CONFIG_DIR / "settings.json"
            ALERTS_FILE = CONFIG_DIR / "alerts.json"
            
            self._load_data()
            
            return {
                "status": "success",
                "message": f"数据路径已更新为: {new_path}",
                "path": str(CONFIG_DIR)
            }
        except Exception as e:
            return {"status": "error", "message": f"设置路径失败: {str(e)}"}
