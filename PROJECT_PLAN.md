# StudyOS — 个人学习操作系统 · 开发路线图

> **目标**：为留学生打造一个集「教材预习 + 课堂录音转写 + 重点提炼 + AI 出题 + 做题复习 + 导出教材」于一体的全栈学习工具。
>
> **用户**：安同学 | 拉夫堡大学 Sport Analytics & AI (2026.09 入学)
>
> **仓库**：`github.com/975801846-star/study-os`

---

## 一、产品概览

### 核心功能

| # | 功能 | 描述 |
|---|------|------|
| 1 | 📖 教材导入 | 上传 PDF/EPUB → 自动解析为结构化 Markdown → 存入知识库 |
| 2 | 🎙 课堂录音 | 上传 mp3/m4a/wav → Whisper 转写 → LLM 标注重点/例子/废话 |
| 3 | 🔗 知识对齐 | 课堂内容自动关联到教材对应章节 |
| 4 | 🧠 智能出题 | 基于「教材 + 课堂重点」生成选择/简答/案例分析题 |
| 5 | ✍️ 在线做题 | 答题 → 自动批改 → 错题归因到知识点 |
| 6 | 📊 学习仪表盘 | 各科进度、掌握度、错题分布可视化 |
| 7 | 📤 导出教材 | 一键拼装「教材要点 + 课堂笔记 + 错题集」→ PDF/EPUB |
| 8 | 🔍 全文检索 | 跨教材、笔记、论文的语义搜索 |

### 用户故事

```
作为一个即将入学的留学生，我希望：
- 拿到课程教材后，能提前预习并生成自测题
- 课堂上录音，课后自动获得带重点标注的文字稿
- 系统根据老师讲的重点和教材内容，自动出作业题和模拟考题
- 做题后能看到薄弱知识点，针对性复习
- 期末能把所有内容导出为一份复习教材
```

---

## 二、技术架构

