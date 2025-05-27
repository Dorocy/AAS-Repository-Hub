import json
import asyncio
from fastapi import APIRouter, Depends, File, Request, UploadFile, Form, HTTPException, Header, Query, Body, Path
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from pydantic import BaseModel
from app.aasModelModule import *
from app.basyxAasenvironmentModule import *
from typing import Optional, Annotated, Literal
from config.config import get_config_value

from middleware.authMiddleware import verify_token
from app.basyxAasenvironmentModule import AASDownloadRequest

router = APIRouter(
    prefix="/basyx"
)

@router.post("/aasmodel/import", tags=["AAS_MODEL_BASYX"], summary="AASX Import", description="AASX Package Explorer 에서 작성한 파일을 Import 하여 JSON으로 파싱")
async def aasModelImport(header: Annotated[dict, Depends(verify_token)],
                            file: UploadFile = File(...),
                            id: str | None = Query(default=None)):
    return await aasModelImportEvent(header, file, id)

@router.post("/aasmodel/validate", tags=["AAS_MODEL_BASYX"], summary="AAS 파일 유효성검사(AASX, JSON, XML)")
async def aasModelValidate(header: Annotated[dict, Depends(verify_token)],
                                  file: UploadFile = File(...)):
    return await aasModelValidateEvent(header, file)

@router.post("/{modelType}/download", tags=["AAS_MODEL_BASYX"], summary="AAS 파일 저장",
             description="json, xml, aasx 파일 다운로드")
async def aasModelDownload(header: Annotated[dict, Depends(verify_token)],
                            body: AASDownloadRequest, 
                            format: Literal["json", "xml", "aasx"] = Query("json"),
                            modelType: Literal["aasmodel", "instance"] = Path(...)):
    return await aasModelDownloadEvent(header, body, format, modelType)

