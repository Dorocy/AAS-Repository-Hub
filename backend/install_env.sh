#!/bin/bash

set -e  # Stop the script on any error

echo "🚀 AAS Repository 환경 5개 파일 자동 설치 시작..."

# Google Drive 파일 다운로드를 위한 gdown 필요
if ! command -v gdown &> /dev/null
then
    echo "🔧 gdown이 설치되지 않았습니다. 설치를 진행합니다..."
    pip install gdown
fi

# Miniconda 설치
echo "===> 1. Miniconda 다운로드 중..."
gdown https://drive.google.com/uc?id=10e-GtK53n1cqeHHqwCFzj_VTLudsPcmq -O Miniconda3-latest-MacOSX-arm64.sh
chmod +x Miniconda3-latest-MacOSX-arm64.sh

# basyx JAR 설치
echo "===========> 2. basyx JAR 다운로드 중..."
mkdir -p basyx
gdown https://drive.google.com/uc?id=17NTuUdk_PmpuSb9Tb6A8vEVYWw3Cs6Ns -O basyx/basyx.aasenvironment.component-2.0.0-SNAPSHOT-shaded.jar

# OpenJDK (macOS)
echo "===================> 3. OpenJDK (macOS) 다운로드 중..."
mkdir -p jdk
gdown https://drive.google.com/uc?id=1tKv3FowNsUCtVxOYh-Exg5HaAmJ65k38 -O jdk-mac.zip
unzip -o jdk-mac.zip -d jdk/
rm jdk-mac.zip


# OpenJDK (Windows)
echo "===================> 4. OpenJDK (Windows) 다운로드 중..."
mkdir -p jdk
gdown https://drive.google.com/uc?id=1vabAcuKPazyq-NsN1Tk9UCkf9O8PRQBY -O jdk-win.zip
unzip -o jdk-win.zip -d jdk/
rm jdk-win.zip

# OpenJDK (Linux)
echo "===================> 5. OpenJDK (Linux) 다운로드 중..."
mkdir -p jdk
gdown https://drive.google.com/uc?id=1Ip-B8RBc-o5zkzkDw6mblXfcYnm2a_av -O jdk-linux.zip
unzip -o jdk-linux.zip -d jdk/
rm jdk-linux.zip

echo ""
echo "<================모든 설치가 완료되었습니다. 이제 프로젝트를 실행할 수 있습니다!================>"