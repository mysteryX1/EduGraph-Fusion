import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
from datetime import datetime
import uuid

from .llm_client import LLMClient


class KGExtractor:
    """知识图谱提取器 - 从教材章节中提取知识节点和关系"""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.metadata_dir = self.data_dir / "metadata"
        self.processed_dir = self.data_dir / "processed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        self.llm_client = LLMClient()
        self.nodes: Dict[str, Dict] = {}  # {node_id: node_data}
        self.edges: List[Dict] = []
        self.node_id_counter = 0

    def extract_all(self, textbook_ids: List[str] = None) -> Dict:
        """从所有教材提取知识图谱

        Args:
            textbook_ids: 要处理的教材 ID 列表。如果为 None，处理所有已解析教材。

        Returns:
            {'success': bool, 'nodes_count': int, 'edges_count': int}
        """
        try:
            # 如果没指定教材，自动发现
            if not textbook_ids:
                textbook_ids = self._discover_textbooks()

            self.nodes = {}
            self.edges = []

            # 从每本教材提取
            for textbook_id in textbook_ids:
                self._extract_from_textbook(textbook_id)

            # 构建节点间关系
            self._build_relationships()

            # 保存结果
            self._save_results()

            return {
                'success': True,
                'nodes_count': len(self.nodes),
                'edges_count': len(self.edges),
                'message': f'Extracted {len(self.nodes)} nodes and {len(self.edges)} edges'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Extraction failed: {str(e)}',
                'nodes_count': 0,
                'edges_count': 0
            }

    def _discover_textbooks(self) -> List[str]:
        """从 metadata 目录发现已解析的教材"""
        textbook_ids = set()

        for metadata_file in self.metadata_dir.glob("*_metadata.json"):
            # 文件名格式: {textbook_id}_metadata.json
            textbook_id = metadata_file.stem.replace('_metadata', '')
            # 验证对应的 chapters 文件存在
            chapters_file = self.metadata_dir / f"{textbook_id}_chapters.json"
            if chapters_file.exists():
                textbook_ids.add(textbook_id)

        return sorted(list(textbook_ids))

    def _extract_from_textbook(self, textbook_id: str) -> None:
        """从单个教材提取知识图谱

        Args:
            textbook_id: 教材 ID
        """
        # 加载元数据
        metadata_file = self.metadata_dir / f"{textbook_id}_metadata.json"
        chapters_file = self.metadata_dir / f"{textbook_id}_chapters.json"

        if not metadata_file.exists() or not chapters_file.exists():
            print(f"Textbook {textbook_id} files not found")
            return

        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            with open(chapters_file, 'r', encoding='utf-8') as f:
                chapters = json.load(f)

            textbook_title = metadata.get('title', textbook_id)

            # 最多处理前 5 章
            for chapter in chapters[:5]:
                self._extract_from_chapter(
                    chapter,
                    textbook_id,
                    textbook_title
                )

        except Exception as e:
            print(f"Error extracting from {textbook_id}: {e}")

    def _extract_from_chapter(self, chapter: Dict, textbook_id: str, textbook_title: str) -> None:
        """从单个章节提取知识节点

        Args:
            chapter: 章节数据
            textbook_id: 所属教材 ID
            textbook_title: 所属教材标题
        """
        chapter_id = chapter.get('id', f"{textbook_id}_ch_{chapter.get('chapter_num', 0)}")
        chapter_title = chapter.get('title', '')
        content = chapter.get('content', '')
        word_count = chapter.get('word_count', 0)

        if not content:
            return

        # 使用 LLM 或规则提取概念
        concepts = self.llm_client.extract_concepts(content, chapter_title)

        # 为每个概念创建节点
        chapter_nodes = []
        for concept in concepts:
            node_id = self._create_node(
                name=concept['name'],
                definition=concept.get('definition', concept['name']),
                node_type=concept.get('type', 'concept'),
                chapter=chapter_title,
                page=chapter.get('start_page', 1),
                source_textbook=textbook_title
            )
            chapter_nodes.append(node_id)

        # 提取章节内的关系
        if chapter_nodes:
            relations = self.llm_client.extract_relations(concepts, content)
            self._add_relations_from_extraction(relations, chapter_nodes)

    def _create_node(self, name: str, definition: str, node_type: str,
                    chapter: str, page: int, source_textbook: str) -> str:
        """创建知识图谱节点

        Args:
            name: 节点名称
            definition: 定义
            node_type: 节点类型
            chapter: 所属章节
            page: 页码
            source_textbook: 源教材

        Returns:
            节点 ID
        """
        # 检查是否已存在相同名称的节点
        for node_id, node_data in self.nodes.items():
            if node_data['name'] == name and node_data['source_textbook'] == source_textbook:
                # 更新频率
                node_data['frequency'] += 1
                if source_textbook not in node_data.get('sources', []):
                    node_data['sources'].append(source_textbook)
                return node_id

        # 创建新节点
        node_id = f"node_{self.node_id_counter}"
        self.node_id_counter += 1

        self.nodes[node_id] = {
            'id': node_id,
            'name': name,
            'type': node_type,
            'description': definition,
            'definition': definition,
            'chapter': chapter,
            'page': page,
            'source_textbook': source_textbook,
            'frequency': 1,
            'sources': [source_textbook]
        }

        return node_id

    def _add_relations_from_extraction(self, relations: List[Dict], node_ids: List[str]) -> None:
        """从提取的关系添加边

        Args:
            relations: 提取的关系列表
            node_ids: 相关节点 ID 列表
        """
        for relation in relations:
            source_name = relation.get('source', '')
            target_name = relation.get('target', '')

            # 找到对应的节点 ID
            source_id = None
            target_id = None

            for node_id in node_ids:
                if self.nodes[node_id]['name'] == source_name:
                    source_id = node_id
                if self.nodes[node_id]['name'] == target_name:
                    target_id = node_id

            if source_id and target_id:
                self._add_edge(
                    source_id=source_id,
                    target_id=target_id,
                    relation_type=relation.get('relation_type', 'related'),
                    weight=relation.get('weight', 0.8)
                )

    def _add_edge(self, source_id: str, target_id: str, relation_type: str, weight: float) -> None:
        """添加知识图谱边

        Args:
            source_id: 源节点 ID
            target_id: 目标节点 ID
            relation_type: 关系类型
            weight: 权重
        """
        # 检查是否已存在
        for edge in self.edges:
            if edge['source_id'] == source_id and edge['target_id'] == target_id:
                # 更新权重
                edge['weight'] = max(edge['weight'], weight)
                return

        self.edges.append({
            'source_id': source_id,
            'target_id': target_id,
            'relation_type': relation_type,
            'weight': weight,
            'confidence': weight
        })

    def _build_relationships(self) -> None:
        """构建节点间的关系（跨章节）"""
        # 同教材内的节点建立联系
        textbook_nodes = {}
        for node_id, node_data in self.nodes.items():
            tb = node_data['source_textbook']
            if tb not in textbook_nodes:
                textbook_nodes[tb] = []
            textbook_nodes[tb].append(node_id)

        # 同教材内频繁出现的节点连接
        for textbook, node_list in textbook_nodes.items():
            for i, node_id1 in enumerate(node_list):
                for node_id2 in node_list[i+1:i+3]:  # 只连接邻近的节点
                    # 检查是否已有边
                    has_edge = any(
                        e['source_id'] == node_id1 and e['target_id'] == node_id2
                        for e in self.edges
                    )
                    if not has_edge:
                        self._add_edge(
                            source_id=node_id1,
                            target_id=node_id2,
                            relation_type='parallel',
                            weight=0.5
                        )

    def _save_results(self) -> None:
        """保存提取结果到 JSON 文件"""
        # 保存节点
        nodes_list = list(self.nodes.values())
        nodes_file = self.processed_dir / "kg_nodes.json"
        with open(nodes_file, 'w', encoding='utf-8') as f:
            json.dump(nodes_list, f, ensure_ascii=False, indent=2)

        # 保存边
        edges_file = self.processed_dir / "kg_edges.json"
        with open(edges_file, 'w', encoding='utf-8') as f:
            json.dump(self.edges, f, ensure_ascii=False, indent=2)

    def get_kg_data(self) -> Dict:
        """获取知识图谱数据

        Returns:
            包含 nodes 和 edges 的字典
        """
        # 从文件加载
        nodes_file = self.processed_dir / "kg_nodes.json"
        edges_file = self.processed_dir / "kg_edges.json"

        nodes = []
        edges = []

        if nodes_file.exists():
            with open(nodes_file, 'r', encoding='utf-8') as f:
                nodes = json.load(f)

        if edges_file.exists():
            with open(edges_file, 'r', encoding='utf-8') as f:
                edges = json.load(f)

        return {
            'nodes': nodes,
            'edges': edges,
            'node_count': len(nodes),
            'edge_count': len(edges)
        }
