import base64
from typing import Union,Optional
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from processor.postgresProcess import *
from tools.stringTool import dollarSign, validate_json
from pydantic import BaseModel
import io
from io import BytesIO
import requests
from app.etcModule import *


## Submodel 리스트
async def aasSubModelListEvent(userinfo, title, searchKey, category_seq, pageNumber = 1, pageSize = 10, pageMode = False):
    
    lang_code = userinfo.lang_code if userinfo is not None else "1"

    user_group_seq = userinfo.user_group_seq if userinfo is not None else 3
    
    ## title == '' 일경우만 searchkey , 타이틀은 메인에서 넘어오는것
    if title != '':
        searchKey = ''

    ##메타 서치
    metadata_info = validate_json(searchKey)
    metadataSearch = metadata_info[1]
    def_metastring = "{}"
    if metadata_info[0]:
        searchKey = ""
    
    rstData = { "result" : "error", "msg" : "Failed to get list" , "data" : ""}

    sql = f"""
    with min_tbl as (
        select submodel_id, min(submodel_seq) as min_submodel_seq
        from aasrepo.submodels
        group by submodel_id
        order by min_submodel_seq desc
    ), last_submodel_tbl as (
        select a.submodel_id, a.status, max(a.submodel_seq) as max_submodel_seq, b.min_submodel_seq
        from aasrepo.submodels a
        left join min_tbl b on a.submodel_id = b.submodel_id
        group by a.submodel_id, a.status, b.min_submodel_seq
        order by 3 desc, 4 desc
    )

    select dense_rank() over ( order by aa.min_submodel_seq desc) as group_seq 
    	, row_number() over (partition by aa.submodel_id  order by a.submodel_seq desc) as in_seq  
        , a.submodel_seq, a.submodel_name, a.submodel_id, a.submodel_version, a.submodel_semantic_id, a.submodel_type
        , a.description, a.category_seq,  CASE {lang_code}
                WHEN 1  THEN b.category_name
                WHEN 2  THEN b.category_name2
                WHEN 3  THEN b.category_name3
                WHEN 4  THEN b.category_name4
                WHEN 5  THEN b.category_name5
                ELSE b.category_name END as category_name, a.status, aasrepo.fncodenm(a.status, {lang_code} ) as status_nm, a.create_date
        , c.submodel_img, c.mime_type, c.filename
    from aasrepo.submodels a
    left join last_submodel_tbl as aa on a.submodel_seq = aa.max_submodel_seq
    join  aasrepo.categories b on  a.category_seq = b.category_seq
    left join aasrepo.submodel_image as c on a.submodel_seq = c.submodel_seq
    where ('{category_seq}' =  case left('{category_seq}', 6) 
				when 'GRP100' then b.refcode1 
				when 'GRP200' then b.refcode2 
				when 'GRP300' then b.refcode3
				else b.category_seq::varchar end or '{category_seq}' = '')
        and ( lower(a.submodel_name) like '%' || lower('{searchKey}') || '%' 
            or lower(a.description) like '%' || lower('{searchKey}') || '%' 
            or lower(a.submodel_id) like '%' || lower('{searchKey}') || '%' 
            or lower(a.submodel_semantic_id) like '%' || lower('{searchKey}') || '%' 
        )
        and lower(a.submodel_name) like '%' || lower('{title}') || '%' 
        and ( a.metadata @> '{metadataSearch}' or '{metadataSearch}' = '{def_metastring}' )
        and ( (3={user_group_seq} and a.status in ('published')  ) 
            or {user_group_seq} in (1, 2)	
            ) --일반사용자 일경우 추가
        and  aa.max_submodel_seq is not null
    
"""

    try:
        rst = await async_postQueryPageData(sql, pageNumber, pageSize , "", "", None, True, False, pageMode)

        if rst["result"] != "ok" :
            return JSONResponse(status_code=400, content=rstData) 
        
        return JSONResponse(status_code=200, content=rst) 
        
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 
    

