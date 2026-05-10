# Codex Handoff：EduGraph Fusion｜智教材图谱融合系统

> 用途：本文件用于把当前 ChatGPT 对话中的关键信息、赛题要求、项目状态、模块一输出、后续任务拆分和执行计划转交给本地 Codex。  
> 当前目标：在已有模块一后端数据底座基础上，继续完成知识图谱、跨教材整合、RAG、教师反馈、前端、文档和部署，形成最小可完赛闭环。

---

## 1. 项目基本信息

### 1.1 项目名称

- 英文名：`EduGraph Fusion`
- 中文名：`智教材图谱融合系统`
- 页面标题建议：`EduGraph Fusion｜智教材图谱融合系统`
- 仓库名建议：`edugraph-fusion`

一句话介绍：

> 面向多教材知识整合的 AI Agent 系统，支持教材解析、知识图谱构建、跨教材去重融合、带引用 RAG 问答、教师反馈修正和整合报告生成。

### 1.2 赛事背景

赛题是“AI 全栈极速黑客松·学科知识整合智能体开发”。核心任务是在 5 小时内开发一个 Web 系统，对多本教材进行知识整合，包含：

1. 多格式教材上传与解析。
2. 每本教材构建知识图谱并可视化。
3. 跨教材识别重复、互补和缺失知识点。
4. 将多本教材内容整合压缩到原始总字数的 30% 以内。
5. 基于整合后的知识库做 RAG 精准问答，必须引用原文来源。
6. 自主设计 Agent 架构，并提交 `docs/Agent架构说明.md`。
7. 支持教师多轮反馈修改整合方案。
8. 提交 GitHub Public 仓库和公网可访问部署链接。

### 1.3 最小完赛闭环

当前策略不是追求完整 7 本教材全量高质量处理，而是先确保一条完整可演示链路：

```text
打开 Web 页面
→ 上传至少 2 个教材文件
→ 显示解析状态和章节
→ 构建 nodes/edges
→ 展示可交互知识图谱
→ 跨教材整合
→ 显示 merge/keep/remove 和压缩比 < 30%
→ 建立 RAG 索引
→ 问答返回引用
→ 教师反馈修改至少一项整合决策
→ 生成整合报告和文档
→ GitHub Public + 在线部署链接
```

### 1.4 不要优先做的内容

在最小完赛闭环完成之前，不要投入以下内容：

```text
Docker 一键部署
BM25 + Rerank
复杂多 Agent
多视图图谱
Excel 解析
DOCX 深度优化
完整 7 本教材全量高质量处理
P2 技术报告
复杂前端动效
```

---

## 2. 当前项目目录与环境

### 2.1 当前项目路径

Windows 本地路径：

```powershell
D:\我的大学\博一下\黑客松2
```

### 2.2 用户当前看到的根目录

```text
D:\我的大学\博一下\黑客松2
├─ .claude
├─ backend
│  ├─ models
│  ├─ routers
│  └─ services
├─ problem
├─ textbooks
├─ .env.example
├─ COMPLETION_SUMMARY.md
├─ FILES_MANIFEST.txt
├─ IMPLEMENTATION_CHECKLIST.md
├─ litellm_modelscope.yaml
├─ message.md
├─ PROJECT_STRUCTURE.md
├─ QUICKSTART.md
├─ QUICK_REFERENCE.md
├─ README_BACKEND.md
├─ requirements.txt
├─ run.py
└─ test_api.py
```

### 2.3 特别注意

- `textbooks/` 是赛事方提供的题目/教材内容。
- 最终不能把教材 PDF 推送到 GitHub。
- `.gitignore` 必须排除：

```gitignore
textbooks/*.pdf
*.pdf
backend/data/uploads/
backend/data/vector_index/
node_modules/
.env
```

### 2.4 Windows 查看完整树命令

用户之前在 PowerShell 里使用 `tree -f` 报错。Windows 应使用：

