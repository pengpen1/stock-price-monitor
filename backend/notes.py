"""
笔记管理模块
- 支持 Markdown 格式
- 本地文件存储
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class NotesManager:
    """笔记管理器"""
    
    def __init__(self, data_dir: Path):
        self.notes_dir = data_dir / "notes"
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        print(f"笔记目录: {self.notes_dir}")
    
    def _get_note_path(self, filename: str) -> Path:
        """获取笔记文件路径"""
        # 确保文件名以 .md 结尾
        if not filename.endswith(".md"):
            filename = f"{filename}.md"
        return self.notes_dir / filename
    
    def _get_note_meta(self, filepath: Path) -> Dict:
        """获取笔记元信息"""
        try:
            stat = filepath.stat()
            content = filepath.read_text(encoding="utf-8")
            # 提取前20个字作为预览（去除标题符号等）
            preview = content.replace("#", "").replace("*", "").replace("-", "").strip()
            preview = preview[:50].split("\n")[0]  # 取第一行的前50字
            
            return {
                "filename": filepath.stem,  # 不含扩展名
                "created_at": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M"),
                "updated_at": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                "preview": preview[:30] if preview else "空笔记",
                "size": stat.st_size
            }
        except Exception as e:
            print(f"获取笔记元信息失败: {e}")
            return None
    
    def list_notes(self) -> Dict:
        """获取所有笔记列表"""
        try:
            notes = []
            for filepath in self.notes_dir.glob("*.md"):
                meta = self._get_note_meta(filepath)
                if meta:
                    notes.append(meta)
            
            # 按更新时间倒序排列
            notes.sort(key=lambda x: x["updated_at"], reverse=True)
            
            return {"status": "success", "notes": notes, "total": len(notes)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_note(self, filename: str) -> Dict:
        """获取笔记内容"""
        try:
            filepath = self._get_note_path(filename)
            if not filepath.exists():
                return {"status": "error", "message": "笔记不存在"}
            
            content = filepath.read_text(encoding="utf-8")
            meta = self._get_note_meta(filepath)
            
            return {
                "status": "success",
                "filename": filename,
                "content": content,
                "meta": meta
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def create_note(self, filename: str, content: str = "") -> Dict:
        """创建新笔记"""
        try:
            # 清理文件名
            filename = filename.strip().replace("/", "_").replace("\\", "_")
            if not filename:
                return {"status": "error", "message": "文件名不能为空"}
            
            filepath = self._get_note_path(filename)
            if filepath.exists():
                return {"status": "error", "message": "笔记已存在"}
            
            # 创建文件
            filepath.write_text(content, encoding="utf-8")
            
            return {
                "status": "success",
                "message": f"已创建笔记: {filename}",
                "filename": filename
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def update_note(self, filename: str, content: str) -> Dict:
        """更新笔记内容"""
        try:
            filepath = self._get_note_path(filename)
            if not filepath.exists():
                return {"status": "error", "message": "笔记不存在"}
            
            filepath.write_text(content, encoding="utf-8")
            
            return {
                "status": "success",
                "message": "笔记已保存",
                "filename": filename
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def delete_note(self, filename: str) -> Dict:
        """删除笔记"""
        try:
            filepath = self._get_note_path(filename)
            if not filepath.exists():
                return {"status": "error", "message": "笔记不存在"}
            
            filepath.unlink()
            
            return {
                "status": "success",
                "message": f"已删除笔记: {filename}",
                "filename": filename
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def rename_note(self, old_name: str, new_name: str) -> Dict:
        """重命名笔记"""
        try:
            old_path = self._get_note_path(old_name)
            if not old_path.exists():
                return {"status": "error", "message": "笔记不存在"}
            
            new_name = new_name.strip().replace("/", "_").replace("\\", "_")
            if not new_name:
                return {"status": "error", "message": "新文件名不能为空"}
            
            new_path = self._get_note_path(new_name)
            if new_path.exists():
                return {"status": "error", "message": "目标文件名已存在"}
            
            old_path.rename(new_path)
            
            return {
                "status": "success",
                "message": f"已重命名: {old_name} -> {new_name}",
                "filename": new_name
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
