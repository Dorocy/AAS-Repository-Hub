import requests
import urllib3
import json
import re
import asyncio
import psycopg
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from processor.postgresProcess import *
from tools.cryptoTool import encrypt_data, decrypt_data, generate_custom_symmetric_key
from tools.stringTool import convert_tuple_to_json_list, is_numeric_string, dollarSign
from tools.cryptoTool import create_access_token, create_full_token, check_password, encrypt_password, create_reset_mail_token, decode_reset_mail_token
from config.config import get_config_value
from io import BytesIO


async def getCodeListEvent(userinfo, type, ref_code1:str = "", ref_code2: str = "", ref_code3: str = ""):

    lang_code = "1" if userinfo is None else userinfo.lang_code

    rstData = { "result" : "error", "msg" : "Error Get Code List" , "data" : ""}

    sql = f"""
            select *
            from aasrepo.fncodelist('{type}', '{lang_code}', '{ref_code1}', '{ref_code2}', '{ref_code3}') 
                
            """
    

    try:
        rst = await async_postQueryDataOne(sql)

        if rst["result"] != "ok" :
            return JSONResponse(status_code=400, content=rst) 
        
        return JSONResponse(status_code=201, content=rst) 
        
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 
    

async def verificationEvent(userinfo, metadata, target_type, target_seq, target_id):
    
    metadata_bytes = json.dumps(metadata).encode("utf-8")
    files = {
        "file": ("metadata.json", BytesIO(metadata_bytes), "application/json")
    }

    keti_api_url = get_config_value('keti_api', 'url')
    api_url = f"{keti_api_url}/verification/metamodel"

    try:
        response = requests.post(api_url, files=files, verify=False)
        validation_response = response.json()
        
        if validation_response.get("status").lower() == 'false': # API 호출 오류
            validation_status = "error"
            validation_result = json.dumps(validation_response.get("error"), ensure_ascii=False)
        else:
            validation_status = validation_response.get("verificiation").get("result")
            validation_result = json.dumps(validation_response.get("verificiation").get("message"), ensure_ascii=False)

        sql = """
            INSERT INTO aasrepo.validations
                (target_type, target_seq, target_id, validation_result, description, status, create_user_seq, create_date)
            VALUES (%s, %s, %s, %s, '', %s, %s, localtimestamp)
            RETURNING validation_seq;
        """

        args = (
            target_type,
            target_seq if target_seq else None,
            target_id,
            validation_result,
            validation_status,
            userinfo.user_seq
        )

        sql_rst = await async_postQueryDataOne(sql, None, True, userinfo.user_seq, target_type, tuple(args))


        if sql_rst.get('result') != 'ok':       
            return {"result" : "error", "msg" : sql_rst, "data" : ""}

        if validation_response.get("status").lower() == 'false': # API 호출 오류
            return {"result" : "error", "msg" : json.dumps(validation_response.get("error"), ensure_ascii=False), "data" : ""}
        elif validation_response.get("verificiation").get("result").lower() == 'fail': # 검증결과 Pass가 아닐 때 status_code=500
            return { "result" : "fail", "msg" : f"{target_type} verification failed. Please check the model structure and try again.", "data" : json.dumps(validation_response.get("verificiation").get("message"), ensure_ascii=False)}
        elif validation_response.get("verificiation").get("result").lower() == 'pass':
            return {"result" : "ok", "msg" : "", "data" : ""}
        else:
            return {"result" : "error", "msg" : f"{target_type} verification failed", "data" : ""}
    except Exception as e:
        return {"result" : "error", "msg" : f"{target_type} verification API call failed", "data" : ""}
    
async def fileListEvent(target_type, target_seq):
    """
    metadata에서 File 노드를 추출해
    CTE(WITH files AS ..)로 만든 뒤
    aasmodel_attachments와 JOIN하여 결과를 리턴
    """

    try:
        # metadata 조회
        sql_meta = f"""
            SELECT aas.aasmodel_seq seq,
                   aas.metadata metadata
              FROM aasrepo.aasmodels aas
             WHERE aas.aasmodel_seq = {target_seq}
               AND '{target_type}' = 'aasmodel' 
          UNION ALL 
            SELECT ins_aas.aasmodel_seq seq,
                   aasrepo.fn_instance_merge(ins.instance_seq) metadata
              FROM aasrepo.aasinstance ins JOIN aasrepo.aasinstance_aasmodels ins_aas
                                             ON ins_aas.instance_seq = ins.instance_seq
             WHERE ins.instance_seq = {target_seq}
               AND '{target_type}' = 'instance';
        """
        rst_meta = await async_postQueryDataSet(sql_meta)
        if rst_meta["result"] != "ok" or not rst_meta["data"]:
            return { "files": [] }
        metadata = rst_meta["data"][0]["metadata"]
        aasmodel_seq = rst_meta["data"][0]["seq"]
        

        # metadata → File (path, obj) 찾기
        def find_file_objects(obj, path="$"):
            out = []
            if isinstance(obj, dict):
                if obj.get("modelType") == "File":
                    out.append({"path": path, "obj": obj})
                for k, v in obj.items():
                    out += find_file_objects(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    out += find_file_objects(item, f"{path}[{i}]")
            return out

        file_nodes = find_file_objects(metadata)

        if not file_nodes:
            # File 노드가 하나도 없으면 빈 리스트
            return { "files": [] }

        # CTE
        rows = []
        for node in file_nodes:
            p = node["path"].replace("'", "''") # 
            o = json.dumps(node["obj"], ensure_ascii=False).replace("'", "''")
            rows.append(f"  SELECT '{p}' AS node_level, '{o}'::jsonb AS obj")

        cte = "WITH files AS (\n" + "\n  UNION ALL\n".join(rows) + "\n)\n"

        base_url = get_config_value("file", "url")

        # aasmodel_attachments와 JOIN
        sql = cte + f"""
         SELECT att.attachment_seq,
                att.aasmodel_seq,
                att.filename,
                att.realpath,
                files.node_level,
                files.obj,
                concat('http://', '{base_url}', att.realpath) AS link
           FROM files
                        JOIN aasrepo.aasmodel_attachments att
                          ON att.aasmodel_seq = {aasmodel_seq}
                         AND '/' || att.filename = files.obj ->> 'value'
        """

        rst = await async_postQueryDataSet(sql)
        if rst["result"] != "ok":
            return { "files": [] }

        return { "files": rst["data"] }

    except Exception as e:
        return { "files": [] }
