# 🗂️ AAS Repository Hub

AAS Repository Hub는 산업 현장에서 분산되어 관리되는 AAS(Asset Administration Shell) 모델을 통합하여 중앙 집중식으로 저장하고 관리하는 시스템입니다.

---

## 🎯 프로젝트 개요

기존에는 AAS 모델 파일이 산발적이고 분산된 형태로 관리되어, 표준화된 통합 관리를 어렵게 만들고 있었습니다.

**AAS Repository Hub**는 다음을 목표로 합니다:

-  AAS 모델 구조를 명확히 정의하여 일원화된 생성 방식 제공
-  AAS Part 1 메타모델 표준에 따라 모델 파일 검증 및 관리
-  국내 최초로 중앙 집중형 AAS 저장소 시스템 구현
-  API 기반으로 AAS 파일 CRUD 기능 제공

---

## 🧱 백엔드 구조 (`backend/`)

### 📁 주요 디렉토리 및 파일

- **`main.py`**: FastAPI 기반의 메인 서버 실행 파일
- **`main_nginx.py`**: Nginx를 활용한 멀티 서비스 실행 파일
- **`requirements.txt`**: 필요한 Python 라이브러리 목록
- **`install_env.sh`**: 환경 설정 및 필요한 파일 다운로드 스크립트
- **`app/`**: AAS 관련 모듈들이 위치한 디렉토리
- **`config/`**: 서버 설정 파일들이 위치한 디렉토리
- **`jdk/`**: 운영체제별 OpenJDK 파일들이 위치한 디렉토리
- **`middleware/`**: 인증 및 기타 미들웨어 모듈들이 위치한 디렉토리
- **`processor/`**: 데이터베이스 처리 모듈이 위치한 디렉토리
- **`router/`**: API 라우터 모듈들이 위치한 디렉토리
- **`tools/`**: 비동기 처리, 암호화, 로그 처리 등의 유틸리티 모듈들이 위치한 디렉토리

### ⚙️ 주요 기술 스택

- Python 3.13.1
- FastAPI
- PostgreSQL
- OpenJDK 17.0.2
- BaSyx AAS Environment

### 🚀 실행 방법

```bash
# 1. Python 의존성 설치
pip install -r requirements.txt

# 2. 환경 설정 스크립트 실행
bash install_env.sh

# 3. 단일 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000

# 또는 멀티 서비스 실행 (Nginx 스타일)
python main_nginx.py --host 0.0.0.0 --port 8081 workers 2
```

---

## 💻 프론트엔드 구조 (`frontEnd/AAS-Repository-Hub/`)

### 📁 주요 디렉토리 및 파일

- **`public/`**: 정적 파일들이 위치한 디렉토리
- **`src/`**: 소스 코드 디렉토리
  - **`components/`**: 재사용 가능한 UI 컴포넌트들이 위치한 디렉토리
  - **`pages/`**: 페이지별 컴포넌트들이 위치한 디렉토리
  - **`App.js`**: 애플리케이션의 루트 컴포넌트
  - **`index.js`**: 애플리케이션의 진입점
- **`package.json`**: 프로젝트 메타데이터 및 의존성 관리 파일

### ⚙️ 주요 기술 스택

- JavaScript, TypeScript
- React
- CSS

### 🚀 실행 방법

```bash
# 1. 의존성 설치
npm install

# 2. 개발 서버 실행
npm start
```

---

## 🔗 백엔드와 프론트엔드 연동

프론트엔드는 백엔드에서 제공하는 API를 통해 AAS 데이터를 조회하고 관리합니다. 이를 통해 사용자 인터페이스에서 AAS 모델을 시각화하고 조작할 수 있습니다.

---

## 📌 요약

- AAS Repository Hub는 산업 현장에서 분산되어 관리되는 AAS 모델을 통합하여 중앙 집중식으로 저장하고 관리하는 시스템입니다.
- 백엔드는 Python과 FastAPI를 기반으로 하며, AAS 모델의 생성, 저장, 관리를 담당합니다.
- 프론트엔드는 React를 기반으로 하며, 사용자에게 AAS 모델을 시각화하고 조작할 수 있는 인터페이스를 제공합니다.

이러한 구조를 통해 AAS 모델의 효율적인 관리와 활용이 가능해집니다.
