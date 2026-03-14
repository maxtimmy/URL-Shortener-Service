from app.utils import generate_short_code
from datetime import datetime, timedelta
from app.utils import is_expired

def test_generate_short_code_type():
    code = generate_short_code()
    assert isinstance(code, str)


def test_generate_short_code_length():
    code = generate_short_code()
    assert len(code) >= 5


def test_generate_short_code_unique():
    a = generate_short_code()
    b = generate_short_code()
    assert a != b

def test_is_expired_true():
    x = datetime.utcnow() - timedelta(minutes=1)
    assert is_expired(x) is True


def test_is_expired_false():
    x = datetime.utcnow() + timedelta(minutes=1)
    assert is_expired(x) is False


def test_is_expired_none():
    assert is_expired(None) is False