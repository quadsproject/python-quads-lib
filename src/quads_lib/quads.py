from json import JSONDecodeError
from pathlib import Path
from typing import Optional
from urllib import parse as url_parse
from urllib.parse import urlencode, urljoin

from requests import Response
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

    # Base functions
    def get(self, endpoint: str) -> dict:
        _response = self.session.get(urljoin(self.base_url, endpoint), verify=False, auth=self.auth)
        if _response.status_code == 500:
            raise APIServerException("Check the flask server logs")
        if _response.status_code == 400:
            try:
                response_json = _response.json()
            except JSONDecodeError as e:
                raise APIBadRequest("Failed to parse response") from e
            raise APIBadRequest(response_json.get("message"))
        return _response.json()

    def post(self, endpoint, data) -> Response:
        _response = self.session.post(
            urljoin(self.base_url, endpoint),
            json=data,
            verify=False,
            auth=self.auth,
        )
        if _response.status_code == 500:
            raise APIServerException("Check the flask server logs")
        if _response.status_code == 400:
            response_json = _response.json()
            raise APIBadRequest(response_json.get("message"))
        return _response

    def patch(self, endpoint, data) -> Response:
        _response = self.session.patch(
            urljoin(self.base_url, endpoint),
            json=data,
            verify=False,
            auth=self.auth,
        )
        if _response.status_code == 500:
            raise APIServerException("Check the flask server logs")
        if _response.status_code == 400:
            response_json = _response.json()
            raise APIBadRequest(response_json.get("message"))
        return _response

    def delete(self, endpoint) -> Response:
        _response = self.session.delete(urljoin(self.base_url, endpoint), verify=False, auth=self.auth)
        if _response.status_code == 500:
            raise APIServerException("Check the flask server logs")
        if _response.status_code == 400:
            response_json = _response.json()
            raise APIBadRequest(response_json.get("message"))
        return _response


class QuadsApi(QuadsBase):
    """
    A python interface into the Quads API
    """

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

    def create_host(self, data: dict) -> Response:
        response = self.post("hosts", data)
        return response

    def update_host(self, hostname: str, data: dict) -> Response:
        endpoint = Path("hosts") / hostname
        response = self.patch(str(endpoint), data)
        return response

    def remove_host(self, hostname: str) -> Response:
        endpoint = Path("hosts") / hostname
        response = self.delete(str(endpoint))
        return response

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

    def insert_cloud(self, data: dict) -> Response:
        return self.post("clouds", data)

    def update_cloud(self, cloud_name: str, data: dict) -> Response:
        endpoint = Path("clouds") / cloud_name
        response = self.patch(str(endpoint), data)
        return response

    def remove_cloud(self, cloud_name: str) -> Response:
        endpoint = Path("clouds") / cloud_name
        response = self.delete(str(endpoint))
        return response

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

    def update_schedule(self, schedule_id: int, data: dict) -> Response:
        endpoint = Path("schedules") / str(schedule_id)
        response = self.patch(str(endpoint), data)
        return response

    def remove_schedule(self, schedule_id: int) -> Response:
        endpoint = Path("schedules") / str(schedule_id)
        response = self.delete(str(endpoint))
        return response

    def insert_schedule(self, data: dict) -> Response:
        return self.post("schedules", data)

    # Available
    def get_available(self) -> dict:
        json_response = self.get("available")
        return json_response

    def filter_available(self, data: dict) -> dict:
        json_response = self.get(f"available?{urlencode(data)}")
        return json_response

    # Assignments
    def insert_assignment(self, data: dict) -> Response:
        return self.post("assignments", data)

    def update_assignment(self, assignment_id: int, data: dict) -> Response:
        endpoint = Path("assignments") / str(assignment_id)
        response = self.patch(str(endpoint), data)
        return response

    def update_notification(self, notification_id: int, data: dict) -> Response:
        endpoint = Path("notifications") / str(notification_id)
        response = self.patch(str(endpoint), data)
        return response

    def get_active_cloud_assignment(self, cloud_name: str) -> dict:
        endpoint = Path("assignments") / "active" / cloud_name
        json_response = self.get(str(endpoint))
        return json_response

    def get_active_assignments(self) -> dict:
        json_response = self.get("assignments/active")
        return json_response

    # Interfaces
    def get_host_interface(self, hostname: str) -> dict:
        endpoint = Path("hosts") / hostname / "interfaces"
        json_response = self.get(str(endpoint))
        return json_response

    def get_interfaces(self) -> dict:
        json_response = self.get("interfaces")
        return json_response

    def update_interface(self, hostname: str, data: dict) -> Response:
        endpoint = Path("interfaces") / hostname
        response = self.patch(str(endpoint), data)
        return response

    def remove_interface(self, hostname: str, if_name: str) -> Response:
        endpoint = Path("interfaces") / hostname / if_name
        response = self.delete(str(endpoint))
        return response

    def create_interface(self, hostname: str, data: dict) -> Response:
        endpoint = Path("interfaces") / hostname
        response = self.post(str(endpoint), data)
        return response

    # Memory
    def create_memory(self, hostname: str, data: dict) -> Response:
        endpoint = Path("memory") / hostname
        response = self.post(str(endpoint), data)
        return response


    def remove_memory(self, memory_id: int) -> Response:
        endpoint = Path("memory") / memory_id
        response = self.delete(str(endpoint))
        return response

    # Disks
    def create_disk(self, hostname: str, data: dict) -> Response:
        endpoint = Path("disks") / hostname
        response = self.post(str(endpoint), data)
        return response

    def update_disk(self, hostname: str, data: dict) -> Response:
        endpoint = Path("disks") / hostname
        response = self.patch(str(endpoint), data)
        return response

    def remove_disk(self, hostname: str, disk_id: int) -> Response:
        endpoint = Path("disks") / hostname / disk_id
        response = self.delete(str(endpoint))
        return response

    # Processor
    def create_processor(self, hostname: str, data: dict) -> Response:
        endpoint = Path("processors") / hostname
        response = self.post(str(endpoint), data)
        return response

    def remove_processor(self, processor_id: int) -> Response:
        endpoint = Path("processors") / processor_id
        response = self.delete(str(endpoint))
        return response

    # Vlans
    def get_vlans(self) -> dict:
        json_response = self.get("vlans")
        return json_response

    def get_vlan(self, vlan_id: int) -> dict:
        endpoint = Path("vlans") / str(vlan_id)
        json_response = self.get(str(endpoint))
        return json_response

    def update_vlan(self, vlan_id: int, data: dict) -> Response:
        endpoint = Path("vlans") / str(vlan_id)
        response = self.patch(str(endpoint), data)
        return response

    def create_vlan(self, data: dict) -> Response:
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
