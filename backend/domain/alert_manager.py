"""
预警管理器

本文件负责股票预警功能：
1. 预警配置的增删改查
2. 预警触发检测
3. 推送通知（PushPlus、钉钉）
4. 预警冷却时间管理
"""

import json
import time
import requests
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class AlertManager:
    """
    预警管理器
    
    管理股票预警配置和触发逻辑
    """
    
    def __init__(self, alerts_file: Path, settings: Dict):
        """
        初始化预警管理器
        
        Args:
            alerts_file: 预警配置文件路径
            settings: 系统设置（包含推送配置）
        """
        self.alerts_file = alerts_file
        self.settings = settings
        self.alerts: Dict[str, dict] = {}
        self.alert_cooldowns: Dict[str, float] = {}  # 预警冷却时间记录
        self.triggered_alerts: List[dict] = []  # 已触发的预警
        self._load_data()
    
    def _load_data(self):
        """从文件加载预警配置"""
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    self.alerts = json.load(f)
                    print(f"已加载 {len(self.alerts)} 个预警配置")
            except Exception as e:
                print(f"加载预警配置失败: {e}")
    
    def _save_data(self):
        """保存预警配置到文件"""
        self.alerts_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump(self.alerts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存预警配置失败: {e}")
    
    def update_settings(self, settings: Dict):
        """
        更新设置引用
        
        Args:
            settings: 新的设置
        """
        self.settings = settings
    
    # ========== 预警配置管理 ==========
    
    def set_alert(self, code: str, alert_config: dict) -> Dict:
        """
        设置股票预警
        
        Args:
            code: 股票代码
            alert_config: 预警配置
                - take_profit: 止盈价
                - stop_loss: 止损价
                - change_alert: 涨跌幅预警(%)
                - enabled: 是否启用
                
        Returns:
            {"status": "success", "message": "..."}
        """
        self.alerts[code] = {
            "take_profit": alert_config.get("take_profit"),
            "stop_loss": alert_config.get("stop_loss"),
            "change_alert": alert_config.get("change_alert"),
            "enabled": alert_config.get("enabled", True),
        }
        self._save_data()
        return {"status": "success", "message": f"已设置 {code} 的预警"}
    
    def remove_alert(self, code: str) -> Dict:
        """
        移除股票预警
        
        Args:
            code: 股票代码
            
        Returns:
            {"status": "success/error", "message": "..."}
        """
        if code in self.alerts:
            del self.alerts[code]
            self._save_data()
            return {"status": "success", "message": f"已移除 {code} 的预警"}
        return {"status": "error", "message": "预警不存在"}
    
    def get_triggered_alerts(self) -> Dict:
        """
        获取触发的预警（并清空列表）
        
        Returns:
            {"status": "success", "alerts": [...]}
        """
        alerts = self.triggered_alerts.copy()
        self.triggered_alerts.clear()
        return {"status": "success", "alerts": alerts}
    
    # ========== 预警检测 ==========
    
    def check_alerts(self, code: str, stock_data: dict):
        """
        检查是否触发预警
        
        Args:
            code: 股票代码
            stock_data: 股票实时数据
        """
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
    
    # ========== 推送通知 ==========
    
    def _send_notification(self, alert_info: dict):
        """
        发送推送通知
        
        Args:
            alert_info: 预警信息
        """
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
