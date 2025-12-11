import os
import json
from datetime import datetime

import aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
CACHE_KEY = "cloudwatch:latest"

class Cache:
    def __init__(self):
        self.redis = None

    async def connect(self):
        self.redis = aioredis.from_url(REDIS_URL)

    async def set_latest(self, payload: dict):
        payload["updated_at"] = datetime.utcnow().isoformat()
        await self.redis.set(CACHE_KEY, json.dumps(payload))

    async def get_latest(self):
        val = await self.redis.get(CACHE_KEY)
        if not val:
            return None
        return json.loads(val)
