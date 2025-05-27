
from typing import  Union
from decimal import Decimal
from fastapi.responses import JSONResponse
from processor.postgresProcess import *



async def publishDraftList(lang_code, user_group_seq, searchKey, category_seq, ty = "", status = "", target_seq: Union[int, str] = "", listMode = True, pageNumber = 0, pageSize = 0 , pageMode = False):
    
    rstData = { "result" : "error", "msg" : "Failed to Get Published/Draft List" , "data" : ""}

    sql = f"""
    with last_aasmodel_tbl as (
        select  aasmodel_id, status, max(aasmodel_seq) as max_aasmodel_seq
        from aasrepo.aasmodels
        where ( 'aasmodel' = '{ty}' or '{ty}' = '' )
            and status in ('draft', 'published', 'deprecated')
        group by aasmodel_id, status
    )
    , last_submodel_tbl as (
        select submodel_id, status, max(submodel_seq) as max_submodel_seq
        from aasrepo.submodels
        where ( 'submodel' = '{ty}' or '{ty}' = '' )
            and status in ('draft', 'published', 'deprecated')
        group by submodel_id, status
    )
    , aasmodel_list as (
	
	    select 'aasmodel' as ty, a.aasmodel_seq, a.aasmodel_name,  a.aasmodel_id, a."version", a.aasmodel_template_id, a."type",  a.description, a.category_seq
            , CASE {lang_code}
                WHEN 1  THEN b.category_name
                WHEN 2  THEN b.category_name2
                WHEN 3  THEN b.category_name3
                WHEN 4  THEN b.category_name4
                WHEN 5  THEN b.category_name5
                ELSE b.category_name END as category_name, a.status, a.create_user_seq, a.create_date, a.last_mod_user_seq, a.last_mod_date
            , max_aasmodel_seq as max_seq
	    from aasrepo.aasmodels a
	    left join last_aasmodel_tbl aa on a.aasmodel_seq = aa.max_aasmodel_seq
        join  aasrepo.categories b on  a.category_seq = b.category_seq
	    where ( 'aasmodel' = '{ty}' or '{ty}' = '' )
            and ('{category_seq}' =  case left('{category_seq}', 6) 
				when 'GRP100' then b.refcode1 
				when 'GRP200' then b.refcode2 
				when 'GRP300' then b.refcode3
				else b.category_seq::varchar end or '{category_seq}' = '')
	        and ( lower(a.aasmodel_name) like '%' || lower('{searchKey}') || '%' or a.description like '%' || lower('{searchKey}') || '%' )
            and a.status in ('draft', 'published', 'deprecated')
	    order by a.aasmodel_seq		
    
	), submodel_list as (
		select 'submodel' as ty,  a.submodel_seq, a.submodel_name, a.submodel_id, a.submodel_version, a.submodel_template_id, a.submodel_type, a.description, a.category_seq 
            , CASE {lang_code}
                WHEN 1  THEN b.category_name
                WHEN 2  THEN b.category_name2
                WHEN 3  THEN b.category_name3
                WHEN 4  THEN b.category_name4
                WHEN 5  THEN b.category_name5
                ELSE b.category_name END as category_name, a.status, a.create_user_seq, a.create_date, a.last_mod_user_seq, a.last_mod_date
            , max_submodel_seq as max_seq
	    from aasrepo.submodels a
	    left join last_submodel_tbl as aa on a.submodel_seq = aa.max_submodel_seq
        join  aasrepo.categories b on  a.category_seq = b.category_seq
	    where ( 'submodel' = '{ty}' or '{ty}' = '' )
            and ('{category_seq}' =  case left('{category_seq}', 6) 
				when 'GRP100' then b.refcode1 
				when 'GRP200' then b.refcode2 
				when 'GRP300' then b.refcode3
				else b.category_seq::varchar end or '{category_seq}' = '')
	        and ( lower(a.submodel_name) like '%' || lower('{searchKey}') || '%' or lower(a.description) like '%' || lower('{searchKey}') || '%' )
            and a.status in ('draft', 'published', 'deprecated')
	    order by a.submodel_seq		 
	
	) , total_list as (   
	
        select a.ty, a.aasmodel_seq as target_seq, a.aasmodel_name as target_name,  a.aasmodel_id as target_id, a."version" as target_version
            , a.aasmodel_template_id  as tmp_seman_id, a."type",  a.description, a.category_seq, a.category_name, a.status
            , a.create_user_seq, a.create_date, a.last_mod_user_seq, a.last_mod_date, a.max_seq
		from aasmodel_list a
		union all
		select a.ty,  a.submodel_seq, a.submodel_name, a.submodel_id, a.submodel_version
            , a.submodel_template_id, a.submodel_type, a.description, a.category_seq , a.category_name, a.status
            , a.create_user_seq,  a.create_date, a.last_mod_user_seq, a.last_mod_date, a.max_seq
		from submodel_list a
		
	)
	
    select a.ty, a.target_seq , a.target_name
        , a.target_id, a.target_version, a.tmp_seman_id
        , a.type,  a.description, a.category_seq, a.category_name, a.status, aasrepo.fncodenm(a.status, {lang_code} ) as status_nm
        , a.create_user_seq, b.user_name as draft_user_nm, a.create_date
        , a.last_mod_user_seq, c.user_name as published_user_nm, a.last_mod_date
	from total_list a
	left join aasrepo.users b on a.create_user_seq = b.user_seq
	left join aasrepo.users c on a.last_mod_user_seq = c.user_seq
	where ( a.target_seq::text = '{target_seq}' or '{target_seq}' = '' )
        and ( ( a.status = '{status}' and a.max_seq is not null )
            or ('{status}' = '' )
            or ('{status}' = 'all' and a.status in ('published', 'deprecated')  and a.max_seq is not null)         
            )
    order by a.last_mod_date desc
"""

    try:
        if listMode:
            rst = await async_postQueryPageData(sql, pageNumber, pageSize , "", "", None, True, False, pageMode)
        else:
            rst = await async_postQueryDataSet(sql)


        return rst
        
    except Exception as e:
        rstData["msg"] = str(e)
        return  JSONResponse(status_code=400, content=rstData)  
    


