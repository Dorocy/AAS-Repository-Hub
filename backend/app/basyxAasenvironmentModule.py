import jpype
from jpype.types import *
from jpype import JClass, JProxy, JByte
from fastapi import UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Literal
from processor.postgresProcess import *
import io
import time
import glob
import os
from  tools.jdbcTool import setJavaEnvironment
import json
from app.aasModelModule import *
import urllib.parse
# import asyncio
from ftfy import fix_text
from zipfile import ZipFile
from io import BytesIO
import mimetypes
from config.config import get_config_value

def start_jvm():

    setJavaEnvironment()

    # JVM 시작: basyx 관련 jar 파일들이 들어있는 디렉토리
    # jar_dir = "./basyx"
    # all_jars = glob.glob(os.path.join(jar_dir, "*.jar"))

    # if not jpype.isJVMStarted():
    #     jpype.startJVM(classpath=all_jars)

    jar_dir = "./basyx"
    all_jars = glob.glob(os.path.join(jar_dir, "*.jar"))

    # JVM 동적 라이브러리 경로 (사용자의 실제 경로에 맞게 수정)
    jvm_dll_path = os.path.abspath("./jdk/mac/jdk-17.0.2.jdk/Contents/Home/lib/libjli.dylib")

    if not jpype.isJVMStarted():
        jpype.startJVM(jvm_dll_path, "-ea", classpath=all_jars)
        
        print("java version:", jpype.java.lang.System.getProperty("java.version"))
        print("java :", jpype.java.lang.System.getProperty("java.version"))


class PyMultipartFile:
    """
    Spring의 MultipartFile 인터페이스를 구현하는 클래스 정의
    이 클래스는 JPype의 JProxy를 통해 Java 코드가 필요한 메서드(getName(), getInputStream() 등)를 호출할 수 있도록 함
    """
    def __init__(self, file_bytes, content_type, name, original_filename):
        self.file_bytes = file_bytes
        self.content_type = content_type
        self.name = name
        self.original_filename = original_filename

    def getName(self):
        return self.name

    def getOriginalFilename(self):
        return self.original_filename

    def getContentType(self):
        return self.content_type

    def isEmpty(self):
        return len(self.file_bytes) == 0

    def getSize(self):
        return len(self.file_bytes)

    def getBytes(self):
        return self.file_bytes

    def getInputStream(self):
        from java.io import ByteArrayInputStream
        # Python bytes를 Java byte[]로 변환
        # java_bytes = jpype.JArray(JByte)(list(self.file_bytes))
        # return ByteArrayInputStream(java_bytes)
    
        # Python의 byte 타입 0~255
        # Java의 byte 타입은 -128부터 127까지 표현되므로, 값이 128 이상이면 256을 빼서 변환
        converted = [x if x < 128 else x - 256 for x in self.file_bytes]
        java_bytes = jpype.JArray(JByte)(converted)
        return ByteArrayInputStream(java_bytes)

    def transferTo(self, dest):
        pass

