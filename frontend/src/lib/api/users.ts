/**
 * 사용자 관리 API 함수.
 *
 * [개발 표준]
 * - 모든 API 함수는 apiClient를 사용합니다.
 * - 관리자 전용 API입니다.
 */

import apiClient from "./client";

// ─── 타입 정의 ──────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string | null;
  updated_at: string | null;
}

export interface UserListResponse {
  data: User[];
  total: number;
}

export interface UserCreateRequest {
  email: string;
  password: string;
  full_name?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface UserUpdateRequest {
  email?: string;
  password?: string;
  full_name?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

// ─── API 함수 ───────────────────────────────────────────────

/** 사용자 목록 조회 (관리자 전용) */
export async function getUsersApi(
  page: number = 1,
  size: number = 20
): Promise<UserListResponse> {
  const skip = (page - 1) * size;
  const response = await apiClient.get<UserListResponse>("/users", {
    params: { skip, limit: size },
  });
  return response.data;
}

/** 사용자 상세 조회 (관리자 전용) */
export async function getUserApi(id: string): Promise<User> {
  const response = await apiClient.get<User>(`/users/${id}`);
  return response.data;
}

/** 사용자 생성 (관리자 전용) */
export async function createUserApi(data: UserCreateRequest): Promise<User> {
  const response = await apiClient.post<User>("/users", data);
  return response.data;
}

/** 사용자 수정 (관리자 전용) */
export async function updateUserApi(
  id: string,
  data: UserUpdateRequest
): Promise<User> {
  const response = await apiClient.put<User>(`/users/${id}`, data);
  return response.data;
}

/** 사용자 삭제 (관리자 전용) */
export async function deleteUserApi(id: string): Promise<void> {
  await apiClient.delete(`/users/${id}`);
}
