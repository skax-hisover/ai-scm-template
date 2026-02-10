"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { isAuthenticated, removeTokens } from "@/lib/auth/token";

/**
 * 대시보드 레이아웃 (인증 필수).
 *
 * [개발 표준]
 * - 인증이 필요한 페이지는 이 레이아웃 하위에 배치합니다.
 * - 사이드바/헤더 등 공통 UI를 여기에 정의합니다.
 */
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
    }
  }, [router]);

  const handleLogout = () => {
    removeTokens();
    router.push("/login");
  };

  return (
    <div className="flex min-h-screen">
      {/* 사이드바 */}
      <aside className="w-64 border-r bg-white p-6">
        <h2 className="mb-8 text-xl font-bold text-blue-600">AI-SCM</h2>
        <nav className="space-y-2">
          <Link
            href="/dashboard"
            className="block rounded-lg px-3 py-2 text-sm text-gray-700 hover:bg-gray-100"
          >
            📊 대시보드
          </Link>
          <Link
            href="/dashboard/items"
            className="block rounded-lg px-3 py-2 text-sm text-gray-700 hover:bg-gray-100"
          >
            📦 아이템 관리
          </Link>
          {/* ─── 새로운 메뉴 추가 위치 ─── */}
        </nav>
        <div className="mt-auto pt-8">
          <button
            onClick={handleLogout}
            className="w-full rounded-lg px-3 py-2 text-left text-sm text-gray-500 hover:bg-gray-100"
          >
            🚪 로그아웃
          </button>
        </div>
      </aside>

      {/* 메인 콘텐츠 */}
      <main className="flex-1 bg-gray-50 p-8">{children}</main>
    </div>
  );
}
