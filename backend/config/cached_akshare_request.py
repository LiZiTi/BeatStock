import os
import inspect
from functools import wraps
from config.LRUCache import cache  # 假设你已经实现了LRU缓存工具类

CACHE_TTL = 3600  # 1小时缓存有效期（秒）

def cached_akshare_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 获取当前函数所在的文件路径
        file_path = os.path.abspath(inspect.getfile(func))

        # 生成一个唯一的缓存键，基于模块文件路径、函数名称和参数
        cache_key = f"{file_path}:{func.__name__}:{args}:{kwargs}"

        # 尝试从缓存中获取数据
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            print(f"从缓存中获取数据: {func.__name__} from {file_path}")
            return cached_data

        # 调用原始 akshare 请求
        print(f"调用 akshare API: {func.__name__} from {file_path}")
        result = func(*args, **kwargs)
        
        # 将结果存储到缓存中
        cache.set(cache_key, result, ttl=CACHE_TTL)
        return result

    return wrapper
