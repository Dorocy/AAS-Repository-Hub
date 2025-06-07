# 🗂️ AAS Repository

[🖥️ 데모 바로 보기 (Vercel)](https://your-vercel-url.vercel.app)

AAS Repository는 산업용 디지털 트윈의 핵심 기술인 AAS (Asset Administration Shell) 모델 파일들을 중앙 집중식으로 저장하고 관리할 수 있는 Python 기반의 서버 애플리케이션입니다.

---

## 🌐 API 문서 접근

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

---

---

## 🎯 프로젝트 개요

기존에는 AAS 모델 파일이 산발적이고 분산된 형태로 관리되어, 표준화된 통합 관리를 어렵게 만들고 있었습니다.

**AAS Repository**는 다음을 목표로 합니다:

- ✅ AAS 모델 구조를 명확히 정의하여 일원화된 생성 방식 제공
- ✅ AAS Part 1 메타모델 표준에 따라 모델 파일 검증 및 관리
- ✅ 국내 최초로 중앙 집중형 AAS 저장소 시스템 구현
- ✅ API 기반으로 AAS 파일 등록, 검색, 수정 기능 제공

---

## ⚙️ 기술 스택

- Python 3.13.1
- FastAPI
- Uvicorn (ASGI)
- OpenJDK 17.0.2
- aas-test-engines
- gdown (Google Drive 다운로드용)
- basyx JAR 연동

---

## 🛠️ 개발환경 및 실행 가이드

### 1️⃣ 로컬 개발 환경 설치

```bash
cd backend
pip install -r requirements.txt
bash install_env.sh
```

설치되는 주요 구성 요소:

- Miniconda
- OpenJDK (macOS / Windows / Linux)
- basyx.aasenvironment.component JAR

설치 후 폴더 예시:

```
backend/
├── basyx/
├── jdk/mac/
├── jdk/window/
├── jdk/linux/
├── Miniconda3-latest-MacOSX-arm64.sh
```

---

### 2️⃣ FastAPI 서버 실행 방법

#### ✅ 단일 FastAPI 실행

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### ✅ Multi FastAPI (nginx 스타일 병렬 서비스 실행)

```bash
python main_nginx.py --host 0.0.0.0 --port 8081 workers 2
```

---

## 📁 프로젝트 폴더 구조 요약

```
backend/
├── main.py
├── main_nginx.py
├── install_env.sh
├── requirements.txt
├── app/
│   ├── aasInstanceModule.py
│   ├── aasModelModule.py
│   ├── authModule.py
│   └── ...
├── basyx/
├── config/
├── jdk/
├── middleware/
├── processor/
├── router/
├── tools/
└── .vscode/
```

---

## 프로젝트 상세 구조

```
AAS_REPO_BACK
│  aasrepo.service      ## 우분투 서비스 파일 만들기
│  main.py              ## main.py 실행
│  main_nginx.py        ## main_nginx.py nginx를 두어 서비스 다중 실행 할때
│  README.md
│  requirements.txt     ## pip install 목록
│
├─.vscode
│      launch.json      ## VSCODE 디버깅 옵션
│
├─app
│      aasInstanceModule.py     ## 인스턴스 모듈
│      aasModelModule.py        ## AAS모델 모듈
│      aasSubModelModule.py     ## AAS SUB모델 모듈
│      authModule.py			## 인증 모듈
│      basyxAasenvironmentModule.py		## 바식스 모듈
│      etcModule.py             ## 기타 시스템 모듈
│      publishModule.py         ## 배포 모듈
│
├─basyx
│      basyx.aasenvironment.component-2.0.0-SNAPSHOT-shaded.jar		## 바식스 Jar 파일
│
├─config
│      config.py        ## 설정 파일 연결
│      config.yaml      ## 개발 서버 설정 파일
│      config_keti.yaml     ## 운영 서버 설정 파일
│
├─jdk       ## JVM호출을 위한 OPENJDK 서버 배포환경에 따른 참조
│  ├─linux
│      └─openjdk-17.0.2			## openjdk 리눅스 버전 17.0.2
│  └─windows
│      └─openjdk-17.0.2			## openjdk 윈도우 버전 17.0.2
│
├─middleware
│      authMiddleware.py        ## API Header 인증 모듈
│
├─processor
│      postgresProcess.py       ## DB 처리 모듈
│
├─router                ## 라우터
│      aasBasyx.py      ## 바식스 라우터
│      aasInstance.py   ## 인스턴스 라우터
│      aasmodel.py      ## AASMODEL 라우터
│      aassubmodel.py   ## SUBMODEL 라우터
│      auth.py          ## 인증 라우터
│      etc.py           ## 기타 설정 라우터
│      publish.py       ## 배포 라우터
│
└─tools     ## 툴
        asyncTool.py        ## 비동기 처리 툴
        cryptoTool.py       ## 암호화 처리 툴
        jdbcTool.py         ## JVM 처리 툴
        loggerTool.py       ## 로그 처리 툴
        stringTool.py       ## 문자열 처리 툴
```

## 기술 스택

```
  - python version : 3.13.1
  - requirements.txt
    : pip install -r requrements.txt
  - java : openjdk 17.0.2
    : python 에서 jdk-jvm 으로 호출 사용
  - Baysix
```

---

## 🐛 VSCode 디버그 모드

`backend/.vscode/launch.json` 설정 예시:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python 디버거: FastAPI",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--host", "0.0.0.0", "--port", "8000"],
      "jinja": true
    }
  ]
}
```

---

## 서비스 실행 방법

```
  - 단독 fastapi
    : uvicorn main:app --host 0.0.0.0 --port 8000

  - Multi fastapi (port 는 시작 포트, workers는 운영되는 서비스 갯수)
    : 가상환경 python main_nginx.py --host 0.0.0.0 --port 8081 workers 2
```

## 🧩 기타 문서 및 참조 자료

- `AAS_REPOSITORY_postgresql16_20250520.sql`: DB 백업 (SQL)
- `AAS_REPOSITORY_관리자_매뉴얼_v1.0.pptx`: 관리자용 설명서
- `AAS_REPOSITORY_사용자_매뉴얼_v1.0.pptx`: 사용자 매뉴얼
- `AAS_REPOSITORY_구축_사업_개발환경.hwp`: 개발환경 요약서
- `AasEnvironmentApiHTTPController.java`: 바식스 API 수정본
- `DefaultAASEnvironment.java`: 바식스 환경 기본 파일

```
