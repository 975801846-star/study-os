import {
  BookOpen,
  Mic,
  BrainCircuit,
  PenLine,
  BarChart3,
  Search,
  FileDown,
  ChevronRight,
  Sparkles,
  Zap,
  Shield,
  Cpu,
} from "lucide-react";

const features = [
  {
    icon: BookOpen,
    title: "教材导入",
    desc: "上传 PDF · 自动结构化解析 · 章节导航 · 全文搜索",
    status: "v1",
    gradient: "from-emerald-500/20 to-teal-500/10 via-emerald-500/5",
    iconBg: "bg-emerald-500/10 text-emerald-400",
  },
  {
    icon: Mic,
    title: "课堂录音",
    desc: "上传音频 → 本地 Whisper 转写 → AI 标注重点与待复习",
    status: "v1",
    gradient: "from-violet-500/20 to-purple-500/10 via-violet-500/5",
    iconBg: "bg-violet-500/10 text-violet-400",
  },
  {
    icon: BrainCircuit,
    title: "AI 出题",
    desc: "基于知识库生成选择/简答/案例分析 · 难度可控",
    status: "v1",
    gradient: "from-amber-500/20 to-orange-500/10 via-amber-500/5",
    iconBg: "bg-amber-500/10 text-amber-400",
  },
  {
    icon: PenLine,
    title: "在线做题",
    desc: "答题 → 自动批改 → 错题归因到知识点 → 间隔复习",
    status: "v1",
    gradient: "from-rose-500/20 to-pink-500/10 via-rose-500/5",
    iconBg: "bg-rose-500/10 text-rose-400",
  },
  {
    icon: BarChart3,
    title: "学习仪表盘",
    desc: "各科进度 · 掌握度热力图 · 错题分布 · 学习时长统计",
    status: "v2",
    gradient: "from-cyan-500/20 to-sky-500/10 via-cyan-500/5",
    iconBg: "bg-cyan-500/10 text-cyan-400",
  },
  {
    icon: FileDown,
    title: "复习资料导出",
    desc: "一键拼装教材要点 + 笔记 + 错题集 → 精美 PDF",
    status: "v2",
    gradient: "from-indigo-500/20 to-blue-500/10 via-indigo-500/5",
    iconBg: "bg-indigo-500/10 text-indigo-400",
  },
];

