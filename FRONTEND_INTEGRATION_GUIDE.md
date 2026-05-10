# EduGraph Fusion - 前端集成指南

**目标**: Agent C 前端如何调用后端 API  
**状态**: ✅ 后端已准备好，可开始集成

---

## 🎯 三大模块集成

### 模块 1: RAG 知识库查询

#### 1.1 建立索引（初始化）
```javascript
async function initializeRAG() {
  const response = await fetch('/api/rag/index', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });

  const data = await response.json();
  // data.data = {
  //   indexed: true,
  //   chunk_count: 4,
  //   textbook_count: 1
  // }
  return data.data;
}
```

#### 1.2 查询知识库（用户输入）
```javascript
async function queryKnowledgeBase(question, topK = 5) {
  const response = await fetch('/api/rag/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: question,
      top_k: topK
    })
  });

  const data = await response.json();
  // data.data = {
  //   question: "什么是函数？",
  //   answer: "基于《...》的《...》章节，相关内容为...",
  //   citations: [
  //     {
  //       textbook: "高等数学基础教材",
  //       chapter: "第一章 基础概念",
  //       chapter_id: "ch1",
  //       page_number: 1,
  //       chunk_id: "ch1_0",
  //       text_excerpt: "基础概念是学习任何学科的基础...",
  //       relevance_score: 0.95
  //     },
  //     ...
  //   ],
  //   source_chunks: [
  //     {
  //       id: "ch1_0",
  //       content: "基础概念是学习...",
  //       similarity: 0.95,
  //       metadata: {...}
  //     }
  //   ]
  // }

  return {
    question: data.data.question,
    answer: data.data.answer,
    citations: data.data.citations,
    sources: data.data.source_chunks
  };
}
```

#### 1.3 获取索引状态
```javascript
async function getRAGStatus() {
  const response = await fetch('/api/rag/status', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });

  const data = await response.json();
  // data.data = {
  //   indexed: true,
  //   chunk_count: 4,
  //   textbook_count: 1
  // }
  return data.data;
}
```

**前端展示**:
- [ ] 显示答案 (data.answer)
- [ ] 显示引用来源 (data.citations，包含 relevance_score)
- [ ] 可选：显示源文本块 (data.source_chunks)
- [ ] 异常处理：如果 answer 为 "当前知识库中未找到相关信息"，显示提示

---

### 模块 2: 教师反馈（知识图谱编辑）

#### 2.1 提交反馈（自然语言指令）
```javascript
async function submitFeedback(instruction) {
  // 支持的格式：
  // - "保留 函数概念"
  // - "删除 冗余内容"
  // - "拆分 函数 和 高级函数"
  // - "合并 基本函数 和 函数概念"

  const response = await fetch('/api/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      instruction: instruction  // 或使用 feedback/text/content 字段
    })
  });

  const data = await response.json();
  // data = {
  //   status: "success",
  //   message: "已标记保留：函数概念",
  //   data: {
  //     instruction: "保留 函数概念",
  //     action: "keep",  // keep/delete/split/merge
  //     summary: "已标记保留：函数概念",
  //     knowledge_graph_summary: {
  //       total_decisions: 4,
  //       keep_count: 1,
  //       delete_count: 1,
  //       split_count: 1,
  //       merge_count: 1,
  //       kg_nodes: 3,
  //       kg_edges: 2,
  //       last_updated: "2026-05-10T..."
  //     }
  //   }
  // }

  return {
    action: data.data.action,
    summary: data.data.summary,
    stats: data.data.knowledge_graph_summary
  };
}

// 兼容模式（前端可用其他字段名）
async function submitFeedbackAlt(feedbackText, fieldName = 'instruction') {
  const body = {};
  body[fieldName] = feedbackText;  // instruction/feedback/text/content

  const response = await fetch('/api/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });

  return await response.json();
}
```

#### 2.2 获取反馈摘要
```javascript
async function getFeedbackSummary() {
  const response = await fetch('/api/feedback/summary', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });

  const data = await response.json();
  // data.data = {
  //   total_decisions: 4,
  //   keep_count: 1,
  //   delete_count: 1,
  //   split_count: 1,
  //   merge_count: 1,
  //   kg_nodes: 3,
  //   kg_edges: 2,
  //   last_updated: "2026-05-10T..."
  // }

  return data.data;
}
```

