# Agent D 直接修复与测试提示词

更新时间：2026-05-10 14:35 CST

## 当前策略

比赛剩余时间很少，现在不再分散给 A/B/C。Agent D 直接负责“修改 + 测试 + 验收”，优先保证网页可演示。

不要继续追求大范围提分项。AI 评审报告里的 Docker、LLM、文档补分都先放后。当前演示阻断优先级更高。

## 给 Agent D 的完整提示词

你是 Agent D。现在请你直接修改代码并完成本地测试，不再只做测试。目标是在最短时间内把项目修到“网页可演示”。

工作目录：

```powershell
D:\我的大学\博一下\黑客松2
```

运行环境：

```powershell
# 后端
cd "D:\我的大学\博一下\黑客松2"
& "D:\software\anaconda\envs\edu\python.exe" run.py

# 前端
cd "D:\我的大学\博一下\黑客松2\frontend"
& "C:\Program Files\nodejs\npm.cmd" run dev
```

前端实际地址以命令输出为准，当前通常是：

```text
http://localhost:3000/
```

## 必须修复的问题

### P0-1：RAG 检索输入后网页出问题

用户手动测试发现：网页中进行检索时，输入问题后仍然会出现页面问题。

请优先检查并修复：

- `frontend/src/components/RagPanel.jsx`
- `frontend/src/api.js`
- 必要时只读 `backend/routers/rag.py`
- 必要时只读 `backend/services/rag.py`

已知高风险点：

`RagPanel.jsx` 里疑似存在 JSX 或字符串损坏，例如：

- `<div className="section-title">.../div>` 这种未正确闭合标签。
- 模板字符串未闭合。
- 中文字符串 mojibake 后导致引号、反引号、标签结构损坏。
- catch 分支拼接字符串可能写坏。

修复要求：

1. 先让 `frontend` 能稳定 `npm.cmd run build`。
2. RAG 面板所有 JSX 必须语法正确，不允许白屏。
3. 点击“构建索引”后能显示索引状态。
4. 输入问题并点击搜索后，即使后端返回异常，也只能在面板内显示错误消息，不能让整个网页崩溃。
5. 对后端返回字段做防御式兼容：
   - `answer` 缺失时显示“未找到相关答案”
   - `citations` 不是数组时转为空数组
   - `source_chunks` 不是数组时转为空数组
6. 不要依赖真实 LLM，fallback 可接受。

建议直接把 `RagPanel.jsx` 清理成一份简洁、语法正确的组件。不要保留乱码字符串。界面中文可直接用正常中文。

验收：

```powershell
cd "D:\我的大学\博一下\黑客松2\frontend"
& "C:\Program Files\nodejs\npm.cmd" run build
```

然后浏览器测试：

1. 打开前端。
2. 进入 RAG/检索面板。
3. 如果未建索引，先点击构建索引。
4. 输入“什么是函数？”或“血液循环的调节机制是什么？”。
5. 点击搜索。
6. 页面不能白屏，必须显示答案或错误提示。

### P0-2：知识图谱不能是均匀球形，要体现关键节点拓扑

用户反馈：当前知识图谱连接关系都是均匀的球形，不像根据关键程度展开的拓扑关系。

请修改：

- `frontend/src/components/GraphView.jsx`
- 必要时 `frontend/src/styles/index.css`

目标：

1. 节点大小必须体现重要程度：
   - degree 越高越大
   - frequency/value 越高越大
   - symbolSize 建议范围 24-90
2. 图谱布局不能平均成球：
   - 核心节点靠中心
   - 边缘节点向外散开
   - 关系强的边更短
   - 关系弱的边更长
3. ECharts force 配置要按数据动态调整：
   - `repulsion` 可设为函数或按节点重要度赋值
   - `edgeLength` 可用 `[60, 220]` 或按 relation/value 调整
   - `gravity` 不要过高，避免所有节点挤成球
   - `layoutAnimation` 可开启但不要影响可读性
4. 边样式要体现关系：
   - `contains/prerequisite/parallel/related` 用不同颜色
   - 重要边更粗
   - opacity 适中，避免一团线
5. 保留节点点击详情。

建议实现方式：

- 先统计每个节点 degree。
- 计算 `importance = degree * 2 + log(frequency + 1)`。
- `symbolSize = clamp(24 + importance * 4, 24, 90)`。
- 节点设置 `value = importance`。
- 对 link 设置 `value` 和 `lineStyle.width`。
- `force.edgeLength` 使用 `[70, 210]`，或者按边强度设置。
- `force.repulsion` 使用 260-900 的范围，至少比现在更强。
- `force.gravity` 降到 0.03-0.06。