## 퍼블리시 리스트(배포)
async def publishListEvent(userinfo, searchKey, category_seq, ty = "", status = "", target_seq = "", pageNumber = 1, pageSize = 10, pageMode = False):
    rstData = { "result" : "error", "msg" : "Failed to get publish list" , "data" : ""}

    lang_code = "1" if userinfo is None else userinfo.lang_code

        
    user_group_seq = userinfo.user_group_seq

    if user_group_seq == 3 or user_group_seq is None:
        return JSONResponse(status_code=403, content={ "result" : "error", "msg" : "You do not have permission." , "data" : ""}) 

    try:
        rst = await publishDraftList(lang_code, user_group_seq, searchKey, category_seq, ty, status, target_seq, True, pageNumber, pageSize, pageMode)

        if rst["result"] != "ok" :
            return JSONResponse(status_code=400, content=rstData) 

        if target_seq != 0 and len(rst["data"]) == 0:
            return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Target Data has different data. Please!! Reload Data." , "data" : ""}) 


        return JSONResponse(status_code=200, content=rst) 
        
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 
    
## 배포 히스토리
async def publishHistoryListEvent(userinfo, ty, target_seq):

    
    lang_code = "1" if userinfo is None else userinfo.lang_code

    rstData = { "result" : "error", "msg" : "Failed to Get History Info" , "data" : ""}

    sql = f"""

 	with aasmodel_list as (
	
	    select 'aasmodel' as ty, a.aasmodel_seq, a.aasmodel_name,  a.aasmodel_id, a."version", a.aasmodel_template_id, a."type",  a.description
	    	, a.category_seq, aasrepo.fncodenm(a.category_seq::varchar, {lang_code}, 'category') as category_name, a.status, a.create_user_seq,  a.create_date, a.last_mod_user_seq, a.last_mod_date
	    from aasrepo.aasmodels a
	    join aasrepo.aasmodels aa on a.aasmodel_id = aa.aasmodel_id and aa.aasmodel_seq = {target_seq}
	    where ( 'aasmodel' = '{ty}' or '{ty}' = '' )
	    order by a.aasmodel_seq		
    
	), submodel_list as (
		select 'submodel' as ty, a.submodel_seq, a.submodel_name, a.submodel_id, a.submodel_version, a.submodel_template_id, a.submodel_type, a.description
			, a.category_seq , aasrepo.fncodenm(a.category_seq::varchar, {lang_code}, 'category') as category_name, a.status, a.create_user_seq,  a.create_date, a.last_mod_user_seq, a.last_mod_date
	    from aasrepo.submodels a
	    join aasrepo.submodels aa on a.submodel_id = aa.submodel_id and aa.submodel_seq = {target_seq}
	    where ( 'submodel' = '{ty}' or '{ty}' = '' )
	    order by a.submodel_seq		 
	
	) , total_list as (   
	
        select a.ty, a.aasmodel_seq as target_seq, a.aasmodel_name as target_name,  a.aasmodel_id as target_id, a."version" as target_version
            , a.aasmodel_template_id  as tmp_seman_id, a."type",  a.description, a.category_seq, a.category_name, a.status, a.create_user_seq, a.create_date, a.last_mod_user_seq, a.last_mod_date
		from aasmodel_list a
		union all
		select a.ty,  a.submodel_seq, a.submodel_name, a.submodel_id, a.submodel_version
            , a.submodel_template_id, a.submodel_type, a.description, a.category_seq , a.category_name, a.status, a.create_user_seq,  a.create_date, a.last_mod_user_seq, a.last_mod_date
		from submodel_list a
		
	)
	
    select a.ty, a.target_seq , a.target_name
        , a.target_id, a.target_version, a.tmp_seman_id
        , a.type,  a.description, a.category_seq, a.category_name, a.status, aasrepo.fncodenm(a.status, {lang_code} ) as status_nm
        , a.create_user_seq, b.user_name as draft_user_nm, a.create_date
        , a.last_mod_user_seq, c.user_name as published_user_nm, a.last_mod_date
	from total_list a
	left join aasrepo.users b on a.create_user_seq = b.user_seq
	left join aasrepo.users c on a.last_mod_user_seq = c.user_seq
    order by a.target_seq desc
    """

    try:

        rst = await async_postQueryDataSet(sql)

        if rst["result"] != "ok" :
            return JSONResponse(status_code=400, content=rstData) 

        return JSONResponse(status_code=200, content=rst) 
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 



