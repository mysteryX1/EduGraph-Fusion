# 知识图谱与合并模块快速开始

## ⚡ 5分钟快速开始

### 方式 1：直接运行集成测试（推荐）

```bash
# 一条命令，生成数据并运行完整测试
python run_full_test.py
```

输出示例：
```
【步骤 1】生成测试教材数据
✅ 创建了 2 本教材，共 10 个章节

【步骤 2】验证模块导入
✅ 所有模块导入成功

【步骤 3】测试知识图谱提取
✅ 知识图谱提取成功
   • 节点数: 42
   • 边数: 58

【步骤 4】测试节点合并
✅ 节点合并成功
   • 原始节点数: 42
   • 合并后节点数: 38
   • 合并数: 3
   • 压缩比: 0.2847

【步骤 5】验证输出文件
✅ kg_nodes.json ...
✅ kg_edges.json ...
✅ merged_kg.json ...
✅ merge_decisions.json ...
```

### 方式 2：启动 API 并测试

```bash
# 1. 启动服务
python -m backend.main

# 2. 新开终端，测试接口
curl -X POST http://localhost:8000/api/kg/build
curl http://localhost:8000/api/kg
curl -X POST http://localhost:8000/api/merge
curl http://localhost:8000/api/merge/decisions
```

## 📖 核心 API

### 1️⃣ 构建知识图谱

```bash
curl -X POST http://localhost:8000/api/kg/build
```

**功能**：从已解析教材中提取知识节点和关系

**响应示例**：
```json
{
  "status": "success",
  "data": {
    "nodes_count": 42,
    "edges_count": 58,
    "textbooks_processed": 2
  }
}
```

### 2️⃣ 获取知识图谱

```bash
curl http://localhost:8000/api/kg
```

**功能**：返回所有知识节点和边

**响应格式**：
```json
{
  "status": "success",
  "data": {
    "nodes": [
      {
        "id": "node_0",
        "name": "函数",
        "type": "concept",
        "definition": "...",
        "chapter": "第1章",
        "page": 5,
        "source_textbook": "高中数学基础",
        "frequency": 3,
        "sources": ["高中数学基础"]
      }
    ],
    "edges": [...],
    "node_count": 42,
    "edge_count": 58
  }
}
```

### 3️⃣ 合并知识图谱

```bash
curl -X POST http://localhost:8000/api/merge
```

**功能**：检测和合并相似节点，优化图结构

**响应示例**：
```json
{
  "status": "success",
  "data": {
    "merged_count": 3,
    "possible_duplicate_count": 2,
    "original_nodes": 42,
    "merged_nodes": 38,
    "compression_ratio": 0.2847
  }
}
```

### 4️⃣ 获取合并决策

```bash
curl http://localhost:8000/api/merge/decisions
```

**功能**：查看所有合并决策和相似度信息

**响应格式**：
```json
{
  "status": "success",
  "data": {
    "decisions": [
      {
        "node_id1": "node_0",
        "node_id2": "node_5",
        "similarity": 0.87,
        "decision": "merge"
      }
    ],
    "statistics": {
      "merge": 3,
      "possible_duplicate": 2,
      "keep": 36,
      "total": 41
    }
  }
}
```

## 📊 数据流程

```
1. 上传教材 (已有功能)
   POST /api/upload

2. 解析教材 (已有功能)
   POST /api/parse/{textbook_id}

3. 构建知识图谱 (新)
   POST /api/kg/build
   → 生成: kg_nodes.json, kg_edges.json

4. 查询知识图谱 (新)
   GET /api/kg

5. 合并知识图谱 (新)
   POST /api/merge
   → 生成: merged_kg.json, merge_decisions.json

6. 查看合并决策 (新)
   GET /api/merge/decisions
```

## 🎯 关键特性

### ✅ 自动提取

- 从每个教材提取 5-8 个关键概念
- 识别概念间的关系（包含、前置、并行等）
- 跨章节建立知识联系

### ✅ 智能合并

- 相似度 ≥ 0.82：自动合并
- 0.65-0.82：标记为可能重复，待人工审核
- < 0.65：保留独立节点

### ✅ LLM 不依赖

