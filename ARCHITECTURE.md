# StudyOS — 技术架构文档

## 架构决策记录 (ADR)

### ADR-001: 单体 API + 嵌入式向量数据库

**决策**：使用单体 FastAPI 后端 + ChromaDB 嵌入式向量数据库，而非微服务架构。

**理由**：
- 单用户场景，无需水平扩展
- 降低运维复杂度（一个进程启动全部服务）
- ChromaDB 嵌入式模式零运维，不需要独立部署
- 未来如果需要扩展，可以拆分为独立服务

**替代方案**：微服务（Kubernetes）、独立 Qdrant/Milvus 服务 —— 过度设计

---

### ADR-002: SQLite + ChromaDB 双存储

**决策**：SQLite 存储结构化业务数据 + ChromaDB 存储向量/语义数据。

**理由**：
- SQLite 零配置、单文件备份、足够支撑单用户
- ChromaDB 专为向量检索优化，SQLite 不适合
- 两者互补，互不干扰
- 迁移到 PostgreSQL 成本低（SQLAlchemy 抽象）

---

### ADR-003: DeepSeek 作为主 LLM

**决策**：优先使用 DeepSeek API 作为唯一 LLM。

**理由**：
- DeepSeek 中文能力优秀（教材标注、题目解析）
- 价格极低（¥1/百万 token），大量出题成本可控
- API 兼容 OpenAI 格式，切换成本低
- 用户在中国，访问 DeepSeek 延迟更低

---

### ADR-004: 异步任务队列

**决策**：使用 FastAPI BackgroundTasks + 轮询状态，不引入 Celery/Redis。

**理由**：
- PDF 解析、Whisper 转写、批量出题是耗时操作
- v1 阶段任务量少，Celery+Redis 是过度设计
- FastAPI BackgroundTasks 足够处理单用户场景
- 未来可平滑迁移到 Celery

---

## 目录结构

```
study-os/
├── README.md
├── PROJECT_PLAN.md               # 开发路线图
├── ARCHITECTURE.md               # 本文档
├── Makefile                      # 常用命令快捷方式
├── docker-compose.yml
├── .gitignore
├── .env.example
│
├── backend/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI 入口
│   │   ├── config.py             # 配置管理 (pydantic-settings)
│   │   ├── database.py           # SQLite + ChromaDB 连接
│   │   │
│   │   ├── api/                  # 路由层
│   │   │   ├── __init__.py
│   │   │   ├── textbooks.py      # POST/GET /api/textbooks
│   │   │   ├── lectures.py       # POST/GET /api/lectures
│   │   │   ├── quizzes.py        # POST/GET /api/quizzes
│   │   │   ├── search.py         # GET /api/search
│   │   │   ├── wrong_book.py     # GET/POST /api/wrong-book
│   │   │   ├── dashboard.py      # GET /api/dashboard
│   │   │   └── export.py         # POST/GET /api/export
│   │   │
│   │   ├── services/             # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── pdf_parser.py     # PDF → Markdown 解析
│   │   │   ├── chunker.py        # 文本分块策略
│   │   │   ├── embedder.py       # 文本向量化
│   │   │   ├── transcriber.py    # Whisper 语音转写
│   │   │   ├── summarizer.py     # LLM 摘要服务
│   │   │   ├── quiz_generator.py # 出题引擎
│   │   │   ├── grader.py         # 批改引擎
│   │   │   ├── aligner.py        # 课堂-教材对齐
│   │   │   ├── rag.py            # RAG 检索
│   │   │   └── exporter.py       # 导出服务
│   │   │
│   │   ├── models/               # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── course.py
│   │   │   ├── textbook.py
│   │   │   ├── lecture.py
│   │   │   ├── quiz.py
│   │   │   └── wrong_book.py
│   │   │
│   │   ├── schemas/              # Pydantic 请求/响应模型
│   │   │   ├── __init__.py
│   │   │   ├── textbook.py
│   │   │   ├── lecture.py
│   │   │   ├── quiz.py
│   │   │   └── dashboard.py
│   │   │
│   │   └── utils/                # 工具函数
│   │       ├── __init__.py
│   │       ├── file.py           # 文件处理
│   │       └── prompts.py        # LLM Prompt 模板
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_pdf_parser.py
│       ├── test_chunker.py
│       ├── test_quiz_generator.py
│       └── test_grader.py
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── components.json           # shadcn/ui 配置
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx          # 首页/仪表盘
│   │   │   ├── textbooks/
│   │   │   │   ├── page.tsx      # 教材列表
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx  # 教材详情/阅读
│   │   │   ├── lectures/
│   │   │   │   ├── page.tsx      # 课堂列表
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx  # 课堂详情/播放
│   │   │   ├── quizzes/
│   │   │   │   ├── page.tsx      # 题目列表
│   │   │   │   ├── [id]/
│   │   │   │   │   ├── page.tsx  # 做题页
│   │   │   │   │   └── review/   # 批改结果
│   │   │   │   └── generate/     # 出题配置页
│   │   │   ├── wrong-book/
│   │   │   │   └── page.tsx
│   │   │   ├── search/
│   │   │   │   └── page.tsx
│   │   │   └── settings/
│   │   │       └── page.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── ui/               # shadcn/ui 基础组件
│   │   │   ├── textbook/
│   │   │   │   ├── TextbookReader.tsx
│   │   │   │   ├── ChapterTree.tsx
│   │   │   │   └── UploadDialog.tsx
│   │   │   ├── lecture/
│   │   │   │   ├── AudioPlayer.tsx
│   │   │   │   ├── TranscriptView.tsx
│   │   │   │   └── KeyPointBadge.tsx
│   │   │   ├── quiz/
│   │   │   │   ├── QuizCard.tsx
│   │   │   │   ├── ChoiceQuestion.tsx
│   │   │   │   ├── ShortAnswerQuestion.tsx
│   │   │   │   └── QuizResult.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── ProgressChart.tsx
│   │   │   │   └── SubjectRadar.tsx
│   │   │   └── layout/
│   │   │       ├── Sidebar.tsx
│   │   │       └── Header.tsx
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts            # API 客户端
│   │   │   └── utils.ts
│   │   │
│   │   └── store/
│   │       ├── index.ts          # Zustand store
│   │       ├── textbookStore.ts
│   │       └── quizStore.ts
│   │
│   └── public/
│       └── favicon.ico
│
├── scripts/
│   ├── setup.sh                  # 一键初始化
│   └── seed_data.py              # 测试数据填充
│
└── docs/
    ├── api-design.md
    ├── data-model.md
    ├── user-stories.md
    └── prompt-engineering.md     # LLM Prompt 设计与迭代记录
```