## AAS SubModel 중복 체크 (중복아닐경우 False, 나머지 True)
async def duplicateSubModelIdCheckEvent(submodel_id, submodel_seq : Union [int, str] = '', user_seq:int=0):
    sql = f"""
    select submodel_id
    FROM aasrepo.submodels a
    where submodel_id = {dollarSign(submodel_id)}
    and ( submodel_seq::varchar = '{submodel_seq}' or '{submodel_seq}' = '')
    """

    try:
        rst = await async_postQueryDataOne(sql, user_seq=user_seq)

        if rst["result"] == "ok" and rst["data"] == "":
            return False

        return True
        
    except Exception as e:
        return True


async def aasSubModelSaveCheckEvent(submodel_id):
    sql = f"""
    select submodel_seq
    FROM aasrepo.submodels a
    where submodel_id = {dollarSign(submodel_id)}
        and status in ( 'temporary', 'draft' )
    """

    try:
        rst = await async_postQueryDataOne(sql)

        if rst["data"] != "":
            # return JSONResponse(status_code=400, content={ "result" : "error", "msg" : f"There are already registration (or temporary save) in progress. {rst["data"]}" , "data" : rst["data"]}) 
            return JSONResponse(
                status_code=400,
                content={
                    "result": "error",
                    "msg": f"There are already registration (or temporary save) in progress. {rst['data']}",
                    "data": rst["data"]
                }
            )
            
        return JSONResponse(status_code=200, content=rst) 

    except Exception as e:
        return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Please Reload Data" , "data" : ""}) 
    
## AAS 모델 히스토리 리스트
async def aasSubModeHistoryListEvent(userinfo, aasmodel_seq):

    user_group_seq = userinfo.user_group_seq if userinfo is not None else 3
        
    rstData = { "result" : "error", "msg" : "History Not Exists!!" , "data" : ""}

    sql = f"""
    with submodel_list as (
	
        select a.submodel_seq as id, case when  a.status != 'published' then a.status else coalesce(a.submodel_version, '') end as text
        from aasrepo.submodels a
        join aasrepo.submodels aa on a.submodel_id = aa.submodel_id and aa.submodel_seq = {aasmodel_seq}
        where ( 'submodel' = 'submodel' or 'submodel' = '' )
            and ( (3={user_group_seq} and a.status in ('published')) or {user_group_seq} in (1, 2)  )
        order by a.submodel_seq	desc	 

    )    

    select *
    from submodel_list 
    """

    try:
        rst = await async_postQueryDataSet(sql)

        if rst["result"] != "ok" and len(rst["data"]) == 0:
            return JSONResponse(status_code=400, content=rst) 

        return JSONResponse(status_code=200, content=rst) 
        
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 


## AAS SubModel ID 체크
async def aasSubModelIdCheckEvent(submodel_id, submodel_seq : Union [int, str] = ''):
    rstData = { "result" : "error", "msg" : "Duplicate AAS SubModel_ID Exists. !!" , "data" : False}

    try:
        
        if not await duplicateSubModelIdCheckEvent(submodel_id, submodel_seq):
            return JSONResponse(status_code=200, content={ "result" : "ok", "msg" : "Duplicate AAS SubModel ID Not Exists. !!" , "data" : False}) 
        else:
            return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Duplicate AAS SubModel ID Exists. !!" , "data" : True}) 
        
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 
    


## AAS 모델 상세 
async def aasSubModelDetailEvent(userinfo, submodel_seq):
    lang_code = "1" if userinfo is None else userinfo.lang_code

    rstData = { "result" : "error", "msg" : "Duplicate AAS SubModel Not Exists. !!" , "data" : ""}

    sql = f"""
select a.submodel_seq, a.submodel_name, a.submodel_version, a.submodel_id, a.submodel_semantic_id, a.submodel_type, a.category_seq
    , aasrepo.fncodenm(a.category_seq::varchar, {lang_code}, 'category') as category_name, a.description, a.status
	, a.metadata
	, c.submodel_img, c.mime_type, c.filename, a.submodel_template_id
from aasrepo.submodels a
left join aasrepo.submodel_image c on a.submodel_seq = c.submodel_seq
where a.submodel_seq = {submodel_seq}
    """

    try:
        rst = await async_postQueryDataSet(sql)

        if rst["result"] != "ok" and len(rst["data"]) == 0:
            return JSONResponse(status_code=400, content={ "result" : "ok", "msg" : "AAS SubModel ID Is Not Exists. !!" , "data" : ""}) 

        return JSONResponse(status_code=200, content=rst) 
        
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 



