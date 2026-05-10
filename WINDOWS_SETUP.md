# 🪟 Windows 系统启动指南

## 📌 问题

在 Windows PowerShell 中，直接运行 `npm run dev` 可能会出现权限错误或无法打开。

## ✅ 解决方案

### 方案 1：使用完整 npm 命令路径（推荐）

**在项目的 `frontend` 目录中执行：**

```powershell
& "C:\Program Files\nodejs\npm.cmd" run dev
```

或者，如果 npm 安装在其他位置：

```powershell
# 先查找 npm 的位置
where npm

# 然后使用找到的完整路径
& "C:\<your-npm-path>\npm.cmd" run dev
```

### 方案 2：使用 npm install 全局安装（一次性）

```powershell
# 安装完成后，npm 会被添加到系统 PATH
npm install -g npm@latest

# 之后就可以直接使用
npm run dev
```

### 方案 3：使用批处理脚本

在 `frontend` 目录中创建 `run.bat`：

```batch
@echo off
cd /d "%~dp0"
"%PROGRAMFILES%\nodejs\npm.cmd" run dev
pause
```

然后双击 `run.bat` 执行。

### 方案 4：使用 Git Bash 或 WSL

```bash
cd frontend
npm run dev
```

## 🔧 完整启动步骤

### 方案 A：PowerShell（管理员）

```powershell
# 打开 PowerShell（以管理员身份运行）

# 后端（终端 1）
cd "D:\我的大学\博一下\黑客松2\backend"
python -m venv venv
venv\Scripts\activate
pip install -r ../requirements.txt
python run.py

# 前端（终端 2）
cd "D:\我的大学\博一下\黑客松2\frontend"
& "C:\Program Files\nodejs\npm.cmd" install
& "C:\Program Files\nodejs\npm.cmd" run dev
```

### 方案 B：使用 cmd.exe（命令提示符）

```cmd
rem 后端（终端 1）
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r ../requirements.txt
python run.py

rem 前端（终端 2）
cd frontend
npm install
npm run dev
```

## 🐛 常见错误及解决

### 错误 1：无法将 "npm" 识别为内部或外部命令

**原因**：npm 不在系统 PATH 中

**解决**：
1. 检查 npm 是否已安装：
   ```powershell
   where npm
   ```

2. 如果找不到，重新安装 Node.js（确保勾选"Add to PATH"）

3. 或使用完整路径：
   ```powershell
   & "C:\Program Files\nodejs\npm.cmd" run dev
   ```

### 错误 2：无法加载文件 ...\npm.ps1，因为在此系统上禁止执行脚本

**原因**：PowerShell 执行策略过严格

**解决**：
```powershell
# 方案 1：使用 cmd.exe 代替
# 或

# 方案 2：修改执行策略（需要管理员权限）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 错误 3：port 3000 already in use

**原因**：前端端口被占用

**解决**：
```powershell
# 查找占用 3000 端口的进程
netstat -ano | findstr :3000

# 关闭该进程（如果 PID 是 1234）
taskkill /PID 1234 /F

# 或者在 vite.config.js 中修改端口
# server: { port: 3001 }
```

## 📝 创建快速启动脚本

### 创建 `start-backend.bat`

```batch
@echo off
cd /d "%~dp0\backend"
python -m venv venv
call venv\Scripts\activate.bat
pip install -r ../requirements.txt
echo.
echo 启动后端服务...
python run.py
pause
```

### 创建 `start-frontend.bat`

```batch
@echo off
cd /d "%~dp0\frontend"
call "%PROGRAMFILES%\nodejs\npm.cmd" install
call "%PROGRAMFILES%\nodejs\npm.cmd" run dev
pause
```

### 创建 `start-all.bat`

```batch
@echo off
echo 启动 EduGraph Fusion...
echo.

REM 检查是否在项目根目录
if not exist "backend\run.py" (
    echo 错误：请在项目根目录运行此脚本
    pause
    exit /b 1
)

echo 启动后端服务...
start "EduGraph Backend" cmd /k "cd backend && python -m venv venv && venv\Scripts\activate && pip install -r ..\requirements.txt && python run.py"

timeout /t 3 /nobreak

echo 启动前端应用...
start "EduGraph Frontend" cmd /k "cd frontend && %PROGRAMFILES%\nodejs\npm.cmd install && %PROGRAMFILES%\nodejs\npm.cmd run dev"

echo.
echo 启动完成！请等待 2-3 分钟。
echo 前端：http://localhost:3000
echo 后端：http://localhost:8000
pause
```

## ✨ 最佳实践

1. **使用 cmd.exe**：对 Node.js 项目最兼容
2. **以管理员身份运行**：避免权限问题
3. **使用全局 npm**：一次配置，永久使用
4. **创建批处理脚本**：一键启动，避免手动输入

## 📚 相关链接

- [Node.js 官方](https://nodejs.org/)
- [npm 官方文档](https://docs.npmjs.com/)
- [PowerShell 执行策略](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies)

---

**如有问题，请参考项目的 STARTUP.md 和 DEPLOYMENT.md 文档。**
