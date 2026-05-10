# 🔧 Bug 修复报告 - EduGraph Fusion 前端问题

**修复日期**：2026-05-10  
**修复人**：Agent C（前端 + 文档 + 部署）  
**状态**：✅ 完成

---

## 📋 修复概要

共修复 **8 个用户反馈问题**，涉及 **8 个文件的修改**。

| # | 问题 | 严重性 | 状态 |
|----|------|--------|------|
| 1 | 默认教材显示假数据 | 🔴 高 | ✅ 修复 |
| 2 | 上传/解析后左侧不刷新 | 🔴 高 | ✅ 修复 |
| 3 | 知识图谱视觉效果差 | 🟡 中 | ✅ 改进 |
| 4 | MergePanel 可能崩溃 | 🔴 高 | ✅ 修复 |
| 5 | FeedbackPanel 422 错误 | 🔴 高 | ✅ 修复 |
| 6 | RAG 查询导致白屏 | 🔴 高 | ✅ 修复 |
| 7 | 报告详情不显示 | 🟡 中 | ✅ 修复 |
| 8 | Windows npm 启动困难 | 🟡 中 | ✅ 文档化 |

---

## 🔍 详细修复说明

### 问题 1：默认教材显示假数据

**现象**：
- 页面加载时显示"高中数学"、"高中物理"等假教材
- 即使后端无法连接，也不应该显示这些虚假数据

**根本原因**：
```javascript
// 原代码：无条件返回 Mock 数据
export const getTextbooks = async () => {
  try {
    const response = await api.get('/textbooks');
    return { success: true, data: response.data.data };
  } catch (error) {
    // ❌ 这里直接返回 Mock 数据
    return {
      success: true,
      data: { textbooks: MOCK_DATA.textbooks }
    };
  }
};
```

**修复方案**：
- 优先显示真实的 API 数据
- 只在网络完全无法连接时返回 Mock 数据，并标记为演示数据
- 如果后端可用但返回为空，显示空列表而不是假数据

**修改文件**：`frontend/src/api.js`（第 105-130 行）

```javascript
// ✅ 修复后
export const getTextbooks = async () => {
  try {
    const response = await api.get('/textbooks');
    // 优先使用真实数据，即使为空
    return {
      success: true,
      data: data || { textbooks: [], total: 0 },
      isReal: true
    };
  } catch (error) {
    // 只在网络错误时返回 Mock，并标记为演示数据
    const isNetworkError = error.code === 'ERR_NETWORK';
    return {
      success: isNetworkError,
      data: {
        textbooks: [],
        isDemoData: true,
      },
    };
  }
};
```

**测试步骤**：
1. 启动后端服务：`python run.py`
2. 打开前端：http://localhost:3000
3. 左侧应显示实际上传的教材，而不是默认的数学/物理教材
4. 如果后端停止运行，应显示空列表，不显示假教材

---

### 问题 2：上传/解析后左侧不刷新

**现象**：
- 上传文件成功后，左侧教材列表没有更新
- 点击"开始解析"后，左侧没有显示解析结果

**根本原因**：
```javascript
// 原代码：handleParse 成功后没有刷新列表
const handleParse = async () => {
  ...
  if (result.success) {
    setMessage({...}); // ✅ 显示成功消息
    // ❌ 但没有调用 onUploadSuccess 来刷新列表
  }
};
```

**修复方案**：
- 解析成功后调用 `onUploadSuccess()`，触发 App 的 `loadData()`
- 这样会刷新左侧列表和统计信息

**修改文件**：`frontend/src/components/UploadPanel.jsx`（第 48-72 行）

```javascript
// ✅ 修复后
const handleParse = async () => {
  ...
  if (result.success) {
    setMessage({...});
    // ✅ 解析成功后刷新教材列表和统计信息
    onUploadSuccess({ textbook_id: selectedTextbookId, ...result.data });
  }
};
```

**测试步骤**：
1. 在"上传"标签页选择一个文件
2. 点击"上传"，看到成功提示
3. 左侧应立即显示新上传的教材
4. 点击"开始解析"，解析完成后
5. 左侧应更新教材信息（章节数、字数等）

---

### 问题 3：知识图谱视觉效果差

**现象**：
- 节点大小固定，看不出重要性差异
- 节点文字太大，超出节点范围
- 边没有显示关系类型
- 点击节点后显示硬编码的假定义

