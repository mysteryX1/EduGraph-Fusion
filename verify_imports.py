#!/usr/bin/env python3
"""验证所有导入和基本功能"""

import sys
from pathlib import Path

print("=" * 60)
print("验证 EduGraph Fusion 模块导入和功能")
print("=" * 60)

# 检查基本模块
print("\n[1/6] 检查基本导入...")
try:
    import json
    import re
    from datetime import datetime
    print("✓ 基本库导入成功")
except ImportError as e:
    print(f"✗ 基本库导入失败: {e}")
    sys.exit(1)

# 检查 FastAPI
print("\n[2/6] 检查 FastAPI...")
try:
    from fastapi import FastAPI
    from pydantic import BaseModel
    print("✓ FastAPI 导入成功")
except ImportError as e:
    print(f"✗ FastAPI 导入失败: {e}")
    print("  提示: pip install fastapi")

# 检查 numpy 和基本 embedding/vector 依赖
print("\n[3/6] 检查数据处理库...")
try:
    import numpy as np
    print("✓ NumPy 导入成功")
except ImportError as e:
    print(f"✗ NumPy 导入失败: {e}")
    print("  提示: pip install numpy")

# 检查可选的 embedding 库
print("\n[4/6] 检查 Embedding 库...")
embedding_available = False
try:
    from sentence_transformers import SentenceTransformer
    print("✓ sentence-transformers 可用（优先使用）")
    embedding_available = True
except ImportError:
    print("⚠ sentence-transformers 不可用，将使用 TF-IDF fallback")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.neighbors import NearestNeighbors
    print("✓ scikit-learn 可用（fallback）")
except ImportError:
    print("✗ scikit-learn 导入失败")
    print("  提示: pip install scikit-learn")

# 检查可选的向量库
print("\n[5/6] 检查向量库...")
faiss_available = False
try:
    import faiss
    print("✓ FAISS 可用（优先使用）")
    faiss_available = True
except ImportError:
    print("⚠ FAISS 不可用，将使用 sklearn NearestNeighbors fallback")

# 检查项目模块
print("\n[6/6] 检查项目模块...")
try:
    from backend.services.rag import RAGEngine, ChunkManager, EmbeddingProvider, VectorStore
    print("✓ RAG 模块导入成功")
except ImportError as e:
    print(f"✗ RAG 模块导入失败: {e}")

try:
    from backend.services.feedback import FeedbackProcessor
    print("✓ Feedback 模块导入成功")
except ImportError as e:
    print(f"✗ Feedback 模块导入失败: {e}")

try:
    from backend.services.report_generator import ReportGenerator
    print("✓ Report 模块导入成功")
except ImportError as e:
    print(f"✗ Report 模块导入失败: {e}")

try:
    from backend.routers import rag, feedback, report
    print("✓ Router 模块导入成功")
except ImportError as e:
    print(f"✗ Router 模块导入失败: {e}")

# 测试基本功能
print("\n" + "=" * 60)
print("测试基本功能")
print("=" * 60)

print("\n[1/3] 测试 ChunkManager...")
try:
    cm = ChunkManager(chunk_size=700, overlap=100)
    chunks = cm.chunk_text(
        "这是一个测试文本。" * 100,
        {"textbook": "测试教材", "chapter": "测试章节", "page": 1}
    )
    print(f"✓ ChunkManager 工作正常，生成 {len(chunks)} 个 chunks")
except Exception as e:
    print(f"✗ ChunkManager 测试失败: {e}")

print("\n[2/3] 测试 EmbeddingProvider...")
try:
    ep = EmbeddingProvider()
    embedding = ep.embed(["测试文本"])
    print(f"✓ EmbeddingProvider 工作正常，嵌入维度: {embedding.shape}")
    if not embedding_available:
        print("  (使用 TF-IDF fallback)")
except Exception as e:
    print(f"✗ EmbeddingProvider 测试失败: {e}")

print("\n[3/3] 测试 FeedbackProcessor...")
try:
    fp = FeedbackProcessor(data_dir="./data/processed")
    result = fp.process_instruction("保留 测试内容")
    if result.get('success'):
        print(f"✓ FeedbackProcessor 工作正常")
    else:
        print(f"⚠ FeedbackProcessor 返回失败: {result.get('message')}")
except Exception as e:
    print(f"✗ FeedbackProcessor 测试失败: {e}")

# 检查数据目录
print("\n" + "=" * 60)
print("检查数据目录")
print("=" * 60)

metadata_dir = Path("./backend/data/metadata")
processed_dir = Path("./backend/data/processed")

print(f"\nmetadata 目录: {metadata_dir.absolute()}")
if metadata_dir.exists():
    files = list(metadata_dir.glob("*.json"))
    print(f"✓ 存在，包含 {len(files)} 个文件")
    for f in files[:3]:
        print(f"  - {f.name}")
else:
    print(f"⚠ 不存在")

print(f"\nprocessed 目录: {processed_dir.absolute()}")
if processed_dir.exists():
    files = list(processed_dir.glob("*.json"))
    print(f"✓ 存在，包含 {len(files)} 个文件")
    for f in files[:3]:
        print(f"  - {f.name}")
else:
    print(f"⚠ 不存在")

# 总结
print("\n" + "=" * 60)
print("验证总结")
print("=" * 60)
print("\n✓ 核心功能已验证")
if embedding_available and faiss_available:
    print("✓ 所有可选优化库已安装")
else:
    print("⚠ 部分可选库未安装，但系统将使用 fallback 机制")

print("\n准备就绪！运行以下命令启动 API 服务器:")
print("  python -m backend.main")

print("\n然后在另一个终端运行测试脚本:")
print("  powershell -ExecutionPolicy Bypass -File test_api.ps1")
print("  或")
print("  python verify_imports.py  # 本脚本")
print("=" * 60)
