from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.aasSubModelModule import *
from app.etcModule import *

class SubmodelMergeRequest(BaseModel):
    aasJson: dict
    submodelIds: list[str]

async def aasSubModelMergeEvent(userinfo, body: SubmodelMergeRequest):
    """
    SubModel Merge
    """
        
    try:
        base_aas = body.aasJson
        submodel_ids = body.submodelIds

        # submodel List
        if "submodels" not in base_aas:
            base_aas["submodels"] = []

        if not base_aas.get("assetAdministrationShells"):
            return JSONResponse(status_code=400, content={"result": "error", "msg": "No AssetAdministrationShell found in AAS JSON.",  "data": ""})

        aas = base_aas["assetAdministrationShells"][0]

        # 참조 submodel
        if "submodels" not in aas:
            aas["submodels"] = []

        # 중복 확인
        existing_submodel_ids = {sm.get("id") for sm in base_aas["submodels"]}

        existing_ref_ids = set()

        for ref in aas["submodels"]:
            if ref.get("keys") and isinstance(ref["keys"], list):
                existing_ref_ids.add(ref["keys"][0]["value"]) # submodel id


        # merge
        for submodel_id in submodel_ids:
            response = await aasSubModelDetailEvent(userinfo, submodel_id)

            if isinstance(response, JSONResponse) and response.status_code == 200:
                detail_data = json.loads(response.body)

                if detail_data.get("result") == "ok" and detail_data.get("data"):
                    submodel_metadata = detail_data["data"][0]["metadata"]
                    submodel_id_val = submodel_metadata.get("id")

                    if submodel_id_val:
                        # submodels 배열에 추가
                        if submodel_id_val not in existing_submodel_ids:
                            base_aas["submodels"].append(submodel_metadata)
                            existing_submodel_ids.add(submodel_id_val)

                        # AAS의 참조에 추가
                        if submodel_id_val not in existing_ref_ids:
                            ref = {
                                "type": "ModelReference",
                                "keys": [
                                    {
                                        "type": "Submodel",
                                        "value": submodel_id_val
                                    }
                                ]
                            }
                            aas["submodels"].append(ref)
                            existing_ref_ids.add(submodel_id_val)

        return JSONResponse(status_code=200, content={"result": "ok", "msg": "Submodel merge successful", "data": base_aas})

    except Exception as e:
        return JSONResponse(status_code=500, content={"result": "error", "msg": f"Failed to merge submodel: {str(e)}", "data": ""})


## 인스턴스 리스트 
## 일단 서브리스트는 제외
async def instanceListEvent(userinfo, category_seq = '', searchKey = '', pageNumber = 1, pageSize = 10, pageMode = False):
    rstData = { "result" : "error", "msg" : "Failed to get instance list" , "data" : ""}

    lang_code = "1" if userinfo is None else userinfo.lang_code

    sql = f"""
(    
    select a.instance_seq, a.instance_name, a.description, a.verification, aasrepo.fncodenm(bb.status, {lang_code}, 'code') as status, a.create_user_seq, a.create_date, a.last_mod_user_seq, a.last_mod_date
	, b.aasmodel_seq
	, bb.aasmodel_id, bb.aasmodel_name, bb.aasmodel_id, bb.aasmodel_template_id, bb.description as aasmodel_description, bb."version" as aasmodel_version
	, CASE {lang_code}
        WHEN 1  THEN bb1.category_name
        WHEN 2  THEN bb1.category_name2
        WHEN 3  THEN bb1.category_name3
        WHEN 4  THEN bb1.category_name4
        WHEN 5  THEN bb1.category_name5
        ELSE bb1.category_name END as category_name
    , c.user_id
from aasrepo.aasinstance a
left join aasrepo.aasinstance_aasmodels b 
	on a.instance_seq = b.instance_seq
left join aasrepo.aasmodels bb
	on b.aasmodel_seq = bb.aasmodel_seq
join aasrepo.categories bb1 
	on bb.category_seq = bb1.category_seq
left join aasrepo.users c 
	on a.create_user_seq = c.user_seq    
where ( ( a.user_seq = {userinfo.user_seq} and {userinfo.user_group_seq} = 3)
       or ( {userinfo.user_group_seq} in (1, 2) )
    )
	and ('{category_seq}' =  case left('{category_seq}', 6) 
		when 'GRP100' then bb1.refcode1 
		when 'GRP200' then bb1.refcode2 
		when 'GRP300' then bb1.refcode3
		else bb1.category_seq::varchar end or '{category_seq}' = '')
	and lower(a.instance_name) like '%'|| lower('{searchKey}') ||'%'
order by a.create_date desc
)

"""

    try:
        rst = await async_postQueryPageData(sql, pageNumber, pageSize , "", "", None, True, False, pageMode)


        return rst
        
    except Exception as e:
        rstData["msg"] = str(e)
        return  JSONResponse(status_code=400, content=rstData)  

