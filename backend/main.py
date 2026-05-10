import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pathlib import Path
import uvicorn

from .routers import upload, textbooks, rag, feedback, report


# 初始化应用
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化目录
    Path("./data").mkdir(exist_ok=True)
    Path("./data/uploads").mkdir(exist_ok=True)
    Path("./data/metadata").mkdir(exist_ok=True)
    Path("./temp").mkdir(exist_ok=True)
    yield
    # 清理临时文件
    import shutil
    if Path("./temp").exists():
        shutil.rmtree("./temp")
        Path("./temp").mkdir(exist_ok=True)


app = FastAPI(
    title="教材知识底座 API",
    description="用于教材上传、解析和知识提取的后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 包含路由
app.include_router(upload.router)
app.include_router(textbooks.router)
app.include_router(rag.router)
app.include_router(feedback.router)
app.include_router(report.router)


# 基础路由
@app.get("/")
async def root():
    """根路由"""
    return {
        "status": "success",
        "message": "教材知识底座 API 服务",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /api/upload",
            "parse": "POST /api/parse/{textbook_id}",
            "list_textbooks": "GET /api/textbooks",
            "get_textbook": "GET /api/textbooks/{textbook_id}",
            "get_stats": "GET /api/stats",
            "textbook_stats": "GET /api/textbooks/{textbook_id}/stats",
            "rag_index": "POST /api/rag/index",
            "rag_query": "POST /api/rag/query",
            "rag_status": "GET /api/rag/status",
            "submit_feedback": "POST /api/feedback",
            "feedback_summary": "GET /api/feedback/summary",
            "generate_report": "POST /api/report/generate",
            "get_report": "GET /api/report/latest",
            "report_summary": "GET /api/report/summary",
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "message": "Service is running"
    }


# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP 异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal Server Error",
            "error": str(exc),
            "path": str(request.url)
        }
    )


if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    reload = os.getenv("API_RELOAD", "false").lower() == "true"

    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=reload
    )
