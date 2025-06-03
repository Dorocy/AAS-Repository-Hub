import json
import asyncio
from fastapi import APIRouter, Depends, File, Request, UploadFile, Form, HTTPException, Header
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from pydantic import BaseModel
from app.etcModule import *
from typing import Optional, Annotated
from config.config import get_config_value

from middleware.authMiddleware import verify_token, verify_token_optional

router = APIRouter()
requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 코드 모음/ 
@router.get("/common/code/{type}", tags=['ETC'], summary='리스트', description="코드목록")
async def geCodeList(header:Annotated[dict, Depends(verify_token_optional)], type: str, ref_code1:str = "", ref_cdoe2:str = "", ref_cdoe3:str = ""):
    return await getCodeListEvent(header, type, ref_code1, ref_cdoe2, ref_cdoe3)


