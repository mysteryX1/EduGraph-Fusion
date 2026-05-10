# EduGraph Fusion - 教材知识底座系统

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-Active-brightgreen.svg)

## 📚 项目简介

**EduGraph Fusion** 是一个智能教材知识管理系统，通过自动化的文件处理、知识图谱构建、智能合并和语义检索等功能，为教育工作者和学生提供高效的知识管理和学习辅助。

### 核心特性

✨ **智能文件处理**
- 支持多种格式（PDF、Markdown、纯文本）
- 自动章节识别和内容提取
- 异步处理，不阻塞主线程

📊 **知识图谱可视化**
- 自动从教材提取知识概念
- 构建概念间的关联关系
- 可视化交互式知识图谱展示

🔗 **图谱合并与去重**
- 自动检测相似概念
- 智能消除知识冗余
- 用户确认的合并决策

🔍 **语义知识检索 (RAG)**
- 基于向量的语义搜索
- 支持自然语言提问
- 提供源文献引用

💬 **用户反馈系统**
- 收集用户意见和建议
- 反馈分类和统计
- 持续改进驱动

📈 **综合报告生成**
- 系统分析报告
- 知识质量评分
- 个性化建议

## 🛠️ 技术栈

### 前端
- **React 18+** - 用户界面框架
- **Vite** - 快速构建工具
- **ECharts 5** - 知识图谱可视化
- **Axios** - HTTP 请求库
- **CSS3** - 响应式设计

### 后端
- **FastAPI** - 高性能 Web 框架
- **Python 3.8+** - 后端编程语言
- **FAISS** - 向量相似度搜索
- **PyPDF2/pdfplumber** - PDF 解析
- **Markdown** - 文本处理

### 开发工具
- **Git** - 版本控制
- **Docker** - 容器化部署
- **Node.js** - 前端工具链

## 📋 环境依赖

### 系统要求
- **操作系统**: Windows 10+, macOS 10.14+, Linux
- **内存**: 4GB+
- **磁盘**: 2GB+ 可用空间

### 前置软件
- **Python 3.8 或更高版本**
  ```bash
  # 验证安装
  python --version
  ```

- **Node.js 16 或更高版本**
  ```bash
  # 验证安装
  node --version
  npm --version
  ```

- **Git**
  ```bash
  # 验证安装
  git --version
  ```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd 黑客松2
```

### 2. 后端配置

#### 2.1 创建虚拟环境
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

#### 2.2 安装依赖
```bash
pip install -r requirements.txt
```

#### 2.3 配置环境变量
```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，设置必要的参数
```

#### 2.4 初始化数据目录
```bash
# 后端会自动创建必要的目录
# data/
# ├── uploads/          # 上传的文件
# ├── processed/        # 解析后的数据
# ├── metadata/         # 元数据
# ├── vector_index/     # 向量索引
# └── reports/          # 生成的报告
```

### 3. 前端配置

#### 3.1 安装依赖
```bash
cd frontend
npm install
```

#### 3.2 配置环境变量（可选）
```bash
# 如果需要修改 API 地址，在前端根目录创建 .env.local 文件
# VITE_API_URL=http://your-api-server:8000/api
```

### 4. 启动应用

#### 4.1 启动后端服务

```bash
cd backend
python run.py
```

输出示例：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

#### 4.2 启动前端应用（新终端）

```bash
cd frontend
npm run dev
```

输出示例：
```
  VITE v5.0.8  ready in 245 ms

  ➜  Local:   http://localhost:3000/
  ➜  Press q to quit
```

#### 4.3 打开浏览器

访问 [http://localhost:3000](http://localhost:3000) 即可使用系统。

## 📖 使用流程

### 基础工作流程

```
1. 上传教材
   └─ 选择 PDF/Markdown/纯文本 文件
   └─ 点击"上传"按钮
   └─ 获得 textbook_id

2. 解析教材
   └─ 选择已上传的教材
   └─ 点击"开始解析"
   └─ 系统自动提取章节和内容

