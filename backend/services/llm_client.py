import os
import json
from typing import List, Dict, Optional
from datetime import datetime


class LLMClient:
    """LLM 客户端 - 支持 fallback 到规则提取"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.available = bool(self.api_key)
        self.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

    def extract_concepts(self, text: str, chapter_title: str) -> List[Dict]:
        """从文本中提取概念节点

        Args:
            text: 章节内容
            chapter_title: 章节标题

        Returns:
            概念节点列表，包含 name, definition, type
        """
        if not self.available:
            return self._fallback_extract_concepts(text, chapter_title)

        try:
            # TODO: 实现 LLM 调用 (e.g., OpenAI API)
            # 这里是占位符，实际项目中需要连接真实 LLM
            return self._fallback_extract_concepts(text, chapter_title)
        except Exception as e:
            print(f"LLM extraction failed: {e}, falling back to rule-based")
            return self._fallback_extract_concepts(text, chapter_title)

    def _fallback_extract_concepts_old(self, text: str, chapter_title: str) -> List[Dict]:
        """规则-based 概念提取（LLM 不可用时）

        提取策略：
        1. 提取加粗或强调的文本
        2. 按句子分割，找关键句子
        3. 提取代表性词汇
        """
        concepts = []

        # 策略1: 提取句子中的名词短语（简化）
        sentences = text.split('。')
        extracted = set()

        for i, sent in enumerate(sentences[:8]):  # 最多从前8句提取
            sent = sent.strip()
            if not sent or len(sent) < 5:
                continue

            # 简单启发式：找括号内的内容（通常是定义）
            if '（' in sent and '）' in sent:
                start = sent.index('（') + 1
                end = sent.index('）')
                concept = sent[start:end].strip()
                if concept and concept not in extracted:
                    concepts.append({
                        "name": concept,
                        "definition": sent,
                        "type": "concept"
                    })
                    extracted.add(concept)

            # 简单启发式：第一句通常包含主要概念
            if i == 0 and len(sent) > 10:
                words = sent.split()
                for j, word in enumerate(words[:5]):
                    word = word.strip('，。；：')
                    if len(word) >= 2 and word not in extracted:
                        concepts.append({
                            "name": word,
                            "definition": sent,
                            "type": "concept"
                        })
                        extracted.add(word)

        # 如果提取不到，用章节标题派生概念
        if not concepts:
            # 从标题中提取关键词
            title_words = chapter_title.split()
            for word in title_words[:3]:
                word = word.replace('第', '').replace('章', '').strip('0123456789')
                if len(word) >= 2:
                    concepts.append({
                        "name": word,
                        "definition": chapter_title,
                        "type": "concept"
                    })

        # 确保返回 5-8 个概念
        while len(concepts) < 5 and len(sentences) > 0:
            # 在不足时添加更多
            for sent in sentences[len(concepts):]:
                sent = sent.strip()
                if sent and len(sent) > 5:
                    words = sent.split('、')
                    for word in words[:2]:
                        word = word.strip()
                        if word and len(word) >= 2 and word not in extracted:
                            concepts.append({
                                "name": word,
                                "definition": sent,
                                "type": "concept"
                            })
                            extracted.add(word)
                            if len(concepts) >= 8:
                                break
                if len(concepts) >= 5:
                    break

        return concepts[:8]  # 最多 8 个

    def _fallback_extract_concepts(self, text: str, chapter_title: str) -> List[Dict]:
        """Fast bounded rule-based concept extraction used for demos."""
        if not text:
            return []

        normalized = (
            text.replace('\n', ' ')
            .replace('?', '。')
            .replace('!', '。')
            .replace('；', '。')
            .replace(';', '。')
        )
        sentences = [s.strip() for s in normalized.split('。') if len(s.strip()) >= 4]
        if not sentences:
            sentences = [normalized[:120].strip()] if normalized.strip() else [chapter_title]

        import re
        seeds = []
        if chapter_title:
            seeds.append((chapter_title.strip(), sentences[0]))

        for sent in sentences[:8]:
            for term in re.findall(r'[（(]([^）)）]{2,30})[）)]', sent):
                seeds.append((term.strip(), sent))
            for term in re.split(r'[，,、\s]+', sent)[:4]:
                term = term.strip(' ：:（）()《》0123456789')
                if 2 <= len(term) <= 24:
                    seeds.append((term, sent))

        concepts = []
        seen = set()
        for name, definition in seeds:
            if not name or name in seen:
                continue
            seen.add(name)
            concepts.append({
                "name": name,
                "definition": definition[:220],
                "type": "concept"
            })
            if len(concepts) >= 8:
                break

        while len(concepts) < 5 and sentences:
            name = f"{chapter_title or '知识点'}-{len(concepts) + 1}"
            if name in seen:
                break
            concepts.append({
                "name": name,
                "definition": sentences[min(len(concepts), len(sentences) - 1)][:220],
                "type": "concept"
            })
            seen.add(name)

        return concepts[:8]

    def extract_relations(self, concepts: List[Dict], text: str) -> List[Dict]:
        """从文本中提取概念间的关系

        Args:
            concepts: 概念列表
            text: 章节内容

        Returns:
            关系列表，包含 source, target, relation_type
        """
        if not self.available:
            return self._fallback_extract_relations(concepts, text)

        try:
            return self._fallback_extract_relations(concepts, text)
        except Exception as e:
            print(f"Relation extraction failed: {e}")
            return []

    def _fallback_extract_relations(self, concepts: List[Dict], text: str) -> List[Dict]:
        """规则-based 关系提取"""
        relations = []

        # 构建概念名称列表
        concept_names = [c['name'] for c in concepts]

        # 关键字规则
        prerequisite_keywords = ['需要', '首先', '基础', '前提', '基于', '依赖']
        contains_keywords = ['包括', '包含', '涵盖', '组成', '由']
        parallel_keywords = ['同时', '并且', '也', '和', '与']

        # 遍历文本，找关键字
        for i, concept in enumerate(concept_names):
            for j, other in enumerate(concept_names):
                if i == j:
                    continue

                # 检查两个概念是否在文本中接近
                concept_pos = text.find(concept)
                other_pos = text.find(other)

                if concept_pos < 0 or other_pos < 0:
                    continue

                distance = abs(concept_pos - other_pos)

                # 如果足够接近，检查中间是否有关键字
                if distance > 0 and distance < 100:
                    between_text = text[min(concept_pos, other_pos):max(concept_pos, other_pos)]

                    relation_type = "related"
                    if any(kw in between_text for kw in prerequisite_keywords):
                        relation_type = "prerequisite" if concept_pos < other_pos else "contained_by"
                    elif any(kw in between_text for kw in contains_keywords):
                        relation_type = "contains" if concept_pos < other_pos else "contained_by"
                    elif any(kw in between_text for kw in parallel_keywords):
                        relation_type = "parallel"

                    relations.append({
                        "source": concept,
                        "target": other,
                        "relation_type": relation_type,
                        "weight": max(0.5, 1.0 - distance / 100)
                    })

        # 同章内的节点默认有 contains 关系
        for i in range(len(concept_names)):
            for j in range(i + 1, min(i + 3, len(concept_names))):  # 最多连接后续两个
                if not any(r['source'] == concept_names[i] and r['target'] == concept_names[j]
                          for r in relations):
                    relations.append({
                        "source": concept_names[i],
                        "target": concept_names[j],
                        "relation_type": "contains",
                        "weight": 0.8
                    })

        return relations[:10]  # 最多 10 个关系
