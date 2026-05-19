"""
Quiz Service — AI 出题 + 批改引擎

DeepSeek V4 驱动：Pro 负责出题/批改，Flash 负责题型分类/格式校验
"""
import json
import logging
import traceback

from openai import OpenAI

from ..config import settings

logger = logging.getLogger("studyos.quiz")

client = OpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url=settings.DEEPSEEK_BASE_URL)


class QuizServiceError(Exception):
    """可安全返回给前端的错误"""
    pass


def _call_llm(prompt: str, use_pro: bool = True, temperature: float = 0.3) -> str:
    """调用 DeepSeek，自动选模型"""
    model = settings.DEEPSEEK_MODEL_PRO if use_pro else settings.DEEPSEEK_MODEL_FLASH
    logger.info(f"LLM call: model={model}, prompt_len={len(prompt)}")

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=8192,
        )
    except Exception as e:
        msg = str(e)
        logger.error(f"DeepSeek API error: {msg}\n{traceback.format_exc()}")
        # 提取有用信息
        if "Connection" in msg or "connect" in msg.lower():
            raise QuizServiceError(f"无法连接 DeepSeek API，请检查网络/代理设置：{msg[:200]}")
        elif "auth" in msg.lower() or "401" in msg or "403" in msg:
            raise QuizServiceError(f"API Key 认证失败，请检查 .env 中 DEEPSEEK_API_KEY：{msg[:200]}")
        else:
            raise QuizServiceError(f"DeepSeek API 调用失败：{msg[:200]}")

    content = resp.choices[0].message.content
    return content.strip() if content else ""


SYSTEM_GENERATE = """你是一位大学课程助教，擅长根据学习材料生成高质量的测验题目。

## 规则
1. 严格按用户指定的题型和数量生成题目
2. 选择题必须有 4 个选项（A/B/C/D），只有一个正确答案
3. 判断题答案只能是"对"或"错"
4. 简答题答案 50-150 字，给出要点
5. 每道题标注对应的知识点（knowledge_point）
6. 输出**纯 JSON 数组**，不要 markdown 代码块，不要额外说明

## JSON 格式
[
  {
    "id": "q1",
    "type": "choice",
    "question": "题目文本",
    "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
    "answer": "A",
    "explanation": "解析",
    "knowledge_point": "知识点名称"
  }
]

判断题示例：
{
  "id": "q2",
  "type": "tf",
  "question": "判断对错：...",
  "answer": "对",
  "explanation": "解析",
  "knowledge_point": "知识点名称"
}

简答题示例：
{
  "id": "q3",
  "type": "short_answer",
  "question": "请简述...",
  "answer": "参考答案要点",
  "explanation": "解析",
  "knowledge_point": "知识点名称"
}"""


def generate_quiz(
    content: str,
    question_types: list[str],
    count: int = 5,
    difficulty: str = "basic",
    language: str = "zh",
) -> tuple[str, list[dict]]:
    """
    生成题目

    Returns:
        (title, questions_list)
    """
    type_map = {
        "choice": "选择题",
        "tf": "判断题",
        "short_answer": "简答题",
        "case_study": "案例分析题",
    }
    diff_map = {"basic": "基础概念", "advanced": "进阶应用", "comprehensive": "综合分析"}
    lang_map = {"zh": "中文", "en": "英文"}

    types_str = "、".join(type_map.get(t, t) for t in question_types)

    user_prompt = f"""请根据以下材料生成 {count} 道题目：

## 要求
- 题型：{types_str}
- 难度：{diff_map.get(difficulty, difficulty)}
- 语言：{lang_map.get(language, language)}
- 直接输出 JSON 数组

## 材料
{content[:32000]}
"""
    raw = _call_llm(SYSTEM_GENERATE + "\n\n" + user_prompt, use_pro=True)

    # Clean possible markdown wrapper
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1])

    try:
        questions = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning(f"JSON parse failed, raw response preview: {raw[:500]}")
        try:
            # Retry with flash for format fix
            fix_prompt = f"以下文本应该是一个 JSON 数组。请修复格式问题，只输出合法的 JSON 数组：\n{raw[:3000]}"
            fixed = _call_llm(fix_prompt, use_pro=False, temperature=0)
            fixed = fixed.strip().lstrip("```json").rstrip("```").strip()
            questions = json.loads(fixed)
        except Exception as e:
            raise QuizServiceError(f"题目解析失败，AI 返回格式异常：{str(e)[:200]}")

    # Ensure unique IDs
    for i, q in enumerate(questions):
        if "id" not in q:
            q["id"] = f"q{i+1}"

    # Get title
    title_prompt = f"为以下材料出的题目集起一个简短标题（10字以内，纯文本无标点）：\n{content[:2000]}"
    title = _call_llm(title_prompt, use_pro=False, temperature=0.7).strip().strip('"').strip("《》")

    return title or "知识测验", questions


SYSTEM_GRADE = """你是一位严格的大学课程助教，负责批改学生答案。

## 规则
1. 逐题比对用户答案和正确答案
2. 选择题：选对即正确（不区分大小写，trim 后比较）
3. 判断题：宽松比对（"对/是/正确/True/true/T" 都算对）
4. 简答题：语义比对，核心要点覆盖即正确，不必逐字相同
5. 每题给出 is_correct (true/false) 和简短 explanation
6. 输出**纯 JSON 数组**，不要额外内容

## JSON 格式
[
  {
    "question_id": "q1",
    "question": "原题",
    "user_answer": "A",
    "correct_answer": "A",
    "is_correct": true,
    "explanation": "正确，...",
    "knowledge_point": "知识点"
  }
]"""


