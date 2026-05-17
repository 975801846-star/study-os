"""
数据库初始化 — SQLite + ChromaDB
"""
import chromadb
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import settings

# SQLite 引擎
engine = create_engine(
    f"sqlite:///{settings.SQLITE_PATH}",
    connect_args={"check_same_thread": False},  # SQLite 单线程限制
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ChromaDB 客户端
chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)


def get_db() -> Session:
    """FastAPI 依赖注入：获取 SQLite 会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_chroma_collection(name: str = "textbooks"):
    """获取或创建 ChromaDB 集合"""
    return chroma_client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


def init_db():
    """初始化数据库表"""
    from .models import Base  # noqa: F401

    Base.metadata.create_all(bind=engine)
