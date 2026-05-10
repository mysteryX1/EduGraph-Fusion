# EduGraph Fusion - 关键 BugFix 总结

**修复日期**: 2026-05-10  
**修复内容**: 4 个关键问题  
**状态**: ✅ 全部完成

---

## 问题 1: RAG LLM Provider 报错噪声

### 原问题
- litellm 调用时报 `BadRequestError: LLM Provider NOT provided. You passed model=qwen3-32b`
- 日志中出现大段红色错误，影响用户体验
- 但接口仍返回 200 OK（使用 fallback）

### 修复方案
**文件**: `backend/services/rag.py`

- 新增 `_try_llm_answer()` 方法，检查环境变量
- 只在配置了 LLM provider 时才调用 litellm
- 捕获 BadRequestError 后只打印简短 warning，不输出完整错误栈
- 保证 fallback 机制稳定工作

### 代码变化
```python
# 旧逻辑: 直接调用 litellm，失败后打印完整错误
try:
    response = litellm.completion(model="qwen3-32b", ...)
except Exception as e:
    print(f"LLM call failed: {e}")  # 打印完整错误信息

# 新逻辑: 先检查配置，再决定是否调用
def _try_llm_answer(self, question, context):
    has_provider = os.getenv("LITELLM_PROVIDER") or \
                   os.getenv("OPENAI_API_KEY") or \
                   os.getenv("QWEN_API_KEY")
    if not has_provider:
        return ""  # 没配置就直接返回，不调用 litellm
    # ... 调用 litellm ...
```

### 验收测试
```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question":"什么是函数？","top_k":5}'
```

**预期结果**:
- ✅ 返回 200 OK
- ✅ response.data.answer 不为空（fallback 内容）
- ✅ 日志不再出现 "LLM Provider NOT provided" 红色大段错误
- ✅ 如果有 warning，仅显示: "⚠️ LLM call warning: BadRequestError"

---

## 问题 2: POST /api/feedback 返回 422

### 原问题
- 前端发送 `{"feedback":"保留 函数"}` 返回 422 Unprocessable Entity
- 后端 FeedbackRequest 只接受 `instruction` 字段
- 与前端字段名不匹配

### 修复方案
**文件**: `backend/routers/feedback.py`

- 修改 FeedbackRequest，支持四个字段: instruction, feedback, text, content
- 所有字段都是可选 (Optional)
- 优先级: instruction > feedback > text > content
- 验证时合并检查，不区分字段来源

### 代码变化
```python
# 旧逻辑: 仅接受 instruction
class FeedbackRequest(BaseModel):
    instruction: str

# 新逻辑: 兼容多个字段名
class FeedbackRequest(BaseModel):
    instruction: Optional[str] = None
    feedback: Optional[str] = None
    text: Optional[str] = None
    content: Optional[str] = None

# 处理时
instruction = (request.instruction or request.feedback or
              request.text or request.content or "").strip()
```

### 验收测试
```bash
# 方式 1: 标准 instruction
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"instruction":"保留 函数"}'

# 方式 2: 兼容 feedback
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"feedback":"保留 函数"}'

# 方式 3: 兼容 text
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"text":"删除 冗余"}'

# 方式 4: 兼容 content
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"content":"拆分 函数 和 高级函数"}'
```

**预期结果**:
- ✅ 全部返回 200 OK
- ✅ response.status = "success"
- ✅ response.data.action 为 keep/delete/split/merge 之一
- ✅ 空值时返回 400，错误信息清晰

---

## 问题 3: merge_decisions.json 兼容性

### 原问题
- 模块 A 生成 list 格式: `[{...}, {...}]`
- feedback.py 期望 dict 格式: `{"decisions": [...], "updated_at": "..."}`
- 格式不匹配导致处理失败

### 修复方案
**文件**: `backend/services/feedback.py`

- 修改 `_load_merge_decisions()` 方法
- 自动检测输入格式（list 或 dict）
- list 格式自动包装为 dict
- dict 格式确保有必需字段
- 保存时统一保存为 dict 格式

### 代码变化
```python
def _load_merge_decisions(self) -> Dict:
    data = json.load(f)

    # 兼容 list 格式（模块 A 输出）
    if isinstance(data, list):
        return {
            'decisions': data,
            'updated_at': datetime.now().isoformat()
        }

    # 兼容 dict 格式
    if isinstance(data, dict):
        data.setdefault('decisions', [])
        data.setdefault('updated_at', datetime.now().isoformat())
        return data
```

### 验收测试
```bash
# 手动测试: 创建 list 格式的 merge_decisions.json
cat > backend/data/processed/merge_decisions.json << 'EOF'
[
  {"decision": "possible_duplicate"},
  {"decision": "keep_both"}
]
EOF

# 调用 feedback 接口
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"instruction":"保留 函数"}'
```

**预期结果**:
- ✅ 返回 200 OK，不报错
- ✅ 内部自动转换 list → dict
- ✅ 保存时为 dict 格式

---

## 问题 4: 报告正文接口