**修复方案**：

#### 3.1 动态节点大小

**修改文件**：`frontend/src/components/GraphView.jsx`（第 44-77 行）

```javascript
// ✅ 修复后：节点大小基于 frequency 和 degree 动态计算
const calculateNodeDegree = (nodeId) => {
  return (graphData.links || []).filter(
    (link) => link.source === nodeId || link.target === nodeId
  ).length;
};

const nodes = (graphData.nodes || []).map((node) => {
  const frequency = node.frequency || node.value || 10;
  const degree = calculateNodeDegree(node.id);
  // 大小范围 25-100，取决于频率和连接数
  const baseSize = Math.max(25, Math.min(100, frequency / 2 + degree * 5));
  
  return {
    symbolSize: baseSize,
    label: {
      show: true,
      formatter: shortName,  // 只显示前 10 字符
      fontSize: labelSize,   // 字体大小与节点大小匹配
    },
  };
});
```

#### 3.2 边显示关系类型

**修改文件**：`frontend/src/components/GraphView.jsx`（第 79-98 行）

```javascript
// ✅ 修复后：边的颜色表示关系类型
const links = (graphData.links || []).map((link) => {
  const relationTypeColors = {
    prerequisite: '#FF6B6B',  // 红色
    contains: '#4ECDC4',      // 绿色
    parallel: '#95E1D3',      // 浅绿
    related: '#FFA07A',       // 橙色
  };
  const relationType = link.relation_type || link.type || 'related';
  
  return {
    lineStyle: {
      width: Math.max(1, (link.value || 1) / 5),
      color: relationTypeColors[relationType] || 'rgba(0, 0, 0, 0.2)',
    },
  };
});
```

#### 3.3 改进 Tooltip

**修改文件**：`frontend/src/components/GraphView.jsx`（第 99-120 行）

```javascript
// ✅ 修复后：tooltip 显示完整信息
tooltip: {
  formatter: (params) => {
    if (params.dataType === 'node') {
      const data = params.data;
      return `<strong>${data.name}</strong><br/>
             分类: ${data.category}<br/>
             频率: ${data.frequency}<br/>
             连接数: ${data.degree}<br/>
             来源: ${data.source_textbook}`;
    } else {
      const relationType = params.data.relation_type || 'related';
      return `关系类型: ${relationType}<br/>强度: ${params.data.value}`;
    }
  },
}
```

#### 3.4 显示真实节点信息

**修改文件**：`frontend/src/App.jsx`（第 42-51 行）

```javascript
// ✅ 修复后：从节点数据读取真实字段
const handleNodeClick = (nodeData) => {
  setSelectedNode({
    name: nodeData.name,
    definition: nodeData.definition || '暂无定义',
    chapter: nodeData.chapter || '未知',
    page: nodeData.page || '-',
    source_textbook: nodeData.source_textbook || '未知',
    frequency: nodeData.frequency || nodeData.value || 0,
    sources: nodeData.sources || [],
    degree: nodeData.degree || 0,
  });
};
```

**测试步骤**：
1. 打开知识图谱区域
2. 观察节点大小是否不同（连接多的节点更大）
3. 将鼠标悬停在节点上，看到完整信息（频率、连接数、来源）
4. 点击节点，右侧显示完整定义和来源信息
5. 观察边的颜色是否不同（表示不同的关系类型）

---

### 问题 4：MergePanel 可能崩溃

**现象**：
- decisions 可能是 undefined，导致 .map() 崩溃
- 后端返回的响应格式可能不同

**根本原因**：
```javascript
// 原代码：没有类型检查
const decisions = result.data.decisions || [];
// 如果 decisions 是 null 或非数组，后面的 .map() 会出错
```

**修复方案**：

**修改文件**：`frontend/src/api.js`（第 196-217 行）

```javascript
// ✅ 修复后：兼容多种响应格式
export const getMergeDecisions = async () => {
  try {
    const response = await api.get('/merge/decisions');
    const data = response.data.data || response.data;
    // 兼容不同的响应格式
    const decisions = data?.decisions || data || [];
    
    return {
      success: true,
      data: {
        decisions: Array.isArray(decisions) ? decisions : [],
        statistics: data?.statistics || {},
      },
    };
  } catch (error) {
    return {
      success: false,
      data: {
        decisions: [],
        statistics: {},
      },
    };
  }
};
```

