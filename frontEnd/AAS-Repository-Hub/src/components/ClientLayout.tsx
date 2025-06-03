/*
 * 파일명: src/components/ClientLayout.tsx
 * 작성자: 김태훈
 * 작성일: 2024-03-15
 * 최종수정일: 2024-03-29
 *
 * 저작권: (c) 2025 IMPIX. 모든 권리 보유.
 *
 * 설명: 애플리케이션의 기본 레이아웃을 구성하는 컴포넌트입니다.
 */

"use client";

import {
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import { ModalsProvider } from "@mantine/modals";
import toast, { Toaster } from "react-hot-toast";
import { showToast } from "@/utils/toast";

import { ReactQueryDevtools } from "@tanstack/react-query-devtools";

import Footer from "./Footer";
import Header from "./Header";
import { AuthProvider } from "../contexts/AuthContext";
import { MantineProvider } from "@mantine/core";
import { usePathname, useRouter } from "next/navigation";
import { ROUTES } from "@/constants/routes";
import { TokenProfile } from "@/types/auth";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 0,
      retry: false,
      refetchOnMount: false,
      refetchOnWindowFocus: false,
      gcTime: 0,
    },
  },
  queryCache: new QueryCache({
    onError: (error, query) => {
      if (query.state.status === "error") {
        showToast.error(`오류가 발생했습니다 ➡️ ${error.message}`);
      }
    },
  }),
});

export default function ClientLayout({
  initialUser,
  children,
}: {
  initialUser: TokenProfile | null;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  return (
    <QueryClientProvider client={queryClient}>
      <MantineProvider>
        <ModalsProvider>
          <AuthProvider initialUser={initialUser}>
            <>
              {![ROUTES.LOGIN, ROUTES.SIGNUP, ROUTES.RESET_PASSWORD].includes(
                pathname
              ) && <Header />}
              {children}
              {![ROUTES.LOGIN, ROUTES.SIGNUP, ROUTES.RESET_PASSWORD].includes(
                pathname
              ) && <Footer />}
            </>
          </AuthProvider>
          <Toaster
            position="top-center"
            containerStyle={{
              marginTop: "8rem",
            }}
            reverseOrder={false}
          />
        </ModalsProvider>
      </MantineProvider>
      <ReactQueryDevtools />
    </QueryClientProvider>
  );
}
