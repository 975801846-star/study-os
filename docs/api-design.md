# API 接口设计

> 详细接口规范，Phase 1-5 逐步补充

## 通用规范

- 基础路径：`/api`
- 请求格式：JSON (GET 参数除外)
- 响应格式：
  ```json
  {
    "success": true,
    "data": {},
    "error": null
  }
  ```
- 文件上传：`multipart/form-data`
- 异步任务：返回 `task_id`，轮询 `/status` 获取进度

## 教材管理

### POST /api/textbooks/upload

上传教材 PDF。

**请求**：`multipart/form-data`
| 字段 | 类型 | 说明 |
|------|------|------|
| file | File | PDF 文件 (≤200MB) |
| course_name | str | 课程名称 |
| semester | str | 学期 (可选) |

**响应**：
```json
{
  "success": true,
  "data": {
    "textbook_id": "uuid",
    "title": "Sport Analytics",
    "status": "processing",
    "task_id": "uuid"
  }
}
```

### GET /api/textbooks

教材列表。

### GET /api/textbooks/:id

教材详情，含章节结构。

### GET /api/textbooks/:id/chapters

章节列表。

---

## 课堂录音

### POST /api/lectures/upload

上传课堂录音。

**请求**：`multipart/form-data`
| 字段 | 类型 | 说明 |
|------|------|------|
| file | File | 音频 (mp3/m4a/wav, ≤500MB) |
| course_id | str | 关联课程 |
| lecture_date | str | 上课日期 (YYYY-MM-DD) |

**响应**：
```json
{
  "success": true,
  "data": {
    "lecture_id": "uuid",
    "status": "transcribing",
    "task_id": "uuid"
  }
}
```

### GET /api/lectures/:id

课堂详情：转写结果 + LLM 摘要 + 重点标注 + 教材对齐。

### GET /api/lectures/:id/status

转写/分析任务进度。

```json
{
  "success": true,
  "data": {
    "task_id": "uuid",
    "status": "transcribing|summarizing|aligning|done",
    "progress": 0.75,
    "message": "正在转写..."
  }
}
```

---

## 题目

### POST /api/quizzes/generate

基于知识库出题。

**请求**：
```json
{
  "source_type": "textbook|lecture|both",
  "source_ids": ["uuid"],
  "question_types": ["choice", "tf", "short_answer", "case_study"],
  "count": 20,
  "difficulty": "basic|advanced|comprehensive"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "quiz_id": "uuid",
    "status": "generating",
    "task_id": "uuid"
  }
}
```

### GET /api/quizzes/:id

题目详情（不包含答案）。

### POST /api/quizzes/:id/submit

提交答案。

**请求**：
```json
{
  "answers": {
    "q1": "A",
    "q2": "True",
    "q3": "限制导向方法强调..."
  }
}
```

### GET /api/quizzes/:id/review

查看批改结果。

---

## 搜索

### GET /api/search

全文 + 语义搜索。

**参数**：
| 参数 | 类型 | 说明 |
|------|------|------|
| q | str | 搜索关键词 |
| course_id | str | 限定课程 (可选) |
| type | str | textbook|lecture|all (默认 all) |
| limit | int | 返回数量 (默认 10) |

---

## 导出

### POST /api/export/study-guide

生成复习资料。

**请求**：
```json
{
  "course_id": "uuid",
  "format": "pdf|epub|markdown",
  "sections": ["key_points", "notes", "wrong_questions", "practice"],
  "date_range": {"start": "2026-09-01", "end": "2026-12-31"}
}
```

### GET /api/export/:task_id/download

下载导出文件。
