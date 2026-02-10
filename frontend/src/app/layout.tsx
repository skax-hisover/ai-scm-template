import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI-SCM",
  description: "AI-SCM Template",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-gray-50 antialiased">{children}</body>
    </html>
  );
}
