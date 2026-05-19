/**
 * 学舟 Zustand 状态管理 — Quiz Store
 */
import { create } from "zustand";

export interface Question {
  id: string;
  type: "choice" | "tf" | "short_answer" | "case_study";
  question: string;
  options?: string[];
  answer?: string;
  explanation?: string;
  knowledge_point?: string;
}

export interface FeedbackItem {
  question_id: string;
  question: string;
  user_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation: string;
  knowledge_point: string;
}

export interface ChapterInfo {
  index: number;
  title: string;
  char_count: number;
  start_char: number;
  end_char: number;
}

interface QuizState {
  // 上传
  fullText: string;
  chapters: ChapterInfo[];

  // 生成
  sourceContent: string;
  selectedChapterIndex: number | null; // null = 全文
  questionTypes: string[];
  count: number;
  difficulty: string;
  language: string;
  generating: boolean;
  quizId: string | null;
  quizTitle: string;
  questions: Question[];

  // 做题
  answers: Record<string, string>;
  submitted: boolean;
  submitting: boolean;
  score: number;
  total: number;
  feedback: FeedbackItem[];
  wrongCount: number;

  // Actions
  setFullText: (text: string) => void;
  setChapters: (chapters: ChapterInfo[]) => void;
  selectChapter: (index: number | null) => void;
  setSourceContent: (text: string) => void;
  setQuestionTypes: (types: string[]) => void;
  setCount: (n: number) => void;
  setDifficulty: (d: string) => void;
  setAnswer: (qid: string, answer: string) => void;
  generateQuiz: () => Promise<void>;
  submitAnswers: () => Promise<void>;
  reset: () => void;
}

const BASE = "/api/quizzes";

export const useQuizStore = create<QuizState>((set, get) => ({
  fullText: "",
  chapters: [],
  sourceContent: "",
  selectedChapterIndex: null,
  questionTypes: ["choice", "tf"],
  count: 5,
  difficulty: "basic",
  language: "zh",
  generating: false,
  quizId: null,
  quizTitle: "",
  questions: [],

  answers: {},
  submitted: false,
  submitting: false,
  score: 0,
  total: 0,
  feedback: [],
  wrongCount: 0,

  setFullText: (text) => set({ fullText: text }),
  setChapters: (chapters) => set({ chapters }),
  selectChapter: (index) => {
    const s = get();
    if (index === null || index < 0 || index >= s.chapters.length) {
      // 全文模式
      set({ sourceContent: s.fullText, selectedChapterIndex: null });
      return;
    }
    const ch = s.chapters[index];
    if (!ch) return;
    const content = s.fullText.slice(ch.start_char, ch.end_char);
    set({ sourceContent: content, selectedChapterIndex: index });
  },
  setSourceContent: (text) => set({ sourceContent: text }),
  setQuestionTypes: (types) => set({ questionTypes: types }),
  setCount: (n) => set({ count: n }),
  setDifficulty: (d) => set({ difficulty: d }),
  setAnswer: (qid, answer) =>
    set((s) => ({ answers: { ...s.answers, [qid]: answer } })),

  generateQuiz: async () => {
    const s = get();
    set({ generating: true });
    try {
      const res = await fetch(`${BASE}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_content: s.sourceContent,
          question_types: s.questionTypes,
          count: s.count,
          difficulty: s.difficulty,
          language: s.language,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "生成失败");
      set({
        quizId: data.id,
        quizTitle: data.title,
        questions: data.questions,
        generating: false,
      });
    } catch (err: any) {
      set({ generating: false });
      alert(err.message);
    }
  },

  submitAnswers: async () => {
    const s = get();
    if (!s.quizId) return;
    set({ submitting: true });
    try {
      const res = await fetch(`${BASE}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          quiz_id: s.quizId,
          answers: s.answers,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "提交失败");
      set({
        submitted: true,
        submitting: false,
        score: data.score,
        total: data.total,
        feedback: data.feedback,
        wrongCount: data.wrong_count,
      });
    } catch (err: any) {
      set({ submitting: false });
      alert(err.message);
    }
  },

  reset: () =>
    set({
      fullText: "",
      chapters: [],
      sourceContent: "",
      selectedChapterIndex: null,
      quizId: null,
      quizTitle: "",
      questions: [],
      answers: {},
      submitted: false,
      score: 0,
      total: 0,
      feedback: [],
      wrongCount: 0,
    }),
}));
