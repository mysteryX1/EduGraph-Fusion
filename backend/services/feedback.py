# -*- coding: utf-8 -*-
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class FeedbackProcessor:
    """处理教师反馈，修改知识图谱决策"""

    def __init__(self, data_dir: str = "./data/processed"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.merge_decisions = self._load_merge_decisions()
        self.merged_kg = self._load_merged_kg()

    def _load_merge_decisions(self) -> Dict:
        """加载合并决策文件"""
        decisions_file = self.data_dir / "merge_decisions.json"
        if decisions_file.exists():
            with open(decisions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                return {
                    'decisions': data,
                    'updated_at': datetime.now().isoformat()
                }
            if isinstance(data, dict):
                data.setdefault('decisions', [])
                data.setdefault('updated_at', datetime.now().isoformat())
                return data
        return {
            'decisions': [],
            'updated_at': datetime.now().isoformat()
        }

    def _load_merged_kg(self) -> Dict:
        """加载合并后的知识图谱"""
        kg_file = self.data_dir / "merged_kg.json"
        if kg_file.exists():
            with open(kg_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'nodes': [],
            'edges': [],
            'updated_at': datetime.now().isoformat()
        }

    def _save_merge_decisions(self):
        """保存合并决策"""
        decisions_file = self.data_dir / "merge_decisions.json"
        self.merge_decisions['updated_at'] = datetime.now().isoformat()
        with open(decisions_file, 'w', encoding='utf-8') as f:
            json.dump(self.merge_decisions, f, ensure_ascii=False, indent=2)

    def _save_merged_kg(self):
        """保存合并后的知识图谱"""
        kg_file = self.data_dir / "merged_kg.json"
        self.merged_kg['updated_at'] = datetime.now().isoformat()
        with open(kg_file, 'w', encoding='utf-8') as f:
            json.dump(self.merged_kg, f, ensure_ascii=False, indent=2)

    def process_instruction(self, instruction: str) -> Dict:
        """处理自然语言指令

        支持的指令格式：
        - "保留 XXX" - 保留指定内容
        - "删除 XXX" - 删除指定内容
        - "拆分 XXX 和 YYY" - 拆分两个内容
        - "合并 XXX 和 YYY" - 合并两个内容

        Args:
            instruction: 自然语言指令

        Returns:
            处理结果
        """
        instruction = instruction.strip()
        summary = []

        # 保留指令
        keep_match = re.match(r'保留\s+(.+?)(?:\s+|$)', instruction)
        if keep_match:
            target = keep_match.group(1)
            result = self._handle_keep(target)
            summary.append(result)
            return {
                'success': True,
                'instruction': instruction,
                'action': 'keep',
                'target': target,
                'summary': result
            }

        # 删除指令
        delete_match = re.match(r'删除\s+(.+?)(?:\s+|$)', instruction)
        if delete_match:
            target = delete_match.group(1)
            result = self._handle_delete(target)
            summary.append(result)
            return {
                'success': True,
                'instruction': instruction,
                'action': 'delete',
                'target': target,
                'summary': result
            }

        # 拆分指令
        split_match = re.match(r'拆分\s+(.+?)\s+和\s+(.+?)(?:\s+|$)', instruction)
        if split_match:
            source = split_match.group(1)
            target = split_match.group(2)
            result = self._handle_split(source, target)
            summary.append(result)
            return {
                'success': True,
                'instruction': instruction,
                'action': 'split',
                'source': source,
                'target': target,
                'summary': result
            }

        # 合并指令
        merge_match = re.match(r'合并\s+(.+?)\s+和\s+(.+?)(?:\s+|$)', instruction)
        if merge_match:
            source = merge_match.group(1)
            target = merge_match.group(2)
            result = self._handle_merge(source, target)
            summary.append(result)
            return {
                'success': True,
                'instruction': instruction,
                'action': 'merge',
                'source': source,
                'target': target,
                'summary': result
            }

        return {
            'success': False,
            'instruction': instruction,
            'message': 'Unsupported instruction format. Supported: 保留/删除/拆分/合并'
        }

    def _handle_keep(self, target: str) -> str:
        """处理保留指令"""
        # 在合并决策中标记为保留
        decision = {
            'action': 'keep',
            'target': target,
            'timestamp': datetime.now().isoformat()
        }

        if 'decisions' not in self.merge_decisions:
            self.merge_decisions['decisions'] = []

        self.merge_decisions['decisions'].append(decision)
        self._save_merge_decisions()

        return f"已标记保留：{target}"

    def _handle_delete(self, target: str) -> str:
        """处理删除指令"""
        # 从 KG 中删除指定节点
        if 'nodes' in self.merged_kg:
            original_count = len(self.merged_kg['nodes'])
            self.merged_kg['nodes'] = [
                node for node in self.merged_kg['nodes']
                if target not in node.get('name', '')
            ]
            deleted_count = original_count - len(self.merged_kg['nodes'])

        # 删除相关边
        if 'edges' in self.merged_kg:
            original_edge_count = len(self.merged_kg['edges'])
            self.merged_kg['edges'] = [
                edge for edge in self.merged_kg['edges']
                if target not in [
                    edge.get('source_id', ''),
                    edge.get('target_id', '')
                ]
            ]
            deleted_edge_count = original_edge_count - len(self.merged_kg['edges'])

        # 记录决策
        decision = {
            'action': 'delete',
            'target': target,
            'deleted_nodes': deleted_count,
            'deleted_edges': deleted_edge_count,
            'timestamp': datetime.now().isoformat()
        }

        if 'decisions' not in self.merge_decisions:
            self.merge_decisions['decisions'] = []

        self.merge_decisions['decisions'].append(decision)
        self._save_merged_kg()
        self._save_merge_decisions()

        return f"已删除：{target}（删除节点数：{deleted_count}, 删除边数：{deleted_edge_count}）"

    def _handle_split(self, source: str, target: str) -> str:
        """处理拆分指令"""
        # 在 KG 中拆分节点（创建新节点，保持原节点）
        decision = {
            'action': 'split',
            'source': source,
            'target': target,
            'timestamp': datetime.now().isoformat()
        }

        # 尝试找到源节点并创建新节点
        new_node_id = f"{target}_{datetime.now().timestamp()}"
        new_node = {
            'id': new_node_id,
            'name': target,
            'type': 'concept',
            'description': f'从 {source} 拆分出来'
        }

        if 'nodes' in self.merged_kg:
            self.merged_kg['nodes'].append(new_node)

        if 'decisions' not in self.merge_decisions:
            self.merge_decisions['decisions'] = []

        self.merge_decisions['decisions'].append(decision)
        self._save_merged_kg()
        self._save_merge_decisions()

        return f"已拆分：{source} -> {target}（新建节点 ID：{new_node_id}）"

    def _handle_merge(self, source: str, target: str) -> str:
        """处理合并指令"""
        # 在 KG 中合并两个节点
        decision = {
            'action': 'merge',
            'source': source,
            'target': target,
            'timestamp': datetime.now().isoformat()
        }

        # 找到源节点并重定向关系
        source_node_id = None
        target_node_id = None

        if 'nodes' in self.merged_kg:
            for node in self.merged_kg['nodes']:
                if source in node.get('name', ''):
                    source_node_id = node.get('id')
                if target in node.get('name', ''):
                    target_node_id = node.get('id')

            # 删除源节点
            if source_node_id:
                self.merged_kg['nodes'] = [
                    node for node in self.merged_kg['nodes']
                    if node.get('id') != source_node_id
                ]

        # 重定向边
        if 'edges' in self.merged_kg and source_node_id and target_node_id:
            for edge in self.merged_kg['edges']:
                if edge.get('source_id') == source_node_id:
                    edge['source_id'] = target_node_id
                if edge.get('target_id') == source_node_id:
                    edge['target_id'] = target_node_id

            # 删除重复边
            seen_edges = set()
            unique_edges = []
            for edge in self.merged_kg['edges']:
                edge_key = (edge.get('source_id'), edge.get('target_id'), edge.get('relation_type'))
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    unique_edges.append(edge)
            self.merged_kg['edges'] = unique_edges

        if 'decisions' not in self.merge_decisions:
            self.merge_decisions['decisions'] = []

        self.merge_decisions['decisions'].append(decision)
        self._save_merged_kg()
        self._save_merge_decisions()

        return f"已合并：{source} -> {target}"

    def get_feedback_summary(self) -> Dict:
        """获取反馈摘要"""
        decisions = self.merge_decisions.get('decisions', [])

        summary = {
            'total_decisions': len(decisions),
            'keep_count': sum(1 for d in decisions if d.get('action') == 'keep'),
            'delete_count': sum(1 for d in decisions if d.get('action') == 'delete'),
            'split_count': sum(1 for d in decisions if d.get('action') == 'split'),
            'merge_count': sum(1 for d in decisions if d.get('action') == 'merge'),
            'kg_nodes': len(self.merged_kg.get('nodes', [])),
            'kg_edges': len(self.merged_kg.get('edges', [])),
            'last_updated': self.merge_decisions.get('updated_at')
        }

        return summary
