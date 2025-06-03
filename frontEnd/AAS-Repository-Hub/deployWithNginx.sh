#!/bin/bash

# ===============================
# 📦 Next.js Docker 배포 자동화 스크립트
# ===============================

# 로컬
# USER="one"
# HOST="localhost"
# TARGET_DIR="/Users/one/deploytest"
# COMPOSE_CMD="docker-compose"

# 운영
USER="root"
HOST="192.168.100.46"
TARGET_DIR="/home/datalake/aas_nextjs"
COMPOSE_CMD="docker compose"

EXCLUDES="--exclude=node_modules --exclude=.next --exclude=.git --exclude=*.tar.gz"

PROJECT_NAME="aas-front"
IMAGE_NAME="aas-front"
IMAGE_TAG="latest"


# ✅ 소스 코드 동기화
echo "📤 서버에 소스 코드 동기화 중..."
rsync -avz --delete $EXCLUDES ./ $USER@$HOST:$TARGET_DIR/


# ✅ 이전 컨테이너 정리 준비
echo "🧹 이전 컨테이너/이미지 정리 중..."
CONTAINERS=$(docker ps -a --filter "ancestor=${IMAGE_NAME}:${IMAGE_TAG}" --format "{{.ID}}")

if [ -n "$CONTAINERS" ]; then
  for CONTAINER_ID in $CONTAINERS; do
    # ✅ 컨테이너 중지 및 삭제
    echo "🛑 컨테이너 정리: $CONTAINER_ID"
    docker stop "$CONTAINER_ID"
    docker rm "$CONTAINER_ID"
  done
else
  echo "✅ 연결된 이전 컨테이너 없음"
fi

# ✅ 이전 이미지 삭제
LATEST_IMAGE_ID=$(docker images --format "{{.Repository}}:{{.Tag}} {{.ID}}" | grep "^${IMAGE_NAME}:${IMAGE_TAG}" | head -n1 | awk '{print $2}')
if [ -n "$LATEST_IMAGE_ID" ]; then
  echo "🗑️ 이전 이미지 삭제: $LATEST_IMAGE_ID"
  docker rmi $LATEST_IMAGE_ID
else
  echo "✅ 삭제할 이전 이미지 없음"
fi

# ✅ 서버에서 docker compose 실행
echo "🚀 서버에서 빌드 및 재시작..."
ssh -t $USER@$HOST <<EOF
  cd $TARGET_DIR
  $COMPOSE_CMD down || true
  $COMPOSE_CMD build
  $COMPOSE_CMD up -d
EOF

echo "✅ 배포 완료! 접속 주소: http://$HOST"
