from fastapi import FastAPI, Request
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from router import auth, aasmodel, aassubmodel, publish, etc, aasBasyx, aasInstance
from config.config import get_config_value, get_section_dict

from starlette.middleware.base import BaseHTTPMiddleware

from starlette.responses import RedirectResponse
#from middleware.authMiddleware import AuthMiddleware

#from processor.jdbcProcess import setJavaEnvironment
import multiprocessing
import signal
import time

import os
import argparse

SYS_NAME = get_config_value('service_info', 'name')
SERVICE_INFO = get_section_dict("service_info")
MAX_REQUEST = get_config_value('fastapi', 'max_request')
MAX_REQUEST_RT = get_config_value('fastapi', 'max_request_interval_rt')


def create_app(port: int, max_requests: int):
    app = FastAPI(title=f"{SYS_NAME} BACKEND")
    
    # 요청 수와 최대 요청 수 초기화
    app.state.request_count = 0
    app.state.MAX_REQUESTS = max_requests  # 요청 수 제한

    @app.middleware("http")
    async def count_requests(request: Request, call_next):
        app.state.request_count += 1
        response = await call_next(request)

        print(f"Request count for Process Port - {port} : {app.state.request_count} / {max_requests}")

        if app.state.request_count >= app.state.MAX_REQUESTS:
            print(f"Max requests reached for Process Service Port - {port} . Restarting server...")
            # 현재 프로세스를 종료하고 새로운 프로세스를 시작합니다.
            os.kill(os.getpid(), signal.SIGTERM)  # 현재 프로세스를 종료
        return response

    # 허용할 Origin 등록
    origins = [SERVICE_INFO["host_f_domain"], SERVICE_INFO["host_f_ip"]]

    # 미들웨어 제거
    # app.add_middleware(BaseHTTPMiddleware, dispatch=AuthMiddleware(app))
    # CORS 미들웨어 등록
    app.add_middleware(
        CORSMiddleware,
        
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ) 
   

    app.include_router(auth.router)
    app.include_router(aasmodel.router)
    app.include_router(aassubmodel.router)
    app.include_router(aasBasyx.router)
    app.include_router(aasInstance.router)
    app.include_router(publish.router)
    app.include_router(etc.router)


    return app


# java 환경 변수 설정
#setJavaEnvironment() 


def run_server(host: str, port: int, max_requests: int):
    import uvicorn
    from app.basyxAasenvironmentModule import start_jvm 
    start_jvm() 
    app = create_app(port, max_requests)
    #uvicorn.run(app, host=host, port=port, reload=False)
    config = uvicorn.Config(app, host=host, port=port, reload=False)
    server = uvicorn.Server(config)
    server.run()

def start_new_process(host: str, port: int, max_requests: int):
    print(f"{SYS_NAME} Backend Server Starting new Uvicorn service on port: {port} with MAX_REQUESTS: {max_requests}")
    process = multiprocessing.Process(target=run_server, args=(host, port, max_requests))
    process.start()
    return process

if __name__ == "__main__":
    ## 시작 포트
    ## nginx에서는 8080 또는 대표로 접속
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='192.168.123.100') # 
    parser.add_argument('--port', type=int, default='8081') # 
    parser.add_argument('--workers', type=int, default='2') # 
    args = parser.parse_args()

    host = args.host
    start_port = args.port
    workers =  args.workers

    processes = []
    max_requests_list = []

    for i in range(workers):
        max_requests_list.append(MAX_REQUEST + i*(MAX_REQUEST*MAX_REQUEST_RT))

    #print(host, start_port, workers, max_requests_list)
    
    for i in range(workers):  # 2개의 FastAPI 인스턴스 생성
        process = start_new_process(host, start_port + i, max_requests_list[i])
        processes.append(process)

    while True:
        for process in processes:
            if not process.is_alive():
                # 프로세스가 종료되면 새로운 프로세스를 시작합니다.
                index = processes.index(process)
                processes[index] = start_new_process(host, start_port + index, max_requests_list[index])
        time.sleep(1)  # 상태 확인 간격