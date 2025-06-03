import json
import time
from fastapi import HTTPException
import psycopg
from psycopg import AsyncConnection
from starlette import status

from config.config import get_config_value, get_section_dict
from tools.loggerTool import *
from tools.stringTool import convert_null_to_blank, valueValidationFalse, convert_ISO8601Date_to_Date, newUUID
from tools.asyncTool import asyncify


#커넥션 타임 일단 7초
#디버그1이면 출력(오류제외), 개별설정을 위해변수처리
DEBUG_FLAG = get_config_value('debug', 'mode')
DB_INFO = get_section_dict('postgres')


#options = '-c timezone=Asia/Seoul', 
def timescaleDB():
    
    conn = psycopg.connect(host = DB_INFO['host'], port = DB_INFO['port'], dbname = DB_INFO['database'], user = DB_INFO['username'], password = DB_INFO['password'], options = f"-c timezone=Asia/Seoul", connect_timeout=DB_INFO['timeout'])
    return conn

async def asyncTimescaleDB():
    
    conn = await AsyncConnection.connect(host = DB_INFO['host'], port = DB_INFO['port'], dbname = DB_INFO['database'], user = DB_INFO['username'], password = DB_INFO['password'], options = f"-c timezone=Asia/Seoul", connect_timeout=DB_INFO['timeout'])
    
    return conn


def timescaleDB2(ip, port, id, pw, database):
    try:
    
        conn = psycopg.connect(host = ip, port = port, dbname = database, user = id, password = pw, options = f"-c timezone=Asia/Seoul", connect_timeout=DB_INFO['timeout'])
    except Exception as e:
        conn = None
    finally:
        return conn

# 연결할 DB 상태확인
def postDBCheckEvent(dbinfo, user_seq:int = 0):
    
    msg = ""

    try:
        sql = f"SELECT 'ONLINE' as status FROM pg_catalog.pg_database WHERE datname='{dbinfo['database']}'"

        rst = exPostQueryDataOne(dbinfo, sql)

        if rst["data"] != "":
            result = rst["data"]
        else:
            result = "Database connection error"

    except Exception as e:
        result = "Database connection error : " + str(e)
        dbLogger(str(e.args[0]), "CONNECT_FAIL", user_seq=user_seq)
    finally:
        return result


## postgresql 쿼리 실행
def exPostExecuteQuery( dbinfo, qry, postConn = None , autoCommit = True , user_seq:int = 0):
    if postConn is None:
        postConn = timescaleDB2(dbinfo["ip"], dbinfo["port"], dbinfo["id"], dbinfo["pw"], dbinfo["database"])
    if postConn is None:
        return {"result" : "error", "msg" : "Database connection error" , "data" : ""}        
    return postExecuteQuery( qry, postConn, autoCommit , user_seq=user_seq)

## postgresql 쿼리 실행
def postExecuteQuery( qry, postConn = None , autoCommit = True , user_seq:int = 0):
    rstData = { "result" : "ERROR", "msg" : "ERROR" , "data" : []}
    uuid_str = newUUID()

    try:
        if DEBUG_FLAG == 1:
            start = time.time()

        if postConn is None:
            postConn = timescaleDB()
        
        postCur = postConn.cursor()
        
        dbLogger(qry,"EXCE_SQL", uuid_str, user_seq=user_seq)
        
        postCur.execute(qry)
        
        rstData = {"result" : "ok", "msg" : "Processing completed"}
        
        if postCur.description is not None and postCur.rowcount > 0:
            columns = [col[0] for col in postCur.description]
            # rows = {k: v for (k, v) in fetch_list}
            data = [dict(zip(columns, tuple)) for tuple in postCur.fetchall()]
            rstData['data'] = data
            
        if (autoCommit):
            postConn.commit()
        
        infoLogger(rstData,"EXCE_DATA", uuid_str, user_seq=user_seq)

    except Exception as e:
        dbLogger(e.args[0], "EXCE_FAIL", uuid_str, True, user_seq=user_seq)
        rstData = { "result" : "error", "msg" : "Error : " +str(e)}
        if (autoCommit):
            postConn.rollback()
    finally:
        postCur.close()
        if (autoCommit): 
            if postConn:
                postConn.close()

        if DEBUG_FLAG == 1:
            print("Processing Time : {} seconds".format(str(time.time() - start)))

        return rstData
    
