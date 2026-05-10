# EduGraph Fusion - Agent 架构说明

## 项目分工

本项目由 3 个 Claude Code Agent 协作完成，分别负责不同的模块开发。

## Agent 1: 后端开发 (Backend Developer)

### 职责范围
- 设计和实现后端 FastAPI 应用
- 实现文件解析和存储模块
- 构建知识图谱生成算法
- 实现图谱合并和去重逻辑
- 集成 RAG 向量搜索引擎
- 实现反馈和报告模块

### 核心模块

#### 1. 文件处理服务 (services/storage.py)
```python
class FileStorage:
  - save_uploaded_file()     # 保存上传的文件
  - load_metadata()          # 加载教材元数据
  - save_parse_result()      # 保存解析结果
  - load_textbook()          # 加载教材信息
  - list_all_textbooks()     # 列出所有教材
```

#### 2. 多格式解析器 (services/parser.py)
```python
class ParserFactory:
  - get_parser()             # 根据文件类型获取解析器

class PDFParser:
  - parse()                  # 解析 PDF 文件

class MarkdownParser:
  - parse()                  # 解析 Markdown 文件

class TextParser:
  - parse()                  # 解析纯文本文件
```

#### 3. 知识图谱构建 (services/kg_builder.py)
- 从章节内容提取关键概念
- 建立概念间的关系
- 计算节点的重要度（frequency）
- 支持多教材融合

#### 4. 图谱合并模块 (services/kg_merger.py)
- 检测相似概念
- 计算概念相似度
- 提供合并建议
- 执行图谱合并操作

#### 5. RAG 引擎 (services/rag.py)
```python
class RAGEngine:
  - load_and_index()         # 加载数据并构建向量索引
  - query()                  # 执行语义搜索
  - add_chunks()             # 添加新的文本块
```

#### 6. 反馈处理 (services/feedback.py)
- 收集用户反馈
- 反馈分类和统计
- 生成反馈报告

#### 7. 报告生成 (services/report_generator.py)
- 生成综合分析报告
- 包含统计信息和建议
- 支持多种导出格式

### API 路由定义

#### 文件上传 (routers/upload.py)
```
POST /api/upload
  参数: file (multipart/form-data)
  返回: textbook_id, filename, file_type, file_size
```

#### 教材管理 (routers/textbooks.py)
```
POST   /api/parse/{textbook_id}
GET    /api/textbooks
GET    /api/textbooks/{textbook_id}
GET    /api/stats
GET    /api/textbooks/{textbook_id}/stats
```

#### 知识图谱 (routers/kg.py)
```
POST   /api/kg/build
GET    /api/kg
POST   /api/merge
GET    /api/merge/decisions
```

#### RAG 搜索 (routers/rag.py)
```
POST   /api/rag/index
POST   /api/rag/query
GET    /api/rag/status
```

#### 反馈管理 (routers/feedback.py)
```
POST   /api/feedback
GET    /api/feedback/summary
```

#### 报告生成 (routers/report.py)
```
POST   /api/report/generate
GET    /api/report/latest
GET    /api/report/summary
```

### 数据存储结构

```
backend/data/
├── uploads/              # 原始上传文件
│   ├── uuid_filename.pdf
│   └── ...
├── processed/            # 解析后的教材数据
│   ├── textbook_xxx.json
│   │   {
│   │     "id": "textbook_xxx",
│   │     "chapters": [...],
│   │     "metadata": {...}
│   │   }
│   └── ...
├── metadata/             # 教材元数据
│   └── textbook_xxx.json
├── vector_index/         # 向量索引（FAISS）
│   ├── index.faiss
│   ├── metadata.json
│   └── embeddings.npy
└── reports/              # 生成的报告
    └── report_xxx.md
```

## Agent 2: 前端开发 (Frontend Developer) - **当前角色**

### 职责范围
- 设计和实现 React 单页应用
- 实现 3 列布局和响应式设计
- 开发 6 个功能面板组件
- 集成 ECharts 知识图谱可视化
- 实现 API 调用层和错误处理
- 提供 Mock 数据 fallback

### 核心模块

#### 1. 应用架构 (App.jsx)
- 管理全局状态
- 协调各个子组件
- 处理选中的教材和节点

