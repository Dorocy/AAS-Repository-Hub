import requests
import urllib3
import json
import re
import asyncio
import psycopg
import base64
from typing import Union, Optional, Any
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
from processor.postgresProcess import *
from tools.stringTool import dollarSign, validate_json
from config.config import get_config_value
from zipfile import ZipFile
from io import BytesIO
import shutil
from app.etcModule import *


## AAS 모델 리스트
async def aasModelListEvent(userinfo, title, searchKey, category_seq, pageNumber = 1, pageSize = 10, pageMode = False):

    lang_code = userinfo.lang_code if  userinfo is not None  else "1"

    user_group_seq = userinfo.user_group_seq if userinfo is not None else 3

    ## title == '' 일경우만 searchkey , 타이틀은 메인에서 넘어오는것
    if title != '':
        searchKey = ''
        
            
    ##메타 서치
    meta_flag, meta_string = validate_json(searchKey)

    ##메타스트링에 key가 없으면, False
    if meta_flag:
        if not "key" in meta_string or not "value" in meta_string :
            meta_flag = False
    
    if meta_flag:
        searchKey = ""

    rstData = { "result" : "error", "msg" : "Failed to get list" , "data" : ""}

#     sql = f"""
#     with min_tbl as (
#         select aasmodel_id, min(aasmodel_seq) as min_aasmodel_seq
#         from aasrepo.aasmodels
#         group by aasmodel_id
#         order by min_aasmodel_seq desc
#     ),  last_aasmodel_tbl as (
#         select a.aasmodel_id, a.status, max(a.aasmodel_seq) as max_aasmodel_seq, b.min_aasmodel_seq
#         from aasrepo.aasmodels a
#         left join min_tbl b on a.aasmodel_id = b.aasmodel_id
#         group by a.aasmodel_id, a.status, b.min_aasmodel_seq
#         order by 3 desc, 4 desc
#     )

#     select dense_rank() over ( order by aa.min_aasmodel_seq desc) as group_seq 
#     	, row_number() over (partition by aa.aasmodel_id  order by a.aasmodel_seq desc) as in_seq 
#         , a.aasmodel_seq, a.aasmodel_name,  a.aasmodel_id, a."version", a.aasmodel_template_id, a."type",  a.description, a.category_seq
#         ,  CASE {lang_code}
#                 WHEN 1  THEN b.category_name
#                 WHEN 2  THEN b.category_name2
#                 WHEN 3  THEN b.category_name3
#                 WHEN 4  THEN b.category_name4
#                 WHEN 5  THEN b.category_name5
#                 ELSE b.category_name END as category_name, a.status, aasrepo.fncodenm(a.status, {lang_code} ) as status_nm, a.create_date
#         , c.aasmodel_img, c.mime_type, c.filename
#     from aasrepo.aasmodels a
#     left join last_aasmodel_tbl aa on a.aasmodel_seq = aa.max_aasmodel_seq
#     join  aasrepo.categories b on  a.category_seq = b.category_seq
#     left join aasrepo.aasmodel_image c on a.aasmodel_seq = c.aasmodel_seq
#     where ('{category_seq}' =  case left('{category_seq}', 6) 
# 				when 'GRP100' then b.refcode1 
# 				when 'GRP200' then b.refcode2 
# 				when 'GRP300' then b.refcode3
# 				else b.category_seq::varchar end or '{category_seq}' = '')
#         and ( lower(a.aasmodel_name) like '%' || lower('{searchKey}') || '%' 
#             or lower(a.description) like '%' || lower('{searchKey}') || '%' 
#             or lower(a.aasmodel_id) like '%' || lower('{searchKey}') || '%' 
#             or (a.aasmodel_template_id) like '%' || lower('{searchKey}') || '%' 
#             )
#         and lower(a.aasmodel_name) like '%' || lower('{title}') || '%' 
#         { f"""and jsonb_path_exists(metadata, '$.**."{meta_string["key"]}" ? (@ == "{meta_string["value"]}")')  """ if meta_flag else ''  }
#         and ( (3={user_group_seq} and a.status in ('published')  )
#              or {user_group_seq} in (1, 2)	) --일반사용자 일경우 배포된것만
#         and  aa.max_aasmodel_seq is not null
    
