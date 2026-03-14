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


def test_create_duplicate_alias(client):
    headers = create_user(client)
    alias = f"alias{uuid.uuid4().hex[:6]}"

    r1 = client.post(
        "/links/shorten",
        json={"original_url": "https://google.com", "custom_alias": alias},
        headers=headers
    )
    assert r1.status_code in [200, 201]

    r2 = client.post(
        "/links/shorten",
        json={"original_url": "https://example.com", "custom_alias": alias},
        headers=headers
    )
    assert r2.status_code == 400


def test_stats_not_found(client):
    r = client.get("/links/notfound123/stats")
    assert r.status_code == 404


def test_redirect_not_found(client):
    r = client.get("/no_such_code_123", follow_redirects=False)
    assert r.status_code == 404


def test_delete_without_auth(client):
    headers = create_user(client)

    r = client.post(
        "/links/shorten",
        json={"original_url": "https://google.com"},
        headers=headers
    )

    short_code = r.json()["short_code"]

    d = client.delete(f"/links/{short_code}")
    assert d.status_code == 401


def test_update_without_auth(client):
    headers = create_user(client)

    r = client.post(
        "/links/shorten",
        json={"original_url": "https://google.com"},
        headers=headers
    )

    short_code = r.json()["short_code"]

    u = client.put(
        f"/links/{short_code}",
        json={"original_url": "https://youtube.com"}
    )
    assert u.status_code == 401


def test_delete_own_link(client):
    headers = create_user(client)

    r = client.post(
        "/links/shorten",
        json={"original_url": "https://google.com"},
        headers=headers
    )

    short_code = r.json()["short_code"]

    d = client.delete(f"/links/{short_code}", headers=headers)
    assert d.status_code == 200

    s = client.get(f"/links/{short_code}/stats")
    assert s.status_code == 404


def test_update_own_link(client):
    headers = create_user(client)

    r = client.post(
        "/links/shorten",
        json={"original_url": "https://google.com"},
        headers=headers
    )

    short_code = r.json()["short_code"]

    u = client.put(
        f"/links/{short_code}",
        json={"original_url": "https://youtube.com"},
        headers=headers
    )

    assert u.status_code == 200
    assert u.json()["original_url"].startswith("https://youtube.com")

def test_search_not_found(client):
    r = client.get("/links/search", params={"original_url": "https://not-found-example.com"})
    assert r.status_code == 200
    assert r.json()["found"] is False

def test_update_short_code_own_link(client):
    headers = create_user(client)

    r = client.post(
        "/links/shorten",
        json={"original_url": "https://google.com"},
        headers=headers
    )

    short_code = r.json()["short_code"]

    u = client.put(
        f"/links/{short_code}",
        json={"new_short_code": "updatedcode123"},
        headers=headers
    )

    assert u.status_code == 200
    assert u.json()["short_code"] == "updatedcode123"


def test_update_duplicate_short_code(client):
    headers = create_user(client)

    r1 = client.post(
        "/links/shorten",
        json={"original_url": "https://google.com", "custom_alias": "alias111"},
        headers=headers
    )
    assert r1.status_code in [200, 201]

    r2 = client.post(
        "/links/shorten",
        json={"original_url": "https://example.com"},
        headers=headers
    )
    assert r2.status_code in [200, 201]

    short_code = r2.json()["short_code"]

    u = client.put(
        f"/links/{short_code}",
        json={"new_short_code": "alias111"},
        headers=headers
    )

    assert u.status_code == 400

def test_expired_history(client):
    r = client.get("/links/expired/history")
    assert r.status_code == 200

def test_delete_foreign_link(client):
    headers1 = create_user(client)
    headers2 = create_user(client)

    r = client.post(
        "/links/shorten",
        json={"original_url": "https://google.com"},
        headers=headers1
    )

    short_code = r.json()["short_code"]

    d = client.delete(f"/links/{short_code}", headers=headers2)
    assert d.status_code == 403


def test_update_foreign_link(client):
    headers1 = create_user(client)
    headers2 = create_user(client)

    r = client.post(
        "/links/shorten",
        json={"original_url": "https://google.com"},
        headers=headers1
    )

    short_code = r.json()["short_code"]

    u = client.put(
        f"/links/{short_code}",
        json={"original_url": "https://youtube.com"},
        headers=headers2
    )

    assert u.status_code == 403