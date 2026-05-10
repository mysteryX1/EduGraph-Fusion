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
        if not self.chunks:
            return []

        # 尝试向量搜索
        if self.embeddings is not None:
            try:
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
                                similarity = 1 / (1 + dist)
                                results.append((self.chunks[idx], float(similarity)))
                        if results:
                            return results
                    except Exception as e:
                        print(f"FAISS search failed: {e}")

                # sklearn NearestNeighbors fallback
                try:
                    distances, indices = self.nn_model.kneighbors(
                        np.array([query_embedding]),
                        n_neighbors=min(top_k, len(self.chunks))
                    )
                    results = []
                    for dist, idx in zip(distances[0], indices[0]):
                        similarity = 1 - dist
                        results.append((self.chunks[idx], float(similarity)))
                    if results:
                        return results
                except Exception as e:
                    print(f"sklearn search failed: {e}")
            except Exception as e:
                print(f"Vector search error: {e}")

        # 关键词匹配 fallback
        print("Using keyword matching fallback")
        return self._keyword_search(query, top_k)

    def _keyword_search(self, query: str, top_k: int = 5) -> List[Tuple[dict, float]]:
        """关键词匹配搜索

        Args:
            query: 查询文本
            top_k: 返回结果数

        Returns:
            [(chunk, relevance_score), ...] 列表
        """
        # 提取查询关键词
        query_words = set(query.split())
        if len(query_words) == 0:
            return []

        # 计算每个 chunk 与查询的匹配度
        scored_chunks = []
        for chunk in self.chunks:
            content = chunk.get('content', '').lower()
            chunk_words = set(content.split())

            # 计算交集比例
            if len(chunk_words) == 0:
                score = 0.0
            else:
                intersection = len(query_words & chunk_words)
                score = intersection / (len(query_words) + len(chunk_words) - intersection + 1e-6)

            if score > 0:
                scored_chunks.append((chunk, float(score)))

        # 按相关性排序，返回 top_k
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return scored_chunks[:top_k]


