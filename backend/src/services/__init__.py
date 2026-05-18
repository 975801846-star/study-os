"""
Quiz Service — AI 出题 + 批改引擎

DeepSeek V4 驱动：Pro 负责出题/批改，Flash 负责题型分类/格式校验
"""
import json
import uuid

from openai import OpenAI

from ..config import settings

client = OpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url=settings.DEEPSEEK_BASE_URL)


def _call_llm(prompt: str, use_pro: bool = True, temperature: float = 0.3) -> str:
    """调用 DeepSeek，自动选模型"""
    model = settings.DEEPSEEK_MODEL_PRO if use_pro else settings.DEEPSEEK_MODEL_FLASH
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=4096,
    )
    return resp.choices[0].message.content.strip() if resp.choices[0].message.content else ""


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
{content[:8000]}
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
        # Retry with flash for format fix
        fix_prompt = f"以下文本应该是一个 JSON 数组。请修复格式问题，只输出合法的 JSON 数组：\n{raw[:3000]}"
        fixed = _call_llm(fix_prompt, use_pro=False, temperature=0)
        fixed = fixed.strip().lstrip("```json").rstrip("```").strip()
        questions = json.loads(fixed)

    # Ensure unique IDs
    for i, q in enumerate(questions):
        if "id" not in q:
            q["id"] = f"q{i+1}"

    # Get title
    title_prompt = f"为以下材料出的题目集起一个简短标题（10字以内，纯文本无标点）：\n{content[:500]}"
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
    # Build grading context
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
        fix_prompt = f"修复以下 JSON：\n{raw[:3000]}"
        fixed = _call_llm(fix_prompt, use_pro=False, temperature=0)
        fixed = fixed.strip().lstrip("```json").rstrip("```").strip()
        feedback = json.loads(fixed)

    total = len(feedback)
    correct = sum(1 for f in feedback if f.get("is_correct"))
    score = round(correct / total * 100, 1) if total > 0 else 0

    return score, correct, total, feedback
