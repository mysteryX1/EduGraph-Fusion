# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, status
from typing import Dict
from pydantic import BaseModel

from ..services.feedback import FeedbackProcessor

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])


from typing import Optional

class FeedbackRequest(BaseModel):
    """反馈请求（兼容多种字段名）"""
    instruction: Optional[str] = None
    feedback: Optional[str] = None
    text: Optional[str] = None
    content: Optional[str] = None


@router.post("")
async def submit_feedback(request: FeedbackRequest) -> Dict:
    """提交教师反馈

    支持的指令：
    - "保留 XXX" - 保留指定知识节点
    - "删除 XXX" - 删除指定知识节点
    - "拆分 XXX 和 YYY" - 拆分两个知识节点
    - "合并 XXX 和 YYY" - 合并两个知识节点

    兼容的请求体字段:
    - instruction: 标准字段
    - feedback: 备选字段
    - text: 备选字段
    - content: 备选字段

    Args:
        request: 包含自然语言指令的请求

    Returns:
        处理结果和修改摘要
    """
    try:
        # 兼容多种字段名
        instruction = (request.instruction or request.feedback or
                      request.text or request.content or "").strip()

        if not instruction:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Instruction/feedback/text/content cannot be empty. Please provide a valid instruction like '保留 函数' or '删除 内容'"
            )

        processor = FeedbackProcessor(data_dir="./data/processed")
        result = processor.process_instruction(instruction)

        if result.get('success'):
            summary = processor.get_feedback_summary()
            return {
                'status': 'success',
                'message': result.get('summary', 'Feedback processed'),
                'data': {
                    'instruction': instruction,
                    'action': result.get('action'),
                    'summary': result.get('summary'),
                    'knowledge_graph_summary': summary
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('message', 'Failed to process instruction')
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process feedback: {str(e)}"
        )


@router.get("/summary")
async def get_feedback_summary() -> Dict:
    """获取反馈摘要

    Returns:
        包含反馈统计和知识图谱状态的摘要
    """
    try:
        processor = FeedbackProcessor(data_dir="./data/processed")
        summary = processor.get_feedback_summary()

        return {
            'status': 'success',
            'message': 'Feedback summary retrieved',
            'data': summary
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary: {str(e)}"
        )
