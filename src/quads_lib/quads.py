from json import JSONDecodeError
from pathlib import Path
from typing import Optional
from urllib import parse as url_parse
from urllib.parse import urlencode
from urllib.parse import urljoin

from requests import Session
from requests.adapters import HTTPAdapter
from requests.adapters import Retry
from requests.auth import HTTPBasicAuth


class APIServerException(Exception):
    pass


class APIBadRequest(Exception):
    pass


class QuadsBase:
    """
    Base class for the Quads API
    """

    def __init__(self, username: str, password: str, base_url: str):
        self.username = username
        self.password = password
        self.base_url = base_url
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
            verify=False,
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


class QuadsApi(QuadsBase):
    """
    A python interface into the Quads API
    """

    # Auth
    def register(self) -> dict:
        json_response = self._make_request("POST", "register", {"email": self.username, "password": self.password})
        return json_response

    def login(self) -> dict:
        endpoint = urljoin(self.base_url, "login")
        _response = self.session.post(endpoint, auth=self.auth, verify=False)
        json_response = _response.json()
        if json_response.get("status_code") == 201:
            self.token = json_response.get("auth_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        return json_response

    def logout(self) -> dict:
        json_response = self._make_request("POST", "logout")
        if json_response.get("status_code") == 200:
            self.token = None
            self.session.headers.clear()
        return json_response

    # Hosts
    def get_hosts(self) -> dict:
        json_response = self.get("hosts")
        return json_response

    def get_host_models(self) -> dict:
        json_response = self.get("hosts?group_by=model")
        return json_response

    def filter_hosts(self, data: dict) -> dict:
        url_params = url_parse.urlencode(data)
        json_response = self.get(f"hosts?{url_params}")
        return json_response

    def filter_clouds(self, data: dict) -> dict:
        url_params = url_parse.urlencode(data)
        json_response = self.get(f"clouds?{url_params}")
        return json_response

    def filter_assignments(self, data: dict) -> dict:
        url_params = url_parse.urlencode(data)
        json_response = self.get(f"assignments?{url_params}")
        return json_response

    def get_host(self, hostname: str) -> dict:
        endpoint = Path("hosts") / hostname
        json_response = self.get(str(endpoint))
        return json_response

    def create_host(self, data: dict) -> dict:
        json_response = self.post("hosts", data)
        return json_response

    def update_host(self, hostname: str, data: dict) -> dict:
        endpoint = Path("hosts") / hostname
        json_response = self.patch(str(endpoint), data)
        return json_response

    def remove_host(self, hostname: str) -> dict:
        endpoint = Path("hosts") / hostname
        json_response = self.delete(str(endpoint))
        return json_response

    def is_available(self, hostname: str, data: dict) -> bool:
        url_params = url_parse.urlencode(data)
        endpoint = Path("available") / hostname
        json_response = self.get(f"{endpoint}?{url_params}")
        return True if "true" in json_response else False

    # Clouds
    def get_clouds(self) -> dict:
        json_response = self.get("clouds")
        return json_response

    def get_free_clouds(self) -> dict:
        json_response = self.get("clouds/free/")
        return json_response

    def get_cloud(self, cloud_name: str) -> dict:
        json_response = self.get(f"clouds?name={cloud_name}")
        return json_response

    def get_summary(self, data: dict) -> dict:
        url_params = url_parse.urlencode(data)
        endpoint = Path("clouds") / "summary"
        url = f"{endpoint}"
        if data:
            url = f"{endpoint}?{url_params}"
        json_response = self.get(url)
        return json_response

    def create_cloud(self, data: dict) -> dict:
        return self.post("clouds", data)

    def update_cloud(self, cloud_name: str, data: dict) -> dict:
        endpoint = Path("clouds") / cloud_name
        json_response = self.patch(str(endpoint), data)
        return json_response

    def remove_cloud(self, cloud_name: str) -> dict:
        endpoint = Path("clouds") / cloud_name
        json_response = self.delete(str(endpoint))
        return json_response

    # Schedules
    def get_schedules(self, data: Optional[dict] = None) -> dict:
        if data is None:
            data = {}
        url_params = url_parse.urlencode(data)
        url = "schedules"
        if url_params:
            url = f"{url}?{url_params}"
        json_response = self.get(url)
        return json_response

    def get_current_schedules(self, data: Optional[dict] = None) -> dict:
        if data is None:
            data = {}
        endpoint = Path("schedules") / "current"
        url = f"{endpoint}"
        if data:
            url_params = url_parse.urlencode(data)
            url = f"{endpoint}?{url_params}"
        json_response = self.get(url)
        return json_response

    def get_schedule(self, schedule_id: int) -> dict:
        endpoint = Path("schedules") / str(schedule_id)
        json_response = self.get(str(endpoint))
        return json_response

    def get_future_schedules(self, data: Optional[dict] = None) -> dict:
        if data is None:
            data = {}
        url_params = url_parse.urlencode(data)
        endpoint = Path("schedules") / "future"
        url = f"{endpoint}"
        if data:
            url = f"{endpoint}?{url_params}"
        json_response = self.get(url)
        return json_response

    def update_schedule(self, schedule_id: int, data: dict) -> dict:
        endpoint = Path("schedules") / str(schedule_id)
        json_response = self.patch(str(endpoint), data)
        return json_response

    def remove_schedule(self, schedule_id: int) -> dict:
        endpoint = Path("schedules") / str(schedule_id)
        json_response = self.delete(str(endpoint))
        return json_response

    def create_schedule(self, data: dict) -> dict:
        return self.post("schedules", data)

    # Available
    def get_available(self) -> dict:
        json_response = self.get("available")
        return json_response

    def filter_available(self, data: dict) -> dict:
        json_response = self.get(f"available?{urlencode(data)}")
        return json_response

    # Assignments
    def create_assignment(self, data: dict) -> dict:
        return self.post("assignments", data)

    def create_self_assignment(self, data: dict) -> dict:
        endpoint = Path("assignments") / "self"
        return self.post(str(endpoint), data)

    def update_assignment(self, assignment_id: int, data: dict) -> dict:
        endpoint = Path("assignments") / str(assignment_id)
        json_response = self.patch(str(endpoint), data)
        return json_response

    def update_notification(self, notification_id: int, data: dict) -> dict:
        endpoint = Path("notifications") / str(notification_id)
        json_response = self.patch(str(endpoint), data)
        return json_response

    def get_active_cloud_assignment(self, cloud_name: str) -> dict:
        endpoint = Path("assignments") / "active" / cloud_name
        json_response = self.get(str(endpoint))
        return json_response

    def get_active_assignments(self) -> dict:
        json_response = self.get("assignments/active")
        return json_response

    def terminate_assignment(self, assignment_id: int) -> dict:
        endpoint = Path("assignments") / "terminate" / str(assignment_id)
        json_response = self.post(str(endpoint))
        return json_response

    # Interfaces
    def get_host_interface(self, hostname: str) -> dict:
        endpoint = Path("hosts") / hostname / "interfaces"
        json_response = self.get(str(endpoint))
        return json_response

    def get_interfaces(self) -> dict:
        json_response = self.get("interfaces")
        return json_response

    def update_interface(self, hostname: str, data: dict) -> dict:
        endpoint = Path("interfaces") / hostname
        json_response = self.patch(str(endpoint), data)
        return json_response

    def remove_interface(self, hostname: str, if_name: str) -> dict:
        endpoint = Path("interfaces") / hostname / if_name
        json_response = self.delete(str(endpoint))
        return json_response

    def create_interface(self, hostname: str, data: dict) -> dict:
        endpoint = Path("interfaces") / hostname
        json_response = self.post(str(endpoint), data)
        return json_response

    # Memory
    def create_memory(self, hostname: str, data: dict) -> dict:
        endpoint = Path("memory") / hostname
        json_response = self.post(str(endpoint), data)
        return json_response

    def remove_memory(self, memory_id: int) -> dict:
        endpoint = Path("memory") / memory_id
        json_response = self.delete(str(endpoint))
        return json_response

    # Disks
    def create_disk(self, hostname: str, data: dict) -> dict:
        endpoint = Path("disks") / hostname
        json_response = self.post(str(endpoint), data)
        return json_response

    def update_disk(self, hostname: str, data: dict) -> dict:
        endpoint = Path("disks") / hostname
        json_response = self.patch(str(endpoint), data)
        return json_response

    def remove_disk(self, hostname: str, disk_id: int) -> dict:
        endpoint = Path("disks") / hostname / disk_id
        json_response = self.delete(str(endpoint))
        return json_response

    # Processor
    def create_processor(self, hostname: str, data: dict) -> dict:
        endpoint = Path("processors") / hostname
        json_response = self.post(str(endpoint), data)
        return json_response

    def remove_processor(self, processor_id: int) -> dict:
        endpoint = Path("processors") / processor_id
        json_response = self.delete(str(endpoint))
        return json_response

    # Vlans
    def get_vlans(self) -> dict:
        json_response = self.get("vlans")
        return json_response

    def get_vlan(self, vlan_id: int) -> dict:
        endpoint = Path("vlans") / str(vlan_id)
        json_response = self.get(str(endpoint))
        return json_response

    def get_free_vlans(self) -> dict:
        endpoint = Path("vlans") / "free"
        json_response = self.get(str(endpoint))
        return json_response

    def update_vlan(self, vlan_id: int, data: dict) -> dict:
        endpoint = Path("vlans") / str(vlan_id)
        json_response = self.patch(str(endpoint), data)
        return json_response

    def create_vlan(self, data: dict) -> dict:
        return self.post("vlans", data)

    # Moves
    def get_moves(self, date: Optional[str] = None) -> dict:
        url = "moves"
        if date:
            url_params = url_parse.urlencode({"date": date})
            url = f"moves?{url_params}"
        json_response = self.get(url)
        return json_response

    def get_version(self) -> dict:
        json_response = self.get("version")
        return json_response