```
┌─────────────────────────────────────────────────────┐
│                   前端 (Next.js 14)                   │
│  App Router · Tailwind CSS · shadcn/ui · Zustand    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│  │ 📖 教材页 │ │ 🎙 录音页 │ │ ✍️ 做题页 │             │
│  │ 🔍 搜索页 │ │ 📊 仪表盘 │ │ ⚙️ 设置页 │             │
│  └──────────┘ └──────────┘ └──────────┘             │
└──────────────────────┬──────────────────────────────┘
                       │ REST + WebSocket
┌──────────────────────▼──────────────────────────────┐
│                后端 (Python FastAPI)                  │
│                                                      │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │ PDF 解析服务 │  │ 语音转写服务  │  │ LLM 服务   │  │
│  │ PyMuPDF     │  │ Whisper API  │  │ DeepSeek   │  │
│  │ Marker      │  │ / local      │  │ Claude     │  │
│  └─────────────┘  └──────────────┘  └────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │              RAG 检索增强生成                   │   │
│  │  LangChain · ChromaDB · 分块策略 · 重排序      │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐   │
│  │ 出题引擎   │  │ 批改引擎   │  │ 导出服务     │   │
│  │ 题型模板   │  │ 评分逻辑   │  │ Pandoc       │   │
│  │ 难度控制   │  │ 错题归因   │  │ WeasyPrint   │   │
│  └────────────┘  └────────────┘  └──────────────┘   │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                   数据层                              │
│  ┌──────────┐  ┌───────────┐  ┌────────────────┐   │
│  │ SQLite   │  │ ChromaDB  │  │ 文件系统       │   │
│  │ 用户数据  │  │ 向量索引   │  │ PDF/音频/导出  │   │
│  │ 做题记录  │  │ 语义搜索   │  │                │   │
│  └──────────┘  └───────────┘  └────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 技术选型理由

| 决策 | 选择 | 理由 |
|------|------|------|
| 前端框架 | Next.js 14 App Router | SSR/SSG 混合、文件路由、Vercel 免费部署 |
| UI 库 | shadcn/ui + Tailwind | 组件可定制、不锁 vendor、暗色模式 |
| 后端框架 | FastAPI | 异步原生、自动 OpenAPI 文档、Python 生态 |
| 向量数据库 | ChromaDB | 轻量、嵌入式、零运维、适合单用户 |
| 主数据库 | SQLite | 零配置、单文件、备份简单 |
| LLM | DeepSeek API | 便宜（¥1/百万 token）、中文优异 |
| 语音转写 | OpenAI Whisper API | 准确率最高、多语言、按量付费 |
| PDF 解析 | PyMuPDF + Marker | 文本提取 + 公式/表格保留 |
| 导出 | Pandoc + WeasyPrint | Markdown→PDF 成熟方案 |
| 认证 | 无（v1 单用户） | YAGNI，先做功能 |

---

## 三、分阶段开发计划

### Phase 0 — 项目初始化（第 1 周）

```
目标：项目骨架、开发环境、CI/CD
```

- [ ] 初始化 monorepo（backend/ + frontend/）
- [ ] Docker Compose 开发环境
- [ ] Backend: FastAPI 项目结构 + 配置管理
- [ ] Frontend: Next.js 项目结构 + shadcn/ui 配置
- [ ] GitHub Actions: lint + type check
- [ ] 开发规范：pre-commit、Black、ESLint

### Phase 1 — 教材导入 + 知识库（第 2-3 周）

```
目标：上传一本教材 → 解析 → 可搜索 → 可浏览
```

- [ ] **PDF 解析服务**：上传 PDF → PyMuPDF 提取文本 → Marker 结构化 → Markdown
- [ ] **分块策略**：按章节/标题分块，保留层级关系
- [ ] **向量化**：text-embedding-3-small → ChromaDB 存储
- [ ] **前端教材页**：左侧目录树 + 右侧正文渲染
- [ ] **全文搜索**：关键词 + 语义混合搜索

**里程碑**：上传一本运动科学教材，能在网页上浏览和搜索

### Phase 2 — 语音转写 + 课堂分析（第 4-5 周）

```
目标：上传课堂录音 → 文字稿 → 重点标注 → 对齐教材
```

- [ ] **音频上传**：前端录音/上传，支持 mp3/m4a/wav
- [ ] **Whisper 集成**：异步转写任务，进度回调
- [ ] **LLM 摘要**：转写结果 → DeepSeek 提炼重点/例子/作业要求
- [ ] **知识点对齐**：课堂内容 → 向量搜索匹配教材章节
- [ ] **前端课堂页**：音频播放器 + 同步高亮文字稿 + 重点标签

**里程碑**：上传一节课堂录音，获得带标注的文字稿并关联到教材

### Phase 3 — AI 出题 + 做题系统（第 6-8 周）

```
目标：基于知识库出题 → 在线做题 → 自动批改 → 错题本
```

- [ ] **出题引擎**：RAG 检索相关知识点 → LLM 生成题目
  - 题型：选择题、判断题、简答题、案例分析题
  - 难度控制：基础/进阶/综合
  - 输出格式：JSON Schema 约束
- [ ] **做题界面**：题目渲染、计时器、进度条
- [ ] **自动批改**：客观题即时判断 + 主观题 LLM 评分
- [ ] **错题本**：错题归因到知识点 → 薄弱点分析
- [ ] **间隔复习**：基于艾宾浩斯曲线的复习提醒

**里程碑**：能根据教材出 20 道题，在线做完并看到错题分析

### Phase 4 — 学习仪表盘 + 导出（第 9-10 周）

```
目标：可视化学习数据 + 一键导出复习资料
```

- [ ] **仪表盘**：各科进度、掌握度雷达图、学习时长统计
- [ ] **导出服务**：选择内容范围 → Markdown 拼装 → PDF/EPUB
- [ ] **模板系统**：期末复习模板、章节总结模板、错题合集模板
- [ ] **数据导入导出**：JSON 格式备份/迁移

**里程碑**：期末一键导出 A4 格式的复习教材 PDF

### Phase 5 — 打磨 + 部署（第 11-12 周）

```
目标：生产可用 + 文档完善
```

- [ ] 性能优化：大文件分片上传、懒加载、缓存
- [ ] 错误处理：全局异常处理、友好提示
- [ ] 响应式适配：手机/平板可访问
- [ ] 部署文档：Vercel（前端）+ Railway/Render（后端）
- [ ] 用户手册：使用教程 + 常见问题

---

## 四、数据模型（核心）

```python
# 课程
class Course:
    id: str
    name: str              # "Sport Analytics"
    semester: str          # "2026-Fall"
    instructor: str

