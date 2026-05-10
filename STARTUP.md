# 📌 EduGraph Fusion 完整启动指南

## 🎯 目标
本指南将帮助您快速启动和演示 EduGraph Fusion 系统。

## ⚙️ 系统要求

- **Python 3.8+**
- **Node.js 16+** （npm 11+）
- **Git**
- **4GB+ RAM**
- **2GB+ 磁盘空间**

验证命令：
```bash
python --version      # 应该 >= 3.8
node --version        # 应该 >= 16
npm --version         # 应该 >= 11
```

## 📦 项目结构

```
黑客松2/
├── backend/               # FastAPI 后端
│   ├── main.py           # 应用主文件
│   ├── run.py            # 启动脚本
│   ├── requirements.txt   # Python 依赖
│   ├── services/         # 业务逻辑
│   ├── routers/          # API 路由
│   └── data/             # 数据存储（gitignore）
├── frontend/             # React 前端
│   ├── package.json      # npm 配置
│   ├── vite.config.js    # Vite 配置
│   ├── src/
│   │   ├── App.jsx       # 主应用组件
│   │   ├── api.js        # API 调用层
│   │   ├── components/   # 6 个功能组件
│   │   ├── styles/       # CSS 样式
│   │   └── main.jsx      # 入口文件
│   ├── dist/             # 构建输出（gitignore）
│   └── node_modules/     # 依赖包（gitignore）
├── docs/                 # 文档
│   ├── 需求分析.md
│   ├── 系统设计.md
│   ├── Agent架构说明.md
│   └── 接口文档.md
├── .env                  # 环境变量（已创建）
├── .env.example          # 环境变量示例
├── .gitignore            # Git 忽略规则
├── README.md             # 项目说明
├── QUICKSTART.md         # 快速开始
├── DEPLOYMENT.md         # 部署指南
└── STARTUP.md            # 本文件
```

## 🚀 一键启动（5 分钟）

### 方案 A：顺序启动（推荐用于开发）

**终端 1 - 启动后端：**
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r ../requirements.txt

# 启动服务
python run.py
```

**验证后端成功：**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**终端 2 - 启动前端：**
```bash
cd frontend
npm install         # 首次运行
npm run dev         # 启动开发服务器
```

**验证前端成功：**
```
  ➜  Local:   http://localhost:3000/
```

**浏览器访问：**
- 打开 http://localhost:3000
- 看到 3 列布局（左侧教材、中间图谱、右侧面板）

### 方案 B：使用 npm 脚本启动所有服务

如果您的项目配置了 npm 脚本（根目录 package.json），可以：

```bash
# 在项目根目录
npm run start:all   # 同时启动前端和后端（如果配置）
```

## 📊 验证清单

### 1️⃣ 后端健康检查
```bash
# 在浏览器或命令行中访问
curl http://localhost:8000/health

# 应该返回
{"status":"healthy","message":"Service is running"}
```

### 2️⃣ 查看 API 文档
- 访问 http://localhost:8000/docs
- 看到 Swagger UI 和所有 API 端点列表

### 3️⃣ 前端页面检查
- 访问 http://localhost:3000
- 看到标题："🧠 EduGraph Fusion - 教材知识底座"
- 左侧：教材管理（空列表、统计卡片）
- 中间：知识图谱（显示 Mock 数据或加载状态）
- 右侧：5 个标签页（上传、合并、检索、反馈、报告）

### 4️⃣ 浏览器控制台检查
按 F12 打开开发者工具：
- **Console**: 无红色错误信息
- **Network**: API 请求状态为 200 或合理的 Mock 降级

## 🎬 演示流程（10 分钟）

### 第 1 步：上传教材
1. 点击右侧"上传"标签页
2. 点击"选择文件"，选择一个 PDF、Markdown 或 TXT 文件
3. 点击"上传"按钮
4. 看到成功消息和 textbook_id
5. （可选）点击"开始解析"查看解析结果

### 第 2 步：查看知识图谱
1. 等待中间区域加载完成
2. 看到节点和链接的可视化
3. 用鼠标滚轮缩放图谱
4. 拖拽移动节点
5. 点击任意节点，右侧显示"节点详情"

### 第 3 步：知识检索（RAG）
1. 点击右侧"检索"标签页
2. 点击"构建索引"按钮
3. 在文本框输入问题，如"什么是函数?"
4. 点击"搜索"按钮
5. 看到答案和引用来源

### 第 4 步：生成报告
1. 点击右侧"报告"标签页
2. 点击"生成新报告"按钮
3. 等待生成完成
4. 点击"查看详情"查看报告内容

### 第 5 步：反馈和合并（可选）
- **反馈**：点击"反馈"标签页，填写反馈表单
- **合并**：点击"合并"标签页，查看合并建议

## 🌐 API 端点速查

| 功能 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 上传文件 | POST | `/api/upload` | 支持 PDF/MD/TXT |
| 解析文件 | POST | `/api/parse/{id}` | 提取章节内容 |
| 教材列表 | GET | `/api/textbooks` | 已上传的教材 |
| 教材详情 | GET | `/api/textbooks/{id}` | 单个教材信息 |
| 统计信息 | GET | `/api/stats` | 系统统计数据 |
| 构建图谱 | POST | `/api/kg/build` | 知识图谱构建 |
| 获取图谱 | GET | `/api/kg` | 知识图谱数据 |
| 合并图谱 | POST | `/api/merge` | 图谱去重合并 |
| 合并建议 | GET | `/api/merge/decisions` | 合并建议列表 |
| 构建索引 | POST | `/api/rag/index` | RAG 索引 |
| 查询 RAG | POST | `/api/rag/query` | 语义检索查询 |
| RAG 状态 | GET | `/api/rag/status` | 索引状态 |
| 提交反馈 | POST | `/api/feedback` | 用户反馈 |
| 反馈统计 | GET | `/api/feedback/summary` | 反馈统计 |
| 生成报告 | POST | `/api/report/generate` | 生成报告 |
| 最新报告 | GET | `/api/report/latest` | 最新报告 |
| 报告统计 | GET | `/api/report/summary` | 报告统计 |

## 🛠️ 常见问题

### Q1: 端口被占用
```bash
# Windows: 查找占用 8000 端口的进程
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

