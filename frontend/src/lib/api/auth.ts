/**
 * 인증 관련 API 함수.
 */

import apiClient from "./client";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string | null;
  token_type: string;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string | null;
}

/**
 * JSON Body 로그인
 */
export async function loginApi(data: LoginRequest): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>("/auth/login/json", data);
  return response.data;
}

/**
 * 현재 로그인된 사용자 정보 조회
 */
export async function getMeApi(): Promise<UserResponse> {
  const response = await apiClient.get<UserResponse>("/auth/me");
  return response.data;
}
