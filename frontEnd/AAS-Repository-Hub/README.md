# 프로젝트 구조

```
/
├── public/           # 정적 리소스 디렉토리
│   ├── favicon/      # 파비콘 및 아이콘 관련 파일
│   │   ├── manifest.json      # PWA 매니페스트 파일
│   │   ├── browserconfig.xml  # Microsoft 브라우저 설정
│   │   ├── favicon.ico        # 기본 파비콘
│   │   ├── favicon-16x16.png  # 16x16 파비콘
│   │   ├── favicon-32x32.png  # 32x32 파비콘
│   │   ├── favicon-96x96.png  # 96x96 파비콘
│   │   ├── apple-icon-*.png   # Apple 기기용 아이콘 (다양한 크기)
│   │   ├── android-icon-*.png # Android 기기용 아이콘 (다양한 크기)
│   │   └── ms-icon-*.png      # Microsoft 기기용 아이콘 (다양한 크기)
├── src/              # 소스 코드 디렉토리
│   ├── app/          # Next.js 13+ App Router
│   │   ├── layout.tsx        # 루트 레이아웃
│   │   ├── page.tsx          # 메인 페이지
│   │   ├── about/            # 소개 페이지
│   │   │   └── page.tsx      # 소개 페이지 컴포넌트
│   │   ├── user/             # 사용자 관련 페이지
│   │   │   ├── page.tsx      # 사용자 목록
│   │   │   ├── edit/[id]/page.tsx # 사용자 수정 (동적 라우트)
│   │   │   └── ins/page.tsx  # 사용자 등록
│   │   ├── submodel/         # 서브모델 관련 페이지
│   │   │   ├── page.tsx      # 서브모델 목록
│   │   │   ├── edit/[id]/page.tsx # 서브모델 수정 (동적 라우트)
│   │   │   ├── view/[id]/page.tsx # 서브모델 상세 (동적 라우트)
│   │   │   └── ins/page.tsx  # 서브모델 등록
│   │   ├── instance/         # 인스턴스 관련 페이지
│   │   │   ├── page.tsx      # 인스턴스 목록
│   │   │   ├── view/[id]/page.tsx # 인스턴스 상세 (동적 라우트)
│   │   │   ├── ins/page.tsx  # 인스턴스 등록
│   │   │   └── server/page.tsx # 서버 관리
│   │   ├── distribute/       # 배포 관련 페이지
│   │   │   ├── page.tsx      # 배포 목록
│   │   │   ├── edit/[id]/page.tsx # 배포 수정 (동적 라우트)
│   │   │   ├── view/[id]/page.tsx # 배포 상세 (동적 라우트)
│   │   │   └── ins/page.tsx  # 배포 등록
│   │   ├── aas/              # AAS 관련 페이지
│   │   │   ├── page.tsx      # AAS 목록
│   │   │   ├── edit/[id]/page.tsx # AAS 수정 (동적 라우트)
│   │   │   ├── view/[id]/page.tsx # AAS 상세 (동적 라우트)
│   │   │   └── ins/page.tsx  # AAS 등록
│   │   ├── test/             # 테스트 페이지
│   │   │   └── login/page.tsx # 로그인 테스트
│   │   ├── sample/           # 샘플 페이지
│   │   │   └── page.tsx      # 샘플 페이지 컴포넌트
│   │   └── api/              # API 라우트
│   ├── components/   # 재사용 가능한 컴포넌트
│   │   ├── GlobalInit.tsx    # 전역 초기화 컴포넌트
│   │   ├── Header.tsx        # 헤더 컴포넌트
│   │   ├── Footer.tsx        # 푸터 컴포넌트
│   │   ├── ProtectedRoute.tsx # 보호된 라우트 컴포넌트
│   │   └── ClientLayout.tsx  # 클라이언트 레이아웃 컴포넌트
│   ├── contexts/     # React Context 관련 파일
│   ├── hooks/        # 커스텀 React Hooks
│   ├── metronic/     # Metronic UI 컴포넌트
│   └── styles/       # 스타일 관련 파일
│       ├── globals.css       # 전역 스타일 (Next.js 기본 스타일)
│       └── webfont.css       # 웹 폰트 설정 (Pretendard)
├── node_modules/     # 프로젝트 의존성 패키지
├── next.config.mjs   # Next.js 설정
├── next.config.ts    # Next.js TypeScript 설정
├── next-env.d.ts     # Next.js TypeScript 타입 정의
├── package.json      # 프로젝트 설정 및 의존성
├── postcss.config.mjs # PostCSS 설정
├── tailwind.config.js # Tailwind CSS 설정
└── tsconfig.json     # TypeScript 설정
```

## 기술 스택

- Next.js 15+ (App Router)
- React 19
- TypeScript
- Tailwind CSS
- Metronic UI
- Mantine

## 스타일 관련

- **globals.css**: Next.js의 전역 스타일 파일로, 기본 스타일과 레이아웃 설정을 포함
- **webfont.css**: Pretendard 웹 폰트를 적용하는 스타일 파일로, CDN을 통해 폰트를 로드

## 파비콘 및 아이콘

- **manifest.json**: PWA(Progressive Web App) 매니페스트 파일
- **browserconfig.xml**: Microsoft 브라우저에서 사용되는 타일 설정
- **아이콘 파일들**: 다양한 기기와 브라우저에서 사용되는 아이콘 파일
  - favicon.ico: 기본 파비콘
  - favicon-*.png: 일반 브라우저용 파비콘
  - apple-icon-*.png: Apple 기기용 아이콘
  - android-icon-*.png: Android 기기용 아이콘
  - ms-icon-*.png: Microsoft 기기용 아이콘

## 배포
### 로컬에서 배포
deployWithNginx.sh 파일 운영서버 접속 정보 수정
```sh
USER="root" # 사용자 ID
HOST="192.168.100.46" # 서버 IP
TARGET_DIR="/home/aas/aas_nextjs" # 소스 저장 경로
```

### 운영서버에서 배포
1. 소스 저장 경로 이동
2. 이미지 생성 후 실행
docker compose up --build -d