## 인스턴스 상세 조회    
async def instanceInfoEvent(userinfo, instance_seq):
    rstData = { "result" : "error", "msg" : "Failed to get Instance Info" , "data" : ""}

    lang_code = "1" if userinfo is None else userinfo.lang_code

    sql = f"""

with base_tbl as (
 
    select a.instance_seq, a.instance_name, a.description, a.verification, aasrepo.fncodenm(bb.status, {lang_code}, 'code') as status, a.create_user_seq, a.create_date, a.last_mod_user_seq, a.last_mod_date
        , b.aasmodel_seq, b.metadata as aasmodel_metadata
        , bb.aasmodel_id, bb.aasmodel_name, bb.aasmodel_id, bb.aasmodel_template_id, bb.description as aasmodel_description, bb."version" as aasmodel_version
        , CASE {lang_code}
            WHEN 1  THEN bb1.category_name
            WHEN 2  THEN bb1.category_name2
            WHEN 3  THEN bb1.category_name3
            WHEN 4  THEN bb1.category_name4
            WHEN 5  THEN bb1.category_name5
            ELSE bb1.category_name END as category_name
        , c.user_name
    from aasrepo.aasinstance a
    left join aasrepo.aasinstance_aasmodels b 
        on a.instance_seq = b.instance_seq
    left join aasrepo.aasmodels bb
        on b.aasmodel_seq = bb.aasmodel_seq
    join aasrepo.categories bb1 
        on bb.category_seq = bb1.category_seq
    left join aasrepo.users c on coalesce(a.last_mod_user_seq, a.create_user_seq) = c.user_seq
    
    where ( ( a.user_seq = {userinfo.user_seq} and {userinfo.user_group_seq} = 3)
        or ( {userinfo.user_group_seq} in (1, 2) )
        )
        and a.instance_seq = {instance_seq}
        
) , submodels_tbl as (
	select a.instance_seq, a.aasmodel_seq, row_number() over (order by c.create_date desc) as submodel_no
        , c.submodel_seq, c.metadata as submodel_metadata
        , cc.submodel_id, cc.submodel_name, cc.submodel_semantic_id, cc.description as submodel_description, cc.submodel_version as submodel_version
        , aasrepo.fncodenm(cc.status, {lang_code}, 'code') as status
        , aasrepo.fncodenm(cc.category_seq::varchar , {lang_code}, 'category') 
	from base_tbl a
	join aasrepo.aasinstance_aasmodel_submodels c 
        on a.instance_seq = c.instance_seq and a.aasmodel_seq = c.aasmodel_seq
    left join aasrepo.submodels cc
        on c.submodel_seq = cc.submodel_seq
)  

select row_to_json(r) as rst
from (
	select *
		, (	select array_agg(row_to_json(r)) as submodels from submodels_tbl r) as submodels
	from base_tbl r
) r

"""

    try:
        rst = await async_postQueryDataOne(sql)

        if rst["result"] != "ok" or rst["data"] == "":
            rstData["msg"] = rstData["msg"] + " : " + rst["msg"]
            return JSONResponse(status_code=400, content=rstData) 

        json_str = await fileListEvent('instance', instance_seq)
        
        if isinstance(rst["data"], dict):
            rst["data"].update(json_str)

        return rst
        
    except Exception as e:
        rstData["msg"] = str(e)
        return  JSONResponse(status_code=400, content=rstData)  

