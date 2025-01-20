import os
from json import JSONDecodeError
from urllib import parse as url_parse
from urllib.parse import urlencode

from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry
from requests.auth import HTTPBasicAuth


class APIServerException(Exception):
    pass


class APIBadRequest(Exception):
    pass


class QuadsBase:
    """
    Base class for the Quads API
    """

    def __init__(self, config):
        self.config = config
        self.base_url = config.API_URL
        self.session = Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.auth = HTTPBasicAuth(self.config.get("quads_api_username"), self.config.get("quads_api_password"))

    # Base functions
    def get(self, endpoint: str) -> dict:
        _response = self.session.get(os.path.join(self.base_url, endpoint), verify=False, auth=self.auth)
        if _response.status_code == 500:
            raise APIServerException("Check the flask server logs")
        if _response.status_code == 400:
            try:
                response_json = _response.json()
            except JSONDecodeError:
                raise APIBadRequest("Failed to parse response")
            raise APIBadRequest(response_json.get("message"))
        return _response.json()

    def post(self, endpoint, data) -> Response:
        _response = self.session.post(
            os.path.join(self.base_url, endpoint),
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
            os.path.join(self.base_url, endpoint),
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
        _response = self.session.delete(os.path.join(self.base_url, endpoint), verify=False, auth=self.auth)
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

    def filter_hosts(self, data) -> dict:
        url_params = url_parse.urlencode(data)
        json_response = self.get(f"hosts?{url_params}")
        return json_response

    def filter_clouds(self, data) -> dict:
        url_params = url_parse.urlencode(data)
        json_response = self.get(f"clouds?{url_params}")
        return json_response

    def filter_assignments(self, data) -> dict:
        url_params = url_parse.urlencode(data)
        json_response = self.get(f"assignments?{url_params}")
        return json_response

    def get_host(self, hostname) -> dict:
        json_response = self.get(os.path.join("hosts", hostname))
        return json_response

    def create_host(self, data) -> Response:
        response = self.post(os.path.join("hosts"), data)
        return response

    def update_host(self, hostname, data) -> Response:
        return self.patch(os.path.join("hosts", hostname), data)

    def remove_host(self, hostname) -> Response:
        return self.delete(os.path.join("hosts", hostname))

    def is_available(self, hostname, data) -> bool:
        url_params = url_parse.urlencode(data)
        uri = os.path.join("available", hostname)
        json_response = self.get(f"{uri}?{url_params}")
        return True if "true" in json_response else False

    # Clouds
    def get_clouds(self) -> dict:
        json_response = self.get("clouds")
        return json_response

    def get_free_clouds(self) -> dict:
        json_response = self.get("clouds/free/")
        return json_response

    def get_cloud(self, cloud_name) -> dict:
        json_response = self.get(f"clouds?name={cloud_name}")
        return json_response

    def get_summary(self, data: dict) -> dict:
        url_params = url_parse.urlencode(data)
        endpoint = os.path.join("clouds", "summary")
        url = f"{endpoint}"
        if data:
            url = f"{endpoint}?{url_params}"
        json_response = self.get(url)
        return json_response

    def insert_cloud(self, data) -> Response:
        return self.post("clouds", data)

    def update_cloud(self, cloud_name, data) -> Response:
        return self.patch(os.path.join("clouds", cloud_name), data)

    def remove_cloud(self, cloud_name) -> Response:
        return self.delete(os.path.join("clouds", cloud_name))

    # Schedules
    def get_schedules(self, data: dict = None) -> dict:
        if data is None:
            data = {}
        url_params = url_parse.urlencode(data)
        url = "schedules"
        if url_params:
            url = f"{url}?{url_params}"
        json_response = self.get(url)
        return json_response

    def get_current_schedules(self, data: dict = None) -> dict:
        if data is None:
            data = {}
        endpoint = os.path.join("schedules", "current")
        url = f"{endpoint}"
        if data:
            url_params = url_parse.urlencode(data)
            url = f"{endpoint}?{url_params}"
        json_response = self.get(url)
        return json_response

    def get_schedule(self, schedule_id: int) -> dict:
        url = os.path.join("schedules", str(schedule_id))
        json_response = self.get(url)
        return json_response

    def get_future_schedules(self, data: dict = None) -> dict:
        if data is None:
            data = {}
        url_params = url_parse.urlencode(data)
        endpoint = os.path.join("schedules", "future")
        url = f"{endpoint}"
        if data:
            url = f"{endpoint}?{url_params}"
        json_response = self.get(url)
        return json_response

    def update_schedule(self, schedule_id, data) -> Response:
        return self.patch(os.path.join("schedules", str(schedule_id)), data)

    def remove_schedule(self, schedule_id) -> Response:
        return self.delete(os.path.join("schedules", str(schedule_id)))

    def insert_schedule(self, data) -> Response:
        return self.post("schedules", data)

    # Available
    def get_available(self) -> dict:
        json_response = self.get("available")
        return json_response

    def filter_available(self, data) -> dict:
        json_response = self.get(f"available?{urlencode(data)}")
        return json_response

    # Assignments
    def insert_assignment(self, data) -> Response:
        return self.post("assignments", data)

    def update_assignment(self, assignment_id, data) -> Response:
        return self.patch(os.path.join("assignments", str(assignment_id)), data)

    def update_notification(self, notification_id, data) -> Response:
        return self.patch(os.path.join("notifications", str(notification_id)), data)

    def get_active_cloud_assignment(self, cloud_name) -> dict:
        json_response = self.get(os.path.join("assignments/active", cloud_name))
        return json_response

    def get_active_assignments(self) -> dict:
        json_response = self.get("assignments/active")
        return json_response

    # Interfaces
    def get_host_interface(self, hostname) -> dict:
        json_response = self.get(os.path.join("hosts", hostname, "interfaces"))
        return json_response

    def get_interfaces(self) -> dict:
        json_response = self.get("interfaces")
        return json_response

    def update_interface(self, hostname, data) -> Response:
        return self.patch(os.path.join("interfaces", hostname), data)

    def remove_interface(self, hostname, if_name) -> Response:
        return self.delete(os.path.join("interfaces", hostname, if_name))

    def create_interface(self, hostname, data) -> Response:
        return self.post(os.path.join("interfaces", hostname), data)

    # Memory
    def create_memory(self, hostname, data) -> Response:
        return self.post(os.path.join("memory", hostname), data)

    def remove_memory(self, memory_id) -> Response  :
        return self.delete(os.path.join("memory", memory_id))

    # Disks
    def create_disk(self, hostname, data) -> Response:
        return self.post(os.path.join("disks", hostname), data)

    def update_disk(self, hostname, data) -> Response:
        return self.patch(os.path.join("disks", hostname), data)
    
    def remove_disk(self, hostname, disk_id) -> Response:
        return self.delete(os.path.join("disks", hostname, disk_id))

    # Processor
    def create_processor(self, hostname, data) -> Response:
        return self.post(os.path.join("processors", hostname), data)

    def remove_processor(self, processor_id) -> Response:
        return self.delete(os.path.join("processors", processor_id))

    # Vlans
    def get_vlans(self) -> dict:
        json_response = self.get("vlans")
        return json_response

    def get_vlan(self, vlan_id) -> dict:
        json_response = self.get(os.path.join("vlans", str(vlan_id)))
        return json_response

    def update_vlan(self, vlan_id, data) -> Response:
        return self.patch(os.path.join("vlans", str(vlan_id)), data)

    def create_vlan(self, data) -> Response:
        return self.post("vlans", data)

    # Moves
    def get_moves(self, date=None) -> dict:
        url = "moves"
        if date:
            url_params = url_parse.urlencode({"date": date})
            url = f"moves?{url_params}"
        json_response = self.get(url)
        return json_response

    def get_version(self) -> dict:
        json_response = self.get("version")
        return json_response