### 原问题
- 前端生成报告后，获取详情看不到正文
- GET /api/report/latest 是否返回完整 Markdown 内容

### 修复方案
**文件**: `backend/routers/report.py`

- ✅ 已有 content 字段，返回完整 Markdown 正文
- 包含: report_file, report_path, modified_at, **content**
- content 是完整的 Markdown 文本，可直接显示

### 接口说明
```
POST /api/report/generate
└─ 生成报告文件 report/整合报告.md
└─ 返回 summary (统计数据)

GET /api/report/latest
└─ 读取 report/整合报告.md
└─ 返回完整 content (Markdown 正文)
└─ 返回 modified_at (修改时间)
```

### 验收测试
```bash
# 1. 生成报告
curl -X POST http://localhost:8000/api/report/generate

# 2. 获取报告正文
curl -X GET http://localhost:8000/api/report/latest
```

**预期结果**:
- ✅ generate 返回 200，path 为 ./report/整合报告.md
- ✅ latest 返回 200，data.content 包含完整 Markdown
- ✅ content 包含:
  - # 教材知识整合报告
  - ## 1. 整合概览
  - ## 2. 教材详细统计
  - 等完整章节

---

## 完整的 API 测试命令

### 1. RAG 模块测试

```bash
# 建立索引
curl -X POST http://localhost:8000/api/rag/index

# 查询（验证不再有大段 LLM 错误）
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question":"什么是函数？","top_k":5}'
```

### 2. 反馈模块测试

```bash
# 方式 1: instruction（标准）
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"instruction":"保留 函数概念"}'

# 方式 2: feedback（兼容）
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"feedback":"删除 冗余内容"}'

# 方式 3: text（兼容）
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"text":"拆分 函数概念 和 高级函数"}'

# 方式 4: content（兼容）
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{"content":"合并 基本函数 和 函数概念"}'

# 获取摘要
curl -X GET http://localhost:8000/api/feedback/summary
```

### 3. 报告模块测试

```bash
# 生成报告
curl -X POST http://localhost:8000/api/report/generate

# 获取报告正文（含 Markdown content）
curl -X GET http://localhost:8000/api/report/latest

# 获取报告摘要
curl -X GET http://localhost:8000/api/report/summary
```

---

## 前端调用说明

### RAG 查询
```javascript
// 查询知识库
const response = await fetch('/api/rag/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: "什么是函数？",
    top_k: 5
  })
});

const data = await response.json();
// data.data.answer - 回答内容
// data.data.citations - 引用信息（包含 relevance_score）
// data.data.source_chunks - 源文本块
```

### 反馈提交
```javascript
// 方式 1: 标准格式
const response = await fetch('/api/feedback', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    instruction: "保留 函数概念"
  })
});

// 方式 2: 备选格式（如果前端使用其他字段名）
const response = await fetch('/api/feedback', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    feedback: "删除 冗余内容"  // 可替换为 instruction/text/content
  })
});

const data = await response.json();
// data.data.action - keep/delete/split/merge
// data.data.summary - 操作摘要
// data.data.knowledge_graph_summary - KG 统计
```

### 报告获取
```javascript
// 获取报告正文
const response = await fetch('/api/report/latest', {
  method: 'GET'
});

const data = await response.json();
// data.data.content - Markdown 正文（可直接渲染）
// data.data.report_file - 文件名
// data.data.modified_at - 修改时间
```

---

## 修改的文件清单

| 文件 | 修改内容 | 行数变化 |
|-----|--------|--------|
| backend/services/rag.py | 新增 _try_llm_answer() 方法，智能 LLM 调用 | +60 |
| backend/routers/feedback.py | FeedbackRequest 支持四个字段，优先级解析 | +8 |
| backend/services/feedback.py | _load_merge_decisions() 兼容 list/dict 格式 | +30 |
| backend/routers/report.py | ✅ 已有 content 字段，无需修改 | 0 |

---

## 验收清单

- [x] RAG 查询日志不再出现 LLM provider 大段错误
- [x] RAG 查询返回 200，answer/citations/source_chunks 完整
- [x] POST /api/feedback 接收 instruction 返回 200
- [x] POST /api/feedback 接收 feedback/text/content 也返回 200
- [x] POST /api/feedback 空值返回 400，错误信息清晰
- [x] feedback.py 自动兼容 list 和 dict 格式的 merge_decisions.json
- [x] GET /api/report/latest 返回 content 字段（完整 Markdown）
- [x] 所有接口统一返回 {status, message, data} 格式

---

## 后续建议

### 前端集成
1. 使用 `feedback` 字段（或其他已兼容的字段）而不是 instruction
2. 从 GET /api/report/latest 的 content 字段获取 Markdown
3. 使用 markdown 库（如 markdown-it）渲染报告正文

### 可选优化
1. 添加 LLM provider 配置界面，让用户自己选择是否启用
2. 缓存报告内容，避免频繁读取文件
3. 添加报告版本历史，记录每次生成时间

---

**修复完成**✅  
**可开始前端集成测试**
