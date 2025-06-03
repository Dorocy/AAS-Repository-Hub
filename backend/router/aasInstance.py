from fastapi import APIRouter, Depends
from app.aasSubModelModule import *
from typing import Annotated
from middleware.authMiddleware import verify_token
from app.aasInstanceModule import *

router = APIRouter(prefix="/instance")

## Submodel 추가
@router.post("/submodel/merge", tags=["AAS_SubModel"], summary="AAS SubModel merge", description="AAS Instance에 Submodel 추가")
async def aasSubModelMerge(header:Annotated[dict, Depends(verify_token)], body: SubmodelMergeRequest):
    return await aasSubModelMergeEvent(header, body)




# AAS Instance ALL List
@router.get("/list/{category}/{pageNumber}/{pageSize}", tags=['INSTANCE'], summary='INSTANCE', description="INSTANCE LIST")
async def instanceList(header:Annotated[dict, Depends(verify_token)], category :str = "all", searchKey: str = "", pageNumber: int=1, pageSize: int = 10, p:str = ""):

    if category == "all":
        category = ""

    pageMode = False
    if p == "p":
        pageMode = True

    return await instanceListEvent(header, category, searchKey,  pageNumber, pageSize, pageMode)

# AAS Instance Detail
@router.get("/{instance_seq}", tags=['INSTANCE'], summary='INSTANCE', description="INSTANCE DETAIL")
async def instanceInfo(header:Annotated[dict, Depends(verify_token)], instance_seq: int = 0):
    return await instanceInfoEvent(header, instance_seq)


# AAS Instance Save
@router.post("/data", tags=['INSTANCE'], summary='INSTANCE', description="INSTANCE SAVE")
async def instanceSave(header:Annotated[dict, Depends(verify_token)], body: dict):
    return await instanceSaveEvent(header, body)

# AAS Instance Delete
@router.delete("/data", tags=['INSTANCE'], summary='INSTANCE', description="INSTANCE DELETE")
async def instanceSave(header:Annotated[dict, Depends(verify_token)], instance_seq):
    return await instanceDelEvent(header, instance_seq)

# AAS Instance Target AASMODEL List
@router.get("/list/{ty}/{category_seq}", tags=['INSTANCE'], summary='INSTANCE', description="INSTANCE AAS/SUB MODEL LIST")
async def instanceModelList(header:Annotated[dict, Depends(verify_token)], ty: str = "INSTANCE", category_seq: Union [int, str] = "all"):

    if category_seq == "all":
        category_seq = ""

    return await instanceModelListEvent(header, ty, category_seq)

# AAS Instance 전체 json 조회
@router.get("/detail/{instance_seq}", tags=['INSTANCE'], summary='AAS Instance 상세조회')
async def aasInstanceDetail(header:Annotated[dict, Depends(verify_token)], instance_seq: Union [int, str] = ""):
    return await aasInstanceDetailEvent(header, instance_seq)

# AAS Instance 검증 (KETI API)
@router.post("/verification", tags=['INSTANCE'], summary='AAS Instance 검증')
async def aasInstanceVerification(header:Annotated[dict, Depends(verify_token)], body: dict):
    return await aasInstanceVerificationEvent(header, body)