```powershell
tree /f
```

---

## 3. 模块一当前状态：后端数据底座

### 3.1 模块一定位

模块一是“后端数据底座”，负责：

```text
文件上传
→ PDF/Markdown/TXT 解析
→ 章节结构化
→ 元数据保存
→ 基础查询 API
```

### 3.2 模块一 Claude 输出摘要

根据用户粘贴的模块一完成总结，当前模块一声称已完成：

- FastAPI 教材知识底座后端。
- 总文件数 30 个。
- Python 源代码 11 个模块。
- 代码行数约 1,458 行。
- 文档约 7–8 份。
- API 端点 6 个。
- Pydantic 数据模型 11 个。
- 支持格式：PDF + Markdown + TXT。
- PDF 使用 PyMuPDF 逐页处理。
- Markdown 按 `#` 标题分割。
- TXT 按固定字数分割。
- 自动章节识别，支持中文章标题、英文 Chapter、数字标题等。
- 识别失败时自动生成伪章节。
- JSON 持久化：

```text
data/metadata/
├── {textbook_id}_metadata.json
└── {textbook_id}_chapters.json
```

### 3.3 已声明的 6 个基础 API

```text
POST /api/upload
POST /api/parse/{id}
GET  /api/textbooks
GET  /api/textbooks/{id}
GET  /api/stats
GET  /api/textbooks/{id}/stats
```

注意：用户之前提到过“8 个新 API 接口”，但模块一总结中实际列出的是 6 个端点。必须以 `http://localhost:8000/docs` 中实际注册的接口为准。

### 3.4 模块一相关文件

```text
backend/
├── __init__.py
├── main.py
├── models/
│   ├── __init__.py
│   └── schemas.py
├── services/
│   ├── parser.py
│   ├── storage.py
│   └── report_stats.py
└── routers/
    ├── upload.py
    └── textbooks.py

根目录：
├── requirements.txt
├── .env.example
├── run.py
├── test_api.py
├── QUICKSTART.md
├── README_BACKEND.md
├── PROJECT_STRUCTURE.md
├── QUICK_REFERENCE.md
├── IMPLEMENTATION_CHECKLIST.md
├── COMPLETION_SUMMARY.md
└── FILES_MANIFEST.txt
```

### 3.5 模块一尚需真实验收

不要只信 Claude 总结。下一步必须进行 API 真实测试。

推荐给本地 Codex 的第一任务：

```text
不要继续开发新功能。先验收模块一。

1. 启动服务：python run.py
2. 打开 http://localhost:8000/docs，核对实际 API。
3. 运行：python test_api.py
4. 用 textbooks/ 中至少一个 PDF 测试上传与解析。
5. 构造简单 test.md 和 test.txt 测试 Markdown/TXT。
6. 确认 data/metadata/ 生成 JSON。
7. 重启服务后确认已解析数据仍可读取。
8. 输出接口测试表：接口 | 状态码 | 是否通过 | 备注。
```

PowerShell 快速测试命令：

```powershell
cd "D:\我的大学\博一下\黑客松2"
python run.py
```

另开一个终端：

```powershell
cd "D:\我的大学\博一下\黑客松2"
python test_api.py
```

手动测试示例：

```powershell
curl.exe http://localhost:8000/api/textbooks
curl.exe http://localhost:8000/api/stats
```

上传 PDF 示例：

```powershell
curl.exe -X POST "http://localhost:8000/api/upload" `
  -F "file=@textbooks\你的教材.pdf"
