import requests

import smtplib
from email.mime.text import MIMEText
import email.utils
import premailer
from typing import Union

from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from processor.postgresProcess import *
from tools.cryptoTool import create_access_token, create_full_token, check_password, encrypt_password, create_reset_mail_token, decode_reset_mail_token
from config.config import get_config_value, get_section_dict

GOOGLE_CLIENT_ID = get_config_value("social_google", "GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = get_config_value("social_google", "GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = get_config_value("social_google", "GOOGLE_REDIRECT_URI")
GOOGLE_AUTH_URL = get_config_value("social_google", "GOOGLE_AUTH_URL")
GOOGLE_TOKEN_URL = get_config_value("social_google", "GOOGLE_TOKEN_URL")
GOOGLE_PROFILE_URL = get_config_value("social_google", "GOOGLE_PROFILE_URL")

NAVER_CLIENT_ID = get_config_value("social_naver", "NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = get_config_value("social_naver", "NAVER_CLIENT_SECRET")
NAVER_REDIRECT_URI = get_config_value("social_naver", "NAVER_REDIRECT_URI")
NAVER_AUTH_URL = get_config_value("social_naver", "NAVER_AUTH_URL")
NAVER_TOKEN_URL = get_config_value("social_naver", "NAVER_TOKEN_URL")
NAVER_PROFILE_URL = get_config_value("social_naver", "NAVER_PROFILE_URL")

SMTP_INFO = get_section_dict("mail")
SERVICE_INFO = get_section_dict("service_info")

## 일반 로그인
async def authLoginEvent(id, pw):
    rstData = { "result" : "error", "msg" : "Login Failed!! Checked ID or Password" , "data" : ""}
    
    if id == "" or id is None or pw == "" or pw is None:
        return JSONResponse(status_code=200, content={ "result" : "ok", "msg" : "Login Sucess!!" , "data" : "" }) 

    try:

        sql = f"""
            select a.user_seq, a.user_id, a.pw_hash, a.user_name, coalesce(a.status, 'Y') as status
                , b.socialaccount_seq as user_social_seq, b.social_id as user_social_id, b.socialprovider_seq as  user_social_provider_seq, null as user_social_provider
                , c.group_seq as user_group_seq, d.group_name as user_group_name
            from aasrepo.users a
            left join aasrepo.socialaccounts b on a.user_seq = b.user_seq
            left join aasrepo.users_group c on a.user_seq = c.user_seq
            left join aasrepo.groups d on c.group_seq = d.group_seq
            where a.user_id = %s
                and coalesce(a.close_timestamp, localtimestamp) >= localtimestamp
            limit 1
        """
        
        rst = await async_postQueryDataSet(sql, None, True, 0, (id, ))

        if rst["result"] != "ok" or len(rst["data"]) == 0:
            return JSONResponse(status_code=200, content=rstData) 
        
        ## 비활성화
        if rst["data"][0]["status"] == "N":
            return JSONResponse(status_code=200, content={ "result" : "error", "msg" : "Your account is not active." , "data" : ""}) 
        
        ##소셜 로그인 유저는 소셜로 로그인 해라는 메시지 리던
        if rst["data"][0]["user_social_seq"] != "" or rst["data"][0]["user_social_seq"] is None:
            return JSONResponse(status_code=200, content={ "result" : "error", "msg" : "Your account is Social Login User." , "data" : ""}) 
        
        hashed_password = rst["data"][0]["pw_hash"]
        token_data =  rst["data"][0]

        token_data.pop("pw_hash", None)
        token_data.pop("status", None)
        
        user_photo_url = ""
        token_data["user_photo_url"] = user_photo_url

        if not check_password(pw, hashed_password):
            return JSONResponse(status_code=200, content={ "result" : "error", "msg" : "Please check your password." , "data" : ""}) 
        
        #정상일경우 토큰 생성
        encrypt_token = create_access_token(token_data["user_seq"], token_data["user_id"], token_data["user_name"]
                                                , token_data["user_social_seq"], token_data["user_social_id"]
                                                , token_data["user_social_provider_seq"], token_data["user_social_provider"]
                                                , token_data["user_group_seq"], token_data["user_group_name"], user_photo_url)
        


        token = create_full_token(encrypt_token, token_data)
        #print("token", token)

        return JSONResponse(status_code=200, content={ "result" : "ok", "msg" : "Login Sucess!!" , "data" : token }) 

    except Exception as e:
        return JSONResponse(status_code=500, content=rstData)  
        
##사용자 등록
async def registerEvent(user_id, user_pw, user_nm = ""):
    rstData = { "result" : "error", "msg" : "User registration failed" , "data" : ""}

    if user_nm == "" or user_nm is None:
        user_nm = user_id

    #기존 사용자 정보 확인 ID체크
    sql = f"""
        select a.user_seq, a.user_id, a.status, coalesce(b.social_id, '') as social_id
        from aasrepo.users a
        left join aasrepo.socialaccounts b on a.user_seq = b.user_seq
        where a.user_id = %s
        limit 1
    """

    try: 
        rst = await async_postQueryDataSet(sql, None, True, 0, (user_id, ))
        
        if rst["result"] != "ok"  :
            return JSONResponse(status_code=200, content={ "result" : "error", "msg" : "User Checking Error" , "data" : ""}) 

        if len(rst["data"]) > 0 :
            rstData = { "result" : "error", "msg" : f"""The account is already registered. { "(Social)" if rst["data"][0]["social_id"] != "" else "" }""" , "data" : ""}
            return JSONResponse(status_code=200, content=rstData)     

        #없으면 저장 알림
        sql2 = f"""
        with inserted as (
            INSERT INTO aasrepo.users ( user_id, pw_hash, user_name, STATUS, start_timestamp,  create_user_seq, create_date)
            VALUES ( %s, %s, %s, 'Y', CURRENT_TIMESTAMP, 0, CURRENT_TIMESTAMP)
            returning user_seq
        ), group_inserted as (
            INSERT INTO aasrepo.users_group (user_seq, group_seq) 
            select user_seq, 3
            from inserted
            returning user_seq
        )
        select user_seq
        from group_inserted

    """
        rst = await async_postQueryDataOne(sql2, None, True, 0, "USERSAVE", (user_id,encrypt_password(user_pw).decode('utf-8'), user_nm,  ))

        if rst["result"] != "ok"  :
            return JSONResponse(status_code=200, content={ "result" : "error", "msg" : "User registration failed" , "data" : ""})  

        if rst["data"] != "":
            return JSONResponse(status_code=200, content={ "result" : "ok", "msg" : "User registration Success" , "data" : f"""user_id ({rst["data"]})"""})  
    
    except Exception as e:
        rstData = { "result" : "error", "msg" : "User registration failed. " + str(e) , "data" : ""}
        return JSONResponse(status_code=500, content=rstData)  


## 비밀번호 초기화 메일보내기
def resetPasswordEvent(email):
    # 비밀번호 초기화 토큰 생성
    reset_token = create_reset_mail_token(email)

    # 이메일 전송
    send_reset_email(email, reset_token)



# 이메일 전송 함수
def send_reset_email(email_address: str, reset_token: str):

    reset_link = SMTP_INFO["reset_password_url"].format(url=SERVICE_INFO["host_f_domain"]) + reset_token
    html_content = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Password Reset Instructions</title>
<style>
  body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333333;
  }
  .container {
    max-width: 600px;
    margin: 20px auto;
    padding: 20px;
    border: 1px solid #dddddd;
    border-radius: 5px;
  }
  .header {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 20px;
  }
  .link {
    display: inline-block;
    margin-top: 15px;
    padding: 10px 15px;
    background-color: #007bff;
    color: white;
    text-decoration: none;
    border-radius: 4px;
  }
  .notes {
    margin-top: 20px;
    font-size: 14px;
    color: #555555;
  }
  .footer {
    margin-top: 30px;
    font-size: 12px;
    color: #888888;
  }
</style>
</head>
<body>
""" 
    html_content += f"""

<div class="container">
<div class="header"><img data-filename="keti_logo.png" data-inline="true" src="https://build.onewayplatform.com:6200/assets/media/logos/keti_logo.png" style="width: 324px; height: 63px;"><br></div>
<div class="header">{SMTP_INFO["smtp_title"]} Password Reset Instructions</div><p>Hello, {email_address},</p>    
    
    <p>Thank you for using KETI AAS Repository Hub.</p>
    
    <p>We are sending you this email because you have requested to reset your password for your account.</p>
    
    <p>Please click on the link below to proceed to the password reset page:</p>
    
    <p><a href="{reset_link}" class="link">Reset Password</a></p>
    
<div class="notes">
      <strong>Important Notes:</strong>
      
<ul>
        
	<li>For security purposes, this link is valid for a single use and will expire within 1 Hour.</li>
        
	<li>If you did not request a password reset, please ignore this email. It is possible that someone else mistakenly entered your email address.</li>
        
	<li>For your privacy, please do not forward this email to anyone.</li>
      
</ul>
    </div><p>If you have any questions, please contact our customer support.</p>
    
<div class="footer">
      <p>Thank you,</p>
      <p>The {SMTP_INFO["smtp_title"]} Team</p>
    </div></div>
</body>    
</html>
    """
    inlined_html_content = premailer.transform(html_content, keep_style_tags=True)
    msg = MIMEText(inlined_html_content, 'html', _charset='utf-8')
    #msg = MIMEText(f"Click on the link below to reset your password:\n\n{reset_link}")
    msg["Subject"] = f"""{SMTP_INFO["smtp_title"]} Password Initialization Request"""
    msg["From"] =  email.utils.formataddr((SMTP_INFO["smtp_title"], SMTP_INFO["email_address"]))
    #msg["From"] = SMTP_INFO["email_address"]
    msg["To"] = email_address

    try:

        server = smtplib.SMTP(SMTP_INFO["smtp_server"], SMTP_INFO["smtp_port"])
        server.starttls()
        server.login(SMTP_INFO["email_address"], SMTP_INFO["email_password"])
        server.sendmail(email_address, email_address, msg.as_string())
        server.quit()

        rstData = { "result" : "error", "msg" : "Sucess to Password initialization mail sent. Please check your mailbox."  , "data" : ""}
        return JSONResponse(status_code=200, content=rstData)
    except Exception as e:
        rstData = { "result" : "error", "msg" : "Failed to Send Mail : " + str(e) , "data" : ""}
        return JSONResponse(status_code=500, content=rstData)


## 비밀번호 초기화 메일보내기
async def resetPasswordRequestEvent(email):
    rstData = { "result" : "error", "msg" : "Password initialization mail sending error." , "data" : ""}

    try:
        if email == "" or email is None:
            return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "email is blank" , "data" : ""}) 
        

        sql = f"""
            select a.user_seq, a.user_id, a.pw_hash, a.user_name, coalesce(a.status, 'Y') as status
                , b.socialaccount_seq as user_social_seq, b.social_id as user_social_id, b.socialprovider_seq as  user_social_provider_seq, null as user_social_provider
                , c.group_seq as user_group_seq, d.group_name as user_group_name
            from aasrepo.users a
            left join aasrepo.socialaccounts b on a.user_seq = b.user_seq
            left join aasrepo.users_group c on a.user_seq = c.user_seq
            left join aasrepo.groups d on c.group_seq = d.group_seq
            where a.user_id = %s
                and coalesce(a.close_timestamp, localtimestamp) >= localtimestamp
            limit 1
        """
        
        rst = await async_postQueryDataSet(sql, None, True, 0, (email, ))

        if rst["result"] != "ok" or len(rst["data"]) == 0:
            return JSONResponse(status_code=200, content={ "result" : "error", "msg" : "Your account is not Exists." , "data" : ""}) 
        
        ## 비활성화
        if rst["data"][0]["status"] == "N":
            return JSONResponse(status_code=200, content={ "result" : "error", "msg" : "Your account is Exists. But, Your account is not active. \nPlease contact the administrator."  , "data" : ""}) 
        
        ##소셜 로그인 유저는 소셜로 로그인 해라는 메시지 리던
        if rst["data"][0]["user_social_seq"] != "" or rst["data"][0]["user_social_seq"] is None:
            return JSONResponse(status_code=200, content={ "result" : "error", "msg" : "Your account is Social User. Please login with your social account." , "data" : ""}) 
        

        # 비밀번호 초기화 토큰 생성 (유효시간 1시간)
        reset_token = create_reset_mail_token(email)

        # 이메일 전송
        send_reset_email(email, reset_token)

        return JSONResponse(status_code=200, content={ "result" : "ok", "msg" : "Password reset mail sent, please check the mailbox." , "data" : ""}) 
    
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=500, content=rstData) 


## 비밀번호 업데이트(초기화)
async def resetPasswordEvent(token, newpassword):
    rstData = { "result" : "error", "msg" : "Password Initialization Error." , "data" : ""}

    try:
        rst = decode_reset_mail_token(token)  # 토큰 검증

        if rst["result"] != "ok":
            return JSONResponse(status_code=400, content=rst)

        email = rst["data"]
        hashed_password = encrypt_password(newpassword).decode('utf-8')

        ## 계정 상태 체크
        sql = f"""
            select a.user_seq, a.user_id, a.status, coalesce(b.social_id, '') as social_id
            from aasrepo.users a
            left join aasrepo.socialaccounts b on a.user_seq = b.user_seq
            where a.user_id = %s
            limit 1
        """

        rst = await async_postQueryDataSet(sql, None, True, 0, (email, ))

        if rst["result"] != "ok" or len(rst["data"]) == 0:
            return JSONResponse(status_code=200, content={ "result" : "error", "msg" : "Your account is not Exists." , "data" : ""}) 
        
        if rst["data"][0]["social_id"] != "":
            return JSONResponse(status_code=200, content={ "result" : "error", "msg" : "This account is social Account. Try to Social Login." , "data" : ""}) 

        sql2 = f"""
        update aasrepo.users 
        set pw_hash = %s
        where user_id = %s
        returning user_seq
"""
        rst = await async_postQueryDataOne(sql2, None, True, 0, "PASSWORD",(hashed_password, email,  ))

        if rst["result"] != "ok":
            return JSONResponse(status_code=200, content={ "result" : "error", "msg" : "Password Initialization Error" , "data" : ""}) 

        return JSONResponse(status_code=200, content={ "result" : "ok", "msg" : "Password reset complete" , "data" : ""})

    except Exception as e:
        return JSONResponse(status_code=500, content=rstData)


## 소셜 로그인 리다이렉트
def socialLoginEvent(social):
    auth_url = None

    if social == "google":
        auth_url = (
            f"{GOOGLE_AUTH_URL}?response_type=code"
            f"&client_id={GOOGLE_CLIENT_ID}"
            f"&redirect_uri={GOOGLE_REDIRECT_URI.format(url=SERVICE_INFO['host_b_domain'])}"
            f"&scope=email%20profile"
            f"&access_type=offline"  # Refresh Token을 받기 위해 추가
            f"&prompt=consent"  # 항상 refresh_token을 받기 위해 추가
        )
    elif social == "naver":
        auth_url = (
            f"{NAVER_AUTH_URL}?response_type=code"
            f"&client_id={NAVER_CLIENT_ID}"
            f"&redirect_uri={NAVER_REDIRECT_URI.format(url=SERVICE_INFO['host_b_domain'])}"
            f"&state=RANDOM_STATE"
            f"&scope=profile%20email"
        )

    return RedirectResponse(auth_url)
    
##로그인 정보를 받으면 result=ok , data = 토큰 정보임 
##아닐경우 팝업과 함께 닫히는 로직, (팝업테마 필요시 백엔드 설정)
def google_callbackEvent(code: str = None, state: str = None, error: str = None):
    if error:
        return resultAlertMsg("Login Failed", f"Google Login Failed : {error}")
    if not code:
        return resultAlertMsg("Login Error", f"Google Access Code Not Found!!") 
    token = {}
    msg = ""

    try:
        # 1) code로 토큰 교환
        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI.format(url=SERVICE_INFO['host_b_domain']),
            "grant_type": "authorization_code",
        }
        r = requests.post(GOOGLE_TOKEN_URL, data=data)
        if r.status_code != 200:
            return resultAlertMsg("Login Failed", f"Failed to obtain token from Google")

        token_json = r.json()
        access_token = token_json["access_token"]
        refresh_token = token_json["refresh_token"]

        #print("google_token : ", token_json)

        # 2) 토큰으로 사용자 정보 가져오기
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_resp = requests.get(GOOGLE_PROFILE_URL, headers=headers)
        if userinfo_resp.status_code != 200:
            return resultAlertMsg("Login Failed", f"Failed to fetch user info from Google")
        
        userinfo = userinfo_resp.json()

        #print("Google User Info :" , userinfo)

        # 3) 이메일 등을 확인해 내부 DB에 사용자 정보 등록 or 기존 계정 찾기
        user_social_in_id = userinfo["id"]
        user_social_id = userinfo["email"]
        user_social_name = userinfo["given_name"] if userinfo["name"] == "" else userinfo["name"]
        user_photo_url = userinfo["picture"] if "picture" in userinfo else ""

        # DB 조회/생성 로직
        rst = userCheckAndSave(user_social_in_id, user_social_id, user_social_name, "1", access_token, refresh_token)


        if rst["result"] != "ok":
            return resultAlertMsg("Login Failed", rst["msg"])

        # 4) 자체 JWT(또는 세션) 발급하여 로그인 처리
        # (JWT 발급 예시)        
        #user_seq: int, user_id: str, user_name: str, user_social_seq: str, user_social_id: str, user_social_provider: str, user_group_seq: str
        encrypt_token = create_access_token(rst["data"][0]["user_seq"], rst["data"][0]["user_id"], rst["data"][0]["user_name"]
                                            , rst["data"][0]["user_social_seq"], rst["data"][0]["user_social_id"]
                                            , rst["data"][0]["user_social_provider_seq"], rst["data"][0]["user_social_provider"]
                                            , rst["data"][0]["user_group_seq"], rst["data"][0]["user_group_name"], user_photo_url)
        
        rst["data"][0]["user_photo_url"] = user_photo_url

        token = create_full_token(encrypt_token, rst["data"][0])
        # 5) 프런트엔드로 리다이렉트 또는 JSON 응답
        #return JSONResponse(status_code=200, content={ "result" : "ok", "msg" : "Login Sucess!!" , "data" : token }) 
        return loginCompletedEvent(token)
    except Exception as e:
        return resultAlertMsg("Login Failed", "Google Social Login Failed!!")
        #return JSONResponse(status_code=400, content={ "result" : "error", "msg" : "Google Social Login Faild!!" , "data" : str(e) }) 


## 시스템마다 상이할듯하여 별도로 만듬.
def naver_callbackEvent(code: str = None, state: str = None, error: str = None, error_description: str = None):
    if error:
        return resultAlertMsg("Login Failed", f"Naver Login Failed : {error}")
    if not code:
        return resultAlertMsg("Login Error", f"Naver Access Code Not Found!!") 
    token = {}
    msg = ""

    try:
        # 1) code로 토큰 교환
        data = {
            "code": code,
            "state" : state,
            "client_id": NAVER_CLIENT_ID,
            "client_secret": NAVER_CLIENT_SECRET,
            "redirect_uri": NAVER_REDIRECT_URI.format(url=SERVICE_INFO['host_b_domain']), 
            "grant_type": "authorization_code",
        }
        r = requests.post(NAVER_TOKEN_URL, params=data)
        if r.status_code != 200:
            return resultAlertMsg("Login Error", f"NAVER OAuth Login Failed!") 

        token_json = r.json()
        access_token = token_json["access_token"]
        refresh_token = token_json["refresh_token"]

        #print("google_token : ", token_json)

        # 2) 토큰으로 사용자 정보 가져오기
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_resp = requests.get(NAVER_PROFILE_URL, headers=headers)
        if userinfo_resp.status_code != 200:
            return resultAlertMsg("Login Failed", f"Failed to fetch user info from Naver")
        
        userinfo = userinfo_resp.json()["response"]
        if userinfo is None:
            return resultAlertMsg("Login Failed", f"Failed to fetch user info from Naver")

        #print("Google User Info :" , userinfo)

        # 3) 이메일 등을 확인해 내부 DB에 사용자 정보 등록 or 기존 계정 찾기
        user_social_in_id = userinfo["id"]
        user_social_id = userinfo["email"]
        user_social_name = userinfo["name"]
        user_photo_url = userinfo["profile_image"] if "profile_image" in userinfo else ""

        # DB 조회/생성 로직
        rst = userCheckAndSave(user_social_in_id, user_social_id, user_social_name, "2", access_token, refresh_token)


        if rst["result"] != "ok":
            return resultAlertMsg("Login Failed", rst["msg"])

        # 4) 자체 JWT(또는 세션) 발급하여 로그인 처리
        # (JWT 발급 예시)        
        #user_seq: int, user_id: str, user_name: str, user_social_seq: str, user_social_id: str, user_social_provider: str, user_group_seq: str
        encrypt_token = create_access_token(rst["data"][0]["user_seq"], rst["data"][0]["user_id"], rst["data"][0]["user_name"]
                                            , rst["data"][0]["user_social_seq"], rst["data"][0]["user_social_id"]
                                            , rst["data"][0]["user_social_provider_seq"], rst["data"][0]["user_social_provider"]
                                            , rst["data"][0]["user_group_seq"], rst["data"][0]["user_group_name"], user_photo_url)

        rst["data"][0]["user_photo_url"] = user_photo_url

        token = create_full_token(encrypt_token, rst["data"][0])
        # 5) 프런트엔드로 리다이렉트 또는 JSON 응답
        #return JSONResponse(status_code=200, content={ "result" : "ok", "msg" : "Login Sucess!!" , "data" : token }) 
        return loginCompletedEvent(token)
    except Exception as e:
        return resultAlertMsg("Login Failed", "Naver Social Login Faild!!")



#"user_social_provider" : "1/GOOGLE", "2/NAVER"
def userCheckAndSave(user_social_in_id, user_social_id, user_social_name, user_social_provider: str = "", access_token:str = "", refresh_token:str = ""):
    rstData = { "result" : "ERROR", "msg" : "ERROR" , "data" : []}

    sql = f"""
    select a.user_seq, a.user_id, a.user_name, b.socialaccount_seq as user_social_seq, b.social_id as user_social_id,  c.socialprovider_seq as user_social_provider_seq, c.socialprovider_name as user_social_provider, d.group_seq as user_group_seq, e.group_name as user_group_name
    from aasrepo.users a
    left join aasrepo.socialaccounts b on a.user_seq = b.user_seq
    join aasrepo.socialproviders c on b.socialprovider_seq = c.socialprovider_seq
    left join aasrepo.users_group d on a.user_seq = d.user_seq
    left join aasrepo.groups e on d.group_seq = e.group_seq
    where b.social_id = '{user_social_id}'
        and c.socialprovider_seq  = {user_social_provider}

    """

    sql2 = f"""
    WITH ins_user AS (
        insert into aasrepo.users (user_id, user_name, pw_hash, status, start_timestamp, create_user_seq)
        values('{user_social_id}', '{user_social_name}', '{refresh_token}', 'Y', localtimestamp, 0)
        RETURNING user_seq, user_id, user_name
    ), ins_social as (
        insert into aasrepo.socialaccounts (socialprovider_seq, social_id, social_in_id, user_seq, access_token, refresh_token, status, create_user_seq, create_date)
        select '{user_social_provider}', '{user_social_id}', '{user_social_in_id}', user_seq, '{access_token}', '{refresh_token}', 'Y', 0, localtimestamp
        from ins_user
        RETURNING socialprovider_seq, socialaccount_seq, social_id, user_seq
    ), ins_group as (
	    insert into aasrepo.users_group (user_seq, group_seq)
	    select user_seq, 3 as group_seq
	    from ins_user
		RETURNING user_seq, group_seq
	) 

    select a.user_seq, a.user_id, a.user_name, b.socialaccount_seq as user_social_seq, b.social_id as user_social_id
        , c.socialprovider_seq as user_social_provider_seq, c.socialprovider_name as user_social_provider
        , d.group_seq as user_group_seq, e.group_name as user_group_name
	from ins_user a
    join ins_social b on a.user_seq = b.user_seq
    join aasrepo.socialproviders c on b.socialprovider_seq = c.socialprovider_seq
    join ins_group d on a.user_seq = d.user_seq
    left join aasrepo.groups e on d.group_seq = e.group_seq
    """
    try:
    
        rst = postQueryDataSet(sql)

        if(rst["result"] != "ok"):
            rstData = { "result" : "ERROR", "msg" : "UserInfo Check Error. " + rst["msg"] , "data" : []}
            return

        ## 로그인 정보 없으면 저장 후 정보 호출
        if len(rst["data"]) == 0:
            rst2 = postQueryDataSet(sql2)

            if(rst2["result"] != "ok"):
                rst2 = { "result" : "ERROR", "msg" : "UserInfo Save Error. " + rst2["msg"] , "data" : []}
            rstData = rst2
        else:
            rstData = rst

    except Exception as e:
        rstData = { "result" : "ERROR", "msg" : "[Exception] UserInfo Checking Error." , "data" : []}
    finally:
        return rstData

    
## 팝업 알림 리턴
def resultAlertMsg(title, msg, isclose = True, actionScript=""):

    if isclose:
        actionScript = actionScript + "window.close();" 
    return HTMLResponse(content=f"""
            <html>
                <head>
                    <title>{title}</title>
                    <script>
                        alert("{msg}");
                        {actionScript}
                    </script>
                </head>
                <body>
                </body>
            </html>
        """)    


## 로그인 완료 처리
def loginCompletedEvent(token: str = ""):
    import json
    payload = json.dumps({ "type": "login", "token": token })
    return HTMLResponse(content=f"""
        <html>
            <head><title>로그인 완료</title></head>
            <body>
                <script>
                    window.opener.postMessage({payload}, "*");
                    window.close();
                </script>
            </body>
        </html>
    """)



## 사용자 현황
async def userListEvent(userinfo, searchKey, user_seq : Union[int, str] = "", group_seq: Union[int, str] = "", pageNumber = 1, pageSize = 10, pageMode = False):

    lang_code = "1" if userinfo is None else userinfo.lang_code

    rstData = { "result" : "error", "msg" : "UserInfo List Error!!" , "data" : ""}

    sql = f"""
    (
    select a.user_seq, a.user_id, a.pw_hash, a.user_name, aasrepo.fncodenm(coalesce(a.status, 'Y'), {lang_code} ) as status_nm
        , coalesce(a.status, 'Y') as status
        , a.user_phonenumber ,a.start_timestamp
        , b.socialaccount_seq, b.social_id, b.social_in_id, b.socialprovider_seq,  e.socialprovider_name
        , c.group_seq as user_group_seq, d.group_name as user_group_name
    from aasrepo.users a
    left join aasrepo.socialaccounts b on a.user_seq = b.user_seq
    left join aasrepo.users_group c on a.user_seq = c.user_seq
    left join aasrepo.groups d on c.group_seq = d.group_seq
    left join aasrepo.socialproviders e on b.socialprovider_seq = e.socialprovider_seq
    where (
        lower(a.user_id) like '%' || lower('{searchKey}') || '%' or lower(a.user_name) like '%' || lower('{searchKey}') || '%' 
        or user_phonenumber like '%{searchKey}%' 
        )  
        and ( a.user_seq::text = '{user_seq}' or '{user_seq}' = '')
        and ( c.group_seq::text = '{group_seq}' or '{group_seq}' = '')
    order by a.user_seq desc
    )
"""

    try:
        rst = await async_postQueryPageData(sql, pageNumber, pageSize, "", "", None, True, False, pageMode)
        
        if rst["result"] != "ok" :
            return JSONResponse(status_code=200, content=rst) 

        return JSONResponse(status_code=200, content=rst) 
        
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=500, content=rstData) 
    
async def userInfoUpdateEvent(userinfo, body):
    rstData = { "result" : "error", "msg" : "UserInfo Update Failed!!" , "data" : ""}

    if userinfo.user_group_seq == 3:
        return JSONResponse(status_code=403, content={ "result" : "error", "msg" : "You don't have permission." , "data" : ""}) 

    sql = f"""
    with user_tbl as (
        UPDATE aasrepo.users 
        SET user_id= '{body["user_id"]}'
        , user_name='{body["user_name"]}'
        , user_phonenumber='{body["user_phonenumber"]}'
        , status= '{ 'Y' if body["status"] == '' else body["status"] }'
        { ', close_timestamp = localtimestamp' if body["status"] == 'N' else ', close_timestamp = null'}
        , last_mod_user_seq={userinfo.user_seq}, last_mod_date= localtimestamp
        WHERE user_seq={body["user_seq"]}
        returning user_seq
    ), group_tbl as (
        INSERT INTO aasrepo.users_group (user_seq, group_seq)
		SELECT src.user_seq, {body["user_group_seq"]}
		FROM user_tbl AS src
		ON CONFLICT(user_seq)
		do UPDATE SET user_seq = EXCLUDED.user_seq, group_seq = EXCLUDED.group_seq
		returning user_seq
    )
    select user_seq 
    from user_tbl
        """
    
    try:
        rst = await async_postQueryDataOne(sql, user_seq = userinfo.user_seq)
        
        if rst["result"] != "ok" :
            return JSONResponse(status_code=200, content=rst) 

        return JSONResponse(status_code=200, content=rst) 
        
    except Exception as e:
        rstData["msg"] = str(e)
        return JSONResponse(status_code=500, content=rstData) 