async def aasModelImportEvent(userinfo, file, id):
    """
    AASX 파일을 import하고 JSON 문자열로 반환
    """

    file_bytes = await file.read()

    # Spring의 MultipartFile 인터페이스 클래스
    MultipartFile = jpype.JClass("org.springframework.web.multipart.MultipartFile")
    # JProxy를 통해 MultipartFile 인터페이스의 구현체 생성
    multipart_file = JProxy(MultipartFile, inst=PyMultipartFile(file_bytes, file.content_type, file.filename, file.filename))
    
    # Java 컨트롤러 인스턴스 생성
    # parseAASXFile 메서드는 HttpServletRequest나 AasEnvironment 같은 의존성을 사용하지 않으므로 None 전달
    AasEnvController = jpype.JClass("org.eclipse.digitaltwin.basyx.aasenvironment.http.AasEnvironmentApiHTTPController")
    controller = AasEnvController(None, None)
    
    # parseAASXFile 메서드 호출
    response = controller.parseAASXFile(multipart_file)
    
    # ResponseEntity<String>에서 JSON 결과와 상태 코드 추출
    status_code = response.getStatusCodeValue()
    json_result = str(response.getBody())
    
    # FIXME: jpype 가 Java의 실제 작업 완료를 기다리지 않는 문제로 추정
    # 결과가 없으면 2초정도 기다리는걸로 해놔서 되긴 되는데 문제 해결이 필요함
    if status_code == 200 and (json_result is None or str(json_result).strip() == ""):
        for _ in range(20):
            # time.sleep(0.1)
            asyncio.sleep(0.1)
            if json_result is not None and str(json_result).strip() != "":
                break

    # 신규(parameter id 없음) : 중복체크 - 중복이면 error
    # 수정(parameter id 있음) : parameter id와 json_result의 assetAdministrationShells "id" value가 같은지 체크 - 다르면 error
    if status_code == 200:

        try:
            json_result = json_result.replace('\ufeff', '') # BOM(Byte Order Mark) 문자 제거
            result_dict = json.loads(json_result) 
            
            shells = result_dict.get("assetAdministrationShells", [])

            if not shells:
                return JSONResponse(status_code=400, content={"result": "error", "msg": "No AssetAdministrationShell found in AAS JSON.", "data": result_dict})
            
            aas_id = shells[0].get("id")

            if not id:
                id_chk_rst = await duplicateAasmodelIdCheckEvent(aas_id) #XXX: DB 처리 오류나도 True 인 문제 수정 필요
                
                if id_chk_rst:
                    return JSONResponse(status_code=400, content={"result": "error", "msg": f"AAS Model ID '{aas_id}' already exists.", "data": ""})
                    
            else:
                if aas_id != id:
                    return JSONResponse(status_code=400, content={"result": "error", "msg": f"AAS Model ID [File] '{aas_id}' differ from AAS Model ID '{id}'. ", "data": ""})

        except Exception as e:
            return JSONResponse(status_code=500, content={"result": "error", "msg": f"JSON parsing error: {str(e)}", "data": ""})

    if status_code != 200:
        return JSONResponse(status_code=status_code, content={"result": "error", "msg": "AASX file import failed", "data": ""})
    else:
        try:
            # json_result = clean_empty_structures(json_result)
            env_json = json.loads(json_result)
            env_json = clean_empty_structures(env_json)
            
        except Exception as e:
            return JSONResponse(status_code=500, content={"result": "error", "msg": f"JSON parsing error: {str(e)}", "data": ""})

        return JSONResponse(status_code=200, content={"result": "ok", "msg": "AASX file import successful", "data": env_json})
async def aasModelValidateEvent(userinfo, file):
    """
    AASX 파일 유효성 검사
    """

    file_bytes = await file.read()

    # Spring의 MultipartFile 인터페이스 클래스
    MultipartFile = jpype.JClass("org.springframework.web.multipart.MultipartFile")
    # JProxy를 통해 MultipartFile 인터페이스의 구현체 생성
    multipart_file = JProxy(MultipartFile, inst=PyMultipartFile(file_bytes, file.content_type, file.filename, file.filename))
    
    # fat jar에 포함된 Java 클래스 로드
    AasEnvController = jpype.JClass("org.eclipse.digitaltwin.basyx.aasenvironment.http.AasEnvironmentApiHTTPController")
    controller = AasEnvController(None, None) # 의존성(HttpServletRequest, AasEnvironment) 사용안함

    # validateEnvironment 메서드 호출: ResponseEntity<Boolean> 반환
    response = controller.validateEnvironment(multipart_file)

    # ResponseEntity<Boolean>에서 결과와 상태 코드 추출
    result_boolean = response.getBody()
    status_code = response.getStatusCodeValue()

    result_boolean = bool(result_boolean.booleanValue())

    if status_code != 200:
        return JSONResponse(status_code=status_code, content={"result": "error", "msg": "AASX file validation failed", "data": result_boolean})
    else:
        return JSONResponse(status_code=200, content={"result": "ok", "msg": "AASX file validation successful", "data": result_boolean})


