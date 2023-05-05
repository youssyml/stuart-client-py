import pytest
from stuart_client.StuartClient import Environment


class TestEnvironment:
    def test_sandbox(self):
        env = Environment("SANDBOX")
        assert env.base_url == "https://api.sandbox.stuart.com"

    def test_production(self):
        env = Environment("SANDBOX")
        assert env.base_url == "https://api.sandbox.stuart.com"

    def test_wrong_value(self):
        with pytest.raises(ValueError) as e:
            Environment("TOTO")
