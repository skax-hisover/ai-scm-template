"use client";

import { useEffect, useState, useCallback } from "react";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import {
  getUsersApi,
  createUserApi,
  updateUserApi,
  deleteUserApi,
  type User,
  type UserCreateRequest,
  type UserUpdateRequest,
} from "@/lib/api/users";

/**
 * 사용자 관리 페이지 (관리자 전용).
 *
 * [기능]
 * - 사용자 목록 조회
 * - 사용자 생성 (모달)
 * - 사용자 수정 (모달)
 * - 사용자 삭제
 */
export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 성공 메시지 (토스트)
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // 모달 상태
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

  // 생성 폼
  const [createForm, setCreateForm] = useState<UserCreateRequest>({
    email: "",
    password: "",
    full_name: "",
    is_active: true,
    is_superuser: false,
  });
  const [createError, setCreateError] = useState<string | null>(null);

  // 수정 폼
  const [updateForm, setUpdateForm] = useState<UserUpdateRequest>({});
  const [updateError, setUpdateError] = useState<string | null>(null);

  // ─── 성공 메시지 표시 (3초 후 자동 사라짐) ─────────────────

  const showSuccess = useCallback((message: string) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(null), 3000);
  }, []);

  // ─── 데이터 로드 ─────────────────────────────────────────

  const loadUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getUsersApi();
      setUsers(data.data);
      setTotal(data.total);
    } catch (err) {
      console.error("사용자 목록 조회 실패:", err);
      setError("사용자 목록을 불러오는데 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  // ─── 생성 ────────────────────────────────────────────────

  const handleOpenCreate = () => {
    setCreateForm({
      email: "",
      password: "",
      full_name: "",
      is_active: true,
      is_superuser: false,
    });
    setCreateError(null);
    setShowCreateModal(true);
  };

  const handleCreate = async () => {
    if (!createForm.email.trim() || !createForm.password.trim()) {
      setCreateError("이메일과 비밀번호는 필수입니다.");
      return;
    }
    if (createForm.password.length < 8) {
      setCreateError("비밀번호는 8자 이상이어야 합니다.");
      return;
    }
    if (!confirm("사용자를 생성하시겠습니까?")) return;
    setCreateError(null);
    try {
      await createUserApi(createForm);
      setShowCreateModal(false);
      showSuccess("사용자가 성공적으로 생성되었습니다.");
      loadUsers();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const detail = error?.response?.data?.detail;
      setCreateError(detail || "사용자 생성에 실패했습니다.");
    }
  };

  // ─── 수정 ────────────────────────────────────────────────

  const handleOpenEdit = (user: User) => {
    setEditingUser(user);
    setUpdateForm({
      email: user.email,
      full_name: user.full_name || "",
      is_active: user.is_active,
      is_superuser: user.is_superuser,
    });
    setUpdateError(null);
  };

  const handleUpdate = async () => {
    if (!editingUser) return;
    if (!confirm("사용자 정보를 수정하시겠습니까?")) return;
    setUpdateError(null);
    try {
      // 비밀번호가 비어있으면 전송하지 않음
      const payload: UserUpdateRequest = { ...updateForm };
      if (!payload.password) {
        delete payload.password;
      }
      await updateUserApi(editingUser.id, payload);
      setEditingUser(null);
      showSuccess("사용자 정보가 성공적으로 수정되었습니다.");
      loadUsers();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const detail = error?.response?.data?.detail;
      setUpdateError(detail || "사용자 수정에 실패했습니다.");
    }
  };

  // ─── 삭제 ────────────────────────────────────────────────

  const handleDelete = async (id: string) => {
    if (!confirm("정말 이 사용자를 삭제하시겠습니까?\n삭제된 데이터는 복구할 수 없습니다.")) return;
    try {
      await deleteUserApi(id);
      showSuccess("사용자가 성공적으로 삭제되었습니다.");
      loadUsers();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const detail = error?.response?.data?.detail;
      alert(detail || "사용자 삭제에 실패했습니다.");
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
        <h1 className="text-2xl font-bold text-gray-900">사용자 관리</h1>
        <Button onClick={handleOpenCreate}>+ 사용자 추가</Button>
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="mb-4 rounded-lg bg-red-50 p-4 text-sm text-red-600">
          {error}
        </div>
      )}

      {/* 사용자 목록 테이블 */}
      <div className="overflow-hidden rounded-xl bg-white shadow-sm">
        <div className="border-b px-6 py-3">
          <span className="text-sm text-gray-500">전체 {total}명</span>
        </div>

        {loading ? (
          <div className="p-6 text-center text-gray-400">로딩중...</div>
        ) : users.length === 0 ? (
          <div className="p-6 text-center text-gray-400">
            등록된 사용자가 없습니다.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b bg-gray-50 text-xs uppercase text-gray-500">
                <tr>
                  <th className="px-6 py-3">이메일</th>
                  <th className="px-6 py-3">이름</th>
                  <th className="px-6 py-3 text-center">상태</th>
                  <th className="px-6 py-3 text-center">권한</th>
                  <th className="px-6 py-3">가입일</th>
                  <th className="px-6 py-3 text-center">관리</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900">
                      {user.email}
                    </td>
                    <td className="px-6 py-4 text-gray-600">
                      {user.full_name || "-"}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span
                        className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          user.is_active
                            ? "bg-green-100 text-green-700"
                            : "bg-red-100 text-red-700"
                        }`}
                      >
                        {user.is_active ? "활성" : "비활성"}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span
                        className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${
                          user.is_superuser
                            ? "bg-purple-100 text-purple-700"
                            : "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {user.is_superuser ? "관리자" : "일반"}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-500">
                      {user.created_at
                        ? new Date(user.created_at).toLocaleDateString("ko-KR")
                        : "-"}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleOpenEdit(user)}
                        >
                          수정
                        </Button>
                        <Button
                          variant="danger"
                          size="sm"
                          onClick={() => handleDelete(user.id)}
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

      {/* ─── 생성 모달 ─── */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h2 className="mb-4 text-lg font-bold text-gray-900">
              사용자 추가
            </h2>

            {createError && (
              <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
                {createError}
              </div>
            )}

            <div className="space-y-4">
              <Input
                label="이메일 *"
                type="email"
                placeholder="user@example.com"
                value={createForm.email}
                onChange={(e) =>
                  setCreateForm({ ...createForm, email: e.target.value })
                }
              />
              <Input
                label="비밀번호 *"
                type="password"
                placeholder="8자 이상"
                value={createForm.password}
                onChange={(e) =>
                  setCreateForm({ ...createForm, password: e.target.value })
                }
              />
              <Input
                label="이름"
                type="text"
                placeholder="홍길동"
                value={createForm.full_name || ""}
                onChange={(e) =>
                  setCreateForm({ ...createForm, full_name: e.target.value })
                }
              />
              <div className="flex items-center gap-6">
                <label className="flex items-center gap-2 text-sm text-gray-700">
                  <input
                    type="checkbox"
                    checked={createForm.is_active}
                    onChange={(e) =>
                      setCreateForm({
                        ...createForm,
                        is_active: e.target.checked,
                      })
                    }
                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  활성 상태
                </label>
                <label className="flex items-center gap-2 text-sm text-gray-700">
                  <input
                    type="checkbox"
                    checked={createForm.is_superuser}
                    onChange={(e) =>
                      setCreateForm({
                        ...createForm,
                        is_superuser: e.target.checked,
                      })
                    }
                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  관리자 권한
                </label>
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
      {editingUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h2 className="mb-4 text-lg font-bold text-gray-900">
              사용자 수정
            </h2>

            {updateError && (
              <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600">
                {updateError}
              </div>
            )}

            <div className="space-y-4">
              <Input
                label="이메일"
                type="email"
                value={updateForm.email || ""}
                onChange={(e) =>
                  setUpdateForm({ ...updateForm, email: e.target.value })
                }
              />
              <Input
                label="새 비밀번호 (변경 시에만 입력)"
                type="password"
                placeholder="8자 이상"
                value={updateForm.password || ""}
                onChange={(e) =>
                  setUpdateForm({ ...updateForm, password: e.target.value })
                }
              />
              <Input
                label="이름"
                type="text"
                placeholder="홍길동"
                value={updateForm.full_name || ""}
                onChange={(e) =>
                  setUpdateForm({ ...updateForm, full_name: e.target.value })
                }
              />
              <div className="flex items-center gap-6">
                <label className="flex items-center gap-2 text-sm text-gray-700">
                  <input
                    type="checkbox"
                    checked={updateForm.is_active ?? true}
                    onChange={(e) =>
                      setUpdateForm({
                        ...updateForm,
                        is_active: e.target.checked,
                      })
                    }
                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  활성 상태
                </label>
                <label className="flex items-center gap-2 text-sm text-gray-700">
                  <input
                    type="checkbox"
                    checked={updateForm.is_superuser ?? false}
                    onChange={(e) =>
                      setUpdateForm({
                        ...updateForm,
                        is_superuser: e.target.checked,
                      })
                    }
                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  관리자 권한
                </label>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <Button
                variant="secondary"
                onClick={() => setEditingUser(null)}
              >
                취소
              </Button>
              <Button onClick={handleUpdate}>저장</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