## AAS 서브모델 임시 및 저장
async def aasSubModelSaveEvent(userinfo, body, image: Optional[UploadFile] = File(None) , is_temporary:bool = True):

    rstData = { "result" : "error", "msg" : f"Failed to {'Temporay' if is_temporary else ''} SubModel Save !!" , "data" : ""}

    status = ""
    submodel_semantic_id = ""
    submodel_id = ""
    submodel_seq = ""

    custom_args = []

    if "status" in body :
        status = body["status"]
    if "submodel_semantic_id" in body:
        submodel_semantic_id = body["submodel_semantic_id"]
    if "submodel_id" in body :
        submodel_id = body["submodel_id"]
    if "submodel_seq" in body :
        submodel_seq = body["submodel_seq"]

    if submodel_id  == "":
        return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "AAS SubModel ID is Blank !!" , "data" : ""}) 

    if not is_temporary:
        
        # ↓ 구조로 보내야됨
        # {
        #     "submodels": [submodel json내용]
        # }
        metadata = { "submodels": [ json.loads(body["metadata"]) ] }

        rst = await verificationEvent(userinfo, metadata, 'submodel', submodel_seq, submodel_id)

        if rst["result"] == "fail": 
            return JSONResponse(status_code=500, content={"result": "error", "msg": rst["msg"], "data": rst["data"]})
        elif rst["result"] == "ok":
            pass
        else:
            return JSONResponse(status_code=400, content={"result": "error", "msg": rst["msg"], "data": ""})
        

    try:
        
        ## submodel_semantic_id = "" 최초 등록이니깐
        ## semantec_id 는 받아옴. 아이디가 버전마다 다르기 때문에 version 으로 변경
        if ((body["submodel_version"] == "" or body["submodel_version"] == "0.0" )  and submodel_seq == ""):
            ## 중복 submodel_id 체크
            if await duplicateSubModelIdCheckEvent(submodel_id, submodel_seq, user_seq=userinfo.user_seq):
                return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Duplicate AAS SubModel ID Exists. !!" , "data" : ""}) 
        
        ## 현상태 비교
        ## 현재 시퀀스가 있을경우 해당 상태 체크
        ## 없을때는 시퀀스가 최근에 저장된게 있으면 리턴        
        if submodel_seq != "":
            sql  = f"""
                --내부적으로 배포가 되었으면
                select status
                from aasrepo.submodels
                where submodel_seq = {submodel_seq}
        """
            rst = await async_postQueryDataOne(sql, log_type = "SUBMODEL", user_seq=userinfo.user_seq)

            if (rst["result"] == "ok" and rst["data"] != status):
                return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Target Data has different data(No draft data). Please!! Reload Data." , "data" : ""}) 
        
        ### 가장 최근 저장된거 있으면 해당된것 가져오기
        sql = f"""
        select submodel_seq
        FROM aasrepo.submodels a
        where submodel_id = {dollarSign(submodel_id)}
            and status in ( 'temporary', 'draft' )
        limit 1
        """

        rst = await async_postQueryDataOne(sql, log_type = "SUBMODEL", user_seq=userinfo.user_seq)

        if rst["data"] != "":
            submodel_seq  = rst["data"]
            
        
        custom_args.append(json.dumps(json.loads(body["metadata"]), ensure_ascii=False)  if body["metadata"] !="" else '{}' )

        sql = f"""

    with inserted as (
        INSERT INTO aasrepo.submodels (submodel_seq, submodel_name, submodel_id
            , submodel_semantic_id, submodel_template_id, submodel_version, submodel_type
            , category_seq, description, status
            , metadata, create_user_seq, create_date) 
        select { submodel_seq if submodel_seq != "" else "nextval('aasrepo.submodels_submodel_seq_seq'::regclass)"}, {dollarSign(body["submodel_name"])}
            , {dollarSign(submodel_id)}
            , {dollarSign(submodel_semantic_id) if submodel_semantic_id != "" else 'NULL'}
            , {dollarSign(body["submodel_template_id"]) if "submodel_template_id" in body else 'NULL'}
            , {body["submodel_version"] if body["submodel_version"] != "" else 'NULL'}, NULL 
            , {body["category_seq"] if str(body["category_seq"]) != "" else 'NULL' }
            , {dollarSign(body["description"])}
            , '{ "temporary" if is_temporary else "draft" }'
            , %s
            , {userinfo.user_seq}, localtimestamp
        ON CONFLICT (submodel_seq) 
        DO UPDATE SET
            submodel_name = EXCLUDED.submodel_name, submodel_type = EXCLUDED.submodel_type
            , category_seq = EXCLUDED.category_seq, description = EXCLUDED.description, status = EXCLUDED.status
            , submodel_template_id = EXCLUDED.submodel_template_id
            , metadata = EXCLUDED.metadata, create_user_seq = EXCLUDED.create_user_seq, create_date = EXCLUDED.create_date            
        returning submodel_seq
    )
        """

        filename = None
        mime_type = None
        image_data = None

        if image and image.filename:
            filename = image.filename
            mime_type = image.content_type
            image_data = await image.read() 
            image_data = base64.b64encode(image_data).decode("utf-8")

            sql = sql + f"""
                , insert_img as (
                    insert into aasrepo.submodel_image ( submodel_seq, submodel_img, filename, mime_type)
                    select submodel_seq, %s, %s, %s
                    from inserted
                    ON CONFLICT (submodel_seq) 
                    DO UPDATE SET
                    submodel_img = EXCLUDED.submodel_img
                    , filename = EXCLUDED.filename
                    , mime_type = EXCLUDED.mime_type
                    returning submodel_seq, submodel_img
                )
            """

            custom_args.extend([image_data, filename, mime_type])
        else:
             sql = sql + f"""
                , del_img as (
                    delete from aasrepo.submodel_image a
                    using inserted b
                        where a.submodel_seq = b.submodel_seq
                )
        """

        ## 일반 저장일떄 혹시, 임시 저장 삭제
        if not is_temporary:
            sql = sql + f"""
                , deleted as (
	                delete from aasrepo.submodels
                    where status = 'temporary'
                        and submodel_id = {dollarSign(submodel_id)}
                    returning submodel_seq
                )
                
            """
        
        sql = sql +  f"""
                select submodel_seq
                from inserted
        """
        rst = await async_postQueryDataOne(sql, None ,True, userinfo.user_seq, "SUBMODEL", custom_args)

        if rst["result"] != "ok" or rst["data"] == "":
            return JSONResponse(status_code=400, content=rst) 
        
        rst["msg"] =  f"Success to {'Temporary' if is_temporary else ''} SubModel Save !!"
        return JSONResponse(status_code=200, content=rst) 

    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 



