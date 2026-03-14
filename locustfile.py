from locust import HttpUser, task, between
import random
import string


def rnd(n=8):
    return "".join(random.choice(string.ascii_lowercase) for _ in range(n))


class ShortenerUser(HttpUser):
    wait_time = between(1, 2)

    @task(2)
    def create_link(self):
        alias = rnd()
        self.client.post(
            "/links/shorten",
            json={
                "original_url": "https://example.com",
                "custom_alias": alias
            }
        )

    @task(1)
    def search_link(self):
        self.client.get(
            "/links/search",
            params={"original_url": "https://example.com"}
        )