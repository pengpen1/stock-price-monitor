"""
笔记管理 API

提供笔记的增删改查、重命名、AI 转换等端点
"""

import re
import json
from fastapi import APIRouter

from schemas.notes import NoteRequest, NoteUpdateRequest, NoteRenameRequest, NoteConvertRequest
from services.ai_service import AIService

router = APIRouter(prefix="/notes", tags=["笔记管理"])

# 依赖注入
notes_manager = None


def set_notes_manager(n):
    """注入 notes_manager 实例"""
    global notes_manager
    notes_manager = n


@router.get("")
def list_notes():
    """获取笔记列表"""
    return notes_manager.list_notes()


@router.get("/{filename}")
def get_note(filename: str):
    """获取笔记内容"""
    return notes_manager.get_note(filename)


@router.post("")
def create_note(req: NoteRequest):
    """创建笔记"""
    return notes_manager.create_note(req.filename, req.content)


@router.put("/{filename}")
def update_note(filename: str, req: NoteUpdateRequest):
    """更新笔记"""
    return notes_manager.update_note(filename, req.content)


@router.delete("/{filename}")
def delete_note(filename: str):
    """删除笔记"""
    return notes_manager.delete_note(filename)


@router.put("/{filename}/rename")
def rename_note(filename: str, req: NoteRenameRequest):
    """重命名笔记"""
    return notes_manager.rename_note(filename, req.new_name)


@router.post("/convert")
def convert_note_to_trades(req: NoteConvertRequest):
    """AI 分析笔记内容，提取交易记录"""
    prompt = f"""请分析以下交易笔记内容，提取出所有交易记录。

笔记内容：
{req.content}

请按以下 JSON 格式返回提取的交易记录：
```json
{{
  "trades": [
    {{
      "date": "2025-12-24",
      "time": "09:30",
      "stock_code": "002985",
      "stock_name": "北摩高科",
      "type": "S",
      "price": 30.11,
      "quantity": 500,
      "reason": "跌破支撑位，执行止损策略"
    }}
  ],
  "summary": "笔记摘要"
}}
```

字段说明：
- date: 交易日期 YYYY-MM-DD
- time: 交易时间 HH:MM
- stock_code: 股票代码（6位数字）
- stock_name: 股票名称
- type: 交易类型 B=买入 S=卖出 T=做T
- price: 成交价格
- quantity: 成交数量（股数）
- reason: 交易原因
"""
    
    try:
        llm_response = AIService.call_llm(
            req.provider, req.api_key, req.model, prompt, req.proxy, max_retries=2
        )
        
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', llm_response)
        if json_match:
            result = json.loads(json_match.group(1))
        else:
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                result = json.loads(json_match.group())
            else:
                return {"status": "error", "message": "无法解析 AI 返回结果"}
        
        return {
            "status": "success",
            "trades": result.get("trades", []),
            "summary": result.get("summary", "")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
