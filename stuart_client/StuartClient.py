import requests
import time


class Environment:
    """
    Helper class to manage the chosen environment and url to use for requests
    """

    def __init__(self, env: str) -> None:
        if env == "PRODUCTION":
            self.base_url = "https://api.stuart.com"
        elif env == "SANDBOX":
            self.base_url = "https://api.sandbox.stuart.com"
        else:
            raise ValueError("Wrong environment, input PRODUCTION or SANDBOX")


class ApiResponse:
    """
    Helper class to manage the response of HTTP requests to the Stuart API
    and their success status depending on the status_code
    """

    def __init__(self, response: requests.Response) -> None:
        self.status_code = int(response.status_code)
        self.content = response.json()
        self.headers = response.headers

    def success(self) -> bool:
        """
        Returns a boolean. True if the request has succeeded and false otherwise.
        """
        return self.status_code >= 200 and self.status_code < 300


class Authentication:
    """
    Helper class to manage authentication (OAuth) to the stuart API.
    """

    def __init__(self, env: Environment, client_id: str, client_secret: str) -> None:
        self.environment = env
        self.access_token = None
        self.client_id = client_id
        self.client_secret = client_secret

    def request_access_token(self) -> dict:
        """
        Method to request the access_token to the /oath/token endpoint.
        Returns a dict with all token information (token, creation timestamp etc.)
        """
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
        """
        Get the access token to add to headers for requests to the stuart API.
        Only requests a new token if there is no current one or it has expired.
        """
        if not self.access_token:
            print("No token")
            self.access_token = self.request_access_token()
        elif self.token_expired():
            print("Token expired")
            self.access_token = self.request_access_token()

        return self.access_token.get("access_token")

    def token_expired(self) -> bool:
        """
        Helper method to check if the token has expired.
        Returns True if the token has expired, False otherwise.
        """
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
        Returns complete endpoint URL using the base URL
        """
        return self.auth.environment.base_url + resource

    def get_default_headers(self) -> dict:
        """
        Returns the default header (a dict) to use for requests
        """
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.get_token()}",
        }

    def get(self, resource, params={}) -> dict:
        """
        Method to use a GET endpoint from the Stuart API.
        Args
            resource: the endpoint (e.g /v2/jobs)
            params: a dict with all query parameters to pass to the endpoint
        Returns
            a json dict with the API response
        """
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

    def post(self, resource: str, body: str) -> dict:
        """
        Method to use a POST endpoint from the Stuart API.
        Args
            resource: the endpoint (e.g /v2/jobs)
            body: a str with the body of the request (use json.dumps() to create it)
        Returns
            a json dict with the API response
        """
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
