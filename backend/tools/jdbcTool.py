import os
import platform 

# def setJavaEnvironment():
#     system = platform.system()
#     jdk_path: str
#     if system == 'Windows':
#         jdk_path = os.path.join(os.getcwd(), 'jdk/windows', 'openjdk-17.0.2')
#     elif system == 'Linux':
#         jdk_path = os.path.join(os.getcwd(), 'jdk/linux', 'openjdk-17.0.2')
#     os.environ['JAVA_HOME'] = jdk_path
#     #print(os.environ['JAVA_HOME'])


#현재 macos에서 실행중임...그래서 수정
def setJavaEnvironment():
    system = platform.system()
    jdk_path: str
    if system == 'Windows':
        jdk_path = os.path.join(os.getcwd(), 'jdk/windows', 'openjdk-17.0.2')
    elif system == 'Linux':
        jdk_path = os.path.join(os.getcwd(), 'jdk/linux', 'openjdk-17.0.2')
    elif system == 'Darwin':  # macOS
        jdk_path = os.path.join(os.getcwd(), 'jdk/mac', 'openjdk-17.0.2')
    os.environ['JAVA_HOME'] = jdk_path
