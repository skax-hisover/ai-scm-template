"use client";

import { useEffect, useState } from "react";
import { getMeApi, type UserResponse } from "@/lib/api/auth";

/**
 * 대시보드 메인 페이지 (샘플).
 */
export default function DashboardPage() {
  const [user, setUser] = useState<UserResponse | null>(null);

  useEffect(() => {
    getMeApi()
      .then(setUser)
      .catch(() => setUser(null));
  }, []);

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-gray-900">대시보드</h1>

      {/* 환영 카드 */}
      <div className="mb-8 rounded-xl bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-800">
          안녕하세요, {user?.full_name || user?.email || "사용자"}님! 👋
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          AI-SCM 프로젝트에 오신 것을 환영합니다.
        </p>
      </div>

      {/* 통계 카드 (샘플) */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "전체 아이템", value: "-", icon: "📦" },
          { label: "활성 사용자", value: "-", icon: "👤" },
          { label: "금일 작업", value: "-", icon: "📋" },
          { label: "시스템 상태", value: "정상", icon: "✅" },
        ].map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl bg-white p-6 shadow-sm"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">{stat.label}</p>
                <p className="mt-1 text-2xl font-bold text-gray-900">
                  {stat.value}
                </p>
              </div>
              <span className="text-3xl">{stat.icon}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
