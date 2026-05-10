# EduGraph Fusion - 部署和启动指南

## 🎯 前端启动命令

### 开发环境启动

```bash
cd frontend
npm install
npm run dev
```

**访问地址**: http://localhost:3000

### 生产环境构建

```bash
cd frontend
npm run build
```

**输出目录**: `frontend/dist/`

## 🔧 后端启动命令

### 开发环境启动

```bash
cd backend
python run.py
```

**API 地址**: http://localhost:8000
**API 文档**: http://localhost:8000/docs

### 虚拟环境设置（首次）

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r ../requirements.txt
```

## 📋 完整启动步骤

### 第一次启动（完整配置）

#### 步骤 1: 克隆项目并配置

```bash
git clone <repository-url>
cd 黑客松2
cp .env.example .env
```

#### 步骤 2: 后端初始化和启动

**终端 1**:
```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r ../requirements.txt

# 启动后端
python run.py
```

**验证后端启动**:
```bash
# 在另一个终端中
curl http://localhost:8000/health
# 应该返回: {"status":"healthy","message":"Service is running"}
```

#### 步骤 3: 前端初始化和启动

**终端 2**:
```bash
cd frontend

# 安装依赖
npm install

# 启动前端开发服务器
npm run dev
```

#### 步骤 4: 打开浏览器

访问 **http://localhost:3000** 即可使用系统。

### 后续启动（快速）

**后端启动**（终端 1）:
```bash
cd backend
# 激活虚拟环境（如果未激活）
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
python run.py
```

**前端启动**（终端 2）:
```bash
cd frontend
npm run dev
```

## 📱 联调检查步骤

### 1. 基础连接检查

- [ ] 后端服务运行: http://localhost:8000/health
- [ ] API 文档可访问: http://localhost:8000/docs
- [ ] 前端应用运行: http://localhost:3000
- [ ] 浏览器控制台无 CORS 错误

### 2. 页面加载检查

- [ ] 页面正常加载，布局完整
- [ ] 左侧教材管理区显示
- [ ] 中间知识图谱区显示（可能是空的或 Mock 数据）
- [ ] 右侧功能面板显示 5 个 Tab

### 3. 功能联调流程

#### 3.1 上传功能测试

1. 准备测试文件：
   - 创建一个 `test.txt` 或 `test.md` 文件
   - 或使用现有的 PDF 文件

2. 进行上传测试：
   - [ ] 点击"上传"Tab
   - [ ] 选择文件
   - [ ] 点击"上传"按钮
   - [ ] 验证上传成功消息
   - [ ] 确认 textbook_id 已生成
   - [ ] 查看左侧教材列表是否更新

3. 解析文件：
   - [ ] 点击"开始解析"按钮
   - [ ] 等待解析完成（可能需要几秒）
   - [ ] 验证章节统计信息

#### 3.2 知识图谱检查

1. 图谱显示：
   - [ ] 中间区域显示网络图
   - [ ] 如果没有数据，应显示 Mock 数据
   - [ ] 验证节点和链接是否可见

2. 图谱交互：
   - [ ] 滚轮缩放图谱
   - [ ] 拖拽移动节点
   - [ ] 点击节点查看详情（右侧应显示节点信息）

#### 3.3 检索功能测试（RAG）

1. 构建索引：
   - [ ] 点击"检索"Tab
   - [ ] 点击"构建索引"按钮
   - [ ] 等待索引构建完成

2. 执行查询：
   - [ ] 在输入框输入问题，如 "什么是函数"
   - [ ] 点击"搜索"按钮
   - [ ] 验证返回结果和引用来源

#### 3.4 其他功能快速检查

- [ ] **合并 Tab**: 显示合并建议列表
- [ ] **反馈 Tab**: 能够提交反馈表单
- [ ] **报告 Tab**: 能够生成报告

### 4. 错误处理检查

#### 4.1 网络错误模拟

1. 停止后端服务：
   - [ ] 前端仍可访问（UI 不崩溃）
   - [ ] 应显示错误提示
   - [ ] 应使用 Mock 数据进行降级展示

2. 重新启动后端：
   - [ ] 前端应能自动恢复连接
   - [ ] 功能应恢复正常

#### 4.2 边界情况测试

- [ ] 上传超大文件（> 100MB）：应显示错误
- [ ] 上传不支持的格式（如 .docx）：应显示错误
- [ ] 输入空问题：应显示验证错误

### 5. 性能检查

#### 5.1 打开浏览器开发者工具（F12）

1. **Network 标签**:
   - [ ] 验证 API 请求成功（状态 200）
   - [ ] 检查请求响应时间（应 < 2 秒）
   - [ ] 验证没有 404 错误

2. **Console 标签**:
   - [ ] 无 JavaScript 错误
   - [ ] 无未捕获的异常
   - [ ] 允许有 CORS 预检请求

3. **Performance 标签**（可选）:
   - [ ] 首屏加载时间 < 3 秒
   - [ ] 图谱渲染流畅（FPS > 30）

## 🐛 常见问题排查

### 问题 1: 端口被占用

**症状**: 启动时报错 "Address already in use"

**解决**:
```bash
# Windows: 查找占用 8000 端口的进程
netstat -ano | findstr :8000
# 然后用 taskkill /PID <PID> /F 杀死进程

