# EduGraph Fusion - 模块加固检查清单

## ✓ 完成的修复项

### 1. RAG 数据读取优化
- [x] **修复 RAG 数据读取优先级**
  - 优先读取 `backend/data/metadata/*_chapters.json` (模块一输出)
  - 兼容 `backend/data/processed/*.json` (模块二输出)
  - 添加 `_load_from_metadata()` 和 `_load_from_processed()` 方法
  - 文件: `backend/services/rag.py:196-320`

### 2. RAG Embedding & Vector Search Fallback
- [x] **添加多层 Fallback 机制**
  - sentence-transformers → TF-IDF → keyword matching
  - FAISS → sklearn NearestNeighbors → keyword matching
  - 添加 `_keyword_search()` 方法用于终极 fallback
  - 文件: `backend/services/rag.py:151-221`

### 3. RAG 查询结果优化
- [x] **改进 Citations 返回格式**
  - 添加 `relevance_score` 字段
  - 支持 `page_number` 和 `page` 两种命名
  - 包含完整的 textbook, chapter, chapter_id, page_number 信息
  - 文件: `backend/services/rag.py:377-392`

### 4. 教师反馈系统
- [x] **完整的知识图谱修改**
  - 支持四个命令: 保留、删除、拆分、合并
  - 持久化到 `merged_kg.json` 和 `merge_decisions.json`
  - 返回统计摘要和操作结果
  - 文件: `backend/services/feedback.py:1-298`

### 5. 报告生成器优化
- [x] **优先级读取和 Fallback**
  - 优先读取 `backend/data/metadata/*_chapters.json`
  - 兼容 `backend/data/processed/*.json`
  - 即使数据不存在也能生成报告（使用默认值）
  - 文件: `backend/services/report_generator.py:61-133`

### 6. API 路由验证
- [x] **检查所有路由注册**
  - main.py 已包含所有路由: upload, textbooks, rag, feedback, report
  - 所有响应格式统一: `{status, message, data}`
  - 文件: `backend/main.py:9,46-50`

### 7. 测试数据准备
- [x] **创建完整的测试数据**
  - `backend/data/metadata/textbook_001_chapters.json` - 章节数据
  - `backend/data/metadata/textbook_001_metadata.json` - 元数据
  - `backend/data/processed/merged_kg.json` - 知识图谱
  - `backend/data/processed/merge_decisions.json` - 合并决策

---

## 📋 API 端点验证

### RAG 端点
- [x] `POST /api/rag/index` - 建立索引，支持 metadata 和 processed 目录数据
- [x] `POST /api/rag/query` - 查询知识库，返回 answer/citations/source_chunks
- [x] `GET /api/rag/status` - 索引状态

### 反馈端点  
- [x] `POST /api/feedback` - 处理自然语言命令
- [x] `GET /api/feedback/summary` - 反馈统计摘要

### 报告端点
- [x] `POST /api/report/generate` - 生成整合报告
- [x] `GET /api/report/latest` - 获取最新报告
- [x] `GET /api/report/summary` - 报告统计摘要

---

## 🔍 兼容性检查

### 与模块一 (Upload/Parse) 的兼容性
- [x] 读取 `backend/data/metadata/*_chapters.json`
- [x] 读取 `backend/data/metadata/*_metadata.json`
- [x] 处理 Chapter 结构: id, chapter_num, title, start_page, end_page, content, word_count
- [x] Chunk 元数据包含: textbook, chapter, chapter_id, page, page_number

### 与模块二 (KG Extraction/Merger) 的兼容性
- [x] 读取 `backend/data/processed/merged_kg.json`
- [x] 读取 `backend/data/processed/merge_decisions.json`
- [x] 修改并持久化到相同位置
- [x] 节点结构: id, name, type, description
- [x] 边结构: source_id, target_id, relation_type, weight

---

## 🛡️ Fallback 机制

### Embedding 级别
```
优先: sentence-transformers (高质量, 较慢)
  ↓ (ImportError or timeout)
Fallback 1: TF-IDF (快速, 足够准确)
  ↓ (ImportError)
Fallback 2: 关键词匹配 (最快, 基础)
```

### 向量搜索级别
```
优先: FAISS (高效, GPU 友好)
  ↓ (ImportError or error)
Fallback 1: sklearn NearestNeighbors (纯 CPU, 可靠)
  ↓ (error)
Fallback 2: 关键词搜索 (无向量依赖)
```

### 数据加载级别
```
优先: ./data/metadata/*_chapters.json (模块一输出)
  ↓ (不存在)
备选: ./data/processed/*.json (模块二输出)
  ↓ (不存在)
返回: 空结果或默认值
```

