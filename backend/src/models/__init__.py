"""
SQLAlchemy 数据模型 — 学舟核心表结构
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


def gen_id():
    return uuid.uuid4().hex[:12]


class Textbook(Base):
    __tablename__ = "textbooks"

    id = Column(String(12), primary_key=True, default=gen_id)
    title = Column(String(256), nullable=False)
    course_name = Column(String(256), default="")
    semester = Column(String(64), default="")
    status = Column(String(32), default="pending")  # pending|processing|done|error
    created_at = Column(DateTime, default=datetime.utcnow)

    chapters = relationship("Chapter", back_populates="textbook", cascade="all, delete-orphan")
    lectures = relationship("Lecture", back_populates="textbook", cascade="all, delete-orphan")


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(String(12), primary_key=True, default=gen_id)
    textbook_id = Column(String(12), ForeignKey("textbooks.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(256), nullable=False)
    order = Column(Integer, default=0)
    content_md = Column(Text, default="")  # Markdown content
    chroma_ids = Column(Text, default="")  # comma-separated ChromaDB vector IDs

    textbook = relationship("Textbook", back_populates="chapters")


class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(String(12), primary_key=True, default=gen_id)
    textbook_id = Column(String(12), ForeignKey("textbooks.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(256), default="")
    audio_path = Column(String(512), default="")
    transcript = Column(Text, default="")  # Whisper 转写全文
    summary = Column(Text, default="")  # LLM 摘要
    key_points = Column(Text, default="")  # JSON: 重点列表
    status = Column(String(32), default="pending")  # pending|transcribing|summarizing|done
    lecture_date = Column(String(32), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    textbook = relationship("Textbook", back_populates="lectures")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(String(12), primary_key=True, default=gen_id)
    title = Column(String(256), default="")
    source_type = Column(String(32), default="text")  # text|textbook|lecture
    source_ids = Column(Text, default="")  # JSON array
    source_content = Column(Text, default="")  # 原始输入文本
    questions_json = Column(Text, default="")  # JSON: 题目列表
    status = Column(String(32), default="pending")  # pending|generating|done|error
    created_at = Column(DateTime, default=datetime.utcnow)

    submissions = relationship("QuizSubmission", back_populates="quiz", cascade="all, delete-orphan")


class QuizSubmission(Base):
    __tablename__ = "quiz_submissions"

    id = Column(String(12), primary_key=True, default=gen_id)
    quiz_id = Column(String(12), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    answers_json = Column(Text, default="")  # JSON: {q1: "A", q2: "True", ...}
    score = Column(Float, default=0.0)
    total = Column(Integer, default=0)
    feedback_json = Column(Text, default="")  # JSON: 逐题批改结果
    created_at = Column(DateTime, default=datetime.utcnow)

    quiz = relationship("Quiz", back_populates="submissions")
    wrong_items = relationship("WrongBookItem", back_populates="submission", cascade="all, delete-orphan")


class WrongBookItem(Base):
    __tablename__ = "wrong_book"

    id = Column(String(12), primary_key=True, default=gen_id)
    submission_id = Column(String(12), ForeignKey("quiz_submissions.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, default="")
    user_answer = Column(Text, default="")
    correct_answer = Column(Text, default="")
    knowledge_point = Column(String(256), default="")
    review_count = Column(Integer, default=0)
    next_review_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("QuizSubmission", back_populates="wrong_items")
