"""
股票列表管理器

本文件负责股票列表的管理：
1. 股票的添加、删除、排序
2. 股票分组管理
3. 重点关注设置
4. 数据持久化（stocks.json）
"""

import json
from typing import List, Dict, Optional
from pathlib import Path


class StockManager:
    """
    股票列表管理器
    
    管理用户的股票列表、分组和关注设置
    """
    
    def __init__(self, stocks_file: Path):
        """
        初始化股票管理器
        
        Args:
            stocks_file: 股票数据文件路径
        """
        self.stocks_file = stocks_file
        self.stocks: List[str] = []
        self.focused_stock: Optional[str] = None
        self.stock_groups: Dict[str, str] = {}  # {code: group_name}
        self.group_list: List[str] = []
        self._load_data()
    
    def _load_data(self):
        """从文件加载数据"""
        if self.stocks_file.exists():
            try:
                with open(self.stocks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.stocks = data.get('stocks', [])
                    self.focused_stock = data.get('focused_stock')
                    self.stock_groups = data.get('groups', {})
                    self.group_list = data.get('group_list', [])
                    print(f"已加载 {len(self.stocks)} 只股票, {len(self.group_list)} 个分组")
            except Exception as e:
                print(f"加载股票列表失败: {e}")
    
    def _save_data(self):
        """保存数据到文件"""
        self.stocks_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.stocks_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'stocks': self.stocks,
                    'focused_stock': self.focused_stock,
                    'groups': self.stock_groups,
                    'group_list': self.group_list
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存股票列表失败: {e}")
    
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
    
    # ========== 股票管理 ==========
    
    def add_stock(self, code: str) -> Dict:
        """
        添加股票
        
        Args:
            code: 股票代码
            
        Returns:
            {"status": "success/error", "message": "..."}
        """
        normalized = self.normalize_code(code.lower())
        
        # 检查是否已存在
        for existing in self.stocks:
            if self.normalize_code(existing.lower()) == normalized:
                return {"status": "error", "message": "股票已存在"}
        
        self.stocks.append(normalized)
        self._save_data()
        return {"status": "success", "message": f"已添加 {normalized}"}
    
    def remove_stock(self, code: str) -> Dict:
        """
        删除股票
        
        Args:
            code: 股票代码
            
        Returns:
            {"status": "success/error", "message": "..."}
        """
        removed = False
        
        if code in self.stocks:
            self.stocks.remove(code)
            removed = True
        else:
            # 尝试模糊匹配
            for s in self.stocks[:]:
                if s.endswith(code) or code.endswith(s):
                    self.stocks.remove(s)
                    removed = True
                    break
        
        # 清理分组
        if code in self.stock_groups:
            del self.stock_groups[code]
        
        if removed:
            self._save_data()
            return {"status": "success", "message": f"已删除 {code}"}
        return {"status": "error", "message": "股票不存在"}
    
    def reorder_stocks(self, new_order: List[str]) -> Dict:
        """
        重新排序股票列表
        
        Args:
            new_order: 新的股票顺序
            
        Returns:
            {"status": "success", "message": "..."}
        """
        self.stocks = new_order
        self._save_data()
        return {"status": "success", "message": "排序已更新"}
    
    def set_focused_stock(self, code: str) -> Dict:
        """
        设置重点关注的股票
        
        Args:
            code: 股票代码
            
        Returns:
            {"status": "success", "message": "..."}
        """
        self.focused_stock = code
        self._save_data()
        return {"status": "success", "message": f"已设置 {code} 为重点关注"}
    
    # ========== 分组管理 ==========
    
    def set_stock_group(self, code: str, group: str) -> Dict:
        """
        设置股票分组
        
        Args:
            code: 股票代码
            group: 分组名称（空字符串表示移除分组）
            
        Returns:
            {"status": "success", "message": "..."}
        """
        if group:
            self.stock_groups[code] = group
            if group not in self.group_list:
                self.group_list.append(group)
        elif code in self.stock_groups:
            del self.stock_groups[code]
        
        self._save_data()
        return {"status": "success", "message": f"已设置 {code} 分组为 {group}"}
    
    def add_group(self, group: str) -> Dict:
        """
        添加新分组
        
        Args:
            group: 分组名称
            
        Returns:
            {"status": "success/error", "message": "..."}
        """
        if group and group not in self.group_list:
            self.group_list.append(group)
            self._save_data()
            return {"status": "success", "message": f"已添加分组 {group}"}
        return {"status": "error", "message": "分组已存在或名称为空"}
    
    def get_groups(self) -> Dict:
        """
        获取所有分组
        
        Returns:
            {"status": "success", "groups": [...]}
        """
        return {"status": "success", "groups": self.group_list}
    
    def delete_group(self, group: str, delete_stocks: bool = False) -> Dict:
        """
        删除分组
        
        Args:
            group: 分组名称
            delete_stocks: 是否同时删除分组内的股票
            
        Returns:
            {"status": "success/error", "message": "...", "deleted_stocks": [...]}
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
                if code in self.stock_groups:
                    del self.stock_groups[code]
        else:
            # 仅移除股票的分组标记
            for code in stocks_in_group:
                if code in self.stock_groups:
                    del self.stock_groups[code]
        
        self.group_list.remove(group)
        self._save_data()
        
        return {
            "status": "success",
            "message": f"已删除分组 {group}",
            "deleted_stocks": stocks_in_group if delete_stocks else []
        }
    
    # ========== 数据获取 ==========
    
    def get_stocks_data(self, stock_data: Dict, alerts: Dict) -> Dict:
        """
        获取股票列表数据（供 API 返回）
        
        Args:
            stock_data: 实时股票数据
            alerts: 预警配置
            
        Returns:
            完整的股票列表数据
        """
        focused = self.focused_stock
        if not focused and self.stocks:
            focused = self.stocks[0]
        
        focused_data = None
        if focused and focused in stock_data:
            focused_data = stock_data[focused]
        
        return {
            "stocks": self.stocks,
            "data": stock_data,
            "alerts": alerts,
            "focused_stock": focused,
            "focused_data": focused_data,
            "groups": self.stock_groups,
            "group_list": self.group_list
        }
