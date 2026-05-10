from typing import Dict, List
from collections import defaultdict
from datetime import datetime, timedelta
from ..models.schemas import Stats
from .storage import FileStorage


class StatsReporter:
    """统计报告生成"""

    def __init__(self, storage: FileStorage):
        self.storage = storage

    def generate_stats(self) -> Stats:
        """生成统计信息

        Returns:
            Stats 对象
        """
        storage_stats = self.storage.get_storage_stats()

        textbooks = self.storage.list_all_textbooks()

        # 统计文件类型
        file_types = defaultdict(int)
        for tb in textbooks:
            file_types[tb.file_type] += 1

        # 统计上传时间分布
        upload_times = defaultdict(int)
        for tb in textbooks:
            date_key = tb.upload_time.strftime("%Y-%m-%d")
            upload_times[date_key] += 1

        total_chapters = sum(tb.chapter_count for tb in textbooks)
        total_words = sum(tb.total_words for tb in textbooks)

        avg_words_per_chapter = (
            total_words / total_chapters if total_chapters > 0 else 0
        )

        return Stats(
            total_textbooks=len(textbooks),
            total_chapters=total_chapters,
            total_words=total_words,
            avg_words_per_chapter=round(avg_words_per_chapter, 2),
            file_types=dict(file_types),
            upload_times=dict(upload_times)
        )

    def get_detailed_stats(self) -> Dict:
        """获取详细统计信息

        Returns:
            详细统计字典
        """
        stats = self.generate_stats()

        textbooks = self.storage.list_all_textbooks()

        # 按文件类型分组
        textbooks_by_type = defaultdict(list)
        for tb in textbooks:
            textbooks_by_type[tb.file_type].append({
                'id': tb.id,
                'title': tb.title,
                'chapter_count': tb.chapter_count,
                'total_words': tb.total_words,
                'upload_time': tb.upload_time.isoformat()
            })

        # 按章节数量排序教材
        top_textbooks = sorted(
            textbooks,
            key=lambda x: x.chapter_count,
            reverse=True
        )[:10]

        return {
            'summary': {
                'total_textbooks': stats.total_textbooks,
                'total_chapters': stats.total_chapters,
                'total_words': stats.total_words,
                'avg_words_per_chapter': stats.avg_words_per_chapter,
            },
            'file_types': stats.file_types,
            'upload_times': stats.upload_times,
            'textbooks_by_type': dict(textbooks_by_type),
            'top_textbooks': [
                {
                    'id': tb.id,
                    'title': tb.title,
                    'chapter_count': tb.chapter_count,
                    'total_words': tb.total_words,
                }
                for tb in top_textbooks
            ]
        }

    def get_textbook_stats(self, textbook_id: str) -> Dict:
        """获取单个教材的统计信息

        Args:
            textbook_id: 教材 ID

        Returns:
            统计信息字典
        """
        textbook = self.storage.load_textbook(textbook_id)
        if not textbook:
            return None

        chapters = textbook.chapters or []

        word_counts = [ch.word_count for ch in chapters]
        avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
        max_words = max(word_counts) if word_counts else 0
        min_words = min(word_counts) if word_counts else 0

        return {
            'textbook_id': textbook_id,
            'title': textbook.title,
            'file_type': textbook.file_type,
            'upload_time': textbook.upload_time.isoformat(),
            'total_pages': textbook.total_pages,
            'total_words': textbook.total_words,
            'chapter_count': len(chapters),
            'chapter_stats': {
                'avg_words_per_chapter': round(avg_words, 2),
                'max_words': max_words,
                'min_words': min_words,
            },
            'chapters': [
                {
                    'chapter_num': ch.chapter_num,
                    'title': ch.title,
                    'word_count': ch.word_count,
                    'start_page': ch.start_page,
                    'end_page': ch.end_page,
                }
                for ch in chapters
            ]
        }