##인스턴스 저장
async def instanceSaveEvent(userinfo, body):

    rstData = { "result" : "error", "msg" : f"Failed to Save the instance !!" , "data" : ""}

    instance_seq = body["instance_seq"] if "instance_seq" in body else ""
    instance_name = body["instance_name"] if "instance_name" in body else ""
    description = body["description"] if "description" in body else ""
    verification = body["verification"] if "verification" in body else ""
    aasmodel_seq = body["aasmodel_seq"] if "aasmodel_seq" in body else ""
    submodels = body["submodels"] if "submodels" in body else []


    custom_args = []

    try:
        # if aasmodel_seq  == "" or len(submodels) == 0 or instance_name == "" or verification == "":
        #     return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Missing data exists." , "data" : ""}) 
        
        submodel_sql = ""
        submodel_seq_list = []
        custom_args.append(json.dumps(json.loads(body["aasmodel_metadata"]), ensure_ascii=False)  if body["aasmodel_metadata"] !="" else '{}' )

        for submodel in submodels:
            if submodel["submodel_seq"] != "":
                submodel_seq_list.append(submodel["submodel_seq"])
                if submodel_sql != "" :
                    submodel_sql += " union all "
                submodel_sql += f""" select {submodel["submodel_seq"]} as submodel_seq, %s as submodel_metadata """
                custom_args.append(json.dumps(json.loads(submodel["submodel_metadata"]), ensure_ascii=False) if submodel["submodel_metadata"] !="" else '{}' )

        ##서브모델 중복 체크
        if len(submodel_seq_list) != len(set(submodel_seq_list)):
            return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Duplicate submodel exists." , "data" : ""})

        # if submodel_sql == "":
        #     return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Checked the Submodels Info" , "data" : ""})                 
        
        sql  = f"""

    with ins_instance as (
        INSERT INTO aasrepo.aasinstance (instance_seq, instance_name, description, verification, user_seq, create_user_seq, create_date, last_mod_user_seq, last_mod_date)
        SELECT { f'''nextval('aasrepo.aasinstance_instance_seq_seq'::regclass)''' if instance_seq == "" else instance_seq }, '{instance_name}', '{description}', '{verification}'
            , {userinfo.user_seq}, {userinfo.user_seq}, localtimestamp, {userinfo.user_seq}, localtimestamp
        ON CONFLICT(instance_seq) 
        do update SET 
        instance_name = EXCLUDED.instance_name, description = EXCLUDED.description, verification = EXCLUDED.verification, 
        user_seq = EXCLUDED.user_seq, last_mod_user_seq = EXCLUDED.last_mod_user_seq, last_mod_date = EXCLUDED.last_mod_date
        returning instance_seq
    ), ins_aasmodel as (
        INSERT INTO aasrepo.aasinstance_aasmodels (instance_seq, aasmodel_seq, metadata, create_user_seq, create_date, last_mod_user_seq, last_mod_date)
        SELECT src.instance_seq, {aasmodel_seq}, %s, {userinfo.user_seq}, localtimestamp, {userinfo.user_seq}, localtimestamp
        FROM ins_instance AS src
        ON CONFLICT(instance_seq, aasmodel_seq) 
        do update SET instance_seq = EXCLUDED.instance_seq, aasmodel_seq = EXCLUDED.aasmodel_seq, metadata = EXCLUDED.metadata,
        last_mod_user_seq = EXCLUDED.last_mod_user_seq, last_mod_date = EXCLUDED.last_mod_date
        returning instance_seq, aasmodel_seq
    ), submodel_tbl as (
        { f"""
        select instance_seq, aasmodel_seq, null::int4 as submodel_seq, null::jsonb as metadata,  0 as create_user_seq,  localtimestamp as create_date
        from  ins_aasmodel  
        """ if submodel_sql == "" else f"""
        select b.instance_seq, b.aasmodel_seq, src.submodel_seq, src.submodel_metadata::jsonb as metadata
            , {userinfo.user_seq} as create_user_seq,  localtimestamp as create_date
        from (
            {submodel_sql}
        ) as src
        , ins_aasmodel as b
        """ 
        }
    ), del_submodel as (
        DELETE FROM aasrepo.aasinstance_aasmodel_submodels t
        WHERE EXISTS (
            SELECT 1
            FROM submodel_tbl s
            WHERE t.instance_seq = s.instance_seq
            AND t.aasmodel_seq = s.aasmodel_seq
        )
        AND NOT EXISTS (
            SELECT 1
            FROM submodel_tbl s2
            WHERE s2.instance_seq = t.instance_seq
            AND s2.aasmodel_seq = t.aasmodel_seq
            AND s2.submodel_seq = t.submodel_seq
        )
    ), ins_submodel as (
        INSERT INTO aasrepo.aasinstance_aasmodel_submodels (
            instance_seq, aasmodel_seq, submodel_seq,
            metadata, create_user_seq, create_date
        )
        SELECT 
            instance_seq, aasmodel_seq, submodel_seq,
            metadata, create_user_seq, create_date
        FROM submodel_tbl
        where submodel_seq is not null
        ON CONFLICT (instance_seq, aasmodel_seq, submodel_seq) DO UPDATE
        SET 
            metadata = EXCLUDED.metadata,
            last_mod_user_seq = EXCLUDED.create_user_seq,
            last_mod_date = EXCLUDED.create_date
    )
    select instance_seq
    from ins_instance
    
"""

        rst = await async_postQueryDataOne(sql, None, True, userinfo.user_seq, "INSTANCE", custom_args)

        if rst["result"] != "ok" or rst["data"] == "":
            rstData["msg"] = rstData["msg"] + " : " + rst["msg"]
            return JSONResponse(status_code=400, content=rstData) 
        
        # 검증 호출
        aasmodel = json.loads(body["aasmodel_metadata"]) if body["aasmodel_metadata"] else {}
        submodel_list = [s["submodel_metadata"] for s in body["submodels"] if "submodel_metadata" in s and s["submodel_metadata"] != ""]

        verification_result = await aasInstanceMergeVerification(userinfo, rst["data"], aasmodel, submodel_list)

        if verification_result["result"] == "ok":
            verification_result = 'success'
        else:
            verification_result = 'fail'

        # 검증결과 업데이트
        verification_sql = f"""
                                UPDATE aasrepo.aasinstance
                                    SET verification = '{verification_result}'
                                    WHERE instance_seq = {rst["data"]}
                                RETURNING instance_seq;
                            """
            
        await async_postQueryDataOne(verification_sql)

        return JSONResponse(status_code=200, content=rst)

    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 