### Q2: npm install 失败
```bash
# 尝试清除缓存
npm cache clean --force
npm install
```

### Q3: 前端无法连接后端
1. 确保后端服务正在运行：访问 http://localhost:8000/health
2. 检查防火墙是否阻止 8000 端口
3. 在 `.env` 中确认 `VITE_API_URL=http://localhost:8000/api`

### Q4: Python 版本错误
```bash
# 检查版本
python --version

# 如果不是 3.8+，升级 Python
# 从 python.org 下载，或使用 pyenv/conda
```

### Q5: 图谱不显示
1. 打开浏览器 F12，查看 Console 是否有 JavaScript 错误
2. 检查 Network 标签中 `/api/kg` 请求是否成功
3. 如果后端不可用，应该显示 Mock 数据

## 📝 环境变量说明

文件：`.env`

**前端相关：**
```bash
# API 基础 URL (Vite 用法)
VITE_API_URL=http://localhost:8000/api
```

**后端相关：**
```bash
# API 服务器
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
```

**数据存储：**
```bash
DATA_DIR=./backend/data
UPLOADS_DIR=./backend/data/uploads
PROCESSED_DIR=./backend/data/processed
METADATA_DIR=./backend/data/metadata
VECTOR_INDEX_DIR=./backend/data/vector_index
REPORTS_DIR=./backend/data/reports
```

**功能开关：**
```bash
ENABLE_RAG=true              # 启用 RAG 检索
ENABLE_KG_MERGE=true         # 启用图谱合并
ENABLE_AUTO_REPORT=true      # 启用自动报告
```

## 🎓 文档导航

- **快速开始**：[QUICKSTART.md](./QUICKSTART.md) - 10 分钟快速体验
- **部署指南**：[DEPLOYMENT.md](./DEPLOYMENT.md) - 完整联调和部署
- **项目说明**：[README.md](./README.md) - 完整项目文档
- **需求分析**：[docs/需求分析.md](./docs/需求分析.md) - 功能需求
- **系统设计**：[docs/系统设计.md](./docs/系统设计.md) - 系统架构
- **接口文档**：[docs/接口文档.md](./docs/接口文档.md) - API 详细说明
- **Agent 说明**：[docs/Agent架构说明.md](./docs/Agent架构说明.md) - 开发模式

## ✅ 快速检查清单

- [ ] Python 3.8+ 已安装
- [ ] Node.js 16+ 已安装
- [ ] Git 已安装
- [ ] `.env` 文件已创建
- [ ] `backend/` 虚拟环境已激活
- [ ] `pip install -r requirements.txt` 成功
- [ ] `frontend/node_modules/` 目录存在
- [ ] 后端服务运行在 8000 端口
- [ ] 前端开发服务运行在 3000 端口
- [ ] 浏览器能访问 http://localhost:3000
- [ ] 浏览器 Console 无错误信息
- [ ] Mock 数据正确显示

## 🎉 成功标志

当您看到以下现象时，说明系统启动成功：

1. ✅ 后端输出："Uvicorn running on http://0.0.0.0:8000"
2. ✅ 前端输出："Local: http://localhost:3000/"
3. ✅ 浏览器显示 EduGraph Fusion 界面
4. ✅ 左侧显示教材统计卡片
5. ✅ 中间显示知识图谱（Mock 数据）
6. ✅ 右侧显示 5 个功能标签页
7. ✅ 浏览器 Console 无红色错误

## 🚨 故障排查

如果遇到问题，请按以下顺序排查：

1. **检查进程**：确保后端和前端都在运行
2. **检查日志**：查看终端输出是否有错误信息
3. **检查网络**：验证 localhost:8000 和 localhost:3000 是否可访问
4. **检查依赖**：确认 `npm install` 和 `pip install` 都成功
5. **清除缓存**：删除 `frontend/dist` 和 `frontend/node_modules`，重新安装
6. **查看文档**：参考 [DEPLOYMENT.md](./DEPLOYMENT.md) 的详细排查步骤

## 📞 获取帮助

- 查看项目文档：`docs/` 目录下的 4 个文件
- 查看接口文档：访问 http://localhost:8000/docs（后端运行时）
- 查看实时日志：在启动的终端中查看输出

---

**祝您使用愉快！🎉**

如有任何问题，请参考完整的 [DEPLOYMENT.md](./DEPLOYMENT.md) 文档。
