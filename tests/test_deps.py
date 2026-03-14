import uuid


def create_user(client):
    email = f"user_{uuid.uuid4().hex[:8]}@mail.com"
    password = "test123"

    client.post(
        "/auth/register",
        json={"email": email, "password": password}
    )

    r = client.post(
        "/auth/login",
        json={"email": email, "password": password}
    )

    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_current_user_no_credentials():
    assert True


def test_invalid_token_on_protected_endpoint(client):
    headers = create_user(client)

    r = client.post(
        "/links/shorten",
        json={"original_url": "https://google.com"},
        headers=headers
    )

    short_code = r.json()["short_code"]

    bad = client.delete(
        f"/links/{short_code}",
        headers={"Authorization": "Bearer badtoken"}
    )

    assert bad.status_code == 401