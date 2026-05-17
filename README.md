# StudyOS 🎓

> 个人学习操作系统 — 为留学生打造的 AI 驱动的学习助手

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)

## 是什么

StudyOS 是一个全栈 Web 应用，帮助留学生：

- 📖 **导入教材** — 上传 PDF，自动解析为结构化知识库
- 🎙 **课堂录音分析** — 上传录音 → Whisper 转文字 → LLM 提炼重点、标注废话
- 🧠 **AI 出题** — 基于教材和课堂重点，自动生成选择题、简答题、案例分析题
- ✍️ **在线做题** — 答题 → 自动批改 → 错题归因到知识点 → 间隔复习
- 📊 **学习仪表盘** — 各科进度、掌握度雷达图
- 📤 **导出教材** — 一键拼装教材要点 + 课堂笔记 + 错题集 → PDF

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Next.js 14 · Tailwind CSS · shadcn/ui · Zustand |
| 后端 | Python FastAPI · LangChain · ChromaDB |
| AI | DeepSeek (LLM) · OpenAI Whisper (STT) · text-embedding-3-small |
| 存储 | SQLite · ChromaDB · 文件系统 |
| 导出 | Pandoc · WeasyPrint |

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 20+
- Docker Desktop（可选，用 Docker Compose 一键启动）

### 安装

```bash
git clone git@github.com:975801846-star/study-os.git
cd study-os

# 一键初始化
bash scripts/setup.sh

# 或手动
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

### 配置

```bash
cp .env.example .env
# 编辑 .env，填入 API Key
```

### 启动

```bash
# Docker Compose（推荐）
docker compose up -d

# 或分别启动
cd backend && uvicorn src.main:app --reload --port 8000
cd frontend && npm run dev --port 3000
```

打开 http://localhost:3000

## 项目文档

- [开发路线图](PROJECT_PLAN.md) — 分阶段计划、里程碑、成本估算
- [技术架构](ARCHITECTURE.md) — 架构决策、目录结构、核心流程
- [API 设计](docs/api-design.md) — 接口规范
- [数据模型](docs/data-model.md) — 数据库设计
- [用户故事](docs/user-stories.md) — 使用场景
- [Prompt 工程](docs/prompt-engineering.md) — LLM Prompt 设计与迭代

## 多 Agent 协作

本项目由多 AI Agent 协作开发：

- **OpenClaw** 🦞 — 项目总管，文档维护，交叉审查
- **Claude Code** — 主力开发，代码生成与调试
- **Trea.cn** — 架构审查，技术方案验证

详见 [PROJECT_PLAN.md § 六](PROJECT_PLAN.md#六多-agent-协作策略)

## License

MIT © 2026 安同学