验收：

1. 图谱中能明显看到核心大节点和外围小节点。
2. 不是所有点均匀分布成一个球。
3. 边关系颜色可区分。
4. 点击节点后右侧详情仍可显示。

### P0-3：节点文字和背景对比度

用户反馈：每个节点上的字需要和背景有对比度，可以黑色字，或者把背景变黑。

当前建议采用“浅色节点 + 黑色文字 + 白色/浅灰画布”，因为更容易演示和截图。

修改要求：

1. 节点 label 颜色改为黑色或近黑色，例如 `#111827`。
2. 节点 label 加白色文字描边或背景，避免压在彩色节点上看不清：
   - `textBorderColor: '#ffffff'`
   - `textBorderWidth: 2`
3. 如果 label 放在节点内部仍然不清楚，可改为：
   - 核心节点 `position: 'inside'`
   - 小节点 `position: 'right'`
4. 不要再用白字压在浅色节点上。
5. 图谱容器背景可以保持浅色；如果改黑色背景，则全部 label、边、tooltip 都要同步适配。时间有限，优先浅色背景 + 黑字。

验收：

- 节点文字肉眼可读。
- 中文概念名不会因为背景颜色相近而看不见。
- 字体不要过大，避免遮挡；建议 10-13px。

### P0-4：中文文件名 PDF 上传仍然 400

Agent D 最终验收报告显示：

```text
上传 textbooks/03_生理学.pdf 原始中文文件名 -> 400
Unsupported file type: . Allowed: .markdown, .txt, .md, .pdf
```

这个报错说明后端拿到的 suffix 为空，不能识别中文文件名里的 `.pdf`。

请检查并修复：

- `backend/routers/upload.py`
- 必要时 `backend/services/parser.py`

要求：

1. 对上传文件名做更稳健的扩展名识别。
2. 如果 `Path(filename).suffix` 为空，但 `content_type` 是 `application/pdf`，应识别为 `.pdf`。
3. 如果文件名经过编码后丢失后缀，可以从原始 `UploadFile.content_type` fallback。
4. 中文文件名 `03_生理学.pdf` 必须上传 200。
5. 不要放开所有文件类型，只允许现有白名单。

建议逻辑：

```python
suffix = Path(file.filename or "").suffix.lower()
if not suffix and file.content_type == "application/pdf":
    suffix = ".pdf"
```

如果发现 `filename` 已经被 Starlette/FastAPI 解码成乱码但仍包含 `.pdf`，则用正则从字符串末尾提取：

```python
match = re.search(r"(\.[A-Za-z0-9]+)$", filename)
```

验收：

- `textbooks/03_生理学.pdf` 上传 200。
- ASCII 文件名 PDF 上传仍然 200。
- 非支持格式仍然 400。

## 测试顺序

请按这个顺序执行，不要跳：

1. `npm.cmd run build`，必须先通过，确认前端语法没有坏。
2. 启动后端，测 `/health`。
3. 启动前端，打开页面。
4. 测 RAG：
   - 构建索引
   - 输入问题
   - 搜索
   - 页面不能白屏
5. 测图谱：
   - 打开知识图谱
   - 观察是否有核心节点/边缘节点层次
   - 检查节点文字是否清晰
   - 点击节点，看详情是否正常
6. 测中文 PDF 上传：
   - 上传 `textbooks/03_生理学.pdf`
   - 解析
7. 最后再跑一次：
   ```powershell
   cd "D:\我的大学\博一下\黑客松2\frontend"
   & "C:\Program Files\nodejs\npm.cmd" run build
   ```

## 输出要求

完成后请提交一份简短报告，包含：

1. 修改了哪些文件。
2. RAG 检索白屏/崩溃是否已修复。
3. 图谱拓扑是否已从均匀球形改成核心-外围结构。
4. 节点文字对比度是否已修复。
5. 中文文件名 PDF 上传是否 200。
6. `npm.cmd run build` 是否通过。
7. 仍然存在的风险，不超过 5 条。

## 禁止事项

1. 不要再做 Docker、LLM 接入、BM25、桑基图等加分项。
2. 不要重构整个前端。
3. 不要删除用户数据。
4. 不要改 `textbooks/` 原始文件。
5. 不要把测试产物误当成源码提交。

