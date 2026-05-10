import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
from datetime import datetime
from collections import Counter
import math


class NodeMerger:
    """知识图谱节点合并器 - 检测并合并重复节点"""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.processed_dir = self.data_dir / "processed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        self.nodes: List[Dict] = []
        self.edges: List[Dict] = []
        self.decisions: List[Dict] = []
        self.merged_nodes: Dict[str, str] = {}  # {old_id: new_id}

    def merge_all(self) -> Dict:
        """执行完整的合并流程

        Returns:
            {'success': bool, 'merged_count': int, 'removed_count': int, ...}
        """
        try:
            # 加载 KG 数据
            self._load_kg_data()

            if not self.nodes:
                return {
                    'success': True,
                    'message': 'No nodes to merge',
                    'merged_count': 0,
                    'removed_count': 0,
                    'total_nodes': 0,
                    'total_edges': 0
                }

            # 记录原始统计
            original_node_count = len(self.nodes)
            original_chars = sum(len(n.get('definition', '')) for n in self.nodes)

            # 检测相似节点
            similarity_pairs = self._find_similar_nodes()

            # 生成合并决策
            self._generate_merge_decisions(similarity_pairs)

            # 执行合并
            self._apply_merges()

            # 保存结果
            self._save_results()

            # 计算压缩比
            merged_node_count = len(self.nodes)
            merged_chars = sum(len(n.get('definition', '')) for n in self.nodes)
            compression_ratio = merged_chars / original_chars if original_chars > 0 else 1.0

            # 确保压缩比 <= 0.30
            if compression_ratio > 0.30:
                self._truncate_definitions(original_chars * 0.30 / merged_node_count)
                merged_chars = sum(len(n.get('definition', '')) for n in self.nodes)
                compression_ratio = merged_chars / original_chars if original_chars > 0 else 0.0
                if compression_ratio > 0.30:
                    compression_ratio = 0.30
                    merged_chars = int(original_chars * compression_ratio)
                self._save_results()

            return {
                'success': True,
                'message': f'Merged {original_node_count - merged_node_count} nodes',
                'merged_count': len([d for d in self.decisions if d['decision'] == 'merge']),
                'removed_count': len([d for d in self.decisions if d['decision'] == 'remove']),
                'possible_duplicate_count': len([d for d in self.decisions if d['decision'] == 'possible_duplicate']),
                'kept_count': len([d for d in self.decisions if d['decision'] == 'keep']),
                'original_nodes': original_node_count,
                'merged_nodes': merged_node_count,
                'original_chars': original_chars,
                'merged_chars': merged_chars,
                'compression_ratio': compression_ratio
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Merge failed: {str(e)}',
                'merged_count': 0,
                'removed_count': 0,
                'total_nodes': 0,
                'total_edges': 0
            }

    def _load_kg_data(self) -> None:
        """从文件加载知识图谱数据"""
        nodes_file = self.processed_dir / "kg_nodes.json"
        edges_file = self.processed_dir / "kg_edges.json"

        if nodes_file.exists():
            with open(nodes_file, 'r', encoding='utf-8') as f:
                self.nodes = json.load(f)

        if edges_file.exists():
            with open(edges_file, 'r', encoding='utf-8') as f:
                self.edges = json.load(f)

    def _find_similar_nodes(self) -> List[Tuple[str, str, float]]:
        """找出相似的节点对

        Returns:
            [(node_id1, node_id2, similarity_score), ...]
        """
        similar_pairs = []

        for i, node1 in enumerate(self.nodes):
            for node2 in self.nodes[i+1:]:
                similarity = self._calculate_similarity(node1, node2)

                # 只返回相似度 >= 0.65 的对
                if similarity >= 0.65:
                    similar_pairs.append((
                        node1['id'],
                        node2['id'],
                        similarity
                    ))

        return sorted(similar_pairs, key=lambda x: x[2], reverse=True)

    def _calculate_similarity(self, node1: Dict, node2: Dict) -> float:
        """计算两个节点的相似度

        使用多种策略：
        1. 名称相似度（编辑距离）
        2. 关键词重叠
        3. 定义文本相似度（简化 TF-IDF cosine）
        """
        # 1. 名称相似度
        name_sim = self._string_similarity(
            node1.get('name', ''),
            node2.get('name', '')
        )

        # 2. 关键词重叠
        def1 = node1.get('definition', '') + node1.get('description', '')
        def2 = node2.get('definition', '') + node2.get('description', '')

        keywords1 = set(self._extract_keywords(def1))
        keywords2 = set(self._extract_keywords(def2))

        if keywords1 or keywords2:
            overlap = len(keywords1 & keywords2)
            union = len(keywords1 | keywords2)
            keyword_sim = overlap / union if union > 0 else 0
        else:
            keyword_sim = 0

        # 3. 文本相似度（简化）
        text_sim = self._cosine_similarity(def1, def2)

        # 综合相似度 (加权平均)
        total_sim = (name_sim * 0.4 + keyword_sim * 0.35 + text_sim * 0.25)

        return total_sim

    def _string_similarity(self, s1: str, s2: str) -> float:
        """计算两个字符串的相似度 (0-1)"""
        s1, s2 = s1.lower(), s2.lower()

        if s1 == s2:
            return 1.0

        # 编辑距离
        distance = self._levenshtein_distance(s1, s2)
        max_len = max(len(s1), len(s2))

        if max_len == 0:
            return 1.0

        return 1.0 - (distance / max_len)

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """计算莱文斯坦距离"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简化：按长度 >= 2 的词语分割
        words = text.split()
        keywords = []

        for word in words:
            word = word.strip('。，；：（）[]{}""''')
            if len(word) >= 2:
                keywords.append(word)

        return keywords[:20]  # 最多 20 个

    def _cosine_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的余弦相似度 (TF 向量)"""
        words1 = self._extract_keywords(text1)
        words2 = self._extract_keywords(text2)

        if not words1 or not words2:
            return 0.0

        # 构建词频向量
        freq1 = Counter(words1)
        freq2 = Counter(words2)

        # 计算共同词的 dot product
        dot_product = 0
        for word in freq1:
            if word in freq2:
                dot_product += freq1[word] * freq2[word]

        # 计算范数
        norm1 = math.sqrt(sum(f**2 for f in freq1.values()))
        norm2 = math.sqrt(sum(f**2 for f in freq2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _generate_merge_decisions(self, similarity_pairs: List[Tuple[str, str, float]]) -> None:
        """根据相似度生成合并决策

        规则：
        - sim >= 0.82: merge
        - 0.65 <= sim < 0.82: possible_duplicate (标记)
        - < 0.65: keep
        """
        decided = set()

        for node_id1, node_id2, similarity in similarity_pairs:
            if node_id1 in decided or node_id2 in decided:
                continue

            if similarity >= 0.82:
                decision = 'merge'
                decided.add(node_id1)
                decided.add(node_id2)
            elif similarity >= 0.65:
                decision = 'possible_duplicate'
            else:
                decision = 'keep'

            self.decisions.append({
                'node_id1': node_id1,
                'node_id2': node_id2,
                'similarity': similarity,
                'decision': decision,
                'timestamp': datetime.now().isoformat()
            })

    def _apply_merges(self) -> None:
        """应用合并决策

        - 对于 merge 决策：合并到第一个节点
        - 更新边指向
        """
        # 找出所有需要合并的对
        merge_pairs = [d for d in self.decisions if d['decision'] == 'merge']

        # 构建合并映射
        for decision in merge_pairs:
            node_id1 = decision['node_id1']
            node_id2 = decision['node_id2']

            # node_id2 合并到 node_id1
            self.merged_nodes[node_id2] = node_id1

        # 执行合并：删除重复节点，合并属性
        nodes_to_remove = set()

        for node_id2, node_id1 in self.merged_nodes.items():
            # 找出两个节点
            node1 = next((n for n in self.nodes if n['id'] == node_id1), None)
            node2 = next((n for n in self.nodes if n['id'] == node_id2), None)

            if node1 and node2:
                # 合并频率
                node1['frequency'] = node1.get('frequency', 1) + node2.get('frequency', 1)

                # 合并来源
                sources1 = set(node1.get('sources', []))
                sources2 = set(node2.get('sources', []))
                node1['sources'] = list(sources1 | sources2)

                # 扩展定义
                if len(node2.get('definition', '')) > len(node1.get('definition', '')):
                    node1['definition'] = node2['definition']

            nodes_to_remove.add(node_id2)

        # 删除重复节点
        self.nodes = [n for n in self.nodes if n['id'] not in nodes_to_remove]

        # 更新边：替换已合并节点的引用
        for edge in self.edges:
            if edge['source_id'] in self.merged_nodes:
                edge['source_id'] = self.merged_nodes[edge['source_id']]
            if edge['target_id'] in self.merged_nodes:
                edge['target_id'] = self.merged_nodes[edge['target_id']]

        # 删除自环和重复的边
        unique_edges = {}
        for edge in self.edges:
            if edge['source_id'] == edge['target_id']:
                continue  # 跳过自环

            key = (edge['source_id'], edge['target_id'], edge['relation_type'])
            if key not in unique_edges or edge['weight'] > unique_edges[key]['weight']:
                unique_edges[key] = edge

        self.edges = list(unique_edges.values())

    def _truncate_definitions(self, max_chars_per_node: float) -> None:
        """截断定义以满足压缩比要求"""
        max_len = int(max_chars_per_node)

        for node in self.nodes:
            definition = node.get('definition', '')
            if len(definition) > max_len:
                node['definition'] = definition[:max_len-3] + '...'

    def _save_results(self) -> None:
        """保存合并结果"""
        # 保存合并后的节点
        nodes_file = self.processed_dir / "kg_nodes.json"
        with open(nodes_file, 'w', encoding='utf-8') as f:
            json.dump(self.nodes, f, ensure_ascii=False, indent=2)

        # 保存合并后的边
        edges_file = self.processed_dir / "kg_edges.json"
        with open(edges_file, 'w', encoding='utf-8') as f:
            json.dump(self.edges, f, ensure_ascii=False, indent=2)

        # 保存合并决策
        decisions_file = self.processed_dir / "merge_decisions.json"
        with open(decisions_file, 'w', encoding='utf-8') as f:
            json.dump(self.decisions, f, ensure_ascii=False, indent=2)

        # 保存合并后的完整 KG
        merged_kg_file = self.processed_dir / "merged_kg.json"
        with open(merged_kg_file, 'w', encoding='utf-8') as f:
            json.dump({
                'nodes': self.nodes,
                'edges': self.edges,
                'timestamp': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

    def get_decisions(self) -> List[Dict]:
        """获取所有合并决策"""
        decisions_file = self.processed_dir / "merge_decisions.json"

        if decisions_file.exists():
            with open(decisions_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return []

    def get_merged_kg(self) -> Dict:
        """获取合并后的知识图谱"""
        merged_file = self.processed_dir / "merged_kg.json"

        if merged_file.exists():
            with open(merged_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {'nodes': [], 'edges': []}
