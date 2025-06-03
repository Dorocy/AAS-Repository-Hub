from cryptography.fernet import Fernet
from config.config import get_config_value
import datetime
import jwt
import bcrypt
from typing import Union
from processor.postgresProcess import postQueryDataOne


SECRET_KEY = get_config_value('auth', 'JWT_SECRET_KEY')
ALGORITHM = get_config_value('auth', 'ALGORITHM')
SYSTEM_NAME = get_config_value('service_info', 'name')
LANG_CODE = get_config_value('service_info', 'lang_code')
EXPIRES_DELTA = get_config_value('auth', 'expires_sec')
EXPIRES_HOUR = get_config_value('auth', 'expires_hour')

# 사용자 정의 대칭키 생성
def generate_custom_symmetric_key():
    # 사용자가 원하는 32바이트 길이의 바이트를 입력
    key = bytes(str(get_config_value("auth", "password_secret_key")), 'utf-8')

    return key

# 데이터를 사용자 정의 대칭키로 암호화
def encrypt_data(key, data):
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data

# 데이터를 사용자 정의 대칭키로 복호화
def decrypt_data(key, encrypted_data):
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data).decode()
    return decrypted_data

#패스워드 암호화
def encrypt_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password  

#패스워드 체크
def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))



##토큰 생성(유효기간 일단 하루로 연장)
def create_access_token(user_seq: Union [int, str], user_id: str, user_name: str, user_social_seq: Union [int, str], user_social_id: str
                        , user_social_provider_seq: Union [int, str], user_social_provider: str, user_group_seq: Union [int, str], user_group_name: str, user_photo_url: str=""
                        , expires_delta: int = EXPIRES_DELTA):
    """사용자 정보를 포함하여 JWT 액세스 토큰 생성"""

    lang_code = LANG_CODE

    sql = f"""
    select refcode1 as lang
    from aasrepo.aas_codeinfo
    where code = 'SYS000'
    limit 1

    """

    rst = postQueryDataOne(sql)
    
    ##기본언어가져오기
    if rst["data"] != "":
        lang_code = rst["data"]
    
    payload = {
        "iss": SYSTEM_NAME, 
        "exp": datetime.datetime.utcnow()  + datetime.timedelta(seconds=expires_delta),  # 만료 시간 설정
        "iat": datetime.datetime.utcnow() ,  # 발급 시간 (Issued At)
        
        "profile" : {
            "user_seq": user_seq,
            "user_id": user_id,
            "user_name": user_name,
            "user_social_seq": user_social_seq if user_social_seq else "",
            "user_social_id": user_social_id if user_social_id else "",
            "user_social_provider_seq": user_social_provider_seq if user_social_provider_seq else "",
            "user_social_provider": user_social_provider if user_social_provider else "",
            "user_group_seq": user_group_seq if user_group_seq else "",
            "user_group_name": user_group_name if user_group_name else "",
            "user_photo_url": user_photo_url if user_photo_url else "",
            "lang_code" : str(lang_code), 
        } 
    }

    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

##더미 토큰생성
##print(create_access_token(1, 'admin', 'admin', "", "", "", "", "", "", ""))

def create_full_token(encrypt_token, userprofile):
    lang_code = LANG_CODE

    sql = f"""
    select refcode1 as lang
    from aasrepo.aas_codeinfo
    where code = 'SYS000'
    limit 1

    """

    rst = postQueryDataOne(sql)
    
    ##기본언어가져오기
    if rst["data"] != "":
        lang_code = rst["data"]

    userprofile["lang_code"] = str(lang_code)

    return {
                "target" : get_config_value('auth', 'target') ,
                "payload" : {
                    "jwt_access_token" : encrypt_token,
                    #"user" : {
                    #    "profile" : userprofile
                    #}
                }
        }


# JWT 토큰 생성 (비밀번호 초기화 용도)
def create_reset_mail_token(email: str) -> str:
    payload = {
        "sub": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=EXPIRES_HOUR)  # 1시간 유효
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

VALIDATE_RESULT_TOKEN_EXPIRED = "Validity of the token has expired"
VALIDATE_RESULT_INVALID_SIGNATURE = "Signature information of token is incorrect"

def decode_reset_mail_token(token):
    try:
        payload = verify_access_token(token)
        if not type(payload) is dict:
            return {"result" : "error", "msg" : VALIDATE_RESULT_INVALID_SIGNATURE, "data" : ""}
        
        # 만료시간 확인
        now = datetime.datetime.utcnow()
        exp = datetime.datetime.utcfromtimestamp(payload["exp"])
        if (exp - now).total_seconds() < 0:
            return {"result" : "error", "msg" : VALIDATE_RESULT_TOKEN_EXPIRED, "data" : ""}
            
        return {"result" : "ok", "msg" : "", "data" : payload["sub"]} 
    except jwt.ExpiredSignatureError:
        return {"result" : "error", "msg" : VALIDATE_RESULT_TOKEN_EXPIRED, "data" : ""}
    except jwt.InvalidTokenError:
        return {"result" : "error", "msg" : VALIDATE_RESULT_INVALID_SIGNATURE, "data" : ""}
        



def verify_access_token(token):
    """JWT 액세스 토큰 검증 및 디코딩"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM) ###정상적인 경우 딕셔너리 반환
    except jwt.ExpiredSignatureError:
        return "Token has expired"
    except jwt.InvalidTokenError:
        return "Invalid token"

