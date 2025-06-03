#!/bin/bash

# ===============================
# 📦 Next.js Docker 배포 자동화 스크립트
# ===============================

USER="one"
HOST="localhost"
TARGET_DIR="/Users/one/deploytest"
EXCLUDES="--exclude=node_modules --exclude=.next --exclude=.git --exclude=*.tar.gz"

PROJECT_NAME="aas-front"
IMAGE_NAME="aas-front"
IMAGE_TAG="latest"

NETWORK_NAME="bridge_aas-front"
NGINX_CONTAINER_NAME="nginx"

# ✅ Docker Compose 명령 자동 감지
if docker compose version > /dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
elif docker-compose version > /dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
else
  echo "❌ Docker Compose 명령어가 없습니다."
  exit 1
fi

# ✅ 소스 코드 동기화
echo "📤 서버에 소스 코드 동기화 중..."
rsync -avz --delete $EXCLUDES ./ $USER@$HOST:$TARGET_DIR/


# ✅ 이전 컨테이너 정리 준비
echo "🧹 이전 컨테이너/이미지 정리 중..."
CONTAINERS=$(docker ps -a --filter "ancestor=${IMAGE_NAME}:${IMAGE_TAG}" --format "{{.ID}}")

if [ -n "$CONTAINERS" ]; then
  for CONTAINER_ID in $CONTAINERS; do
    # ✅ 네트워크에서 disconnect
    if docker inspect "$CONTAINER_ID" | grep -q "$NETWORK_NAME"; then
      echo "🔌 네트워크 연결 해제: $NETWORK_NAME → $CONTAINER_ID"
      docker network disconnect "$NETWORK_NAME" "$CONTAINER_ID"
    fi

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

# ✅ 네트워크 없으면 생성
echo "🔍 $NETWORK_NAME 네트워크 존재 여부 확인 중..."
docker network inspect $NETWORK_NAME > /dev/null 2>&1 || docker network create $NETWORK_NAME
docker network inspect $NGINX_CONTAINER_NAME > /dev/null 2>&1 || docker network connect $NETWORK_NAME $NGINX_CONTAINER_NAME

# ✅ 서버에서 docker compose 실행
echo "🚀 서버에서 빌드 및 재시작..."
ssh -t $USER@$HOST <<EOF
  cd $TARGET_DIR
  $COMPOSE_CMD down || true
  $COMPOSE_CMD build
  $COMPOSE_CMD up -d
EOF

echo "✅ 배포 완료! 접속 주소: http://$HOST"
