"""
Quiz API — 出题 / 提交 / 批改 / 文件上传
"""
import hashlib
import json
import os
import tempfile
from datetime import datetime

import pymupdf  # PyMuPDF
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Quiz, QuizSubmission, WrongBookItem
from ..schemas import (
    FeedbackItem,
    MultiQuizGenerateRequest,
    QuestionItem,
    QuizGenerateRequest,
    QuizResponse,
    SubmitAnswerRequest,
    SubmissionResponse,
)
from ..services import (
    QuizServiceError,
    generate_quiz,
    generate_quiz_multi,
    grade_submission,
    hash_source,
    _lookup_cache,
    _save_to_cache,
    test_connection,
    detect_chapters,
)

router = APIRouter()


@router.get("/test-connection")
async def api_test_connection():
    """测试 DeepSeek API 连接（调试用）"""
    result = test_connection()
    return result


@router.post("/upload-source")
async def upload_source(file: UploadFile = File(...)):
    """上传文档提取文本（支持 PDF / TXT / MD）"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".txt", ".md", ".markdown"):
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {ext}，仅支持 PDF/TXT/MD")

    content_bytes = await file.read()
    max_size = 20 * 1024 * 1024  # 20MB
    if len(content_bytes) > max_size:
        raise HTTPException(status_code=400, detail="文件过大，限制 20MB")

    try:
        if ext == ".pdf":
            # PyMuPDF 解析 PDF
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(content_bytes)
                tmp_path = tmp.name

            doc = pymupdf.open(tmp_path)
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
            os.unlink(tmp_path)
        else:
            # TXT / MD 直接解码
            text = content_bytes.decode("utf-8", errors="replace")

        text = text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="文档内容为空")

        char_count = len(text)
        # 50 万字符上限（约一本教材），超出截断并提示
        max_chars = 500000
        truncated = char_count > max_chars
        if truncated:
            text = text[:max_chars] + "\n\n（内容过长，已截取前 50 万字符，建议分册/分章上传）"

        # 检测章节
        chapters = detect_chapters(text)
        # 章节过多时只取前 80 个
        if len(chapters) > 80:
            total_detected = len(chapters)
            chapters = chapters[:80]
            chapters.append({
                "index": 80,
                "title": f"（还有 {total_detected - 80}+ 个章节未显示，建议分章上传）",
                "content": "",
                "char_count": 0,
                "start_char": 0,
                "end_char": 0,
            })

        return {
            "success": True,
            "data": {
                "filename": file.filename,
                "format": ext,
                "char_count": char_count,
                "truncated": truncated,
                "content": text,
                "chapters": [
                    {"index": c["index"], "title": c["title"], "char_count": c["char_count"],
                     "start_char": c.get("start_char", 0), "end_char": c.get("end_char", 0)}
                    for c in chapters
                ],
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")


@router.post("/detect-chapters")
async def api_detect_chapters(body: dict):
    """从纯文本检测章节（用于手动粘贴场景）"""
    text = body.get("text", "")
    if not text or len(text) < 50:
        raise HTTPException(status_code=400, detail="文本太短，至少 50 字符")
    chapters = detect_chapters(text)
    return {
        "success": True,
        "data": {
            "char_count": len(text),
            "chapters": [
                {"index": c["index"], "title": c["title"], "char_count": c["char_count"],
                 "start_char": c["start_char"], "end_char": c["end_char"]}
                for c in chapters
            ],
        },
    }


@router.post("/generate")
def api_generate_quiz(req: QuizGenerateRequest, db: Session = Depends(get_db)):
    """生成题目（带指纹缓存——相同输入+参数命中则 0 token）"""
    cached = False

    # 1. 指纹查缓存
    fingerprint = hash_source(req.source_content)
    hit = _lookup_cache(
        fingerprint,
        req.question_types,
        req.count,
        req.difficulty,
        req.language,
        db,
    )

    if hit:
        return QuizResponse(
            id=hit["quiz_id"],
            title=hit["title"],
            source_type=hit.get("source_type", req.source_type),
            status="done",
            questions=hit["questions"],
            created_at=hit["created_at"],
            cached=True,
        )

    # 2. 缓存未命中 → LLM 生成
    try:
        title, questions = generate_quiz(
            content=req.source_content,
            question_types=req.question_types,
            count=req.count,
            difficulty=req.difficulty,
            language=req.language,
        )
    except QuizServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")

    # 3. 保存到 quizzes 表
    quiz = Quiz(
        title=title,
        source_type=req.source_type,
        source_content=req.source_content,
        questions_json=json.dumps(questions, ensure_ascii=False),
        status="done",
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    # 4. 保存缓存
    _save_to_cache(
        fingerprint,
        req.source_content,
        req.question_types,
        req.count,
        req.difficulty,
        req.language,
        quiz.id,
        db,
    )

    return QuizResponse(
        id=quiz.id,
        title=title,
        source_type=req.source_type,
        status="done",
        questions=questions,
        created_at=quiz.created_at.isoformat() if quiz.created_at else "",
        cached=cached,
    )


@router.post("/generate-multi")
def api_generate_quiz_multi(req: MultiQuizGenerateRequest, db: Session = Depends(get_db)):
    """多文献综合出题（含跨论文对比题 cross_paper）"""
    # 转 dict
    sources = [s.model_dump() for s in req.sources]

    # 组合指纹（多文献联合哈希）
    fp_parts = [hash_source(s["content"]) for s in sources]
    combined_fp = hashlib.sha256("".join(sorted(fp_parts)).encode()).hexdigest()

    # 查缓存
    hit = _lookup_cache(combined_fp, req.question_types, req.count, req.difficulty, req.language, db)
    if hit:
        return QuizResponse(
            id=hit["quiz_id"],
            title=hit["title"],
            source_type=hit.get("source_type", "multi_paper"),
            status="done",
            questions=hit["questions"],
            created_at=hit["created_at"],
            cached=True,
        )

    # 生成
    try:
        title, questions = generate_quiz_multi(
            sources=sources,
            question_types=req.question_types,
            count=req.count,
            difficulty=req.difficulty,
            language=req.language,
        )
    except QuizServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"多文献出题失败: {str(e)}")

    # 组装 source_content
    combined_content = "\n\n===SEPARATOR===\n\n".join(
        f"[{s.get('label', '')}] {s['content'][:3000]}" for s in sources
    )

    quiz = Quiz(
        title=title,
        source_type="multi_paper",
        source_content=combined_content,
        questions_json=json.dumps(questions, ensure_ascii=False),
        status="done",
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    # 保存缓存
    _save_to_cache(combined_fp, combined_content, req.question_types, req.count, req.difficulty, req.language, quiz.id, db)

    return QuizResponse(
        id=quiz.id,
        title=title,
        source_type="multi_paper",
        status="done",
        questions=questions,
        created_at=quiz.created_at.isoformat() if quiz.created_at else "",
        cached=False,
    )


@router.get("/{quiz_id}", response_model=QuizResponse)
def get_quiz(quiz_id: str, include_answers: bool = False, db: Session = Depends(get_db)):
    """获取题目（可选择是否包含答案）"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="题目不存在")

    questions = json.loads(quiz.questions_json) if quiz.questions_json else []

    if not include_answers:
        questions = [
            {k: v for k, v in q.items() if k not in ("answer", "explanation")}
            for q in questions
        ]

    return QuizResponse(
        id=quiz.id,
        title=quiz.title,
        source_type=quiz.source_type,
        status=quiz.status,
        questions=questions,
        created_at=quiz.created_at.isoformat() if quiz.created_at else "",
    )


