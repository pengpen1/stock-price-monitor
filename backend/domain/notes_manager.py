"""
笔记管理器

本文件负责管理用户的交易笔记：
1. 笔记的增删改查
2. 笔记重命名
3. 笔记列表获取

笔记以 Markdown 文件形式存储在 data/notes/ 目录下
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class NotesManager:
    """
    笔记管理器
    
    管理用户的交易笔记，支持 Markdown 格式
    """
    
    def __init__(self, data_dir: Path):
        """
        初始化笔记管理器
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = data_dir
        self.notes_dir = data_dir / "notes"
        self._ensure_dir()
    
    def _ensure_dir(self):
        """确保笔记目录存在"""
        self.notes_dir.mkdir(parents=True, exist_ok=True)
    
    def list_notes(self) -> Dict:
        """
        获取笔记列表
        
        Returns:
            {"status": "success", "notes": [...]}
        """
        self._ensure_dir()
        notes = []
        
        for file in self.notes_dir.glob("*.md"):
            stat = file.stat()
            notes.append({
                "filename": file.name,
                "title": file.stem,  # 不含扩展名的文件名
                "size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "updated_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
        
        # 按更新时间倒序排列
        notes.sort(key=lambda x: x["updated_at"], reverse=True)
        return {"status": "success", "notes": notes}
    
    def get_note(self, filename: str) -> Dict:
        """
        获取笔记内容
        
        Args:
            filename: 笔记文件名
            
        Returns:
            {"status": "success/error", "content": "...", "message": "..."}
        """
        # 确保文件名以 .md 结尾
        if not filename.endswith(".md"):
            filename = f"{filename}.md"
        
        file_path = self.notes_dir / filename
        
        if not file_path.exists():
            return {"status": "error", "message": "笔记不存在"}
        
        try:
            content = file_path.read_text(encoding="utf-8")
            stat = file_path.stat()
            return {
                "status": "success",
                "filename": filename,
                "title": file_path.stem,
                "content": content,
                "updated_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }
        except Exception as e:
            return {"status": "error", "message": f"读取笔记失败: {str(e)}"}
    
    def create_note(self, filename: str, content: str = "") -> Dict:
        """
        创建笔记
        
        Args:
            filename: 笔记文件名
            content: 笔记内容
            
        Returns:
            {"status": "success/error", "message": "..."}
        """
        self._ensure_dir()
        
        # 确保文件名以 .md 结尾
        if not filename.endswith(".md"):
            filename = f"{filename}.md"
        
        file_path = self.notes_dir / filename
        
        if file_path.exists():
            return {"status": "error", "message": "笔记已存在"}
        
        try:
            file_path.write_text(content, encoding="utf-8")
            return {"status": "success", "message": "笔记创建成功", "filename": filename}
        except Exception as e:
            return {"status": "error", "message": f"创建笔记失败: {str(e)}"}
    
    def update_note(self, filename: str, content: str) -> Dict:
        """
        更新笔记内容
        
        Args:
            filename: 笔记文件名
            content: 新的笔记内容
            
        Returns:
            {"status": "success/error", "message": "..."}
        """
        # 确保文件名以 .md 结尾
        if not filename.endswith(".md"):
            filename = f"{filename}.md"
        
        file_path = self.notes_dir / filename
        
        if not file_path.exists():
            return {"status": "error", "message": "笔记不存在"}
        
        try:
            file_path.write_text(content, encoding="utf-8")
            return {"status": "success", "message": "笔记更新成功"}
        except Exception as e:
            return {"status": "error", "message": f"更新笔记失败: {str(e)}"}
    
    def delete_note(self, filename: str) -> Dict:
        """
        删除笔记
        
        Args:
            filename: 笔记文件名
            
        Returns:
            {"status": "success/error", "message": "..."}
        """
        # 确保文件名以 .md 结尾
        if not filename.endswith(".md"):
            filename = f"{filename}.md"
        
        file_path = self.notes_dir / filename
        
        if not file_path.exists():
            return {"status": "error", "message": "笔记不存在"}
        
        try:
            file_path.unlink()
            return {"status": "success", "message": "笔记删除成功"}
        except Exception as e:
            return {"status": "error", "message": f"删除笔记失败: {str(e)}"}
    
    def rename_note(self, old_filename: str, new_filename: str) -> Dict:
        """
        重命名笔记
        
        Args:
            old_filename: 原文件名
            new_filename: 新文件名
            
        Returns:
            {"status": "success/error", "message": "..."}
        """
        # 确保文件名以 .md 结尾
        if not old_filename.endswith(".md"):
            old_filename = f"{old_filename}.md"
        if not new_filename.endswith(".md"):
            new_filename = f"{new_filename}.md"
        
        old_path = self.notes_dir / old_filename
        new_path = self.notes_dir / new_filename
        
        if not old_path.exists():
            return {"status": "error", "message": "原笔记不存在"}
        
        if new_path.exists():
            return {"status": "error", "message": "目标文件名已存在"}
        
        try:
            old_path.rename(new_path)
            return {"status": "success", "message": "重命名成功", "filename": new_filename}
        except Exception as e:
            return {"status": "error", "message": f"重命名失败: {str(e)}"}