async def submodelDeleteEvent(userinfo, submodel_seq = ""):

    rstData = { "result" : "error", "msg" : f"Failed to SuBModel Delete !!" , "data" : ""}

    try:

        if submodel_seq  == "":
            return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "SubModel Seq is Blank !!" , "data" : ""}) 


        ## 현상태 비교
        ## 현재 시퀀스가 있을경우 해당 상태 체크
        ## 없을때는 시퀀스가 최근에 저장된게 있으면 리턴
        if submodel_seq != "":
            sql  = f"""
                --내부적으로 배포가 되었으면
                select status
                from aasrepo.submodels
                where submodel_seq = {submodel_seq}
                    and status in ( 'temporary', 'draft' )
        """
            rst = await async_postQueryDataOne(sql, log_type = "SUBMODEL", user_seq=userinfo.user_seq)

            if (rst["result"] == "ok" and rst["data"] == "" ):
                return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Target Data Status is not Draft or Temporary. Please!! Reload Data." , "data" : ""}) 

        else:
            return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "SUBModel Seq is Blank !!" , "data" : ""}) 


        sql =  f"""
                with base_data as (
                    select submodel_seq
                    from aasrepo.submodels
                    where submodel_seq = {submodel_seq}
                ), del_models as (

                    delete from aasrepo.submodels a
                    using base_data b 
                    where a.submodel_seq = b.submodel_seq

                ), del_img as (
                    delete from aasrepo.submodel_image a
                    using base_data b
                        where a.submodel_seq = b.submodel_seq
                )

                select submodel_seq 
                from base_data
                
"""
        
        rst = await async_postQueryDataOne(sql, None, True, userinfo.user_seq, "SUBMODEL" )

        if rst["result"] != 'ok' or rst["data"] == "":
            rst["msg"] = "Failed to SUBModel Delete !!"
            return JSONResponse(status_code=400, content=rst)

        rst['msg'] = f"Success to Delete !! ({rst['data']})"
        return JSONResponse(status_code=200, content=rst)
    
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 
    


