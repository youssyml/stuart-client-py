import pytest
from stuart_client.StuartClient import Authentication, Environment, StuartClient
import time


class TestClient:
    @pytest.fixture
    def auth(self, requests_mock):
        env = Environment("SANDBOX")
        requests_mock.register_uri(
            "POST",
            env.base_url + "/oauth/token",
            json={
                "access_token": "some_token",
                "created_at": time.time(),
                "expires_in": 36000,
            },
        )
        return Authentication(env, "aaa", "bbb")

    @pytest.mark.parametrize("method,status_code", [("GET", 200), ("POST", 204)])
    def test_success(self, requests_mock, auth, method, status_code):
        requests_mock.register_uri(
            method,
            auth.environment.base_url + "/success",
            status_code=status_code,
            json={"response": "success"},
        )
        client = StuartClient(auth)

        if method == "GET":
            assert client.get("/success").get("response") == "success"
        else:
            assert (
                client.post("/success", {"body": "body"}).get("response") == "success"
            )

    @pytest.mark.parametrize("method,status_code", [("GET", 301), ("POST", 404)])
    def test_failure(self, requests_mock, auth, method, status_code):
        requests_mock.register_uri(
            method,
            auth.environment.base_url + "/failure",
            status_code=status_code,
            json={"error_description": "Purposeful failure"},
        )

        with pytest.raises(Exception) as e:
            client = StuartClient(auth)
            if method == "GET":
                client.get("/failure")
            else:
                client.post("/failure", {"body": "body"})
