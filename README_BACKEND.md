# 教材知识底座 - 后端服务

## 项目结构

```
backend/
├── __init__.py
├── main.py                      # FastAPI 应用主文件
├── models/
│   ├── __init__.py
│   └── schemas.py               # Pydantic 数据模型定义
├── services/
│   ├── __init__.py
│   ├── parser.py                # 文件解析服务（PDF/Markdown/TXT）
│   ├── storage.py               # 文件存储和元数据管理
│   └── report_stats.py          # 统计报告生成
└── routers/
    ├── __init__.py
    ├── upload.py                # 文件上传 API
    └── textbooks.py             # 教材和统计 API

requirements.txt                 # Python 依赖
.env.example                    # 环境变量示例
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 根据需要编辑 .env 文件
```

### 3. 运行服务

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

或直接运行：

```bash
python -m backend.main
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 健康检查

```bash
GET /health
```

### 文件上传

```bash
POST /api/upload
Content-Type: multipart/form-data

Body:
  file: <binary>
```

响应示例：
```json
{
  "status": "success",
  "message": "File uploaded successfully",
  "data": {
    "textbook_id": "textbook_abc123def456",
    "filename": "chapter1.pdf",
    "file_type": "pdf",
    "file_size": 1024000
  }
}
```

### 解析教材

```bash
POST /api/parse/{textbook_id}?chunk_size=1000
```

响应示例：
```json
{
  "status": "success",
  "message": "Successfully parsed 10 pages, 3 chapters",
  "data": {
    "textbook_id": "textbook_abc123def456",
    "chapter_count": 3,
    "total_words": 5000,
    "chapters": [
      {
        "id": "textbook_abc123def456_ch_0",
        "chapter_num": 0,
        "title": "Chapter 1",
        "start_page": 0,
        "end_page": 3,
        "word_count": 1500
      }
    ]
  }
}
```

### 获取教材列表

```bash
GET /api/textbooks?limit=100&offset=0
```

响应示例：
```json
{
  "status": "success",
  "data": {
    "total": 5,
    "limit": 100,
    "offset": 0,
    "textbooks": [
      {
        "id": "textbook_abc123def456",
        "filename": "chapter1.pdf",
        "title": "chapter1",
        "file_type": "pdf",
        "upload_time": "2024-01-01T12:00:00",
        "chapter_count": 3,
        "total_words": 5000,
        "total_pages": 10
      }
    ]
  }
}
```

### 获取单个教材详情

```bash
GET /api/textbooks/{textbook_id}
```

### 获取全局统计信息

```bash
GET /api/stats
```

响应示例：
```json
{
  "status": "success",
  "data": {
    "summary": {
      "total_textbooks": 5,
      "total_chapters": 15,
      "total_words": 50000,
      "avg_words_per_chapter": 3333.33
    },
    "file_types": {
      "pdf": 3,
      "markdown": 1,
      "txt": 1
    },
    "upload_times": {
      "2024-01-01": 2,
      "2024-01-02": 3
    },
    "textbooks_by_type": {
      "pdf": [...],
      "markdown": [...]
    },
    "top_textbooks": [...]
  }
}
```

### 获取单个教材的统计信息

```bash
GET /api/textbooks/{textbook_id}/stats
```

## 支持的文件格式

### PDF (.pdf)
- 使用 PyMuPDF 逐页解析
- 自动识别章节标题（支持多种格式）
- 无法识别章节时按固定字数分割

### Markdown (.md, .markdown)
- 按 `#` 标题分割为章节
- 保持原始文本格式

### 纯文本 (.txt)
- 按固定字数分割为伪章节

## 章节识别规则

解析器支持以下章节标题格式：

1. **中文格式**: `第一章 标题` / `第1章 标题`
2. **英文格式**: `Chapter 1 标题` / `Chapter I 标题`
3. **数字格式**: `1.1 标题` / `1 标题`

如果无法识别任何章节标题，会自动按 `chunk_size`（默认 1000 字）分割文本。

## 数据存储

- 上传的文件保存在: `./data/uploads/`
- 元数据和解析结果保存在: `./data/metadata/`
  - `{textbook_id}_metadata.json`: 教材元数据
  - `{textbook_id}_chapters.json`: 章节内容和统计

## 错误处理

所有 API 都返回统一的错误格式：

```json
{
  "status": "error",
  "message": "错误描述",
  "path": "/api/endpoint"
}
```

常见错误码：
- `400`: 请求参数错误或不支持的文件类型
- `404`: 资源不存在
- `500`: 服务器错误

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `API_HOST` | `0.0.0.0` | API 服务器地址 |
| `API_PORT` | `8000` | API 服务器端口 |
| `API_RELOAD` | `false` | 是否启用热重载 |
| `DATA_DIR` | `./data` | 数据存储目录 |
| `DEFAULT_CHUNK_SIZE` | `1000` | 默认文本分割大小 |
| `LOG_LEVEL` | `INFO` | 日志级别 |

## 测试 API

使用 curl：

```bash
# 上传文件
curl -X POST -F "file=@example.pdf" http://localhost:8000/api/upload

# 解析教材
curl -X POST http://localhost:8000/api/parse/textbook_abc123def456

# 获取教材列表
curl http://localhost:8000/api/textbooks

# 获取统计信息
curl http://localhost:8000/api/stats
```

## 限制

- 最大文件大小: 100MB
- 单次分页返回最多: 1000 项
- 默认文本分割大小: 1000 字
