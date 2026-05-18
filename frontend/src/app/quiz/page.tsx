"use client";

import { useRef, useState } from "react";
import {
  BrainCircuit,
  Check,
  ChevronLeft,
  FileText,
  Lightbulb,
  Loader2,
  Sparkles,
  Target,
  Upload,
  X,
} from "lucide-react";
import { useQuizStore } from "@/store";

const typeOptions = [
  { value: "choice", label: "选择题" },
  { value: "tf", label: "判断题" },
  { value: "short_answer", label: "简答题" },
];

const diffOptions = [
  { value: "basic", label: "基础" },
  { value: "advanced", label: "进阶" },
  { value: "comprehensive", label: "综合" },
];

export default function QuizPage() {
  const store = useQuizStore();
  const [showSettings, setShowSettings] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (file: File) => {
    if (!file) return;
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (!["pdf", "txt", "md"].includes(ext || "")) {
      alert("仅支持 PDF / TXT / MD 文件");
      return;
    }
    setUploading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch("/api/quizzes/upload-source", {
        method: "POST",
        body: form,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "上传失败");
      store.setSourceContent(data.data.content);
      setUploadedFile(`${data.data.filename} (${(data.data.char_count / 1000).toFixed(1)}k 字${data.data.truncated ? "，已截取" : ""})`);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  // ── Step 1: 输入材料 ──
  if (!store.quizId) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-16">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 inline-flex rounded-2xl bg-amber-500/10 p-4 text-amber-400">
            <BrainCircuit size={32} />
          </div>
          <h1 className="text-3xl font-bold text-white">AI 出题</h1>
          <p className="mt-2 text-slate-400">
            粘贴学习材料，一键生成测验题目
          </p>
        </div>

        {/* Settings */}
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="mb-3 text-xs text-slate-500 hover:text-slate-300 transition-colors"
        >
          {showSettings ? "收起设置 ▲" : "展开设置 ▼"}
        </button>
        {showSettings && (
          <div className="mb-4 grid grid-cols-2 gap-3 rounded-xl border border-white/10 bg-white/5 p-4 sm:grid-cols-4">
            {/* 题型 */}
            <div>
              <label className="mb-1.5 block text-[11px] text-slate-500">题型</label>
              <div className="flex flex-wrap gap-1">
                {typeOptions.map((t) => (
                  <button
                    key={t.value}
                    onClick={() =>
                      store.setQuestionTypes(
                        store.questionTypes.includes(t.value)
                          ? store.questionTypes.filter((x) => x !== t.value)
                          : [...store.questionTypes, t.value]
                      )
                    }
                    className={`rounded-md px-2 py-1 text-[11px] font-medium transition-colors ${
                      store.questionTypes.includes(t.value)
                        ? "bg-amber-500/20 text-amber-300 ring-1 ring-amber-500/30"
                        : "bg-slate-800 text-slate-500 hover:bg-slate-700"
                    }`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>
            {/* 数量 */}
            <div>
              <label className="mb-1.5 block text-[11px] text-slate-500">数量</label>
              <select
                value={store.count}
                onChange={(e) => store.setCount(Number(e.target.value))}
                className="w-full rounded-md border border-white/10 bg-slate-800 px-2 py-1.5 text-xs text-slate-300"
              >
                {[3, 5, 8, 10, 15, 20].map((n) => (
                  <option key={n} value={n}>{n} 题</option>
                ))}
              </select>
            </div>
            {/* 难度 */}
            <div>
              <label className="mb-1.5 block text-[11px] text-slate-500">难度</label>
              <div className="flex gap-1">
                {diffOptions.map((d) => (
                  <button
                    key={d.value}
                    onClick={() => store.setDifficulty(d.value)}
                    className={`rounded-md px-2 py-1 text-[11px] font-medium transition-colors ${
                      store.difficulty === d.value
                        ? "bg-blue-500/20 text-blue-300 ring-1 ring-blue-500/30"
                        : "bg-slate-800 text-slate-500 hover:bg-slate-700"
                    }`}
                  >
                    {d.label}
                  </button>
                ))}
              </div>
            </div>
            {/* 语言 */}
            <div>
              <label className="mb-1.5 block text-[11px] text-slate-500">语言</label>
              <select
                value={store.language}
                onChange={(e) => useQuizStore.setState({ language: e.target.value })}
                className="w-full rounded-md border border-white/10 bg-slate-800 px-2 py-1.5 text-xs text-slate-300"
              >
                <option value="zh">中文</option>
                <option value="en">English</option>
              </select>
            </div>
          </div>
        )}

        {/* Upload Zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`mb-3 cursor-pointer rounded-xl border-2 border-dashed p-6 text-center transition-all ${
            dragOver
              ? "border-blue-400/50 bg-blue-500/10"
              : uploadedFile
              ? "border-emerald-500/30 bg-emerald-500/5"
              : "border-white/10 bg-white/[0.02] hover:border-white/20 hover:bg-white/[0.04]"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt,.md"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleUpload(file);
            }}
          />
          {uploading ? (
            <div className="flex items-center justify-center gap-2 text-slate-400">
              <Loader2 size={18} className="animate-spin" />
              <span className="text-sm">正在解析文档...</span>
            </div>
          ) : uploadedFile ? (
            <div className="flex items-center justify-center gap-2 text-emerald-400">
              <FileText size={18} />
              <span className="text-sm font-medium">{uploadedFile}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  store.setSourceContent("");
                  setUploadedFile(null);
                }}
                className="ml-2 rounded-md p-0.5 text-slate-500 hover:text-rose-400 transition-colors"
              >
                <X size={14} />
              </button>
            </div>
          ) : (
            <div className="text-slate-500">
              <Upload size={24} className="mx-auto mb-2" />
              <span className="text-sm">
                拖拽上传 PDF / TXT / MD 文档，或点击选择
              </span>
              <p className="mt-1 text-xs text-slate-600">
                最大 20MB · PDF 自动解析文本
              </p>
            </div>
          )}
        </div>

        {/* Divider */}
        <div className="mb-3 flex items-center gap-3">
          <hr className="flex-1 border-white/5" />
          <span className="text-[11px] text-slate-600">或手动粘贴</span>
          <hr className="flex-1 border-white/5" />
        </div>

        {/* Text Input */}
        <textarea
          value={store.sourceContent}
          onChange={(e) => store.setSourceContent(e.target.value)}
          placeholder="在此粘贴学习材料...（至少 50 字）"
          rows={12}
          className="w-full rounded-xl border border-white/10 bg-white/5 p-5 text-sm text-slate-200 placeholder-slate-600 backdrop-blur transition-colors focus:border-blue-500/50 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
        />

        {/* Generate Button */}
        <button
          onClick={store.generateQuiz}
          disabled={store.sourceContent.length < 50 || store.generating}
          className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-amber-500/20 transition-all hover:from-amber-400 hover:to-orange-400 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {store.generating ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              AI 正在出题...
            </>
          ) : (
            <>
              <Sparkles size={16} />
              生成题目
            </>
          )}
        </button>
      </div>
    );
  }

  // ── Step 2: 做题 ──
  if (!store.submitted) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-12">
        {/* Header */}
        <div className="mb-8 flex items-center gap-4">
          <button
            onClick={store.reset}
            className="rounded-lg border border-white/10 p-2 text-slate-400 hover:bg-white/5 hover:text-white transition-colors"
          >
            <ChevronLeft size={18} />
          </button>
          <div>
            <h1 className="text-xl font-bold text-white">{store.quizTitle}</h1>
            <p className="text-xs text-slate-500">
              {store.questions.length} 题 · {store.questionTypes.join("/")}
            </p>
          </div>
        </div>

        {/* Questions */}
        <div className="space-y-6">
          {store.questions.map((q, i) => (
            <div
              key={q.id}
              className="rounded-xl border border-white/10 bg-white/5 p-5 backdrop-blur"
            >
              <div className="mb-3 flex items-start gap-2">
                <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-lg bg-blue-500/10 text-xs font-bold text-blue-400">
                  {i + 1}
                </span>
                <p className="text-sm text-slate-200 leading-relaxed">{q.question}</p>
              </div>

              {/* Choice */}
              {q.type === "choice" && q.options && (
                <div className="ml-8 space-y-2">
                  {q.options.map((opt) => {
                    const letter = opt.slice(0, 1);
                    const selected = store.answers[q.id] === letter;
                    return (
                      <button
                        key={letter}
                        onClick={() => store.setAnswer(q.id, letter)}
                        className={`flex w-full items-center gap-3 rounded-lg border px-4 py-2.5 text-left text-sm transition-all ${
                          selected
                            ? "border-blue-500/50 bg-blue-500/10 text-blue-200"
                            : "border-white/5 bg-white/[0.02] text-slate-400 hover:border-white/10 hover:bg-white/5"
                        }`}
                      >
                        <span
                          className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-md text-xs font-bold ${
                            selected
                              ? "bg-blue-500 text-white"
                              : "bg-slate-700 text-slate-400"
                          }`}
                        >
                          {letter}
                        </span>
                        {opt.slice(3)}
                      </button>
                    );
                  })}
                </div>
              )}

              {/* True/False */}
              {q.type === "tf" && (
                <div className="ml-8 flex gap-3">
                  {["对", "错"].map((v) => {
                    const selected = store.answers[q.id] === v;
                    return (
                      <button
                        key={v}
                        onClick={() => store.setAnswer(q.id, v)}
                        className={`flex-1 rounded-lg border px-4 py-2.5 text-center text-sm font-medium transition-all ${
                          selected
                            ? v === "对"
                              ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-300"
                              : "border-rose-500/50 bg-rose-500/10 text-rose-300"
                            : "border-white/5 bg-white/[0.02] text-slate-400 hover:border-white/10 hover:bg-white/5"
                        }`}
                      >
                        {v === "对" ? "✓ 对" : "✗ 错"}
                      </button>
                    );
                  })}
                </div>
              )}

              {/* Short Answer */}
              {q.type === "short_answer" && (
                <div className="ml-8">
                  <textarea
                    value={store.answers[q.id] || ""}
                    onChange={(e) => store.setAnswer(q.id, e.target.value)}
                    placeholder="输入你的答案..."
                    rows={3}
                    className="w-full rounded-lg border border-white/10 bg-white/5 p-3 text-sm text-slate-200 placeholder-slate-600 transition-colors focus:border-blue-500/50 focus:outline-none"
                  />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Submit */}
        <button
          onClick={store.submitAnswers}
          disabled={store.submitting}
          className="mt-8 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/20 transition-all hover:from-blue-500 hover:to-indigo-500 disabled:opacity-40"
        >
          {store.submitting ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              批改中...
            </>
          ) : (
            <>
              <Check size={16} />
              提交答案
            </>
          )}
        </button>
      </div>
    );
  }

  // ── Step 3: 结果 ──
  return (
    <div className="mx-auto max-w-2xl px-6 py-12">
      {/* Score Card */}
      <div className="mb-8 rounded-2xl border border-white/10 bg-gradient-to-br from-blue-500/10 to-indigo-500/5 p-8 text-center backdrop-blur">
        <div className="mb-3 inline-flex rounded-2xl bg-blue-500/10 p-4 text-blue-400">
          <Target size={32} />
        </div>
        <div className="text-5xl font-extrabold text-white">{store.score}</div>
        <div className="mt-1 text-sm text-slate-400">
          得分 · {store.total} 题 · 错 {store.wrongCount} 题
        </div>
        <p className="mt-3 text-xs text-slate-500">
          AI 批改完成 · 错题已自动收入错题本
        </p>
      </div>

      {/* Feedback */}
      <h2 className="mb-4 text-lg font-semibold text-white">答题详情</h2>
      <div className="space-y-4">
        {store.feedback.map((f, i) => (
          <div
            key={f.question_id}
            className={`rounded-xl border p-5 backdrop-blur ${
              f.is_correct
                ? "border-emerald-500/10 bg-emerald-500/[0.03]"
                : "border-rose-500/10 bg-rose-500/[0.03]"
            }`}
          >
            <div className="mb-3 flex items-start gap-3">
              <span
                className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-lg text-xs font-bold ${
                  f.is_correct
                    ? "bg-emerald-500/20 text-emerald-400"
                    : "bg-rose-500/20 text-rose-400"
                }`}
              >
                {f.is_correct ? <Check size={12} /> : <X size={12} />}
              </span>
              <div>
                <p className="text-sm text-slate-200">{f.question}</p>
                {f.knowledge_point && (
                  <span className="mt-1 inline-block rounded-md bg-slate-800 px-2 py-0.5 text-[11px] text-slate-500">
                    {f.knowledge_point}
                  </span>
                )}
              </div>
            </div>

            <div className="ml-9 space-y-2 text-xs">
              <div className="flex gap-2">
                <span className="shrink-0 text-slate-500">你的答案：</span>
                <span className={f.is_correct ? "text-emerald-400" : "text-rose-400"}>
                  {f.user_answer || "（未作答）"}
                </span>
              </div>
              {!f.is_correct && (
                <div className="flex gap-2">
                  <span className="shrink-0 text-slate-500">正确答案：</span>
                  <span className="text-emerald-400">{f.correct_answer}</span>
                </div>
              )}
              {f.explanation && (
                <div className="flex gap-2 rounded-lg bg-white/[0.02] p-3 text-slate-400">
                  <Lightbulb size={14} className="mt-0.5 shrink-0 text-amber-500" />
                  <span>{f.explanation}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="mt-8 flex gap-3">
        <button
          onClick={() =>
            useQuizStore.setState({ submitted: false, score: 0, total: 0, feedback: [], wrongCount: 0 })
          }
          className="flex-1 rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-medium text-slate-300 backdrop-blur transition-colors hover:bg-white/10"
        >
          再做一次
        </button>
        <button
          onClick={store.reset}
          className="flex-1 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-600/20 transition-all hover:from-blue-500 hover:to-indigo-500"
        >
          出新的题目
        </button>
      </div>
    </div>
  );
}