```

解析：

```powershell
curl.exe -X POST "http://localhost:8000/api/parse/返回的textbook_id"
```

详情：

```powershell
curl.exe "http://localhost:8000/api/textbooks/返回的textbook_id"
```

### 3.6 模块一最低通过标准

模块一只有满足以下条件后，才可锁定：

```text
1. 服务能启动。
2. /docs 能打开。
3. PDF 能上传。
4. PDF 能解析出 chapters。
5. Markdown/TXT 能解析。
6. GET /api/textbooks 能返回教材列表。
7. GET /api/textbooks/{id} 能返回 chapters。
8. /api/stats 能返回 total_textbooks、total_chars 等统计。
9. data/metadata/ 中有实际 JSON 文件。
10. 重启服务后仍能读取已解析数据。
```

模块一通过后执行：

```powershell
git add .
git commit -m "complete module 1 backend textbook parser"
```

---

## 4. 后续三大任务包

模块一完成后，后续不是继续按“模块二/三”粗略分，而是拆成三个并行任务：

```text
Claude/Codex A：知识图谱 + 跨教材整合
Claude/Codex B：RAG + 教师反馈 + 报告生成
Claude/Codex C：前端 + 文档 + 部署
```

核心原则：

```text
1. 三个任务包不要同时修改同一批文件。
2. 不要重构模块一已有 parser/storage/upload/textbooks 逻辑。
3. 先让每个模块可单独 mock 测试。
4. 最后 40 分钟只联调、修 bug、补文档、部署。
```

---

## 5. Codex A：知识图谱 + 跨教材整合

### 5.1 目标

```text
解析后的 textbook/chapter
→ LLM 抽取知识点
→ 构建 KG nodes/edges
→ 跨教材语义对齐
→ merge/keep/remove 决策
→ 压缩比统计
```

### 5.2 允许新增/修改文件

```text
backend/services/llm_client.py
backend/services/kg_extractor.py
backend/services/merger.py
backend/routers/kg.py
backend/routers/merge.py
```

必要时可在 `backend/main.py` 里只添加 router 注册，不要重构主程序。

### 5.3 禁止修改

```text
backend/services/parser.py
backend/services/storage.py
backend/routers/upload.py
backend/routers/textbooks.py
textbooks/
problem/
```

### 5.4 需要实现的 API

```text
POST /api/kg/build
GET  /api/kg
POST /api/merge
GET  /api/merge/decisions
```

### 5.5 KG 抽取要求

- 每本教材最多处理前 5 个章节。
- 每章抽取 5–8 个知识点。
- 关系类型至少支持：
  - `prerequisite`
  - `contains`
  - `parallel`
- 可选支持：`applies_to`
- LLM 输出必须要求 JSON 格式。
- LLM 调用失败时，必须有规则 fallback，保证接口不崩。

KG 节点建议结构：

```json
{
  "id": "book01_node_001",
  "name": "快速排序",
  "definition": "快速排序是一种基于分治思想的排序算法。",
  "category": "算法方法",
  "chapter": "第七章 排序",
  "page": 120,
  "source_textbook": "数据结构A",
  "frequency": 1,
  "sources": [
    {
      "textbook": "数据结构A",
      "chapter": "第七章 排序",
      "page": 120
    }
  ]
}
```

KG 边建议结构：

```json
{
  "source": "book01_node_001",
  "target": "book01_node_002",
  "relation_type": "prerequisite",
  "description": "理解快速排序需要先理解递归。"
}
```

### 5.6 整合算法要求

推荐最小策略：

```text
1. 对所有节点计算 embedding。
2. 对不同教材来源的节点两两计算 cosine similarity。
3. sim >= 0.82：merge。
4. 0.65 <= sim < 0.82：keep，但 reason 标记 possible duplicate。
5. sim < 0.65：keep。
6. 合并后节点 frequency = 来源节点数量。
7. 合并 sources。
8. 统计 original_chars、merged_chars、compression_ratio。
9. 若 compression_ratio > 0.30，截断低频节点 definition 或低优先级内容，确保 <=0.30。
```

输出文件：

```text
backend/data/processed/kg_nodes.json
backend/data/processed/kg_edges.json
backend/data/processed/merged_kg.json
backend/data/processed/merge_decisions.json
```

整合决策格式：

```json
{
  "decision_id": "merge_001",
  "action": "merge",
  "affected_nodes": ["book01_node_001", "book02_node_007"],
  "result_node": "merged_node_001",
  "reason": "两个知识点语义高度相似，因此合并。",
  "confidence": 0.88
}
```

### 5.7 给 Codex A 的可复制任务提示

```text
你接手 EduGraph Fusion 项目的知识图谱与跨教材整合模块。模块一后端数据底座已完成，包含 PDF/Markdown/TXT 上传解析、data/metadata JSON 持久化和基础 API。请不要修改 parser.py、storage.py、upload.py、textbooks.py。

