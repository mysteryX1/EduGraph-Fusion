from fastapi import APIRouter, HTTPException, status
from typing import Dict
from pydantic import BaseModel

from ..services.feedback import FeedbackProcessor

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])


class FeedbackRequest(BaseModel):
    """反馈请求"""
    instruction: str


@router.post("")
async def submit_feedback(request: FeedbackRequest) -> Dict:
    """提交教师反馈

    支持的指令：
    - "保留 XXX" - 保留指定知识节点
    - "删除 XXX" - 删除指定知识节点
    - "拆分 XXX 和 YYY" - 拆分两个知识节点
    - "合并 XXX 和 YYY" - 合并两个知识节点

    Args:
        request: 包含自然语言指令的请求

    Returns:
        处理结果和修改摘要
    """
    try:
        if not request.instruction or not request.instruction.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Instruction cannot be empty"
            )

        processor = FeedbackProcessor(data_dir="./data/processed")
        result = processor.process_instruction(request.instruction)

        if result.get('success'):
            summary = processor.get_feedback_summary()
            return {
                'status': 'success',
                'message': result.get('summary', 'Feedback processed'),
                'data': {
                    'instruction': request.instruction,
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
