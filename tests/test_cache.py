from app.cache import get_cached_url, set_cached_url, delete_cached_url


def test_cache_functions_without_redis():
    k = "abc123"
    v = "https://example.com"

    set_cached_url(k, v, ttl=10)

    x = get_cached_url(k)

    assert x in [None, v]

    delete_cached_url(k)

    y = get_cached_url(k)

    assert y is None