# """

    json_filter = (
        f"""and jsonb_path_exists(metadata, '$.**."{meta_string["key"]}" ? (@ == "{meta_string["value"]}")')"""
        if meta_flag else ''
    )

    sql = f"""
    WITH min_tbl AS (
        SELECT aasmodel_id, MIN(aasmodel_seq) AS min_aasmodel_seq
        FROM aasrepo.aasmodels
        GROUP BY aasmodel_id
        ORDER BY min_aasmodel_seq DESC
    ), last_aasmodel_tbl AS (
        SELECT a.aasmodel_id, a.status, MAX(a.aasmodel_seq) AS max_aasmodel_seq, b.min_aasmodel_seq
        FROM aasrepo.aasmodels a
        LEFT JOIN min_tbl b ON a.aasmodel_id = b.aasmodel_id
        GROUP BY a.aasmodel_id, a.status, b.min_aasmodel_seq
        ORDER BY 3 DESC, 4 DESC
    )

    SELECT DENSE_RANK() OVER (ORDER BY aa.min_aasmodel_seq DESC) AS group_seq,
        ROW_NUMBER() OVER (PARTITION BY aa.aasmodel_id ORDER BY a.aasmodel_seq DESC) AS in_seq,
        a.aasmodel_seq, a.aasmodel_name, a.aasmodel_id, a."version", a.aasmodel_template_id, a."type", a.description, a.category_seq,
        CASE {lang_code}
            WHEN 1 THEN b.category_name
            WHEN 2 THEN b.category_name2
            WHEN 3 THEN b.category_name3
            WHEN 4 THEN b.category_name4
            WHEN 5 THEN b.category_name5
            ELSE b.category_name
        END AS category_name,
        a.status,
        aasrepo.fncodenm(a.status, {lang_code}) AS status_nm,
        a.create_date,
        c.aasmodel_img, c.mime_type, c.filename
    FROM aasrepo.aasmodels a
    LEFT JOIN last_aasmodel_tbl aa ON a.aasmodel_seq = aa.max_aasmodel_seq
    JOIN aasrepo.categories b ON a.category_seq = b.category_seq
    LEFT JOIN aasrepo.aasmodel_image c ON a.aasmodel_seq = c.aasmodel_seq
    WHERE ('{category_seq}' = CASE LEFT('{category_seq}', 6)
                WHEN 'GRP100' THEN b.refcode1
                WHEN 'GRP200' THEN b.refcode2
                WHEN 'GRP300' THEN b.refcode3
                ELSE b.category_seq::VARCHAR END OR '{category_seq}' = '')
    AND (LOWER(a.aasmodel_name) LIKE '%' || LOWER('{searchKey}') || '%'
        OR LOWER(a.description) LIKE '%' || LOWER('{searchKey}') || '%'
        OR LOWER(a.aasmodel_id) LIKE '%' || LOWER('{searchKey}') || '%'
        OR LOWER(a.aasmodel_template_id) LIKE '%' || LOWER('{searchKey}') || '%')
    AND LOWER(a.aasmodel_name) LIKE '%' || LOWER('{title}') || '%'
    {json_filter}
    AND ((3={user_group_seq} AND a.status IN ('published'))
        OR {user_group_seq} IN (1, 2))
    AND aa.max_aasmodel_seq IS NOT NULL
"""

    try:
        
        rst = await async_postQueryPageData(sql, pageNumber, pageSize, "", "", None, True, False, pageMode)

        if rst["result"] != "ok" :
            return JSONResponse(status_code=400, content=rstData) 
        
        return JSONResponse(status_code=200, content=rst) 
        
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 
    

## AAS 모델 중복 체크 (중복아닐경우 False, 나머지 True)
async def duplicateAasmodelIdCheckEvent(aasmodel_id, aasmodel_seq : Union [int, str] = '', user_seq:int=0):
    sql = f"""
    select aasmodel_id
    FROM aasrepo.aasmodels a
    where aasmodel_id = {dollarSign(aasmodel_id)}
        and (aasmodel_seq::varchar <> '{aasmodel_seq}' or '{aasmodel_seq}' = '' )
    """

    try:
        rst = await async_postQueryDataOne(sql, user_seq=user_seq)

        if rst["result"] == "ok" and rst["data"] == "":
            return False

        return True
        
    except Exception as e:
        return True

