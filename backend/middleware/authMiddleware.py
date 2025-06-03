from fastapi import HTTPException, Request
from pydantic import BaseModel
import datetime
import json
import urllib.parse
from typing import Union, Optional

from jose import jwt, JWTError
from config.config import get_section_dict, get_config_value
from tools.cryptoTool import verify_access_token

DEBUG_FLAG = get_config_value("debug", "mode")

AUTH = get_section_dict("auth")


class Token(BaseModel):
    payload: str
    target: str

class Payload(BaseModel):
    jwt_access_token: str

class NomalUser(BaseModel):
    user_seq: Union[int, str]
    user_id: str
    user_name: str
    user_social_seq: Union[int, str]
    user_social_id: str
    user_social_provider_seq: Union[int, str]
    user_social_provider: str
    user_group_seq: Union[int, str]
    user_group_name: str
    user_photo_url: str
    lang_code: str

class TokenPayload(BaseModel):
    iss: str
    exp: int
    iat: int
    profile: NomalUser

VALIDATE_RESULT_EMPTY_TOKEN = "Token is empty"
VALIDATE_RESULT_TOKEN_EXPIRED = "Validity of the token has expired"
VALIDATE_RESULT_INVALID_SIGNATURE = "Signature information of token is incorrect"
VALIDATE_RESULT_UNSUPPORTED_TOKEN = "token of unsupported format"
VALIDATE_RESULT_UNAUTHORIZED_ERROR = "Unauthorized access target."

def get_token_from_request(request: Request) -> Optional[Token]:
    """
    HttpOnly 쿠키 사용으로 로직 변경
    서버 컴포넌트 사용 시 쿠키 세팅이 불가능하여 헤더로 전달
    클라이언트 컴포넌트 사용 시 헤더 세팅이 불가능하여 쿠키로 전달
    
    헤더: Authorization: Bearer <payload>
    쿠키: token_message (URL 인코딩된 JSON 문자열)
    """
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        return json.loads(auth_header.removeprefix("Bearer ").strip())

    cookie_raw = request.cookies.get("token_message")
    if cookie_raw:
        return json.loads(urllib.parse.unquote(cookie_raw))

    return None

def verify_token(request: Request) -> NomalUser:
    """
    토큰 검증 후 유효한 사용자 정보를 반환 (토큰 검증이 필수인 경우 사용)
    """
    try:
        # 디버그 모드일땐 토큰 패스쓰루
        # if DEBUG_FLAG == 1:
        #     return NomalUser (
        #         user_seq=1, user_id='admin'
        #             , user_name='관리자'
        #             , user_social_seq="", user_social_id=""
        #             , user_social_provider_seq="", user_social_provider=""
        #             , user_group_seq=1, user_group_name='관리자'
        #             , user_photo_url = "", lang_code = "1"

        #     )
        
        # 토큰 존재 여부 확인
        token_json = get_token_from_request(request)
        if token_json is None:
            raise HTTPException(status_code=401, detail=VALIDATE_RESULT_EMPTY_TOKEN)

        # 타겟 유효성 검사
        if token_json["target"] != AUTH["target"]:
            raise HTTPException(status_code=401, detail=VALIDATE_RESULT_UNAUTHORIZED_ERROR)
        
        # 토큰 검증
        payload = verify_access_token(token_json["payload"]["jwt_access_token"])
        if not isinstance(payload, dict):
            raise HTTPException(status_code=401, detail=VALIDATE_RESULT_INVALID_SIGNATURE)

        payload = TokenPayload(**payload)

        # 만료시간 확인
        now = datetime.datetime.utcnow()
        exp = datetime.datetime.utcfromtimestamp(payload.exp)
        if (exp - now).total_seconds() < 0:
            raise HTTPException(status_code=401, detail=VALIDATE_RESULT_TOKEN_EXPIRED)

        # 발급자 확인
        if payload.iss != get_config_value("service_info", "name"):
            raise HTTPException(status_code=401, detail=VALIDATE_RESULT_INVALID_SIGNATURE)

        # 사용자 정보 포함 여부 확인
        profile = payload.profile
        if profile is None:
            raise HTTPException(status_code=401, detail=VALIDATE_RESULT_INVALID_SIGNATURE)

        return profile

    except JWTError:
        raise HTTPException(status_code=401, detail=VALIDATE_RESULT_INVALID_SIGNATURE)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=401, detail=VALIDATE_RESULT_INVALID_SIGNATURE)

def verify_token_optional(request: Request) -> Optional[NomalUser]:
    """
    토큰 검증이 필수가 아닌 경우 사용
    """
    try:
        return verify_token(request)
    except HTTPException:
        return None
