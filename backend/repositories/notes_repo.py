"""
笔记数据存储

封装笔记的存储操作
当前使用 Markdown 文件存储，后续可替换为数据库
"""

# 注意：当前实现复用 notes.py 中的 NotesManager
# 后续可将其重构为纯数据访问层

from domain.notes_manager import NotesManager

# 导出别名，保持接口一致
NotesRepository = NotesManager