## 임시저장 // 저장 시 등록된 시퀀스 체크 
async def aasmodelSaveCheckEvent(aasmodel_id):
    sql = f"""
    select aasmodel_seq
    FROM aasrepo.aasmodels a
    where aasmodel_id = {dollarSign(aasmodel_id)}
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


## AAS MODEL ID 체크
async def aasmodelIdCheckEvent(aasmodel_id, aasmodel_seq : Union [int, str] = ''):
    rstData = { "result" : "error", "msg" : "Duplicate AAS Model_Id Exists. !!" , "data" : False}

    try:
        
        if not await duplicateAasmodelIdCheckEvent(aasmodel_id, aasmodel_seq):
            return JSONResponse(status_code=200, content={ "result" : "ok", "msg" : "Duplicate AAS Model ID Not Exists. !!" , "data" : False}) 
        else:
            return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Duplicate AAS Model ID Exists. !!" , "data" : True}) 
        
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 
    


## AAS 모델 상세 
async def aasmodelDetailEvent(userinfo, aasmodel_seq):
    lang_code = "1" if userinfo is None else userinfo.lang_code
        
    rstData = { "result" : "error", "msg" : "Duplicate AAS Model Not Exists. !!" , "data" : ""}

    sql = f"""
select a.aasmodel_seq, a.aasmodel_name, a."version", a.aasmodel_id, a.aasmodel_template_id, a."type", a.category_seq
    , aasrepo.fncodenm(a.category_seq::varchar, {lang_code}, 'category') as category_name, a.description, a.status, a.source_project
	, a.metadata
	, c.aasmodel_img, c.mime_type, c.filename