---

## 核心技术流程

### 1. 教材导入流程

```
用户上传 PDF
       │
       ▼
┌─────────────────┐
│ 1. 文件校验     │  类型/大小检查
└────────┬────────┘
         ▼
┌─────────────────┐
│ 2. PyMuPDF 提取 │  提取文本 + 章节结构 + 图片引用
└────────┬────────┘
         ▼
┌─────────────────┐
│ 3. Marker 结构化│  公式识别、表格还原、标题层级
└────────┬────────┘
         ▼
┌─────────────────┐
│ 4. 分块         │  按标题/段落分块 (chunk_size=1000, overlap=200)
└────────┬────────┘
         ▼
┌─────────────────┐
│ 5. 向量化       │  Embedding API → ChromaDB
└────────┬────────┘
         ▼
┌─────────────────┐
│ 6. 保存         │  SQLite (元数据) + ChromaDB (向量) + 文件系统 (Markdown)
└─────────────────┘
```

### 2. 课堂录音处理流程

```
用户上传音频
       │
       ▼
┌─────────────────┐
│ 1. 格式转换     │  ffmpeg → 16kHz mono wav (Whisper 最佳格式)
└────────┬────────┘
         ▼
┌─────────────────┐
│ 2. Whisper 转写  │  API 或本地模型，返回文字稿 + 时间戳
└────────┬────────┘
         ▼
┌─────────────────┐
│ 3. LLM 分析     │  DeepSeek:
│                 │  - 分段：按主题切分
│                 │  - 标注：key_point / example / assignment / filler
│                 │  - 提取：专业术语表
│                 │  - 总结：每段一句话摘要
└────────┬────────┘
         ▼
┌─────────────────┐
│ 4. 教材对齐     │  每个 key_point → 向量搜索最相关教材段落
└────────┬────────┘
         ▼
┌─────────────────┐
│ 5. 存储         │  文字稿 + 摘要 + 标签 + 对齐结果
└─────────────────┘
```

### 3. 出题流程

```
用户选择范围（教材/章节/课堂）+ 题型 + 数量 + 难度
       │
       ▼
┌─────────────────┐
│ 1. 知识点检索   │  RAG: 从 ChromaDB 检索相关 Chunk
└────────┬────────┘
         ▼
┌─────────────────┐
│ 2. LLM 生成     │  System Prompt 约束:
│                 │  - JSON Schema 输出
│                 │  - 基于给定知识点
│                 │  - 难度分级规则
│                 │  - 避免重复和歧义
└────────┬────────┘
         ▼
┌─────────────────┐
│ 3. 质量检查     │  - JSON 格式校验
│                 │  - 答案一致性检查（同题答案不矛盾）
│                 │  - 去重（与已有题目向量相似度）
└────────┬────────┘
         ▼
┌─────────────────┐
│ 4. 存储         │  SQLite + 关联知识点
└─────────────────┘
```

### 4. 批改流程

```
用户提交答案
       │
       ▼
┌─────────────────┐
│ 客观题          │  字符串匹配/正则 → 即时结果
│ (选择/判断)     │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 主观题          │  LLM 评分:
│ (简答/案例分析) │  - 对照标准答案
│                 │  - 评分维度：完整性/准确性/深度
│                 │  - 给出改进建议
└────────┬────────┘
         ▼
┌─────────────────┐
│ 错题归因        │  错误题目 → 关联知识点 → 更新薄弱度
└────────┬────────┘
         ▼
┌─────────────────┐
│ 间隔复习计划    │  艾宾浩斯曲线 → 下次复习日期
└─────────────────┘
```

---

## 安全设计

| 层级 | 措施 |
|------|------|
| API Key | .env 文件存储，不提交 Git，后端启动时加载 |
| 文件上传 | 类型白名单、大小限制（PDF≤200MB, 音频≤500MB）、病毒扫描 |
| 路径遍历 | 文件路径 Canonicalize，拒绝 ../ |
| CORS | 仅允许前端域名 |
| 速率限制 | 单 IP 每分钟 60 请求（防止 API 费用失控） |
| 数据隔离 | v1 单用户跳过多租户，v2 加 JWT |

---

_最后更新：2026-05-17_
