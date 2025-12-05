import time
import json
from typing import List, Dict
import os
from pathlib import Path

# 配置文件路径
CONFIG_DIR = Path(__file__).parent / "data"
STOCKS_FILE = CONFIG_DIR / "stocks.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"

# 默认设置
DEFAULT_SETTINGS = {
    "refresh_interval": 5,  # 刷新间隔（秒）
    "pushplus_token": "",   # PushPlus 推送 Token
    "dingtalk_webhook": "", # 钉钉机器人 Webhook
    "alert_cooldown": 300,  # 预警冷却时间（秒）
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
        
        # 加载本地缓存
        self._load_data()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_data(self):
        """从本地文件加载数据"""
        self._ensure_data_dir()
        
        # 加载股票列表
        if STOCKS_FILE.exists():
            try:
                with open(STOCKS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.stocks = data.get('stocks', [])
                    print(f"已加载 {len(self.stocks)} 只股票")
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
    
    def _save_stocks(self):
        """保存股票列表到本地"""
        self._ensure_data_dir()
        try:
            with open(STOCKS_FILE, 'w', encoding='utf-8') as f:
                json.dump({'stocks': self.stocks}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存股票列表失败: {e}")
    
    def _save_settings(self):
        """保存设置到本地"""
        self._ensure_data_dir()
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def get_settings(self):
        """获取当前设置"""
        return {"status": "success", "settings": self.settings}
    
    def update_settings(self, new_settings: Dict):
        """更新设置"""
        self.settings.update(new_settings)
        self._save_settings()
        return {"status": "success", "message": "设置已更新", "settings": self.settings}

    def add_stock(self, code: str):
        if code not in self.stocks:
            self.stocks.append(code)
            self._save_stocks()  # 保存到本地
            return {"status": "success", "message": f"已添加 {code}"}
        return {"status": "error", "message": "股票已存在"}

    def remove_stock(self, code: str):
        if code in self.stocks:
            self.stocks.remove(code)
            if code in self.data:
                del self.data[code]
            self._save_stocks()  # 保存到本地
            return {"status": "success", "message": f"已删除 {code}"}
        return {"status": "error", "message": "股票不存在"}

    def get_stocks(self):
        return {"stocks": self.stocks, "data": self.data}

    def fetch_data(self):
        if not self.stocks:
            return
        
        # print(f"Fetching data for: {self.stocks}")
        try:
            # Use Sina API
            # Format: http://hq.sinajs.cn/list=sh600519,sz000001
            # We need to ensure codes have prefixes (sh/sz). 
            # Frontend sends "sh600519" or "600519". If no prefix, we might need to guess or require it.
            # For now, let's assume user provides prefix or we try to add it.
            # Actually, user input "600021" (sh) or "000001" (sz).
            # Simple heuristic: 6xx -> sh, 0xx/3xx -> sz. 4xx/8xx -> bj (Sina might be different for bj)
            
            query_list = []
            for code in self.stocks:
                if code.startswith("sh") or code.startswith("sz") or code.startswith("bj"):
                    query_list.append(code)
                else:
                    # Guess prefix
                    if code.startswith("6"):
                        query_list.append(f"sh{code}")
                    elif code.startswith("0") or code.startswith("3"):
                        query_list.append(f"sz{code}")
                    elif code.startswith("4") or code.startswith("8"):
                        query_list.append(f"bj{code}")
                    else:
                        query_list.append(code) # Try as is

            codes_str = ",".join(query_list)
            url = f"http://hq.sinajs.cn/list={codes_str}"
            headers = {
                "Referer": "https://finance.sina.com.cn/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            # Use explicit empty proxies to bypass system proxy settings
            import requests
            resp = requests.get(url, headers=headers, timeout=5, proxies={"http": None, "https": None})
            
            # Encoding is usually GBK
            content = resp.content.decode('gbk')
            
            # Parse response
            # var hq_str_sh600519="贵州茅台,1435.810,1436.030,1428.290,1435.970,1428.000,1428.280,1428.310,..."
            lines = content.strip().split('\n')
            for line in lines:
                if not line: continue
                # line: var hq_str_sh600519="Name,..."
                parts = line.split('=')
                if len(parts) < 2: continue
                
                # Extract code from var name
                # var hq_str_sh600519 -> sh600519
                code_part = parts[0].split('_')[-1]
                
                data_part = parts[1].strip('"')
                if not data_part: continue
                
                fields = data_part.split(',')
                if len(fields) < 30: continue
                
                # Sina Fields:
                # 0: Name
                # 1: Open
                # 2: PreClose
                # 3: Price
                # 4: High
                # 5: Low
                # 30: Date
                # 31: Time
                
                name = fields[0]
                pre_close = float(fields[2])
                price = float(fields[3])
                high = fields[4]
                low = fields[5]
                time_str = fields[31]
                
                # Calculate change percent
                change_percent = 0.0
                if pre_close > 0:
                    change_percent = (price - pre_close) / pre_close * 100
                
                # Map back to original code if possible, or use the one from Sina
                # We stored "600021" in self.stocks, but query was "sh600021"
                # We need to update self.data with the key that matches self.stocks or just use the full code
                # Let's use the code from Sina (with prefix) as the key in data, 
                # but we need to ensure frontend knows how to display it.
                # Or we strip prefix if the original didn't have it.
                
                # Better: Update data with the code used in query (with prefix) 
                # AND ensure add_stock supports adding with/without prefix.
                
                stock_data = {
                    "code": code_part,
                    "name": name,
                    "price": f"{price:.2f}",
                    "change_percent": f"{change_percent:.2f}",
                    "high": high,
                    "low": low,
                    "open": fields[1],
                    "volume": fields[8],
                    "amount": fields[9],
                    "time": time_str
                }
                
                # Store data. 
                # We update self.stocks to use the canonical code (with prefix) so delete works reliably.
                if code_part not in self.stocks:
                    # Check if we have the raw version
                    raw_code = code_part[2:]
                    if raw_code in self.stocks:
                        self.stocks.remove(raw_code)
                        self.stocks.append(code_part)
                
                self.data[code_part] = stock_data
                
        except Exception as e:
            print(f"Error fetching data: {e}")

    def remove_stock_flexible(self, code: str):
        """灵活删除股票（支持带前缀和不带前缀）"""
        removed = False
        if code in self.stocks:
            self.stocks.remove(code)
            removed = True
        else:
            # 尝试匹配带/不带前缀的情况
            for s in self.stocks[:]:
                if s.endswith(code) or code.endswith(s):
                    self.stocks.remove(s)
                    removed = True
                    break
        
        if code in self.data:
            del self.data[code]
        
        # 清理相关的数据
        keys_to_remove = [k for k in self.data.keys() if k.endswith(code) or code.endswith(k)]
        for k in keys_to_remove:
            del self.data[k]
        
        if removed:
            self._save_stocks()  # 保存到本地



    def start(self):
        self.running = True
        print("Monitor started")
        while self.running:
            if self.stocks:
                self.fetch_data()
            time.sleep(5)

