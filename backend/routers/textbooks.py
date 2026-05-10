from fastapi import APIRouter, HTTPException, status, Query
from typing import Dict, List
from ..services import FileStorage, ParserFactory, StatsReporter
from ..models.schemas import Textbook, TextbookMetadata, Stats


router = APIRouter(prefix="/api", tags=["textbooks"])

# 全局实例
storage = FileStorage()
stats_reporter = StatsReporter(storage)


@router.post("/parse/{textbook_id}")
async def parse_textbook(textbook_id: str, chunk_size: int = Query(1000)) -> Dict:
    """解析教材文件

    Args:
        textbook_id: 教材 ID
        chunk_size: 无法识别章节时的固定字数（默认 1000）

    Returns:
        解析结果
    """
    try:
        # 加载元数据
        metadata = storage.load_metadata(textbook_id)
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Textbook {textbook_id} not found"
            )

        file_path = metadata.get('file_path')
        file_type = metadata.get('file_type')

        if not file_path or not file_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid textbook metadata"
            )

        # 获取解析器
        try:
            parser = ParserFactory.get_parser(file_type, chunk_size=chunk_size)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        # 解析文件
        parse_result = parser.parse(file_path, textbook_id)

        if parse_result.status == "failed":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=parse_result.message
            )

        # 保存解析结果
        metadata['total_pages'] = len(parse_result.chapters)  # 对于非 PDF，用章节数代替
        if file_type == 'pdf':
            # PDF 已在解析器中设置正确的 total_pages
            pass

        storage.save_parse_result(textbook_id, parse_result.chapters, metadata)

        # 构建响应
        chapters_data = [
            {
                'id': ch.id,
                'chapter_num': ch.chapter_num,
                'title': ch.title,
                'start_page': ch.start_page,
                'end_page': ch.end_page,
                'word_count': ch.word_count,
            }
            for ch in parse_result.chapters
        ]

        return {
            'status': parse_result.status,
            'message': parse_result.message,
            'data': {
                'textbook_id': textbook_id,
                'chapter_count': len(parse_result.chapters),
                'total_words': sum(ch.word_count for ch in parse_result.chapters),
                'chapters': chapters_data,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Parsing failed: {str(e)}"
        )


@router.get("/textbooks")
async def list_textbooks(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> Dict:
    """获取教材列表

    Args:
        limit: 返回数量限制
        offset: 偏移量

    Returns:
        教材列表
    """
    try:
        all_textbooks = storage.list_all_textbooks()

        # 分页
        total = len(all_textbooks)
        textbooks = all_textbooks[offset:offset + limit]

        textbooks_data = [
            {
                'id': tb.id,
                'filename': tb.filename,
                'title': tb.title,
                'file_type': tb.file_type,
                'upload_time': tb.upload_time.isoformat(),
                'chapter_count': tb.chapter_count,
                'total_words': tb.total_words,
                'total_pages': tb.total_pages,
            }
            for tb in textbooks
        ]

        return {
            'status': 'success',
            'data': {
                'total': total,
                'limit': limit,
                'offset': offset,
                'textbooks': textbooks_data,
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list textbooks: {str(e)}"
        )


@router.get("/textbooks/{textbook_id}")
async def get_textbook(textbook_id: str) -> Dict:
    """获取单个教材的详细信息

    Args:
        textbook_id: 教材 ID

    Returns:
        教材详细信息
    """
    try:
        textbook = storage.load_textbook(textbook_id)
        if not textbook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Textbook {textbook_id} not found"
            )

        chapters_data = [
            {
                'id': ch.id,
                'chapter_num': ch.chapter_num,
                'title': ch.title,
                'start_page': ch.start_page,
                'end_page': ch.end_page,
                'word_count': ch.word_count,
            }
            for ch in textbook.chapters
        ]

        return {
            'status': 'success',
            'data': {
                'id': textbook.id,
                'filename': textbook.filename,
                'title': textbook.title,
                'file_type': textbook.file_type,
                'upload_time': textbook.upload_time.isoformat(),
                'file_path': textbook.file_path,
                'total_pages': textbook.total_pages,
                'total_words': textbook.total_words,
                'chapter_count': len(textbook.chapters),
                'chapters': chapters_data,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get textbook: {str(e)}"
        )


@router.get("/stats")
async def get_stats() -> Dict:
    """获取统计信息

    Returns:
        统计信息
    """
    try:
        detailed_stats = stats_reporter.get_detailed_stats()

        return {
            'status': 'success',
            'data': detailed_stats
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get("/textbooks/{textbook_id}/stats")
async def get_textbook_stats(textbook_id: str) -> Dict:
    """获取单个教材的统计信息

    Args:
        textbook_id: 教材 ID

    Returns:
        统计信息
    """
    try:
        stats = stats_reporter.get_textbook_stats(textbook_id)
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Textbook {textbook_id} not found"
            )

        return {
            'status': 'success',
            'data': stats
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get textbook stats: {str(e)}"
        )