## 프로시저 실행    
def exPostCallProc( dbinfo, qry, parameters= None, postConn = None , autoCommit = True, user_seq:int = 0 ):
    if postConn is None:
        postConn = timescaleDB2(dbinfo["ip"], dbinfo["port"], dbinfo["id"], dbinfo["pw"], dbinfo["database"])
    if postConn is None:
        return {"result" : "error", "msg" : "Database connection error" , "data" : ""}            
    return postCallProc( qry, parameters, postConn , autoCommit, user_seq=user_seq)    

## 프로시저 실행
def postCallProc( qry, parameters= None, postConn = None , autoCommit = True, user_seq:int =0 ):
    rstData = { "result" : "ERROR", "msg" : "ERROR" , "data" : ""}
    uuid_str = newUUID()

    try:
        if DEBUG_FLAG == 1:
            start = time.time()
            
        if postConn is None:
            postConn = timescaleDB()
        
        postCur = postConn.cursor()
            
        dbLogger(f"{qry}","CALL_PROC", uuid_str, user_seq=user_seq)

        if (parameters is None):
            postCur.callproc(qry )
        else:
            if DEBUG_FLAG == 1:
                print(qry, parameters )
            postCur.callproc(qry, parameters )
        
        result = postCur.fetchone()[0]

                
        if (autoCommit):
            postConn.commit()

        rstData = {"result" : "ok", "msg" : "Processing completed", "data" : result}

        dbLogger(result,"CALL_PROC", uuid_str, user_seq=user_seq)
    
    except Exception as e:
        
        dbLogger(str(e), "CALL_PROC_FAIL", uuid_str, True, user_seq=user_seq)
        rstData = { "result" : "error", "msg" : "ERROR : {}".format(str(e)) , "data" : ""}
        if (autoCommit):
            postConn.rollback()
    finally:
        postCur.close()
        if (autoCommit): 
            if postConn:
                postConn.close()

        if DEBUG_FLAG == 1:
            print("Processing Time : {} seconds".format(str(time.time() - start)))
            
        return rstData

## postgresql 다중 여러행
def exPostQueryDataSet( dbinfo, qry, postConn = None , autoCommit = True, user_seq:int = 0, *args ):
    if postConn is None:
        postConn = timescaleDB2(dbinfo["ip"], dbinfo["port"], dbinfo["id"], dbinfo["pw"], dbinfo["database"])

    if postConn is None:
        return {"result" : "error", "msg" : "Database connection error" , "data" : ""}
    return postQueryDataSet( qry, postConn , autoCommit, user_seq=user_seq)     
## postgresql 다중 여러행
def postQueryDataSet( qry , postConn = None, autoCommit = True, user_seq:int=0, *args  ):
    rstData = { "result" : "ERROR", "msg" : "ERROR" , "data" : []}
    data = []
    uuid_str = newUUID()

    try:
        if DEBUG_FLAG == 1:
            start = time.time()
        
        if postConn is None: 
            postConn = timescaleDB()
        postCur = postConn.cursor()

        
        dbLogger(qry,"SET_SQL", uuid_str, user_seq=user_seq)
        
        postCur.execute(qry, *args )
        rows = postCur.fetchall()
        
        columns = [column[0] for column in postCur.description]
        for row in rows:
            data.append(dict(zip(columns,row)))

        if not data:
            rstData = {"result" : "ok", "msg" : "Data does not exist" , "data" : [] } 
            return rstData

        if (not (data is None)):
            datas = json.dumps(data, default=str, indent=4, ensure_ascii=False)

            jsonDatas = json.loads(datas)
            jsonDatas = convert_null_to_blank(jsonDatas)
        if (autoCommit):
            postConn.commit()

        rstData = {"result" : "ok", "msg" : "Processing completed", "data" : jsonDatas}

        dbLogger(rstData,"SET_RESULT", uuid_str, user_seq=user_seq)
    
    except Exception as e:
        dbLogger(e.args[0], "SET_FAIL", uuid_str, True, user_seq=user_seq)
        rstData = { "result" : "error", "msg" : "ERROR : {}".format(str(e)) , "data" : []}
        if (autoCommit):
            postConn.rollback()
    finally:
        postCur.close()
        if (autoCommit): 
            if postConn:
                postConn.close()

        if DEBUG_FLAG == 1:
            print("Processing Time : {} seconds".format(str(time.time() - start)))

        return rstData
    


