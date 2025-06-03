// src/providers/AuthProvider.tsx
"use client";

import React, { createContext, useState, useContext, useEffect } from "react";
import { useRouter, usePathname, redirect } from "next/navigation";
import { ROUTES, PROTECTED_ROUTES, canAccessPath } from "@/constants/routes";
import type { TokenProfile } from "@/types/auth";
import { showToast } from "@/utils/toast";
import { signUp, loginWithCredentials } from "@/api";
import { getUserFromToken } from "@/utils";

interface AuthContextType {
  user: TokenProfile | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loginWithSocial: (social: "google" | "naver") => void;
  signUpWithCredential: (email: string, password: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({
  initialUser,
  children,
}: {
  initialUser: TokenProfile | null;
  children: React.ReactNode;
}) => {
  const [user, setUser] = useState<TokenProfile | null>(initialUser);
  const router = useRouter();
  const pathname = usePathname();

  const isAuthenticated = !!user;
  const allowRender = canAccessPath(pathname, user?.user_group_seq);

  // 로그인 함수 (서버에 토큰 전달)
  const login = async (email: string, password: string) => {
    const token = await loginWithCredentials(email, password);
    await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    });

    setUser(getUserFromToken(token));
    router.replace(ROUTES.HOME);
  };

  // 로그아웃 함수 (서버에 쿠키 삭제 요청)
  const logout = async () => {
    await fetch("/api/logout", { method: "POST" });
    setUser(null);
    router.push(ROUTES.LOGIN);
  };

  // 소셜 로그인 (팝업으로 열기)
  const loginWithSocial = (social: "google" | "naver") => {
    const left = window.screen.width / 2 - 800 / 2;
    const top = window.screen.height / 2 - 600 / 2;
    const socialUrl = `${process.env.NEXT_PUBLIC_AAS_API_BASE}:${process.env.NEXT_PUBLIC_AAS_API_PORT}/${social}/login`;

    window.open(
      socialUrl,
      "_blank",
      `width=800,height=600,left=${left},top=${top}`
    );
  };

  // postMessage로 소셜 토큰 받아서 처리
  useEffect(() => {
    const loginMessage = (event: MessageEvent) => {
      if (event.data?.type === "login") {
        const token = event.data.token;
        if (!token) return;

        fetch("/api/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token }),
        }).then(() => {
          setUser(getUserFromToken(token));
          router.replace(ROUTES.HOME);
        });
      }
    };

    window.addEventListener("message", loginMessage);
    return () => window.removeEventListener("message", loginMessage);
  }, []);

  // 회원가입
  const signUpWithCredential = async (email: string, password: string) => {
    try {
      await signUp(email, password);
      router.replace(ROUTES.LOGIN);
    } catch (error) {}
  };

  // 권한 미충족 시 리디렉션
  useEffect(() => {
    // console.log({ user, pathname, isAuthenticated, allowRender });

    // 로그인한 경우 메인페이지 이동
    if (pathname === ROUTES.LOGIN && isAuthenticated) {
      router.replace(ROUTES.HOME);
    }

    if (allowRender === "forbidden" && pathname !== ROUTES.UNAUTHORIZED) {
      router.replace(ROUTES.UNAUTHORIZED);
    }

    if (allowRender === "allow") return;

    if (!isAuthenticated) {
      const protectedRoute = PROTECTED_ROUTES.find(
        ({ path }) => path === pathname
      );
      if (protectedRoute && pathname !== ROUTES.LOGIN) {
        router.replace(ROUTES.LOGIN);
      }
    }
  }, [pathname, isAuthenticated, allowRender]);

  // console.log({ user, allowRender, pathname, isAuthenticated });

  if (pathname === ROUTES.LOGIN && isAuthenticated) {
    return null;
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        login,
        logout,
        loginWithSocial,
        signUpWithCredential,
      }}
    >
      {allowRender === "allow" && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
};