**前端展示**:
- [ ] 显示操作摘要 (data.summary)
- [ ] 显示知识图谱统计 (stats.total_decisions, stats.kg_nodes 等)
- [ ] 操作历史：显示 keep_count, delete_count, split_count, merge_count
- [ ] 异常处理：
  - 如果返回 400，显示错误信息 (detail 字段)
  - 如果是空值错误，提示 "请输入有效的指令"
  - 支持的指令格式示例

**指令验证**:
```javascript
const validInstructions = [
  "保留 [内容名]",
  "删除 [内容名]",
  "拆分 [名A] 和 [名B]",
  "合并 [名A] 和 [名B]"
];

function validateInstruction(text) {
  const patterns = [
    /^保留\s+\S+$/,
    /^删除\s+\S+$/,
    /^拆分\s+\S+\s+和\s+\S+$/,
    /^合并\s+\S+\s+和\s+\S+$/
  ];

  return patterns.some(p => p.test(text));
}
```

---

### 模块 3: 报告生成

#### 3.1 生成报告
```javascript
async function generateReport() {
  const response = await fetch('/api/report/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });

  const data = await response.json();
  // data.data = {
  //   report_file: "整合报告.md",
  //   report_path: "./report/整合报告.md",
  //   generated_at: "2026-05-10T13:00:00...",
  //   summary: {
  //     textbooks: 1,
  //     original_words: 195,
  //     merged_words: 156,
  //     compression_ratio: 20.0,
  //     keep_count: 1,
  //     remove_count: 0,
  //     merge_count: 1,
  //     kg_nodes: 2,
  //     kg_edges: 1
  //   }
  // }

  return data.data;
}
```

#### 3.2 获取报告正文（完整 Markdown）
```javascript
async function getReportContent() {
  const response = await fetch('/api/report/latest', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });

  const data = await response.json();
  // data.data = {
  //   report_file: "整合报告.md",
  //   report_path: "./report/整合报告.md",
  //   modified_at: 1715386800.0,
  //   content: "# 教材知识整合报告\n\n**生成时间**：...\n\n## 1. 整合概览\n..."
  // }

  return {
    filename: data.data.report_file,
    path: data.data.report_path,
    modifiedAt: new Date(data.data.modified_at * 1000),
    markdown: data.data.content  // 完整 Markdown 内容
  };
}

// 使用 markdown 库渲染
async function displayReport() {
  const report = await getReportContent();

  // 需要安装 markdown 库，例如：
  // npm install markdown-it
  // import MarkdownIt from 'markdown-it';
  // const md = new MarkdownIt();

  // const html = md.render(report.markdown);
  // document.getElementById('report-container').innerHTML = html;

  return report;
}
```

#### 3.3 获取报告摘要
```javascript
async function getReportSummary() {
  const response = await fetch('/api/report/summary', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });

  const data = await response.json();
  // data.data = {
  //   textbooks: {
  //     total: 1,
  //     original_words: 195,
  //     merged_words: 156,
  //     compression_ratio: 20.0
  //   },
  //   knowledge_graph: {
  //     nodes: 2,
  //     edges: 1,
  //     node_types: {
  //       concept: 2
  //     }
  //   },
  //   decisions: {
  //     keep: 1,
  //     remove: 0,
  //     merge: 1,
  //     split: 0,
  //     total: 2
  //   }
  // }

  return data.data;
}
```

**前端展示**:
- [ ] 显示生成时间 (generated_at)
- [ ] 显示摘要统计 (summary.*)
- [ ] 显示完整报告正文 (content - Markdown 格式)
- [ ] 使用 markdown 库渲染 Markdown → HTML
- [ ] 可选：显示详细统计 (knowledge_graph, decisions)

---

## 📦 依赖库建议

### 用于渲染 Markdown
```bash
npm install markdown-it
npm install @types/markdown-it  # TypeScript 支持

# 或使用其他库
npm install marked
npm install remark react-markdown
```

### 示例代码
```javascript
// markdown-it 示例
import MarkdownIt from 'markdown-it';

const md = new MarkdownIt();
const htmlContent = md.render(markdownText);

// marked 示例
import { marked } from 'marked';
const htmlContent = marked(markdownText);

// react-markdown 示例（React）
import ReactMarkdown from 'react-markdown';
<ReactMarkdown>{markdownText}</ReactMarkdown>
```

