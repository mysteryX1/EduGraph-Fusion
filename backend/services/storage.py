import json
import os
from typing import Optional, List
from pathlib import Path
from datetime import datetime
import uuid
from ..models.schemas import Textbook, Chapter, TextbookMetadata


class FileStorage:
    """文件存储管理"""

    def __init__(self, base_path: str = "./data"):
        self.base_path = Path(base_path)
        self.uploads_dir = self.base_path / "uploads"
        self.metadata_dir = self.base_path / "metadata"

        # 创建必要的目录
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

    def save_uploaded_file(self, file_path: str, filename: str) -> str:
        """保存上传的文件

        Args:
            file_path: 临时文件路径
            filename: 原始文件名

        Returns:
            保存后的文件路径
        """
        # 生成唯一的文件名
        file_ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        saved_path = self.uploads_dir / unique_name

        # 移动文件
        import shutil
        shutil.move(file_path, str(saved_path))

        return str(saved_path)

    def save_parse_result(self, textbook_id: str, chapters: List[Chapter], metadata: dict):
        """保存解析结果为 JSON

        Args:
            textbook_id: 教材 ID
            chapters: 章节列表
            metadata: 元数据
        """
        # 保存章节内容
        chapters_file = self.metadata_dir / f"{textbook_id}_chapters.json"
        chapters_data = [
            {
                "id": ch.id,
                "chapter_num": ch.chapter_num,
                "title": ch.title,
                "start_page": ch.start_page,
                "end_page": ch.end_page,
                "content": ch.content,
                "word_count": ch.word_count,
            }
            for ch in chapters
        ]

        with open(chapters_file, 'w', encoding='utf-8') as f:
            json.dump(chapters_data, f, ensure_ascii=False, indent=2)

        # 保存元数据
        metadata_file = self.metadata_dir / f"{textbook_id}_metadata.json"
        metadata['id'] = textbook_id
        metadata['upload_time'] = metadata.get('upload_time', datetime.now().isoformat())

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def load_chapters(self, textbook_id: str) -> Optional[List[Chapter]]:
        """加载保存的章节

        Args:
            textbook_id: 教材 ID

        Returns:
            Chapter 列表或 None
        """
        chapters_file = self.metadata_dir / f"{textbook_id}_chapters.json"

        if not chapters_file.exists():
            return None

        with open(chapters_file, 'r', encoding='utf-8') as f:
            chapters_data = json.load(f)

        chapters = [
            Chapter(
                id=ch['id'],
                chapter_num=ch['chapter_num'],
                title=ch['title'],
                start_page=ch['start_page'],
                end_page=ch['end_page'],
                content=ch['content'],
                word_count=ch['word_count'],
            )
            for ch in chapters_data
        ]

        return chapters

    def load_metadata(self, textbook_id: str) -> Optional[dict]:
        """加载元数据

        Args:
            textbook_id: 教材 ID

        Returns:
            元数据字典或 None
        """
        metadata_file = self.metadata_dir / f"{textbook_id}_metadata.json"

        if not metadata_file.exists():
            return None

        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_textbook(self, textbook_id: str) -> Optional[Textbook]:
        """加载完整的教材信息

        Args:
            textbook_id: 教材 ID

        Returns:
            Textbook 对象或 None
        """
        metadata = self.load_metadata(textbook_id)
        if not metadata:
            return None

        chapters = self.load_chapters(textbook_id) or []

        return Textbook(
            id=textbook_id,
            filename=metadata.get('filename', ''),
            title=metadata.get('title', ''),
            file_type=metadata.get('file_type', ''),
            upload_time=datetime.fromisoformat(metadata.get('upload_time', datetime.now().isoformat())),
            file_path=metadata.get('file_path', ''),
            total_pages=metadata.get('total_pages', 0),
            total_words=sum(ch.word_count for ch in chapters),
            chapters=chapters
        )

    def list_all_textbooks(self) -> List[TextbookMetadata]:
        """列出所有教材

        Returns:
            TextbookMetadata 列表
        """
        textbooks = []

        # 查找所有元数据文件
        for metadata_file in self.metadata_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

                textbook_id = metadata.get('id', '')
                if not textbook_id:
                    continue

                # 加载对应的章节获取统计信息
                chapters = self.load_chapters(textbook_id) or []

                textbook = TextbookMetadata(
                    id=textbook_id,
                    filename=metadata.get('filename', ''),
                    title=metadata.get('title', ''),
                    file_type=metadata.get('file_type', ''),
                    upload_time=datetime.fromisoformat(metadata.get('upload_time', datetime.now().isoformat())),
                    total_pages=metadata.get('total_pages', 0),
                    total_words=sum(ch.word_count for ch in chapters),
                    chapter_count=len(chapters)
                )
                textbooks.append(textbook)
            except Exception as e:
                print(f"Error loading textbook from {metadata_file}: {e}")
                continue

        return sorted(textbooks, key=lambda x: x.upload_time, reverse=True)

    def delete_textbook(self, textbook_id: str) -> bool:
        """删除教材及其相关文件

        Args:
            textbook_id: 教材 ID

        Returns:
            是否删除成功
        """
        try:
            # 删除元数据
            metadata_file = self.metadata_dir / f"{textbook_id}_metadata.json"
            chapters_file = self.metadata_dir / f"{textbook_id}_chapters.json"

            if metadata_file.exists():
                metadata_file.unlink()
            if chapters_file.exists():
                chapters_file.unlink()

            # 删除上传的文件
            metadata = self.load_metadata(textbook_id)
            if metadata and 'file_path' in metadata:
                file_path = Path(metadata['file_path'])
                if file_path.exists():
                    file_path.unlink()

            return True
        except Exception as e:
            print(f"Error deleting textbook {textbook_id}: {e}")
            return False

    def get_storage_stats(self) -> dict:
        """获取存储统计信息"""
        textbooks = self.list_all_textbooks()

        total_files = len(textbooks)
        total_chapters = sum(tb.chapter_count for tb in textbooks)
        total_words = sum(tb.total_words for tb in textbooks)

        file_types = {}
        for tb in textbooks:
            file_type = tb.file_type
            file_types[file_type] = file_types.get(file_type, 0) + 1

        return {
            'total_textbooks': total_files,
            'total_chapters': total_chapters,
            'total_words': total_words,
            'file_types': file_types,
            'textbooks': [
                {
                    'id': tb.id,
                    'title': tb.title,
                    'file_type': tb.file_type,
                    'chapter_count': tb.chapter_count,
                    'total_words': tb.total_words,
                }
                for tb in textbooks
            ]
        }