你的任务：
1. 读取 backend/models/schemas.py，复用已有 KGNode、KGEdge、MergeDecision 等 schema；必要时做兼容性扩展，不要破坏已有字段。
2. 实现 backend/services/llm_client.py，从 .env 读取 API_KEY、BASE_URL、MODEL_NAME，兼容 OpenAI-style API；如果没有 API_KEY，提供 mock/fallback 输出。
3. 实现 backend/services/kg_extractor.py：读取已解析教材，每本最多前 5 章，每章 5–8 个知识点，关系类型至少 prerequisite、contains、parallel；LLM 输出 JSON；失败时规则 fallback。
4. 实现 backend/services/merger.py：不同教材节点语义相似度对齐，>=0.82 merge，0.65–0.82 keep+possible duplicate，<0.65 keep；输出 merge/keep/remove 决策；统计 original_chars、merged_chars、compression_ratio，并确保 compression_ratio <=0.30。
5. 实现 backend/routers/kg.py 和 backend/routers/merge.py：POST /api/kg/build、GET /api/kg、POST /api/merge、GET /api/merge/decisions。
6. 输出 JSON 到 backend/data/processed/：kg_nodes.json、kg_edges.json、merged_kg.json、merge_decisions.json。
7. 所有接口返回统一 JSON：success、message、data。
8. 必要时只在 main.py 添加 include_router，不要重构 main.py。
9. 完成后给出 API 测试命令和结果。
```

---

## 6. Codex B：RAG + 教师反馈 + 报告生成

### 6.1 目标

```text
章节内容
→ chunk 切分
→ embedding/TF-IDF
→ 向量索引/近邻检索
→ top-5 chunk
→ 带引用回答
→ 教师反馈修改整合结果
→ 生成 report/整合报告.md
```

### 6.2 允许新增/修改文件

```text
backend/services/rag.py
backend/services/feedback.py
backend/services/report_generator.py
backend/routers/rag.py
backend/routers/feedback.py
backend/routers/report.py
report/整合报告.md
```

必要时可在 `backend/main.py` 里只添加 router 注册。

### 6.3 禁止修改

```text
backend/services/parser.py
backend/services/storage.py
backend/services/kg_extractor.py
backend/services/merger.py
backend/routers/upload.py
backend/routers/textbooks.py
textbooks/
problem/
```

### 6.4 需要实现的 API

```text
POST /api/rag/index
POST /api/rag/query
GET  /api/rag/status
POST /api/feedback
POST /api/report/generate
```

### 6.5 RAG 最小策略

- 读取模块一解析后的章节内容。
- `chunk_size = 700` 中文字符。
- `overlap = 100` 中文字符。
- 每个 chunk 保留元数据：
  - `textbook`
  - `chapter`
  - `page`
  - `chunk_id`
- 检索 `top_k = 5`。
- 优先使用 `sentence-transformers + FAISS`。
- 如果不可用，使用 `TF-IDF + sklearn NearestNeighbors` fallback。
- LLM 回答必须只基于上下文。
- 找不到答案时返回：

```text
当前知识库中未找到相关信息
```

RAG 查询返回结构：

```json
{
  "answer": "快速排序是一种基于分治思想的排序算法。[数据结构A, 第七章 排序, 第120页]",
  "citations": [
    {
      "textbook": "数据结构A",
      "chapter": "第七章 排序",
      "page": 120,
      "relevance_score": 0.91
    }
  ],
  "source_chunks": [
    "快速排序是一种基于分治思想的排序算法..."
  ]
}
```

### 6.6 教师反馈最小策略

支持以下自然语言命令：

```text
保留 XXX
删除 XXX
拆分 XXX 和 YYY
合并 XXX 和 YYY
```

读取并修改：

```text
backend/data/processed/merge_decisions.json
backend/data/processed/merged_kg.json
```

返回修改摘要，并保存变更。

### 6.7 报告生成要求

生成文件：

```text
report/整合报告.md
```

报告至少包含：

```text
1. 教材数量。
2. 原始总字数。
3. 整合后字数。
4. 压缩比。
5. merge/keep/remove 数量。
6. 整合前后节点数。
7. 3 个典型整合案例。
8. 教学完整性说明。
```

### 6.8 给 Codex B 的可复制任务提示

```text
你接手 EduGraph Fusion 项目的 RAG、教师反馈和报告生成模块。模块一后端数据底座已完成，另一个模块会负责知识图谱与跨教材整合。请不要修改 parser.py、storage.py、kg_extractor.py、merger.py。

