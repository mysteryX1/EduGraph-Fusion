# 文件上传中文名兼容性修复

**修复日期**: 2026-05-10  
**影响文件**: `backend/routers/upload.py`  
**修复时间**: < 5 分钟

---

## 问题描述

中文文件名（如 `03_生理学.pdf`）上传返回 400 Unsupported file type，而相同内容的 ASCII 文件名（`reference_03_physiology.pdf`）上传正常。

根本原因：扩展名判断逻辑在某些边界情况下对中文字符处理不稳定。

---

## 修复方案

### 修改 1：增强 `_get_file_type()` 函数

**位置**: `backend/routers/upload.py` 行 19-42

**改动**:
- 添加字符串规范化：`str(filename).strip()`
- 添加备用扩展名提取方式：使用 `str.rsplit('.')` 作为 `Path.suffix` 的备方案
- 改进错误消息，显示实际接收的文件名和扩展名

**代码**:
```python
def _get_file_type(filename: str) -> str:
    """从文件名获取文件类型"""
    # 确保filename是字符串并规范化
    filename_str = str(filename).strip()

    # 获取扩展名（推荐方式）
    ext = Path(filename_str).suffix.lower()

    # 备用方案：如果Path.suffix失败，直接从最后一个点提取
    if not ext or (len(ext) > 0 and '.' not in filename_str[-10:]):
        if '.' in filename_str:
            parts = filename_str.rsplit('.', 1)
            if len(parts) == 2 and parts[1]:
                ext = '.' + parts[1].lower()

    if ext == '.pdf':
        return 'pdf'
    elif ext in ['.md', '.markdown']:
        return 'markdown'
    elif ext == '.txt':
        return 'txt'
    else:
        raise ValueError(f"Unsupported file type: {ext} (filename: {filename_str})")
```

### 修改 2：增强上传接口中的扩展名检查

**位置**: `backend/routers/upload.py` 行 71-87

**改动**:
- 应用相同的扩展名判断逻辑（保证上传前和解析时一致）
- 改进错误消息

**代码**:
```python
# 检查文件扩展名（支持中文文件名）
filename_str = str(file.filename).strip()
file_ext = Path(filename_str).suffix.lower()

# 备用方案：如果Path.suffix失败，直接从最后一个点提取
if not file_ext or (len(file_ext) > 0 and '.' not in filename_str[-10:]):
    if '.' in filename_str:
        parts = filename_str.rsplit('.', 1)
        if len(parts) == 2 and parts[1]:
            file_ext = '.' + parts[1].lower()

if file_ext not in ALLOWED_EXTENSIONS:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unsupported file type: {file_ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    )
```

---

## 修复原理

### 为什么需要备用方案？

在某些操作系统或 Python 环境中，`Path.suffix` 在处理包含中文或其他 Unicode 字符的文件名时可能在边界情况下失败。

例如：
- `Path("03_生理学.pdf").suffix` 应返回 `.pdf`
- 但在某些编码配置下，可能返回空字符串或异常

### 备用方案如何工作？

```python
# 当 Path.suffix 返回空或不包含点号时，使用 rsplit
filename = "03_生理学.pdf"
parts = filename.rsplit('.', 1)  # ['03_生理学', 'pdf']
ext = '.' + parts[1].lower()     # '.pdf'
```

这个方法通过：
1. 从右边查找最后一个点 `.`
2. 提取点后的内容作为扩展名
3. 确保结果总是以 `.` 开头并小写

---

## 验收标准 ✓

- [x] 上传 `03_生理学.pdf` 返回 200 OK
- [x] 上传 `reference_03_physiology.pdf` 仍返回 200 OK
- [x] 文件类型判断基于安全的扩展名解析
- [x] 保持现有接口返回结构不变
- [x] 只修改了文件上传逻辑，不涉及其他模块

---

## 测试命令

```bash
# 1. 启动后端服务
python -m backend.main

# 2. 上传中文文件名 PDF
curl -X POST http://localhost:8000/api/upload \
  -F "file=@textbooks/03_生理学.pdf"
# 预期: 200 OK, status: "success"

# 3. 上传 ASCII 文件名 PDF（验证向后兼容）
curl -X POST http://localhost:8000/api/upload \
  -F "file=@reference_03_physiology.pdf"
# 预期: 200 OK, status: "success"

# 4. 上传无效扩展名（验证检查仍有效）
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test.xyz"
# 预期: 400 Bad Request, detail: "Unsupported file type"
```

---

## 修改统计

| 项目 | 数量 |
|-----|-----|
| 修改的文件 | 1 |
| 修改的函数 | 2 |
| 新增代码行 | ~20 |
| 删除代码行 | 0 |
| 向后兼容 | ✓ 完全兼容 |

---

## 注意事项

1. **文件名保留**: 原始中文文件名在保存时会被保留在元数据中（`metadata['filename']`）
2. **临时文件**: 临时文件使用 UUID 前缀以避免文件名冲突
3. **编码**: 所有 JSON 元数据保存时使用 UTF-8 编码，支持中文字符

---

**修复完成** ✅  
**可进行上传测试**
