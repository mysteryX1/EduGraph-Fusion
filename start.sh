#!/bin/bash

# EduGraph Fusion - macOS/Linux 启动脚本

echo ""
echo "================================================================================"
echo "  EduGraph Fusion 系统启动脚本"
echo "================================================================================"
echo ""
echo "本脚本将在后台启动后端服务和前端应用"
echo ""

# 检查是否已在项目目录
if [ ! -f "backend/run.py" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    echo "正确用法: cd 黑客松2 && bash start.sh"
    exit 1
fi

echo "✓ 项目目录验证通过"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    exit 1
fi

echo "✓ Python 和 Node.js 已安装"
echo ""

# 启动后端
echo "启动后端服务..."
(
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r ../requirements.txt
    python3 run.py
) &
BACKEND_PID=$!

# 等待后端启动
sleep 2

# 启动前端
echo "启动前端应用..."
(
    cd frontend
    npm install
    npm run dev
) &
FRONTEND_PID=$!

# 等待应用启动
sleep 3

echo ""
echo "================================================================================"
echo "  启动完成！"
echo "================================================================================"
echo ""
echo "后端访问地址: http://localhost:8000"
echo "后端 API 文档: http://localhost:8000/docs"
echo ""
echo "前端访问地址: http://localhost:3000"
echo ""
echo "后端进程 PID: $BACKEND_PID"
echo "前端进程 PID: $FRONTEND_PID"
echo ""
echo "停止服务，请运行: kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "================================================================================"
echo ""

# 保持脚本运行
wait
