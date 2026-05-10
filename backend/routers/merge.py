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

    返回所有的合并决策，兼容 decision 和 action 字段
    支持的决策类型：merge、possible_duplicate、keep、remove、delete、split

    Returns:
        包含决策列表和统计信息的响应
    """
    try:
        global node_merger
        if node_merger is None:
            node_merger = NodeMerger(data_dir="./data")

        decisions = node_merger.get_decisions()

        # 计算统计，兼容 'decision' 和 'action' 字段
        # 初始化所有可能的决策类型
        decision_stats = {
            'merge': 0,
            'possible_duplicate': 0,
            'keep': 0,
            'remove': 0,
            'delete': 0,
            'split': 0,
            'total': len(decisions)
        }

        # 统计各种决策类型
        for decision_obj in decisions:
            # 兼容 'decision' 和 'action' 字段
            decision_type = decision_obj.get('decision') or decision_obj.get('action')

            if not decision_type:
                continue

            # 确保 decision_type 在统计字典中
            if decision_type in decision_stats:
                decision_stats[decision_type] += 1
            else:
                # 如果遇到未知的决策类型，也记录下来
                if decision_type not in decision_stats:
                    decision_stats[decision_type] = 0
                decision_stats[decision_type] += 1

        return {
            'status': 'success',
            'message': 'Merge decisions retrieved successfully',
            'data': {
                'decisions': decisions,
                'statistics': decision_stats
            }
        }

    except Exception as e:
        # 返回友好错误，而不是 500
        return {
            'status': 'success',
            'message': f'Merge decisions not available: {str(e)}',
            'data': {
                'decisions': [],
                'statistics': {
                    'merge': 0,
                    'possible_duplicate': 0,
                    'keep': 0,
                    'remove': 0,
                    'delete': 0,
                    'split': 0,
                    'total': 0
                }
            }
        }
