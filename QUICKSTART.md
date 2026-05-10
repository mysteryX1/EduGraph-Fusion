# EduGraph Fusion - 快速开始指南

## 📋 项目概述

**EduGraph Fusion** 是一个完整的教材知识管理系统，包括：
- 🔙 **后端**: FastAPI 服务，处理文件上传、解析、知识图谱构建、RAG 检索等
- 🎨 **前端**: React 单页应用，提供交互式用户界面
- 📚 **功能**: 多教材管理、知识图谱可视化、语义检索、用户反馈、报告生成

## 🚀 10 分钟快速启动（完整系统）

### 前置条件
- Python 3.8+
- Node.js 16+
- Git

### 1️⃣ 克隆项目并配置环境

```bash
# 克隆项目
git clone <repository-url>
cd 黑客松2

# 复制配置文件
cp .env.example .env
```

### 2️⃣ 启动后端服务（终端 1）

```bash
cd backend

# 创建虚拟环境（首次）
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r ../requirements.txt

# 启动服务
python run.py
```

**输出示例**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 3️⃣ 启动前端应用（终端 2）

```bash
cd frontend

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

**输出示例**:
```
  VITE v5.0.8  ready in 245 ms
  ➜  Local:   http://localhost:3000/
```

### 4️⃣ 打开浏览器

- **前端应用**: http://localhost:3000 ⭐ **从这里开始**
- **后端 API 文档**: http://localhost:8000/docs
- **后端健康检查**: http://localhost:8000/health

## 📚 主要功能

| 功能 | 端点 | 说明 |
|------|------|------|
| 文件上传 | `POST /api/upload` | 支持 PDF、Markdown、TXT |
| 文件解析 | `POST /api/parse/{id}` | 解析文件并提取章节 |
| 查看列表 | `GET /api/textbooks` | 查看所有上传的教材 |
| 查看详情 | `GET /api/textbooks/{id}` | 查看教材的详细信息 |
| 统计信息 | `GET /api/stats` | 查看全局统计数据 |

## 🧪 测试 API

### 使用 Swagger UI（推荐）

1. 访问 http://localhost:8000/docs
2. 点击各个 API 端点
3. 点击 "Try it out" 进行测试

### 使用命令行工具

```bash
# 健康检查
curl http://localhost:8000/health

# 上传文件
curl -X POST -F "file=@example.pdf" http://localhost:8000/api/upload

# 获取教材列表
curl http://localhost:8000/api/textbooks

# 获取统计信息
curl http://localhost:8000/api/stats
```

### 使用测试脚本

```bash
python test_api.py
```

## 📁 项目结构速览

```
backend/
├── main.py                # FastAPI 应用
├── models/schemas.py      # 数据模型
├── services/
│   ├── parser.py         # 文件解析
│   ├── storage.py        # 存储管理
│   └── report_stats.py   # 统计报告
└── routers/
    ├── upload.py         # 上传 API
    └── textbooks.py      # 教材 API
```

## ⚙️ 配置

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

主要配置项：
- `API_HOST`: API 服务器地址（默认 0.0.0.0）
- `API_PORT`: API 服务器端口（默认 8000）
- `API_RELOAD`: 是否启用热重载（默认 false）
- `DEFAULT_CHUNK_SIZE`: 默认文本分割大小（默认 1000）

## 🛠️ 常见操作

### 上传并解析 PDF

```bash
# 1. 上传文件
curl -X POST -F "file=@mybook.pdf" http://localhost:8000/api/upload

# 返回示例:
# {
#   "data": {
#     "textbook_id": "textbook_abc123def456"
#   }
# }

# 2. 解析文件（使用上面返回的 textbook_id）
curl -X POST http://localhost:8000/api/parse/textbook_abc123def456

# 3. 获取详情
curl http://localhost:8000/api/textbooks/textbook_abc123def456
```

### 批量上传和解析

```bash
# 创建脚本 batch_upload.sh
for file in *.pdf; do
  response=$(curl -s -X POST -F "file=@$file" http://localhost:8000/api/upload)
  textbook_id=$(echo $response | jq -r '.data.textbook_id')
  echo "解析 $file -> $textbook_id"
  curl -X POST http://localhost:8000/api/parse/$textbook_id
done
```

## 📊 响应格式

所有 API 都返回统一的 JSON 格式：

**成功响应：**
```json
{
  "status": "success",
  "message": "操作成功",
  "data": { ... }
}
```

**错误响应：**
```json
{
  "status": "error",
  "message": "错误描述",
  "path": "/api/endpoint"
}
```

## 🔍 支持的文件格式

### PDF (.pdf)
- 自动识别章节标题
- 支持多种章节格式（第X章、Chapter X、1.1 标题等）
- 无法识别时按固定字数分割

### Markdown (.md, .markdown)
- 按 `#` 标题分割为章节
- 保持原始格式

### 纯文本 (.txt)
- 按固定字数分割为伪章节

## 🐛 故障排除

### 无法连接到服务

```bash
# 检查服务是否在运行
curl http://localhost:8000/health

# 如果不行，重新启动服务
python run.py
```

### 文件上传失败

1. 检查文件大小（最大 100MB）
2. 检查文件格式（必须是 PDF、MD 或 TXT）
3. 检查磁盘空间

### 解析失败

1. 确保文件格式正确
2. 查看日志输出了解具体错误
3. 尝试调整 `chunk_size` 参数

## 📚 进阶使用

### 自定义 chunk_size

```bash
curl -X POST "http://localhost:8000/api/parse/textbook_abc123?chunk_size=500"
```

### 分页查询教材

```bash
# 获取前 10 条
curl "http://localhost:8000/api/textbooks?limit=10&offset=0"

# 获取 11-20 条
curl "http://localhost:8000/api/textbooks?limit=10&offset=10"
```

## 📖 更多信息

- 详细文档: 查看 `README_BACKEND.md`
- API 文档: http://localhost:8000/docs
- 更多示例: 查看 `test_api.py`

## ✅ 完成清单

- [x] 文件上传 API
- [x] 文件解析服务
- [x] 教材管理 API
- [x] 统计信息 API
- [x] 错误处理
- [x] 数据持久化
- [x] 文档完整
- [ ] 单元测试（可选）
- [ ] 部署配置（可选）

## 💡 提示

1. **开发时使用 Swagger UI** (`/docs`) 进行 API 测试，比手写 curl 命令更方便
2. **查看日志** 可以了解 API 的运行情况和错误信息
3. **数据保存在** `./data/` 目录，可以安全删除来重置状态
4. **支持热重载** 开发时修改代码会自动重启服务

---

**遇到问题？** 检查日志输出或查看 `README_BACKEND.md` 获取更详细的信息。