- 没有 API Key 时自动降级到规则提取
- 使用启发式算法从文本中提取概念
- 功能完整，只是准确度略有降低

### ✅ 数据持久化

生成 4 种 JSON 输出：

```
data/processed/
├── kg_nodes.json          # 知识节点（50-100 个）
├── kg_edges.json          # 知识关系（80-150 条）
├── merged_kg.json         # 合并后的完整图
└── merge_decisions.json   # 详细的合并决策
```

## 🔍 文件位置

| 文件 | 作用 |
|-----|------|
| `run_full_test.py` | 完整集成测试 |
| `generate_test_data.py` | 生成示例数据 |
| `KG_MERGE_GUIDE.md` | 详细文档 |
| `KG_MERGE_IMPLEMENTATION.md` | 实现总结 |
| `backend/services/llm_client.py` | LLM 客户端 |
| `backend/services/kg_extractor.py` | KG 提取器 |
| `backend/services/merger.py` | 节点合并器 |
| `backend/routers/kg.py` | KG 路由 |
| `backend/routers/merge.py` | Merge 路由 |

## 🚀 典型工作流

### 场景 1：从头开始

```bash
# 1. 生成示例数据
python generate_test_data.py

# 2. 启动 API
python -m backend.main &

# 3. 构建知识图谱
curl -X POST http://localhost:8000/api/kg/build

# 4. 获取图数据
curl http://localhost:8000/api/kg > kg.json

# 5. 执行合并
curl -X POST http://localhost:8000/api/merge

# 6. 查看决策
curl http://localhost:8000/api/merge/decisions > decisions.json
```

### 场景 2：使用已有教材

```bash
# 假设已上传和解析过教材，直接调用
curl -X POST http://localhost:8000/api/kg/build

curl -X POST http://localhost:8000/api/merge

curl http://localhost:8000/api/kg
```

## ⚙️ 环境配置

### 可选的 LLM 配置

```bash
# 使用 OpenAI API（可选）
export LLM_API_KEY="sk-..."
export LLM_MODEL="gpt-3.5-turbo"

# 不设置则自动使用规则提取
```

### 数据目录

```bash
# 自定义数据目录（可选，默认 ./data）
export DATA_DIR="/path/to/data"
```

## 📈 输出示例

### kg_nodes.json（知识节点）

```json
[
  {
    "id": "node_0",
    "name": "函数",
    "type": "concept",
    "description": "函数是建立集合之间对应关系的工具...",
    "definition": "函数是建立集合之间对应关系的工具...",
    "chapter": "第1章 集合与函数",
    "page": 5,
    "source_textbook": "高中数学基础",
    "frequency": 3,
    "sources": ["高中数学基础"]
  },
  {
    "id": "node_1",
    "name": "导数",
    "type": "concept",
    "description": "导数表示函数在某点的变化率...",
    "definition": "导数表示函数在某点的变化率...",
    "chapter": "第2章 导数与微分",
    "page": 51,
    "source_textbook": "高中数学基础",
    "frequency": 2,
    "sources": ["高中数学基础"]
  }
]
```

### merge_decisions.json（合并决策）

```json
[
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
    "similarity": 0.72,
    "decision": "possible_duplicate",
    "timestamp": "2024-05-10T15:30:46.234567"
  }
]
```

## 🐛 常见问题

**Q: 如何增加知识节点的数量？**  
A: 增加教材的章节数或修改 `llm_client.py` 中的 `_fallback_extract_concepts()` 方法

**Q: 如何提高合并的准确度？**  
A: 设置 `LLM_API_KEY` 使用真实 LLM，或调整 `merger.py` 中的权重参数

**Q: 压缩比多少才合适？**  
A: 推荐 0.20-0.30，系统自动保证 ≤ 0.30

**Q: 支持哪些教材格式？**  
A: PDF、Markdown、TXT（由上传和解析模块决定）

## 📞 需要帮助？

查看详细文档：
- `KG_MERGE_GUIDE.md` - 完整实现指南
- `KG_MERGE_IMPLEMENTATION.md` - 实现总结
- `README_BACKEND.md` - 整体后端文档

---

**版本**: 1.0.0  
**更新**: 2026-05-10
