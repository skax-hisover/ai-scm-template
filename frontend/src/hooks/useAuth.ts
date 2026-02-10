/**
 * 인증 커스텀 훅.
 *
 * [개발 표준]
 * - 컴포넌트에서 인증 관련 로직은 이 훅을 통해 사용하세요.
 */

"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { loginApi, getMeApi, type UserResponse } from "@/lib/api/auth";
import { setTokens, removeTokens, isAuthenticated } from "@/lib/auth/token";

export function useAuth() {
  const router = useRouter();
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);

  /** 현재 사용자 정보 로드 */
  const loadUser = useCallback(async () => {
    if (!isAuthenticated()) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const userData = await getMeApi();
      setUser(userData);
    } catch {
      removeTokens();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  /** 로그인 */
  const login = async (email: string, password: string) => {
    const tokens = await loginApi({ email, password });
    setTokens(tokens.access_token, tokens.refresh_token);
    await loadUser();
    router.push("/dashboard");
  };

  /** 로그아웃 */
  const logout = () => {
    removeTokens();
    setUser(null);
    router.push("/login");
  };

  return {
    user,
    loading,
    isLoggedIn: !!user,
    login,
    logout,
  };
}
