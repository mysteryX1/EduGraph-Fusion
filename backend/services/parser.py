import re
import json
from typing import List, Tuple, Optional
from pathlib import Path
from ..models.schemas import Chapter, ParseResult
from datetime import datetime

try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False


class ChapterParser:
    """章节识别和解析"""

    # 章节标题正则模式
    CHAPTER_PATTERNS = [
        r"^第[一二三四五六七八九十百千万\d]{1,4}章\s*[^\n]*",  # 第X章
        r"^Chapter\s+[IVX\d]+\s*[^\n]*",  # Chapter X
        r"^(\d{1,2}\.\d{1,2})\s+[^\n]+",  # 1.1 标题
        r"^(\d{1,2})\s+[^\n]+",  # 1 标题
    ]

    def __init__(self, chunk_size: int = 1000):
        """初始化解析器

        Args:
            chunk_size: 无法识别章节时的固定字数
        """
        self.chunk_size = chunk_size

    def is_chapter_title(self, text: str) -> bool:
        """判断文本是否为章节标题"""
        text = text.strip()
        for pattern in self.CHAPTER_PATTERNS:
            if re.match(pattern, text):
                return True
        return False

    def extract_chapter_num(self, title: str) -> Optional[int]:
        """从标题提取章节号"""
        # 提取数字
        match = re.search(r'\d+', title)
        if match:
            try:
                return int(match.group())
            except:
                return None
        return None