class RAGEngine:
    """RAG 引擎"""

    def __init__(self, data_dir: str = "./data/processed"):
        self.data_dir = Path(data_dir)
        self.metadata_dir = Path("./data/metadata")
        self.embedding_provider = EmbeddingProvider()
        self.vector_store = VectorStore(self.embedding_provider)
        self.chunks = []

    def load_and_index(self):
        """加载已解析教材并建立索引

        优先读取 ./data/metadata/*_chapters.json (模块一输出)，
        兼容 ./data/processed 目录 (模块二输出)
        """
        chunk_manager = ChunkManager(chunk_size=700, overlap=100)
        all_chunks = []

        # 优先从 metadata 目录读取（模块一的输出）
        if self.metadata_dir.exists():
            all_chunks.extend(self._load_from_metadata(chunk_manager))

        # 兼容 processed 目录（模块二的输出）
        if self.data_dir.exists():
            all_chunks.extend(self._load_from_processed(chunk_manager))

        # 添加到向量库
        if all_chunks:
            self.vector_store.add_chunks(all_chunks)
            self.chunks = all_chunks
            return True

        return False

    def _load_from_metadata(self, chunk_manager) -> List[dict]:
        """从 metadata 目录加载章节数据（模块一输出）"""
        all_chunks = []

        for chapters_file in self.metadata_dir.glob("*_chapters.json"):
            try:
                # 提取教材 ID
                textbook_id = chapters_file.stem.replace('_chapters', '')

                with open(chapters_file, 'r', encoding='utf-8') as f:
                    chapters_data = json.load(f)

                # 尝试加载对应的元数据
                metadata_file = self.metadata_dir / f"{textbook_id}_metadata.json"
                textbook_name = textbook_id
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            textbook_name = metadata.get('title', textbook_id)
                    except:
                        pass

                # 处理章节
                for chapter in chapters_data:
                    chapter_id = chapter.get('id', '')
                    chapter_num = chapter.get('chapter_num', 0)
                    chapter_title = chapter.get('title', '')
                    content = chapter.get('content', '')
                    start_page = chapter.get('start_page', 0)

                    if not content or not content.strip():
                        continue

                    # 为章节内容创建 chunks
                    metadata_dict = {
                        'textbook': textbook_name,
                        'textbook_id': textbook_id,
                        'chapter': chapter_title,
                        'chapter_id': chapter_id,
                        'chapter_num': chapter_num,
                        'page': start_page,
                        'page_number': start_page,  # 兼容两种命名
                    }

                    chunks = chunk_manager.chunk_text(content, metadata_dict)
                    all_chunks.extend(chunks)

            except Exception as e:
                print(f"Error loading from metadata {chapters_file}: {e}")
                continue

        return all_chunks

    def _load_from_processed(self, chunk_manager) -> List[dict]:
        """从 processed 目录加载数据（模块二输出，兼容）"""
        all_chunks = []

        for json_file in self.data_dir.glob("*.json"):
            if json_file.name.startswith('_') or json_file.name in ['merged_kg.json', 'merge_decisions.json', 'kg_nodes.json', 'kg_edges.json']:
                continue

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 兼容 list 和 dict 格式
                if isinstance(data, list):
                    continue
                if not isinstance(data, dict):
                    continue

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

                    if not content or not content.strip():
                        continue

                    # 为章节内容创建 chunks
                    metadata = {
                        'textbook': textbook_name,
                        'textbook_id': textbook_id,
                        'chapter': chapter_title,
                        'chapter_id': chapter_id,
                        'chapter_num': chapter_num,
                        'page': start_page,
                        'page_number': start_page,
                    }

                    chunks = chunk_manager.chunk_text(content, metadata)
                    all_chunks.extend(chunks)

            except Exception as e:
                print(f"Error loading from processed {json_file}: {e}")
                continue

        return all_chunks

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
            source_chunk_dict = {
                'id': chunk['id'],
                'content': chunk['content'][:200] + '...' if len(chunk['content']) > 200 else chunk['content'],
                'similarity': similarity,
                'metadata': chunk['metadata']
            }
            source_chunks.append(source_chunk_dict)
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
        # 先尝试 LLM，如果没有配置则直接用 fallback
        answer = self._try_llm_answer(question, context)
        if answer:
            return answer

        # Fallback: 返回上下文中最相关的部分
        if source_chunks:
            first_source = source_chunks[0]
            textbook = first_source['metadata'].get('textbook', '')
            chapter = first_source['metadata'].get('chapter', '')
            return f"基于《{textbook}》的《{chapter}》章节，相关内容为：\n{first_source['content'][:500]}..."
        return "无法生成答案，请稍后重试"

    def _try_llm_answer(self, question: str, context: str) -> str:
        """尝试使用 LLM 生成答案，失败则返回空"""
        try:
            import os
            # 检查是否配置了 LLM 提供商
            has_provider = os.getenv("LITELLM_PROVIDER") or os.getenv("OPENAI_API_KEY") or os.getenv("QWEN_API_KEY")
            if not has_provider:
                return ""  # 没有配置，跳过 LLM 调用

            import litellm

            prompt = f"""你是一个教学知识助手。根据以下上下文回答问题。

严格遵循以下规则：
1. 只能基于提供的上下文回答问题
2. 如果上下文中没有相关信息，必须回复："当前知识库中未找到相关信息"
3. 在答案中附带来源信息（格式：来自《教材名称》第X章）

上下文：
{context}

问题：{question}

请提供基于上下文的答案："""

            response = litellm.completion(
                model="qwen3-32b",
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

        except ImportError:
            # litellm 未安装，使用 fallback
            return ""
        except Exception as e:
            # 其他错误（如提供商未配置），使用 fallback，不打印大段错误
            if "NOT provided" not in str(e) and "BadRequestError" not in str(type(e).__name__):
                print(f"⚠️  LLM call warning: {type(e).__name__}")
            return ""

    def _build_citations(self, source_chunks: List[dict]) -> List[Dict]:
        """构建引用信息"""
        citations = []
        for chunk in source_chunks:
            metadata = chunk['metadata']
            citation = {
                'textbook': metadata.get('textbook', ''),
                'chapter': metadata.get('chapter', ''),
                'chapter_id': metadata.get('chapter_id', ''),
                'page_number': metadata.get('page_number', metadata.get('page', 0)),
                'chunk_id': chunk['id'],
                'text_excerpt': chunk['content'][:100] + '...' if len(chunk['content']) > 100 else chunk['content'],
                'relevance_score': chunk.get('similarity', 0.0),
            }
            citations.append(citation)
        return citations
