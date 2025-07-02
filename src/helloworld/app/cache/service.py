import asyncio
import time
import json
from collections import deque
from typing import Any, Dict, List, Optional, Tuple

class LiteAsyncCache:
    __slots__ = ('cache', 'keys_queue', 'lock', 'max_size')
    
    def __init__(self, max_size: Optional[int] = 5000):
        # Store keys: (value, expiration timestamp)
        self.cache = {}
        
        # Maintains insertion order (FIFO)
        self.keys_queue = deque()  
        
        # Ensure thread-safe operations
        self.lock = asyncio.Lock()
        
        # Maximum cache size (None = unlimited)
        self.max_size = max_size

    async def get(self, key: str) -> Any:
        """Get value with TTL check"""
        async with self.lock:
            return self._get_with_ttl_check(key)

    async def mget(self, keys: List[str]) -> Dict[str, Any]:
        """Batch get with TTL check"""
        async with self.lock:
            return {k: self._get_with_ttl_check(k) for k in keys}

    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Set value with optional TTL"""
        return await self.mset({key: value}, ttl=ttl)

    async def mset(self, items: Dict[str, Any], ttl: Optional[float] = None) -> bool:
        """Batch set with optional TTL"""
        async with self.lock:
            # Calculate absolute expiration time
            expire_at = time.time() + ttl if ttl is not None else None
            
            # Clean expired keys at queue head
            self._clean_head_expired()
            
            # Identify new keys being added
            new_keys = [k for k in items if k not in self.cache]
            
            # Handle capacity overflow for new keys
            self._handle_overflow(len(new_keys))
            
            # Insert/update cache entries
            for key, value in items.items():
                is_new = key not in self.cache
                serialized_value = json.dumps(value, default=str)
                self.cache[key] = (serialized_value, expire_at)
                if is_new:
                    self.keys_queue.append(key)
            return True

    def _get_with_ttl_check(self, key: str) -> Any:
        """Get with TTL expiration check"""
        if key not in self.cache:
            return None
            
        value, expire_at = self.cache[key]
        
        # Lazy deletion of expired items
        if expire_at is not None and expire_at < time.time():
            del self.cache[key]
            return None
            
        try:
            return json.loads(value)
        except Exception:
            return value

    def _clean_head_expired(self):
        """Clean consecutive expired keys at queue head"""
        while self.keys_queue:
            oldest_key = self.keys_queue[0]
            
            # Skip if key was already deleted
            if oldest_key not in self.cache:
                self.keys_queue.popleft()
                continue
                
            value, expire_at = self.cache[oldest_key]
            
            # Stop at first non-expired key
            if expire_at is None or expire_at >= time.time():
                break
                
            # Remove expired key
            del self.cache[oldest_key]
            self.keys_queue.popleft()

    def _handle_overflow(self, new_count: int):
        """Handle capacity overflow"""
        if not self.max_size:
            return
            
        # Calculate overflow after cleanup
        current_size = len(self.cache)
        overflow = current_size + new_count - self.max_size
        
        # Evict oldest keys if still overflowing
        if overflow > 0:
            for _ in range(min(overflow, len(self.keys_queue))):
                if not self.keys_queue:
                    break
                    
                oldest_key = self.keys_queue.popleft()
                if oldest_key in self.cache:
                    del self.cache[oldest_key]

    async def size(self) -> int:
        """Get count of valid keys (excludes expired)"""
        return len(self.cache)


aiocache = LiteAsyncCache()


if __name__ == "__main__":
    async def demo():
        cache = LiteAsyncCache(max_size=3)
        
        # 设置带TTL的值
        await cache.set("temp", "data", ttl=0.5)  # 0.5秒后过期
        
        # 立即读取（有效）
        print(await cache.get("temp"))  # "data"
        
        # 0.6秒后读取
        await asyncio.sleep(0.6)
        print(await cache.get("temp"))  # None (自动删除)
        
        # 批量设置TTL
        await cache.mset(
            {"a": 1, "b": 2}, 
            ttl=1.0  # 统一过期时间
        )
        
        # 混合TTL设置
        await cache.set("c", 3)          # 永不过期
        await cache.set("d", 4, ttl=1)  # 10秒过期

        print(await cache.mget(["a", "b", "c", "d"]))  # None (自动删除)
        await asyncio.sleep(1.6)
        print(await cache.mget(["a", "b", "c", "d"]))  # None (自动删除)


        await cache.mset({"e": 5, "f": 6}, ttl=1)  # 淘汰b和c
        print(await cache.mget(["d", "e", "f"]))  # {'d':4, 'e':5, 'f':6}
        await asyncio.sleep(1.6)
        print(await cache.mget(["d", "e", "f"]))  # {'d':4, 'e':5, 'f':6}

        # 测试容量溢出
        await cache.mset({"g": 7, "h": 8, "i": 9}, ttl=1)  # 淘汰d和e
        print(await cache.mget(["d", "e", "f", "g", "h", "i"]))  # {'f':6, 'g':7, 'h':8, 'i':9}


    asyncio.run(demo())



# import asyncio
# from collections import deque
# from typing import Any, Dict, List, Optional

# class LiteAsyncCache:
#     __slots__ = ('cache', 'keys_queue', 'lock', 'max_size')  # 内存优化关键
    
#     def __init__(self, max_size: Optional[int] = 5000):
#         self.cache = {}
#         self.keys_queue = deque()
#         self.lock = asyncio.Lock()
#         self.max_size = max_size

#     async def get(self, key: str) -> Any:
#         async with self.lock:
#             return self.cache.get(key)

#     async def mget(self, keys: List[str]) -> Dict[str, Any]:
#         async with self.lock:
#             return {k: self.cache.get(k) for k in keys}

#     async def set(self, key: str, value: Any) -> bool:
#         async with self.lock:
#             if key not in self.cache:
#                 self._handle_overflow(1)
#                 self.keys_queue.append(key)
#             self.cache[key] = value
#             return True

#     async def mset(self, items: Dict[str, Any]) -> bool:
#         async with self.lock:
#             new_keys = [k for k in items if k not in self.cache]
#             self._handle_overflow(len(new_keys))
            
#             for key, value in items.items():
#                 if key not in self.cache:
#                     self.keys_queue.append(key)
#                 self.cache[key] = value
#             return True

#     def _handle_overflow(self, new_count: int):
#         if not self.max_size:
#             return
        
#         current_size = len(self.cache)
#         overflow = current_size + new_count - self.max_size
        
#         if overflow > 0:
#             for _ in range(min(overflow, len(self.keys_queue))):
#                 oldest_key = self.keys_queue.popleft()
#                 del self.cache[oldest_key]

#     async def size(self) -> int:
#         return len(self.cache)