def grade_submission(
    questions: list[dict],
    answers: dict[str, str],
) -> tuple[float, int, int, list[dict]]:
    """
    批改答案

    Returns:
        (score, correct_count, total, feedback_list)
    """
    q_text = json.dumps(questions, ensure_ascii=False, indent=2)
    a_text = json.dumps(answers, ensure_ascii=False, indent=2)

    prompt = f"""## 题目
{q_text[:6000]}

## 用户答案
{a_text[:2000]}

请逐题批改，输出 JSON 数组。"""
    raw = _call_llm(SYSTEM_GRADE + "\n\n" + prompt, use_pro=True)
    raw = raw.strip().lstrip("```json").rstrip("```").strip()

    try:
        feedback = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning(f"Grade JSON parse failed, raw: {raw[:500]}")
        try:
            fix_prompt = f"修复以下 JSON：\n{raw[:3000]}"
            fixed = _call_llm(fix_prompt, use_pro=False, temperature=0)
            fixed = fixed.strip().lstrip("```json").rstrip("```").strip()
            feedback = json.loads(fixed)
        except Exception as e:
            raise QuizServiceError(f"批改结果解析失败：{str(e)[:200]}")

    total = len(feedback)
    correct = sum(1 for f in feedback if f.get("is_correct"))
    score = round(correct / total * 100, 1) if total > 0 else 0

    return score, correct, total, feedback


def test_connection() -> dict:
    """测试 DeepSeek API 连接"""
    model = settings.DEEPSEEK_MODEL_FLASH
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "回复OK"}],
            max_tokens=10,
        )
        return {
            "ok": True,
            "model": model,
            "base_url": settings.DEEPSEEK_BASE_URL,
            "key_prefix": settings.DEEPSEEK_API_KEY[:10] + "..." if settings.DEEPSEEK_API_KEY else "(空)",
            "response": resp.choices[0].message.content,
        }
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return {
            "ok": False,
            "error": str(e),
            "model": model,
            "base_url": settings.DEEPSEEK_BASE_URL,
            "key_prefix": settings.DEEPSEEK_API_KEY[:10] + "..." if settings.DEEPSEEK_API_KEY else "(空)",
        }


# ─── 章节检测 ───

def detect_chapters(text: str) -> list[dict]:
    """
    检测文档中的章节，返回 [{index, title, content, char_count}]
    支持：中文第X章/X节、英文 Chapter X、Markdown 标题、IMRaD 论文结构
    未检测到章节时返回单元素列表
    """
    import re

    patterns: list[tuple[str, int]] = [
        # P0: 中文第X章/第X节（最高优先级）
        (r'(?:^|\n)\s*(第[一二三四五六七八九十百千\d]+[章节])\s*[　\s]*.*?(?=\n|$)', 1),
        # P1: 英文 Chapter X
        (r'(?:^|\n)\s*(Chapter\s+\d+[\s:\.\-]*.*?)(?=\n|$)', 1),
        # P2: Markdown 标题 # ## ###
        (r'(?:^|\n)\s*(#{1,3}\s+[^\n]+)', 1),
        # P3: 学术论文章节
        (r'(?:^|\n)\s*(Abstract|Introduction|Methods?|Results?|Discussion|Conclusion|References?|Acknowledgments?|附录[\s\d]*|摘要|引言|方法|结果|讨论|结论|参考文献|致谢)[\s:]*', 1),
    ]

    chapters = []
    matched_starts: set[int] = set()

    for pattern, _ in patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
            pos = m.start()
            # 去重：同位置不同 pattern 只取第一个
            if any(abs(pos - ms) < 10 for ms in matched_starts):
                continue
            matched_starts.add(pos)
            chapters.append({
                "pos": pos,
                "title": m.group(0).strip()[:80],
            })

    chapters.sort(key=lambda c: c["pos"])

    # 无章节则整篇为一个
    if not chapters:
        return [{
            "index": 0,
            "title": "全文",
            "content": text,
            "char_count": len(text),
        }]

    # 根据位置切分内容
    result = []
    n = len(chapters)
    for i, ch in enumerate(chapters):
        start = ch["pos"]
        end = chapters[i + 1]["pos"] if i + 1 < n else len(text)
        content = text[start:end].strip()
        if len(content) < 20:
            continue  # 跳过太短的
        result.append({
            "index": len(result),
            "title": ch["title"],
            "content": content,
            "char_count": len(content),
            "start_char": start,
            "end_char": end,
        })

    # 如果第一个章节前有内容，作为「前言/目录」
    first_pos = chapters[0]["pos"]
    if first_pos > 50:
        preamble = text[:first_pos].strip()
        if len(preamble) > 50:
            result.insert(0, {
                "index": 0,
                "title": "前言/摘要",
                "content": preamble,
                "char_count": len(preamble),
                "start_char": 0,
                "end_char": first_pos,
            })
            # 重新编号
            for i, r in enumerate(result):
                r["index"] = i

    return result if result else [{
        "index": 0,
        "title": "全文",
        "content": text,
        "char_count": len(text),
        "start_char": 0,
        "end_char": len(text),
    }]
