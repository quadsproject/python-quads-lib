from json import JSONDecodeError
from typing import Optional
from typing import Union
from urllib.parse import urljoin

from requests import Session
from requests.adapters import HTTPAdapter
from requests.adapters import Retry
from requests.auth import HTTPBasicAuth

from quads_lib.exceptions import APIBadRequest
from quads_lib.exceptions import APIServerException


class QuadsBase:
    """
    Base class for the Quads API
    """

    def __init__(
        self,
        username: str,
        password: str,
        base_url: str,
        verify: Union[bool, str] = False,
    ):
        """
        Initialize QuadsBase.

        Args:
            username: Username for QUADS authentication
            password: Password for QUADS authentication
            base_url: Base URL for the QUADS API
            verify: Controls TLS certificate verification. Can be:
                - False: Disable certificate verification (default, for backward compatibility)
                - True: Enable verification using default CA bundle
                - str: Path to a custom CA bundle file
        """
        self.username = username
        self.password = password
        self.base_url = urljoin(base_url, "api/v3/")
        self.verify = verify
        self.session = Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.auth = HTTPBasicAuth(self.username, self.password)
        self.token = None
        self.headers = {}

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logout()
        self.session.close()

    def _make_request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        _response = self.session.request(
            method,
            urljoin(self.base_url, endpoint),
            json=data,
            verify=self.verify,
        )
        if _response.status_code == 500:
            raise APIServerException("Check the flask server logs")
        if _response.status_code == 400:
            try:
                response_json = _response.json()
            except JSONDecodeError as e:
                raise APIBadRequest("Failed to parse response") from e
            raise APIBadRequest(response_json.get("message"))
        return _response.json()

    # Base functions
    def get(self, endpoint: str) -> dict:
        _response = self._make_request("GET", endpoint)
        return _response

    def post(self, endpoint: str, data: Optional[dict] = None) -> dict:
        _response = self._make_request("POST", endpoint, data)
        return _response

    def patch(self, endpoint: str, data: Optional[dict] = None) -> dict:
        _response = self._make_request("PATCH", endpoint, data)
        return _response

    def delete(self, endpoint: str) -> dict:
        _response = self._make_request("DELETE", endpoint)
        return _response
