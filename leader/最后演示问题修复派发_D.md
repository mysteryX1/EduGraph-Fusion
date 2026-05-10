# 最后演示问题修复派发：交给 Agent D

更新时间：2026-05-10 14:55 CST

## 当前人工测试问题

Agent D 已完成上一轮本地验证，但用户继续网页测试后发现 3 个演示问题：

1. 上传/选择一本教材后，构建或查看知识图谱时，其他教材的内容也显示在图谱里。用户期望：点击左侧某一本教材时，中间知识图谱只显示这一本书的知识图谱。
2. 图谱中有一些和知识点无关的节点内容，需要过滤掉。
3. RAG 检索可以返回答案，但参考来源只显示 `[object Object]`，没有具体显示是哪本书、哪一章、哪一页。
4. 报告内容后端生成正常，但前端没有显示出来。

这些都是最终演示阻断项。当前不要再做 Docker、LLM、文档加分项，先让网页演示闭环正确。

## 给 Agent D 的完整提示词

你是 Agent D。请继续直接修改并测试。现在只修 4 个最终演示问题，不要扩大范围。

工作目录：

```powershell
D:\我的大学\博一下\黑客松2
```

环境：

```powershell
# 后端
cd "D:\我的大学\博一下\黑客松2"
& "D:\software\anaconda\envs\edu\python.exe" run.py

# 前端
cd "D:\我的大学\博一下\黑客松2\frontend"
& "C:\Program Files\nodejs\npm.cmd" run dev
```

## P0-1：图谱必须按当前选中教材过滤

用户期望：点击左侧某一本教材后，中间图谱只显示这一本书的知识图谱，不要混入其他教材节点。

重点检查：

- `frontend/src/App.jsx`
- `frontend/src/components/GraphView.jsx`
- `frontend/src/api.js`
- 必要时只读 `backend/routers/kg.py`
- 必要时只读 `backend/services/kg_extractor.py`

当前线索：

- `App.jsx` 里已经有 `selectedTextbook`。
- 但当前 `<GraphView onNodeClick={handleNodeClick} />` 没有把 `selectedTextbook` 传进去。
- `getKnowledgeGraph()` 当前也没有参数，默认拿全量 `/api/kg`。

修复要求：

1. `App.jsx` 把当前选中教材传给 `GraphView`：
   - 推荐：`<GraphView selectedTextbook={selectedTextbook} onNodeClick={handleNodeClick} />`
2. `GraphView.jsx` 在加载图谱后按教材过滤节点和边。
3. 过滤字段需要兼容：
   - `node.source_textbook`
   - `node.textbook_id`
   - `node.source`
   - `node.sources`
4. 左侧没有选中教材时，可以显示全量图谱；一旦选中教材，只显示该教材相关节点。
5. 边只保留两端节点都在当前教材节点集合里的边。
6. 如果过滤后没有节点，要显示明确空状态，例如“当前教材暂无知识图谱，请先解析并构建图谱”。
7. 点击节点详情仍然可用。

验收：

- 左侧点击 `reference_03_physiology.pdf` 后，图谱只显示这本书的节点。
- 再点击其他教材，图谱随之切换。
- 不会混入 `textbook_math_001`、`textbook_physics_001` 或其他非当前教材节点。

## P0-2：过滤非知识点节点

用户反馈：图谱中有一些和知识点无关的节点内容。

请在 `GraphView.jsx` 增加前端展示层过滤，必要时也可在后端 KG 输出处做最小过滤，但优先前端。

过滤建议：

1. 丢弃空名、纯数字、过短无意义节点：
   - `name` 为空
   - 去空格后长度小于 2
   - 纯页码、纯序号、纯标点
2. 丢弃明显目录/噪声节点，例如：
   - `目录`
   - `参考文献`
   - `习题`
   - `复习题`
   - `本章小结`
   - `思考题`
   - `附录`
   - `二维码`
   - `图`
   - `表`
3. 对过长节点名截断展示，但不要改原始 name；完整内容放 tooltip/详情。
4. 过滤后重新计算 degree 和 importance，不要用过滤前的连接数。

验收：

- 图谱中主要是概念、主题、公式、机制、结构等知识点。
- 明显目录、页码、习题、参考文献类节点不再显示。

## P0-3：RAG 引用来源不能显示 object

用户反馈：RAG 可以正确检索，但参考来源只显示 `object` 或 `[object Object]`，没有写明是哪本书哪一页。

