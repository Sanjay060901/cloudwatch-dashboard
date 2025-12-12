import time
from threading import Lock

class SimpleTTLCache:
    def __init__(self):
        self._store = {}
        self._lock = Lock()

    def set(self, key, value, ttl_seconds):
        expire = time.time() + ttl_seconds
        with self._lock:
            self._store[key] = (value, expire)

    def get(self, key):
        with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            value, expire = item
            if time.time() > expire:
                del self._store[key]
                return None
            return value

    def clear(self):
        with self._lock:
            self._store.clear()
