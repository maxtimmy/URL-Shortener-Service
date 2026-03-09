import redis
from app.config import settings


r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_cached_url(short_code: str):
    return r.get(f"link:{short_code}")


def set_cached_url(short_code: str, original_url: str, ttl: int = 3600):
    r.setex(f"link:{short_code}", ttl, original_url)


def delete_cached_url(short_code: str):
    r.delete(f"link:{short_code}")