重点检查：

- `frontend/src/components/RagPanel.jsx`
- `frontend/src/api.js`
- 必要时 `backend/services/rag.py`
- 必要时 `backend/routers/rag.py`

修复要求：

1. 前端不能直接 `String(citation)` 显示对象。
2. 增加 `formatCitation(citation, index)`：
   - 如果是字符串，直接显示。
   - 如果是对象，优先拼接这些字段：
     - `textbook_title`
     - `textbook_name`
     - `filename`
     - `source_textbook`
     - `chapter`
     - `page`
     - `pages`
     - `score`
   - 格式建议：
     `来源 1：生理学.pdf / 第三章 血液循环 / p.23 / score 0.82`
   - 缺字段时不要显示 `undefined`。
3. 如果 `citations` 为空，但 `source_chunks` 有数据，则从 `source_chunks` 派生引用来源。
4. `source_chunks` 对象也要兼容：
   - `metadata.title`
   - `metadata.filename`
   - `metadata.chapter`
   - `metadata.page`
   - 顶层 `textbook_title/chapter/page`
5. 同一个来源重复出现时可以去重。

验收：

- RAG 查询后，引用来源区域显示具体可读文本。
- 不允许出现 `[object Object]`、`object Object`、`undefined`。
- 至少能看到教材名或文件名；如果后端有 chapter/page，也要显示。

## P0-4：报告生成后必须显示正文

用户反馈：报告后端生成是 OK 的，但是前端没有显示。

重点检查：

- `frontend/src/components/ReportPanel.jsx`
- `frontend/src/api.js`
- 必要时 `backend/routers/report.py`

当前线索：

- `ReportPanel.jsx` 里生成报告后只在 `result.data.content` 存在时才 `setReportData(result.data)`。
- 如果 `/api/report/generate` 只返回 report_id/status，而正文需要 `/api/report/latest` 获取，前端就不会自动显示正文。

修复要求：

1. `handleGenerateReport` 成功后，无论 generate 是否返回 content，都要继续调用 `getLatestReport()`。
2. 拿到 latest 后立刻 `setReportData(...)`。
3. 如果 latest 没有 content，要显示明确错误：“报告已生成，但未读取到正文”，不要空白。
4. `api.js` 的 `getLatestReport()` 需要兼容更多字段：
   - `content`
   - `report_content`
   - `markdown`
   - `text`
   - `data.content`
   - 如果接口直接返回字符串，也要兼容。
5. 报告正文区域要放在按钮下方，生成后自动出现，不需要用户再点“查看详情”。

验收：

- 点击“生成新报告”后，右侧报告面板直接显示 Markdown 正文。
- 点击“查看详情”也能显示同一份正文。
- 不允许只显示“生成成功”但正文为空。

## 额外注意：当前前端文件有乱码风险

终端读取显示多个前端文件存在 mojibake。请你修改时直接用正常中文替换受影响的 UI 文案，保证 JSX 字符串和标签语法正确。

每次修改后必须跑：

```powershell
cd "D:\我的大学\博一下\黑客松2\frontend"
& "C:\Program Files\nodejs\npm.cmd" run build
```

## 最终测试路径

1. 启动后端，确认 `/health` 200。
2. 启动前端，打开 `http://localhost:3000/`。
3. 左侧选择一本真实上传教材，例如 `reference_03_physiology.pdf` 或 `03_生理学.pdf`。
4. 查看图谱：
   - 只显示该教材节点。
   - 无明显目录/页码/习题噪声。
   - 点击节点详情正常。
5. RAG：
   - 构建索引。
   - 输入一个问题。
   - 答案显示。
   - 引用来源显示具体教材/章节/页码，不出现 object。
6. 报告：
   - 点击生成新报告。
   - 生成后自动显示 Markdown 正文。
7. `npm.cmd run build` 通过。

## 输出报告格式

完成后请回复：

1. 修改了哪些文件。
2. 图谱按教材过滤是否通过。
3. 噪声节点过滤规则有哪些。
4. RAG 引用是否已从 object 改为可读来源。
5. 报告生成后是否自动显示正文。
6. build 是否通过。
7. 剩余风险，不超过 5 条。

## 禁止事项

1. 不要做 Docker，Docker 放到网页演示修复之后。
2. 不要改教材原始文件。
3. 不要清空 `data/`。
4. 不要引入大型新依赖。
5. 不要重构整个应用结构。