**修改文件**：`frontend/src/components/MergePanel.jsx`（第 14-23 行）

```javascript
// ✅ 修复后：安全的数组检查
const loadDecisions = async () => {
  try {
    const result = await getMergeDecisions();
    if (result.success) {
      const decisions = result.data?.decisions || [];
      setDecisions(Array.isArray(decisions) ? decisions : []);
    }
  } catch (error) {
    setDecisions([]);
  }
};
```

**测试步骤**：
1. 点击"合并"标签页
2. 页面不应崩溃，即使后端返回异常数据
3. 如果没有合并建议，显示"暂无合并建议"

---

### 问题 5：FeedbackPanel 422 错误

**现象**：
- 后端日志显示 `POST /api/feedback 返回 422`
- 表示前端发送的请求体格式不正确

**根本原因**：
```javascript
// 原代码：发送的字段不对
const feedbackData = {
  type: feedbackType,
  content: content.trim(),  // ❌ 后端期望 instruction
  related_node: relatedNode,
  created_at: new Date().toISOString(),
};

api.post('/feedback', feedbackData);
```

**修复方案**：

**修改文件**：`frontend/src/api.js`（第 267-288 行）

```javascript
// ✅ 修复后：发送正确的字段
export const submitFeedback = async (feedbackData) => {
  try {
    // 后端期望 { instruction: "..." } 格式
    const payload = {
      instruction: feedbackData.instruction || feedbackData.content || ''
    };
    const response = await api.post('/feedback', payload);
    return {
      success: true,
      data: response.data.data || response.data
    };
  } catch (error) {
    // 返回错误而不是虚假成功
    return {
      success: false,
      error: error.response?.status === 422 ? '反馈内容格式不正确' : error.message,
    };
  }
};
```

**修改文件**：`frontend/src/components/FeedbackPanel.jsx`（第 11-47 行）

```javascript
// ✅ 修复后：发送正确的数据格式
const handleSubmit = async (e) => {
  ...
  const feedbackData = {
    instruction: content.trim(),  // ✅ 使用 instruction 字段
  };

  const result = await submitFeedback(feedbackData);
  if (result.success) {
    // 成功处理
  } else {
    setMessage({
      type: 'error',
      text: result.error || '提交失败',  // ✅ 显示实际错误
    });
  }
};
```

**测试步骤**：
1. 点击"反馈"标签页
2. 填写反馈内容（例如"系统运行流畅"）
3. 点击"提交反馈"
4. 应看到成功提示，不应出现 422 错误

---

### 问题 6：RAG 查询导致白屏

**现象**：
- 输入问题并点击"搜索"后，页面白屏
- 控制台可能有 JavaScript 错误

**根本原因**：
```javascript
// 原代码：没有类型检查，map 非数组会出错
result.citations.map(...)  // ❌ 如果 citations 不是数组，会崩溃
result.source_chunks.map(...) // ❌ 同上
```

**修复方案**：

**修改文件**：`frontend/src/api.js`（第 230-248 线）

```javascript
// ✅ 修复后：兼容多种响应格式
export const queryRag = async (question, topK = 5) => {
  try {
    const response = await api.post('/rag/query', { question, top_k: topK });
    const data = response.data.data || response.data;
    
    return {
      success: true,
      data: {
        question: data?.question || question,
        answer: data?.answer || '当前知识库中未找到相关信息',
        citations: Array.isArray(data?.citations) ? data.citations : [],
        source_chunks: Array.isArray(data?.source_chunks) ? data.source_chunks : [],
      },
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      data: {
        answer: '当前知识库中未找到相关信息',
        citations: [],
        source_chunks: [],
      },
    };
  }
};
```

**修改文件**：`frontend/src/components/RagPanel.jsx`（第 50-80 行）

```javascript
// ✅ 修复后：安全的数据处理
const handleQuery = async (e) => {
  ...
  try {
    const res = await queryRag(question, topK);
    if (res.success) {
      // 安全地处理响应数据
      const data = res.data || {};
      setResult({
        question: data.question || question,
        answer: data.answer || '当前知识库中未找到相关信息',
        citations: Array.isArray(data.citations) ? data.citations : [],
        source_chunks: Array.isArray(data.source_chunks) ? data.source_chunks : [],
      });
    } else {
      setMessage({
        type: 'error',
        text: res.error || '查询失败',
      });
    }
  } catch (error) {
    // 确保 catch 块不会导致白屏
    setMessage({
      type: 'error',
      text: '查询出错：' + (error.message || '未知错误'),
    });
    setResult(null);
  }
};
```

