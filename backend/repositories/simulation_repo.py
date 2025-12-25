"""
模拟会话数据存储

封装模拟会话的存储操作
当前使用 JSON 文件存储，后续可替换为数据库
"""

# 注意：当前实现复用 simulation.py 中的 SimulationManager
# 后续可将其重构为纯数据访问层

from domain.simulation_manager import SimulationManager

# 导出别名，保持接口一致
SimulationRepository = SimulationManager
