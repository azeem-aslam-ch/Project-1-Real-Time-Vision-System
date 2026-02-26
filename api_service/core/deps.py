import redis
import json
import logging
from fastapi import Header, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from config.config import config

logger = logging.getLogger(__name__)

API_KEY = config.api.get("api_key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="Could not validate credentials")

class RedisReader:
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url)

    def get_metrics(self):
        data = self.redis.get("vision:metrics")
        return json.loads(data) if data else {}

    def get_latest_events(self):
        events = self.redis.lrange("vision:events", 0, 9)
        return [json.loads(e) for e in events]

    def get_latest_frame(self):
        return self.redis.get("vision:latest_frame")

    def get_status(self):
        status = self.redis.get("vision:status")
        return status.decode() if status else "UNKNOWN"
