from typing import Any

import requests
from pydantic import HttpUrl


class APIBase:
    """
    A generic base class for working with HTTP-based APIs.
    """

    def __init__(
        self,
        base_url: HttpUrl,
        headers: dict[str, str | None] | None = None,
        timeout: int = 10,
    ):
        self.base_url = str(base_url).rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def send_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: dict[str, str | int | float | bool | None] | None = None,
        data: dict | str | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """
        Sends an HTTP request and returns the parsed JSON response.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        # Remove any parameters that are None
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                headers=request_headers,
                params=params,
                data=data,
                json=json,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            raise RuntimeError(
                f"HTTP error occurred: {http_err} - Response: {response.text}"
            )
        except requests.exceptions.RequestException as err:
            raise RuntimeError(f"Error during request to {url}: {err}")
        except ValueError:
            raise RuntimeError("Invalid JSON response")

    def close(self) -> None:
        self.session.close()
