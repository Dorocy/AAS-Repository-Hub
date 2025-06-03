import os
import logging
import datetime
from  config.config import get_config_value, get_section_dict
from tools.stringTool import dollarSign, newUUID

from time import sleep
from sqlalchemy import create_engine, text


formatter = logging.Formatter('|%(asctime)s|==|%(name)s||%(levelname)s|\n\t%(message)s\n')    
DEBUG_FLAG = get_config_value('debug', 'mode')
MSG_LENGTH = get_config_value('log', 'length', 'system')
LOG_NAME = get_config_value('log', 'name')
LOG_DBNAME = get_config_value('log', 'db_name')
DB_INFO = get_section_dict('postgres')

##로그커넥션 관리
DATABASE_URL = f"""postgresql+psycopg://{DB_INFO["username"]}:{DB_INFO["password"]}@{DB_INFO["host"]}:{DB_INFO["port"]}/{DB_INFO["database"]}"""
engine = create_engine(DATABASE_URL)


## 로그 메시지 중복 방지
def prevent_duplicate(logger):
    logger.propagate = False
    if logger.hasHandlers():
        logger.handlers.clear()

## 정보성 로그
def infoLogger(msg:str = "", logName=None, target:str = "", user_seq:int = 0, errFlag = False):

    target = newUUID() if target == "" else target

    if logName is None:
        name = LOG_NAME
    else:
        # name = f"{LOG_NAME}|{logName}{ '|' + target if target != '' else ''}|{user_seq}|"
        #큰따옴표에서 발생하는에러..?
        name = f"{LOG_NAME}|{logName}{'|' + target if target != '' else ''}|{user_seq}|"

    infoLog = logging.getLogger(name=f'{name}') 
    infoLog.setLevel(logging.INFO) ## 경고 수준 설정
    prevent_duplicate(infoLog)    

    stream_handler = logging.StreamHandler() ## 스트림 핸들러 생성
    stream_handler.setFormatter(formatter) ## 텍스트 포맷 설정
    infoLog.addHandler(stream_handler) ## 핸들러 등록
    
    if DEBUG_FLAG == 1 and user_seq != 0:
        if (errFlag):
            infoLog.error("\n\t"+"-"*77+ f"\n\n\t\t\t{msg[:MSG_LENGTH] if len(msg) > MSG_LENGTH else msg}\n\n\t"+"-"*77)
        else:
            infoLog.info("\n\t"+"-"*77+ f"\n\n\t\t\t{msg[:MSG_LENGTH] if len(msg) > MSG_LENGTH else msg}\n\n\t"+"-"*77)
    ## aas/submoel등 meta데이터때문에 주석
    # else:
    #     print("*"*150, "\n\n", msg)

    return infoLog

import psycopg
postConn = None

#parameter : msg = 오류 로그, logName = 로그 Name or Title,  flag = True or False(출력을 남기지 않을경우 False)
## 오류 정보성 로그 기록(DB)
def dbLogger(msg:str = "", logName:str=None, target:str = "", user_seq:int = 0, errFlag = False, dblogFlag = True):
    target = newUUID() if target == "" else target
    current_year = datetime.datetime.now().year
    log_table_name = f"{LOG_DBNAME}logs_{current_year}"  # 연도별 로그 테이블 이름 설정
    global postConn

    if logName is None:
        name = LOG_NAME
    else:
        name = f"{LOG_NAME}|{logName}"

    try:
        
        ## 기본은 경고도 포함
        infoLog = infoLogger(msg, logName, target, user_seq, errFlag)        
        
        if postConn is None or postConn.closed:
            postConn = psycopg.connect(host = DB_INFO['host'], port = DB_INFO['port'], dbname = DB_INFO['database'], user = DB_INFO['username'], password = DB_INFO['password'], options = f"-c timezone=Asia/Seoul", connect_timeout=DB_INFO['timeout'])
        postCur = postConn.cursor()

        ## 조회는 user_seq = 0 으로 넘어오기에 단순 조회는 로그 남김 제외
        if dblogFlag and user_seq != 0:
            
            create_sql = f"""

                CREATE TABLE IF NOT EXISTS aasrepo.{log_table_name} (
                    dt TIMESTAMP,
                    log_type VARCHAR(50),
                    msg TEXT,
                    target VARCHAR(50),
                    state VARCHAR(50),
                    flag CHAR(1),
                    user_seq int
                )
            """
            log_sql = f"""
                insert into aasrepo.{log_table_name}(dt, log_type, msg, target, state, flag, user_seq)
                values(localtimestamp, %s, %s, %s, %s, 'N', %s )
            """

            params = (name, str(msg), target, "ERROR" if errFlag else "LOG", user_seq )
            postCur.execute(create_sql)
            postCur.execute(log_sql, params=params)
            postConn.commit()

    except Exception as e:
        print("+"*150, f"""\n {logName}|{target}|\n\n log db insert error : \n {str(e)} \n""", "+"*150)
    finally:    
        return infoLog

