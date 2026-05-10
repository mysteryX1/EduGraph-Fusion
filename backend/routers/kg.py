from fastapi import APIRouter, HTTPException, status
from typing import Dict, List
from pydantic import BaseModel

from ..services.kg_extractor import KGExtractor


router = APIRouter(prefix="/api/kg", tags=["Knowledge Graph"])

# 全局 KG 提取器实例
kg_extractor = None


class BuildKGRequest(BaseModel):
    """构建知识图谱请求"""
    textbook_ids: List[str] = None


@router.post("/build")
async def build_knowledge_graph(request: BuildKGRequest = None) -> Dict:
    """构建知识图谱

    从已解析的教材章节中提取知识节点和关系

    Args:
        request: 包含要处理的教材 ID 列表。如果为空，处理所有已解析教材。

    Returns:
        包含节点数和边数的响应
    """
    try:
        global kg_extractor
        kg_extractor = KGExtractor(data_dir="./data")

        textbook_ids = request.textbook_ids if request and request.textbook_ids else None
        result = kg_extractor.extract_all(textbook_ids=textbook_ids)

        if result.get('success'):
            return {
                'status': 'success',
                'message': result.get('message', 'Knowledge graph built successfully'),
                'data': {
                    'nodes_count': result.get('nodes_count', 0),
                    'edges_count': result.get('edges_count', 0),
                    'textbooks_processed': len(kg_extractor._discover_textbooks())
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('message', 'Failed to build knowledge graph')
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build knowledge graph: {str(e)}"
        )


@router.get("")
async def get_knowledge_graph() -> Dict:
    """获取知识图谱

    返回已构建的知识图谱数据（节点和边）

    Returns:
        包含节点列表和边列表的响应
    """
    try:
        global kg_extractor
        if kg_extractor is None:
            kg_extractor = KGExtractor(data_dir="./data")

        kg_data = kg_extractor.get_kg_data()

        return {
            'status': 'success',
            'message': 'Knowledge graph retrieved successfully',
            'data': {
                'nodes': kg_data.get('nodes', []),
                'edges': kg_data.get('edges', []),
                'node_count': kg_data.get('node_count', 0),
                'edge_count': kg_data.get('edge_count', 0)
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve knowledge graph: {str(e)}"
        )
