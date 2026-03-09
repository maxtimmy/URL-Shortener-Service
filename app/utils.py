import random
import string
from datetime import datetime


def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def is_expired(expires_at: datetime | None) -> bool:
    return bool(expires_at and expires_at <= datetime.utcnow())