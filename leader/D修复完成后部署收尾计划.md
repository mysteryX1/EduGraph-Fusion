# D 修复完成后部署收尾计划

更新时间：2026-05-10 14:45 CST

## 当前状态

用户反馈：Agent D 已直接修复并完成本地验证。

上一轮 D 负责的 P0 项包括：

1. RAG 检索输入后页面异常/白屏。
2. 知识图谱从均匀球形改为更能体现关键节点的拓扑布局。
3. 图谱节点文字与背景对比度。
4. 中文文件名 PDF 上传 400。

现在默认这些项已经由 D 完成本地验证。下一步不要再扩散功能需求，进入部署打包和最终演示准备。

## 当前必须保留的要求

项目后续必须打包成 Docker，并部署到魔搭创空间。这个是 P0 收尾任务，不能遗漏。

## 下一步优先级

### P0：确认 D 的最终验证证据

需要 D 给出或更新一份最终报告，至少包含：

1. 修改文件列表。
2. `npm.cmd run build` 是否通过。
3. RAG 检索是否不再白屏。
4. 图谱拓扑是否已有核心-外围层次。
5. 图谱文字是否清晰可读。
6. 中文文件名 `textbooks/03_生理学.pdf` 上传是否 200。
7. 后端 `/health`、RAG、KG、Merge、Feedback、Report 主链路是否 200。

### P0：Docker 化

需要新增或确认这些文件：

1. `Dockerfile.backend`
2. `Dockerfile.frontend`
3. `docker-compose.yml`
4. `.dockerignore`
5. 魔搭创空间部署说明，例如 `docs/ModelScope部署说明.md`

### P0：公网部署适配

需要确认：

1. 前端 API 地址不能写死 `localhost`。
2. Vite 通过 `VITE_API_BASE_URL` 读取后端地址。
3. Docker/魔搭环境中，前端能访问后端服务。
4. 后端 CORS 允许魔搭创空间前端域名，或者临时允许 `*` 用于比赛演示。
5. 大文件上传目录和 `data/`、`report/` 目录在容器内可写。

## 给部署 Agent 的完整提示词

你是部署 Agent。当前本地功能已经由 Agent D 修复并验证。现在你的任务是把项目打包成 Docker，并准备部署到魔搭创空间。不要再改业务功能。

工作目录：

```powershell
D:\我的大学\博一下\黑客松2
```

技术栈：

- Backend：Python + FastAPI + Uvicorn。
- Frontend：React 18 + Vite + Axios + ECharts。
- 本地后端入口：`run.py`。
- 本地前端启动：`frontend/package.json` 中的 Vite dev server。

必须完成：

1. 新建 `Dockerfile.backend`。
2. 新建 `Dockerfile.frontend`。
3. 新建 `docker-compose.yml`。
4. 新建 `.dockerignore`。
5. 新建 `docs/ModelScope部署说明.md`。
6. 修改前端 API base URL 配置，使其支持环境变量 `VITE_API_BASE_URL`，不要写死 localhost。
7. 确认后端监听 `0.0.0.0:8000`。
8. 确认容器内 `data/`、`report/` 可写。

后端 Docker 要求：

- 使用 Python 3.10 或 3.11 slim。
- 安装 `requirements.txt`。
- 复制 `backend/`、`run.py`、必要配置和目录。
- 暴露 8000。
- 启动命令应能运行 FastAPI 服务。
- 如果使用 `run.py`，确认它监听 `0.0.0.0` 而不是只监听 `127.0.0.1`。

前端 Docker 要求：

- 使用 Node 18 或 20 构建。
- 优先使用 `npm ci`，如果 lockfile 不稳定再退回 `npm install`。
- 构建产物用 nginx 或等价静态服务器提供。
- 暴露 3000 或 80，最终文档写清楚。
- 支持构建参数：

```dockerfile
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
```

docker-compose 要求：

- `backend` 服务暴露 `8000:8000`。
- `frontend` 服务暴露 `3000:80` 或 `3000:3000`，以实际 Dockerfile 为准。
- `frontend` 依赖 `backend`。
- 挂载或声明数据目录：
  - `./data:/app/data`
  - `./report:/app/report`
- 设置前端构建 API 地址。若 compose 内部访问后端，可用 `/api` 代理或公网地址；如果没有 nginx 反向代理，文档中说明部署时要设置 `VITE_API_BASE_URL` 为公网后端地址。

魔搭创空间说明文档必须包含：

1. 本地 Docker 验证命令：

```powershell
docker compose up --build
```

2. 访问地址：

```text
Frontend: http://localhost:3000
Backend:  http://localhost:8000
```

3. 魔搭部署时需要配置的环境变量：

```text
VITE_API_BASE_URL=<后端公网地址>
PYTHONUNBUFFERED=1
```

4. 如果魔搭只暴露一个端口，说明需要选择“前端 nginx 反代 /api 到后端”或拆成两个 Space。
5. 上传 PDF、生成数据、报告目录需要持久化，否则容器重启会丢失。

验收标准：

1. `docker compose config` 通过。
2. `docker compose up --build` 能启动前后端。
3. 前端能打开。
4. `/health` 返回 200。
5. 前端能访问后端 API，不出现 localhost 写死导致的公网访问失败。
6. `docs/ModelScope部署说明.md` 写清楚部署步骤和风险。

禁止事项：

1. 不要再改 RAG、KG、Merge、Feedback 的业务逻辑。
2. 不要删除测试数据或教材。
3. 不要把 `node_modules/`、`frontend/dist/`、`test_artifacts/` 打进镜像上下文。
4. 不要把 `.env` 中的密钥写进 Dockerfile。

## 最后复测提示词

Docker 完成后，请让测试 Agent 再执行一次最终部署复测：

1. `docker compose up --build`。
2. 打开 `http://localhost:3000`。
3. 检查 `/health`。
4. 上传中文 PDF。
5. 构建 KG。
6. 查看图谱文字和拓扑。
7. RAG 查询。
8. Feedback 提交。
9. Report 生成和查看。
10. 记录是否可部署到魔搭创空间。

