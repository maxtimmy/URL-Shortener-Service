import uuid


def test_register_user(client):
    data = {
        "email": f"test_{uuid.uuid4().hex[:8]}@mail.com",
        "password": "test123"
    }

    r = client.post("/auth/register", json=data)

    assert r.status_code in [200, 201]
    assert "access_token" in r.json()


def test_login_user(client):
    email = f"test_{uuid.uuid4().hex[:8]}@mail.com"
    password = "test123"

    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password
        }
    )

    r = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert r.status_code == 200
    assert "access_token" in r.json()