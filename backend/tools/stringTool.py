
import datetime
import decimal
import uuid
import json

## postgreslq 은 공백처리 상관없는데 
## 타 DB json null로 나올경 우 공백으로 대체 
class NoneToEmptyJSON(json.JSONEncoder):
    def default(self, o):

        
        if o == None:
            o = ''
        elif type(o) == dict:
            return {self.default(key): self.default(value) for key, value in o.items()}
        elif type(o) == list or type(o) == tuple:
            return [self.default(item) for item in o]
        return o
    def encode(self, o):
        return super().encode(self.default(o))
    

def convert_null_to_blank(data):
        if isinstance(data, dict):
            return {k: convert_null_to_blank(v) if v is not None else '' for k, v in data.items()}
        elif isinstance(data, list):
            return [convert_null_to_blank(item) if item is not None else '' for item in data]
        else:
            return data    
        

def find_matching_indexes(array, value):
    indexes = []  # 일치하는 인덱스를 저장할 리스트

    for i in range(len(array)):
        if array[i] == value:
            indexes.append(i)

    return indexes

## 조건절에 ; 들어가지 않게 SQL INJECT 임시 처리
## 존재하면 : TRUE -> 알람 필요.
def valueValidationFalse(value):
    query_list = value.replace(" ", "").split(';')

    prohibited_keywords = ['allprivileges', 'grant', 'revoke', 'excecute', 'insert', 'insertinto', 'truncate', 'upsert', 'mergeinto', 'delete', 'create', 'drop', 'update', 'create', 'alter', 'deletefrom', 'truncatetable', 'dropdatabase', 'dropschema', 'merge']

    for query in query_list:
        for keyword in prohibited_keywords:
            if query.lower().startswith(keyword):
                return True

    if value.find(";") == -1:
        return False
    else:
        return True


def convert_tuple_to_json_list(columns, fetch_list):
    result_set: list = []

    for tuples in fetch_list:
        temp_dict = {}
        for column, value in zip(columns, tuples):
            if value is None:
                value = ""
            elif isinstance(value, datetime.date):
                value = value.strftime("%Y-%m-%d %H:%M:%S.%f")
            elif isinstance(value, float) or isinstance(value, decimal.Decimal):
                if str(value).find('.') == -1:
                    value = str(value)
                else:
                    value = str(value).rstrip('0').rstrip('.')

            temp_dict[column] = value

        result_set.append(temp_dict)

    return result_set


##json 문자열 여부 검증
def validate_json(query: str):
    try:
        # 문자열을 JSON으로 변환 시도
        data = json.loads(query)

        if isinstance(data, (dict, list)):
            return True, data
        else:
            return False, {}
    except json.JSONDecodeError:
        # JSON 변환에 실패하면 예외 발생
        return False, {}
    

## ISO8601에서 Date타입 구분 확인
def is_iso8601_datetime_before(value):
    
    try:
        datetime.datetime.fromisoformat(value)
        ##print("sssssss" , is_iso8601_datetime("2024-05-02T19:46:28.43")) ## 이게 오류남.... 밀리초가 1,2자리일경우...
        ##print("tttttt" , is_iso8601_datetime("2024-05-02T19:46:28.435"))
        return True
    except ValueError:
        return False
        
def is_iso8601_datetime(value):
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%dT%H", "%Y-%m-%dT%H:%M:%S.%f%z"):
        try:
            datetime.datetime.strptime(value, fmt)
            return True
        except ValueError:
            
            continue
    return False
        
## ISO8601에서 Date로 변경
def convert_ISO8601Date_to_Date(jsonData):
    # print("ddddddddd" , is_iso8601_datetime("2024-05-02T19:46:28.438554+09:00"))
    # print("sssssss" , is_iso8601_datetime("2024-05-02T19:46:28.43"))
    # print("tttttt" , is_iso8601_datetime("2024-05-02T19:46:28.435"))
    # print("aaaaa" , is_iso8601_datetime("2024-05-02T19:46:28.4"))
    # 키의 값을 확인하여 'T'를 제외
    if isinstance(jsonData, dict):
        return {k: convert_ISO8601Date_to_Date(v) if not (isinstance(v, (str)) and is_iso8601_datetime(v)) else v.replace('T', ' ') for k, v in jsonData.items()}
    elif isinstance(jsonData, list):
        return [convert_ISO8601Date_to_Date(item) if item is not None else 'null' for item in jsonData]
    else:
        return jsonData    

## 문자 
def remove_bom(text):
    if isinstance(text, str):
        return text.lstrip('\ufeff')
    return text

##숫자 변환 여부 확인
def is_numeric_string(s):
    return s.isdigit()

## float 포함 변환 여부 확인
def is_float_string(s):
    try:
        float(s)  # 또는 int(s)로 변경 가능
        return True
    except ValueError:
        return False

def newUUID():
    newUUID = f'''{str(uuid.uuid4())}'''
    return newUUID

## 포스트그리 $$ 치환
def dollarSign(string: str):
    newUUID = f'''dollar{str(uuid.uuid4()).replace("-", "")}'''
    return f''' ${newUUID}${string}${newUUID}$ '''


