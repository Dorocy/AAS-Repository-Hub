## 프로젝트 구조
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

## VSCODE 디버그 모드
```
  - vscode debug mod  "launch.json" file

{
    // IntelliSense를 사용하여 가능한 특성에 대해 알아보세요.
    // 기존 특성에 대한 설명을 보려면 가리킵니다.
    // 자세한 내용을 보려면 https://go.microsoft.com/fwlink/?linkid=830387을(를) 방문하세요.
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python 디버거: FastAPI",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                //"--reload"
            ],
            "jinja": true
        }
    ]
}
```

## 서비스 실행 방법
```  
  - 단독 fastapi
    : uvicorn main:app --host 0.0.0.0 --port 8000 
  
  - Multi fastapi (port 는 시작 포트, workers는 운영되는 서비스 갯수)
    : 가상환경 python main_nginx.py --host 0.0.0.0 --port 8081 workers 2
```

## ETC_DOCUMENT
```
	AAS_REPOSITORY_postgresql16_20250520.sql		## AAS Repository postgresql16 db 백업파일(SQL형식)
    AAS_REPOSITORY_postgresql16_20250520.tar		## AAS Repository postgresql16 db 백업파일(TAR형식)
    AAS_REPOSITORY_postgresql_Schema_Info.txt		## AAS Repository 스키마 생성 및 초기화
    AAS_REPOSITORY_관리자_매뉴얼_v.1.0.pptx			## 관리자 매뉴얼
    AAS_REPOSITORY_사용자_매뉴얼_v.1.0.pptx			## 사용자 매뉴얼
	AAS_REPOSITORY_구축_사업_개발환경.hwp			## 개발 환경 정보(Basyx 추가 사항 포함)
    AasEnvironmentApiHTTPController.java			## 바식스 수정 파일1
	DefaultAASEnvironment.java						## 바식스 수정 파일2
	https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_windows-x64_bin.zip  		
		## openjdk windows version : 17.0.2 하위 폴더를 bin~부터 압축 풀어 jdk\windows\openjdk-17.0.2   압축 풀기
	https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-x64_bin.tar.gz
		## openjdk linux version : 17.0.2 하위 폴더를 bin~부터 압축 풀어 jdk\linux\openjdk-17.0.2   압축 풀기
```
