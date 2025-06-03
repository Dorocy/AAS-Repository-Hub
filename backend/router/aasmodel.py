import json
import re
import asyncio
import psycopg
from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.aasModelModule import *
from typing import Annotated, Union, Optional
import requests
import urllib3

from middleware.authMiddleware import verify_token, verify_token_optional

router = APIRouter()
requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# AAS AASmodel Template List
@router.get("/aasmodel/list/{pageNumber}/{pageSize}", tags=['AAS_MODEL'], summary='AAS_MODEL', description="모델현황")
async def aasModelList(header:Annotated[dict, Depends(verify_token_optional)], title:str = "", searchKey: str = "", category_seq: Union [int, str] = "", pageNumber: int=1, pageSize: int = 10 , p:str = ""):

    pageMode = False
    if p == "p":
        pageMode = True

    return await aasModelListEvent(header, title, searchKey, category_seq,pageNumber, pageSize, pageMode)

## AAS AASmodel_id Check
@router.post("/aasmodel/verify/aasmodel-id", tags=['AAS_MODEL'], summary='AAS_MODEL', description="등록중인 AASMODEL_ID 확인")
async def aasSubModelSaveCheck(header:Annotated[dict, Depends(verify_token)], aasmodel_id: str, status: str = "temporary"):
    return await aasmodelSaveCheckEvent(aasmodel_id)


## AAS AASmodel 상세 조회
@router.get("/aasmodel/{aasmodel_seq}", tags=['AAS_MODEL'], summary='AAS_MODEL', description="aas 모델 상세 조회")
async def aasmodelDetail(header:Annotated[dict, Depends(verify_token)], aasmodel_seq: Union [int, str] = ""):
    return await aasmodelDetailEvent(header, aasmodel_seq)


## AAS AASmodel 히스토리 조회
@router.get("/aasmodel/history/{aasmodel_seq}", tags=['AAS_MODEL'], summary='AAS_MODEL', description="aas 모델 히스토리 리스트")
async def aasmodelHistoryList(header:Annotated[dict, Depends(verify_token)], aasmodel_seq: Union [int, str] = ""):
    return await aasmodelHistoryListEvent(header, aasmodel_seq)


## AAS AASmodel Template Temporary Save
@router.post("/aasmodel/temporary/data", tags=['AAS_MODEL'], summary='AAS_MODEL', description="임시저장")
async def aasmodelTempSave(header:Annotated[dict, Depends(verify_token)], body: str = Form(...), image: Optional[Union[UploadFile, str]]  = File(None), attachments: Optional[Union[UploadFile, str]]  = File(None)):
    
    if isinstance(image, str):
        image = None

    body  = json.loads(body)
    return await aasmodelSaveEvent(header, body, image, attachments = attachments)

@router.delete("/aasmodel/data", tags=['AAS_MODEL'], summary='AAS_MODEL', description="저장 삭제")
async def aasmodelTempDelete(header:Annotated[dict, Depends(verify_token)], aasmodel_seq: Union [int, str] = ""):
    
    return await aasmodelDeleteEvent(header, aasmodel_seq)

## AAS AASmodel Template Draft Save/수정
@router.post("/aasmodel/draft/data", tags=['AAS_MODEL'], summary='AAS_MODEL', description="저장")
async def aasmodelDraftSave(header:Annotated[dict, Depends(verify_token)], body: str = Form(...), image: Optional[Union[UploadFile, str]] = File(None), attachments: Optional[Union[UploadFile, str]]  = File(None)):

    if isinstance(image, str):
        image = None

    body  = json.loads(body)

    return await aasmodelSaveEvent(header, body, image, is_temporary = False, attachments = attachments)

