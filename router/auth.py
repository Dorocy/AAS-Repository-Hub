import requests
import urllib3
import json
import re
import asyncio
import psycopg

from fastapi import APIRouter, Depends, File, Request, UploadFile, Form, HTTPException, Header
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from pydantic import BaseModel
import urllib3

from typing import Optional, Annotated, Union
from config.config import get_config_value

from middleware.authMiddleware import verify_token
from app.authModule import *

router = APIRouter()
requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)




# login 
@router.post("/login", tags=['인증'], summary='로그인', description="로그인처리")
async def authLogin(body: dict):
    user_id = ""
    user_pw = ""

    if 'id' in body:
        user_id = body['id'] 
    if 'pw' in body:
        user_pw = body['pw'] 
    
    return await authLoginEvent(user_id, user_pw)



# 회원가입
@router.post("/register", tags=['인증'], summary='회원가입', description="회원가입처리")
async def register(body: dict):

    user_id = ""
    user_pw = ""
    user_name = ""

    if 'id' in body:
        user_id = body['id'] 
    if 'pw' in body:
        user_pw = body['pw'] 
    if 'name' in body:
        user_name = body['name'] 
    
    return await registerEvent(user_id, user_pw, user_name)

##비밀번호 초기화
### TODO 비밀번호 초기화
@router.get("/password-reset/request", tags=['인증'], summary='비밀번호찾기', description="비밀번호 찾기")
async def resetPasswordRequest(email: str):
    return await resetPasswordRequestEvent(email)


class ResetPassword(BaseModel):
    token: str
    new_password: str
# 2. 비밀번호 변경 (토큰 검증 후 비밀번호 업데이트)
@router.post("/password-reset", tags=['인증'], summary='비밀번호 변경', description="비밀번호 변경")
async def reset_password(data: ResetPassword):
    return await resetPasswordEvent(data.token, data.new_password)



# 소셜로그인
@router.get("/{social}/login", tags=['인증'], summary='로그인', description="소셜 로그인")
def socialLogin(social: str):
    return socialLoginEvent(social)

## 소셜 로그인 Call Back
@router.get('/{social}/callback', tags=['인증'], summary='로그인', description="구글/네이버 소셜 로그인 콜백")
def google_callback(social: str , code: str = None, state: str = None, error: str = None, error_description: str = None):
    if social == "google":
        return google_callbackEvent(code, state, error)
    elif social == "naver":
        return naver_callbackEvent(code, state, error, error_description)


## User List
@router.get('/user/list/{pageNumber}/{pageSize}', tags=['사용자'], summary='사용자', description="사용자 리스트")
async def userList(header:Annotated[dict, Depends(verify_token)], searchKey: str = "", user_group_seq: Union[int, str] = "",  pageNumber: int=1, pageSize: int = 10 , p:str = ""):
    pageMode = False
    if p == "p":
        pageMode = True
    return await userListEvent(header, searchKey, '', user_group_seq, pageNumber, pageSize, pageMode)

@router.get('/user/info/{user_seq}', tags=['사용자'], summary='사용자', description="사용자 정보")
async def userInfo(header:Annotated[dict, Depends(verify_token)], user_seq:str = ''):
    return await userListEvent(header, '', user_seq, '', 1, 1, False)

@router.post('/user/info', tags=['사용자'], summary='사용자', description="사용자 정보 수정")
async def userInfo(header:Annotated[dict, Depends(verify_token)], body : dict):
    return await userInfoUpdateEvent(header, body)

    