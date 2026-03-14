import redis
from app.config import settings


r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True) if settings.REDIS_URL else None


def get_cached_url(short_code: str):
    if not r:
        return None
    return r.get(f"link:{short_code}")


def set_cached_url(short_code: str, original_url: str, ttl: int = 3600):
    if not r:
        return
    r.setex(f"link:{short_code}", ttl, original_url)


def delete_cached_url(short_code: str):
    if not r:
        return
    r.delete(f"link:{short_code}")