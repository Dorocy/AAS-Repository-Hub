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
from app.basyxAasenvironmentModule import start_jvm  

SYS_NAME = get_config_value('service_info', 'name')
SERVICE_INFO = get_section_dict("service_info")
MAX_REQUEST = get_config_value('fastapi', 'max_request')
MAX_REQUEST_RT = get_config_value('fastapi', 'max_request_interval_rt')


app = FastAPI(title=f"{SYS_NAME} BACKEND by Impix.")


# 허용할 Origin 등록
origins = [SERVICE_INFO["host_f_domain"], SERVICE_INFO["host_f_ip"], ""]

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

start_jvm()