#### 2. API 调用模块 (src/api.js)
```javascript
// 文件操作
uploadFile()              # 上传文件
parseTextbook()           # 解析教材
getTextbooks()            # 获取教材列表
getTextbookDetail()       # 获取教材详情
getStats()                # 获取统计信息

// 知识图谱
buildKnowledgeGraph()     # 构建知识图谱
getKnowledgeGraph()       # 获取知识图谱
mergeGraphs()             # 合并图谱
getMergeDecisions()       # 获取合并建议

// RAG 检索
buildRagIndex()           # 构建 RAG 索引
queryRag()                # 执行检索查询
getRagStatus()            # 获取 RAG 状态

// 反馈和报告
submitFeedback()          # 提交反馈
getFeedbackSummary()      # 获取反馈总结
generateReport()          # 生成报告
getLatestReport()         # 获取最新报告
getReportSummary()        # 获取报告总结
```

#### 3. 组件开发

##### UploadPanel.jsx
- 文件选择和验证
- 上传进度显示
- 文件解析触发
- 错误提示

##### GraphView.jsx
- ECharts 知识图谱可视化
- 节点颜色区分教材来源
- 节点大小表示频率
- 支持缩放和拖拽
- 点击节点交互

##### MergePanel.jsx
- 显示合并建议列表
- 选择要合并的建议
- 执行图谱合并
- 合并结果显示

##### RagPanel.jsx
- RAG 索引管理
- 问题输入和查询
- 搜索结果展示
- 引用来源显示
- Top-K 参数调整

##### FeedbackPanel.jsx
- 反馈类型选择
- 反馈内容输入
- 相关知识点输入
- 反馈提交
- 提交结果确认

##### ReportPanel.jsx
- 报告生成触发
- 最新报告信息显示
- 报告详情展示
- 下载功能

#### 4. 样式设计 (src/styles/index.css)
- 3 列响应式布局
- 组件样式库
- 动画和过渡效果
- 深色模式支持（可选）

### 前端特性

#### 交互特性
1. **实时反馈**
   - Loading 状态指示器
   - 成功/错误提示
   - 进度显示

2. **图谱交互**
   - 节点点击显示详情
   - 拖拽移动节点
   - 缩放查看
   - 关联高亮

3. **表单优化**
   - 输入验证
   - 错误提示
   - 禁用不可用操作
   - 清空确认

#### 容错机制
1. **Mock 数据 Fallback**
   - 后端不可用时自动降级
   - 保证页面可用性
   - 提示用户当前为演示模式

2. **错误处理**
   - 网络错误捕获
   - 用户友好的错误提示
   - 重试机制

## Agent 3: 文档和部署 (Documentation & Deployment) - **当前角色**

### 职责范围
- 编写项目文档
- 创建部署配置
- 编写 README 和快速开始指南
- 设置 .gitignore 和其他配置文件
- 整合报告模板

### 文档结构

```
docs/
├── 需求分析.md              # 项目需求
├── 系统设计.md              # 系统架构设计
├── Agent架构说明.md         # Agent 分工说明（本文件）
└── 接口文档.md              # API 接口文档
```

### 配置文件

#### .gitignore
- 排除 `*.pdf` 文件
- 排除 `backend/data/` 目录
- 排除 `node_modules/`
- 排除 `.env` 文件

#### README.md（根目录）
- 项目简介
- 技术栈
- 环境依赖
- 配置说明
- 启动步骤
- 使用流程
- 部署指南

#### .env.example
- API 配置示例
- 模型配置示例
- 数据库配置示例

## Agent 间的协作流程

### 1. 接口定义阶段
- Agent 1 定义所有 API 接口规范
- Agent 2 根据接口设计 API 调用层
- Agent 3 整合接口文档

### 2. 开发阶段
- Agent 1 实现后端 API 和服务
- Agent 2 实现前端组件和交互
- Agent 3 持续更新文档和配置

### 3. 集成测试阶段
- Agent 2 调用 Agent 1 的 API
- 修复接口不匹配问题
- Agent 3 更新已发现的文档问题

### 4. 交付阶段
- Agent 3 完成最终文档
- 所有 Agent 配合进行联调测试
- 确保系统完整可用

## 数据流穿过三个 Agent

```
用户上传文件
    ↓ (Agent 2 前端捕获)
前端验证和上传
    ↓ (Agent 1 后端处理)
保存文件和解析
    ↓ (Agent 2 显示结果)
更新前端状态
    ↓ (Agent 3 记录流程)
文档更新

用户查看知识图谱
    ↓ (Agent 2 前端调用)
GET /api/kg
    ↓ (Agent 1 返回图数据)
ECharts 渲染图谱
    ↓ (Agent 2 显示交互)
点击节点显示详情
    ↓ (Agent 3 在文档中说明)
用户体验文档记录
```