@router.get("/", response_model=list[QuizResponse])
def list_quizzes(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """题目列表"""
    quizzes = (
        db.query(Quiz)
        .order_by(Quiz.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        QuizResponse(
            id=q.id,
            title=q.title,
            source_type=q.source_type,
            status=q.status,
            questions=[],
            created_at=q.created_at.isoformat() if q.created_at else "",
        )
        for q in quizzes
    ]


@router.post("/submit", response_model=SubmissionResponse)
def submit_answers(req: SubmitAnswerRequest, db: Session = Depends(get_db)):
    """提交答案 → 批改"""
    quiz = db.query(Quiz).filter(Quiz.id == req.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="题目不存在")

    questions = json.loads(quiz.questions_json) if quiz.questions_json else []
    if not questions:
        raise HTTPException(status_code=400, detail="题目为空")

    try:
        score, correct, total, feedback = grade_submission(questions, req.answers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批改失败: {str(e)}")

    # 保存提交记录
    sub = QuizSubmission(
        quiz_id=req.quiz_id,
        answers_json=json.dumps(req.answers, ensure_ascii=False),
        score=score,
        total=total,
        feedback_json=json.dumps(feedback, ensure_ascii=False),
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    # 错题入库
    wrong_count = 0
    for f in feedback:
        if not f.get("is_correct"):
            wrong = WrongBookItem(
                submission_id=sub.id,
                question_text=f.get("question", ""),
                user_answer=f.get("user_answer", ""),
                correct_answer=f.get("correct_answer", ""),
                knowledge_point=f.get("knowledge_point", ""),
            )
            db.add(wrong)
            wrong_count += 1
    db.commit()

    return SubmissionResponse(
        id=sub.id,
        quiz_id=req.quiz_id,
        score=score,
        total=total,
        pct=round(score / 100, 4) if total > 0 else 0,
        feedback=feedback,
        wrong_count=wrong_count,
        created_at=sub.created_at.isoformat() if sub.created_at else "",
    )


@router.get("/history/{quiz_id}", response_model=list[SubmissionResponse])
def quiz_history(quiz_id: str, db: Session = Depends(get_db)):
    """某套题的历史提交记录"""
    subs = (
        db.query(QuizSubmission)
        .filter(QuizSubmission.quiz_id == quiz_id)
        .order_by(QuizSubmission.created_at.desc())
        .all()
    )
    results = []
    for sub in subs:
        feedback = json.loads(sub.feedback_json) if sub.feedback_json else []
        wrong_count = sum(1 for f in feedback if not f.get("is_correct"))
        results.append(
            SubmissionResponse(
                id=sub.id,
                quiz_id=sub.quiz_id,
                score=sub.score,
                total=sub.total,
                pct=round(sub.score / 100, 4) if sub.total > 0 else 0,
                feedback=feedback,
                wrong_count=wrong_count,
                created_at=sub.created_at.isoformat() if sub.created_at else "",
            )
        )
    return results
