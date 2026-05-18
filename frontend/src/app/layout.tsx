import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "学舟 StudyOS",
  description: "AI 驱动的个人学习操作系统",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