class PDFParser:
    """PDF 解析器 - 逐页处理"""

    def __init__(self, chunk_size: int = 1000):
        self.chapter_parser = ChapterParser(chunk_size=chunk_size)
        self.chunk_size = chunk_size

    def parse(self, file_path: str, textbook_id: str) -> ParseResult:
        """解析 PDF 文件

        Args:
            file_path: PDF 文件路径
            textbook_id: 教材 ID

        Returns:
            ParseResult 包含解析结果
        """
        try:
            if not HAS_FITZ:
                # 没有 PyMuPDF，使用文本模拟解析
                return self._parse_without_fitz(file_path, textbook_id)

            doc = fitz.open(file_path)
            chapters = []
            current_chapter = None
            current_content = ""
            current_page = 0
            start_page = 0

            total_pages = len(doc)

            for page_num in range(total_pages):
                page = doc[page_num]
                text = page.get_text()

                # 按行分割文本
                lines = text.split('\n')

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # 检查是否为章节标题
                    if self.chapter_parser.is_chapter_title(line):
                        # 保存前一个章节
                        if current_content.strip():
                            if current_chapter is None:
                                current_chapter = {
                                    'title': 'Introduction',
                                    'chapter_num': 0,
                                    'start_page': 0,
                                }

                            chapter = self._create_chapter(
                                textbook_id,
                                len(chapters),
                                current_chapter['title'],
                                current_chapter['start_page'],
                                page_num,
                                current_content
                            )
                            chapters.append(chapter)

                        # 开始新章节
                        chapter_num = self.chapter_parser.extract_chapter_num(line) or len(chapters) + 1
                        current_chapter = {
                            'title': line,
                            'chapter_num': chapter_num,
                            'start_page': page_num,
                        }
                        current_content = ""
                        start_page = page_num
                    else:
                        current_content += line + "\n"

                current_page = page_num

            # 保存最后一个章节
            if current_content.strip():
                if current_chapter is None:
                    current_chapter = {
                        'title': 'Conclusion',
                        'chapter_num': len(chapters),
                        'start_page': current_page,
                    }

                chapter = self._create_chapter(
                    textbook_id,
                    len(chapters),
                    current_chapter['title'],
                    current_chapter['start_page'],
                    total_pages - 1,
                    current_content
                )
                chapters.append(chapter)

            # 如果没有识别到任何章节，按固定字数分割
            if not chapters:
                chapters = self._split_by_chunk_size(
                    textbook_id,
                    self._read_all_text(doc),
                    total_pages
                )

            doc.close()

            total_words = sum(ch.word_count for ch in chapters)

            return ParseResult(
                textbook_id=textbook_id,
                status="success",
                message=f"Successfully parsed {total_pages} pages, {len(chapters)} chapters",
                chapters=chapters,
                created_at=datetime.now()
            )

        except Exception as e:
            return ParseResult(
                textbook_id=textbook_id,
                status="failed",
                message=f"PDF parsing failed: {str(e)}",
                chapters=[],
                created_at=datetime.now()
            )

    def _create_chapter(
        self,
        textbook_id: str,
        chapter_index: int,
        title: str,
        start_page: int,
        end_page: int,
        content: str
    ) -> Chapter:
        """创建 Chapter 对象"""
        word_count = len(content.split())
        chapter_id = f"{textbook_id}_ch_{chapter_index}"

        return Chapter(
            id=chapter_id,
            chapter_num=chapter_index,
            title=title,
            start_page=start_page,
            end_page=end_page,
            content=content,
            word_count=word_count
        )

    def _read_all_text(self, doc) -> str:
        """读取 PDF 全文"""
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text

    def _parse_without_fitz(self, file_path: str, textbook_id: str) -> ParseResult:
        """在没有 PyMuPDF 的情况下解析 PDF（使用文本模拟）"""
        try:
            # 模拟读取 PDF，实际上读取文本
            with open(file_path, 'rb') as f:
                content = f.read()

            # 假设是文本形式，解析为文本
            text = content.decode('utf-8', errors='ignore')

            # 按章节分割
            chapters = []
            lines = text.split('\n')

            current_chapter = None
            current_content = ""

            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue

                if self.chapter_parser.is_chapter_title(line):
                    if current_content.strip() and current_chapter:
                        chapter = self._create_chapter(
                            textbook_id,
                            len(chapters),
                            current_chapter['title'],
                            current_chapter['start_page'],
                            i,
                            current_content
                        )
                        chapters.append(chapter)

                    current_chapter = {
                        'title': line,
                        'chapter_num': self.chapter_parser.extract_chapter_num(line) or len(chapters),
                        'start_page': i,
                    }
                    current_content = ""
                else:
                    if current_chapter:
                        current_content += line + "\n"

            if current_content.strip() and current_chapter:
                chapter = self._create_chapter(
                    textbook_id,
                    len(chapters),
                    current_chapter['title'],
                    current_chapter['start_page'],
                    len(lines),
                    current_content
                )
                chapters.append(chapter)

            if not chapters:
                chapters = self._split_by_chunk_size(textbook_id, text, 1)

            total_words = sum(ch.word_count for ch in chapters)

            return ParseResult(
                textbook_id=textbook_id,
                status="success",
                message=f"Successfully parsed {len(chapters)} chapters (模拟模式，无 PyMuPDF)",
                chapters=chapters,
                created_at=datetime.now()
            )
        except Exception as e:
            return ParseResult(
                textbook_id=textbook_id,
                status="failed",
                message=f"PDF parsing failed: {str(e)}",
                chapters=[],
                created_at=datetime.now()
            )

    def _split_by_chunk_size(
        self,
        textbook_id: str,
        text: str,
        total_pages: int
    ) -> List[Chapter]:
        """按固定字数分割文本生成伪章节"""
        chapters = []
        words = text.split()

        chapter_index = 0
        for i in range(0, len(words), self.chunk_size):
            chunk_words = words[i:i + self.chunk_size]
            content = " ".join(chunk_words)

            chapter = Chapter(
                id=f"{textbook_id}_ch_{chapter_index}",
                chapter_num=chapter_index,
                title=f"Section {chapter_index + 1}",
                start_page=int(i * total_pages / len(words)),
                end_page=int((i + self.chunk_size) * total_pages / len(words)),
                content=content,
                word_count=len(chunk_words)
            )
            chapters.append(chapter)
            chapter_index += 1

        return chapters


