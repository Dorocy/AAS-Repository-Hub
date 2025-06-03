/*
 * 파일명: src/components/ProtectedRoute.tsx
 * 작성자: 김태훈
 * 작성일: 2024-03-15
 * 최종수정일: 2024-03-29
 * 
 * 저작권: (c) 2025 IMPIX. 모든 권리 보유.
 * 
 * 설명: 인증된 사용자만 접근할 수 있는 라우트를 보호하는 컴포넌트입니다.
 */

import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push(`/login?redirect=${encodeURIComponent(router.asPath)}`);
    }
  }, [isAuthenticated, loading, router]);

  if (loading) {
    return <div className="d-flex justify-content-center p-10">로딩 중...</div>;
  }

  return isAuthenticated ? <>{children}</> : null;
};

export default ProtectedRoute; 