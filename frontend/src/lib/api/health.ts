/**
 * 시스템 헬스체크 API.
 *
 * [개발 표준]
 * - 대시보드에서 시스템 상태를 동적으로 표시하기 위해 사용합니다.
 */

import apiClient from "./client";

/** 개별 구성요소 상태 */
export interface HealthCheckDetail {
  status: "정상" | "경고" | "오류";
  message: string;
}

/** 상세 헬스체크 응답 */
export interface DetailedHealthResponse {
  overall: "정상" | "경고" | "오류";
  checks: {
    database: HealthCheckDetail;
    redis?: HealthCheckDetail;
  };
}

/**
 * 상세 시스템 상태 조회.
 * DB, Redis 등 주요 구성요소의 상태를 반환합니다.
 */
export async function getDetailedHealthApi(): Promise<DetailedHealthResponse> {
  const response = await apiClient.get<DetailedHealthResponse>(
    "/health/detailed"
  );
  return response.data;
}