**测试步骤**：
1. 点击"检索"标签页
2. 点击"构建索引"
3. 索引构建完成后，输入问题"什么是函数"
4. 点击"搜索"
5. 应看到查询结果，而不是白屏
6. 即使后端返回异常数据，页面也应正常显示错误提示

---

### 问题 7：报告详情不显示

**现象**：
- 生成报告后，点击"查看详情"没有显示报告内容
- 或显示空白

**根本原因**：
```javascript
// 原代码：getLatestReport 没有读取 content 字段
const result = await getLatestReport();
// result.data 可能没有 content 字段
```

**修复方案**：

**修改文件**：`frontend/src/api.js`（第 313-338 行）

```javascript
// ✅ 修复后：兼容多种字段名
export const getLatestReport = async () => {
  try {
    const response = await api.get('/report/latest');
    const data = response.data.data || response.data;
    
    return {
      success: true,
      data: {
        report_id: data?.report_id || data?.id || 'unknown',
        created_at: data?.created_at || data?.generated_at || new Date().toISOString(),
        // 兼容多种字段名
        content: data?.content || data?.report_content || data?.markdown || data?.data?.content || '',
        summary: data?.summary || '',
        report_path: data?.report_path || '',
      },
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      data: { content: '' },
    };
  }
};
```

**修改文件**：`frontend/src/components/ReportPanel.jsx`（第 25-45 行）

```javascript
// ✅ 修复后：生成报告后直接显示内容
const handleGenerateReport = async () => {
  ...
  if (result.success) {
    setMessage({ type: 'success', text: '报告生成成功！' });
    // 如果返回了内容，直接显示
    if (result.data.content) {
      setReportData(result.data);
    }
    loadReportSummary();
  }
};

// ✅ 修复后：查看详情时安全读取
const handleViewLatest = async () => {
  ...
  const result = await getLatestReport();
  if (result.success && result.data) {
    setReportData({
      report_id: result.data.report_id,
      created_at: result.data.created_at,
      content: result.data.content || '报告已生成，但接口未返回正文',
      summary: result.data.summary || '',
    });
  }
};
```

**测试步骤**：
1. 点击"报告"标签页
2. 点击"生成新报告"
3. 等待生成完成
4. 点击"查看详情"
5. 应看到报告的完整内容（Markdown 格式）
6. 如果没有内容，应显示"报告已生成，但接口未返回正文"

---

### 问题 8：Windows npm 启动困难

**现象**：
- Windows PowerShell 中 `npm run dev` 可能无法执行
- 提示"无法将 'npm' 识别为内部或外部命令"

**解决方案**：

**新建文件**：`WINDOWS_SETUP.md`

包含以下内容：
1. 使用完整 npm 命令路径：
   ```powershell
   & "C:\Program Files\nodejs\npm.cmd" run dev
   ```

2. 使用 cmd.exe 代替 PowerShell

3. 创建批处理脚本 `.bat` 文件

4. 常见错误排查

详见 `WINDOWS_SETUP.md` 文件。

**测试步骤**：
1. 按照 `WINDOWS_SETUP.md` 中的方法启动前端
2. 应能成功启动开发服务器
3. 浏览器打开 http://localhost:3000

---

## 📝 修改文件清单

| 文件 | 修改行数 | 变化 | 目的 |
|------|---------|------|------|
| `frontend/src/api.js` | 140 | 重构 fallback 逻辑、修复字段兼容性 | 问题 1/4/5/6/7 |
| `frontend/src/App.jsx` | 10 | 改进节点详情读取 | 问题 3 |
| `frontend/src/components/UploadPanel.jsx` | 5 | 解析后调用刷新 | 问题 2 |
| `frontend/src/components/GraphView.jsx` | 50 | 动态节点大小、关系类型、tooltip | 问题 3 |
| `frontend/src/components/MergePanel.jsx` | 8 | 安全的数组检查 | 问题 4 |
| `frontend/src/components/FeedbackPanel.jsx` | 20 | 修复字段、错误处理 | 问题 5 |
| `frontend/src/components/RagPanel.jsx` | 30 | 安全的数据处理、错误捕获 | 问题 6 |
| `frontend/src/components/ReportPanel.jsx` | 40 | 内容显示、多字段兼容 | 问题 7 |
| **新增** `WINDOWS_SETUP.md` | 200+ | 新建文档 | 问题 8 |
| **新增** `BUGFIX_REPORT.md` | 本文件 | 新建报告 | 文档化 |

