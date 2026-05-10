import json
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import numpy as np
from datetime import datetime
import re

from ..models.schemas import Citation, RagAnswer


class ChunkManager:
    """负责文本 chunk 管理"""

    def __init__(self, chunk_size: int = 700, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, metadata: dict) -> List[dict]:
        """按字符数切分文本，保留元数据

        Args:
            text: 要切分的文本
            metadata: 元数据 {textbook, chapter, page, chapter_id}

        Returns:
            chunk 列表，每个 chunk 包含 content 和 metadata
        """
        chunks = []
        chunk_id = 0

        if not text:
            return chunks

        # 按照 chunk_size 和 overlap 切分
        for start in range(0, len(text), self.chunk_size - self.overlap):
            end = start + self.chunk_size
            chunk_content = text[start:end]

            if not chunk_content.strip():
                continue

            chunk = {
                'id': f"{metadata.get('chapter_id', 'unknown')}_{chunk_id}",
                'content': chunk_content,
                'start_pos': start,
                'end_pos': end,
                'metadata': {
                    'textbook': metadata.get('textbook', ''),
                    'chapter': metadata.get('chapter', ''),
                    'chapter_id': metadata.get('chapter_id', ''),
                    'page': metadata.get('page', 0),
                }
            }
            chunks.append(chunk)
            chunk_id += 1

        return chunks


class EmbeddingProvider:
    """向量嵌入提供者"""

    def __init__(self):
        self.embedding_model = None
        self.use_tfidf = False
        self._init_embedding()

    def _init_embedding(self):
        """初始化嵌入模型"""
        try:
            from sentence_transformers import SentenceTransformer
            # 尝试使用轻量级的中文模型
            model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            self.embedding_model = SentenceTransformer(model_name)
            print(f"Using SentenceTransformer: {model_name}")
        except ImportError:
            print("sentence-transformers not available, using TF-IDF fallback")
            self.use_tfidf = True
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                self.tfidf = TfidfVectorizer(max_features=5000, analyzer='char', ngram_range=(1, 2))
            except ImportError:
                raise ImportError("Neither sentence-transformers nor sklearn is available")

    def embed(self, texts: List[str]) -> np.ndarray:
        """生成文本向量"""
        if self.embedding_model:
            return self.embedding_model.encode(texts, convert_to_numpy=True)
        else:
            # TF-IDF fallback
            if not hasattr(self, '_tfidf_fitted'):
                self.tfidf.fit(texts)
                self._tfidf_fitted = True
            return self.tfidf.transform(texts).toarray().astype('float32')

    def embed_single(self, text: str) -> np.ndarray:
        """生成单条文本向量"""
        return self.embed([text])[0]


class VectorStore:
    """向量库管理"""

    def __init__(self, embedding_provider: EmbeddingProvider):
        self.embedding_provider = embedding_provider
        self.chunks = []
        self.embeddings = None
        self.index = None
        self.use_faiss = False
        self._init_store()

    def _init_store(self):
        """初始化向量库"""
        try:
            import faiss
            self.use_faiss = True
            self.faiss_index = None
            print("Using FAISS for vector search")
        except ImportError:
            print("FAISS not available, using sklearn NearestNeighbors")
            from sklearn.neighbors import NearestNeighbors
            self.nn_model = NearestNeighbors(n_neighbors=5, metric='cosine')

    def add_chunks(self, chunks: List[dict]):
        """添加 chunks 到向量库"""
        if not chunks:
            return

        self.chunks.extend(chunks)

        # 为所有 chunks 生成向量
        chunk_contents = [chunk['content'] for chunk in self.chunks]
        self.embeddings = self.embedding_provider.embed(chunk_contents)

        # 初始化索引
        if self.use_faiss:
            try:
                import faiss
                dimension = self.embeddings.shape[1]
                self.faiss_index = faiss.IndexFlatL2(dimension)
                # FAISS 使用 L2 距离，转换为 float32
                self.faiss_index.add(self.embeddings.astype('float32'))
            except Exception as e:
                print(f"FAISS indexing failed: {e}, falling back to sklearn")
                self.use_faiss = False

        if not self.use_faiss:
            self.nn_model.fit(self.embeddings)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[dict, float]]:
        """搜索最相似的 chunks

        Args:
            query: 查询文本
            top_k: 返回结果数

        Returns:
            [(chunk, similarity_score), ...] 列表
        """
        if not self.chunks or self.embeddings is None:
            return []

        query_embedding = self.embedding_provider.embed_single(query)

        if self.use_faiss and self.faiss_index:
            try:
                import faiss
                distances, indices = self.faiss_index.search(
                    np.array([query_embedding], dtype='float32'),
                    min(top_k, len(self.chunks))
                )
                results = []
                for dist, idx in zip(distances[0], indices[0]):
                    if idx >= 0 and idx < len(self.chunks):
                        # L2 距离转换为相似度 (1 - normalized_distance)
                        similarity = 1 / (1 + dist)
                        results.append((self.chunks[idx], float(similarity)))
                return results
            except Exception as e:
                print(f"FAISS search failed: {e}")

        # sklearn NearestNeighbors fallback
        distances, indices = self.nn_model.kneighbors(
            np.array([query_embedding]),
            n_neighbors=min(top_k, len(self.chunks))
        )
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            # cosine 距离转换为相似度
            similarity = 1 - dist
            results.append((self.chunks[idx], float(similarity)))
        return results