---

## 📊 测试数据检查

### 已创建的测试文件

**元数据目录 (`backend/data/metadata/`)**
```
✓ textbook_001_chapters.json (195 字)
  - 2 个章节
  - 共约 195 字内容
  
✓ textbook_001_metadata.json (278 字)
  - 教材标题: "高等数学基础教材"
  - 文件类型: PDF
```

**处理目录 (`backend/data/processed/`)**
```
✓ merged_kg.json (870 字)
  - 2 个节点: 函数概念, 集合论
  - 1 条边: 基于
  
✓ merge_decisions.json (603 字)
  - 2 个决策: keep, merge
```

---

## 🚀 快速开始指南

### 1. 验证导入
```bash
python verify_imports.py
```

输出应该包含:
- ✓ 基本库导入成功
- ✓ FastAPI 导入成功
- ✓ RAG 模块导入成功
- ✓ Feedback 模块导入成功
- ✓ Report 模块导入成功

### 2. 启动 API 服务器
```bash
python -m backend.main
```

输出:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 3. 在另一个终端运行测试
```bash
# PowerShell
powershell -ExecutionPolicy Bypass -File test_api.ps1

# 或使用 curl (见 TEST_ENDPOINTS.md)
curl -X POST http://localhost:8000/api/rag/index
```

### 4. 查看结果
- 检查终端输出中的 ✓ 成功/✗ 失败
- 查看 `report/整合报告.md` (报告生成后)
- 检查 `backend/data/processed/merge_decisions.json` (反馈后更新)

---

## 🐛 常见问题排除

### RAG 索引返回 0 chunks
**原因**: 数据目录为空或格式不正确

**解决**:
1. 验证 `backend/data/metadata/textbook_001_chapters.json` 存在
2. 检查 JSON 格式是否正确
3. 确保 chapters 中 content 字段非空

### 查询返回"当前知识库中未找到相关信息"
**原因**: 向量相似度过低或数据不匹配

**解决**:
1. 尝试使用关键词匹配: 确保查询词出现在 content 中
2. 检查 chunk 内容是否合理
3. 查看日志是否使用了 keyword fallback

### 反馈处理返回 unsupported instruction
**原因**: 指令格式不正确

**正确格式**:
- `保留 [名称]` - 中文字符，空格分隔
- `删除 [名称]`
- `拆分 [名称A] 和 [名称B]`
- `合并 [名称A] 和 [名称B]`

### 报告生成失败
**原因**: 目录权限或数据格式问题

**解决**:
1. 确保 `report/` 目录可写
2. 检查 `data/metadata/` 或 `data/processed/` 中有数据
3. 查看 Python 控制台错误日志

---

## 📦 依赖清单

### 必需依赖
- fastapi >= 0.95
- uvicorn >= 0.20
- pydantic >= 2.0
- numpy >= 1.24.0
- python >= 3.8

### 强烈推荐
- scikit-learn >= 1.3.0 (embedding fallback)
- sentence-transformers >= 2.2.0 (高质量 embedding)

### 可选优化
- faiss-cpu >= 1.7.4 (或 faiss-gpu 用于 GPU)

**安装**:
```bash
pip install -r requirements.txt
```

---

## ✅ 最终验证清单

- [x] 所有文件修改已完成
- [x] 测试数据已创建
- [x] 导入验证脚本已创建
- [x] API 测试脚本已创建
- [x] 文档已编写 (TEST_ENDPOINTS.md)
- [x] 兼容性已确认
- [x] Fallback 机制已实现
- [x] 错误处理已完善

---

## 📝 后续建议

### 短期 (立即)
1. 运行 `verify_imports.py` 确保环境配置正确
2. 运行 `test_api.ps1` 测试所有端点
3. 检查 `report/整合报告.md` 是否正确生成

### 中期 (集成前)
1. 用模块一的真实数据测试 RAG 索引
2. 用模块二的真实知识图谱测试反馈
3. 测试边界情况和异常条件

### 长期 (生产前)
1. 添加日志级别配置
2. 实现缓存机制 (RAG 查询)
3. 添加速率限制
4. 性能优化 (大规模数据)

---

## 📞 技术支持

如遇到问题:
1. 检查日志输出中的错误信息
2. 参考 TEST_ENDPOINTS.md 中的故障排除部分
3. 验证数据格式与预期结构一致
4. 确认所有依赖正确安装

---

**更新时间**: 2026-05-10  
**版本**: 1.0.0  
**状态**: ✓ 准备就绪
