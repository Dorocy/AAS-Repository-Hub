import json
import requests
import urllib3
import asyncio
from fastapi import APIRouter, Depends, File, Request, UploadFile, Form, HTTPException, Header
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from pydantic import BaseModel
from app.publishModule import *
from typing import Optional, Annotated, Union
from config.config import get_config_value

from middleware.authMiddleware import verify_token, verify_token_optional

router = APIRouter()
requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# AAS Publish ALL List
@router.get("/published/list/{status}/{ty}/{pageNumber}/{pageSize}", tags=['PUBLISH'], summary='PUBLISHED', description="PUBLISHED LIST")
async def publishList(header:Annotated[dict, Depends(verify_token)], status :str = "all", ty:str = "all", category_seq: Union [int, str] = "", searchKey: str = "", pageNumber: int=1, pageSize: int = 10, p:str = ""):



    if ty == "all":
        ty = ""

    pageMode = False
    if p == "p":
        pageMode = True

    return await publishListEvent(header, searchKey, category_seq, ty, status, "",  pageNumber, pageSize, pageMode)



# AAS Publish  Detail
@router.get("/published/{ty}/{target_seq}", tags=['PUBLISH'], summary='PUBLISHED', description="PUBLISHED 대상 상세 정보")
async def publishDraftDetail(header:Annotated[dict, Depends(verify_token)],  target_seq:Union[int, str] = "",  ty:str = "aasmodel"):

    return await publishListEvent(header, "", "", ty, "", target_seq, 1, 1)


# AAS Publish History
@router.get("/published/history/{ty}/{target_seq}", tags=['PUBLISH'], summary='PUBLISHED', description="PUBLISHED 배포 히스토리(draft, published, )")
async def publishHistoryList(header:Annotated[dict, Depends(verify_token)], target_seq: Union [int, str] = "",  ty:str = "aasmodel"):
    return await publishHistoryListEvent(header, ty, target_seq)


# AAS Publish Process
@router.post("/published/data", tags=['PUBLISH'], summary='PUBLISHED', description="PUBLISHED 배포승인")
async def publishProcess(header:Annotated[dict, Depends(verify_token)], body : dict):
    return await publishProcessEvent(header, body)


# AAS Publish Modify
@router.put("/published/data", tags=['PUBLISH'], summary='PUBLISHED', description="PUBLISHED 배포수정")
async def publishModify(header:Annotated[dict, Depends(verify_token)], body : dict):
    return await publishModifyEvent(header, body)

# AAS Publish Modify
@router.get("/published/count", tags=['PUBLISH'], summary='PUBLISHED', description="등록된 건수(배포)")
async def publishedCount(header:Annotated[dict, Depends(verify_token_optional)]):
    return await publishedCountEvent(header)