##인스턴스 삭제
async def instanceDelEvent(userinfo, instance_seq = ""):

    rstData = { "result" : "error", "msg" : f"Failed to Delete Instance !!" , "data" : ""}

    if instance_seq == "" :
        return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "No instance has been selected, Please refresh with the latest data" , "data" : ""})

    try:
        sql = f"""
        with main_tbl as (
            select *
            from aasrepo.aasinstance
            where instance_seq = {instance_seq}
                and user_seq = {userinfo.user_seq}
        )
        , del_aasmodel as (
            delete from aasrepo.aasinstance_aasmodels a
            using main_tbl as b 
            where a.instance_seq = b.instance_seq
        )
        , del_submodels as (
            delete from aasrepo.aasinstance_aasmodel_submodels a
            using main_tbl as b
            where a.instance_seq = b.instance_seq
        )
        select instance_name
        from main_tbl
"""
    
        rst = await async_postQueryDataOne(sql, None, True, userinfo.user_seq, "INSTANCE")

        if rst["result"] != "ok" or rst["msg"] == "":
            return JSONResponse(status_code=400, content=rstData) 

        rst["msg"] = f""" '{rst["msg"]}' has been deleted successfully."""

        return JSONResponse(status_code=200, content=rst) 
    
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 

async def instanceModelListEvent(userinfo, ty,  category_seq = ""):

    rstData = { "result" : "error", "msg" : f"Failed to Get {ty} List !!" , "data" : ""}

    lang_code = "1" if userinfo is None else userinfo.lang_code

    sql  = f"""

    with min_tbl as (
        select aasmodel_id, min(aasmodel_seq) as min_aasmodel_seq
        from aasrepo.aasmodels
        group by aasmodel_id
        order by min_aasmodel_seq desc
    )

    select 
    	 dense_rank() over ( order by aa.min_aasmodel_seq desc) as group_seq
    	, row_number() over (partition by aa.aasmodel_id  order by a.aasmodel_seq desc) as in_seq
    	, a.aasmodel_seq, a.aasmodel_name,  a.aasmodel_id, a."version", a.aasmodel_template_id, a.description, a.category_seq
        ,  CASE {lang_code}
                WHEN 1  THEN b.category_name
                WHEN 2  THEN b.category_name2
                WHEN 3  THEN b.category_name3
                WHEN 4  THEN b.category_name4
                WHEN 5  THEN b.category_name5
                ELSE b.category_name END as category_name
    from aasrepo.aasmodels a
    left join min_tbl aa on a.aasmodel_id = aa.aasmodel_id
    join  aasrepo.categories b on  a.category_seq = b.category_seq
    where ('{category_seq}' =  case left('{category_seq}', 6)
	                            when 'GRP100' then b.refcode1
	                            when 'GRP200' then b.refcode2
	                            when 'GRP300' then b.refcode3
	                            else b.category_seq::varchar end or '{category_seq}' = '')
	    and a.status in ('published')

""" if ty == "aasmodel" else  f"""

    with min_tbl as (
        select submodel_id, min(submodel_seq) as min_submodel_seq
        from aasrepo.submodels
        group by submodel_id
        order by min_submodel_seq desc
    )

    select 
        dense_rank() over ( order by aa.min_submodel_seq desc) as group_seq
    	, row_number() over (partition by aa.submodel_id  order by a.submodel_seq desc) as in_seq
    	, a.submodel_seq, a.submodel_name,  a.submodel_id, a.submodel_version as version, a.submodel_semantic_id,  a.description, a.category_seq
        ,  CASE {lang_code}
                WHEN 1  THEN b.category_name
                WHEN 2  THEN b.category_name2
                WHEN 3  THEN b.category_name3
                WHEN 4  THEN b.category_name4
                WHEN 5  THEN b.category_name5
                ELSE b.category_name END as category_name
    from aasrepo.submodels a
    left join min_tbl aa on a.submodel_id = aa.submodel_id
    join  aasrepo.categories b on  a.category_seq = b.category_seq
    where ('{category_seq}' =  case left('{category_seq}', 6)
	                            when 'GRP100' then b.refcode1
	                            when 'GRP200' then b.refcode2
	                            when 'GRP300' then b.refcode3
	                            else b.category_seq::varchar end or '{category_seq}' = '')
	    and  a.status in ('published')

"""

    try:

        rst = await async_postQueryDataSet(sql)

        if rst["result"] != "ok" :
            return JSONResponse(status_code=400, content=rstData) 

        return JSONResponse(status_code=200, content=rst) 
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 

    
# Instance 전체조회
async def aasInstanceDetailEvent(userinfo, instance_seq : Union [int, str] = ''):

    rstData = { "result" : "error", "msg" : "AAS Instance Not Exists. !!" , "data" : ""}

    sql = f"""
        SELECT aasrepo.fn_instance_merge(instance_seq) metadata, *
          FROM aasrepo.aasinstance
         WHERE instance_seq = {instance_seq}
           AND ( 
           ( user_seq = {userinfo.user_seq} and {userinfo.user_group_seq} = 3)
            or ( {userinfo.user_group_seq} in (1, 2) )
            )
          ;
    """

    try:
        rst = await async_postQueryDataSet(sql)

        if rst["result"] != "ok" and len(rst["data"]) == 0:
            return JSONResponse(status_code=400, content={ "result" : "ok", "msg" : "AAS Instance Not Exists. !!" , "data" : ""}) 

        return JSONResponse(status_code=200, content=rst) 
        
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData)

