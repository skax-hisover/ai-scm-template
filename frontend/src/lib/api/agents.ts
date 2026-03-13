/**
 * Agent 실행 API 함수.
 */

import apiClient from "./client";

export interface AgentRun {
  id: string;
  agent_id: string;
  status: "queued" | "running" | "succeeded" | "failed";
  input_text: string;
  output_text: string | null;
  error_message: string | null;
  external_run_id: string | null;
  model_name: string | null;
  metadata_json: string | null;
  owner_id: string;
  started_at: string | null;
  finished_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface AgentRunCreateRequest {
  agent_id: string;
  input_text: string;
  sync?: boolean;
  model_name?: string;
  metadata?: Record<string, unknown>;
}

export interface AgentRunListResponse {
  data: AgentRun[];
  total: number;
}

/** Agent 실행 요청 생성 */
export async function createAgentRunApi(
  data: AgentRunCreateRequest
): Promise<AgentRun> {
  const response = await apiClient.post<AgentRun>("/agents/runs", data);
  return response.data;
}

/** Agent 실행 단건 조회 */
export async function getAgentRunApi(id: string): Promise<AgentRun> {
  const response = await apiClient.get<AgentRun>(`/agents/runs/${id}`);
  return response.data;
}

/** Agent 실행 목록 조회 */
export async function getAgentRunsApi(
  page: number = 1,
  size: number = 20
): Promise<AgentRunListResponse> {
  const skip = (page - 1) * size;
  const response = await apiClient.get<AgentRunListResponse>("/agents/runs", {
    params: { skip, limit: size },
  });
  return response.data;
}

