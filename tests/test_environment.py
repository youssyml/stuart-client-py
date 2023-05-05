import pytest
from stuart_client.StuartClient import Environment


class TestEnvironment:
    def test_sandbox(self):
        """
        Test that the sandbox env has the right base url
        """
        env = Environment("SANDBOX")
        assert env.base_url == "https://api.sandbox.stuart.com"

    def test_production(self):
        """
        Test that the production env has the right base url
        """
        env = Environment("PRODUCTION")
        assert env.base_url == "https://api.stuart.com"

    def test_wrong_value(self):
        """
        Test that any other environment value raises an error
        """
        with pytest.raises(ValueError) as e:
            Environment("TOTO")