# Python에서 Java의 MultipartFile 인터페이스를 구현하기 위한 클래스
class PyMultipartFile:
    def __init__(self, file_bytes, content_type, name, original_filename):
        # file_bytes: 파일 내용
        # content_type: 파일의 MIME 타입 
        # name: 파일 이름
        # original_filename: 원래 파일명
        self.file_bytes = file_bytes
        self.content_type = content_type
        self.name = name
        self.original_filename = original_filename

    def getName(self): return self.name
    def getOriginalFilename(self): return self.original_filename
    def getContentType(self): return self.content_type
    def isEmpty(self): return len(self.file_bytes) == 0
    def getSize(self): return len(self.file_bytes)
    def getBytes(self): return self.file_bytes

    def getInputStream(self):
        converted = [b if b < 128 else b - 256 for b in self.file_bytes]
        java_bytes = jpype.JArray(JByte)(converted)
        return jpype.JClass("java.io.ByteArrayInputStream")(java_bytes)

    def transferTo(self, dest): pass

class AASDownloadRequest(BaseModel):
    name: str
    source: Literal["json", "db"] = "json" 
    model_key: Optional[str] = None 
    jsonData: Optional[dict] = None       


# FIXME: 파일 구성에 문제가 있는경우 
# 파싱까지는 잘 되지만 그거 그대로 내려받으면 download 받았을 때 package explorer에서 안열림.. 확인 필요
async def aasModelDownloadEvent(userinfo, body: AASDownloadRequest, format: str, modelType: str):
    """
    파일 다운로드
    """
    try:
        # from java.io import ByteArrayOutputStream
        ByteArrayOutputStream = jpype.JClass("java.io.ByteArrayOutputStream")

        filename = body.name
        attachments_json = None
        
        if body.source == "json": # JSON을 파일로 내려받을 경우
            if body.jsonData is None:
                return JSONResponse(status_code=400, content={"result": "error", "msg": "jsonData is required when source is 'json'"})
            try:
                # xml에서 허용되지 않는 문자가 있을경우 오류남
                json_str = normalize_text(body.jsonData) 
                json_str = json.dumps(json_str)
            except Exception as e:
                return JSONResponse(status_code=500, content={"result": "error", "msg": f"Failed to serialize jsonData: {str(e)}"})
        elif body.source == "db": # 저장된 데이터를 파일로 내려받을 경우
            if not body.model_key:
                return JSONResponse(status_code=400, content={"result": "error", "msg": "model_key is required when source is 'db'"})
            try:
                
                if not str(body.model_key).isdigit():
                    return JSONResponse(status_code=500, content={ "result" : "error", "msg" : "Invalid model_key" , "data" : ""})
                          
                db_result = await aasModelMetadata(body.model_key, modelType)

                if not db_result:
                    return JSONResponse(status_code=500, content={ "result" : "error", "msg" : "AAS Model Not Exists" , "data" : ""}) 
                
                # DB에서 받아온 JSON string을 dict로 파싱 후 문자열 대체하도록 수정
                # json_dict = json.loads(db_result)
                json_str = normalize_text(db_result)
                json_str = json.dumps(json_str)
                
                # aasx 파일일 경우 저장 된 첨부파일이 있는지 확인
                if format == "aasx":
                    if modelType == "aasmodel":
                        file_key = body.model_key
                    else:
                        file_key = await aasModelKey(body.model_key)
                        
                    file_content_result = await aasModelFileContent(file_key)
                    if file_content_result:
                        attachments_dict = {
                            row["filename"]: base64.b64encode(row["content"]).decode("utf-8")
                            for row in file_content_result
                        }
                        attachments_json = json.dumps(attachments_dict)

                        
            except Exception as e:
                return JSONResponse(status_code=500, content={"result": "error", "msg": f"DB failed: {str(e)}"})
        else:
            return JSONResponse(status_code=400, content={"result": "error", "msg": "Invalid source value."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"result": "error", "msg": f"Error input processing: {str(e)}"})
    
    try:
        file_bytes = json_str.encode("utf-8")  # JSON 문자열을 UTF-8 인코딩한 바이트 배열로 변환
    except Exception as e:
        return JSONResponse(status_code=500, content={"result": "error", "msg": f"Failed to encode JSON string: {str(e)}"})
        
    try:
        MultipartFile = JClass("org.springframework.web.multipart.MultipartFile")
        # JSON 문자열을 파일처럼 전달하기 위해 PyMultipartFile 사용
        multipart_file = JProxy(MultipartFile, inst=PyMultipartFile(file_bytes, "application/json", "json", "json"))
        
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"result": "error", "msg": f"Failed to create MultipartFile proxy: {str(e)}"})
    
    try:
        AasRepository = JClass("org.eclipse.digitaltwin.basyx.aasrepository.AasRepository")
        SubmodelRepository = JClass("org.eclipse.digitaltwin.basyx.submodelrepository.SubmodelRepository")
        ConceptDescriptionRepository = JClass("org.eclipse.digitaltwin.basyx.conceptdescriptionrepository.ConceptDescriptionRepository")
        # 인터페이스에 전달할 인스턴스 (메서드 호출이 일어나지 않도록 None)
        aasRepo = JProxy(AasRepository, {
            "getAas": lambda id: None,
            "createAas": lambda aas: None,
            "updateAas": lambda aas: None,
        })
        submodelRepo = JProxy(SubmodelRepository, {
            "getSubmodel": lambda id: None,
            "createSubmodel": lambda submodel: None,
            "updateSubmodel": lambda submodel: None,
        })
        conceptRepo = JProxy(ConceptDescriptionRepository, {
            "getConceptDescription": lambda id: None,
            "createConceptDescription": lambda cd: None,
            "updateConceptDescription": lambda cd: None,
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"result": "error", "msg": f"Failed to create repository proxies: {str(e)}"})
    
    try:
        # DefaultAASEnvironment 인스턴스를 생성
        DefaultAASEnvironment = JClass("org.eclipse.digitaltwin.basyx.aasenvironment.base.DefaultAASEnvironment")
        aas_env = DefaultAASEnvironment(aasRepo, submodelRepo, conceptRepo)
    except Exception as e:
        return JSONResponse(status_code=500, content={"result": "error", "msg": f"Failed to create AAS environment: {str(e)}"})
    
    try:
        # 컨트롤러 생성 시 AasEnvironment 인스턴스 전달
        ControllerClass = JClass("org.eclipse.digitaltwin.basyx.aasenvironment.http.AasEnvironmentApiHTTPController")
        controller = ControllerClass(None, aas_env)
    except Exception as e:
        return JSONResponse(status_code=500, content={"result": "error", "msg": f"Failed to create AAS controller: {str(e)}"})
    
    try:
        JavaString = jpype.JClass("java.lang.String")
        attachments_java_str = JavaString(attachments_json or "") # None이면 ""
        response = controller.downloadAASXFile(multipart_file, format, attachments_java_str) 


        status_code = response.getStatusCodeValue()
        resource = response.getBody()
    except Exception as e:
        return JSONResponse(status_code=500, content={"result": "error", "msg": f"Controller call failed: {str(e)}"}, media_type="application/json")
    
    if resource is None or status_code != 200:
        return JSONResponse(status_code=status_code, content={"result": "error", "msg": f"Java serialization failed: status {status_code}"})
    
    try:
        input_stream = resource.getInputStream()
        buffer = jpype.JArray(JByte)(1024)
        output_stream = ByteArrayOutputStream()
        while True:
            read = input_stream.read(buffer)
            if read == -1:
                break
            output_stream.write(buffer, 0, read)
        result_bytes = bytes(output_stream.toByteArray())
    except Exception as e:
        return JSONResponse(status_code=500, content={"result": "error", "msg": f"Failed to read output stream: {str(e)}"})
    
    content_type = {
        "json": "application/json",
        "xml": "application/xml",
        "aasx": "application/asset-administration-shell-package+xml"
    }.get(format, "application/json")
    
    filename = urllib.parse.quote(f"{filename}.{format}") # 파일명 인코딩

    return StreamingResponse(io.BytesIO(result_bytes),
                             media_type=content_type,
                             headers={"Content-Disposition": f"attachment; filename={filename}.{format}"})

