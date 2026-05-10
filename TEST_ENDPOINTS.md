# EduGraph Fusion - API 端点测试指南

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动 API 服务器
```bash
python -m backend.main
```

服务器将运行在 `http://localhost:8000`

### 3. 测试端点

#### 测试 1: 建立 RAG 索引
```bash
curl -X POST http://localhost:8000/api/rag/index \
  -H "Content-Type: application/json"
```

**期望结果：**
```json
{
  "status": "success",
  "message": "RAG index built successfully",
  "data": {
    "indexed": true,
    "chunk_count": 4,
    "textbook_count": 1
  }
}
```

---

#### 测试 2: 查询知识库
```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "什么是函数？",
    "top_k": 5
  }'
```

**期望结果：**
```json
{
  "status": "success",
  "message": "Query successful",
  "data": {
    "question": "什么是函数？",
    "answer": "基于《高等数学基础教材》的《第一章 基础概念》章节，函数是从一个集合映射到另一个集合的规则...",
    "citations": [
      {
        "textbook": "高等数学基础教材",
        "chapter": "第一章 基础概念",
        "chapter_id": "ch1",
        "page_number": 1,
        "chunk_id": "ch1_0",
        "text_excerpt": "基础概念是学习任何学科的基础。本章介绍了数学中的基本概念...",
        "relevance_score": 0.95
      }
    ],
    "source_chunks": [...]
  }
}
```

---

#### 测试 3: 获取 RAG 索引状态
```bash
curl -X GET http://localhost:8000/api/rag/status \
  -H "Content-Type: application/json"
```

**期望结果：**
```json
{
  "status": "success",
  "message": "RAG index status retrieved",
  "data": {
    "indexed": true,
    "chunk_count": 4,
    "textbook_count": 1
  }
}
```

---

#### 测试 4: 提交教师反馈 - 保留指令
```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "保留 函数概念"
  }'
```

**期望结果：**
```json
{
  "status": "success",
  "message": "已标记保留：函数概念",
  "data": {
    "instruction": "保留 函数概念",
    "action": "keep",
    "summary": "已标记保留：函数概念",
    "knowledge_graph_summary": {
      "total_decisions": 1,
      "keep_count": 1,
      "delete_count": 0,
      "split_count": 0,
      "merge_count": 0,
      "kg_nodes": 2,
      "kg_edges": 1,
      "last_updated": "2026-05-10T..."
    }
  }
}
```

---

#### 测试 5: 提交教师反馈 - 删除指令
```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "删除 冗余内容"
  }'
```

**期望结果：**
```json
{
  "status": "success",
  "message": "已删除：冗余内容（删除节点数：0, 删除边数：0）",
  "data": {
    "instruction": "删除 冗余内容",
    "action": "delete",
    "summary": "已删除：冗余内容（删除节点数：0, 删除边数：0）",
    "knowledge_graph_summary": {...}
  }
}
```

---

#### 测试 6: 提交教师反馈 - 拆分指令
```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "拆分 函数概念 和 高级函数"
  }'
```

**期望结果：**
```json
{
  "status": "success",
  "message": "已拆分：函数概念 -> 高级函数（新建节点 ID：...）",
  "data": {
    "instruction": "拆分 函数概念 和 高级函数",
    "action": "split",
    "summary": "已拆分：函数概念 -> 高级函数（新建节点 ID：...）",
    "knowledge_graph_summary": {...}
  }
}
```

---

#### 测试 7: 提交教师反馈 - 合并指令
```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "合并 基本函数 和 函数概念"
  }'
```

**期望结果：**
```json
{
  "status": "success",
  "message": "已合并：基本函数 -> 函数概念",
  "data": {
    "instruction": "合并 基本函数 和 函数概念",
    "action": "merge",
    "summary": "已合并：基本函数 -> 函数概念",
    "knowledge_graph_summary": {...}
  }
}
```

---

#### 测试 8: 获取反馈摘要
```bash
curl -X GET http://localhost:8000/api/feedback/summary \
  -H "Content-Type: application/json"
```

**期望结果：**
```json
{
  "status": "success",
  "message": "Feedback summary retrieved",
  "data": {
    "total_decisions": 4,
    "keep_count": 1,
    "delete_count": 1,
    "split_count": 1,
    "merge_count": 1,
    "kg_nodes": 3,
    "kg_edges": 1,
    "last_updated": "2026-05-10T..."
  }
}
```

---

#### 测试 9: 生成整合报告
```bash
curl -X POST http://localhost:8000/api/report/generate \
  -H "Content-Type: application/json"
```

