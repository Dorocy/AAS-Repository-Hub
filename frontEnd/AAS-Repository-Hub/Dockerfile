# ✅ 1단계: 빌드 이미지
FROM node:23-alpine AS builder

WORKDIR /app

# 🔑 의존성 파일만 먼저 복사
COPY package.json yarn.lock ./

# ✅ 의존성 설치 (개발용 포함)
RUN yarn install --network-timeout 600000 --frozen-lockfile

# 🔄 필요한 파일만 복사 (불필요한 것 제거를 위해 .dockerignore도 꼭 설정)
COPY . .

# ✅ Next.js 프로덕션 빌드
RUN yarn build


# ✅ 2단계: 실행 이미지
FROM node:23-alpine AS runner

WORKDIR /app

# 🧊 시스템 루트 CA 인증서 설치
RUN apk add --no-cache ca-certificates && update-ca-certificates

# 🧼 의존성 최소화 (필수 러UNTIME only)
COPY package.json yarn.lock ./
RUN yarn install --network-timeout 600000 --frozen-lockfile --production

# ✅ 빌드 산출물만 복사
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.mjs ./next.config.mjs

# ✅ 환경 변수 설정
ENV NODE_ENV=production
EXPOSE 3000

# ✅ 실행
CMD ["yarn", "start"]
