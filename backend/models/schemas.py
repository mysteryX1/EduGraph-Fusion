from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class KGNode(BaseModel):
    """知识图谱节点"""
    id: str
    name: str
    type: str  # concept, entity, process, etc.
    description: Optional[str] = None
    definition: Optional[str] = None
    chapter: Optional[str] = None
    page: Optional[int] = None
    source_textbook: Optional[str] = None
    frequency: int = 1
    sources: List[str] = []  # 出现位置列表


class KGEdge(BaseModel):
    """知识图谱边"""
    source_id: str
    target_id: str
    relation_type: str  # prerequisite, contains, parallel, related
    weight: float = 1.0
    confidence: float = 1.0


class Citation(BaseModel):
    """引用信息"""
    chapter_id: str
    page_number: int
    text_excerpt: str
    start_pos: int
    end_pos: int


class Chapter(BaseModel):
    """章节"""
    id: str
    chapter_num: int
    title: str
    start_page: int
    end_page: int
    content: str
    word_count: int


class Textbook(BaseModel):
    """教材"""
    id: str
    filename: str
    title: str
    file_type: str  # pdf, markdown, txt
    upload_time: datetime
    file_path: str
    total_pages: int
    total_words: int
    chapters: List[Chapter] = []


class KGExtraction(BaseModel):
    """知识图谱提取结果"""
    textbook_id: str
    nodes: List[KGNode] = []
    edges: List[KGEdge] = []


class MergeDecision(BaseModel):
    """合并决策"""
    source_chapter_ids: List[str]
    target_chapter_id: str
    merge_type: str  # auto, manual
    reason: Optional[str] = None


class RagAnswer(BaseModel):
    """RAG 答案"""
    question: str
    answer: str
    citations: List[Citation] = []
    confidence: float


class ParseResult(BaseModel):
    """解析结果"""
    textbook_id: str
    status: str  # success, failed
    message: str
    chapters: List[Chapter] = []
    created_at: datetime


class TextbookMetadata(BaseModel):
    """教材元数据"""
    id: str
    filename: str
    title: str
    file_type: str
    upload_time: datetime
    total_pages: int
    total_words: int
    chapter_count: int


class Stats(BaseModel):
    """统计信息"""
    total_textbooks: int
    total_chapters: int
    total_words: int
    avg_words_per_chapter: float
    file_types: dict  # {file_type: count}
    upload_times: dict  # {timestamp: count}
