# 知识图谱与合并模块实现指南

## 概述

本文档描述 EduGraph Fusion 项目的知识图谱（KG）和节点合并（Merge）模块的完整实现，包括：

- **KG 提取**：从已解析教材中自动提取知识节点和关系
- **节点合并**：检测和合并相似的知识节点，降低冗余

## 架构设计

### 文件结构

```
backend/
├── services/
│   ├── llm_client.py          # LLM 客户端 (支持 fallback)
│   ├── kg_extractor.py        # 知识图谱提取器
│   ├── merger.py              # 节点合并器
│   └── __init__.py            # (已更新)
├── routers/
│   ├── kg.py                  # KG 路由
│   ├── merge.py               # Merge 路由
│   └── __init__.py            # (已更新)
└── main.py                    # (已更新，添加路由)

data/
├── metadata/                  # 已解析教材元数据
│   ├── {textbook_id}_metadata.json
│   └── {textbook_id}_chapters.json
└── processed/                 # 处理结果
    ├── kg_nodes.json          # 提取的知识节点
    ├── kg_edges.json          # 提取的知识关系
    ├── merged_kg.json         # 合并后的完整知识图谱
    └── merge_decisions.json   # 合并决策记录
```

## 核心模块说明

### 1. LLMClient (`backend/services/llm_client.py`)

**职责**：提供 LLM 能力，当 LLM 不可用时自动降级到规则-based 提取。

**关键方法**：

```python
# 概念提取
concepts = llm_client.extract_concepts(text, chapter_title)
# 返回: [{'name': str, 'definition': str, 'type': str}, ...]

# 关系提取
relations = llm_client.extract_relations(concepts, text)
# 返回: [{'source': str, 'target': str, 'relation_type': str, 'weight': float}, ...]
```

**特性**：

- 自动 fallback：检查 LLM_API_KEY 环境变量，不存在时使用规则
- 规则-based 提取：
  - 括号内的内容识别为定义
  - 关键词重叠度量
  - 句子相近性评分
  - 从章节标题派生概念

### 2. KGExtractor (`backend/services/kg_extractor.py`)

**职责**：从已解析教材中提取知识图谱。

**工作流程**：

```
1. 发现教材 (discover_textbooks)
   └─ 扫描 ./data/metadata/ 找出 {id}_metadata.json 文件

2. 逐教材处理 (extract_from_textbook)
   ├─ 加载元数据和章节
   └─ 最多处理前 5 章

3. 逐章节提取 (extract_from_chapter)
   ├─ 用 LLMClient 提取概念 (5-8 个)
   ├─ 为每个概念创建节点
   └─ 提取概念间的关系

4. 构建跨章节关系 (build_relationships)
   └─ 同教材内的节点建立联系

5. 保存结果 (save_results)
   ├─ kg_nodes.json
   └─ kg_edges.json
```

**节点格式**：

```json
{
  "id": "node_0",
  "name": "函数",
  "type": "concept",
  "description": "函数是一种数学关系...",
  "definition": "同 description",
  "chapter": "第1章 集合与函数",
  "page": 1,
  "source_textbook": "高中数学基础",
  "frequency": 3,
  "sources": ["高中数学基础", "高中物理基础"]
}
```

**边格式**：

```json
{
  "source_id": "node_0",
  "target_id": "node_1",
  "relation_type": "contains|prerequisite|parallel|related",
  "weight": 0.85,
  "confidence": 0.85
}
```

### 3. NodeMerger (`backend/services/merger.py`)

**职责**：检测和合并重复节点，优化知识图谱。

**相似度计算**：

```
总相似度 = 名称相似度 × 0.4 + 关键词重叠 × 0.35 + 文本相似度 × 0.25

其中：
- 名称相似度：编辑距离 / 最大长度
- 关键词重叠：Jaccard 指数
- 文本相似度：简化的 TF 向量余弦相似度
```

**合并决策规则**：

| 相似度范围 | 决策 | 说明 |
|---------|------|------|
| ≥ 0.82 | merge | 直接合并到第一个节点 |
| 0.65-0.82 | possible_duplicate | 标记为可能重复，人工审核 |
| < 0.65 | keep | 保留两个节点 |