# 教材
class Textbook:
    id: str
    course_id: str
    title: str
    file_path: str          # 原始 PDF 路径
    chapters: List[Chapter]

class Chapter:
    id: str
    textbook_id: str
    number: int
    title: str
    chunks: List[Chunk]     # 向量分块

class Chunk:
    id: str
    chapter_id: str
    content: str
    embedding_id: str       # ChromaDB 引用
    chunk_index: int

# 课堂记录
class Lecture:
    id: str
    course_id: str
    date: datetime
    audio_path: str
    transcript: str          # 原始转写
    summary: str             # LLM 摘要
    key_points: List[KeyPoint]
    aligned_chapters: List[str]  # 关联教材章节

class KeyPoint:
    text: str
    type: str               # key_point | example | assignment | filler
    importance: int          # 1-5
    related_chunk_ids: List[str]

# 题目
class Quiz:
    id: str
    source_ids: List[str]    # 来源 Chunk/Lecture
    questions: List[Question]
    difficulty: str          # basic | advanced | comprehensive

class Question:
    id: str
    type: str               # choice | tf | short_answer | case_study
    stem: str
    options: List[str]       # 选择题选项
    answer: str
    explanation: str
    knowledge_points: List[str]

# 做题记录
class QuizAttempt:
    id: str
    quiz_id: str
    answers: Dict[str, str]
    scores: Dict[str, float]
    completed_at: datetime

class WrongBook:
    user_id: str
    entries: List[WrongEntry]

class WrongEntry:
    question_id: str
    wrong_count: int
    last_wrong_at: datetime
    next_review_at: datetime  # 间隔复习
    mastered: bool
```

---

## 五、API 设计（核心端点）

```
# 教材管理
POST   /api/textbooks/upload          # 上传教材 PDF
GET    /api/textbooks                 # 教材列表
GET    /api/textbooks/:id             # 教材详情
GET    /api/textbooks/:id/chapters    # 章节列表
GET    /api/chapters/:id/chunks       # 章节内容块

# 搜索
GET    /api/search?q=keyword&course=id  # 混合搜索

# 课堂录音
POST   /api/lectures/upload           # 上传录音
GET    /api/lectures/:id              # 课堂详情（含转写+摘要）
GET    /api/lectures/:id/status       # 转写进度
POST   /api/lectures/:id/align        # 对齐教材

# 出题
POST   /api/quizzes/generate          # 基于知识库出题
GET    /api/quizzes/:id               # 题目详情（不包含答案）
POST   /api/quizzes/:id/submit        # 提交答案 → 批改
GET    /api/quizzes/:id/review        # 查看批改结果

# 错题本
GET    /api/wrong-book                # 错题列表
GET    /api/wrong-book/review-due     # 待复习错题
POST   /api/wrong-book/:entry/review  # 标记已复习

# 学习分析
GET    /api/dashboard/overview        # 总览
GET    /api/dashboard/course/:id      # 单科详情