const techStack = [
  { name: "DeepSeek V4 Pro", icon: Cpu, desc: "LLM 推理" },
  { name: "Whisper 本地", icon: Mic, desc: "语音转写" },
  { name: "FastAPI", icon: Zap, desc: "后端框架" },
  { name: "Next.js 14", icon: Sparkles, desc: "前端框架" },
  { name: "ChromaDB", icon: Search, desc: "向量搜索" },
  { name: "离线可用", icon: Shield, desc: "数据本地" },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950">
      {/* Grain / noise overlay */}
      <div className="pointer-events-none fixed inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIj48ZmlsdGVyIGlkPSJhIj48ZmVUdXJidWxlbmNlIGJhc2VGcmVxdWVuY3k9Ii43NSIgc3RpdGNoVGlsZXM9InN0aXRjaCIgdHlwZT0iZnJhY3RhbE5vaXNlIi8+PGZlQ29sb3JNYXRyaXggdHlwZT0ic2F0dXJhdGUiIHZhbHVlcz0iMCIvPjwvZmlsdGVyPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbHRlcj0idXJsKCNhKSIgb3BhY2l0eT0iLjAzIi8+PC9zdmc+')] opacity-40" />

      {/* Hero */}
      <section className="relative mx-auto max-w-6xl px-6 pb-12 pt-24 text-center">
        {/* Badge */}
        <div className="mb-8 inline-flex animate-fade-up items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-sm text-blue-300 backdrop-blur">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-blue-400 opacity-75" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-blue-500" />
          </span>
          v0.1 — AI 引擎就绪
        </div>

        <h1 className="animate-fade-up text-6xl font-extrabold tracking-tight sm:text-7xl [animation-delay:100ms]">
          <span className="text-white">学舟</span>{" "}
          <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-violet-400 bg-clip-text text-transparent">
            StudyOS
          </span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl animate-fade-up text-lg leading-relaxed text-slate-400 [animation-delay:200ms]">
          为留学生打造的 AI 学习操作系统。
          <br className="hidden sm:block" />
          教材解析 · 录音转写 · 智能出题 · 错题管理 · 一键导出 —— 全部离线可用。
        </p>

        {/* CTA */}
        <div className="mt-10 flex animate-fade-up items-center justify-center gap-4 [animation-delay:300ms]">
          <a
            href="#"
            className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/25 transition-all hover:from-blue-500 hover:to-indigo-500 hover:shadow-blue-500/30"
          >
            开始使用
            <ChevronRight size={16} />
          </a>
          <a
            href="https://github.com/975801846-star/study-os"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800/50 px-6 py-3 text-sm font-medium text-slate-300 backdrop-blur transition-colors hover:border-slate-600 hover:text-white"
          >
            <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
            GitHub
          </a>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="relative mx-auto max-w-6xl px-6 pb-24">
        <div className="mb-10 text-center">
          <h2 className="text-2xl font-bold text-white">核心功能</h2>
          <p className="mt-2 text-slate-400">七模块覆盖完整学习闭环</p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map(({ icon: Icon, title, desc, status, gradient, iconBg }, i) => (
            <div
              key={title}
              className={`group relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br ${gradient} p-6 backdrop-blur transition-all hover:-translate-y-1 hover:border-white/20 hover:shadow-2xl`}
              style={{ animationDelay: `${i * 80}ms` }}
            >
              {/* Icon */}
              <div className={`mb-4 inline-flex rounded-xl ${iconBg} p-3`}>
                <Icon size={22} />
              </div>

              {/* Title + badge */}
              <div className="mb-2 flex items-center gap-2.5">
                <h3 className="font-semibold text-white">{title}</h3>
                <span
                  className={`rounded-md px-1.5 py-0.5 text-[10px] font-semibold tracking-wide ${
                    status === "v1"
                      ? "bg-blue-500/20 text-blue-300"
                      : "bg-slate-700 text-slate-400"
                  }`}
                >
                  {status === "v1" ? "P1" : "P2"}
                </span>
              </div>

              <p className="text-sm leading-relaxed text-slate-400">{desc}</p>

              {/* Hover glow */}
              <div className="pointer-events-none absolute -inset-1 rounded-2xl bg-gradient-to-br from-white/5 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
            </div>
          ))}
        </div>
      </section>

      {/* Tech Stack Bar */}
      <section className="relative border-y border-white/5 bg-white/[0.02] py-16">
        <div className="mx-auto max-w-4xl px-6">
          <h3 className="mb-8 text-center text-sm font-medium uppercase tracking-widest text-slate-500">
            技术栈
          </h3>
          <div className="grid grid-cols-3 gap-8 sm:grid-cols-6">
            {techStack.map(({ name, icon: Icon, desc }) => (
              <div key={name} className="flex flex-col items-center gap-2 text-center">
                <div className="rounded-xl bg-slate-800 p-3 text-slate-400">
                  <Icon size={20} />
                </div>
                <span className="text-xs font-medium text-slate-300">{name}</span>
                <span className="text-[11px] text-slate-500">{desc}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-10 text-center">
        <p className="text-sm text-slate-500">
          🚣 学舟 StudyOS v0.1 · MIT License
        </p>
        <p className="mt-1 text-xs text-slate-600">
          Made by 安同学 · Loughborough University · Sport Analytics &amp; AI
        </p>
        <p className="mt-3 text-xs text-slate-700">
          DeepSeek V4 · Whisper · sentence-transformers · ChromaDB · FastAPI · Next.js
        </p>
      </footer>
    </div>
  );
}
