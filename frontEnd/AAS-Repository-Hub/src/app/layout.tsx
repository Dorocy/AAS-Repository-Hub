/*
 * 파일명: src/app/layout.tsx
 * 작성자: 김태훈
 * 작성일: 2024-03-15
 * 최종수정일: 2024-03-29
 *
 * 저작권: (c) 2025 IMPIX. 모든 권리 보유.
 *
 * 설명: Next.js 애플리케이션의 루트 레이아웃 컴포넌트입니다.
 * 이 컴포넌트는 전체 애플리케이션의 기본 HTML 구조를 정의하며,
 * 메타데이터, 파비콘, 글로벌 스타일시트 등을 설정합니다.
 */

import "@mantine/core/styles.css";
import "@mantine/dates/styles.css";
import "@mantine/dropzone/styles.css";
import "@mantine/spotlight/styles.css";
import "mantine-react-table/styles.css";

import { ColorSchemeScript, mantineHtmlProps } from "@mantine/core";

import "../styles/globals.css";
import ClientLayout from "../components/ClientLayout";
import { cookies } from "next/headers";
import { TokenProfile } from "@/types/auth";
import { getUserFromToken } from "@/utils";

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const tokenMessage = (await cookies()).get("token_message")?.value || "";

  let initialUser: TokenProfile | null = getUserFromToken(tokenMessage);

  return (
    <html className="h-full light" lang="en" {...mantineHtmlProps}>
      <head>
        <ColorSchemeScript />
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>KETI AAS Repository Hub</title>
        <meta name="description" content="KETI AAS Repository Hub" />
        <meta name="keywords" content="KETI, AAS" />
        <meta property="og:locale" content="en_US" />
        <meta property="og:type" content="article" />
        <meta property="og:title" content="KETI AAS Repository Hub" />
        <meta property="og:site_name" content="KETI AAS Repository Hub" />
        {/*favicon Start*/}
        <link
          rel="apple-touch-icon"
          sizes="57x57"
          href="/favicon/apple-icon-57x57.png"
        />
        <link
          rel="apple-touch-icon"
          sizes="60x60"
          href="/favicon/apple-icon-60x60.png"
        />
        <link
          rel="apple-touch-icon"
          sizes="72x72"
          href="/favicon/apple-icon-72x72.png"
        />
        <link
          rel="apple-touch-icon"
          sizes="76x76"
          href="/favicon/apple-icon-76x76.png"
        />
        <link
          rel="apple-touch-icon"
          sizes="114x114"
          href="/favicon/apple-icon-114x114.png"
        />
        <link
          rel="apple-touch-icon"
          sizes="120x120"
          href="/favicon/apple-icon-120x120.png"
        />
        <link
          rel="apple-touch-icon"
          sizes="144x144"
          href="/favicon/apple-icon-144x144.png"
        />
        <link
          rel="apple-touch-icon"
          sizes="152x152"
          href="/favicon/apple-icon-152x152.png"
        />
        <link
          rel="apple-touch-icon"
          sizes="180x180"
          href="/favicon/apple-icon-180x180.png"
        />
        <link
          rel="icon"
          type="image/png"
          sizes="192x192"
          // href="/favicon/android-icon-192x192.png"
        />
        <link
          rel="icon"
          type="image/png"
          sizes="32x32"
          href="/favicon/favicon-32x32.png"
        />
        <link
          rel="icon"
          type="image/png"
          sizes="96x96"
          href="/favicon/favicon-96x96.png"
        />
        <link
          rel="icon"
          type="image/png"
          sizes="16x16"
          href="/favicon/favicon-16x16.png"
        />
        <link rel="manifest" href="/favicon/manifest.json" />
        <meta name="msapplication-TileColor" content="#ffffff" />
        <meta name="msapplication-TileImage" content="/ms-icon-144x144.png" />
        <meta name="theme-color" content="#ffffff" />
        <link
          href="/assets/plugins/global/plugins.bundle.css"
          rel="stylesheet"
          type="text/css"
        />
        <link
          href="/assets/css/style.bundle.css"
          rel="stylesheet"
          type="text/css"
        />
      </head>
      <body className="header-fixed header-tablet-and-mobile-fixed toolbar-enabled">
        <div className="d-flex flex-column flex-root">
          {/* begin::Page */}
          <div className="page d-flex flex-row flex-column-fluid">
            {/* begin::Wrapper */}
            <div
              className="wrapper d-flex flex-column flex-row-fluid"
              id="kt_wrapper"
            >
              <div id="app"></div>
              <ClientLayout initialUser={initialUser}>{children}</ClientLayout>
            </div>
            {/* end::Wrapper */}
          </div>
          {/* end::Page */}
        </div>
        {/* <script>var hostUrl = "assets/";</script> */}
        {/* <!--begin::Global Javascript Bundle(mandatory for all pages)--> */}
        {/* <script src="/assets/plugins/global/plugins.bundle.js"></script> */}
        <script src="/assets/js/scripts.bundle.js"></script>
        {/* <!--end::Global Javascript Bundle--> */}
      </body>
    </html>
  );
}