##비동기 적용만하고 일단 기존 로직 적용/스레드 검토전 테스트
async def asyncPostQueryDataSet( qry , postConn = None, autoCommit = True, user_seq:int=0 , *args):
    rstData = { "result" : "ERROR", "msg" : "ERROR" , "data" : []}
    data = []
    uuid_str = newUUID()
    
    try:
        if DEBUG_FLAG == 1:
            start = time.time()
        
        postConn = await asyncTimescaleDB()
        
        async with postConn.transaction():

            dbLogger(qry,"SET_SQL", uuid_str, user_seq=user_seq)

            async with postConn.cursor() as postCur:
                await postCur.execute(qry, *args)
                rows = await postCur.fetchall()
        
            columns = [column[0] for column in postCur.description]

            for row in rows:
                data.append(dict(zip(columns,row)))

            if not data:
                rstData = {"result" : "ok", "msg" : "Data does not exist" , "data" : [] } 
                return rstData

            if (not (data is None)):
                datas = json.dumps(data, default=str, indent=4, ensure_ascii=False)

                jsonDatas = json.loads(datas)
                jsonDatas = convert_null_to_blank(jsonDatas)
        
        if (autoCommit):
            await postConn.commit()

        rstData = {"result" : "ok", "msg" : "Processing completed", "data" : jsonDatas}

        dbLogger(rstData,"SET_RESULT", uuid_str, user_seq=user_seq)
        
    except Exception as e:
        dbLogger(str(e),"SET_FAIL", uuid_str, True, user_seq=user_seq)
        rstData = { "result" : "error", "msg" : "ERROR : {}".format(str(e)) , "data" : []}
        
    finally:
    
        if DEBUG_FLAG == 1:
            print("Processing Time : {} seconds".format(str(time.time() - start)))

        return rstData
    
    
## postgresql 단일값
def exPostQueryDataOne( dbinfo, qry, postConn = None , autoCommit = True, user_seq:int = 0, log_type:str  = "", *args  ):
    if postConn is None:
        postConn = timescaleDB2(dbinfo["ip"], dbinfo["port"], dbinfo["id"], dbinfo["pw"], dbinfo["database"])
    if postConn is None:
        return {"result" : "error", "msg" : "Database connection error" , "data" : ""}
    return postQueryDataOne( qry, postConn , autoCommit, user_seq, log_type, *args  )

## postgresql 단일값
def postQueryDataOne( qry , postConn = None , autoCommit = True, user_seq:int = 0, log_type:str = "", *args):
    rstData = { "result" : "ERROR", "msg" : "ERROR" , "data" : ""}

    log_type ="|" + log_type if log_type != "" else ""


    uuid_str = newUUID()
    try:
        if DEBUG_FLAG == 1:
            start = time.time()
            
        if postConn is None:
            postConn = timescaleDB()
        postCur = postConn.cursor()
        
        
        postCur.execute(qry, *args )
        data = postCur.fetchone()
        
        dbLogger(f"{qry}\n", "ONE_SQL" + log_type, uuid_str, user_seq=user_seq)

            
        if (autoCommit):
            postConn.commit()

        if (data is None):
            oData = ""
        else:
            oData = data[0]

        rstData = {"result" : "ok", "msg" : "Processing completed", "data" : oData}
 
        dbLogger(rstData, "ONE_RESULT" + log_type, uuid_str, user_seq=user_seq)

    except Exception as e:
        dbLogger(str(e.args[0]), "ONE_FAIL" + log_type, uuid_str, True, user_seq=user_seq)
        rstData = { "result" : "error", "msg" : "Error {}".format(str(e)) , "data" : ""}
        if (autoCommit):
            postConn.rollback()
    finally:
        postCur.close()
        if (autoCommit): 
            if postConn:
                postConn.close()

        if DEBUG_FLAG == 1:
            print("Processing Time : {} seconds".format(str(time.time() - start)))

        return rstData
    

