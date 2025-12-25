"""
交易记录数据存储

封装交易记录和 AI 分析记录的存储操作
当前使用 JSON 文件存储，后续可替换为数据库
"""

# 注意：当前实现复用 records.py 中的 RecordsManager
# 后续可将其重构为纯数据访问层

from domain.records_manager import RecordsManager

# 导出别名，保持接口一致
RecordsRepository = RecordsManager
