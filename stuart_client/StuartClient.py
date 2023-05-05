import requests
import time


class Environment:
    """
    Helper class to return the right base_url for API requests
    """

    def __init__(self, env: str) -> None:
        if env == "PRODUCTION":
            self.base_url = "https://api.stuart.com"
        elif env == "SANDBOX":
            self.base_url = "https://api.sandbox.stuart.com"
        else:
            raise ValueError("Wrong environment, input PRODUCTION or SANDBOX")


class ApiResponse:
    def __init__(self, response: requests.Response) -> None:
        self.status_code = int(response.status_code)
        self.content = response.json()
        self.headers = response.headers

    def success(self) -> bool:
        return self.status_code >= 200 and self.status_code < 300


class Authentication:
    def __init__(self, env: Environment, client_id: str, client_secret: str) -> None:
        self.environment = env
        self.access_token = None
        self.client_id = client_id
        self.client_secret = client_secret

    def request_access_token(self) -> dict:
        response = requests.post(
            url=f"{self.environment.base_url}/oauth/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
                "scope": "api",
            },
        )
        api_response = ApiResponse(response)

        # catching errors
        if not api_response.success():
            raise Exception(
                f"Stuart token API returned error {api_response.content.get('error_description')}"
            )
        else:
            return api_response.content

    def get_token(self) -> str:
        # checks if access token exists or has expired
        # if so, requests another one
        if not self.access_token:
            print("No token")
            self.access_token = self.request_access_token()
        elif self.token_expired():
            print("Token expired")
            self.access_token = self.request_access_token()

        return self.access_token.get("access_token")

    def token_expired(self) -> bool:
        current_timestamp = time.time()
        return (
            float(self.access_token.get("created_at"))
            + float(self.access_token.get("expires_in"))
            <= current_timestamp
        )


class StuartClient:
    def __init__(self, auth: Authentication) -> None:
        self.auth = auth

    def url(self, resource: str) -> str:
        """
        Returns complete endpoint
        """
        return self.auth.environment.base_url + resource

    def get_default_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.get_token()}",
        }

    def get(self, resource, params={}):
        response = requests.get(
            url=self.url(resource),
            headers=self.get_default_headers(),
            params=params,
        )

        api_response = ApiResponse(response)

        if not api_response.success():
            raise Exception(
                f"Get request failed with error {api_response.content.get('error')}: {api_response.content.get('message')}"
            )

        return api_response.content

    def post(self, resource, body):
        response = requests.post(
            url=self.url(resource),
            headers=self.get_default_headers(),
            data=body,
        )
        api_response = ApiResponse(response)

        if not api_response.success():
            raise Exception(
                f"Post request failed with error {api_response.content.get('error')}: {api_response.content.get('message')}"
            )

        return api_response.content