**合并流程**：

```
1. 加载 KG 数据 (load_kg_data)
2. 找出相似节点对 (find_similar_nodes)
3. 生成合并决策 (generate_merge_decisions)
4. 执行合并 (apply_merges)
   ├─ 删除重复节点
   ├─ 合并频率
   ├─ 合并来源
   ├─ 更新边指向
   └─ 删除自环和重复边
5. 确保压缩比 ≤ 0.30 (truncate_definitions)
6. 保存结果
```

**输出统计**：

```json
{
  "original_nodes": 45,
  "merged_nodes": 38,
  "merged_count": 5,
  "possible_duplicate_count": 2,
  "original_chars": 15000,
  "merged_chars": 4200,
  "compression_ratio": 0.28
}
```

## API 端点

### 1. POST /api/kg/build

**功能**：构建知识图谱

**请求**：
```bash
curl -X POST http://localhost:8000/api/kg/build \
  -H "Content-Type: application/json" \
  -d '{
    "textbook_ids": ["textbook_math_001", "textbook_physics_001"]
  }'
```

如果 `textbook_ids` 为空或未提供，将处理所有已解析教材。

**响应** (成功)：
```json
{
  "status": "success",
  "message": "Knowledge graph built successfully",
  "data": {
    "nodes_count": 45,
    "edges_count": 68,
    "textbooks_processed": 2
  }
}
```

**响应** (失败)：
```json
{
  "status": "error",
  "message": "Failed to build knowledge graph: ...",
  "path": "/api/kg/build"
}
```

### 2. GET /api/kg

**功能**：获取已构建的知识图谱

**请求**：
```bash
curl http://localhost:8000/api/kg
```

**响应**：
```json
{
  "status": "success",
  "message": "Knowledge graph retrieved successfully",
  "data": {
    "nodes": [
      {
        "id": "node_0",
        "name": "函数",
        "type": "concept",
        ...
      }
    ],
    "edges": [
      {
        "source_id": "node_0",
        "target_id": "node_1",
        ...
      }
    ],
    "node_count": 45,
    "edge_count": 68
  }
}
```

### 3. POST /api/merge

**功能**：合并知识图谱中的重复节点

**请求**：
```bash
curl -X POST http://localhost:8000/api/merge \
  -H "Content-Type: application/json" \
  -d '{}'
```

**响应**：
```json
{
  "status": "success",
  "message": "Graphs merged successfully",
  "data": {
    "merged_count": 5,
    "removed_count": 0,
    "possible_duplicate_count": 2,
    "kept_count": 36,
    "original_nodes": 45,
    "merged_nodes": 38,
    "original_chars": 15000,
    "merged_chars": 4200,
    "compression_ratio": 0.28
  }
}
```

### 4. GET /api/merge/decisions

**功能**：获取所有合并决策

**请求**：
```bash
curl http://localhost:8000/api/merge/decisions
```

**响应**：
```json
{
  "status": "success",
  "message": "Merge decisions retrieved successfully",
  "data": {
    "decisions": [
      {
        "node_id1": "node_0",
        "node_id2": "node_5",
        "similarity": 0.87,
        "decision": "merge",
        "timestamp": "2024-05-10T15:30:45.123456"
      },
      {
        "node_id1": "node_3",
        "node_id2": "node_8",
        "similarity": 0.73,
        "decision": "possible_duplicate",
        "timestamp": "2024-05-10T15:30:45.234567"
      }
    ],
    "statistics": {
      "merge": 5,
      "possible_duplicate": 2,
      "keep": 36,
      "total": 43
    }
  }
}
```

## 使用指南

### 步骤 1：准备教材数据

教材必须通过以下步骤预处理：

1. 上传教材文件：`POST /api/upload`
2. 解析教材：`POST /api/parse/{textbook_id}`

解析后，数据保存在 `./data/metadata/` 目录：
- `{textbook_id}_metadata.json`
- `{textbook_id}_chapters.json`

### 步骤 2：运行 KG 提取

