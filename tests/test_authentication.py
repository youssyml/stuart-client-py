import pytest
from stuart_client.StuartClient import Authentication, Environment
import time


class TestAuthentication:
    def test_new_token(self, requests_mock):
        env = Environment("SANDBOX")
        requests_mock.register_uri(
            "POST",
            env.base_url + "/oauth/token",
            status_code=200,
            json={"access_token": "new_token"},
        )
        auth = Authentication(env, "aaa", "bbb")
        assert auth.get_token() == "new_token"

    def test_existing_token(self, requests_mock):
        env = Environment("SANDBOX")
        requests_mock.register_uri(
            "POST",
            env.base_url + "/oauth/token",
            status_code=200,
            json={
                "access_token": "existing_token",
                "created_at": time.time(),
                "expires_in": 36000,
            },
        )
        auth = Authentication(env, "aaa", "bbb")
        auth.get_token()
        requests_mock.register_uri(
            "POST",
            env.base_url + "/oauth/token",
            status_code=200,
            json={"access_token": "new_token"},
        )
        assert auth.get_token() == "existing_token"

    def test_token_expiration(self, requests_mock):
        env = Environment("SANDBOX")
        requests_mock.register_uri(
            "POST",
            env.base_url + "/oauth/token",
            status_code=200,
            json={
                "access_token": "existing_token",
                "created_at": time.time() - 20,
                "expires_in": 10,
            },
        )
        auth = Authentication(env, "aaa", "bbb")
        auth.get_token()
        requests_mock.register_uri(
            "POST",
            env.base_url + "/oauth/token",
            status_code=200,
            json={"access_token": "new_token"},
        )
        assert auth.get_token() == "new_token"
