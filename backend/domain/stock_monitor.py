"""
股票监控核心模块

本文件是股票监控系统的核心，整合各个管理器：
1. StockManager - 股票列表管理
2. AlertManager - 预警管理
3. StockDataFetcher - 股票数据获取
4. IndexDataFetcher - 指数数据获取

主要功能：
- 启动/停止监控循环
- 定时获取实时数据
- 触发预警检测
- 数据导入导出
"""

import os
import time
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from core.config import (
    get_data_dir,
    get_default_data_dir,
    load_custom_data_path,
    save_custom_data_path,
    DEFAULT_SETTINGS,
)
from core.stock_data import StockDataFetcher
from core.index_data import IndexDataFetcher
from .stock_manager import StockManager
from .alert_manager import AlertManager


class StockMonitor:
    """
    股票监控器
    
    整合股票管理、预警管理、数据获取等功能
    提供统一的对外接口
    """
    
    def __init__(self):
        """初始化股票监控器"""
        # 禁用代理
        self._disable_proxy()
        
        # 初始化数据目录
        self.data_dir = get_data_dir()
        self._ensure_data_dir()
        
        # 初始化设置
        self.settings: Dict = DEFAULT_SETTINGS.copy()
        self._load_settings()
        
        # 初始化各管理器
        self.stock_manager = StockManager(self.data_dir / "stocks.json")
        self.alert_manager = AlertManager(self.data_dir / "alerts.json", self.settings)
        self.stock_fetcher = StockDataFetcher()
        self.index_fetcher = IndexDataFetcher()
        
        # 运行状态
        self.running = False
        
        # 实时数据缓存
        self.data: Dict[str, dict] = {}
        self.index_data: Dict[str, dict] = {}
        self.market_stats: Dict = {}
    
    def _disable_proxy(self):
        """禁用系统代理"""
        for k in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "all_proxy", "ALL_PROXY"]:
            os.environ.pop(k, None)
        os.environ["NO_PROXY"] = "*"
        os.environ["no_proxy"] = "*"
        print("代理设置已清除")
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        print(f"数据目录: {self.data_dir}")
    
    def _load_settings(self):
        """加载设置"""
        settings_file = self.data_dir / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
                    print("已加载设置")
            except Exception as e:
                print(f"加载设置失败: {e}")
    
    def _save_settings(self):
        """保存设置"""
        settings_file = self.data_dir / "settings.json"
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    # ========== 监控控制 ==========
    
    def start(self):
        """启动监控"""
        self.running = True
        print("监控已启动")
        while self.running:
            # 获取大盘指数
            self.index_data = self.index_fetcher.fetch_index_data()
            self.market_stats = self.index_fetcher.fetch_market_stats()
            
            # 获取股票数据
            if self.stock_manager.stocks:
                self._fetch_stock_data()
            
            time.sleep(self.settings.get("refresh_interval", 5))
    
    def stop(self):
        """停止监控"""
        self.running = False
        print("监控已停止")
    
    def _fetch_stock_data(self):
        """获取股票实时数据"""
        new_data = self.stock_fetcher.fetch_realtime_data(self.stock_manager.stocks)
        
        # 更新数据并检查预警
        for code, stock_data in new_data.items():
            self.data[code] = stock_data
            
            # 更新股票列表中的代码格式
            if code not in self.stock_manager.stocks:
                raw_code = code[2:]
                if raw_code in self.stock_manager.stocks:
                    self.stock_manager.stocks.remove(raw_code)
                    self.stock_manager.stocks.append(code)
                    self.stock_manager._save_data()
            
            # 检查预警
            self.alert_manager.check_alerts(code, stock_data)
    
    # ========== 设置相关 ==========
    
    def get_settings(self) -> Dict:
        """获取设置"""
        return {"status": "success", "settings": self.settings}
    
    def update_settings(self, new_settings: Dict) -> Dict:
        """更新设置"""
        self.settings.update(new_settings)
        self._save_settings()
        self.alert_manager.update_settings(self.settings)
        return {"status": "success", "message": "设置已更新", "settings": self.settings}
    
    # ========== 股票管理（代理到 StockManager）==========
    
    def add_stock(self, code: str) -> Dict:
        """添加股票"""
        return self.stock_manager.add_stock(code)
    
    def remove_stock(self, code: str) -> Dict:
        """删除股票"""
        result = self.stock_manager.remove_stock(code)
        # 清理相关数据
        if code in self.data:
            del self.data[code]
        self.alert_manager.remove_alert(code)
        return result
    
    def reorder_stocks(self, new_order: List[str]) -> Dict:
        """重新排序股票"""
        return self.stock_manager.reorder_stocks(new_order)
    
    def set_focused_stock(self, code: str) -> Dict:
        """设置重点关注"""
        return self.stock_manager.set_focused_stock(code)
    
    def get_stocks(self) -> Dict:
        """获取股票列表和数据"""
        result = self.stock_manager.get_stocks_data(self.data, self.alert_manager.alerts)
        result["index_data"] = self.index_data
        return result
    
    # ========== 分组管理（代理到 StockManager）==========
    
    def set_stock_group(self, code: str, group: str) -> Dict:
        """设置股票分组"""
        return self.stock_manager.set_stock_group(code, group)
    
    def add_group(self, group: str) -> Dict:
        """添加分组"""
        return self.stock_manager.add_group(group)
    
    def get_groups(self) -> Dict:
        """获取所有分组"""
        return self.stock_manager.get_groups()
    
    def delete_group(self, group: str, delete_stocks: bool = False) -> Dict:
        """删除分组"""
        return self.stock_manager.delete_group(group, delete_stocks)
    
    # ========== 预警管理（代理到 AlertManager）==========
    
    def set_alert(self, code: str, alert_config: dict) -> Dict:
        """设置预警"""
        return self.alert_manager.set_alert(code, alert_config)
    
    def remove_alert(self, code: str) -> Dict:
        """移除预警"""
        return self.alert_manager.remove_alert(code)
    
    def get_triggered_alerts(self) -> Dict:
        """获取触发的预警"""
        return self.alert_manager.get_triggered_alerts()
    
    # ========== 股票数据（代理到 StockDataFetcher）==========
    
    def get_minute_data(self, code: str) -> Dict:
        """获取分时数据"""
        return self.stock_fetcher.get_minute_data(code)
    
    def get_history_minute_data(self, code: str, date: str) -> Dict:
        """获取历史分时数据"""
        return self.stock_fetcher.get_history_minute_data(code, date)
    
    def get_kline_data(self, code: str, period: str = "day", count: int = 120) -> Dict:
        """获取K线数据"""
        return self.stock_fetcher.get_kline_data(code, period, count)
    
    def get_money_flow(self, code: str) -> Dict:
        """获取资金流向"""
        return self.stock_fetcher.get_money_flow(code)
    
    def get_stock_extra_data(self, code: str) -> Dict:
        """获取股票额外数据"""
        return self.stock_fetcher.get_stock_extra_data(code)
    
    def get_dragon_tiger(self, code: str) -> Dict:
        """获取龙虎榜数据"""
        return self.stock_fetcher.get_dragon_tiger(code)
    
    def get_stock_detail(self, code: str) -> Dict:
        """获取股票详情"""
        code = self.stock_fetcher.normalize_code(code)
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
    
    # ========== 指数数据（代理到 IndexDataFetcher）==========
    
    def get_market_stats(self) -> Dict:
        """获取市场统计"""
        return {"status": "success", "stats": self.market_stats}
    
    def get_market_stats_history(self, days: int = 30) -> Dict:
        """获取市场统计历史"""
        return self.index_fetcher.get_market_stats_history(days)
    
    def get_index_detail(self, code: str) -> Dict:
        """获取指数详情"""
        return self.index_fetcher.get_index_detail(code, self.index_data, self.market_stats)
    
    # ========== 数据导入导出 ==========
    
    def export_data(self) -> Dict:
        """导出所有配置数据"""
        stocks_data = {}
        settings_data = {}
        alerts_data = {}
        
        stocks_file = self.data_dir / "stocks.json"
        settings_file = self.data_dir / "settings.json"
        alerts_file = self.data_dir / "alerts.json"
        
        if stocks_file.exists():
            try:
                with open(stocks_file, 'r', encoding='utf-8') as f:
                    stocks_data = json.load(f)
            except:
                pass
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
            except:
                pass
        
        if alerts_file.exists():
            try:
                with open(alerts_file, 'r', encoding='utf-8') as f:
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
                "version": "1.2.1"
            }
        }
    
    def import_data(
        self,
        stocks: Optional[Dict],
        settings: Optional[Dict],
        alerts: Optional[Dict]
    ) -> Dict:
        """导入配置数据"""
        imported = []
        
        try:
            self._ensure_data_dir()
            
            if stocks:
                stocks_file = self.data_dir / "stocks.json"
                with open(stocks_file, 'w', encoding='utf-8') as f:
                    json.dump(stocks, f, ensure_ascii=False, indent=2)
                self.stock_manager._load_data()
                imported.append('股票列表')
            
            if settings:
                settings_file = self.data_dir / "settings.json"
                with open(settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                self.settings.update(settings)
                imported.append('设置')
            
            if alerts:
                alerts_file = self.data_dir / "alerts.json"
                with open(alerts_file, 'w', encoding='utf-8') as f:
                    json.dump(alerts, f, ensure_ascii=False, indent=2)
                self.alert_manager._load_data()
                imported.append('预警配置')
            
            return {
                "status": "success",
                "message": f"已导入: {', '.join(imported)}" if imported else "无数据导入"
            }
        except Exception as e:
            return {"status": "error", "message": f"导入失败: {str(e)}"}
    
    # ========== 数据路径管理 ==========
    
    def get_data_path(self) -> Dict:
        """获取当前数据存储路径"""
        return {
            "status": "success",
            "current_path": str(self.data_dir),
            "default_path": str(get_default_data_dir()),
            "is_custom": load_custom_data_path() is not None and load_custom_data_path() != ""
        }
    
    def set_data_path(self, new_path: str) -> Dict:
        """设置自定义数据存储路径"""
        if not new_path:
            # 清除自定义路径，恢复默认
            save_custom_data_path("")
            self.data_dir = get_default_data_dir()
            self._reload_all()
            return {
                "status": "success",
                "message": "已恢复默认数据路径",
                "path": str(self.data_dir)
            }
        
        try:
            new_dir = Path(new_path)
            new_dir.mkdir(parents=True, exist_ok=True)
            
            save_custom_data_path(new_path)
            self.data_dir = new_dir
            self._reload_all()
            
            return {
                "status": "success",
                "message": f"数据路径已更新为: {new_path}",
                "path": str(self.data_dir)
            }
        except Exception as e:
            return {"status": "error", "message": f"设置路径失败: {str(e)}"}
    
    def _reload_all(self):
        """重新加载所有数据"""
        self._ensure_data_dir()
        self._load_settings()
        self.stock_manager = StockManager(self.data_dir / "stocks.json")
        self.alert_manager = AlertManager(self.data_dir / "alerts.json", self.settings)