## 배포 처리
async def publishProcessEvent(userinfo, body):

    rstData = { "result" : "error", "msg" : "Failed to Published!!" , "data" : ""}
        
    user_group_seq = userinfo.user_group_seq

    lang_code = "1" if userinfo is None else userinfo.lang_code

    target_seq = body["target_seq"] if "target_seq" in body else ""
    ty = body["ty"] if "ty" in body else ""
    status = body["status"] if "status" in body else ""
    version = body["version"] if "version" in body else ""
    description = body["description"] if "description" in body else ""

    
    if target_seq == "" or ty == "" or status not in ["draft"]:
        return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Please. Check the Target Data." , "data" : ""}) 
    
    if user_group_seq == 3 or user_group_seq is None :
        return JSONResponse(status_code=403, content={ "result" : "error", "msg" : "You don't have permission." , "data" : ""}) 
    
    try:
        ## 해당 타겟이 변경사항이 현황과 같은지 체크
        sql = f"""
        with aasmodel_tbl as (
            select aasmodel_id as target_id, version
            from aasrepo.aasmodels
            where aasmodel_seq = {target_seq}
                and 'aasmodel' = '{ty}'
        ), submodel_tbl as (
            select submodel_id as target_id, submodel_version as version
            from aasrepo.submodels
            where submodel_seq = {target_seq}
                and 'submodel' = '{ty}'
    
        ), max_aasmodel_tbl as (
            select a.aasmodel_id as target_id, b.version,  max(a.version::decimal(18,1)) as max_version
            from aasrepo.aasmodels a
            join aasmodel_tbl b on a.aasmodel_id = b.target_id
            group by a.aasmodel_id, b.version
        ), max_submmodel_tbl as (
            select a.submodel_id as target_id, b.version, max(a.submodel_version::decimal(18,1)) as max_version
            from aasrepo.submodels a
            join submodel_tbl b on a.submodel_id = b.target_id
            group by a.submodel_id, b.version
        ) , tot_tbl as (
            select target_id, version, coalesce(max_version, 0.0) + 0.1 as new_version
            from max_aasmodel_tbl
            union all
            select target_id, version, coalesce(max_version, 0.0) + 0.1 as new_version
            from max_submmodel_tbl
        )
        
        select target_id, version, new_version
        from tot_tbl a
        limit 1
        
        """
        rst = await async_postQueryDataSet(sql, user_seq=userinfo.user_seq)
        
        if rst["result"] != "ok" :
            return JSONResponse(status_code=400, content=rstData) 
        
        ## 데이터가 없으면 리로드 해라
        if (len(rst["data"]) == 0):
            return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Target Data has different data(No draft data). Please!! Reload Data." , "data" : ""}) 
        
        if rst["result"] != "ok" :
            return JSONResponse(status_code=400, content=rstData) 

        #버전 0.1 더함. --> 최신 버전가져오기 
        new_version = "0.0" if rst["data"][0]["new_version"] == "" else rst["data"][0]["new_version"]
        target_version = "0.0" if rst["data"][0]["version"] == "" else rst["data"][0]["version"]
        version = "0.0" if version == "" else version
        
        if version != target_version:
            return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Target Data version has different data(version). Please!! Reload Data." , "data" : ""}) 

        ##상태만 draft => published, new_version 적용, 배포자 업데이트
        ## 서브모델 semantic_id 는 받아오는 로직(20250411)
        ##, submodel_semantic_id = case when coalesce(submodel_semantic_id, '') = '' then aasrepo.generator_code('submodel' , {body["category_seq"]}::varchar) else submodel_semantic_id end
        sql = f"""
        update aasrepo.aasmodels 
        set status = 'published'
            , aasmodel_name = {dollarSign(body["target_name"])}
            , version = '{new_version}'
            , aasmodel_template_id = aasrepo.generator_code('aasmodel' , {body["category_seq"]}::varchar, '{new_version}', '{ "" if (body["tmp_seman_id"] == "" or body["tmp_seman_id"] is None)  else body["tmp_seman_id"] }') 
            , description = {dollarSign(description)}
            , last_mod_user_seq = {userinfo.user_seq}
            , last_mod_date = localtimestamp
            , category_seq = {body["category_seq"]}
        where aasmodel_seq = {target_seq}
        returning aasmodel_seq as target_seq
        
        """  if ty == "aasmodel" else f"""

        update aasrepo.submodels 
        set status = 'published'
            , submodel_name = {dollarSign(body["target_name"])}
            , submodel_version = '{new_version}'
            , submodel_template_id = aasrepo.generator_code('submodel' , {body["category_seq"]}::varchar, '{new_version}', '{ "" if (body["tmp_seman_id"] == "" or body["tmp_seman_id"] is None)  else body["tmp_seman_id"] }') 
            , description = {dollarSign(description)}
            , last_mod_user_seq = {userinfo.user_seq}
            , last_mod_date = localtimestamp
            , category_seq = {body["category_seq"]}
        where submodel_seq = {target_seq}
        returning submodel_seq as target_seq
        """

        rst = await async_postQueryDataOne(sql, None, True, userinfo.user_seq, "PUBLISH")

        if rst["result"] != "ok" or rst["data"] == "":
            return JSONResponse(status_code=400, content=rstData) 
        
        return JSONResponse(status_code=200, content={ "result" : "ok", "msg" : "Successful to Published!!" , "data" : ""}) 
        
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 





