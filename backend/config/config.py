## DEBUG모드일경우 출력되게/예외처리 출력은 제외
## 함수 개별 설정 가능하게 함수별

import os
import yaml 

def config_file_path(file_name='config.yaml'):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_dir, file_name)

def get_config_value(section, key, sub_key=None, default_value=None, yaml_file = config_file_path()):
    with open(yaml_file, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        # 깊이 3단계의 키 접근
        if sub_key:
            return config.get(section, {}).get(key, {}).get(sub_key, default_value)
        else:
            return config.get(section, {}).get(key, default_value)

def get_section_dict(section, yaml_file=config_file_path()):
    with open(yaml_file, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

        # 특정 섹션의 모든 키-값 쌍을 딕셔너리 형태로 반환
        return config.get(section, {})
