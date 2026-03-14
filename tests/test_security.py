from app.security import hash_password, verify_password, create_access_token, decode_token


def test_password_hash_and_verify():
    p = "test123"
    h = hash_password(p)

    assert h != p
    assert verify_password(p, h) is True
    assert verify_password("wrongpass", h) is False


def test_create_and_decode_token():
    t = create_access_token({"sub": "1"})
    data = decode_token(t)

    assert data is not None
    assert data["sub"] == "1"


def test_decode_invalid_token():
    data = decode_token("bad.token.value")
    assert data is None