class RAGEngine:
    """RAG 引擎"""

    def __init__(self, data_dir: str = "./data/processed"):
        self.data_dir = Path(data_dir)
        self.embedding_provider = EmbeddingProvider()
        self.vector_store = VectorStore(self.embedding_provider)
        self.chunks = []

    def load_and_index(self):
        """加载已解析教材并建立索引"""
        processed_dir = self.data_dir

        if not processed_dir.exists():
            print(f"Warning: {processed_dir} does not exist, creating it")
            processed_dir.mkdir(parents=True, exist_ok=True)
            return False

        chunk_manager = ChunkManager(chunk_size=700, overlap=100)
        all_chunks = []

        # 遍历所有教材的已解析 JSON
        for json_file in processed_dir.glob("*.json"):
            if json_file.name.startswith('_'):
                continue

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 处理教材数据
                textbook_id = data.get('id', json_file.stem)
                textbook_name = data.get('title', '')
                chapters = data.get('chapters', [])

                for chapter in chapters:
                    chapter_id = chapter.get('id', '')
                    chapter_num = chapter.get('chapter_num', 0)
                    chapter_title = chapter.get('title', '')
                    content = chapter.get('content', '')
                    start_page = chapter.get('start_page', 0)

                    # 为章节内容创建 chunks
                    metadata = {
                        'textbook': textbook_name,
                        'textbook_id': textbook_id,
                        'chapter': chapter_title,
                        'chapter_id': chapter_id,
                        'chapter_num': chapter_num,
                        'page': start_page,
                    }

                    chunks = chunk_manager.chunk_text(content, metadata)
                    all_chunks.extend(chunks)

            except Exception as e:
                print(f"Error loading {json_file}: {e}")
                continue

        # 添加到向量库
        self.vector_store.add_chunks(all_chunks)
        self.chunks = all_chunks

        return len(all_chunks) > 0

    def query(self, question: str, top_k: int = 5) -> Dict:
        """查询并生成答案"""
        if not self.chunks:
            return {
                'success': False,
                'message': 'Knowledge base not indexed',
                'answer': '',
                'citations': [],
                'source_chunks': []
            }

        # 搜索相关 chunks
        search_results = self.vector_store.search(question, top_k=top_k)

        if not search_results:
            return {
                'success': True,
                'message': 'No relevant content found',
                'answer': '当前知识库中未找到相关信息',
                'citations': [],
                'source_chunks': []
            }

        # 获取源文本和元数据
        source_chunks = []
        source_texts = []
        for chunk, similarity in search_results:
            source_chunks.append({
                'id': chunk['id'],
                'content': chunk['content'][:200] + '...' if len(chunk['content']) > 200 else chunk['content'],
                'similarity': similarity,
                'metadata': chunk['metadata']
            })
            source_texts.append(chunk['content'])

        # 调用 LLM 生成答案
        context = '\n\n'.join(source_texts)
        answer = self._generate_answer(question, context, source_chunks)

        # 构建 citations
        citations = self._build_citations(source_chunks)

        return {
            'success': True,
            'answer': answer,
            'citations': citations,
            'source_chunks': source_chunks
        }

    def _generate_answer(self, question: str, context: str, source_chunks: List[dict]) -> str:
        """使用 LLM 生成答案"""
        prompt = f"""你是一个教学知识助手。根据以下上下文回答问题。

严格遵循以下规则：
1. 只能基于提供的上下文回答问题
2. 如果上下文中没有相关信息，必须回复："当前知识库中未找到相关信息"
3. 在答案中附带来源信息（格式：来自《教材名称》第X章）

上下文：
{context}

问题：{question}

请提供基于上下文的答案："""

        try:
            import litellm

            response = litellm.completion(
                model="qwen3-32b",  # 使用配置文件中的模型
                messages=[
                    {"role": "system", "content": "你是一个专业的教学知识助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
                timeout=30,
            )

            answer = response.choices[0].message.content
            return answer

        except Exception as e:
            print(f"LLM call failed: {e}")
            # Fallback: 返回上下文中最相关的部分
            if source_chunks:
                first_source = source_chunks[0]
                textbook = first_source['metadata'].get('textbook', '')
                chapter = first_source['metadata'].get('chapter', '')
                return f"基于《{textbook}》的《{chapter}》章节，相关内容为：\n{first_source['content'][:500]}..."
            return "无法生成答案，请稍后重试"

    def _build_citations(self, source_chunks: List[dict]) -> List[Dict]:
        """构建引用信息"""
        citations = []
        for chunk in source_chunks:
            metadata = chunk['metadata']
            citation = {
                'chapter_id': metadata.get('chapter_id', ''),
                'chapter': metadata.get('chapter', ''),
                'textbook': metadata.get('textbook', ''),
                'page_number': metadata.get('page', 0),
                'chunk_id': chunk['id'],
                'text_excerpt': chunk['content'][:100] + '...' if len(chunk['content']) > 100 else chunk['content'],
            }
            citations.append(citation)
        return citations
