from pathlib import Path
from typing import Optional
from urllib import parse as url_parse
from urllib.parse import urlencode
from urllib.parse import urljoin

from quads_lib.base import QuadsBase
from quads_lib.decorators import returns


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
        _response = self.session.post(endpoint, auth=self.auth, verify=self.verify)
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
    @returns("List[Host]")
    def get_hosts(self) -> dict:
        json_response = self.get("hosts")
        return json_response

    def get_host_models(self) -> dict:
        json_response = self.get("hosts?group_by=model")
        return json_response

    @returns("List[Host]")
    def filter_hosts(self, data: dict) -> dict:
        url_params = url_parse.urlencode(data)
        json_response = self.get(f"hosts?{url_params}")
        return json_response

    @returns("List[Cloud]")
    def filter_clouds(self, data: dict) -> dict:
        url_params = url_parse.urlencode(data)
        json_response = self.get(f"clouds?{url_params}")
        return json_response

    @returns("List[Assignment]")
    def filter_assignments(self, data: dict) -> dict:
        url_params = url_parse.urlencode(data)
        json_response = self.get(f"assignments?{url_params}")
        return json_response

    @returns("Host")
    def get_host(self, hostname: str) -> dict:
        endpoint = Path("hosts") / hostname
        json_response = self.get(str(endpoint))
        return json_response

    @returns("Host")
    def create_host(self, data: dict) -> dict:
        json_response = self.post("hosts", data)
        return json_response

    @returns("Host")
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
    @returns("List[Cloud]")
    def get_clouds(self) -> dict:
        json_response = self.get("clouds")
        return json_response

    @returns("List[Cloud]")
    def get_free_clouds(self) -> dict:
        json_response = self.get("clouds/free/")
        return json_response

    @returns("Cloud")
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

    @returns("Cloud")
    def create_cloud(self, data: dict) -> dict:
        return self.post("clouds", data)

    @returns("Cloud")
    def update_cloud(self, cloud_name: str, data: dict) -> dict:
        endpoint = Path("clouds") / cloud_name
        json_response = self.patch(str(endpoint), data)
        return json_response

    def remove_cloud(self, cloud_name: str) -> dict:
        endpoint = Path("clouds") / cloud_name
        json_response = self.delete(str(endpoint))
        return json_response

    # Schedules
    @returns("List[Schedule]")
    def get_schedules(self, data: Optional[dict] = None) -> dict:
        if data is None:
            data = {}
        url_params = url_parse.urlencode(data)
        url = "schedules"
        if url_params:
            url = f"{url}?{url_params}"
        json_response = self.get(url)
        return json_response

    @returns("List[Schedule]")
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

    @returns("Schedule")
    def get_schedule(self, schedule_id: int) -> dict:
        endpoint = Path("schedules") / str(schedule_id)
        json_response = self.get(str(endpoint))
        return json_response

    @returns("List[Schedule]")
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

    @returns("Schedule")
    def update_schedule(self, schedule_id: int, data: dict) -> dict:
        endpoint = Path("schedules") / str(schedule_id)
        json_response = self.patch(str(endpoint), data)
        return json_response

    def remove_schedule(self, schedule_id: int) -> dict:
        endpoint = Path("schedules") / str(schedule_id)
        json_response = self.delete(str(endpoint))
        return json_response

    @returns("Schedule")
    def create_schedule(self, data: dict) -> dict:
        return self.post("schedules", data)

    # Available
    @returns("List[Host]")
    def get_available(self) -> dict:
        json_response = self.get("available")
        return json_response

    @returns("List[Host]")
    def filter_available(self, data: dict) -> dict:
        json_response = self.get(f"available?{urlencode(data)}")
        return json_response

    # Assignments
    @returns("Assignment")
    def create_assignment(self, data: dict) -> dict:
        response = self.post("assignments", data)
        if response and {"id", "cloud"} <= response.keys():
            print(f"Assignment created - ID: {response['id']}, Cloud: {response['cloud']['name']}")
        return response

    @returns("Assignment")
    def create_self_assignment(self, data: dict) -> dict:
        endpoint = Path("assignments") / "self"
        response = self.post(str(endpoint), data)
        if response and {"id", "cloud"} <= response.keys():
            print(f"Self-assignment created - ID: {response['id']}, Cloud: {response['cloud']['name']}")
        return response

    @returns("Assignment")
    def update_assignment(self, assignment_id: int, data: dict) -> dict:
        endpoint = Path("assignments") / str(assignment_id)
        json_response = self.patch(str(endpoint), data)
        return json_response

    @returns("Notification")
    def update_notification(self, notification_id: int, data: dict) -> dict:
        endpoint = Path("notifications") / str(notification_id)
        json_response = self.patch(str(endpoint), data)
        return json_response

    @returns("Assignment")
    def get_active_cloud_assignment(self, cloud_name: str) -> dict:
        endpoint = Path("assignments") / "active" / cloud_name
        json_response = self.get(str(endpoint))
        return json_response

    @returns("List[Assignment]")
    def get_active_assignments(self) -> dict:
        json_response = self.get("assignments/active")
        return json_response

    def terminate_assignment(self, assignment_id: int) -> dict:
        endpoint = Path("assignments") / "terminate" / str(assignment_id)
        json_response = self.post(str(endpoint))
        return json_response

    # Interfaces
    @returns("List[Interface]")
    def get_host_interface(self, hostname: str) -> dict:
        endpoint = Path("hosts") / hostname / "interfaces"
        json_response = self.get(str(endpoint))
        return json_response

    @returns("List[Interface]")
    def get_interfaces(self) -> dict:
        json_response = self.get("interfaces")
        return json_response

    @returns("Interface")
    def update_interface(self, hostname: str, data: dict) -> dict:
        endpoint = Path("interfaces") / hostname
        json_response = self.patch(str(endpoint), data)
        return json_response

    def remove_interface(self, hostname: str, if_name: str) -> dict:
        endpoint = Path("interfaces") / hostname / if_name
        json_response = self.delete(str(endpoint))
        return json_response

    @returns("Interface")
    def create_interface(self, hostname: str, data: dict) -> dict:
        endpoint = Path("interfaces") / hostname
        json_response = self.post(str(endpoint), data)
        return json_response

    # Memory
    @returns("Memory")
    def create_memory(self, hostname: str, data: dict) -> dict:
        endpoint = Path("memory") / hostname
        json_response = self.post(str(endpoint), data)
        return json_response

    def remove_memory(self, memory_id: int) -> dict:
        endpoint = Path("memory") / memory_id
        json_response = self.delete(str(endpoint))
        return json_response

    # Disks
    @returns("Disk")
    def create_disk(self, hostname: str, data: dict) -> dict:
        endpoint = Path("disks") / hostname
        json_response = self.post(str(endpoint), data)
        return json_response

    @returns("Disk")
    def update_disk(self, hostname: str, data: dict) -> dict:
        endpoint = Path("disks") / hostname
        json_response = self.patch(str(endpoint), data)
        return json_response

    def remove_disk(self, hostname: str, disk_id: int) -> dict:
        endpoint = Path("disks") / hostname / disk_id
        json_response = self.delete(str(endpoint))
        return json_response

    # Processor
    @returns("Processor")
    def create_processor(self, hostname: str, data: dict) -> dict:
        endpoint = Path("processors") / hostname
        json_response = self.post(str(endpoint), data)
        return json_response

    def remove_processor(self, processor_id: int) -> dict:
        endpoint = Path("processors") / processor_id
        json_response = self.delete(str(endpoint))
        return json_response

    # Vlans
    @returns("List[Vlan]")
    def get_vlans(self) -> dict:
        json_response = self.get("vlans")
        return json_response

    @returns("Vlan")
    def get_vlan(self, vlan_id: int) -> dict:
        endpoint = Path("vlans") / str(vlan_id)
        json_response = self.get(str(endpoint))
        return json_response

    @returns("List[Vlan]")
    def get_free_vlans(self) -> dict:
        endpoint = Path("vlans") / "free"
        json_response = self.get(str(endpoint))
        return json_response

    @returns("Vlan")
    def update_vlan(self, vlan_id: int, data: dict) -> dict:
        endpoint = Path("vlans") / str(vlan_id)
        json_response = self.patch(str(endpoint), data)
        return json_response

    @returns("Vlan")
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
