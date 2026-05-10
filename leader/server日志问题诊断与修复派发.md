# Server 日志问题诊断与修复派发

## 日志结论

用户提供的后端日志显示：

```text
LLM call failed: litellm.BadRequestError: LLM Provider NOT provided...
POST /api/rag/query HTTP/1.1 200 OK
GET /api/merge/decisions HTTP/1.1 500 Internal Server Error
POST /api/feedback HTTP/1.1 422 Unprocessable Entity
```

### 1. RAG LLM 报错不是当前阻断

`litellm.BadRequestError` 说明当前 `model=qwen3-32b` 没有指定 provider，LiteLLM 无法调用真实模型。

但日志里紧接着：

```text
POST /api/rag/query HTTP/1.1 200 OK
```

说明 RAG fallback 已返回结果。当前阶段不必优先修真实 LLM，除非最终演示必须接真实模型。

建议：

- 后端应减少这个错误对演示的干扰。
- 如果没有配置完整 LLM provider，就不要尝试 litellm，直接走 fallback。

### 2. `/api/merge/decisions` 500 是真实阻断

高概率原因：

- A 模块 `merger.py` 早期把 `merge_decisions.json` 写成 list。
- B 模块 feedback 兼容后可能把它写成 dict：`{"decisions": [...], "updated_at": "..."}`
- `backend/routers/merge.py` 的 `get_merge_decisions()` 仍假设 `node_merger.get_decisions()` 返回 list，并直接：

```python
for d in decisions:
    d['decision']
```

当 `decisions` 实际是 dict 时，遍历到的是 key 字符串，引发 500。

必须修为同时兼容 list 与 dict。

### 3. `/api/feedback` 422 是前端请求体字段不匹配

后端 `backend/routers/feedback.py` 要求：

```json
{
  "instruction": "保留 函数"
}
```

422 说明前端大概率发送了错误结构，例如：

```json
{
  "feedback": "...",
  "content": "...",
  "text": "..."
}
```

必须修 `frontend/src/components/FeedbackPanel.jsx` 和/或 `frontend/src/api.js`，确保传给后端的是 `instruction` 字段。

## 最新任务派发

### Agent Backend-Fix：修复 merge decisions、feedback 兼容、LLM fallback 噪声

负责：

- `backend/routers/merge.py`
- `backend/services/merger.py`
- `backend/services/feedback.py`
- `backend/services/rag.py`

不要改：

- `backend/services/parser.py`
- `backend/services/storage.py`
- `textbooks/`
- `problem/`

验收：

- `GET /api/merge/decisions` 不再 500。
- `POST /api/feedback` 接收 `{ "instruction": "保留 函数" }` 返回 200。
- 未配置 LiteLLM provider 时，RAG 不应刷红色错误堆栈，直接 fallback。

### Agent Frontend-Fix：修复 feedback 请求体、merge panel、RAG/报告显示

负责：

- `frontend/src/api.js`
- `frontend/src/components/FeedbackPanel.jsx`
- `frontend/src/components/MergePanel.jsx`
- `frontend/src/components/RagPanel.jsx`
- `frontend/src/components/ReportPanel.jsx`

验收：

- 教师反馈提交时请求体是 `{ instruction: "..." }`。
- MergePanel 调 `/api/merge/decisions` 时兼容 `data.decisions` 和 `data.statistics`。
- RAG 查询失败或 fallback 时页面不白屏。
- 报告生成后能显示正文；如果 generate 不返回正文，则继续调用 `/api/report/latest`。

### Agent Test：只做复测

只测试，不改代码。

重点复测：

- `/api/merge/decisions`
- `/api/feedback`
- 前端教师反馈按钮
- 前端整合决策面板
- RAG 输入后不白屏
- 报告生成后显示正文

