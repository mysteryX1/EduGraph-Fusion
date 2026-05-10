#!/usr/bin/env python
"""
快速启动脚本

使用示例:
    python run.py
"""

import os
import sys
import subprocess

# 确保在项目根目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 检查依赖
try:
    import fastapi
    import pydantic
    import fitz
except ImportError:
    print("依赖不完整，正在安装...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# 启动应用
if __name__ == "__main__":
    import uvicorn

    print("""
    ╔════════════════════════════════════════╗
    ║   教材知识底座 API 服务启动中...         ║
    ╚════════════════════════════════════════╝

    API 文档访问: http://localhost:8000/docs
    健康检查: http://localhost:8000/health
    """)

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
