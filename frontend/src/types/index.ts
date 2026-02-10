/**
 * 전역 TypeScript 타입 정의.
 *
 * [개발 표준]
 * - API 응답 타입은 해당 API 모듈 (lib/api/) 파일에 정의합니다.
 * - 여러 곳에서 공유되는 타입만 이 파일에 정의합니다.
 */

/** API 에러 응답 */
export interface ApiError {
  detail: string;
  errors?: Array<{
    loc: string[];
    msg: string;
    type: string;
  }>;
}

/** 페이지네이션 응답 */
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  size: number;
}

/** 공통 메시지 응답 */
export interface MessageResponse {
  message: string;
}