```bash
curl -X POST http://localhost:8000/api/kg/build
```

生成的文件：
- `./data/processed/kg_nodes.json` - 知识节点
- `./data/processed/kg_edges.json` - 知识关系

### 步骤 3：运行 Merge

```bash
curl -X POST http://localhost:8000/api/merge
```

生成的文件：
- `./data/processed/merged_kg.json` - 合并后的知识图谱
- `./data/processed/merge_decisions.json` - 合并决策

### 步骤 4：查询结果

```bash
# 获取知识图谱
curl http://localhost:8000/api/kg

# 获取合并决策
curl http://localhost:8000/api/merge/decisions
```

## 测试

### 使用示例数据测试

1. **生成测试数据**：
```bash
python generate_test_data.py
```

这将创建 2 个样本教材（数学和物理），共 10 个章节。

2. **启动 API 服务**：
```bash
python -m backend.main
```

3. **运行 API 测试**：
```bash
# 构建 KG
curl -X POST http://localhost:8000/api/kg/build

# 获取 KG
curl http://localhost:8000/api/kg

# 合并
curl -X POST http://localhost:8000/api/merge

# 获取合并决策
curl http://localhost:8000/api/merge/decisions
```

或运行脚本测试：
```bash
bash test_api_kg_merge.sh
```

## 性能考虑

### 节点提取

- **每本教材最多处理前 5 章**：避免处理过多数据
- **每章提取 5-8 个概念**：平衡覆盖面和噪音
- **内存高效**：逐章处理，不一次性加载全部

### 节点合并

- **相似度计算**：O(n²) 复杂度，1000 个节点需要约 100 万次比较
- **推荐压缩比**：0.20-0.30 为最佳（减少冗余，保留多样性）
- **截断定义**：当压缩比 > 0.30 时自动截断定义

## 环境变量

```bash
# LLM 配置（可选）
export LLM_API_KEY="your-api-key"
export LLM_MODEL="gpt-3.5-turbo"

# 数据目录
export DATA_DIR="./data"
```

## 常见问题

### Q: 没有 LLM_API_KEY 时会怎样？

A: 系统自动降级到规则-based 提取，功能完整，只是准确度可能略低。

### Q: 如何调整合并的严格程度？

A: 修改 `merger.py` 中的相似度阈值：
- 提高 0.82 阈值：减少自动合并，更保守
- 降低 0.65 阈值：减少人工审核项

### Q: 如何检查压缩比是否满足要求？

A: 检查 `POST /api/merge` 的响应中的 `compression_ratio` 字段，应该 ≤ 0.30。

## 输出文件详解

### kg_nodes.json

知识节点列表，每个节点包含：

```json
[
  {
    "id": "node_0",
    "name": "函数",
    "type": "concept",
    "description": "函数是一种数学关系...",
    "definition": "函数是一种数学关系...",
    "chapter": "第1章 集合与函数",
    "page": 1,
    "source_textbook": "高中数学基础",
    "frequency": 3,
    "sources": ["高中数学基础"]
  }
]
```

### kg_edges.json

知识关系列表，每条边包含：

```json
[
  {
    "source_id": "node_0",
    "target_id": "node_1",
    "relation_type": "contains",
    "weight": 0.85,
    "confidence": 0.85
  }
]
```

### merged_kg.json

合并后的完整知识图谱：

```json
{
  "nodes": [...],
  "edges": [...],
  "timestamp": "2024-05-10T15:30:45.123456"
}
```

### merge_decisions.json

详细的合并决策记录：

```json
[
  {
    "node_id1": "node_0",
    "node_id2": "node_5",
    "similarity": 0.87,
    "decision": "merge",
    "timestamp": "2024-05-10T15:30:45.123456"
  }
]
```

## 总结

该实现提供了：

✅ 完整的知识图谱提取流程
✅ 智能的节点相似度检测
✅ 自动化的合并决策
✅ LLM fallback 机制
✅ 压缩比控制
✅ RESTful API 接口
✅ 完整的错误处理

所有功能已集成到 FastAPI 框架中，可直接投入使用。