from aasrepo.aasmodels a
left join aasrepo.aasmodel_image c on a.aasmodel_seq = c.aasmodel_seq
where a.aasmodel_seq = {aasmodel_seq}
    """

    try:
        rst = await async_postQueryDataSet(sql)

        if rst["result"] != "ok" and len(rst["data"]) == 0:
            return JSONResponse(status_code=400, content={ "result" : "ok", "msg" : "AAS Model ID Is Not Exists. !!" , "data" : ""}) 

        json_str = await fileListEvent('aasmodel', aasmodel_seq)
        
        if isinstance(rst["data"][0], dict):
            rst["data"][0].update(json_str)

        return JSONResponse(status_code=200, content=rst) 
        
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 

## AAS 모델 히스토리 리스트
async def aasmodelHistoryListEvent(userinfo, aasmodel_seq):

    user_group_seq = userinfo.user_group_seq if userinfo is not None else 3
        
    rstData = { "result" : "error", "msg" : "History Not Exists!!" , "data" : ""}

    sql = f"""
    with aasmodel_list as (
        
        select a.aasmodel_seq as id, case when  a.status != 'published' then a.status else coalesce(a.version, '') end as text
        from aasrepo.aasmodels a
        join aasrepo.aasmodels aa on a.aasmodel_id = aa.aasmodel_id and aa.aasmodel_seq = {aasmodel_seq}
        where ( (3={user_group_seq} and a.status in ( 'published')) or {user_group_seq} in (1, 2)  )
        order by a.aasmodel_seq	desc	 

    )    

    select id, text
    from aasmodel_list 
    """

    try:
        rst = await async_postQueryDataSet(sql)

        if rst["result"] != "ok" and len(rst["data"]) == 0:
            return JSONResponse(status_code=400, content=rst)

        return JSONResponse(status_code=200, content=rst) 
        
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 



## AAS모델 임시 및 저장
async def aasmodelSaveEvent(userinfo, body, image: Optional[UploadFile] = File(None), is_temporary:bool = True, attachments: Optional[UploadFile] = File(None)):

    rstData = { "result" : "error", "msg" : f"Failed to {'Temporary' if is_temporary else ''} AASModel Save !!" , "data" : ""}
    aasmodel_template_id = ""
    status = ""
    aasmodel_id = ""
    aasmodel_seq = ""
    custom_args = []

    if "status" in body :
        status = body["status"]
    if "aasmodel_template_id" in body:
        aasmodel_template_id = body["aasmodel_template_id"]
    if "aasmodel_id" in body :
        aasmodel_id = body["aasmodel_id"]
    if "aasmodel_seq" in body :
        aasmodel_seq = body["aasmodel_seq"]

    
    # KETI 검증 API
    if not is_temporary:

        rst = await verificationEvent(userinfo, json.loads(body["metadata"]), 'aasmodel', aasmodel_seq, aasmodel_id)

        if rst["result"] == "fail": 
            return JSONResponse(status_code=500, content={"result": "error", "msg": rst["msg"], "data": rst["data"]})
        elif rst["result"] == "ok":
            pass
        else:
            return JSONResponse(status_code=400, content={"result": "error", "msg": rst["msg"], "data": ""})
        

    # 저장
    try:

        if aasmodel_id  == "":
            return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "AAS Model_Id is Blank !!" , "data" : ""}) 

        ## aasmodel_template_id 없으면 최초 등록이니깐
        ## template 아이디가 버전마다 다르기 때문에 version 으로 변경
        
        if ((body["version"] == "" or body["version"] == "0.0" ) and aasmodel_seq == ""):
            ## 중복 aasmode_id 체크
            if await duplicateAasmodelIdCheckEvent(aasmodel_id, aasmodel_seq, user_seq=userinfo.user_seq):
                return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Duplicate AAS Model_Id Exists. !!" , "data" : ""}) 
            
        
        ## 현상태 비교
        ## 현재 시퀀스가 있을경우 해당 상태 체크
        ## 없을때는 시퀀스가 최근에 저장된게 있으면 리턴
        if aasmodel_seq != "":
            sql  = f"""
                --내부적으로 배포가 되었으면
                select status
                from aasrepo.aasmodels
                where aasmodel_seq = {aasmodel_seq}
        """
            rst = await async_postQueryDataOne(sql, log_type = "AASMODEL", user_seq=userinfo.user_seq)

            if (rst["result"] == "ok" and rst["data"] != status):
                return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Target Data has different data(No draft data). Please!! Reload Data." , "data" : ""}) 


        ### 가장 최근 저장된거 있으면 해당된것 가져오기
        sql = f"""
        select aasmodel_seq
        FROM aasrepo.aasmodels a
        where aasmodel_id = {dollarSign(aasmodel_id)}
            and status in ( 'temporary', 'draft' )
        limit 1
        """

        rst = await async_postQueryDataOne(sql, log_type = "AASMODEL", user_seq=userinfo.user_seq)

        if rst["data"] != "":
            aasmodel_seq = rst["data"]
        

        custom_args.append(json.dumps(json.loads(body["metadata"]), ensure_ascii=False)  if body["metadata"] !="" else '{}')

        ##-> 저장/임시저장 template_id, 초기화:배포시마다 새로 채번 될꺼기때문에 -> 재적용 (끝 번호만 바뀌는)
        ##, {dollarSign(aasmodel_template_id) if aasmodel_template_id != "" else 'NULL'}
        ##{dollarSign(json.dumps(json.loads(body["metadata"]), ensure_ascii=False))  if body["metadata"] !="" else 'NULL' }
        sql = f"""
    with inserted as (
        INSERT INTO aasrepo.aasmodels (aasmodel_seq, aasmodel_name, aasmodel_id
            , aasmodel_template_id, version, type
            , category_seq, description, status,  metadata, create_user_seq, create_date)
        select { aasmodel_seq if aasmodel_seq != "" else "nextval('aasrepo.aasmodels_aasmodel_seq_seq'::regclass)"}, { dollarSign(body["aasmodel_name"])}, {dollarSign(aasmodel_id)}
            , {dollarSign(aasmodel_template_id) if aasmodel_template_id != "" else 'NULL'}
            , {dollarSign(body["version"]) if body["version"] != "" else 'NULL'}, NULL
            , {body["category_seq"] if str(body["category_seq"]) != "" else 'NULL' }
            , {dollarSign(body["description"])}
            , '{ "temporary" if is_temporary else "draft" }'
            , %s
            , {userinfo.user_seq}, localtimestamp
        ON CONFLICT (aasmodel_seq) 
        DO UPDATE SET
            aasmodel_name = EXCLUDED.aasmodel_name, type = EXCLUDED.type
            , category_seq = EXCLUDED.category_seq, description = EXCLUDED.description, status = EXCLUDED.status
            , metadata = EXCLUDED.metadata, create_user_seq = EXCLUDED.create_user_seq, create_date = EXCLUDED.create_date
        returning aasmodel_seq
    )
        """

        filename = None
        mime_type = None
        image_data = None
        

        ## TODO 이미지 저장시 오류 체크 필요
        if image and image.filename:
            filename = image.filename
            mime_type = image.content_type
            image_data = await image.read() 
            image_data = base64.b64encode(image_data).decode("utf-8")

            sql = sql + f"""
                , insert_img as (
                    insert into aasrepo.aasmodel_image ( aasmodel_seq, aasmodel_img, filename, mime_type)
                    select aasmodel_seq, %s, %s, %s 
                    from inserted
                    ON CONFLICT (aasmodel_seq) 
                    DO UPDATE SET
                    aasmodel_img = EXCLUDED.aasmodel_img
                    , filename = EXCLUDED.filename
                    , mime_type = EXCLUDED.mime_type
                    returning aasmodel_seq
                )
        """
            custom_args.extend([image_data, filename, mime_type])
        else:
             sql = sql + f"""
                , del_img as (
                    delete from aasrepo.aasmodel_image a
                    using inserted b
                        where a.aasmodel_seq = b.aasmodel_seq
                )
        """
    
            
        ## 일반 저장일떄 혹시 임시저장 있으면 삭제 (=동일안 aasmodel_id)
        if not is_temporary:
            
            sql = sql + f"""
                , deleted as (
	                delete from aasrepo.aasmodels
                    where status = 'temporary'
                        and aasmodel_id = {dollarSign(aasmodel_id)}
                    returning aasmodel_seq
                )

            """
            
        
        
        # 파일명 리스트만 추출
        extracted_files = {}
        attachments_list = []
        attached_files = set()
        if attachments and attachments.filename.endswith('.aasx'):
            file_bytes = await attachments.read()
            metadata_str = json.loads(body['metadata'])
            extracted_files = await extractAttachments(file_bytes, metadata_str)

            for file_path, content in extracted_files.items():
                attachments_list.append({
                    'filename': file_path,
                    'realpath': file_path.replace('\\', '/')
                })
                attached_files.add(os.path.basename(file_path))

        if attachments_list:
            url_prefix = get_config_value('file', 'mainpath')
            sql += f"""
            , insert_attachments AS (
            INSERT INTO aasrepo.aasmodel_attachments (aasmodel_seq, filename, realpath)
            SELECT aasmodel_seq,
                    f.filename,
                    %s || '/' || aasmodel_seq::text || '/' || f.realpath
                FROM inserted,
                    json_to_recordset(%s) AS f(filename text, realpath text)
            ON CONFLICT (aasmodel_seq, filename) DO UPDATE
                SET realpath = EXCLUDED.realpath
            RETURNING aasmodel_seq
            )
            """
            custom_args.extend([url_prefix, json.dumps(attachments_list)])
        elif aasmodel_template_id != "": #FIXME 조건 수정필요
            sql += f"""
            , insert_attachments AS (
                INSERT INTO aasrepo.aasmodel_attachments (aasmodel_seq, filename, realpath)
                SELECT
                    inserted.aasmodel_seq,
                    att.filename,
                    att.realpath
                FROM inserted
                                INNER JOIN (
                                                SELECT aasmodel_seq
                                                  FROM aasrepo.aasmodels
                                                 WHERE aasmodel_template_id = {dollarSign(aasmodel_template_id)}
                                                   AND status = 'published'
                                              ORDER BY aasmodel_seq DESC
                                                 LIMIT 1
                                            ) AS prev
                                        ON 1=1
                                INNER JOIN aasrepo.aasmodel_attachments AS att
                                        ON att.aasmodel_seq = prev.aasmodel_seq
                ON CONFLICT (aasmodel_seq, filename) DO UPDATE
                    SET realpath = EXCLUDED.realpath
                RETURNING aasmodel_seq
                )
            """


        # 최종 SELECT
        sql += """
                    SELECT aasmodel_seq 
                      FROM inserted
        """

        rst = await async_postQueryDataOne(sql, None, True, userinfo.user_seq, "AASMODEL", tuple(custom_args) )
        if rst.get('result') != 'ok' or rst.get('data') == '':
            return JSONResponse(status_code=400, content=rst)

        aasmodel_seq = rst['data']

        # 실제 파일 쓰기 
        if extracted_files:
            upload_dir = get_config_value('file', 'fullpath')
            upload_dir = f"{upload_dir}/{aasmodel_seq}"
            os.makedirs(upload_dir, exist_ok=True)
            for file_path, content in extracted_files.items():
                save_path = os.path.join(upload_dir, file_path).replace('\\', '/')
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                with open(save_path, 'wb') as out_file:
                    out_file.write(content)

        rst['msg'] = f"Success to {'Temporary' if is_temporary else ''} Save !!"
        return JSONResponse(status_code=200, content=rst)

    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 
    


async def aasmodelDeleteEvent(userinfo, aasmodel_seq = ""):

    rstData = { "result" : "error", "msg" : f"Failed to AASModel Delete !!" , "data" : ""}

    try:

        if aasmodel_seq  == "":
            return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "AASModel Seq is Blank !!" , "data" : ""}) 


        ## 현상태 비교
        ## 현재 시퀀스가 있을경우 해당 상태 체크
        ## 없을때는 시퀀스가 최근에 저장된게 있으면 리턴
        if aasmodel_seq != "":
            sql  = f"""
                --내부적으로 배포가 되었으면
                select status
                from aasrepo.aasmodels
                where aasmodel_seq = {aasmodel_seq}
                    and status in ( 'temporary', 'draft' )
        """
            rst = await async_postQueryDataOne(sql, log_type = "AASMODEL", user_seq=userinfo.user_seq)

            if (rst["result"] == "ok" and rst["data"] == "" ):
                return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Target Data Status is not Draft or Temporary. Please!! Reload Data." , "data" : ""}) 

        else:
            return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "AASModel Seq is Blank !!" , "data" : ""}) 


        sql =  f"""
                with base_data as (
                    select aasmodel_seq
                    from aasrepo.aasmodels
                    where aasmodel_seq = {aasmodel_seq}
                ), del_models as (

                    delete from aasrepo.aasmodels a
                    using base_data b 
                    where a.aasmodel_seq = b.aasmodel_seq

                ), del_img as (
                    delete from aasrepo.aasmodel_image a
                    using base_data b
                        where a.aasmodel_seq = b.aasmodel_seq
                ), del_attachments as (
                    delete from aasrepo.aasmodel_attachments a
                    using base_data b
                        where a.aasmodel_seq = b.aasmodel_seq
                )

                select aasmodel_seq 
                from base_data
                