#외부 요청은 NULL은 그대로이기에 False, 페이징 정보도 False
def postQueryPageData( qryTable, pageNumber:int=1, pageSize:int = 10, whereOption:str = "", orderby:str = "", postConn = None, autoCommit = True, nullToBlank = False, pageMode = False, user_seq:int=0):    

    uuid_str = newUUID()

    if valueValidationFalse(whereOption) or valueValidationFalse(orderby) :
        return { "result" : "error", "msg" : "[Warning] There are forbidden characters in the query." , "data" : ""}
    
    rstData = { "result" : "error", "msg" : "ERROR" , "data" : ""}

    if  orderby.lstrip() == '':
        orderby = ""
    else:
        orderby = f" ORDER BY {orderby} " 

    try:
        if DEBUG_FLAG == 1:
            start = time.time()

        if postConn is None:
            postConn = timescaleDB()
        
        postCur = postConn.cursor()            
        
        if postConn is None:
            return {"result" : "error", "msg" : "Database connection error" , "data" : ""}
        
        postCur = postConn.cursor()

        data = []
        qry = ""

        ##서브쿼리시 페이징 처리 속도 개선이 필요(8.14)
        ##서브쿼리 안에 오프셋 넣는걸로
        ##서브쿼리 () 제거후 오프셋 넣고 다시 2024.02.28 select * from () r 로 변경
        newQryTable = qryTable.strip()

        if newQryTable.lstrip()[0:4].upper() == "WITH" or newQryTable.lstrip()[0:7].upper() == "SELECT " :
            newQryTable = f"""( 
    {newQryTable} 
)"""

        logQuery = f"""SELECT *
FROM 
{  f''' (    
    ''' + newQryTable[1:-1] + f''' 
) r''' if (newQryTable[0] == '(' and newQryTable[-1] == ')')  else qryTable }  
{whereOption if whereOption.lstrip() != '' else ''} 
{orderby} """
        
        qry = f"""
WITH baseTBL AS (

    SELECT *
    FROM {  f''' (     
            ''' + newQryTable[1:-1] + f'''
    ) r''' if (newQryTable[0] == '(' and newQryTable[-1] == ')') else qryTable }   
)
"""
        ##컬럼정보
        col_lsit = get_col_list(f"""{qry} SELECT * FROM baseTBL LIMIT 0""", postConn)
        
        qry += f"""                        
, dataTBL as (
    SELECT ROW_NUMBER() OVER( {orderby} ) { f'''+  ( ( {pageNumber } -1 ) * {pageSize} )::bigint  '''   if pageNumber != 0 else '' }  as "AAS_Seq_No"
        , *
    FROM (
        SELECT 
            dkfdldktm_a.*
        FROM baseTBL
        as dkfdldktm_a 
        {whereOption if whereOption.lstrip() != '' else ''}
        {
        f''' 
         {orderby} 
        OFFSET  ( ( {pageNumber } -1 )::bigint  * {pageSize} )
        ROWS FETCH NEXT {pageSize}  ROWS ONLY 
        '''  if pageNumber != 0 else ''
        } 
    ) r
            
) """
        
        qry += f"""
, totTBL as (

    SELECT count(1) as recordsTotal
    FROM  baseTBL as dkfdldktm_a

)
, filterTBL as (

    {

    f'''SELECT count(*) as recordsFiltered  FROM  {  'baseTBL' if (newQryTable[0] == '(' and newQryTable[-1] == ')') else qryTable }   
        {whereOption} '''  if whereOption.lstrip() != '' else  'SELECT recordsTotal as recordsFiltered FROM totTBL'
    }

) """ if pageMode else ''
        
        qry += f"""    
, jsonDataTBL as (
    SELECT row_to_json(a_aliasname1) as JsonData
    FROM dataTBL  a_aliasname1
)

SELECT row_to_json(r) as results
FROM (
    SELECT 
        { pageNumber }::bigint as draw
        ,{ 'b_aliasname.recordsTotal' if pageMode else 'NULL' } as "recordsTotal"
        ,{ 'c_aliasname.recordsFiltered' if pageMode else 'NULL' } as "recordsFiltered"
        , ARRAY{col_lsit} as "columns"
        , a_aliasname.data
    FROM (
        SELECT array_to_json( 
            array (
                 SELECT * FROM jsonDataTBL 
            )         
        ) as data
    ) as a_aliasname
    { f''', totTBL as b_aliasname
    , filterTBL as c_aliasname''' if pageMode else '' }
    
) r  
    
        """
        
        dbLogger(qry, "EX_PAGE_SQL", uuid_str, user_seq=user_seq)
        
        postCur.execute(qry)
        data = postCur.fetchone()
        jsonDatas = data[0] 
        jsonDatas = convert_null_to_blank(jsonDatas) if nullToBlank else jsonDatas
        jsonDatas = convert_ISO8601Date_to_Date(jsonDatas)
    
        if (autoCommit):
            postConn.commit()

        rstData = { "result" : "ok", "msg" : "Processing completed" , "data" : jsonDatas}

        dbLogger(rstData, "EX_PAGE_RESULT", uuid_str, user_seq=user_seq)

    except Exception as e:
        
        dbLogger(e.args[0], "EX_PAGE_FAIL", uuid_str, True, user_seq=user_seq)

        rstData = { "result" : "error", "msg" : "ERROR {}".format(str(e)) , "data" : ""}
        if (autoCommit):
            postConn.rollback()
    finally:
        postCur.close()
        if (autoCommit): 
            if postConn:
                postConn.close()

        if DEBUG_FLAG == 1:
            print("Processing Time : {} seconds".format(str(time.time() - start)))
        return rstData