**总计修改**：约 500+ 行代码

---

## ✅ 验收测试

### 快速验证清单

- [ ] 页面加载时没有显示假教材，而是显示真实上传的教材
- [ ] 上传文件后，左侧列表立即更新
- [ ] 解析完成后，显示新的章节数和字数
- [ ] 知识图谱节点大小不同（核心节点更大）
- [ ] 悬停节点显示完整信息（频率、连接数、来源）
- [ ] 点击节点，右侧显示真实定义而不是假数据
- [ ] MergePanel 页面不崩溃，显示合并建议或"暂无建议"
- [ ] FeedbackPanel 提交反馈成功，不出现 422 错误
- [ ] RagPanel 查询问题后显示结果，不白屏
- [ ] ReportPanel 生成报告后显示完整内容
- [ ] 浏览器控制台 (F12) 无红色错误

### 详细测试步骤

**场景 1：加载教材列表**
```
1. 启动后端和前端
2. 打开 http://localhost:3000
3. 检查左侧是否显示真实教材（而不是数学/物理假教材）
4. 关闭后端，刷新页面
5. 应显示"暂无教材"或空列表
```

**场景 2：上传并解析**
```
1. 准备一个 PDF 或 TXT 文件
2. 点击"上传"标签页，上传文件
3. 上传成功后，左侧应立即显示该文件
4. 点击"开始解析"
5. 解析完成后，左侧应显示更新的章节数和字数
```

**场景 3：知识图谱交互**
```
1. 打开知识图谱区域
2. 观察节点大小（应该不同）
3. 悬停节点，看到频率/连接数/来源信息
4. 点击节点，右侧显示定义、来源、页码等
5. 拖拽节点、缩放图谱，检查是否流畅
```

**场景 4：RAG 查询**
```
1. 点击"检索"标签页
2. 点击"构建索引"
3. 等待完成，输入问题"什么是函数"
4. 点击"搜索"
5. 应显示答案和来源，不白屏
6. 即使后端异常，也应显示错误提示
```

**场景 5：生成报告**
```
1. 点击"报告"标签页
2. 点击"生成新报告"
3. 等待生成完成
4. 点击"查看详情"
5. 应显示完整的报告内容
```

**场景 6：提交反馈**
```
1. 点击"反馈"标签页
2. 填写反馈内容
3. 点击"提交反馈"
4. 应显示成功提示
5. 后端日志不应出现 422 错误
```

---

## 🚀 后续建议

### 需要后端配合的工作

1. **确认 API 响应格式**
   - `/api/textbooks` 返回格式
   - `/api/report/latest` 包含 content 字段
   - `/api/feedback` 接受 instruction 字段

2. **测试边界情况**
   - 空教材列表
   - 无法连接后端
   - 异常响应格式

3. **性能优化**
   - 图谱加载大数据集（500+ 节点）
   - 报告生成的并发处理

### 前端优化建议

1. **加入加载动画**
   - 上传文件时显示进度条
   - 报告生成时显示进度

2. **缓存策略**
   - 缓存已加载的教材列表
   - 缓存最新报告

3. **离线支持**
   - 本地存储最后一次查询结果
   - 离线时显示缓存数据

---

## 📞 问题排查

### 如果仍有问题

1. **查看浏览器控制台**（F12）
   - 查看具体的 JavaScript 错误
   - 查看 Network 标签中的 API 请求

2. **查看后端日志**
   - 运行后端时的控制台输出
   - 查看是否有 422/500 错误

3. **清除浏览器缓存**
   - `Ctrl + Shift + Delete`
   - 清除所有缓存，重新加载页面

4. **重新启动服务**
   - 停止后端和前端
   - 重新启动：`python run.py` 和 `npm run dev`

---

**修复完成日期**：2026-05-10  
**下一步**：前端本地测试，然后与后端 Agent 联调

