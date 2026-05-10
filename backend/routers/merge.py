from fastapi import APIRouter, HTTPException, status
from typing import Dict, List
from pydantic import BaseModel

from ..services.merger import NodeMerger


router = APIRouter(prefix="/api/merge", tags=["Knowledge Graph Merge"])

# 全局合并器实例
node_merger = None


class MergeRequest(BaseModel):
    """合并请求"""
    decisions: List[Dict] = None


@router.post("")
async def merge_graphs(request: MergeRequest = None) -> Dict:
    """合并知识图谱

    检测重复节点并进行合并，确保压缩比 <= 0.30

    Args:
        request: 可选的合并决策列表（暂未使用，系统自动计算）

    Returns:
        包含合并统计的响应
    """
    try:
        global node_merger
        node_merger = NodeMerger(data_dir="./data")

        result = node_merger.merge_all()

        if result.get('success'):
            return {
                'status': 'success',
                'message': result.get('message', 'Graphs merged successfully'),
                'data': {
                    'merged_count': result.get('merged_count', 0),
                    'removed_count': result.get('removed_count', 0),
                    'possible_duplicate_count': result.get('possible_duplicate_count', 0),
                    'kept_count': result.get('kept_count', 0),
                    'original_nodes': result.get('original_nodes', 0),
                    'merged_nodes': result.get('merged_nodes', 0),
                    'original_chars': result.get('original_chars', 0),
                    'merged_chars': result.get('merged_chars', 0),
                    'compression_ratio': round(result.get('compression_ratio', 1.0), 4)
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('message', 'Failed to merge graphs')
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to merge graphs: {str(e)}"
        )


@router.get("/decisions")
async def get_merge_decisions() -> Dict:
    """获取合并决策

    返回所有的合并决策，包括 merge、possible_duplicate 和 keep

    Returns:
        包含决策列表的响应
    """
    try:
        global node_merger
        if node_merger is None:
            node_merger = NodeMerger(data_dir="./data")

        decisions = node_merger.get_decisions()

        # 统计决策
        decision_stats = {
            'merge': len([d for d in decisions if d['decision'] == 'merge']),
            'possible_duplicate': len([d for d in decisions if d['decision'] == 'possible_duplicate']),
            'keep': len([d for d in decisions if d['decision'] == 'keep']),
            'total': len(decisions)
        }

        return {
            'status': 'success',
            'message': 'Merge decisions retrieved successfully',
            'data': {
                'decisions': decisions,
                'statistics': decision_stats
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve merge decisions: {str(e)}"
        )