# AAS Model Json 데이터 조회
async def aasModelMetadata(model_key, model_type):
    
    if model_type == 'aasmodel':
        sql = f"""
                SELECT a.metadata
                  FROM aasrepo.aasmodels a
                 WHERE a.aasmodel_seq = {model_key};
                """
    else:
        sql = f"""
                SELECT aasrepo.fn_instance_merge(instance_seq) metadata
                  FROM aasrepo.aasinstance
                 WHERE instance_seq = {model_key};
                """
    rstData = await async_postQueryDataOne(sql)
    return rstData["data"]

# AAS Instance Model Key 조회
async def aasModelKey(model_key):
    
    sql = f"""
            SELECT aasmodel_seq
                FROM aasrepo.aasinstance_aasmodels
                WHERE instance_seq = {model_key};
            """
    rstData = await async_postQueryDataOne(sql)
    return rstData["data"]


async def aasModelFileContent(model_key):
    sql = f"""
        SELECT filename, realpath
          FROM aasrepo.aasmodel_attachments
         WHERE aasmodel_seq = {model_key};
    """
    rstData = await async_postQueryDataSet(sql)

    result = []
    for row in rstData["data"]:
        
        realpath = row.get("realpath")        
        filename = row.get("filename")

        url_prefix = get_config_value("file", "mainpath") 
        file_root = get_config_value("file", "fullpath")

        # 실제 경로
        realpath = realpath[len(url_prefix):].lstrip("/")
        realpath = os.path.join(file_root, realpath).replace("\\", "/")   

        try:
            with open(realpath, "rb") as f:
                content = f.read()
            result.append({
                "filename": filename,
                "content": content
            })
        except Exception as e:
            continue

    return result