async def aasSubModelImportEvent(userinfo, file, id):
    """
    AAS SubModel Import
    """

    if not file.filename.endswith(".json"): 
        return JSONResponse(status_code=400, content={"result": "error", "msg": "Unsupported file type. Only .json files are allowed.", "data": ""})

    try:
        contents = await file.read()

        json_data = json.loads(contents.decode("utf-8"))

        # BOM(Byte Order Mark) 문자 제거
        # json 에서 escape 처리된 문자 (\\uFEFF)로 존재하기 때문에 파싱 후 dict에서 제거해야 함

        json_data = remove_bom(json_data)

        submodel_id = json_data.get("id")
        semantic_id = json_data.get("semanticId")

        # id, semantic id 체크
        if not submodel_id and not semantic_id:
            return JSONResponse(status_code=400, content={"result": "error", "msg": "'id', 'Semantic ID' are missing in the Submodel file.", "data": ""})
        elif not submodel_id:
            return JSONResponse(status_code=400, content={"result": "error", "msg": "'id' is missing in the Submodel file.", "data": ""})
        elif not semantic_id:
            return JSONResponse(status_code=400, content={"result": "error", "msg": "'Semantic ID' is missing in the Submodel file.", "data": ""})

        #   "semanticId": {
        #     "type": "ExternalReference",
        #     "keys": [
        #       {
        #         "type": "GlobalReference",
        #         "value": "Semantic ID Value"
        #       }
        #     ]
        #   }
        semantic_id_value = None
        try:
            keys = json_data["semanticId"]["keys"]
            if isinstance(keys, list) and keys: # list, keys exist 체크
                semantic_id_value = keys[0].get("value", "")
        except Exception:
            semantic_id_value = None

        if not semantic_id_value:
            return JSONResponse(status_code=400, content={"result": "error", "msg": "'Semantic ID' is missing in the Submodel file.", "data": ""})


        if not id:
            id_chk_rst = await duplicateSubModelIdCheckEvent(submodel_id, "")

            if id_chk_rst:
                return JSONResponse(status_code=400, content={ "result" : "error", "msg" : f"AAS Submodel Template ID '{submodel_id}' already exists." , "data" : ""}) 
        else:
            if submodel_id != id:
                return JSONResponse(status_code=400, content={ "result" : "error", "msg" : f"Submodel ID '{id}' differ from parameter id '{submodel_id}'." , "data" : ""})
        
    except Exception as e:
        return JSONResponse(status_code=400, content={"result": "error", "msg": f"Failed to import submodel: {str(e)}", "data": ""})

    return JSONResponse(status_code=200, content={"result": "ok", "msg": "Submodel import successful", "data": json_data})

async def aasSubModelDownloadEvent(userinfo, id):


    metadata = await aasSubmodelMetadata(id)

    if not metadata:
        return JSONResponse(status_code=404, content={"result": "error", "msg": "Submodel metadata not found", "data": ""})

    try:
        json_data = metadata
    except json.JSONDecodeError as e:
        return JSONResponse(status_code=500, content={"result": "error", "msg": f"Invalid JSON format in metadata: {str(e)}", "data": ""})

    # JSON 변환
    buffer = io.BytesIO()
    buffer.write(json.dumps(json_data, ensure_ascii=False, indent=4).encode("utf-8"))
    buffer.seek(0)

    return StreamingResponse(
        content=buffer,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=submodel_{id}.json"}
    )


# AAS Submodel Json 데이터 조회
async def aasSubmodelMetadata(model_key):
    
    sql = f"""
               SELECT submodels.metadata
                 FROM aasrepo.submodels
                WHERE submodels.submodel_seq = {model_key};
            """
    rstData = await async_postQueryDataOne(sql)
    return rstData["data"]


# dict, list 안에 bom 문자 제거
def remove_bom(obj):
    if isinstance(obj, dict):
        return {k: remove_bom(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [remove_bom(v) for v in obj]
    elif isinstance(obj, str):
        return obj.replace('\ufeff', '')
    else:
        return obj