你的任务：
1. 读取 backend/models/schemas.py，复用 Textbook、Chapter、Citation、RagAnswer、MergeDecision 等 schema。
2. 实现 backend/services/rag.py：读取 data/metadata 中已解析教材，对 chapter.content 做 chunk 切分，chunk_size=700，overlap=100；保留 textbook、chapter、page、chunk_id 元数据；优先 sentence-transformers/FAISS，不可用则 TF-IDF/sklearn fallback；查询返回 top-5 chunk；用 LLM 或 fallback 生成带引用回答；找不到答案返回“当前知识库中未找到相关信息”。
3. 实现 backend/routers/rag.py：POST /api/rag/index、POST /api/rag/query、GET /api/rag/status。
4. 实现 backend/services/feedback.py：读取 merge_decisions.json 和 merged_kg.json，支持“保留 XXX”“删除 XXX”“拆分 XXX 和 YYY”“合并 XXX 和 YYY”，修改并保存整合结果。
5. 实现 backend/routers/feedback.py：POST /api/feedback。
6. 实现 backend/services/report_generator.py：读取教材统计、kg_nodes、kg_edges、merge_decisions、merged_kg，生成 report/整合报告.md，包含教材数量、总字数、整合后字数、压缩比、merge/keep/remove 数量、整合前后节点数、3 个典型整合案例和教学完整性说明。
7. 实现 backend/routers/report.py：POST /api/report/generate。
8. 所有接口返回统一 JSON：success、message、data。
9. 必要时只在 main.py 添加 include_router，不要重构 main.py。
10. 完成后给出 API 测试命令和结果。
```

---

## 7. Codex C：前端 + 文档 + 部署

### 7.1 目标

做出可演示、可提交的 Web 产品界面，并补齐提交文档。

```text
上传界面
→ 教材列表
→ 图谱可视化
→ 整合决策面板
→ RAG 问答面板
→ 教师反馈面板
→ 报告生成
→ README/docs/report/.gitignore
→ 部署准备
```

### 7.2 允许新增/修改文件

```text
frontend/
docs/
report/
README.md
.gitignore
package.json
```

可读取但不要破坏：

```text
QUICKSTART.md
README_BACKEND.md
PROJECT_STRUCTURE.md
```

### 7.3 禁止修改

```text
backend/services/
backend/routers/
textbooks/
problem/
```

除非最后联调只改 API 地址。

### 7.4 前端技术选择

- React + Vite。
- 图谱使用 ECharts graph。
- 单页应用 SPA。
- 布局：

```text
左侧：教材管理区
中间：知识图谱可视化区
右侧：Tab 面板
```

### 7.5 前端功能要求

左侧：

```text
上传文件
文件列表
解析状态
解析按钮
构建图谱按钮
执行整合按钮
建立 RAG 索引按钮
```

中间：

```text
ECharts graph
节点颜色区分教材来源
节点大小表示 frequency
支持缩放、拖拽
点击节点后右侧显示详情
```

右侧 Tab：

```text
节点详情
整合决策
RAG 问答
教师反馈
报告生成
```

### 7.6 前端 API 集中定义

文件：

```text
frontend/src/api.js
```

接口：

```javascript
export const API = {
  upload: "/api/upload",
  parse: (id) => `/api/parse/${id}`,
  textbooks: "/api/textbooks",
  buildKG: "/api/kg/build",
  getKG: "/api/kg",
  merge: "/api/merge",
  decisions: "/api/merge/decisions",
  ragIndex: "/api/rag/index",
  ragQuery: "/api/rag/query",
  ragStatus: "/api/rag/status",
  feedback: "/api/feedback",
  reportGenerate: "/api/report/generate",
  stats: "/api/stats"
};
```

### 7.7 必备文档

```text
README.md
docs/需求分析.md
docs/系统设计.md
docs/Agent架构说明.md
docs/接口文档.md
report/整合报告.md
```

README 至少包含：

```text
项目简介
技术栈
环境依赖
.env 配置
后端启动命令
前端启动命令
使用流程
部署说明
```

需求分析至少包含：

```text
知识点粒度定义
重复判定标准
教学连贯性保障
压缩比计算方式
RAG 分块策略选择依据
```

系统设计至少包含：

```text
系统架构图
数据流
模块划分
技术选型理由
API 一览
```

Agent 架构说明至少包含：

```text
架构总览
为什么采用模块化单 Agent/轻量多模块编排
为什么不做复杂多 Agent
每个模块职责边界
数据流与调用链路
取舍与权衡
已知局限与后续改进
```

### 7.8 给 Codex C 的可复制任务提示

```text
你接手 EduGraph Fusion 项目的前端、文档和部署准备。后端模块一已完成，A/B 模块会继续提供知识图谱、整合、RAG、反馈和报告 API。请不要修改 backend/services 和 backend/routers。

