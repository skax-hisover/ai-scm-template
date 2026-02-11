"use client";

import { useEffect, useState } from "react";
import { getMeApi, type UserResponse } from "@/lib/api/auth";
import { getItemsApi } from "@/lib/api/items";
import { getUsersApi } from "@/lib/api/users";
import { getDetailedHealthApi } from "@/lib/api/health";

/**
 * 대시보드 메인 페이지.
 *
 * [기능]
 * - 환영 메시지 (로그인 사용자 이름)
 * - 전체 아이템 수 표시
 * - 활성 사용자 수 표시 (관리자만)
 * - 시스템 상태 표시
 */
export default function DashboardPage() {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [itemTotal, setItemTotal] = useState<number | null>(null);
  const [activeUserCount, setActiveUserCount] = useState<number | null>(null);
  const [systemStatus, setSystemStatus] = useState<string>("-");
  const [systemStatusIcon, setSystemStatusIcon] = useState<string>("⏳");

  useEffect(() => {
    // 현재 사용자 정보 조회
    getMeApi()
      .then((me) => {
        setUser(me);

        // 관리자인 경우 활성 사용자 수 조회
        if (me.is_superuser) {
          getUsersApi(1, 100)
            .then((data) => {
              const activeCount = data.data.filter((u) => u.is_active).length;
              setActiveUserCount(activeCount);
            })
            .catch(() => setActiveUserCount(null));
        }
      })
      .catch(() => setUser(null));

    // 아이템 수 조회
    getItemsApi(1, 1)
      .then((data) => setItemTotal(data.total))
      .catch(() => setItemTotal(null));

    // 시스템 상태 조회
    getDetailedHealthApi()
      .then((data) => {
        setSystemStatus(data.overall);
        if (data.overall === "정상") {
          setSystemStatusIcon("✅");
        } else if (data.overall === "경고") {
          setSystemStatusIcon("⚠️");
        } else {
          setSystemStatusIcon("❌");
        }
      })
      .catch(() => {
        setSystemStatus("연결 실패");
        setSystemStatusIcon("❌");
      });
  }, []);

  // 통계 데이터 (관리자 전용 카드는 조건부로 추가)
  const stats = [
    {
      label: "전체 아이템",
      value: itemTotal !== null ? itemTotal.toLocaleString() : "-",
      icon: "📦",
    },
    // 관리자인 경우에만 활성 사용자 카드 표시
    ...(user?.is_superuser
      ? [
          {
            label: "활성 사용자",
            value:
              activeUserCount !== null
                ? activeUserCount.toLocaleString()
                : "-",
            icon: "👤",
          },
        ]
      : []),
    {
      label: "금일 작업",
      value: "-",
      icon: "📋",
      sub: "준비중",
    },
    {
      label: "시스템 상태",
      value: systemStatus,
      icon: systemStatusIcon,
    },
  ];

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

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
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
                {stat.sub && (
                  <p className="mt-0.5 text-xs text-gray-400">{stat.sub}</p>
                )}
              </div>
              <span className="text-3xl">{stat.icon}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