"""
        
        rst = await async_postQueryDataOne(sql, None, True, userinfo.user_seq, "AASMODEL" )

        if rst["result"] != 'ok' or rst["data"] == "":
            rst["msg"] = "Failed to AASModel Delete !!"
            return JSONResponse(status_code=400, content=rst)
        
        # 파일 삭제
        try:
            upload_dir = get_config_value('file', 'fullpath')
            target_dir = f"{upload_dir}/{aasmodel_seq}"
            if aasmodel_seq and os.path.exists(target_dir):
                shutil.rmtree(target_dir) # 디렉토리 하위 전체 삭제
        except Exception as file_err:
            dbLogger(f"File delete fail aasmodel_seq [{aasmodel_seq}]: {file_err}", 'File delete', "", user_seq=userinfo.user_seq)

        rst['msg'] = f"Success to Delete !! ({rst['data']})"
        return JSONResponse(status_code=200, content=rst)
    
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 
    



# file인 경우 contentType 필수입력. 첨부파일 있는 경우에만 검사
def find_invalid_file_nodes(data, path="", attached_files: Optional[set] = None):
    invalid_nodes = []

    if isinstance(data, dict):
        if data.get("modelType") == "File":
            value = data.get("value", "")
            content_type = data.get("contentType", "")

            # 첨부파일 있는 경우에만 검사
            if value and attached_files and value in attached_files:
                if not content_type or content_type.strip() == "":
                    invalid_nodes.append(path or "/")

        for key, val in data.items():
            new_path = f"{path}/{key}" if path else key
            invalid_nodes += find_invalid_file_nodes(val, new_path, attached_files)

    elif isinstance(data, list):
        for idx, item in enumerate(data):
            new_path = f"{path}[{idx}]"
            invalid_nodes += find_invalid_file_nodes(item, new_path, attached_files)

    return invalid_nodes



async def extractAttachments(file_bytes: bytes, env_json: dict) -> dict[str, bytes]:
    """ basyx-java-server-sdk FileElementPathCollector 참고
    Submodel의 submodelElements 모델 타입이 file인 경우 (Supplemental Files 확인)
    """

    file_paths = set()

    def collect_paths(node: Any):
        if isinstance(node, dict):
            if node.get("modelType") == "File":
                val = node.get("value") or ""
                val = val.strip()
                if val:
                    file_paths.add(val.lstrip("/"))
            # 하위 노드 재귀 탐색
            for v in node.values():
                collect_paths(v)
        elif isinstance(node, list):
            for item in node:
                collect_paths(item)

    collect_paths(env_json)

    # 해당 경로 파일만 추출
    attachments = {}
    with ZipFile(BytesIO(file_bytes)) as zip_file:
        for entry in zip_file.infolist():
            fname = entry.filename
            if fname in file_paths:
                with zip_file.open(entry) as f:
                    attachments[fname] = f.read()

    return attachments