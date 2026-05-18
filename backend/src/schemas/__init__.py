"""
Pydantic 请求/响应模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ──── Quiz ────

class QuizGenerateRequest(BaseModel):
    source_content: str = Field(..., min_length=50, description="输入文本（≥50字符）")
    source_type: str = Field(default="text", description="text|textbook|lecture")
    question_types: list[str] = Field(
        default=["choice", "tf", "short_answer"],
        description="题型: choice / tf / short_answer / case_study",
    )
    count: int = Field(default=5, ge=1, le=30, description="题目数量")
    difficulty: str = Field(default="basic", description="basic|advanced|comprehensive")
    language: str = Field(default="zh", description="zh|en")


class QuestionItem(BaseModel):
    id: str
    type: str  # choice | tf | short_answer | case_study
    question: str
    options: Optional[list[str]] = None  # choice 才有
    answer: str
    explanation: str = ""
    knowledge_point: str = ""


class QuizResponse(BaseModel):
    id: str
    title: str
    source_type: str
    status: str
    questions: list[QuestionItem] = []
    created_at: str = ""


# ──── Submission ────

class SubmitAnswerRequest(BaseModel):
    quiz_id: str
    answers: dict[str, str]  # {q1: "A", q2: "True", q3: "..."}


class FeedbackItem(BaseModel):
    question_id: str
    question: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str = ""
    knowledge_point: str = ""


class SubmissionResponse(BaseModel):
    id: str
    quiz_id: str
    score: float
    total: int
    pct: float
    feedback: list[FeedbackItem] = []
    wrong_count: int
    created_at: str = ""


# ──── Generic ────

class APIResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: float = 0.0
    message: str = ""
