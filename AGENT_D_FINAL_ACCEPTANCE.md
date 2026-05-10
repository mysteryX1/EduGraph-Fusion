# Agent D 最终验收测试结果

## 1. 测试时间

2026-05-10 14:22:11 +08:00

测试产物目录：

`D:\我的大学\博一下\黑客松2\test_artifacts\agent_d_final_20260510_142211`

## 2. Git 冻结是否满足

不完全满足。

测试前已存在功能代码改动：

- `backend/routers/feedback.py`
- `backend/routers/upload.py`
- `backend/services/feedback.py`
- `backend/services/rag.py`

测试前后没有发现新增功能代码改动。测试后新增或变化主要是：

- `data/processed/*`
- `report/整合报告.md`
- `test_artifacts/*`

这些属于测试链路产物变化。但由于冻结开始前工作区已非干净状态，本轮判定为：

**测试期间未新增功能代码变更，冻结前状态不干净。**

A/B/C 完成证据：本地可见 Agent A/B/C 对应完成或修复记录文件。

## 3. 前端端口

前端 dev server 实际端口：

`http://localhost:3000/`

返回 200。

`5173` 未启用。

## 4. 必测项结果

| 测试项 | 状态码 | 结果 |
| --- | --- | --- |
| `/health` | 200 | 通过，返回 healthy |
| 前端 dev server | 200 | 通过，实际端口 3000 |
| `npm.cmd run build` | 退出码 0 | 通过，存在 chunk size warning，可接受 |
| `/api/textbooks` | 200 | total=3；首位为 `reference_03_physiology.pdf`，未把假教材作为首屏第一重点；但列表中仍有疑似历史/演示教材 |
| 上传 `textbooks/03_生理学.pdf` 原始中文文件名 | 400 | 失败，返回 `Unsupported file type: . Allowed: .markdown, .txt, .md, .pdf` |
| 解析中文文件名教材 | 未执行 | 上传未返回 `textbook_id` |
| `/api/kg/build` | 200 | 通过 |
| `/api/kg` | 200 | 通过，nodes=86，edges=235 |
| `/api/merge` | 200 | 通过 |
| `/api/merge/decisions` | 200 | 通过，decisions=15，compression_ratio=0.2263 |
| `/api/rag/index` | 200 | 通过 |
| `/api/rag/query` | 200 | 通过，answer 长度 607，citations=5 |
| RAG 后端日志 | - | 未再出现 `list object has no attribute get` |
| `/api/feedback`，body `{ "instruction": "保留 函数" }` | 200 | 通过 |
| `/api/report/generate` | 200 | 通过 |
| `/api/report/latest` | 200 | 通过，Markdown 正文长度 2385 |

## 5. 是否可演示

**不可演示。**

最终判定标准要求：

- 反馈 200
- 中文文件名上传 200
- 假教材不再作为默认展示重点

本轮反馈已通过，假教材未作为首屏第一重点，但 **中文文件名上传仍为 400**，因此不可演示。

## 6. 是否可部署到公网

**不可部署。**

前端 build 通过，KG、Merge、RAG、Feedback、Report 主链路通过；但上传中文原始教材这一核心入口失败，后端主链路未完全通过。

## 7. 剩余风险

1. 中文文件名 PDF 上传仍失败，阻断演示入口。
2. 教材列表仍残留疑似历史/演示教材，只是当前未排在第一。
3. Git 冻结前功能代码已处于 modified 状态，缺少干净验收基线。
4. Chrome/Edge headless 截图此前受 GPU fatal 影响，未做完整视觉截图验收。

## 8. 最终判定

当前版本：

- **不可演示**
- **不可准备公网部署**

主要阻断项：

`textbooks/03_生理学.pdf` 原始中文文件名上传必须返回 200，目前实际返回 400。
