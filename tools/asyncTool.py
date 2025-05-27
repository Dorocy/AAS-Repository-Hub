import asyncio
from functools import wraps

def asyncify(func):
    # 동기 함수인지 확인
    # if not asyncio.iscoroutinefunction(func):
    #     warnings.warn(f"Function {func.__name__} is a synchronous function. It is being wrapped asynchronously.", UserWarning)
    @wraps(func)
    async def wrapper(*args, **kwargs):
        data = await asyncio.to_thread(func, *args, **kwargs)
        
        return data
    
    return wrapper