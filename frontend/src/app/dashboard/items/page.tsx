"use client";

import { useEffect, useState } from "react";
import Button from "@/components/ui/Button";
import {
  getItemsApi,
  createItemApi,
  deleteItemApi,
  type Item,
} from "@/lib/api/items";

/**
 * 아이템 관리 페이지 (샘플 CRUD).
 *
 * [개발 표준]
 * - 새로운 비즈니스 페이지를 추가할 때 이 파일을 참고하세요.
 * - API 호출은 lib/api/ 의 함수를 사용합니다.
 */
export default function ItemsPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("");

  const loadItems = async () => {
    setLoading(true);
    try {
      const data = await getItemsApi();
      setItems(data.data);
      setTotal(data.total);
    } catch (err) {
      console.error("아이템 목록 조회 실패:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadItems();
  }, []);

  const handleCreate = async () => {
    if (!title.trim()) return;
    try {
      await createItemApi({ title: title.trim() });
      setTitle("");
      loadItems();
    } catch (err) {
      console.error("아이템 생성 실패:", err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("정말 삭제하시겠습니까?")) return;
    try {
      await deleteItemApi(id);
      loadItems();
    } catch (err) {
      console.error("아이템 삭제 실패:", err);
    }
  };

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-gray-900">아이템 관리</h1>

      {/* 생성 폼 */}
      <div className="mb-6 flex gap-3">
        <input
          type="text"
          placeholder="새 아이템 제목"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleCreate()}
          className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <Button onClick={handleCreate}>추가</Button>
      </div>

      {/* 목록 */}
      <div className="rounded-xl bg-white shadow-sm">
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
          <ul className="divide-y">
            {items.map((item) => (
              <li
                key={item.id}
                className="flex items-center justify-between px-6 py-4"
              >
                <div>
                  <p className="font-medium text-gray-900">{item.title}</p>
                  <p className="text-xs text-gray-400">
                    {item.created_at
                      ? new Date(item.created_at).toLocaleDateString("ko-KR")
                      : ""}
                  </p>
                </div>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => handleDelete(item.id)}
                >
                  삭제
                </Button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