## 배포 수정
async def publishModifyEvent(userinfo, body):

    rstData = { "result" : "error", "msg" : "Failed Modification to Published!!" , "data" : ""}

    user_group_seq = userinfo.user_group_seq

    lang_code = "1" if userinfo is None else userinfo.lang_code
    
    target_seq = body["target_seq"] if "target_seq" in body else ""
    ty = body["ty"] if "ty" in body else ""
    status = body["status"] if "status" in body else ""
    version = body["version"] if "version" in body else ""
    description = body["description"] if "description" in body else ""

    if target_seq == "" or ty == "" or status not in ["published" , "deprecated"]:
        return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Please. Check the Target Data." , "data" : ""}) 

    if user_group_seq == 3 or user_group_seq is None :
        return JSONResponse(status_code=403, content={ "result" : "error", "msg" : "You do not have permission." , "data" : ""}) 

    try:
        ## 해당 타겟이 변경사항이 현황과 같은지 체크
        rst = await publishDraftList(lang_code, user_group_seq, "", "",  ty, "", target_seq, False)

        if rst["result"] != "ok" :
            return JSONResponse(status_code=400, content=rstData) 
        
        ## 데이터가 없으면 리로드 해라
        if (len(rst["data"]) == 0):
            return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Target Data has different data. Please!! Reload Data." , "data" : ""}) 
        
        new_version = rst["data"][0]["target_version"]

        version = "0.0" if version == "" else version
        new_version = "0.0" if new_version == "" or new_version is None else new_version
        
        if new_version != version:
            return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Target Data version has different data. Please!! Reload Data." , "data" : ""}) 
        

        #old_status = rst["data"][0]["status"]
        
        ##타겟이 deprecated -> published 될때 
        ##해당 template_id 외 나머지 등록 된건이 있는지 확인
        ## 해당 아이디로 무조건 동일 트리로 버전 업되어야함... 이원화 되면 안됨...
        # if old_status == 'deprecated' and status == "published":

        #     sql = f"""
        #     select aasmodel_seq as target_seq
        #     from aasrepo.aasmodels
        #     where left(aasmodel_template_id,14) <> left('{body["tmp_seman_id"]}',14)
        #         and status <> 'deprecated'
        #     limit 1	
        #     """ if ty == "aasmodel" else f"""
        #     select submodel_seq as target_seq
        #     from aasrepo.submodels
        #     where left(submodel_template_id,14) <> left('{body["tmp_seman_id"]}',14)
        #         and status <> 'deprecated'
        #     limit 1	
        #     """
        #     rst = await async_postQueryDataOne(sql, None, True, userinfo.user_seq, "PUBLISH")

        #     if rst["data"] != "":
        #         return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "This data cannot be changed to the 'Published' state. There are registered cases with the same ID." , "data" : ""}) 


        ##상태만 deprecate <=> published, new_version 적용, 배포자 업데이트
        sql = f"""
        update aasrepo.aasmodels 
        set status = '{status}'
            , aasmodel_name = {dollarSign(body["target_name"])}
            , description = {dollarSign(description)}
            , last_mod_user_seq = {userinfo.user_seq}
            , last_mod_date = localtimestamp
            , category_seq = {body["category_seq"]}
        where aasmodel_seq = {target_seq}
        returning aasmodel_seq as target_seq
        
        """  if ty == "aasmodel" else f"""

        update aasrepo.submodels 
        set status = '{status}'
            , submodel_name = {dollarSign(body["target_name"])}
            , description = {dollarSign(description)}
            , last_mod_user_seq = {userinfo.user_seq}
            , last_mod_date = localtimestamp
            , category_seq = {body["category_seq"]}
        where submodel_seq = {target_seq}
        returning submodel_seq as target_seq
        """

        rst = await async_postQueryDataOne(sql, None, True, userinfo.user_seq, "PUBLISH")

        if rst["result"] != "ok" or rst["data"] == "":
            return JSONResponse(status_code=400, content=rstData) 
        
        return JSONResponse(status_code=200, content={ "result" : "ok", "msg" : "Successful Modification to Published!!" , "data" : ""}) 
        
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 
    


