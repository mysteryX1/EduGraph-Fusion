from fastapi import APIRouter, HTTPException, status
from typing import Dict
from pydantic import BaseModel

from ..services.rag import RAGEngine

router = APIRouter(prefix="/api/rag", tags=["RAG"])

# 全局 RAG 引擎实例
rag_engine = None


class QueryRequest(BaseModel):
    """查询请求"""
    question: str
    top_k: int = 5


class IndexStatusResponse(BaseModel):
    """索引状态响应"""
    indexed: bool
    chunk_count: int
    textbook_count: int


@router.post("/index")
async def index_textbooks() -> Dict:
    """建立 RAG 索引

    从 backend/data/processed/ 加载已解析教材并建立向量索引

    Returns:
        包含索引状态的响应
    """
    try:
        global rag_engine
        rag_engine = RAGEngine(data_dir="./data/processed")

        success = rag_engine.load_and_index()

        if success:
            return {
                'status': 'success',
                'message': 'RAG index built successfully',
                'data': {
                    'indexed': True,
                    'chunk_count': len(rag_engine.chunks),
                    'textbook_count': len(set(
                        chunk['metadata'].get('textbook_id', '')
                        for chunk in rag_engine.chunks
                    ))
                }
            }
        else:
            return {
                'status': 'success',
                'message': 'No textbooks to index',
                'data': {
                    'indexed': False,
                    'chunk_count': 0,
                    'textbook_count': 0
                }
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to build RAG index: {str(e)}"
        )


@router.post("/query")
async def query_knowledge_base(request: QueryRequest) -> Dict:
    """查询知识库

    Args:
        request: 包含 question 和可选的 top_k

    Returns:
        包含答案、引用和源 chunks 的响应
    """
    try:
        global rag_engine
        if rag_engine is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="RAG index not built. Call /api/rag/index first"
            )

        result = rag_engine.query(request.question, top_k=request.top_k)

        return {
            'status': 'success' if result.get('success') else 'error',
            'message': result.get('message', ''),
            'data': {
                'question': request.question,
                'answer': result.get('answer', ''),
                'citations': result.get('citations', []),
                'source_chunks': result.get('source_chunks', [])
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}"
        )


@router.get("/status")
async def get_index_status() -> Dict:
    """获取 RAG 索引状态

    Returns:
        索引是否已建立及 chunk 数量
    """
    try:
        global rag_engine
        if rag_engine is None:
            return {
                'status': 'success',
                'message': 'RAG index not built',
                'data': {
                    'indexed': False,
                    'chunk_count': 0,
                    'textbook_count': 0
                }
            }

        return {
            'status': 'success',
            'message': 'RAG index status retrieved',
            'data': {
                'indexed': len(rag_engine.chunks) > 0,
                'chunk_count': len(rag_engine.chunks),
                'textbook_count': len(set(
                    chunk['metadata'].get('textbook_id', '')
                    for chunk in rag_engine.chunks
                ))
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )
