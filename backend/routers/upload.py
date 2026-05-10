from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import Dict
import uuid
import os
from pathlib import Path
from ..services import FileStorage, ParserFactory
from ..models.schemas import Textbook


router = APIRouter(prefix="/api", tags=["upload"])

# 全局存储实例
storage = FileStorage()

# 允许的文件类型
ALLOWED_EXTENSIONS = {'.pdf', '.md', '.markdown', '.txt'}


def _get_file_type(filename: str) -> str:
    """从文件名获取文件类型"""
    ext = Path(filename).suffix.lower()

    if ext == '.pdf':
        return 'pdf'
    elif ext in ['.md', '.markdown']:
        return 'markdown'
    elif ext == '.txt':
        return 'txt'
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _save_temp_file(file: UploadFile) -> str:
    """保存上传的临时文件"""
    temp_dir = Path("./temp")
    temp_dir.mkdir(exist_ok=True)

    temp_path = temp_dir / f"{uuid.uuid4()}_{file.filename}"

    with open(temp_path, "wb") as f:
        content = file.file.read()
        f.write(content)

    return str(temp_path)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> Dict:
    """上传文件

    支持的文件类型:
    - PDF (.pdf)
    - Markdown (.md, .markdown)
    - 纯文本 (.txt)

    Returns:
        包含文件信息和教材 ID 的响应
    """
    try:
        # 检查文件扩展名
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # 检查文件大小 (最大 100MB)
        max_size = 100 * 1024 * 1024
        file.file.seek(0, 2)  # 移到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置指针

        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size is {max_size / 1024 / 1024:.0f}MB"
            )

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )

        # 生成教材 ID
        textbook_id = f"textbook_{uuid.uuid4().hex[:12]}"

        # 保存临时文件
        temp_path = await _save_temp_file_async(file)

        # 保存到存储
        saved_path = storage.save_uploaded_file(temp_path, file.filename)

        # 获取文件类型
        file_type = _get_file_type(file.filename)

        # 保存元数据
        metadata = {
            'filename': file.filename,
            'title': Path(file.filename).stem,
            'file_type': file_type,
            'file_path': saved_path,
            'file_size': file_size,
            'total_pages': 0,  # 暂时设为 0，解析时更新
        }

        storage.save_parse_result(textbook_id, [], metadata)

        return {
            'status': 'success',
            'message': 'File uploaded successfully',
            'data': {
                'textbook_id': textbook_id,
                'filename': file.filename,
                'file_type': file_type,
                'file_size': file_size,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )


async def _save_temp_file_async(file: UploadFile) -> str:
    """异步保存临时文件"""
    temp_dir = Path("./temp")
    temp_dir.mkdir(exist_ok=True)

    temp_path = temp_dir / f"{uuid.uuid4()}_{file.filename}"

    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return str(temp_path)
