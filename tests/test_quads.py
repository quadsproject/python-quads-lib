from json import JSONDecodeError
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from quads_lib.base import QuadsBase
from quads_lib.exceptions import APIBadRequest
from quads_lib.exceptions import APIServerException
from quads_lib.quads import QuadsApi


class TestQuadsApi:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.username = "testuser"
        self.password = "testpassword"
        self.base_url = "http://example.com/"
        self.api = QuadsApi(self.username, self.password, self.base_url)

    @patch("requests.Session.request")
    def test_get_hosts(self, mock_get):
        expected_response = {"hosts": [{"name": "host1", "model": "model1"}, {"name": "host2", "model": "model2"}]}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_hosts()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/hosts")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_hosts_empty(self, mock_get):
        expected_response = {"hosts": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_hosts()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/hosts")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_hosts_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_hosts()

    @patch("requests.Session.request")
    def test_get_host_models(self, mock_get):
        expected_response = {
            "model1": [{"name": "host1", "model": "model1"}, {"name": "host2", "model": "model1"}],
            "model2": [{"name": "host3", "model": "model2"}],
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_host_models()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/hosts?group_by=model")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_host_models_empty(self, mock_get):
        expected_response = {}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_host_models()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/hosts?group_by=model")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_host_models_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_host_models()

    @patch("requests.Session.request")
    def test_get_hosts_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid request parameters"}
        mock_get.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Invalid request parameters"):
            self.api.get_hosts()

    @patch("requests.Session.request")
    def test_get_host_models_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid group_by parameter"}
        mock_get.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Invalid group_by parameter"):
            self.api.get_host_models()

    @patch("requests.Session.request")
    def test_get_hosts_bad_request_no_json(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Failed to parse response"):
            self.api.get_hosts()

    @patch("requests.Session.request")
    def test_filter_hosts(self, mock_get):
        expected_response = {"hosts": [{"name": "host1", "model": "model1"}, {"name": "host2", "model": "model1"}]}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        filter_data = {"model": "model1", "cloud": "cloud1", "status": "active"}

        result = self.api.filter_hosts(filter_data)

        mock_get.assert_called_once()
        called_url = str(mock_get.call_args[0][1])
        assert called_url.endswith(
            (
                "/hosts?model=model1&cloud=cloud1&status=active",
                "/hosts?status=active&model=model1&cloud=cloud1",
                "/hosts?cloud=cloud1&status=active&model=model1",
            )
        )
        assert result == expected_response

    @patch("requests.Session.request")
    def test_filter_hosts_special_chars(self, mock_get):
        expected_response = {"hosts": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        filter_data = {"name": "test host & more", "tag": "special=tag"}

        result = self.api.filter_hosts(filter_data)

        mock_get.assert_called_once()
        called_url = str(mock_get.call_args[0][1])
        assert "name=test+host+%26+more" in called_url
        assert "tag=special%3Dtag" in called_url
        assert result == expected_response

    @patch("requests.Session.request")
    def test_filter_hosts_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.filter_hosts({"model": "test"})

    @patch("requests.Session.request")
    def test_filter_hosts_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid filter parameters"}
        mock_get.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Invalid filter parameters"):
            self.api.filter_hosts({"invalid": "parameter"})

    @patch("requests.Session.request")
    def test_filter_clouds(self, mock_get):
        expected_response = {"clouds": [{"name": "cloud1", "owner": "user1"}, {"name": "cloud2", "owner": "user1"}]}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        filter_data = {"owner": "user1", "description": "test cloud", "ticket": "123"}

        result = self.api.filter_clouds(filter_data)

        mock_get.assert_called_once()
        called_url = str(mock_get.call_args[0][1])
        assert called_url.endswith(
            (
                "/clouds?owner=user1&description=test+cloud&ticket=123",
                "/clouds?ticket=123&owner=user1&description=test+cloud",
                "/clouds?description=test+cloud&ticket=123&owner=user1",
            )
        )
        assert result == expected_response

    @patch("requests.Session.request")
    def test_filter_clouds_special_chars(self, mock_get):
        expected_response = {"clouds": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        filter_data = {"name": "test cloud & more", "tag": "special=tag"}

        result = self.api.filter_clouds(filter_data)

        mock_get.assert_called_once()
        called_url = str(mock_get.call_args[0][1])
        assert "name=test+cloud+%26+more" in called_url
        assert "tag=special%3Dtag" in called_url
        assert result == expected_response

    @patch("requests.Session.request")
    def test_filter_clouds_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.filter_clouds({"owner": "test"})

    @patch("requests.Session.request")
    def test_filter_clouds_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid filter parameters"}
        mock_get.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Invalid filter parameters"):
            self.api.filter_clouds({"invalid": "parameter"})

    @patch("requests.Session.request")
    def test_filter_assignments(self, mock_get):
        expected_response = {"assignments": [{"id": 1, "cloud": "cloud1", "host": "host1"}, {"id": 2, "cloud": "cloud1", "host": "host2"}]}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        filter_data = {"cloud": "cloud1", "host": "host1", "status": "active"}

        result = self.api.filter_assignments(filter_data)

        mock_get.assert_called_once()
        called_url = str(mock_get.call_args[0][1])
        assert called_url.endswith(
            (
                "/assignments?cloud=cloud1&host=host1&status=active",
                "/assignments?status=active&cloud=cloud1&host=host1",
                "/assignments?host=host1&status=active&cloud=cloud1",
            )
        )
        assert result == expected_response

    @patch("requests.Session.request")
    def test_filter_assignments_special_chars(self, mock_get):
        expected_response = {"assignments": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        filter_data = {"cloud": "test cloud & more", "tag": "special=tag"}

        result = self.api.filter_assignments(filter_data)

        mock_get.assert_called_once()
        called_url = str(mock_get.call_args[0][1])
        assert "cloud=test+cloud+%26+more" in called_url
        assert "tag=special%3Dtag" in called_url
        assert result == expected_response

    @patch("requests.Session.request")
    def test_filter_assignments_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.filter_assignments({"cloud": "test"})

    @patch("requests.Session.request")
    def test_filter_assignments_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid filter parameters"}
        mock_get.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Invalid filter parameters"):
            self.api.filter_assignments({"invalid": "parameter"})

    @patch("requests.Session.request")
    def test_get_host(self, mock_get):
        expected_response = {"name": "host1", "model": "model1", "cloud": "cloud1", "interfaces": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_host("host1")

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/hosts/host1")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_host_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_host("host1")

    @patch("requests.Session.request")
    def test_get_host_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Host not found"}
        mock_get.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Host not found"):
            self.api.get_host("nonexistent")

    @patch("requests.Session.request")
    def test_get_host_special_chars(self, mock_get):
        expected_response = {"name": "host.1", "model": "model1"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_host("host.1")

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/hosts/host.1")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_create_host(self, mock_post):
        host_data = {"name": "new-host", "model": "model1", "cloud": "cloud1", "interfaces": []}
        mock_response = Mock()
        mock_response.json.return_value = host_data
        mock_post.return_value = mock_response

        result = self.api.create_host(host_data)

        mock_post.assert_called_once()
        assert str(mock_post.call_args[0][1]).endswith("/hosts")
        assert result == host_data

    @patch("requests.Session.request")
    def test_create_host_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.create_host({"name": "new-host"})

    @patch("requests.Session.request")
    def test_create_host_bad_request(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid host data"}
        mock_post.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Invalid host data"):
            self.api.create_host({"invalid": "data"})

    @patch("requests.Session.request")
    def test_create_host_with_all_fields(self, mock_post):
        host_data = {
            "name": "new-host",
            "model": "model1",
            "cloud": "cloud1",
            "interfaces": [{"name": "eth0", "mac_address": "00:11:22:33:44:55"}],
            "disks": [{"name": "sda", "size": "1TB"}],
            "memory": {"total": "64GB"},
            "processors": [{"model": "Intel", "cores": 32}],
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = host_data
        mock_post.return_value = mock_response

        result = self.api.create_host(host_data)

        mock_post.assert_called_once()
        assert str(mock_post.call_args[0][1]).endswith("/hosts")
        assert mock_post.call_args[1]["json"] == host_data
        assert result == host_data

    @patch("requests.Session.request")
    def test_update_host(self, mock_patch):
        hostname = "existing-host"
        update_data = {"model": "updated-model", "cloud": "new-cloud"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = update_data
        mock_patch.return_value = mock_response

        result = self.api.update_host(hostname, update_data)

        mock_patch.assert_called_once()
        assert str(mock_patch.call_args[0][1]).endswith(f"/hosts/{hostname}")
        assert mock_patch.call_args[1]["json"] == update_data
        assert result == update_data

    @patch("requests.Session.request")
    def test_update_host_error(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_patch.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.update_host("host1", {"model": "new-model"})

    @patch("requests.Session.request")
    def test_update_host_bad_request(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Host not found"}
        mock_patch.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Host not found"):
            self.api.update_host("nonexistent", {"model": "new-model"})

    @patch("requests.Session.request")
    def test_update_host_all_fields(self, mock_patch):
        hostname = "existing-host"
        update_data = {
            "model": "updated-model",
            "cloud": "new-cloud",
            "interfaces": [{"name": "eth0", "mac_address": "00:11:22:33:44:55"}],
            "disks": [{"name": "sda", "size": "2TB"}],
            "memory": {"total": "128GB"},
            "processors": [{"model": "AMD", "cores": 64}],
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = update_data
        mock_patch.return_value = mock_response

        result = self.api.update_host(hostname, update_data)

        mock_patch.assert_called_once()
        assert str(mock_patch.call_args[0][1]).endswith(f"/hosts/{hostname}")
        assert mock_patch.call_args[1]["json"] == update_data
        assert result == update_data

    @patch("requests.Session.request")
    def test_remove_host(self, mock_delete):
        hostname = "host-to-remove"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_delete.return_value = mock_response

        result = self.api.remove_host(hostname)

        mock_delete.assert_called_once()
        assert str(mock_delete.call_args[0][1]).endswith(f"/hosts/{hostname}")
        assert result == {}

    @patch("requests.Session.request")
    def test_remove_host_error(self, mock_delete):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_delete.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.remove_host("host1")

    @patch("requests.Session.request")
    def test_remove_host_bad_request(self, mock_delete):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Host not found"}
        mock_delete.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Host not found"):
            self.api.remove_host("nonexistent")

    @patch("requests.Session.request")
    def test_remove_host_special_chars(self, mock_delete):
        hostname = "host.with.dots"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_delete.return_value = mock_response

        result = self.api.remove_host(hostname)

        mock_delete.assert_called_once()
        assert str(mock_delete.call_args[0][1]).endswith(f"/hosts/{hostname}")
        assert result == {}

    @patch("requests.Session.request")
    def test_is_available_true(self, mock_get):
        hostname = "test-host"
        query_data = {"start_date": "2024-03-20", "end_date": "2024-03-21"}
        mock_response = Mock()
        mock_response.json.return_value = "true"
        mock_get.return_value = mock_response

        result = self.api.is_available(hostname, query_data)

        mock_get.assert_called_once()
        called_url = str(mock_get.call_args[0][1])
        assert called_url.endswith(
            (
                f"/available/{hostname}?start_date=2024-03-20&end_date=2024-03-21",
                f"/available/{hostname}?end_date=2024-03-21&start_date=2024-03-20",
            )
        )
        assert result is True

    @patch("requests.Session.request")
    def test_is_available_false(self, mock_get):
        hostname = "test-host"
        query_data = {"start_date": "2024-03-20", "end_date": "2024-03-21"}
        mock_response = Mock()
        mock_response.json.return_value = "false"
        mock_get.return_value = mock_response

        result = self.api.is_available(hostname, query_data)

        mock_get.assert_called_once()
        assert result is False

    @patch("requests.Session.request")
    def test_is_available_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.is_available("host1", {"start_date": "2024-03-20"})

    @patch("requests.Session.request")
    def test_is_available_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid date format"}
        mock_get.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Invalid date format"):
            self.api.is_available("host1", {"start_date": "invalid-date"})

    @patch("requests.Session.request")
    def test_get_clouds(self, mock_get):
        expected_response = {
            "clouds": [{"name": "cloud1", "owner": "user1", "ticket": "123"}, {"name": "cloud2", "owner": "user2", "ticket": "456"}]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_clouds()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/clouds")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_clouds_empty(self, mock_get):
        expected_response = {"clouds": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_clouds()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/clouds")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_clouds_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_clouds()

    @patch("requests.Session.request")
    def test_get_clouds_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid request"}
        mock_get.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Invalid request"):
            self.api.get_clouds()

    @patch("requests.Session.request")
    def test_get_free_clouds(self, mock_get):
        expected_response = {
            "clouds": [{"name": "cloud1", "owner": "user1", "status": "free"}, {"name": "cloud2", "owner": "user2", "status": "free"}]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_free_clouds()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/clouds/free/")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_free_clouds_empty(self, mock_get):
        expected_response = {"clouds": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_free_clouds()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/clouds/free/")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_free_clouds_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_free_clouds()

    @patch("requests.Session.request")
    def test_get_free_clouds_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid request"}
        mock_get.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Invalid request"):
            self.api.get_free_clouds()

    @patch("requests.Session.request")
    def test_get_cloud(self, mock_get):
        cloud_name = "test-cloud"
        expected_response = {"name": "test-cloud", "owner": "user1", "ticket": "123", "description": "Test cloud environment"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_cloud(cloud_name)

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith(f"/clouds?name={cloud_name}")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_cloud_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_cloud("test-cloud")

    @patch("requests.Session.request")
    def test_get_cloud_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Cloud not found"}
        mock_get.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Cloud not found"):
            self.api.get_cloud("nonexistent-cloud")

    @patch("requests.Session.request")
    def test_get_summary(self, mock_get):
        query_data = {"start_date": "2024-03-20", "end_date": "2024-03-21"}
        expected_response = {"total_clouds": 10, "active_clouds": 5, "free_clouds": 5}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_summary(query_data)

        mock_get.assert_called_once()
        called_url = str(mock_get.call_args[0][1])
        assert called_url.endswith(
            ("/clouds/summary?start_date=2024-03-20&end_date=2024-03-21", "/clouds/summary?end_date=2024-03-21&start_date=2024-03-20")
        )
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_summary_no_params(self, mock_get):
        expected_response = {"total_clouds": 10, "active_clouds": 5, "free_clouds": 5}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_summary({})

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/clouds/summary")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_summary_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_summary({"start_date": "2024-03-20"})

    @patch("requests.Session.request")
    def test_get_summary_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid date format"}
        mock_get.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Invalid date format"):
            self.api.get_summary({"start_date": "invalid-date"})

    @patch("requests.Session.request")
    def test_create_cloud(self, mock_post):
        cloud_data = {"name": "new-cloud", "owner": "user1", "ticket": "123", "description": "New test cloud"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = cloud_data
        mock_post.return_value = mock_response

        result = self.api.create_cloud(cloud_data)

        mock_post.assert_called_once()
        assert str(mock_post.call_args[0][1]).endswith("/clouds")
        assert mock_post.call_args[1]["json"] == cloud_data
        assert result == cloud_data

    @patch("requests.Session.request")
    def test_create_cloud_minimal(self, mock_post):
        cloud_data = {"name": "new-cloud", "owner": "user1"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = cloud_data
        mock_post.return_value = mock_response

        result = self.api.create_cloud(cloud_data)

        mock_post.assert_called_once()
        assert str(mock_post.call_args[0][1]).endswith("/clouds")
        assert mock_post.call_args[1]["json"] == cloud_data
        assert result == cloud_data

    @patch("requests.Session.request")
    def test_create_cloud_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.create_cloud({"name": "new-cloud"})

    @patch("requests.Session.request")
    def test_create_cloud_bad_request(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Cloud name already exists"}
        mock_post.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Cloud name already exists"):
            self.api.create_cloud({"name": "existing-cloud"})

    @patch("requests.Session.request")
    def test_update_cloud(self, mock_patch):
        cloud_name = "existing-cloud"
        update_data = {"owner": "new-owner", "ticket": "456", "description": "Updated description"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = update_data
        mock_patch.return_value = mock_response

        result = self.api.update_cloud(cloud_name, update_data)

        mock_patch.assert_called_once()
        assert str(mock_patch.call_args[0][1]).endswith(f"/clouds/{cloud_name}")
        assert mock_patch.call_args[1]["json"] == update_data
        assert result == update_data

    @patch("requests.Session.request")
    def test_update_cloud_error(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_patch.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.update_cloud("cloud1", {"owner": "new-owner"})

    @patch("requests.Session.request")
    def test_update_cloud_bad_request(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Cloud not found"}
        mock_patch.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Cloud not found"):
            self.api.update_cloud("nonexistent", {"owner": "new-owner"})

    @patch("requests.Session.request")
    def test_remove_cloud(self, mock_delete):
        cloud_name = "cloud-to-remove"
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.status_code = 200
        mock_delete.return_value = mock_response

        result = self.api.remove_cloud(cloud_name)

        mock_delete.assert_called_once()
        assert str(mock_delete.call_args[0][1]).endswith(f"/clouds/{cloud_name}")
        assert result == {}

    @patch("requests.Session.request")
    def test_remove_cloud_error(self, mock_delete):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_delete.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.remove_cloud("cloud1")

    @patch("requests.Session.request")
    def test_remove_cloud_bad_request(self, mock_delete):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Cloud not found"}
        mock_delete.return_value = mock_response

        with pytest.raises(APIBadRequest, match="Cloud not found"):
            self.api.remove_cloud("nonexistent")

    @patch("requests.Session.request")
    def test_get_schedules(self, mock_get):
        expected_response = {
            "schedules": [
                {"id": 1, "cloud": "cloud1", "start": "2024-03-20", "end": "2024-03-21"},
                {"id": 2, "cloud": "cloud2", "start": "2024-03-22", "end": "2024-03-23"},
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_schedules()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/schedules")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_schedules_with_params(self, mock_get):
        query_data = {"cloud": "cloud1", "start": "2024-03-20"}
        expected_response = {"schedules": [{"id": 1, "cloud": "cloud1", "start": "2024-03-20", "end": "2024-03-21"}]}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_schedules(query_data)

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/schedules?cloud=cloud1&start=2024-03-20") or str(mock_get.call_args[0][1]).endswith(
            "/schedules?start=2024-03-20&cloud=cloud1"
        )
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_current_schedules(self, mock_get):
        expected_response = {"schedules": [{"id": 1, "cloud": "cloud1", "start": "2024-03-20", "end": "2024-03-21"}]}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_current_schedules()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/schedules/current")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_current_schedules_with_params(self, mock_get):
        query_data = {"cloud": "cloud1"}
        expected_response = {"schedules": [{"id": 1, "cloud": "cloud1", "start": "2024-03-20", "end": "2024-03-21"}]}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_current_schedules(query_data)

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/schedules/current?cloud=cloud1")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_schedules_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_schedules()

    @patch("requests.Session.request")
    def test_get_current_schedules_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_current_schedules()

    @patch("requests.Session.request")
    def test_get_schedule(self, mock_get):
        schedule_id = 123
        expected_response = {"id": 123, "cloud": "cloud1", "start": "2024-03-20", "end": "2024-03-21"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_schedule(schedule_id)

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith(f"/schedules/{schedule_id}")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_future_schedules(self, mock_get):
        expected_response = {
            "schedules": [
                {"id": 1, "cloud": "cloud1", "start": "2024-03-20", "end": "2024-03-21"},
                {"id": 2, "cloud": "cloud2", "start": "2024-03-22", "end": "2024-03-23"},
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_future_schedules()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/schedules/future")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_future_schedules_with_params(self, mock_get):
        query_data = {"cloud": "cloud1"}
        expected_response = {"schedules": [{"id": 1, "cloud": "cloud1", "start": "2024-03-20", "end": "2024-03-21"}]}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_future_schedules(query_data)

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/schedules/future?cloud=cloud1")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_update_schedule(self, mock_patch):
        schedule_id = 123
        update_data = {"cloud": "new-cloud", "end": "2024-03-22"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = update_data
        mock_patch.return_value = mock_response

        result = self.api.update_schedule(schedule_id, update_data)

        mock_patch.assert_called_once()
        assert str(mock_patch.call_args[0][1]).endswith(f"/schedules/{schedule_id}")
        assert mock_patch.call_args[1]["json"] == update_data
        assert result == update_data

    @patch("requests.Session.request")
    def test_remove_schedule(self, mock_delete):
        schedule_id = 123
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.status_code = 200
        mock_delete.return_value = mock_response

        result = self.api.remove_schedule(schedule_id)

        mock_delete.assert_called_once()
        assert str(mock_delete.call_args[0][1]).endswith(f"/schedules/{schedule_id}")
        assert result == {}

    @patch("requests.Session.request")
    def test_get_schedule_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_schedule(123)

    @patch("requests.Session.request")
    def test_get_future_schedules_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_future_schedules()

    @patch("requests.Session.request")
    def test_update_schedule_error(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_patch.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.update_schedule(123, {"cloud": "new-cloud"})

    @patch("requests.Session.request")
    def test_remove_schedule_error(self, mock_delete):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_delete.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.remove_schedule(123)

    @patch("requests.Session.request")
    def test_create_schedule(self, mock_post):
        schedule_data = {"cloud": "cloud1", "start": "2024-03-20", "end": "2024-03-21"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = schedule_data
        mock_post.return_value = mock_response

        result = self.api.create_schedule(schedule_data)

        mock_post.assert_called_once()
        assert str(mock_post.call_args[0][1]).endswith("/schedules")
        assert mock_post.call_args[1]["json"] == schedule_data
        assert result == schedule_data

    @patch("requests.Session.request")
    def test_get_available(self, mock_get):
        expected_response = {"hosts": [{"name": "host1", "model": "model1"}, {"name": "host2", "model": "model2"}]}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_available()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/available")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_filter_available(self, mock_get):
        filter_data = {"start_date": "2024-03-20", "end_date": "2024-03-21", "model": "model1"}
        expected_response = {"hosts": [{"name": "host1", "model": "model1"}]}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.filter_available(filter_data)

        mock_get.assert_called_once()
        called_url = str(mock_get.call_args[0][1])
        assert "start_date=2024-03-20" in called_url
        assert "end_date=2024-03-21" in called_url
        assert "model=model1" in called_url
        assert result == expected_response

    @patch("requests.Session.request")
    def test_create_assignment(self, mock_post):
        assignment_data = {"cloud": "cloud1", "host": "host1", "start": "2024-03-20", "end": "2024-03-21"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = assignment_data
        mock_post.return_value = mock_response

        result = self.api.create_assignment(assignment_data)

        mock_post.assert_called_once()
        assert str(mock_post.call_args[0][1]).endswith("/assignments")
        assert mock_post.call_args[1]["json"] == assignment_data
        assert result == assignment_data

    @patch("requests.Session.request")
    def test_update_assignment(self, mock_patch):
        assignment_id = 123
        update_data = {"end": "2024-03-22", "status": "completed"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = update_data
        mock_patch.return_value = mock_response

        result = self.api.update_assignment(assignment_id, update_data)

        mock_patch.assert_called_once()
        assert str(mock_patch.call_args[0][1]).endswith(f"/assignments/{assignment_id}")
        assert mock_patch.call_args[1]["json"] == update_data
        assert result == update_data

    @patch("requests.Session.request")
    def test_update_notification(self, mock_patch):
        notification_id = 456
        update_data = {"status": "read", "acknowledged": True}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = update_data
        mock_patch.return_value = mock_response

        result = self.api.update_notification(notification_id, update_data)

        mock_patch.assert_called_once()
        assert str(mock_patch.call_args[0][1]).endswith(f"/notifications/{notification_id}")
        assert mock_patch.call_args[1]["json"] == update_data
        assert result == update_data

    @patch("requests.Session.request")
    def test_create_schedule_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.create_schedule({"cloud": "cloud1"})

    @patch("requests.Session.request")
    def test_get_available_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_available()

    @patch("requests.Session.request")
    def test_create_assignment_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.create_assignment({"cloud": "cloud1"})

    @patch("requests.Session.request")
    def test_update_assignment_error(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_patch.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.update_assignment(123, {"status": "completed"})

    @patch("requests.Session.request")
    def test_update_notification_error(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_patch.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.update_notification(456, {"status": "read"})

    @patch("requests.Session.request")
    def test_get_active_cloud_assignment(self, mock_get):
        cloud_name = "cloud1"
        expected_response = {"id": 123, "cloud": "cloud1", "host": "host1", "status": "active"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_active_cloud_assignment(cloud_name)

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith(f"/assignments/active/{cloud_name}")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_active_assignments(self, mock_get):
        expected_response = {
            "assignments": [
                {"id": 1, "cloud": "cloud1", "host": "host1", "status": "active"},
                {"id": 2, "cloud": "cloud2", "host": "host2", "status": "active"},
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_active_assignments()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/assignments/active")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_host_interface(self, mock_get):
        hostname = "host1"
        expected_response = {
            "interfaces": [{"name": "eth0", "mac_address": "00:11:22:33:44:55"}, {"name": "eth1", "mac_address": "00:11:22:33:44:66"}]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_host_interface(hostname)

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith(f"/hosts/{hostname}/interfaces")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_interfaces(self, mock_get):
        expected_response = {
            "interfaces": [
                {"host": "host1", "name": "eth0", "mac_address": "00:11:22:33:44:55"},
                {"host": "host2", "name": "eth0", "mac_address": "00:11:22:33:44:66"},
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_interfaces()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/interfaces")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_update_interface(self, mock_patch):
        hostname = "host1"
        update_data = {"name": "eth0", "mac_address": "00:11:22:33:44:77"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = update_data
        mock_patch.return_value = mock_response

        result = self.api.update_interface(hostname, update_data)

        mock_patch.assert_called_once()
        assert str(mock_patch.call_args[0][1]).endswith(f"/interfaces/{hostname}")
        assert mock_patch.call_args[1]["json"] == update_data
        assert result == update_data

    @patch("requests.Session.request")
    def test_remove_interface(self, mock_delete):
        hostname = "host1"
        if_name = "eth0"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_delete.return_value = mock_response

        result = self.api.remove_interface(hostname, if_name)

        mock_delete.assert_called_once()
        assert str(mock_delete.call_args[0][1]).endswith(f"/interfaces/{hostname}/{if_name}")
        assert result == {}

    @patch("requests.Session.request")
    def test_create_interface(self, mock_post):
        hostname = "host1"
        interface_data = {"name": "eth0", "mac_address": "00:11:22:33:44:55", "switch_port": "Gi1/0/1"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = interface_data
        mock_post.return_value = mock_response

        result = self.api.create_interface(hostname, interface_data)

        mock_post.assert_called_once()
        assert str(mock_post.call_args[0][1]).endswith(f"/interfaces/{hostname}")
        assert mock_post.call_args[1]["json"] == interface_data
        assert result == interface_data

    @patch("requests.Session.request")
    def test_create_memory(self, mock_post):
        hostname = "host1"
        memory_data = {"total": "64GB", "speed": "3200MHz"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = memory_data
        mock_post.return_value = mock_response

        result = self.api.create_memory(hostname, memory_data)

        mock_post.assert_called_once()
        assert str(mock_post.call_args[0][1]).endswith(f"/memory/{hostname}")
        assert mock_post.call_args[1]["json"] == memory_data
        assert result == memory_data

    @patch("requests.Session.request")
    def test_get_active_cloud_assignment_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_active_cloud_assignment("cloud1")

    @patch("requests.Session.request")
    def test_get_host_interface_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_host_interface("host1")

    @patch("requests.Session.request")
    def test_update_interface_error(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_patch.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.update_interface("host1", {"name": "eth0"})

    @patch("requests.Session.request")
    def test_create_interface_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.create_interface("host1", {"name": "eth0"})

    @patch("requests.Session.request")
    def test_remove_memory(self, mock_delete):
        memory_id = "123"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_delete.return_value = mock_response

        result = self.api.remove_memory(memory_id)

        mock_delete.assert_called_once()
        assert str(mock_delete.call_args[0][1]).endswith(f"/memory/{memory_id}")
        assert result == {}

    @patch("requests.Session.request")
    def test_create_disk(self, mock_post):
        hostname = "host1"
        disk_data = {"name": "sda", "size": "1TB", "type": "SSD"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = disk_data
        mock_post.return_value = mock_response

        result = self.api.create_disk(hostname, disk_data)

        mock_post.assert_called_once()
        assert str(mock_post.call_args[0][1]).endswith(f"/disks/{hostname}")
        assert mock_post.call_args[1]["json"] == disk_data
        assert result == disk_data

    @patch("requests.Session.request")
    def test_update_disk(self, mock_patch):
        hostname = "host1"
        disk_data = {"name": "sda", "size": "2TB"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = disk_data
        mock_patch.return_value = mock_response

        result = self.api.update_disk(hostname, disk_data)

        mock_patch.assert_called_once()
        assert str(mock_patch.call_args[0][1]).endswith(f"/disks/{hostname}")
        assert mock_patch.call_args[1]["json"] == disk_data
        assert result == disk_data

    @patch("requests.Session.request")
    def test_remove_disk(self, mock_delete):
        hostname = "host1"
        disk_id = "123"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_delete.return_value = mock_response

        result = self.api.remove_disk(hostname, disk_id)

        mock_delete.assert_called_once()
        assert str(mock_delete.call_args[0][1]).endswith(f"/disks/{hostname}/{disk_id}")
        assert result == {}

    @patch("requests.Session.request")
    def test_create_processor(self, mock_post):
        hostname = "host1"
        processor_data = {"model": "Intel Xeon", "cores": 32, "threads": 64}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = processor_data
        mock_post.return_value = mock_response

        result = self.api.create_processor(hostname, processor_data)

        mock_post.assert_called_once()
        assert str(mock_post.call_args[0][1]).endswith(f"/processors/{hostname}")
        assert mock_post.call_args[1]["json"] == processor_data
        assert result == processor_data

    @patch("requests.Session.request")
    def test_remove_processor(self, mock_delete):
        processor_id = "123"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_delete.return_value = mock_response

        result = self.api.remove_processor(processor_id)

        mock_delete.assert_called_once()
        assert str(mock_delete.call_args[0][1]).endswith(f"/processors/{processor_id}")
        assert result == {}

    @patch("requests.Session.request")
    def test_get_vlans(self, mock_get):
        expected_response = {
            "vlans": [
                {"id": 100, "name": "prod", "description": "Production network"},
                {"id": 200, "name": "dev", "description": "Development network"},
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_vlans()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/vlans")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_vlan(self, mock_get):
        vlan_id = 100
        expected_response = {"id": 100, "name": "prod", "description": "Production network"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_vlan(vlan_id)

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith(f"/vlans/{vlan_id}")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_free_vlan(self, mock_get):
        expected_response = {"id": 100, "name": "prod", "description": "Production network"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_free_vlans()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/vlans/free")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_update_vlan(self, mock_patch):
        vlan_id = 100
        update_data = {"name": "prod-new", "description": "Updated production network"}
        mock_response = Mock()
        mock_response.json.return_value = update_data
        mock_response.status_code = 200
        mock_patch.return_value = mock_response

        result = self.api.update_vlan(vlan_id, update_data)

        mock_patch.assert_called_once()
        assert str(mock_patch.call_args[0][1]).endswith(f"/vlans/{vlan_id}")
        assert mock_patch.call_args[1]["json"] == update_data
        assert result == update_data

    @patch("requests.Session.request")
    def test_create_vlan(self, mock_post):
        vlan_data = {"id": 300, "name": "test", "description": "Test network"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = vlan_data
        mock_post.return_value = mock_response

        result = self.api.create_vlan(vlan_data)

        mock_post.assert_called_once()
        assert str(mock_post.call_args[0][1]).endswith("/vlans")
        assert mock_post.call_args[1]["json"] == vlan_data
        assert result == vlan_data

    @patch("requests.Session.request")
    def test_get_moves(self, mock_get):
        expected_response = {
            "moves": [
                {"id": 1, "host": "host1", "from_cloud": "cloud1", "to_cloud": "cloud2"},
                {"id": 2, "host": "host2", "from_cloud": "cloud2", "to_cloud": "cloud3"},
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_moves()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/moves")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_moves_with_date(self, mock_get):
        date = "2024-03-20"
        expected_response = {"moves": [{"id": 1, "host": "host1", "from_cloud": "cloud1", "to_cloud": "cloud2"}]}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_moves(date)

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith(f"/moves?date={date}")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_get_version(self, mock_get):
        expected_response = {"version": "1.0.0", "api_version": "2.0"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response

        result = self.api.get_version()

        mock_get.assert_called_once()
        assert str(mock_get.call_args[0][1]).endswith("/version")
        assert result == expected_response

    @patch("requests.Session.request")
    def test_remove_memory_error(self, mock_delete):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_delete.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.remove_memory("123")

    @patch("requests.Session.request")
    def test_create_disk_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.create_disk("host1", {"name": "sda"})

    @patch("requests.Session.request")
    def test_get_vlans_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_vlans()

    @patch("requests.Session.request")
    def test_get_version_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_version()

    @patch("requests.Session.request")
    def test_terminate_assignment(self, mock_post):
        assignment_id = 123
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response
        result = self.api.terminate_assignment(assignment_id)

        mock_post.assert_called_once()
        assert str(mock_post.call_args[0][1]).endswith("/assignments/terminate/123")
        assert result == {}

    @patch("requests.Session.request")
    def test_create_self_assignment(self, mock_post):
        test_data = {"cloud": "test-cloud", "start": "2024-03-20", "end": "2024-03-21"}

        expected_response = {"status": "success", "assignment_id": 123}

        with patch.object(self.api, "post") as mock_post:
            mock_post.return_value = expected_response
            result = self.api.create_self_assignment(test_data)
            mock_post.assert_called_once_with(str(Path("assignments") / "self"), test_data)
            assert result == expected_response

    @patch("requests.Session.request")
    def test_register_success(self, mock_post):
        expected_response = {"status_code": 201, "message": "User registered successfully"}
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = expected_response
        mock_post.return_value = mock_response
        response = self.api.register()

        mock_post.assert_called_once()
        assert str(mock_post.call_args[0][1]).endswith("/register")
        assert response == expected_response

    @patch("requests.Session.request")
    def test_login_success(self, mock_post):
        expected_response = {"status_code": 201, "auth_token": "fake-token-123", "message": "Login successful"}
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = expected_response
        mock_post.return_value = mock_response
        response = self.api.login()
        mock_post.assert_called_once()
        assert str(mock_post.call_args[0][1]).endswith("/login")
        assert self.api.token == "fake-token-123"
        assert response == expected_response

    @patch("requests.Session.request")
    def test_login_failure(self, mock_post):
        expected_response = {"status_code": 401, "message": "Invalid credentials"}
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = expected_response
        mock_post.return_value = mock_response
        response = self.api.login()

        assert self.api.token is None
        assert not mock_post.headers.update.called
        assert response == expected_response

    @patch("requests.Session.request")
    def test_logout_success(self, mock_post):
        self.api.token = "existing-token"
        expected_response = {"status_code": 200, "message": "Logout successful"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_response
        mock_post.return_value = mock_response
        response = self.api.logout()

        mock_post.assert_called_once()
        assert self.api.token is None
        assert response == expected_response

    @patch("requests.Session.request")
    def test_logout_failure(self, mock_post):
        self.api.token = "existing-token"
        expected_response = {"status_code": 400, "message": "Logout failed"}
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = expected_response
        mock_post.return_value = mock_response
        with pytest.raises(APIBadRequest, match="Logout failed"):
            self.api.logout()

        assert self.api.token == "existing-token"

    @patch("builtins.print")
    @patch("requests.Session.request")
    def test_create_assignment_logging(self, mock_request, mock_print):
        assignment_data = {"cloud": "cloud1", "host": "host1", "start": "2025-06-20", "end": "2025-06-21"}
        response_data = {
            "id": 42,
            "cloud": {"name": "cloud1", "owner": "user1"},
            "host": "host1",
            "start": "2025-06-20",
            "end": "2025-06-21",
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = response_data
        mock_request.return_value = mock_response

        self.api.create_assignment(assignment_data)

        mock_print.assert_called_once_with("Assignment created - ID: 42, Cloud: cloud1")

    @patch("builtins.print")
    @patch("requests.Session.request")
    def test_create_assignment_no_logging(self, mock_request, mock_print):
        assignment_data = {"cloud": "cloud1", "host": "host1", "start": "2025-06-20", "end": "2025-06-21"}
        # Missing 'id' field in response - should not trigger logging
        response_data = {"cloud": {"name": "cloud1", "owner": "user1"}, "host": "host1", "start": "2025-06-20", "end": "2025-06-21"}

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = response_data
        mock_request.return_value = mock_response

        self.api.create_assignment(assignment_data)

        mock_print.assert_not_called()

    @patch("builtins.print")
    @patch("requests.Session.request")
    def test_create_assignment_limit_reached(self, mock_request, mock_print):
        assignment_data = {"cloud": "cloud1", "host": "host1", "start": "2025-06-20", "end": "2025-06-21"}
        # Error response for scheduling limit reached
        error_response = {"error": "Forbidden", "message": "Self scheduling limit reached", "status_code": 403}

        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = error_response
        mock_request.return_value = mock_response

        result = self.api.create_assignment(assignment_data)

        mock_print.assert_not_called()
        assert result == error_response

    @patch("builtins.print")
    @patch("requests.Session.request")
    def test_create_self_assignment_logging(self, mock_request, mock_print):
        assignment_data = {"cloud": "cloud1", "start": "2025-06-20", "end": "2025-06-21"}
        response_data = {"id": 123, "cloud": {"name": "cloud1", "owner": "user1"}, "start": "2025-06-20", "end": "2025-06-21"}

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = response_data
        mock_request.return_value = mock_response

        self.api.create_self_assignment(assignment_data)

        mock_print.assert_called_once_with("Self-assignment created - ID: 123, Cloud: cloud1")

    @patch("builtins.print")
    @patch("requests.Session.request")
    def test_create_self_assignment_no_logging(self, mock_request, mock_print):
        assignment_data = {"cloud": "cloud1", "start": "2025-06-20", "end": "2025-06-21"}
        # Missing 'cloud' field in response - should not trigger logging
        response_data = {"id": 123, "start": "2025-06-20", "end": "2025-06-21"}

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = response_data
        mock_request.return_value = mock_response

        self.api.create_self_assignment(assignment_data)

        mock_print.assert_not_called()

    @patch("builtins.print")
    @patch("requests.Session.request")
    def test_create_self_assignment_limit_reached(self, mock_request, mock_print):
        assignment_data = {"cloud": "cloud1", "start": "2025-06-20", "end": "2025-06-21"}
        # Error response for self scheduling limit reached
        error_response = {"error": "Forbidden", "message": "Self scheduling limit reached", "status_code": 403}

        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = error_response
        mock_request.return_value = mock_response

        result = self.api.create_self_assignment(assignment_data)

        mock_print.assert_not_called()
        assert result == error_response


class TestQuadsBase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.username = "test_user"
        self.password = "test_pass"
        self.base_url = "http://test.com"

    @pytest.fixture
    def quads_base(self):
        return QuadsBase(username=self.username, password=self.password, base_url=self.base_url)

    def test_context_manager_enter(self, quads_base):
        quads_base.login = Mock()
        with patch.object(quads_base, "login") as mock_login:
            result = quads_base.__enter__()
            mock_login.assert_called_once()
            assert result == quads_base

    def test_context_manager_exit(self, quads_base):
        quads_base.logout = Mock()
        quads_base.session = Mock()
        quads_base.__exit__(None, None, None)

        quads_base.logout.assert_called_once()
        quads_base.session.close.assert_called_once()

    @patch("requests.Session.request")
    def test_verify_default_false(self, mock_request):
        """Test that verify defaults to False for backward compatibility."""
        api = QuadsApi(self.username, self.password, self.base_url)
        expected_response = {"hosts": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_request.return_value = mock_response

        api.get_hosts()

        mock_request.assert_called_once()
        # Check that verify=False is passed
        assert mock_request.call_args[1]["verify"] is False

    def test_verify_default_false_login(self):
        """Test that verify defaults to False in login method."""
        api = QuadsApi(self.username, self.password, self.base_url)
        expected_response = {"status_code": 201, "auth_token": "token"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        api.session.post = Mock(return_value=mock_response)

        api.login()

        api.session.post.assert_called_once()
        # Check that verify=False is passed
        assert api.session.post.call_args[1]["verify"] is False

    @patch("requests.Session.request")
    def test_verify_true(self, mock_request):
        """Test that verify=True is passed correctly."""
        api = QuadsApi(self.username, self.password, self.base_url, verify=True)
        expected_response = {"hosts": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_request.return_value = mock_response

        api.get_hosts()

        mock_request.assert_called_once()
        # Check that verify=True is passed
        assert mock_request.call_args[1]["verify"] is True

    def test_verify_true_login(self):
        """Test that verify=True is passed correctly in login method."""
        api = QuadsApi(self.username, self.password, self.base_url, verify=True)
        expected_response = {"status_code": 201, "auth_token": "token"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        api.session.post = Mock(return_value=mock_response)

        api.login()

        api.session.post.assert_called_once()
        # Check that verify=True is passed
        assert api.session.post.call_args[1]["verify"] is True

    @patch("requests.Session.request")
    def test_verify_custom_ca_bundle(self, mock_request):
        """Test that a custom CA bundle path is passed correctly."""
        custom_ca = "/path/to/ca-bundle.pem"
        api = QuadsApi(self.username, self.password, self.base_url, verify=custom_ca)
        expected_response = {"hosts": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_request.return_value = mock_response

        api.get_hosts()

        mock_request.assert_called_once()
        # Check that custom CA bundle path is passed
        assert mock_request.call_args[1]["verify"] == custom_ca

    def test_verify_custom_ca_bundle_login(self):
        """Test that a custom CA bundle path is passed correctly in login method."""
        custom_ca = "/path/to/ca-bundle.pem"
        api = QuadsApi(self.username, self.password, self.base_url, verify=custom_ca)
        expected_response = {"status_code": 201, "auth_token": "token"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        api.session.post = Mock(return_value=mock_response)

        api.login()

        api.session.post.assert_called_once()
        # Check that custom CA bundle path is passed
        assert api.session.post.call_args[1]["verify"] == custom_ca
