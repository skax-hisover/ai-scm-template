"use client";

import { useEffect, useState, useCallback } from "react";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import {
  getItemsApi,
  getItemApi,
  createItemApi,
  updateItemApi,
  deleteItemApi,
  type Item,
  type ItemCreateRequest,
  type ItemUpdateRequest,
} from "@/lib/api/items";

/**
 * 아이템 관리 페이지 (전체 CRUD).
 *
 * [기능]
 * - 아이템 목록 조회 (테이블)
 * - 아이템 상세 조회 (모달)
 * - 아이템 생성 (모달)
 * - 아이템 수정 (모달)
 * - 아이템 삭제
 */
export default function ItemsPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 성공 메시지 (토스트)
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // 모달 상태
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingItem, setEditingItem] = useState<Item | null>(null);
  const [viewingItem, setViewingItem] = useState<Item | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // 생성 폼
  const [createForm, setCreateForm] = useState<ItemCreateRequest>({
    title: "",
    description: "",
  });
  const [createError, setCreateError] = useState<string | null>(null);

  // 수정 폼
  const [updateForm, setUpdateForm] = useState<ItemUpdateRequest>({});
  const [updateError, setUpdateError] = useState<string | null>(null);

  // ─── 성공 메시지 표시 (3초 후 자동 사라짐) ─────────────────

  const showSuccess = useCallback((message: string) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(null), 3000);
  }, []);

  // ─── 데이터 로드 ─────────────────────────────────────────

  const loadItems = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getItemsApi();
      setItems(data.data);
      setTotal(data.total);
    } catch (err) {
      console.error("아이템 목록 조회 실패:", err);
      setError("아이템 목록을 불러오는데 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadItems();
  }, []);

  // ─── 상세 조회 ───────────────────────────────────────────

  const handleView = async (id: string) => {
    setDetailLoading(true);
    try {
      const item = await getItemApi(id);
      setViewingItem(item);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const detail = error?.response?.data?.detail;
      alert(detail || "아이템 상세 조회에 실패했습니다.");
    } finally {
      setDetailLoading(false);
    }
  };

  // ─── 생성 ────────────────────────────────────────────────

  const handleOpenCreate = () => {
    setCreateForm({ title: "", description: "" });
    setCreateError(null);
    setShowCreateModal(true);
  };

  const handleCreate = async () => {
    if (!createForm.title.trim()) {
      setCreateError("제목은 필수입니다.");
      return;
    }
    if (!confirm("아이템을 생성하시겠습니까?")) return;
    setCreateError(null);
    try {
      await createItemApi({
        title: createForm.title.trim(),
        description: createForm.description?.trim() || undefined,
      });
      setShowCreateModal(false);
      showSuccess("아이템이 성공적으로 생성되었습니다.");
      loadItems();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const detail = error?.response?.data?.detail;
      setCreateError(detail || "아이템 생성에 실패했습니다.");
    }
  };

  // ─── 수정 ────────────────────────────────────────────────

  const handleOpenEdit = (item: Item) => {
    setEditingItem(item);
    setUpdateForm({
      title: item.title,
      description: item.description || "",
    });
    setUpdateError(null);
  };

  const handleUpdate = async () => {
    if (!editingItem) return;
    if (!updateForm.title?.trim()) {
      setUpdateError("제목은 필수입니다.");
      return;
    }
    if (!confirm("아이템을 수정하시겠습니까?")) return;
    setUpdateError(null);
    try {
      await updateItemApi(editingItem.id, {
        title: updateForm.title?.trim(),
        description: updateForm.description?.trim() || undefined,
      });
      setEditingItem(null);
      showSuccess("아이템이 성공적으로 수정되었습니다.");
      loadItems();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const detail = error?.response?.data?.detail;
      setUpdateError(detail || "아이템 수정에 실패했습니다.");
    }
  };

  // ─── 삭제 ────────────────────────────────────────────────

  const handleDelete = async (id: string) => {
    if (!confirm("정말 이 아이템을 삭제하시겠습니까?\n삭제된 데이터는 복구할 수 없습니다.")) return;
    try {
      await deleteItemApi(id);
      showSuccess("아이템이 성공적으로 삭제되었습니다.");
      loadItems();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const detail = error?.response?.data?.detail;
      alert(detail || "아이템 삭제에 실패했습니다.");
    }
  };

  // ─── 렌더링 ──────────────────────────────────────────────

  return (
    <div>
      {/* 성공 메시지 토스트 */}
      {successMessage && (
        <div className="fixed right-6 top-6 z-[60] animate-fade-in rounded-lg bg-green-50 border border-green-200 px-5 py-3 shadow-lg">
          <div className="flex items-center gap-2">
            <span className="text-green-500 text-lg">✓</span>
            <p className="text-sm font-medium text-green-700">{successMessage}</p>
            <button
              onClick={() => setSuccessMessage(null)}
              className="ml-3 text-green-400 hover:text-green-600"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* 헤더 */}
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">아이템 관리</h1>
        <Button onClick={handleOpenCreate}>+ 아이템 추가</Button>
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="mb-4 rounded-lg bg-red-50 p-4 text-sm text-red-600">
          {error}
        </div>
      )}

      {/* 아이템 목록 테이블 */}
      <div className="overflow-hidden rounded-xl bg-white shadow-sm">
        <div className="border-b px-6 py-3">
          <span className="text-sm text-gray-500">전체 {total}건</span>
        </div>

        {loading ? (
          <div className="p-6 text-center text-gray-400">로딩중...</div>
        ) : items.length === 0 ? (
          <div className="p-6 text-center text-gray-400">
            아이템이 없습니다.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b bg-gray-50 text-xs uppercase text-gray-500">
                <tr>
                  <th className="px-6 py-3">제목</th>
                  <th className="px-6 py-3">설명</th>
                  <th className="px-6 py-3">생성일</th>
                  <th className="px-6 py-3">수정일</th>
                  <th className="px-6 py-3 text-center">관리</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {items.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <button
                        onClick={() => handleView(item.id)}
                        className="font-medium text-blue-600 hover:text-blue-800 hover:underline"
                      >
                        {item.title}
                      </button>
                    </td>
                    <td className="max-w-xs truncate px-6 py-4 text-gray-600">
                      {item.description || "-"}
                    </td>
                    <td className="px-6 py-4 text-gray-500">
                      {item.created_at
                        ? new Date(item.created_at).toLocaleDateString("ko-KR")
                        : "-"}
                    </td>
                    <td className="px-6 py-4 text-gray-500">
                      {item.updated_at
                        ? new Date(item.updated_at).toLocaleDateString("ko-KR")
                        : "-"}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleOpenEdit(item)}
                        >
                          수정
                        </Button>
                        <Button
                          variant="danger"
                          size="sm"
                          onClick={() => handleDelete(item.id)}
                        >
                          삭제
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ─── 상세 조회 모달 ─── */}
      {viewingItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">
            <h2 className="mb-4 text-lg font-bold text-gray-900">
              아이템 상세
            </h2>

            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-500">
                  제목
                </label>
                <p className="text-gray-900">{viewingItem.title}</p>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-500">
                  설명
                </label>
                <p className="whitespace-pre-wrap text-gray-900">
                  {viewingItem.description || "-"}
                </p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-500">
                    생성일
                  </label>
                  <p className="text-gray-900">
                    {viewingItem.created_at
                      ? new Date(viewingItem.created_at).toLocaleString("ko-KR")
                      : "-"}
                  </p>
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-gray-500">
                    수정일
                  </label>
                  <p className="text-gray-900">
                    {viewingItem.updated_at
                      ? new Date(viewingItem.updated_at).toLocaleString("ko-KR")
                      : "-"}
                  </p>
                </div>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-500">
                  ID
                </label>
                <p className="font-mono text-xs text-gray-500">
                  {viewingItem.id}
                </p>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <Button
                variant="ghost"
                onClick={() => {
                  handleOpenEdit(viewingItem);
                  setViewingItem(null);
                }}
              >
                수정
              </Button>
              <Button
                variant="secondary"
                onClick={() => setViewingItem(null)}
              >
                닫기
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* ─── 생성 모달 ─── */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h2 className="mb-4 text-lg font-bold text-gray-900">
              아이템 추가
            </h2>

            {createError && (
              <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
                {createError}
              </div>
            )}

            <div className="space-y-4">
              <Input
                label="제목 *"
                type="text"
                placeholder="아이템 제목을 입력하세요"
                value={createForm.title}
                onChange={(e) =>
                  setCreateForm({ ...createForm, title: e.target.value })
                }
              />
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  설명
                </label>
                <textarea
                  placeholder="아이템에 대한 설명을 입력하세요 (선택)"
                  value={createForm.description || ""}
                  onChange={(e) =>
                    setCreateForm({
                      ...createForm,
                      description: e.target.value,
                    })
                  }
                  rows={4}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm transition-colors focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <Button
                variant="secondary"
                onClick={() => setShowCreateModal(false)}
              >
                취소
              </Button>
              <Button onClick={handleCreate}>생성</Button>
            </div>
          </div>
        </div>
      )}

      {/* ─── 수정 모달 ─── */}
      {editingItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h2 className="mb-4 text-lg font-bold text-gray-900">
              아이템 수정
            </h2>

            {updateError && (
              <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
                {updateError}
              </div>
            )}

            <div className="space-y-4">
              <Input
                label="제목 *"
                type="text"
                placeholder="아이템 제목을 입력하세요"
                value={updateForm.title || ""}
                onChange={(e) =>
                  setUpdateForm({ ...updateForm, title: e.target.value })
                }
              />
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  설명
                </label>
                <textarea
                  placeholder="아이템에 대한 설명을 입력하세요 (선택)"
                  value={updateForm.description || ""}
                  onChange={(e) =>
                    setUpdateForm({
                      ...updateForm,
                      description: e.target.value,
                    })
                  }
                  rows={4}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm transition-colors focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <Button
                variant="secondary"
                onClick={() => setEditingItem(null)}
              >
                취소
              </Button>
              <Button onClick={handleUpdate}>저장</Button>
            </div>
          </div>
        </div>
      )}

      {/* 상세 조회 로딩 오버레이 */}
      {detailLoading && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
          <div className="rounded-lg bg-white px-6 py-4 shadow-lg">
            <p className="text-sm text-gray-600">로딩중...</p>
          </div>
        </div>
      )}
    </div>
  );
}