class MarkdownParser:
    """Markdown 解析器"""

    def __init__(self, chunk_size: int = 1000):
        self.chapter_parser = ChapterParser(chunk_size=chunk_size)
        self.chunk_size = chunk_size

    def parse(self, file_path: str, textbook_id: str) -> ParseResult:
        """解析 Markdown 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 按 # 分割为章节
            chapters = []
            lines = content.split('\n')

            current_chapter = None
            current_content = ""

            for line in lines:
                # 检测 Markdown 标题
                if line.startswith('#'):
                    if current_content.strip() and current_chapter:
                        chapter = self._create_chapter(
                            textbook_id,
                            len(chapters),
                            current_chapter['title'],
                            current_content
                        )
                        chapters.append(chapter)

                    # 提取标题
                    title = line.lstrip('#').strip()
                    current_chapter = {'title': title}
                    current_content = ""
                else:
                    if current_chapter:
                        current_content += line + "\n"

            # 保存最后一个章节
            if current_content.strip() and current_chapter:
                chapter = self._create_chapter(
                    textbook_id,
                    len(chapters),
                    current_chapter['title'],
                    current_content
                )
                chapters.append(chapter)

            return ParseResult(
                textbook_id=textbook_id,
                status="success",
                message=f"Successfully parsed {len(chapters)} chapters",
                chapters=chapters,
                created_at=datetime.now()
            )

        except Exception as e:
            return ParseResult(
                textbook_id=textbook_id,
                status="failed",
                message=f"Markdown parsing failed: {str(e)}",
                chapters=[],
                created_at=datetime.now()
            )

    def _create_chapter(
        self,
        textbook_id: str,
        chapter_index: int,
        title: str,
        content: str
    ) -> Chapter:
        """创建 Chapter 对象"""
        word_count = len(content.split())

        return Chapter(
            id=f"{textbook_id}_ch_{chapter_index}",
            chapter_num=chapter_index,
            title=title,
            start_page=0,
            end_page=0,
            content=content,
            word_count=word_count
        )


class TextParser:
    """纯文本解析器"""

    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size

    def parse(self, file_path: str, textbook_id: str) -> ParseResult:
        """解析文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 按固定字数分割
            chapters = self._split_by_chunk_size(textbook_id, content)

            return ParseResult(
                textbook_id=textbook_id,
                status="success",
                message=f"Successfully parsed {len(chapters)} sections",
                chapters=chapters,
                created_at=datetime.now()
            )

        except Exception as e:
            return ParseResult(
                textbook_id=textbook_id,
                status="failed",
                message=f"Text parsing failed: {str(e)}",
                chapters=[],
                created_at=datetime.now()
            )

    def _split_by_chunk_size(self, textbook_id: str, text: str) -> List[Chapter]:
        """按固定字数分割"""
        chapters = []
        words = text.split()

        chapter_index = 0
        for i in range(0, len(words), self.chunk_size):
            chunk_words = words[i:i + self.chunk_size]
            content = " ".join(chunk_words)

            chapter = Chapter(
                id=f"{textbook_id}_ch_{chapter_index}",
                chapter_num=chapter_index,
                title=f"Section {chapter_index + 1}",
                start_page=0,
                end_page=0,
                content=content,
                word_count=len(chunk_words)
            )
            chapters.append(chapter)
            chapter_index += 1

        return chapters


class ParserFactory:
    """解析器工厂"""

    @staticmethod
    def get_parser(file_type: str, chunk_size: int = 1000):
        """根据文件类型返回相应的解析器"""
        if file_type.lower() == 'pdf':
            return PDFParser(chunk_size=chunk_size)
        elif file_type.lower() in ['md', 'markdown']:
            return MarkdownParser(chunk_size=chunk_size)
        elif file_type.lower() == 'txt':
            return TextParser(chunk_size=chunk_size)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
