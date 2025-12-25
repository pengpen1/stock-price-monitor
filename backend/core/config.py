"""
配置管理模块

本文件负责：
1. 数据存储目录管理（默认目录、自定义目录）
2. 配置文件路径管理（stocks.json、settings.json、alerts.json）
3. 默认设置定义

数据存储规则：
- 打包后：使用用户数据目录 %APPDATA%/stock-monitor（Windows）或 ~/.stock-monitor（Mac/Linux）
- 开发模式：使用项目目录下的 data 文件夹
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional


def get_default_data_dir() -> Path:
    """
    获取默认数据存储目录
    
    - 打包后：使用用户数据目录
    - 开发模式：使用项目目录下的 data 文件夹
    
    Returns:
        数据目录路径
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
        data_dir = Path(__file__).parent.parent / "data"
    return data_dir


def get_config_file() -> Path:
    """
    获取全局配置文件路径
    
    用于存储自定义数据路径等全局配置
    
    Returns:
        配置文件路径
    """
    if getattr(sys, 'frozen', False):
        if sys.platform == 'win32':
            base = Path(os.environ.get('APPDATA', os.path.expanduser('~')))
        else:
            base = Path.home()
        return base / 'stock-monitor' / 'config.json'
    else:
        return Path(__file__).parent.parent / "config.json"


def load_custom_data_path() -> Optional[str]:
    """
    从全局配置加载自定义数据路径
    
    Returns:
        自定义数据路径或 None
    """
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
    """
    保存自定义数据路径到全局配置
    
    Args:
        path: 自定义数据路径
    """
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
    """
    获取实际使用的数据目录
    
    优先使用自定义路径，否则使用默认路径
    
    Returns:
        数据目录路径
    """
    custom_path = load_custom_data_path()
    if custom_path and Path(custom_path).exists():
        return Path(custom_path)
    return get_default_data_dir()


# ========== 配置文件路径（初始化时设置，后续可能动态更新）==========
CONFIG_DIR = get_data_dir()
STOCKS_FILE = CONFIG_DIR / "stocks.json"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
ALERTS_FILE = CONFIG_DIR / "alerts.json"


# ========== 默认设置 ==========
DEFAULT_SETTINGS = {
    "refresh_interval": 5,          # 刷新间隔（秒）
    "pushplus_token": "",           # PushPlus 推送 Token
    "dingtalk_webhook": "",         # 钉钉 Webhook
    "alert_cooldown": 300,          # 预警冷却时间（秒）
    # AI 配置
    "ai_provider": "gemini",        # AI 提供商
    "ai_api_key": "",               # AI API Key
    "ai_model": "",                 # AI 模型
    "ai_proxy": "",                 # AI 代理
}
