from app.main import app


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["message"] == "URL Shortener API is running"


def test_openapi(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200