3. 构建知识图谱
   └─ 解析完成后，系统自动构建图谱
   └─ 查看节点和关系
   └─ 点击节点查看详情

4. 合并图谱（可选）
   └─ 系统检测相似概念
   └─ 查看合并建议
   └─ 选择并确认合并

5. 构建 RAG 索引
   └─ 点击"检索"标签页
   └─ 点击"构建索引"
   └─ 等待构建完成

6. 知识检索
   └─ 输入自然语言问题
   └─ 点击"搜索"
   └─ 查看答案和引用来源

7. 生成报告
   └─ 点击"报告"标签页
   └─ 点击"生成新报告"
   └─ 查看综合分析报告
```

### 功能区介绍

#### 左侧 - 教材管理
- **统计信息**: 显示教材数、章节数
- **已上传教材**: 教材列表，支持选择和查看详情

#### 中间 - 知识图谱
- **交互式展示**: 用 ECharts 渲染知识图谱
- **支持操作**:
  - 缩放：鼠标滚轮
  - 拖拽：点击并拖动节点
  - 点击节点：显示详情信息

#### 右侧 - 功能面板（5 个 Tab）

**1. 上传**
- 上传新教材文件
- 自动解析提取内容
- 查看解析结果统计

**2. 合并**
- 查看图谱合并建议
- 选择要合并的节点对
- 执行合并操作

**3. 检索**
- 构建 RAG 向量索引
- 输入自然语言问题
- 获取答案和源引用

**4. 反馈**
- 提交使用反馈
- 报告系统缺陷
- 提出改进建议

**5. 报告**
- 生成综合分析报告
- 查看最新报告详情
- 导出报告内容

## ⚙️ 环境配置

### .env 配置文件

在项目根目录创建 `.env` 文件：

```env
# 后端 API 配置
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# 前端 API 配置
REACT_APP_API_URL=http://localhost:8000/api

# 模型配置（可选）
LLM_MODEL=gpt-3.5-turbo
LLM_API_KEY=your_api_key

# 向量数据库配置（可选）
VECTOR_DB_PATH=./backend/data/vector_index
```

### 数据存储配置

后端将自动创建以下目录结构：

```
backend/
├── data/
│   ├── uploads/           # 原始上传文件
│   ├── processed/         # 解析后的教材数据
│   ├── metadata/          # 教材元数据
│   ├── vector_index/      # 向量索引（FAISS）
│   └── reports/           # 生成的报告
├── temp/                  # 临时文件
└── logs/                  # 系统日志
```

## 🌐 API 端点概览

| 功能 | 方法 | 端点 |
|------|------|------|
| 上传文件 | POST | `/api/upload` |
| 解析教材 | POST | `/api/parse/{textbook_id}` |
| 教材列表 | GET | `/api/textbooks` |
| 教材详情 | GET | `/api/textbooks/{textbook_id}` |
| 系统统计 | GET | `/api/stats` |
| 构建图谱 | POST | `/api/kg/build` |
| 获取图谱 | GET | `/api/kg` |
| 获取合并建议 | GET | `/api/merge/decisions` |
| 执行合并 | POST | `/api/merge` |
| 构建 RAG 索引 | POST | `/api/rag/index` |
| RAG 查询 | POST | `/api/rag/query` |
| 提交反馈 | POST | `/api/feedback` |
| 生成报告 | POST | `/api/report/generate` |

**详见**: [接口文档](./docs/接口文档.md)

## 📚 文档

- **[需求分析](./docs/需求分析.md)** - 项目需求和业务场景
- **[系统设计](./docs/系统设计.md)** - 架构设计和数据流
- **[Agent 架构说明](./docs/Agent架构说明.md)** - 开发团队分工
- **[接口文档](./docs/接口文档.md)** - API 详细说明

## 🔧 开发命令

### 后端命令

```bash
# 启动开发服务器
python run.py

# 运行测试
python -m pytest

# 查看 API 文档
# 访问 http://localhost:8000/docs
```

### 前端命令

```bash
# 启动开发服务器
npm run dev

# 生产构建
npm run build