def find_one(query):
    conn = timescaleDB()
    cursor = conn.cursor()
    uuid_str = newUUID()

    try:
        if DEBUG_FLAG == 1:
            start = time.time()

        cursor.execute(query)
        fetch_one = cursor.fetchone()

        if fetch_one is not None:
            fetch_one = fetch_one[0]
        if DEBUG_FLAG == 1:
            print("Processing Time : {} seconds".format(str(time.time() - start)))
            print(fetch_one)

    except Exception as e:
        dbLogger(str(e), 'find_one', uuid_str, 0, True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        cursor.close()
        if conn:
            conn.close()
    return fetch_one


def find_one_as_dict(query):
    conn = timescaleDB()
    cursor = conn.cursor()
    uuid_str = newUUID()

    try:
        if DEBUG_FLAG == 1:
            start = time.time()

        cursor.execute(query)
        fetch_one = cursor.fetchone()
        if fetch_one is None:
            return None            
        
        columns = [col[0] for col in cursor.description]
        
        # rows = {k: v for (k, v) in fetch_list}
        # data = dict(zip(columns, fetch_one))
        data = dict(zip(columns, fetch_one))

        if DEBUG_FLAG == 1:
            print("Processing Time : {} seconds".format(str(time.time() - start)))

    except Exception as e:
        dbLogger(str(e), 'FIND_ONE_AS_DICT', uuid_str, 0, True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        cursor.close()
        if conn:
            conn.close()    
    return data


def find_all(query):
    conn = timescaleDB()
    cursor = conn.cursor()
    uuid_str = newUUID()

    try:
        if DEBUG_FLAG == 1:
            start = time.time()

        cursor.execute(query)
        fetch_list = cursor.fetchall()

        columns = [col[0] for col in cursor.description]
        # rows = {k: v for (k, v) in fetch_list}
        data_list = [dict(zip(columns, tuple)) for tuple in fetch_list]
        # data_list = {k: v for (k, v) in zip(columns, rows)}

        if DEBUG_FLAG == 1:
            print("Processing Time : {} seconds".format(str(time.time() - start)))
    except Exception as e:
        dbLogger(str(e), 'find_all', uuid_str, 0, True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        cursor.close()
        if conn:
            conn.close()
    return data_list


def find_all_as_dict(query):
    conn = timescaleDB()
    cursor = conn.cursor()
    uuid_str = newUUID()

    try:
        if DEBUG_FLAG == 1:
            start = time.time()

        cursor.execute(query)
        fetch_list = cursor.fetchall()

        data_dict = dict((k, v) for k, v in fetch_list)

        if DEBUG_FLAG == 1:
            print("Processing Time : {} seconds".format(str(time.time() - start)))
    except Exception as e:
        dbLogger(str(e), 'find_all_as_dict', uuid_str, 0, True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        cursor.close()
        if conn:
            conn.close()
    return data_dict

#컬럼 리스트 (포스트그리는 시퀀스처리 서브쿼리에서 다시 하기때문에 리스트를 별도로 가져오는 부분에서 추가)
def get_col_list(query, conn = None):

    uuid_str = newUUID()

    if conn is None:
        conn = timescaleDB()

    cursor = conn.cursor()
    data = []

    try:

        cursor.execute(query)

        data = ["AAS_Seq_No"] + [col[0] for col in cursor.description]

    except Exception as e:
        dbLogger(str(e), 'GET_COL_LIST', uuid_str, 0, True)
    finally:
        return data
    



# 비동기 래핑 처리
async_postQueryDataOne = asyncify(postQueryDataOne)
async_postQueryDataSet = asyncify(postQueryDataSet)
async_postQueryPageData = asyncify(postQueryPageData)
async_postExecuteQuery = asyncify(postExecuteQuery)
# async_exPostQueryDataOne = asyncify(exPostQueryDataOne)
# async_exPostExecuteQuery = asyncify(exPostExecuteQuery)
# async_exPostQueryDataSet = asyncify(exPostQueryDataSet)
# async_exPostQueryPageData = asyncify(exPostQueryPageData)

async_find_one_as_dict = asyncify(find_one_as_dict)
