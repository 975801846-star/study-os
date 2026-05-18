import {
  BookOpen,
  Mic,
  Brain,
  PenLine,
  BarChart3,
  Search,
  FileDown,
} from "lucide-react";

const features = [
  {
    icon: BookOpen,
    title: "教材导入",
    desc: "上传 PDF，自动解析为结构化知识库",
    status: "即将上线",
  },
  {
    icon: Mic,
    title: "课堂录音",
    desc: "上传录音 → 本地 Whisper 转写 → AI 标注重点",
    status: "即将上线",
  },
  {
    icon: Brain,
    title: "AI 出题",
    desc: "基于知识库自动生成选择/简答/案例分析题",
    status: "开发中",
  },
  {
    icon: PenLine,
    title: "在线做题",
    desc: "答题 → 自动批改 → 错题归因到知识点",
    status: "开发中",
  },
  {
    icon: BarChart3,
    title: "学习仪表盘",
    desc: "各科进度、掌握度、错题分布可视化",
    status: "即将上线",
  },
  {
    icon: Search,
    title: "全文搜索",
    desc: "跨教材、笔记的语义搜索",
    status: "即将上线",
  },
  {
    icon: FileDown,
    title: "复习资料导出",
    desc: "一键拼装教材要点 + 笔记 + 错题集 → PDF",
    status: "即将上线",
  },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Hero */}
      <div className="mx-auto max-w-5xl px-6 py-20 text-center">
        <h1 className="text-5xl font-bold tracking-tight text-gray-900">
          🚣 学舟{" "}
          <span className="text-blue-600">StudyOS</span>
        </h1>
        <p className="mt-4 text-lg text-gray-500">
          AI 驱动的个人学习操作系统 · 为拉夫堡留学之旅保驾护航
        </p>

        {/* Status */}
        <div className="mt-8 inline-flex items-center gap-2 rounded-full bg-green-50 px-4 py-2 text-sm text-green-700 ring-1 ring-green-200">
          <span className="relative flex h-2.5 w-2.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75" />
            <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-green-500" />
          </span>
          系统已就绪 · DeepSeek V4 Pro · 纯本地 STT/Embedding
        </div>
      </div>

      {/* Features Grid */}
      <div className="mx-auto max-w-5xl px-6 pb-20">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map(({ icon: Icon, title, desc, status }) => (
            <div
              key={title}
              className="group rounded-2xl border border-gray-100 bg-white p-6 transition-shadow hover:shadow-md"
            >
              <div className="mb-4 inline-flex rounded-xl bg-blue-50 p-3 text-blue-600">
                <Icon size={24} />
              </div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-gray-900">{title}</h3>
                <span
                  className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${
                    status === "开发中"
                      ? "bg-amber-50 text-amber-700 ring-1 ring-amber-200"
                      : "bg-gray-50 text-gray-500 ring-1 ring-gray-200"
                  }`}
                >
                  {status}
                </span>
              </div>
              <p className="mt-2 text-sm text-gray-500">{desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-8 text-center text-sm text-gray-400">
        <p>学舟 StudyOS v0.1 · MIT License · 安同学</p>
        <p className="mt-1">
          Powered by DeepSeek V4 · Whisper · sentence-transformers
        </p>
      </footer>
    </main>
  );
}
