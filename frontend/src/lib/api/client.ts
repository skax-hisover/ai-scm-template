/**
 * Axios API 클라이언트 설정.
 *
 * [개발 표준]
 * - 모든 API 호출은 이 클라이언트 인스턴스를 사용하세요.
 * - 직접 axios.get(), axios.post() 등을 사용하지 마세요.
 * - 인터셉터에서 토큰 자동 주입 및 에러 처리를 수행합니다.
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { getAccessToken, removeTokens, setTokens } from "@/lib/auth/token";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_V1 = "/api/v1";

/**
 * API 클라이언트 인스턴스
 */
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}${API_V1}`,
  timeout: 30000, // 30초
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * 요청 인터셉터 - JWT 토큰 자동 주입
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * 응답 인터셉터 - 401 에러 시 토큰 갱신 또는 로그아웃 처리
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // 401 에러이고 재시도하지 않은 경우
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // 리프레시 토큰으로 재발급 시도
        const refreshToken = localStorage.getItem("refresh_token");
        if (refreshToken) {
          const response = await axios.post(
            `${API_BASE_URL}${API_V1}/auth/refresh`,
            { refresh_token: refreshToken }
          );
          const { access_token, refresh_token: newRefreshToken } = response.data;
          setTokens(access_token, newRefreshToken);
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch {
        // 리프레시 실패 시 로그아웃
        removeTokens();
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