async def publishedCountEvent(userinfo=None):

    rstData = { "result" : "error", "msg" : "Failed to Counter" , "data" : ""}


    user_seq =  "" if userinfo is None else userinfo.user_seq
    user_group_seq =  "" if userinfo is None else userinfo.user_group_seq

    sql = f"""

select a.ordsq, a.ty, coalesce(count(r.target),0) as cnt, case when to_char(max(max_dt), 'YYYY-MM-DD') = to_char(localtimestamp, 'YYYY-MM-DD') then 'new' else '' end as is_new 
from (
	select 1 as ordsq,  'aasmodel' as ty 
	union all 
	select 2 as ordsq, 'submodel' as ty 
	union all
	select 3 as ordsq, 'instance' as ty 
	
) a
left join 
(

        select 1 as ordsq,  'aasmodel' as ty,  aasmodel_id as target, max(create_date) as max_dt
        from aasrepo.aasmodels
        where status in ('published')
        group by aasmodel_id

        union all 
        
        select 2 as ordsq, 'submodel' as ty, submodel_id as target, max(create_date) as max_dt 
        from aasrepo.submodels
        where  status in ('published')
        group by submodel_id
        
        union all
        
        select 3 as ordsq, 'instance' as ty, instance_name, create_date as max_dt
        from aasrepo.aasinstance
        where ( 
            (user_seq::varchar = '{user_seq}' and '{user_group_seq}' = '3')
            or
            ('{user_group_seq}' in ('1', '2'))
        )

) r
on a.ty = r.ty and a.ordsq = r.ordsq
group by a.ordsq, a.ty
order by a.ordsq


    """

    try:

        rst = await async_postQueryDataSet(sql)

        if rst["result"] != "ok":
            return JSONResponse(status_code=400, content=rstData) 
        
        return JSONResponse(status_code=200, content=rst) 
        
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=400, content=rstData) 
            