## 通信约定

### API 响应格式（由 Agent 1 定义）
```json
{
  "status": "success|error",
  "message": "操作描述",
  "data": { /* 具体数据 */ }
}
```

### 错误处理约定（由 Agent 2 实现）
1. 网络错误 → 显示错误提示，尝试 Mock 降级
2. 4xx 错误 → 显示用户错误提示
3. 5xx 错误 → 显示服务器错误提示

### 文档约定（由 Agent 3 维护）
- Markdown 格式
- 中文编写
- 包含代码示例
- 更新及时

## 项目开发检查清单

### Agent 1 (后端) 完成项检查
- [ ] 所有路由实现
- [ ] 文件解析功能
- [ ] 知识图谱构建
- [ ] RAG 索引和查询
- [ ] 反馈收集
- [ ] 报告生成
- [ ] API 文档完整
- [ ] 错误处理完善
- [ ] 后端测试通过

### Agent 2 (前端) 完成项检查
- [ ] React 项目初始化
- [ ] 3 列布局实现
- [ ] 所有组件开发
- [ ] 图谱可视化
- [ ] API 调用集成
- [ ] Mock 数据 fallback
- [ ] 错误提示完整
- [ ] Loading 状态完整
- [ ] 前端测试通过

### Agent 3 (文档和部署) 完成项检查
- [ ] README.md 完成
- [ ] 需求分析文档
- [ ] 系统设计文档
- [ ] 接口文档完整
- [ ] .gitignore 配置
- [ ] .env.example 创建
- [ ] Docker 配置
- [ ] 启动脚本
- [ ] 部署文档

### 联调检查清单
- [ ] 前后端通信正常
- [ ] 所有接口可用
- [ ] 错误处理一致
- [ ] 数据流完整
- [ ] 文档和代码一致
- [ ] 性能指标达成
- [ ] 安全检查通过

## 开发环境配置

### 前提条件
- Python 3.8+
- Node.js 16+
- npm 或 yarn
- Git

### 初始化步骤

#### 1. 克隆项目
```bash
git clone <repo>
cd 黑客松2
```

#### 2. 后端环境（Agent 1）
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. 前端环境（Agent 2）
```bash
cd frontend
npm install
```

#### 4. 项目配置（Agent 3）
```bash
# 根目录
cp .env.example .env
# 编辑 .env 配置必要参数
```

## 版本管理

### Git 分支策略
```
main            # 生产分支
  └─ develop   # 开发分支
      ├─ agent-1-backend      # Agent 1 开发
      ├─ agent-2-frontend     # Agent 2 开发
      └─ agent-3-docs-deploy  # Agent 3 开发
```

### 提交约定
```
feat(component): 新增功能
fix(component): 修复缺陷
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
perf: 性能优化
test: 测试相关
chore: 构建/配置调整
```

## 常见问题解决

### 问题 1: 前端无法连接后端
**解决方案**：
1. 确保后端运行在 http://localhost:8000
2. 检查 vite.config.js 中的代理配置
3. 查看浏览器控制台的网络错误

### 问题 2: 知识图谱不显示
**解决方案**：
1. 检查后端 GET /api/kg 是否返回正确的数据
2. 验证 ECharts 是否正确初始化
3. 查看浏览器控制台的 JavaScript 错误

### 问题 3: 文件上传失败
**解决方案**：
1. 检查文件格式是否支持（PDF/MD/TXT）
2. 验证文件大小是否超过 100MB 限制
3. 查看后端日志获取详细错误信息

## 部署清单

### 生产环境部署前
- [ ] 所有测试通过
- [ ] 代码审查完成
- [ ] 文档已更新
- [ ] 环境变量已配置
- [ ] 数据库已初始化
- [ ] 备份已创建

### 部署步骤
1. 构建前端: `npm run build`
2. 启动后端: `python run.py`
3. 验证所有接口可用
4. 进行冒烟测试
5. 监控系统运行

## 持续改进

### 反馈收集
- 用户反馈模块
- 系统日志分析
- 性能监控数据

### 迭代计划
- 月度优化迭代
- 新功能开发
- 文档更新

---

**最后更新**: 2024-01-01
**维护人**: EduGraph Fusion Team
