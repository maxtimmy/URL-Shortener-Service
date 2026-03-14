import uuid


def create_user_and_get_token(client):
    email = f"user_{uuid.uuid4().hex[:8]}@mail.com"
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

    return r.json()["access_token"]


def test_create_link(client):
    token = create_user_and_get_token(client)

    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "original_url": "https://google.com"
    }

    r = client.post("/links/shorten", json=data, headers=headers)

    assert r.status_code in [200, 201]

    body = r.json()

    assert "short_code" in body
    assert "short_url" in body


def test_create_link_with_alias(client):
    token = create_user_and_get_token(client)

    headers = {"Authorization": f"Bearer {token}"}

    alias = f"code{uuid.uuid4().hex[:6]}"

    r = client.post(
        "/links/shorten",
        json={
            "original_url": "https://example.com",
            "custom_alias": alias
        },
        headers=headers
    )

    assert r.status_code in [200, 201]
    assert r.json()["short_code"] == alias


def test_search_link(client):
    token = create_user_and_get_token(client)

    headers = {"Authorization": f"Bearer {token}"}

    url = "https://example.com"

    client.post(
        "/links/shorten",
        json={"original_url": url},
        headers=headers
    )

    r = client.get("/links/search", params={"original_url": url})

    assert r.status_code == 200
    assert "found" in r.json()


def test_link_stats(client):
    token = create_user_and_get_token(client)

    headers = {"Authorization": f"Bearer {token}"}

    create_resp = client.post(
        "/links/shorten",
        json={"original_url": "https://google.com"},
        headers=headers
    )

    short_code = create_resp.json()["short_code"]

    client.get(f"/{short_code}", follow_redirects=False)

    r = client.get(f"/links/{short_code}/stats")

    assert r.status_code == 200
    assert r.json()["short_code"] == short_code
    assert "click_count" in r.json()