# macOS/Linux:
lsof -i :8000
# 然后 kill -9 <PID>
```

**临时方案**: 修改 .env 中的 API_PORT

### 问题 2: 前端无法连接后端

**症状**: 浏览器显示连接错误，Network 标签中看到 CORS 错误

**检查**:
1. 后端是否运行: `curl http://localhost:8000/health`
2. 后端是否监听 0.0.0.0:8000
3. 防火墙是否阻止了连接

**解决**:
```bash
# 确保后端启动了 CORS 中间件
# 在 backend/main.py 中验证:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境可用 *
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 问题 3: 知识图谱不显示

**症状**: 中间区域空白或显示 Loading

**检查**:
1. 打开 F12 Console，查看是否有 JavaScript 错误
2. Network 标签中查看 `/api/kg` 请求是否成功
3. 是否有数据返回

**解决**:
- 使用 Mock 数据（应自动降级）
- 确保至少上传和解析了一个文件

### 问题 4: npm install 失败

**症状**: 报错 "npm ERR! code ERESOLVE"

**解决**:
```bash
cd frontend
npm install --legacy-peer-deps
```

### 问题 5: Python 版本不兼容

**症状**: 启动后端时报错关于 f-string 或类型提示

**检查**:
```bash
python --version  # 应该是 3.8+
```

**升级 Python**（如需要）:
- 访问 python.org 下载最新版本
- 或使用包管理器: `brew install python@3.11`

## 📊 验收测试清单

完整的联调验收应包含以下检查：

### 功能验收
- [ ] 所有 API 端点均可正常调用
- [ ] 前端能调用所有后端 API
- [ ] 所有 UI 组件正常显示
- [ ] 所有按钮和表单可交互
- [ ] 错误处理和提示信息正确

### 性能验收
- [ ] API 响应时间 < 2 秒
- [ ] 页面加载时间 < 3 秒
- [ ] 支持 500+ 个节点的知识图谱显示
- [ ] 支持 10+ 并发连接

### 安全验收
- [ ] 文件上传验证正常
- [ ] 输入清洁和验证正常
- [ ] CORS 配置正确
- [ ] 敏感错误不泄露

### 兼容性验收
- [ ] 在 Chrome/Firefox/Safari 中正常显示
- [ ] 响应式设计在不同分辨率下正常
- [ ] 在 Windows/macOS/Linux 上运行正常

## 🚀 生产部署建议

### 前端部署

```bash
# 构建
npm run build

# 使用 Nginx 部署
# nginx.conf 配置:
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
    }
}
```

### 后端部署

```bash
# 使用 Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "backend.main:app"

# 或使用 Docker
docker build -f Dockerfile.backend -t edugraph-backend:latest .
docker run -p 8000:8000 edugraph-backend:latest
```

### Docker Compose 一键部署

```bash
docker-compose up -d
```

## 📞 支持

遇到问题？
1. 查看 [README.md](./README.md) 的常见问题部分
2. 查看 [接口文档](./docs/接口文档.md)
3. 检查 [系统设计](./docs/系统设计.md)
4. 提交 Issue 或联系开发团队

---

**最后更新**: 2024-01-15
**维护人**: EduGraph Fusion Team
