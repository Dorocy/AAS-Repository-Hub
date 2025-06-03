import { NextRequest, NextResponse } from "next/server";
import type { AuthTokenData } from "@/types/auth";

// POST /api/login
// 클라이언트로부터 전달받은 token 정보를 HttpOnly 쿠키로 설정
export async function POST(req: NextRequest) {
  // 요청 본문에서 token 객체 추출 (타입은 AuthTokenData)
  const { token }: { token: AuthTokenData } = await req.json();

  // JSON 응답 객체 생성
  const response = NextResponse.json({ success: true });

  // HttpOnly 쿠키로 JWT token_message 저장
  // - httpOnly: JS에서 접근 불가 (보안)
  // - secure: HTTPS에서만 동작
  // - sameSite: lax로 CSRF 방어
  // - path: 모든 경로에 대해 전송됨
  response.cookies.set("token_message", JSON.stringify(token), {
    path: "/",
    httpOnly: true,
    secure: true, // 서버가 https 사용하는 경우만 True
    sameSite: "lax", // 같은 도메인일 경우, 다른 도메인은 GET 요청만 쿠키 전송 가능
  });

  // 응답 반환
  return response;
}
