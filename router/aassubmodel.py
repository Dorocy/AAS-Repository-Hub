import requests
import urllib3
import json
import re
import asyncio
import psycopg
from fastapi import APIRouter, Depends, File, Request, UploadFile, Form, HTTPException, Header, Query
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from pydantic import BaseModel
import urllib3
from app.aasSubModelModule import *
from typing import Optional, Annotated, Union
from config.config import get_config_value

from middleware.authMiddleware import verify_token, verify_token_optional

router = APIRouter()
requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


## AAS SubModel Template List
@router.get("/submodel/list/{pageNumber}/{pageSize}", tags=['AAS_SubModel'], summary='AAS_SubModel', description="모델현황")
async def aasModelList(header:Annotated[dict, Depends(verify_token_optional)], title:str = "", searchKey: str = "", category_seq: Union [int, str] = "", pageNumber: int=1, pageSize: int = 10, p:str = ""):
    
    pageMode = False
    if p == "p":
        pageMode = True

    return await aasSubModelListEvent(header, title, searchKey, category_seq, pageNumber, pageSize, pageMode)


## AAS SubModel Check
@router.post("/submodel/verify/submodel-id", tags=['AAS_SubModel'], summary='AAS_SubModel', description="등록중인 SUBMODEL_ID 확인")
async def aasSubModelSaveCheck(header:Annotated[dict, Depends(verify_token)], submodel_id: str):
    return await aasSubModelSaveCheckEvent(submodel_id)


## SubModel 상세 조회
@router.get("/submodel/{submodel_seq}", tags=['AAS_SubModel'], summary='AAS_SubModel', description="aas 서브모델 상세 조회")
async def aasSubModelDetail(header:Annotated[dict, Depends(verify_token)], submodel_seq: Union [int, str] = ""):
    return await aasSubModelDetailEvent(header, submodel_seq)


## AAS SubModel 히스토리 조회
@router.get("/submodel/history/{submodel_seq}", tags=['AAS_SubModel'], summary='AAS_SubModel', description="aas 서브모델 히스토리 리스트")
async def aasSubModelHistoryList(header:Annotated[dict, Depends(verify_token)], submodel_seq: Union [int, str] = ""):
    return await aasSubModeHistoryListEvent(header, submodel_seq)



## AAS SubModel Template Temporary Save
@router.post("/submodel/temporary/data", tags=['AAS_SubModel'], summary='AAS_SubModel', description="서브모델 임시저장")
async def aasSubModelDetailTempSave(header:Annotated[dict, Depends(verify_token)], body: str = Form(...), image: Optional[Union [UploadFile, str]] = File(None)):

    if isinstance(image, str):
        image = None

    body  = json.loads(body)
    return await aasSubModelSaveEvent(header, body, image)


@router.delete("/submodel/data", tags=['AAS_SubModel'], summary='AAS_SubModel', description="저장 삭제")
async def aasmodelTempDelete(header:Annotated[dict, Depends(verify_token)], submodel_seq: Union [int, str] = ""):
    
    return await submodelDeleteEvent(header, submodel_seq)

## AAS SubModel Template Draft Save
@router.post("/submodel/draft/data", tags=['AAS_SubModel'], summary='AAS_SubModel', description="서브모델 저장")
async def aasSubModelDraftSave(header:Annotated[dict, Depends(verify_token)], body: str = Form(...), image: Optional[Union [UploadFile, str]] = File(None)):
    if isinstance(image, str):
        image = None

    body  = json.loads(body)
    return await aasSubModelSaveEvent(header, body, image, False)



## JSON 파일 업로드
@router.post("/submodel/import", tags=["AAS_SubModel"], summary="AAS SubModel Import", description="JSON 파일 업로드")
async def aasSubModelImport(header:Annotated[dict, Depends(verify_token)], file: UploadFile = File(...),
                            id: str | None = Query(default=None)):
    return await aasSubModelImportEvent(header, file, id)

## JSON 파일 다운로드
@router.post("/submodel/download", tags=["AAS_SubModel"], summary="Submodel 다운로드")
async def aasSubModelDownload(header:Annotated[dict, Depends(verify_token)], id: str = Query(..., description="Submodel ID")):
    return await aasSubModelDownloadEvent(header, id)