# 导出
POST   /api/export/study-guide        # 生成复习资料
GET    /api/export/:task_id/status    # 导出进度
GET    /api/export/:task_id/download  # 下载导出文件
```

---

## 六、多 Agent 协作策略

### 为什么用多 Agent？

| Agent | 角色 | 擅长 |
|-------|------|------|
| **OpenClaw** | 项目总管 + 知识库专家 | 论文检索、文档管理、cron 任务、跨文件一致性 |
| **Claude Code** | 主力开发 | 代码生成、调试、重构、大型文件操作 |
| **Trea.cn** | 架构审查 + 方案验证 | 多方案对比、技术选型验证、安全性审查 |

### 协作流程

```
1. OpenClaw 写任务 Spec → 推送到 GitHub Issue
2. Claude Code 认领 Issue → 开发 → PR
3. Trea.cn 审查 PR（架构/安全）→ 反馈
4. OpenClaw 合并 + 更新文档 + 更新 MEMORY.md
5. 循环
```

### 交叉查验清单（每个 Phase 完成后）

- [ ] OpenClaw: 检查所有文件是否遵守项目规范（命名、目录结构）
- [ ] OpenClaw: 检查 API 文档与实际实现是否一致
- [ ] Claude Code: 跑测试套件 + lint
- [ ] Trea.cn: 审查代码安全（API key 管理、文件上传安全）
- [ ] Trea.cn: 审查架构是否偏离设计方案
- [ ] 三方交叉验证：向量搜索准确率、出题质量、转写准确性

---

## 七、本地开发环境

### 前置依赖

```bash
# 必须
Python 3.11+    # 后端
Node.js 20+     # 前端
Docker Desktop  # 开发和 ChromaDB

# 推荐
Git             # 版本控制
VS Code         # 编辑器
```

### 一键启动

```bash
# 克隆
git clone git@github.com:975801846-star/study-os.git
cd study-os

# 启动全部服务
docker compose up -d

# 或分别启动
cd backend && python -m uvicorn src.main:app --reload
cd frontend && npm run dev
```

### 环境变量（.env）

```bash
# LLM
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 语音转写
OPENAI_API_KEY=sk-xxx  # Whisper API
# 或本地 Whisper
WHISPER_MODEL=medium    # tiny/base/small/medium/large

# 向量化
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_API_KEY=sk-xxx

# 数据库
CHROMA_PERSIST_DIR=./data/chroma
SQLITE_PATH=./data/studyos.db

# 文件存储
UPLOAD_DIR=./data/uploads
EXPORT_DIR=./data/exports
```

---

## 八、风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| Whisper 转写英文体育术语不准 | 高 | 允许手动修正 + 术语表增强 |
| LLM 出题质量不稳定 | 中 | 题型模板约束 + 人工抽查 + prompt 迭代 |
| 教材 PDF 排版复杂解析失败 | 中 | 多解析器后备（PyMuPDF → Marker → 手动） |
| 留学后没时间继续开发 | 高 | Phase 1-2 必须在入学前完成核心功能 |
| API 费用超预期 | 低 | DeepSeek 极便宜，Whisper 按需使用 |

---

## 九、成本估算（月）

| 服务 | 用量估算 | 月费 |
|------|----------|------|
| DeepSeek API | 出题+摘要，约 1M token/月 | ¥1-2 |
| OpenAI Whisper | 每周 3 节课 × 2h = 6h 音频/月 | ¥20-30 |
| Embedding API | 教材向量化，一次性约 ¥5 | ¥5 |
| Vercel (前端) | 静态部署 | 免费 |
| Railway/Render (后端) | 512MB RAM | 免费额度 / $5 |
| **合计** | | **≈ ¥30-50/月** |

---

## 十、成功标准

- [ ] 上传一本 200 页教材，5 分钟内完成解析和向量化
- [ ] 上传 2 小时课堂录音，10 分钟内完成转写和摘要
- [ ] 基于教材生成 20 道题，80% 无需人工修改
- [ ] 做题批改准确率 > 95%（客观题）
- [ ] 导出 PDF 格式正确，A4 可打印
- [ ] 前端在手机/iPad 上可正常使用

---

_最后更新：2026-05-17 | 版本 v1.0_