**期望结果：**
```json
{
  "status": "success",
  "message": "Report generated successfully",
  "data": {
    "report_file": "整合报告.md",
    "report_path": "./report/整合报告.md",
    "generated_at": "2026-05-10T13:00:00...",
    "summary": {
      "textbooks": 1,
      "original_words": 195,
      "merged_words": 156,
      "compression_ratio": 20.0,
      "keep_count": 1,
      "remove_count": 0,
      "merge_count": 1,
      "kg_nodes": 2,
      "kg_edges": 1
    }
  }
}
```

---

#### 测试 10: 获取最新报告
```bash
curl -X GET http://localhost:8000/api/report/latest \
  -H "Content-Type: application/json"
```

**期望结果：**
```json
{
  "status": "success",
  "message": "Report retrieved successfully",
  "data": {
    "report_file": "整合报告.md",
    "report_path": "./report/整合报告.md",
    "modified_at": 1715386800.0,
    "content": "# 教材知识整合报告\n\n**生成时间**：2026-05-10 13:00:00\n\n## 1. 整合概览\n...\n"
  }
}
```

---

#### 测试 11: 获取报告摘要
```bash
curl -X GET http://localhost:8000/api/report/summary \
  -H "Content-Type: application/json"
```

**期望结果：**
```json
{
  "status": "success",
  "message": "Report summary retrieved successfully",
  "data": {
    "textbooks": {
      "total": 1,
      "original_words": 195,
      "merged_words": 156,
      "compression_ratio": 20.0
    },
    "knowledge_graph": {
      "nodes": 2,
      "edges": 1,
      "node_types": {
        "concept": 2
      }
    },
    "decisions": {
      "keep": 1,
      "remove": 0,
      "merge": 1,
      "split": 0,
      "total": 2
    }
  }
}
```

---

## 数据流说明

### 数据读取优先级（RAG 和报告生成）
1. **`backend/data/metadata/*_chapters.json`** - 模块一（upload/parse）的输出 ✓ 优先读取
2. **`backend/data/processed/*.json`** - 模块二（kg_extractor/merger）的输出 ✓ 兼容读取
3. 如果上述都不存在，使用默认值返回空结果

### 知识图谱编辑（反馈系统）
- 读取：`backend/data/processed/merged_kg.json`
- 读取：`backend/data/processed/merge_decisions.json`
- 写入：修改后的 JSON 文件

### 报告生成
- 输出：`report/整合报告.md`
- 包含：教材统计、知识图谱分析、决策统计、典型案例

---

## 关键功能说明

### RAG（检索增强生成）
- **chunk_size**: 700 字符
- **overlap**: 100 字符  
- **top_k**: 5 个最相关的块
- **Embedding 策略**：
  1. sentence-transformers (优先)
  2. TF-IDF (fallback)
  3. 关键词匹配 (终极fallback)
- **向量库**：
  1. FAISS (优先)
  2. sklearn NearestNeighbors (fallback)

### 教师反馈支持的指令
- `保留 XXX` - 标记内容为保留
- `删除 XXX` - 删除节点及相关边
- `拆分 XXX 和 YYY` - 从 XXX 中拆分出 YYY
- `合并 XXX 和 YYY` - 合并两个节点，删除 XXX，重定向边到 YYY

### 报告生成
- 即使缺少数据也能生成报告（使用默认值兜底）
- 包含教学完整性说明
- 提供典型整合案例和建议

---

## 故障排除

### RAG 索引失败
- 检查 `backend/data/metadata` 或 `backend/data/processed` 是否有数据
- 确保 JSON 文件格式正确
- 检查 sentence-transformers 是否已安装

### 查询返回空结果
- 确保已执行 `/api/rag/index`
- 尝试使用不同的关键词
- 检查知识库中是否有数据

### 反馈处理失败
- 检查指令格式是否正确
- 确保 `merged_kg.json` 和 `merge_decisions.json` 存在
- 检查节点名称是否存在

### 报告生成失败
- 检查 `./report` 目录是否可写
- 确保 `data/metadata` 或 `data/processed` 中有数据
- 查看错误日志了解详细信息

---

## 注意事项

1. **兼容性**：所有接口都兼容模块一和模块二的输出格式
2. **Fallback**：所有关键功能都有多层 fallback 机制，确保即使依赖不可用也能运行
3. **数据持久性**：反馈修改会持久化到 JSON 文件
4. **并发性**：RAG 索引是全局单例，支持并发查询
5. **错误处理**：所有接口统一返回 `{status, message, data}` 格式
