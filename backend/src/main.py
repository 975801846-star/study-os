"""
StudyOS Backend — FastAPI Application
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "0.1.0"}


# 注册路由（Phase 1-5 逐步启用）
# from .api import textbooks, lectures, quizzes, search, wrong_book, dashboard, export
# app.include_router(textbooks.router, prefix="/api/textbooks", tags=["教材"])
# app.include_router(lectures.router, prefix="/api/lectures", tags=["课堂"])
# app.include_router(quizzes.router, prefix="/api/quizzes", tags=["题目"])
# app.include_router(search.router, prefix="/api/search", tags=["搜索"])
# app.include_router(wrong_book.router, prefix="/api/wrong-book", tags=["错题本"])
# app.include_router(dashboard.router, prefix="/api/dashboard", tags=["仪表盘"])
# app.include_router(export.router, prefix="/api/export", tags=["导出"])
