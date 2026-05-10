# 项目文件结构

## 完整的项目树

```
黑客松2/
├── backend/
│   ├── __init__.py
│   ├── main.py ⭐ (已更新 - 导入和注册新路由)
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py (已有的数据模型)
│   ├── services/
│   │   ├── __init__.py ⭐ (已更新 - 导出新类)
│   │   ├── parser.py (不修改)
│   │   ├── storage.py (不修改)
│   │   ├── report_stats.py (不修改)
│   │   ├── rag.py ✨ NEW (381 行)
│   │   ├── feedback.py ✨ NEW (283 行)
│   │   └── report_generator.py ✨ NEW (380 行)
│   └── routers/
│       ├── __init__.py ⭐ (已更新 - 导出新路由)
│       ├── upload.py (不修改)
│       ├── textbooks.py (不修改)
│       ├── rag.py ✨ NEW (160 行)
│       ├── feedback.py ✨ NEW (78 行)
│       └── report.py ✨ NEW (175 行)
│
├── requirements.txt ⭐ (已更新 - 添加依赖)
├── run.py (不修改)
├── test_api.py (不修改)
├── litellm_modelscope.yaml (不修改)
│
├── QUICK_REFERENCE.md ✨ NEW (API 文档)
├── PROJECT_COMPLETION.md ✨ NEW (完成总结)
├── FILE_STRUCTURE.md ✨ NEW (本文件)
│
├── data/
│   ├── uploads/ (由 Team 1 管理)
│   ├── metadata/ (由 Team 1 管理)
│   └── processed/
│       ├── textbook_*.json (由 Team 1 生成)
│       ├── merge_decisions.json (由反馈操作维护)
│       └── merged_kg.json (由 Team 2 生成，反馈修改)
│
├── report/ (由报告生成服务创建)
│   └── 整合报告.md ✨ (生成的报告)
│
└── temp/ (临时文件目录)
```

## 新增代码统计

| 文件 | 行数 | 功能 |
|------|------|------|
| backend/services/rag.py | 381 | RAG 服务 |
| backend/services/feedback.py | 283 | 反馈处理 |
| backend/services/report_generator.py | 380 | 报告生成 |
| backend/routers/rag.py | 160 | RAG 路由 |
| backend/routers/feedback.py | 78 | 反馈路由 |
| backend/routers/report.py | 175 | 报告路由 |
| **总计** | **1,457** | **6 个新文件** |

## 文件修改记录

### requirements.txt
```diff
+ sentence-transformers>=2.2.0
+ faiss-cpu>=1.7.4
+ scikit-learn>=1.3.0
+ numpy>=1.24.0
+ litellm>=0.1.0
```

### backend/main.py (第 9 行)
```diff
- from .routers import upload, textbooks
+ from .routers import upload, textbooks, rag, feedback, report
```

### backend/main.py (第 45-50 行)
```diff
  # 包含路由
  app.include_router(upload.router)
  app.include_router(textbooks.router)
+ app.include_router(rag.router)
+ app.include_router(feedback.router)
+ app.include_router(report.router)
```

### backend/main.py (第 58-68 行)
```diff
  "endpoints": {
      "upload": "POST /api/upload",
      ...
+     "rag_index": "POST /api/rag/index",
+     "rag_query": "POST /api/rag/query",
+     "rag_status": "GET /api/rag/status",
+     "submit_feedback": "POST /api/feedback",
+     "feedback_summary": "GET /api/feedback/summary",
+     "generate_report": "POST /api/report/generate",
+     "get_report": "GET /api/report/latest",
+     "report_summary": "GET /api/report/summary",
  }
```

### backend/routers/__init__.py
```diff
  from . import upload
  from . import textbooks
+ from . import rag
+ from . import feedback
+ from . import report

- __all__ = ["upload", "textbooks"]
+ __all__ = ["upload", "textbooks", "rag", "feedback", "report"]
```

### backend/services/__init__.py
```diff
  from .storage import FileStorage
  from .report_stats import StatsReporter
+ from .rag import RAGEngine, ChunkManager, EmbeddingProvider, VectorStore
+ from .feedback import FeedbackProcessor
+ from .report_generator import ReportGenerator

  __all__ = [
      ...
+     "RAGEngine",
+     "ChunkManager",
+     "EmbeddingProvider",
+     "VectorStore",
+     "FeedbackProcessor",
+     "ReportGenerator",
  ]
```

## API 接口清单

### RAG 模块 (3 个)
- ✅ `POST /api/rag/index` - 建立向量索引
- ✅ `POST /api/rag/query` - 查询知识库
- ✅ `GET /api/rag/status` - 获取索引状态

### 反馈模块 (2 个)
- ✅ `POST /api/feedback` - 提交自然语言反馈
- ✅ `GET /api/feedback/summary` - 获取反馈统计

### 报告模块 (3 个)
- ✅ `POST /api/report/generate` - 生成整合报告
- ✅ `GET /api/report/latest` - 获取最新报告
- ✅ `GET /api/report/summary` - 获取报告摘要

**新增接口总数：8 个**

## 依赖新增

| 包名 | 版本 | 用途 |
|-----|------|------|
| sentence-transformers | >=2.2.0 | 文本嵌入 (Embedding) |
| faiss-cpu | >=1.7.4 | 向量相似度搜索 |
| scikit-learn | >=1.3.0 | TF-IDF fallback 和 NearestNeighbors |
| numpy | >=1.24.0 | 数值计算 |
| litellm | >=0.1.0 | LLM 接口统一层 |

## 数据流向

### 输入数据源
- Team 1: `data/processed/textbook_*.json` (教材 JSON)
- Team 2: `data/processed/merged_kg.json` (合并后的知识图谱)
- Team 2: `data/processed/merge_decisions.json` (合并决策)

### 输出数据源
- Team 3: `report/整合报告.md` (生成的报告)
- 反馈系统更新: `data/processed/merge_decisions.json` (修改后的决策)
- 反馈系统更新: `data/processed/merged_kg.json` (修改后的 KG)

## 关键类和方法

### RAGEngine (rag.py)
```python
class RAGEngine:
    load_and_index()  # 加载教材并建立索引
    query(question, top_k=5)  # 查询知识库
```

### FeedbackProcessor (feedback.py)
```python
class FeedbackProcessor:
    process_instruction(instruction)  # 处理自然语言指令
    get_feedback_summary()  # 获取反馈摘要
```

### ReportGenerator (report_generator.py)
```python
class ReportGenerator:
    generate_report()  # 生成完整报告
```

## 测试清单

- [ ] 安装依赖: `pip install -r requirements.txt`
- [ ] 启动服务: `python run.py`
- [ ] 测试 RAG 索引: `POST /api/rag/index`
- [ ] 测试 RAG 查询: `POST /api/rag/query`
- [ ] 测试反馈: `POST /api/feedback`
- [ ] 测试报告生成: `POST /api/report/generate`
- [ ] 验证所有接口返回格式一致

## 架构设计原则

1. **分层设计**
   - Services: 业务逻辑实现
   - Routers: API 接口层
   - Models: 数据模型定义

2. **容错设计**
   - Embedding 失败时使用 TF-IDF
   - FAISS 不可用时使用 sklearn
   - LLM 失败时返回摘要

3. **数据独立性**
   - 不修改 Team 1 和 Team 2 的核心文件
   - 通过 JSON 文件进行数据交互
   - 支持多模块并行开发

4. **可扩展性**
   - 统一的 JSON 响应格式
   - 易于扩展的指令解析系统
   - 灵活的报告生成框架

---

**最后更新**: 2024-05-10
