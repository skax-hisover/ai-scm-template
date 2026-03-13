"use client";

import { useCallback, useEffect, useState } from "react";
import Button from "@/components/ui/Button";
import {
  createAgentRunApi,
  getAgentRunApi,
  getAgentRunsApi,
  type AgentRun,
} from "@/lib/api/agents";

const TERMINAL_STATUSES = new Set(["succeeded", "failed"]);

export default function AgentsPage() {
  const [agentId, setAgentId] = useState("default-agent");
  const [inputText, setInputText] = useState("");
  const [syncMode, setSyncMode] = useState(false);

  const [runs, setRuns] = useState<AgentRun[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [runningId, setRunningId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadRuns = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAgentRunsApi();
      setRuns(data.data);
      setTotal(data.total);
    } catch {
      setError("실행 이력을 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadRuns();
  }, [loadRuns]);

  useEffect(() => {
    if (!runningId) return;
    const interval = setInterval(async () => {
      try {
        const run = await getAgentRunApi(runningId);
        if (TERMINAL_STATUSES.has(run.status)) {
          setRunningId(null);
          loadRuns();
        }
      } catch {
        setRunningId(null);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [runningId, loadRuns]);

  const handleRun = async () => {
    if (!agentId.trim() || !inputText.trim()) {
      setError("Agent ID와 입력 텍스트는 필수입니다.");
      return;
    }

    setError(null);
    try {
      const run = await createAgentRunApi({
        agent_id: agentId.trim(),
        input_text: inputText.trim(),
        sync: syncMode,
      });
      setInputText("");
      loadRuns();
      if (!TERMINAL_STATUSES.has(run.status)) {
        setRunningId(run.id);
      }
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { detail?: string } } };
      setError(apiError?.response?.data?.detail || "Agent 실행 요청에 실패했습니다.");
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Agent 실행</h1>
        <p className="mt-1 text-sm text-gray-500">
          Agent 플랫폼 실행 요청을 만들고 상태/결과를 확인합니다.
        </p>
      </div>

      {error && (
        <div className="mb-4 rounded-lg bg-red-50 p-4 text-sm text-red-600">
          {error}
        </div>
      )}

      <div className="mb-6 rounded-xl bg-white p-6 shadow-sm">
        <div className="grid gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Agent ID
            </label>
            <input
              type="text"
              value={agentId}
              onChange={(e) => setAgentId(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="default-agent"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              입력 텍스트
            </label>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              rows={5}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Agent에게 전달할 요청을 입력하세요."
            />
          </div>
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={syncMode}
              onChange={(e) => setSyncMode(e.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            동기 실행(즉시 결과 반환)
          </label>
          <div className="flex justify-end">
            <Button onClick={handleRun}>실행 요청</Button>
          </div>
        </div>
      </div>

      <div className="overflow-hidden rounded-xl bg-white shadow-sm">
        <div className="border-b px-6 py-3">
          <span className="text-sm text-gray-500">전체 {total}건</span>
        </div>
        {loading ? (
          <div className="p-6 text-center text-gray-400">로딩중...</div>
        ) : runs.length === 0 ? (
          <div className="p-6 text-center text-gray-400">
            실행 이력이 없습니다.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b bg-gray-50 text-xs uppercase text-gray-500">
                <tr>
                  <th className="px-6 py-3">Agent</th>
                  <th className="px-6 py-3">상태</th>
                  <th className="px-6 py-3">입력</th>
                  <th className="px-6 py-3">결과/오류</th>
                  <th className="px-6 py-3">생성일</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {runs.map((run) => (
                  <tr key={run.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900">
                      {run.agent_id}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          run.status === "succeeded"
                            ? "bg-green-100 text-green-700"
                            : run.status === "failed"
                              ? "bg-red-100 text-red-700"
                              : "bg-yellow-100 text-yellow-700"
                        }`}
                      >
                        {run.status}
                      </span>
                    </td>
                    <td className="max-w-xs truncate px-6 py-4 text-gray-600">
                      {run.input_text}
                    </td>
                    <td className="max-w-md truncate px-6 py-4 text-gray-600">
                      {run.output_text || run.error_message || "-"}
                    </td>
                    <td className="px-6 py-4 text-gray-500">
                      {run.created_at
                        ? new Date(run.created_at).toLocaleString("ko-KR")
                        : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

