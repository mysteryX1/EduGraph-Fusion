# 项目结构详细说明

## 完整目录树

```
黑客松2/
├── backend/                          # FastAPI 后端应用
│   ├── __init__.py                   # 包初始化
│   ├── main.py                       # FastAPI 应用主文件，定义路由和中间件
│   │
│   ├── models/                       # 数据模型层
│   │   ├── __init__.py               # 模型导出
│   │   └── schemas.py                # Pydantic 数据模型
│   │       ├── KGNode               # 知识图谱节点
│   │       ├── KGEdge               # 知识图谱边
│   │       ├── Citation             # 引用信息
│   │       ├── Chapter              # 章节信息
│   │       ├── Textbook             # 教材信息
│   │       ├── KGExtraction         # 知识图谱提取结果
│   │       ├── MergeDecision        # 合并决策
│   │       ├── RagAnswer            # RAG 答案
│   │       ├── ParseResult          # 解析结果
│   │       ├── TextbookMetadata     # 教材元数据
│   │       └── Stats                # 统计信息
│   │
│   ├── services/                     # 业务逻辑层
│   │   ├── __init__.py               # 服务导出
│   │   ├── parser.py                 # 文件解析服务
│   │   │   ├── ChapterParser         # 章节识别
│   │   │   ├── PDFParser             # PDF 解析（支持逐页处理）
│   │   │   ├── MarkdownParser        # Markdown 解析
│   │   │   ├── TextParser            # 文本解析
│   │   │   └── ParserFactory         # 解析器工厂
│   │   ├── storage.py                # 文件存储和元数据管理
│   │   │   └── FileStorage           # 存储管理
│   │   │       ├── save_uploaded_file()    # 保存上传文件
│   │   │       ├── save_parse_result()     # 保存解析结果
│   │   │       ├── load_chapters()         # 加载章节
│   │   │       ├── load_metadata()         # 加载元数据
│   │   │       ├── load_textbook()         # 加载完整教材
│   │   │       ├── list_all_textbooks()    # 列出所有教材
│   │   │       └── delete_textbook()       # 删除教材
│   │   └── report_stats.py           # 统计报告生成
│   │       └── StatsReporter         # 统计报告
│   │           ├── generate_stats()   # 生成统计
│   │           ├── get_detailed_stats()  # 详细统计
│   │           └── get_textbook_stats()  # 教材统计
│   │
│   └── routers/                      # 路由层（API 端点）
│       ├── __init__.py               # 路由导出
│       ├── upload.py                 # 文件上传 API
│       │   └── POST /api/upload      # 上传文件
│       └── textbooks.py              # 教材管理 API
│           ├── POST /api/parse/{id}  # 解析教材
│           ├── GET /api/textbooks    # 获取教材列表
│           ├── GET /api/textbooks/{id}      # 获取教材详情
│           ├── GET /api/stats        # 获取全局统计
│           └── GET /api/textbooks/{id}/stats # 教材统计
│
├── data/                             # 数据存储目录（自动创建）
│   ├── uploads/                      # 上传的文件
│   └── metadata/                     # 元数据和解析结果
│       ├── {textbook_id}_metadata.json   # 教材元数据
│       └── {textbook_id}_chapters.json   # 章节内容
│
├── temp/                             # 临时文件目录（自动创建）
│
├── requirements.txt                  # Python 依赖列表
├── .env.example                      # 环境变量示例
├── run.py                            # 快速启动脚本
├── test_api.py                       # API 集成测试脚本
├── README_BACKEND.md                 # 详细文档
├── QUICKSTART.md                     # 快速开始指南
└── PROJECT_STRUCTURE.md              # 本文件
```

## 核心模块说明

### 1. Models (backend/models/)

**schemas.py** - 定义所有数据模型

| 模型 | 用途 |
|------|------|
| `KGNode` | 知识图谱节点（概念、实体等） |
| `KGEdge` | 知识图谱边（关系连接） |
| `Citation` | 引用信息（来源、位置） |
| `Chapter` | 章节数据（包含内容和统计） |
| `Textbook` | 教材完整信息 |
| `KGExtraction` | 知识提取结果 |
| `MergeDecision` | 章节合并决策 |
| `RagAnswer` | RAG 系统答案 |
| `ParseResult` | 解析结果 |
| `TextbookMetadata` | 教材元信息 |
| `Stats` | 统计数据 |

### 2. Services (backend/services/)

#### parser.py - 文件解析服务

**支持的格式：**
- **PDF**: 使用 PyMuPDF，逐页处理，支持自动章节识别
- **Markdown**: 按 `#` 标题分割
- **Text**: 按固定字数分割

**章节识别模式：**
```
第一章 标题        (中文格式)
Chapter 1 标题     (英文格式)
1.1 标题          (数字格式)
```

**处理流程：**
1. 逐行/逐页读取文件
2. 识别章节标题
3. 分割和存储内容
4. 生成统计信息

#### storage.py - 存储管理

**职责：**
- 保存上传的文件
- 管理元数据
- 持久化解析结果
- 提供查询接口

**存储位置：**
```
./data/
├── uploads/              # 上传的源文件
│   └── {uuid}_{filename}
└── metadata/             # 元数据和解析结果
    ├── {textbook_id}_metadata.json
    └── {textbook_id}_chapters.json
```

#### report_stats.py - 统计报告

**功能：**
- 生成全局统计
- 生成详细统计
- 教材级别统计
- 文件类型分布

