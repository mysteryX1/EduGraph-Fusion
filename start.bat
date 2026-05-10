@echo off
REM EduGraph Fusion - Windows 启动脚本
REM 打开两个终端，分别启动后端和前端

echo.
echo ================================================================================
echo  EduGraph Fusion 系统启动脚本
echo ================================================================================
echo.
echo 本脚本将在两个新窗口中启动后端服务和前端应用
echo.

REM 检查是否已在项目目录
if not exist "backend\run.py" (
    echo 错误: 请在项目根目录运行此脚本
    echo 正确用法: cd 黑客松2 && start.bat
    pause
    exit /b 1
)

echo ✓ 项目目录验证通过
echo.

REM 启动后端（在新窗口）
echo 启动后端服务...
start "EduGraph Backend" cmd /k "cd backend && python -m venv venv && venv\Scripts\activate && pip install -r ..\requirements.txt && python run.py"

REM 等待 2 秒让后端启动
timeout /t 2 /nobreak

REM 启动前端（在新窗口）
echo 启动前端应用...
start "EduGraph Frontend" cmd /k "cd frontend && npm install && npm run dev"

echo.
echo ================================================================================
echo  启动完成！
echo ================================================================================
echo.
echo 后端访问地址: http://localhost:8000
echo 后端 API 文档: http://localhost:8000/docs
echo.
echo 前端访问地址: http://localhost:3000
echo.
echo 请等待 2-3 分钟让依赖完全安装
echo.
echo ================================================================================
echo.
pause