# 预览构建结果
npm run preview
```

## 📦 部署

### Docker 部署

```bash
# 构建后端镜像
docker build -f Dockerfile.backend -t edugraph-backend:latest .

# 构建前端镜像
docker build -f Dockerfile.frontend -t edugraph-frontend:latest .

# 使用 Docker Compose
docker-compose up -d
```

### 手动部署

#### 前端构建
```bash
cd frontend
npm run build
# 输出在 frontend/dist 目录
# 使用 Nginx 或其他 Web 服务器部署
```

#### 后端部署
```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:8000 "main:app"
```

## 🧪 测试

### 后端测试

```bash
# 运行所有测试
python -m pytest

# 运行特定测试文件
python -m pytest test_api.py

# 运行测试并生成覆盖率报告
python -m pytest --cov=backend
```

### 前端测试

```bash
# 运行测试（如果配置了）
npm test
```

### 联调测试

1. **启动后端**: `python run.py`
2. **启动前端**: `npm run dev`
3. **打开浏览器**: http://localhost:3000
4. **测试流程**:
   - [ ] 上传教材文件
   - [ ] 解析文件内容
   - [ ] 查看知识图谱
   - [ ] 测试图谱交互（缩放、拖拽、点击）
   - [ ] 构建 RAG 索引
   - [ ] 执行知识检索
   - [ ] 提交反馈
   - [ ] 生成报告

## 🐛 常见问题

### 问题 1: 前端无法连接后端
```
解决方案：
1. 确保后端运行在 http://localhost:8000
2. 检查 vite.config.js 中的代理设置
3. 查看浏览器控制台错误信息
4. 检查防火墙设置
```

### 问题 2: 文件上传失败
```
解决方案：
1. 检查文件格式（只支持 PDF/MD/TXT）
2. 确认文件大小 < 100MB
3. 检查后端日志获取详细错误
4. 确保 backend/data/uploads 目录存在
```

### 问题 3: 知识图谱不显示
```
解决方案：
1. 确认后端已返回正确的图谱数据
2. 检查浏览器控制台 JavaScript 错误
3. 验证 ECharts 库是否正确加载
4. 尝试刷新页面
```

### 问题 4: RAG 查询无结果
```
解决方案：
1. 确保 RAG 索引已构建（/api/rag/status）
2. 验证教材已上传和解析
3. 尝试修改查询问题
4. 增加 top_k 参数值
```

## 📊 性能指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| API 响应时间 | < 2s | P95 响应时间 |
| 页面加载时间 | < 3s | 首屏加载 |
| 图谱渲染性能 | 500+ 节点 | 支持最大规模 |
| 并发用户数 | 100+ | 同时连接数 |
| 系统可用性 | 99%+ | 年度可用性 |

## 🔐 安全性

- ✅ 文件上传验证（类型、大小）
- ✅ 输入数据清洁和验证
- ✅ CORS 跨域配置
- ✅ 错误信息不泄露内部细节
- ✅ 文件隔离存储

## 📝 许可证

MIT License - 详见 [LICENSE](./LICENSE)

## 👥 贡献者

- **后端开发**: Backend Agent
- **前端开发**: Frontend Agent
- **文档和部署**: Documentation & Deployment Agent

## 📞 支持

如有问题或建议，请：
1. 查看 [FAQ](./docs/FAQ.md)
2. 提交 Issue
3. 联系开发团队

## 🗺️ 项目路线图

### v1.0.0 (当前版本)
- ✅ 基础文件管理
- ✅ 知识图谱构建
- ✅ RAG 检索
- ✅ 反馈系统

### v1.1.0 (计划)
- 用户权限管理
- 批量操作支持
- 高级搜索过滤
- 数据导出功能

### v2.0.0 (计划)
- 插件系统
- 自定义工作流
- 多语言支持
- 移动应用

## 📈 最新更新

**最后更新**: 2024-01-15

详见 [CHANGELOG.md](./CHANGELOG.md)

---

**EduGraph Fusion** - 让知识管理更高效 | Made with ❤️ by the Team