# 유니코드 텍스트를 입력받아, 문자 깨짐이나 비정상적인 표현을 자동으로 고쳐주는 함수
def normalize_text(obj):
    if isinstance(obj, str):
        return fix_text(obj) 
    elif isinstance(obj, dict):
        return {k: normalize_text(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_text(item) for item in obj]
    else:
        return obj
    

def clean_empty_structures(obj):
    """
    AAS JSON 내에서 의미 없는 빈 구조 제거:
    - embeddedDataSpecifications: [{}] 제거
    - keys가 비어 있으면 전체 제거
    - "dataSpecification"이 없으면 제거
    """
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():

            # keys 필드가 빈 리스트인 경우 전체 항목 제거
            if isinstance(v, dict) and "keys" in v and isinstance(v["keys"], list) and len(v["keys"]) == 0:
                continue 

            # embeddedDataSpecifications 처리
            if k == "embeddedDataSpecifications" and isinstance(v, list):
                filtered_list = []
                for item in v:
                    if isinstance(item, dict):
                        # "dataSpecification"이 없으면 제거
                        if "dataSpecificationContent" in item and "dataSpecification" not in item:
                            continue

                        # "dataSpecification"이 있지만 keys가 없는 경우도 제거
                        ds = item.get("dataSpecification")
                        if isinstance(ds, dict) and not ds.get("keys"):
                            continue

                        filtered_list.append(clean_empty_structures(item))
                if not filtered_list or filtered_list == [{}]:
                    continue
                cleaned[k] = filtered_list
                continue

            # 재귀 처리
            cleaned_v = clean_empty_structures(v)

            # [{}] 제거
            if isinstance(cleaned_v, list) and cleaned_v == [{}]:
                continue

            cleaned[k] = cleaned_v
        return cleaned
    elif isinstance(obj, list):
        return [clean_empty_structures(item) for item in obj]
    else:
        return obj
