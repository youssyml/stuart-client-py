import pytest
from stuart_client.StuartClient import Authentication, Environment
import time


class TestAuthentication:
    @pytest.fixture
    def get_new_auth(self, requests_mock):
        """
        Factory fixture to generate auth object for each test
        """

        def _get_new_auth(
            token: str = "new_token",
            created_at: float = time.time(),
            expires_in: float = 36000,
        ):
            env = Environment("SANDBOX")
            requests_mock.register_uri(
                "POST",
                env.base_url + "/oauth/token",
                status_code=200,
                json={
                    "access_token": token,
                    "created_at": created_at,
                    "expires_in": expires_in,
                },
            )
            auth = Authentication(env, "aaa", "bbb")
            auth.get_token()
            return auth

        return _get_new_auth

    def test_new_token(self, get_new_auth):
        """
        Tests if new token generation works properly
        """
        auth = get_new_auth()
        assert auth.get_token() == "new_token"

    def test_existing_token(self, requests_mock, get_new_auth):
        """
        Tests that existing token is returned if not expired
        """
        auth = get_new_auth(token="existing_token")
        requests_mock.register_uri(
            "POST",
            auth.environment.base_url + "/oauth/token",
            status_code=200,
            json={"access_token": "new_token"},
        )
        assert auth.get_token() == "existing_token"

    def test_token_expiration(self, requests_mock, get_new_auth):
        """
        Tests that new token is generated if current one is expired
        """
        auth = get_new_auth(
            token="existing_token", created_at=time.time() - 20, expires_in=10
        )
        requests_mock.register_uri(
            "POST",
            auth.environment.base_url + "/oauth/token",
            status_code=200,
            json={"access_token": "new_token"},
        )
        assert auth.get_token() == "new_token"
