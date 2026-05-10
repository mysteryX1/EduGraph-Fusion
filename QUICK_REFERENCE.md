# 教材知识底座 API - 快速参考

## 概述

本 API 服务为教材上传、解析、知识提取、RAG 查询和报告生成的完整后端解决方案。

## 模块分工

| 模块 | 负责人 | 功能 |
|------|--------|------|
| 文件上传、教材解析、数据底座 | Team 1 | 教材导入、解析、存储 |
| 知识图谱和跨教材整合 | Team 2 | KG 构建、去重、合并 |
| RAG、教师反馈、整合报告 | Team 3 | 智能查询、反馈处理、报告生成 |

## API 文档

### 1. RAG 相关接口

#### 1.1 建立 RAG 索引
```
POST /api/rag/index
```

#### 1.2 查询知识库
```
POST /api/rag/query
Content-Type: application/json

{
  "question": "什么是机器学习？",
  "top_k": 5
}
```

#### 1.3 获取 RAG 索引状态
```
GET /api/rag/status
```

### 2. 教师反馈接口

#### 2.1 提交反馈
```
POST /api/feedback
Content-Type: application/json

{
  "instruction": "合并 '线性代数' 和 '矩阵论'"
}
```

支持的指令格式：
- `保留 XXX` - 保留指定知识节点
- `删除 XXX` - 删除指定知识节点
- `拆分 XXX 和 YYY` - 将一个节点拆分为两个
- `合并 XXX 和 YYY` - 合并两个相关节点

#### 2.2 获取反馈摘要
```
GET /api/feedback/summary
```

### 3. 报告生成接口

#### 3.1 生成整合报告
```
POST /api/report/generate
```

#### 3.2 获取最新报告
```
GET /api/report/latest
```

#### 3.3 获取报告摘要
```
GET /api/report/summary
```

## 技术栈

### RAG 服务
- Chunking: 700 中文字符，100 字符重叠
- Embedding: sentence-transformers (fallback: TF-IDF)
- Vector Store: FAISS (fallback: sklearn NearestNeighbors)
- LLM: Qwen3-32B via ModelScope

### 反馈处理
- 自然语言指令解析 (regex)
- 知识图谱动态修改
- 决策持久化存储

### 报告生成
- 统计数据收集
- 典型案例提取
- Markdown 文档生成

## 文件结构

```
backend/
├── models/
│   └── schemas.py
├── services/
│   ├── rag.py              ✨ RAG 服务
│   ├── feedback.py         ✨ 反馈处理
│   └── report_generator.py ✨ 报告生成
├── routers/
│   ├── rag.py              ✨ RAG 路由
│   ├── feedback.py         ✨ 反馈路由
│   └── report.py           ✨ 报告路由
└── main.py

data/
├── uploads/
├── metadata/
└── processed/
    ├── textbook_*.json
    ├── merge_decisions.json
    └── merged_kg.json

report/
└── 整合报告.md
```

## 快速开始

```bash
# 1. 启动服务
python run.py

# 2. 建立 RAG 索引
curl -X POST http://localhost:8000/api/rag/index

# 3. 查询知识库
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "什么是机器学习？"}'

# 4. 提交反馈
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"instruction": "合并 线性代数 和 矩阵论"}'

# 5. 生成报告
curl -X POST http://localhost:8000/api/report/generate
```

## 依赖配置

requirements.txt 已更新，包括：
- sentence-transformers>=2.2.0
- faiss-cpu>=1.7.4
- scikit-learn>=1.3.0
- numpy>=1.24.0
- litellm>=0.1.0

## 注意事项

1. RAG 索引初始化：首次使用必须先调用 `/api/rag/index`
2. LLM 调用：需要配置 MODELSCOPE_SDK_TOKEN
3. 向量库 fallback：FAISS 失败时自动使用 sklearn
4. 反馈指令：必须严格遵循格式规范
5. 报告依赖：需要 KG 和 merge_decisions 文件存在

---

**版本**：1.0.0
**最后更新**：2024-05-10
