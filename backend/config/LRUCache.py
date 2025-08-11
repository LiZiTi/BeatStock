import time
import threading
from collections import OrderedDict

class LRUCache:
    def __init__(self, max_size=100):
        self._cache = OrderedDict()  # 使用OrderedDict维护缓存顺序
        self._max_size = max_size    # 设置缓存的最大容量
        self._lock = threading.Lock()  # 用于线程安全

    def set(self, key, value, ttl=None):
        """将数据存储到缓存中，达到最大容量时淘汰最不常用的键"""
        expire_time = time.time() + ttl if ttl else None
        with self._lock:
            if key in self._cache:
                # 如果键已存在，先删除，后面再添加，确保它在末尾
                self._cache.pop(key)
            # 添加新键，或将其移动到末尾
            self._cache[key] = (value, expire_time)
            # 如果超过最大缓存容量，移除最不常使用的键（最前面的项）
            if len(self._cache) > self._max_size:
                self._cache.popitem(last=False)  # 删除最前面的键，即最少使用的

    def get(self, key):
        """从缓存中获取数据，如果缓存项已过期或不存在，则返回None"""
        with self._lock:
            if key not in self._cache:
                return None
            value, expire_time = self._cache.pop(key)  # 弹出项
            # 检查是否过期
            if expire_time and expire_time < time.time():
                return None
            # 将键重新插入到字典末尾，表示它是最近使用的
            self._cache[key] = (value, expire_time)
            return value

    def delete(self, key):
        """删除缓存中的某个键"""
        with self._lock:
            if key in self._cache:
                self._cache.pop(key)

    def clear(self):
        """清空缓存"""
        with self._lock:
            self._cache.clear()

    def clean_expired(self):
        """手动清理过期的缓存项"""
        with self._lock:
            keys_to_delete = []
            for key, (value, expire_time) in self._cache.items():
                if expire_time and expire_time < time.time():
                    keys_to_delete.append(key)
            for key in keys_to_delete:
                self._cache.pop(key)

# 示例使用
cache = LRUCache(max_size=1024)