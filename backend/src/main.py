"""
StudyOS Backend — FastAPI Application
"""
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库"""
    init_db()
    yield


app = FastAPI(
    title="StudyOS API",
    description="个人学习操作系统后端 API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── 全局异常处理：确保所有错误返回 JSON ───
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    # 打印完整 traceback 到控制台
    print(f"\n{'='*60}")
    print(f"[ERROR] {request.method} {request.url.path}")
    print(f"[ERROR] {type(exc).__name__}: {exc}")
    print(f"[ERROR] {tb}")
    print(f"{'='*60}\n")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "detail": f"{type(exc).__name__}: {str(exc)[:500]}",
            "traceback": tb[-800:],  # 末尾几行
        },
    )


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "0.1.0"}


# 注册路由
from .api import router as quiz_router  # noqa: E402

app.include_router(quiz_router, prefix="/api/quizzes", tags=["题目"])