你的任务：
1. 新建 frontend/，使用 React + Vite。
2. 实现单页应用布局：左侧教材管理区，中间知识图谱可视化区，右侧 Tab 功能面板。
3. 所有 API 统一写在 frontend/src/api.js，对接 /api/upload、/api/parse/{textbook_id}、/api/textbooks、/api/kg/build、/api/kg、/api/merge、/api/merge/decisions、/api/rag/index、/api/rag/query、/api/rag/status、/api/feedback、/api/report/generate。
4. 使用 ECharts graph 实现知识图谱：节点颜色区分教材来源，节点大小表示 frequency，支持缩放、拖拽，点击节点后在右侧显示 name、definition、chapter、page、source_textbook。
5. 实现组件：UploadPanel.jsx、GraphView.jsx、MergePanel.jsx、RagPanel.jsx、FeedbackPanel.jsx、ReportPanel.jsx。
6. 所有按钮要有 loading 状态和错误提示。
7. 后端接口暂时不可用时，前端要有 mock 数据 fallback，保证页面能展示。
8. 新建 docs/需求分析.md、docs/系统设计.md、docs/Agent架构说明.md、docs/接口文档.md。
9. 新建 report/整合报告.md 模板。
10. 新建根目录 README.md。
11. 新建或修改 .gitignore，必须排除 textbooks/*.pdf、*.pdf、backend/data/uploads、backend/data/vector_index、node_modules、.env。
12. 提供前端启动命令和联调检查步骤。
```

---

## 8. 后端统一响应格式建议

后续 A/B 模块尽量统一返回：

```json
{
  "success": true,
  "message": "ok",
  "data": {}
}
```

错误格式：

```json
{
  "success": false,
  "message": "错误原因",
  "data": null
}
```

---

## 9. 联调顺序

### 9.1 第一步：锁定模块一

```powershell
python run.py
python test_api.py
```

确认 6 个基础 API 可用，尤其是上传、解析、chapters 输出和 JSON 持久化。

### 9.2 第二步：合并 Codex A

检查：

```text
POST /api/kg/build
GET  /api/kg
POST /api/merge
GET  /api/merge/decisions
```

重点验收：

```text
1. 能基于已解析教材生成 nodes/edges。
2. 关系类型至少有 prerequisite、contains、parallel 三类中的若干。
3. 能输出 merge/keep/remove 决策。
4. compression_ratio <= 0.30。
5. JSON 文件写入 backend/data/processed/。
```

### 9.3 第三步：合并 Codex B

检查：

```text
POST /api/rag/index
POST /api/rag/query
GET  /api/rag/status
POST /api/feedback
POST /api/report/generate
```

重点验收：

```text
1. RAG 能建立索引。
2. RAG 能返回 answer。
3. citations 中包含 textbook、chapter、page、relevance_score。
4. 找不到答案时返回“当前知识库中未找到相关信息”。
5. feedback 能修改 merge_decisions 或 merged_kg。
6. report/整合报告.md 能生成。
```

### 9.4 第四步：合并 Codex C

启动前端：

```powershell
cd frontend
npm install
npm run dev
```

前端验收：

```text
1. 页面能打开。
2. 能上传教材。
3. 能解析教材。
4. 能构建图谱。
5. 能展示图谱。
6. 点击节点能显示详情。
7. 能执行整合。
8. 能显示压缩比和 merge/keep/remove。
9. 能建立 RAG 索引。
10. 能输入问题并显示回答和引用。
11. 能提交教师反馈并看到变化。
12. 能生成报告。
```

---

## 10. 最终提交检查清单

### 10.1 功能链路

```text
[ ] Web 页面可访问。
[ ] 上传至少 2 个教材。
[ ] 显示解析状态。
[ ] 显示章节结构。
[ ] 构建 KG nodes/edges。
[ ] 图谱可交互。
[ ] 跨教材整合。
[ ] 显示 merge/keep/remove。
[ ] 显示压缩比 < 30%。
[ ] 建立 RAG 索引。
[ ] 问答返回引用。
[ ] 教师反馈修改至少一项决策。
[ ] 生成整合报告。
```

### 10.2 仓库与文档

```text
[ ] GitHub 仓库 Public。
[ ] 在线部署链接可访问。
[ ] README.md 存在且可复现。
[ ] docs/需求分析.md 存在。
[ ] docs/系统设计.md 存在。
[ ] docs/Agent架构说明.md 存在。
[ ] docs/接口文档.md 存在或至少 README 中有接口说明。
[ ] report/整合报告.md 存在。
[ ] .gitignore 排除 PDF、textbooks、node_modules、.env。
[ ] requirements.txt 存在。
[ ] package.json 存在。
```

---

## 11. 当前 Codex 接手后的推荐执行顺序

本地 Codex 接手时，不要一上来重构。推荐执行：

```text
1. 扫描项目结构，确认实际文件与本文档是否一致。
2. 运行 python run.py，确认后端服务能启动。
3. 打开 /docs，记录实际 API。
4. 运行 python test_api.py。
5. 选择 textbooks 中最小 PDF 测试上传和解析。
6. 检查 data/metadata 的 JSON 输出。
7. 若模块一通过，git commit 锁定。
8. 实现 Codex A 或 B 中尚未完成的后端模块。
9. 实现前端或切换前端 mock 到真实 API。
10. 最后补齐 README/docs/report/.gitignore。
```

---

## 12. 给 Codex 的总控提示词

可以把下面这段直接发给本地 Codex：

```text
你现在接手 EduGraph Fusion｜智教材图谱融合系统。这是一个 AI 全栈极速黑客松项目，目标是在 5 小时内实现多教材上传解析、知识图谱构建、跨教材整合、RAG 引用问答、教师反馈、整合报告、前端展示和公网部署。

当前项目路径是：D:\我的大学\博一下\黑客松2。
已有 backend/problem/textbooks/.claude 等目录。textbooks 是赛事方教材数据，不要提交到 GitHub。模块一后端数据底座已由 Claude Code 完成，声称支持 PDF/Markdown/TXT 上传解析、章节结构化、JSON 持久化和 6 个基础 API：POST /api/upload、POST /api/parse/{id}、GET /api/textbooks、GET /api/textbooks/{id}、GET /api/stats、GET /api/textbooks/{id}/stats。

第一步不是继续开发，而是先验收模块一：启动 python run.py，打开 /docs，运行 python test_api.py，用 textbooks 中至少一个 PDF 和简单 md/txt 测试上传解析，确认 chapters 输出、data/metadata JSON 和重启后数据可读。

模块一通过后，不要破坏 parser.py、storage.py、upload.py、textbooks.py。继续按三个任务包推进：
A：知识图谱 + 跨教材整合，实现 /api/kg/build、/api/kg、/api/merge、/api/merge/decisions。
B：RAG + 教师反馈 + 报告生成，实现 /api/rag/index、/api/rag/query、/api/rag/status、/api/feedback、/api/report/generate。
C：前端 + 文档 + 部署，实现 React + Vite 单页应用、ECharts 图谱、RAG 问答、教师反馈、report/docs/README/.gitignore。

最小完赛链路是：打开 Web 页面 → 上传至少 2 个教材 → 显示解析状态和章节 → 构建 nodes/edges → 可交互图谱 → 跨教材整合 → 显示 merge/keep/remove 和压缩比 <30% → 建立 RAG 索引 → 问答返回引用 → 教师反馈修改至少一项整合决策 → 生成文档和报告 → GitHub Public + 在线部署链接。

请先检查现有文件，再根据本文档执行。不要重构已完成模块，不要做 Docker、BM25/Rerank、多视图图谱、复杂多 Agent、DOCX/Excel 优化等非必要功能。
```

---

## 13. 备注：tmux/psmux 分屏小信息

用户问过“psmux 如何上下分屏”，实际应为 `tmux`：

```text
Ctrl + b，然后按 "      # 上下分屏
Ctrl + b，然后按 %       # 左右分屏
Ctrl + b，然后按方向键   # 切换 pane
Ctrl + b，然后按 x       # 关闭当前 pane
Ctrl + b，然后按 z       # 当前 pane 最大化/恢复
```

该信息与项目代码无直接关系，仅供本地开发时多终端并行使用。

---

## 14. 最重要的风险点

1. **不要信完成总结，必须看真实运行结果。** 现在模块一总结很完整，但仍需 API 实测。
2. **接口数量存在口径不一致。** 用户曾说 8 个新 API，但总结列出 6 个端点；以 `/docs` 为准。
3. **后续模块依赖 chapters 数据结构。** 若 chapters 字段不稳定，KG/RAG/报告都会失败。
4. **不要把教材 PDF 推到 GitHub。** `textbooks/` 和 `*.pdf` 必须 gitignore。
5. **前端要有 mock fallback。** 后端未完全稳定时，前端仍需可展示。
6. **最后 40 分钟只联调。** 不再新增技术点。
7. **压缩比必须显示且小于 30%。** 必要时用内容截断策略保证。
8. **RAG 回答必须带引用。** 引用至少包含教材名、章节、页码。

---

## 15. 建议当前立刻执行的命令

```powershell
cd "D:\我的大学\博一下\黑客松2"
tree /f
python run.py
```

另开终端：

```powershell
cd "D:\我的大学\博一下\黑客松2"
python test_api.py
```

检查 Git 状态：

```powershell
git status
```

模块一通过后提交：

```powershell
git add .
git commit -m "complete module 1 backend textbook parser"
```

