/**
 * 아이템 API 함수 (샘플).
 *
 * [개발 표준]
 * - 새로운 API 모듈을 추가할 때 이 파일을 참고하세요.
 * - 모든 API 함수는 apiClient를 사용합니다.
 * - 타입은 types/ 폴더에 별도 정의하거나, 같은 파일에 정의할 수 있습니다.
 */

import apiClient from "./client";

// ─── 타입 정의 ──────────────────────────────────────────────

export interface Item {
  id: string;
  title: string;
  description: string | null;
  owner_id: string;
  created_at: string | null;
  updated_at: string | null;
}

export interface ItemListResponse {
  data: Item[];
  total: number;
}

export interface ItemCreateRequest {
  title: string;
  description?: string;
}

export interface ItemUpdateRequest {
  title?: string;
  description?: string;
}

// ─── API 함수 ───────────────────────────────────────────────

/** 아이템 목록 조회 */
export async function getItemsApi(
  page: number = 1,
  size: number = 20
): Promise<ItemListResponse> {
  const skip = (page - 1) * size;
  const response = await apiClient.get<ItemListResponse>("/items", {
    params: { skip, limit: size },
  });
  return response.data;
}

/** 아이템 상세 조회 */
export async function getItemApi(id: string): Promise<Item> {
  const response = await apiClient.get<Item>(`/items/${id}`);
  return response.data;
}

/** 아이템 생성 */
export async function createItemApi(data: ItemCreateRequest): Promise<Item> {
  const response = await apiClient.post<Item>("/items", data);
  return response.data;
}

/** 아이템 수정 */
export async function updateItemApi(
  id: string,
  data: ItemUpdateRequest
): Promise<Item> {
  const response = await apiClient.put<Item>(`/items/${id}`, data);
  return response.data;
}

/** 아이템 삭제 */
export async function deleteItemApi(id: string): Promise<void> {
  await apiClient.delete(`/items/${id}`);
}
