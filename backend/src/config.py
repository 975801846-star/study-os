"""
应用配置 — 使用 pydantic-settings 管理环境变量
"""
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """全局配置，自动从 .env 文件加载"""

    # LLM — 按任务复杂度分级
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL_PRO: str = "deepseek-v4-pro"     # 出题/批改/摘要
    DEEPSEEK_MODEL_FLASH: str = "deepseek-v4-flash"   # 分类/闲聊/简单问答

    # 语音转写 (本地 Whisper)
    WHISPER_PROVIDER: str = "local"   # local (免费开源)
    WHISPER_MODEL: str = "medium"     # tiny/base/small/medium/large-v3

    # 向量化 (本地 sentence-transformers)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSIONS: int = 384

    # 数据库
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    SQLITE_PATH: str = "./data/studyos.db"

    # 文件存储
    UPLOAD_DIR: str = "./data/uploads"
    EXPORT_DIR: str = "./data/exports"
    MAX_UPLOAD_SIZE_MB: int = 500

    # 服务器
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000"

    # 日志
    LOG_LEVEL: str = "INFO"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()

# 确保数据目录存在
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.EXPORT_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.SQLITE_PATH).parent.mkdir(parents=True, exist_ok=True)