---

## 🔄 完整工作流

### 用户场景 1: 查询知识库
```
1. 用户输入问题
2. 前端调用 queryKnowledgeBase()
3. 后端返回 answer + citations + source_chunks
4. 前端展示：
   - 答案内容
   - 来源信息（教材、章节、相关度）
   - 可选：源文本块
```

### 用户场景 2: 编辑知识图谱
```
1. 用户输入反馈指令（例如 "保留 函数")
2. 前端验证指令格式
3. 前端调用 submitFeedback()
4. 后端返回 action + summary + stats
5. 前端展示：
   - 操作确认信息
   - KG 统计更新（节点数、边数、决策计数）
```

### 用户场景 3: 生成和查看报告
```
1. 用户点击"生成报告"
2. 前端调用 generateReport()
3. 后端生成并返回 summary
4. 用户点击"查看报告"
5. 前端调用 getReportContent()
6. 后端返回完整 Markdown content
7. 前端使用 markdown 库渲染 HTML 显示
```

---

## ⚠️ 常见错误处理

### 错误 1: 422 Unprocessable Entity
**原因**: 请求体格式错误  
**解决**:
```javascript
// ✓ 正确
{ "instruction": "保留 函数" }
{ "feedback": "保留 函数" }
{ "text": "保留 函数" }

// ✗ 错误
{ "instruct": "保留 函数" }  // 字段名错误
{ }  // 缺少字段
```

### 错误 2: 400 Bad Request
**原因**: 空值或无效指令  
**解决**:
```javascript
const instruction = userInput.trim();
if (!instruction) {
  alert("请输入有效的指令");
  return;
}

// 可选：验证格式
if (!validateInstruction(instruction)) {
  alert("指令格式无效。支持：保留/删除/拆分/合并");
  return;
}
```

### 错误 3: 报告内容为空
**原因**: 数据不足  
**解决**:
```javascript
const report = await getReportContent();
if (!report.markdown || report.markdown.length === 0) {
  console.log("报告正在生成，请稍候...");
} else {
  renderMarkdown(report.markdown);
}
```

---

## 📝 API 响应格式统一

所有接口都遵循以下格式：
```javascript
{
  "status": "success" | "error",
  "message": "描述信息",
  "data": {
    // 具体数据
  }
}
```

**错误响应示例**:
```javascript
{
  "status": "error",
  "message": "Instruction/feedback/text/content cannot be empty",
  "detail": "具体错误说明"
}
```

---

## 🧪 调试技巧

### 1. 检查网络请求
```javascript
// 启用详细日志
fetch(url, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
})
.then(res => {
  console.log('Status:', res.status);
  return res.json();
})
.then(data => {
  console.log('Response:', data);
});
```

### 2. 使用浏览器开发者工具
- 打开 F12 → Network 标签
- 查看每个请求的 Request/Response
- 检查状态码是否为 200

### 3. 测试 curl 命令
```bash
# 直接测试后端 API
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"instruction":"保留 函数"}'
```

---

## 🚀 集成清单

- [ ] 实现 RAG 查询功能
  - [ ] 初始化索引 (/api/rag/index)
  - [ ] 查询知识库 (/api/rag/query)
  - [ ] 获取索引状态 (/api/rag/status)
  
- [ ] 实现反馈功能
  - [ ] 提交反馈 (/api/feedback)
  - [ ] 获取摘要 (/api/feedback/summary)
  - [ ] 指令验证

- [ ] 实现报告功能
  - [ ] 生成报告 (/api/report/generate)
  - [ ] 获取报告正文 (/api/report/latest)
  - [ ] 获取报告摘要 (/api/report/summary)
  - [ ] 使用 markdown 库渲染

- [ ] 错误处理
  - [ ] 网络错误
  - [ ] 验证错误（400）
  - [ ] 服务器错误（500）

- [ ] UI 优化
  - [ ] Loading 状态
  - [ ] 成功提示
  - [ ] 错误提示
  - [ ] 数据缓存

---

**后端已准备就绪 ✅**  
**前端可开始集成！**