**统计指标：**
- 教材总数
- 章节总数
- 字数统计
- 平均章节长度
- 上传时间分布

### 3. Routers (backend/routers/)

#### upload.py - 上传 API

```
POST /api/upload
```

**功能：**
- 接收文件上传
- 验证文件类型（PDF/MD/TXT）
- 检查文件大小（≤100MB）
- 生成教材 ID
- 保存文件和元数据

**响应：**
```json
{
  "status": "success",
  "data": {
    "textbook_id": "textbook_xyz123",
    "filename": "chapter1.pdf",
    "file_type": "pdf",
    "file_size": 1024000
  }
}
```

#### textbooks.py - 教材管理 API

**API 列表：**

| 方法 | 路由 | 说明 |
|------|------|------|
| POST | `/api/parse/{textbook_id}` | 解析教材文件 |
| GET | `/api/textbooks` | 获取教材列表（分页） |
| GET | `/api/textbooks/{textbook_id}` | 获取教材详情 |
| GET | `/api/stats` | 获取全局统计 |
| GET | `/api/textbooks/{textbook_id}/stats` | 获取教材统计 |

### 4. Main (backend/main.py)

**FastAPI 应用配置：**
- 定义 CORS 中间件
- 注册所有路由
- 全局异常处理
- 生命周期管理（启动和关闭）

**基础端点：**
- `GET /` - API 信息
- `GET /health` - 健康检查
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc

## 数据流

### 文件上传和解析流程

```
上传文件 (Upload)
    ↓
验证文件 (Validate)
    ├─ 检查类型
    ├─ 检查大小
    └─ 检查内容
    ↓
保存文件 (Save)
    ├─ 生成 UUID
    └─ 存储到 ./data/uploads/
    ↓
解析文件 (Parse)
    ├─ 选择合适的解析器
    ├─ 逐页/逐行处理
    ├─ 识别章节标题
    └─ 生成 ParseResult
    ↓
保存结果 (Persist)
    ├─ 保存元数据到 JSON
    └─ 保存章节内容到 JSON
    ↓
返回结果 (Response)
    └─ 返回统计信息
```

### 查询流程

```
API 请求 (GET /api/textbooks/{id})
    ↓
加载元数据 (Load Metadata)
    └─ 读取 {id}_metadata.json
    ↓
加载章节 (Load Chapters)
    └─ 读取 {id}_chapters.json
    ↓
构建响应 (Build Response)
    └─ 组合元数据和章节数据
    ↓
返回 JSON
```

## 依赖关系

```
main.py
├── routers/
│   ├── upload.py
│   │   ├── services/storage.py
│   │   └── models/schemas.py
│   └── textbooks.py
│       ├── services/
│       │   ├── parser.py
│       │   ├── storage.py
│       │   └── report_stats.py
│       └── models/schemas.py

services/
├── parser.py
│   ├── models/schemas.py
│   └── fitz (PyMuPDF)
├── storage.py
│   ├── models/schemas.py
│   └── pathlib
└── report_stats.py
    ├── services/storage.py
    └── models/schemas.py
```

## 配置参数

### 环境变量 (.env)

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `API_HOST` | `0.0.0.0` | 绑定地址 |
| `API_PORT` | `8000` | 监听端口 |
| `API_RELOAD` | `false` | 热重载 |
| `DATA_DIR` | `./data` | 数据目录 |
| `DEFAULT_CHUNK_SIZE` | `1000` | 默认分割大小 |
| `LOG_LEVEL` | `INFO` | 日志级别 |

### 系统限制

| 限制项 | 值 |
|--------|-----|
| 最大文件大小 | 100 MB |
| 最大分页返回 | 1000 项 |
| 默认 Chunk 大小 | 1000 字 |
| 允许的文件类型 | pdf, md, markdown, txt |

## 扩展点

### 添加新的文件类型

1. 在 `parser.py` 中新增 `XxxParser` 类
2. 在 `ParserFactory.get_parser()` 中添加条件
3. 在 `upload.py` 中更新 `ALLOWED_EXTENSIONS`

### 添加新的 API 端点

1. 在 `routers/` 中创建新的路由模块
2. 定义路由函数
3. 在 `main.py` 中注册路由

### 自定义统计指标

修改 `report_stats.py` 中的 `StatsReporter` 类

## 文件生成和删除

### 自动创建

| 目录 | 时机 |
|------|------|
| `./data` | 应用启动 |
| `./data/uploads` | 应用启动 |
| `./data/metadata` | 应用启动 |
| `./temp` | 应用启动 |

### 自动删除

| 文件 | 时机 |
|------|------|
| `./temp/*` | 应用关闭 |

### 手动删除

删除 `./data` 可以重置所有数据：
```bash
rm -rf ./data
```

## 开发指南

### 调试技巧

1. **启用日志**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **使用 Swagger UI 测试**
访问 http://localhost:8000/docs

3. **查看数据文件**
```bash
# 查看元数据
cat ./data/metadata/{textbook_id}_metadata.json

# 查看章节
cat ./data/metadata/{textbook_id}_chapters.json
```

### 性能优化

- PDF 逐页处理避免内存溢出
- 元数据和章节分离存储
- 查询时只加载需要的数据

### 错误处理

所有 API 都遵循统一的错误格式：
```json
{
  "status": "error",
  "message": "错误描述",
  "path": "/api/endpoint"
}
```

HTTP 状态码：
- `200` - 成功
- `400` - 请求错误
- `404` - 资源不存在
- `500` - 服务器错误