async def aasInstanceVerificationEvent(userinfo, body):

    rstData = { "result" : "error", "msg" : f"Instance verification failed." , "data" : ""}

    instance_seq = body["instance_seq"] if "instance_seq" in body else ""
    aasmodel = body["aasmodel"] if "aasmodel" in body else ""
    submodels = body["submodels"] if "submodels" in body else []    
    
    if aasmodel == "":
        return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "AAS model is required but not provided." , "data" : ""}) 

    try:
        rst = await aasInstanceMergeVerification(userinfo, instance_seq, aasmodel, submodels)

        if rst["result"] == "fail":
            return JSONResponse(status_code=500, content={"result": "error", "msg": rst["msg"], "data": rst["data"]})
        elif rst["result"] == "ok":
            return JSONResponse(status_code=200, content={"result": "ok", "msg": "Instance verification completed successfully", "data": ""})
        else:
            return JSONResponse(status_code=400, content={"result": "error", "msg": rst["msg"], "data": ""})

    except Exception as e:
        return JSONResponse(status_code=400, content=rstData)


async def aasInstanceMergeVerification(userinfo, instance_seq: str, aasmodel: dict, submodels: list):
    """
    aasmodel, submodels 합쳐서 KETI API 검증
    """
    if not aasmodel:
        return {"result": "error", "msg": "AAS model is required but not provided.", "data": ""}

    if "submodels" not in aasmodel:
        aasmodel["submodels"] = []

    if not aasmodel.get("assetAdministrationShells"):
        return {"result": "error", "msg": "No AssetAdministrationShell found in AAS JSON.", "data": ""}

    aas = aasmodel["assetAdministrationShells"][0]
    if "submodels" not in aas:
        aas["submodels"] = []

    existing_submodel_ids = {sm.get("id") for sm in aasmodel["submodels"]}
    existing_ref_ids = {
        ref["keys"][0]["value"]
        for ref in aas["submodels"]
        if ref.get("keys") and isinstance(ref["keys"], list)
    }

    for submodel_metadata in submodels:

        if type(submodel_metadata) != dict:
            submodel_metadata = json.loads(submodel_metadata)
        else:
            continue

        submodel_id_val = submodel_metadata.get("id")
        if not submodel_id_val:
            continue

        if submodel_id_val not in existing_submodel_ids:
            aasmodel["submodels"].append(submodel_metadata)
            existing_submodel_ids.add(submodel_id_val)

        if submodel_id_val not in existing_ref_ids:
            ref = {
                "type": "ModelReference",
                "keys": [{"type": "Submodel", "value": submodel_id_val}]
            }
            aas["submodels"].append(ref)
            existing_ref_ids.add(submodel_id_val)

    return await verificationEvent(userinfo, aasmodel, 'instance', instance_seq, "")













