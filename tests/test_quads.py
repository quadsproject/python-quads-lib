from unittest.mock import patch, Mock
import pytest
from quads_lib.quads import QuadsApi, APIServerException, APIBadRequest
from json import JSONDecodeError

class TestQuadsApi:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_config = Mock()
        self.mock_config.API_URL = "http://example.com"
        self.api = QuadsApi(self.mock_config)

    @patch('requests.Session.get')
    def test_get_hosts(self, mock_get):
        expected_response = {
            "hosts": [
                {"name": "host1", "model": "model1"},
                {"name": "host2", "model": "model2"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_hosts()
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/hosts")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_hosts_empty(self, mock_get):
        expected_response = {"hosts": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_hosts()
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/hosts")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_hosts_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_hosts()

    @patch('requests.Session.get')
    def test_get_host_models(self, mock_get):
        expected_response = {
            "model1": [
                {"name": "host1", "model": "model1"},
                {"name": "host2", "model": "model1"}
            ],
            "model2": [
                {"name": "host3", "model": "model2"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_host_models()
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/hosts?group_by=model")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_host_models_empty(self, mock_get):
        expected_response = {}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_host_models()
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/hosts?group_by=model")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_host_models_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_host_models()

    @patch('requests.Session.get')
    def test_get_hosts_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid request parameters"}
        mock_get.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Invalid request parameters"):
            self.api.get_hosts()

    @patch('requests.Session.get')
    def test_get_host_models_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid group_by parameter"}
        mock_get.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Invalid group_by parameter"):
            self.api.get_host_models()

    @patch('requests.Session.get')
    def test_get_hosts_bad_request_no_json(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Failed to parse response"):
            self.api.get_hosts()

    @patch('requests.Session.get')
    def test_filter_hosts(self, mock_get):
        expected_response = {
            "hosts": [
                {"name": "host1", "model": "model1"},
                {"name": "host2", "model": "model1"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        filter_data = {
            "model": "model1",
            "cloud": "cloud1",
            "status": "active"
        }
        
        result = self.api.filter_hosts(filter_data)
        
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        assert called_url.endswith("/hosts?model=model1&cloud=cloud1&status=active") or \
               called_url.endswith("/hosts?status=active&model=model1&cloud=cloud1") or \
               called_url.endswith("/hosts?cloud=cloud1&status=active&model=model1")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_filter_hosts_empty_params(self, mock_get):
        expected_response = {"hosts": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.filter_hosts({})
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/hosts?")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_filter_hosts_special_chars(self, mock_get):
        expected_response = {"hosts": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        filter_data = {
            "name": "test host & more",
            "tag": "special=tag"
        }
        
        result = self.api.filter_hosts(filter_data)
        
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        assert "name=test+host+%26+more" in called_url
        assert "tag=special%3Dtag" in called_url
        assert result == expected_response

    @patch('requests.Session.get')
    def test_filter_hosts_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.filter_hosts({"model": "test"})

    @patch('requests.Session.get')
    def test_filter_hosts_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid filter parameters"}
        mock_get.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Invalid filter parameters"):
            self.api.filter_hosts({"invalid": "parameter"})

    @patch('requests.Session.get')
    def test_filter_clouds(self, mock_get):
        expected_response = {
            "clouds": [
                {"name": "cloud1", "owner": "user1"},
                {"name": "cloud2", "owner": "user1"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        filter_data = {
            "owner": "user1",
            "description": "test cloud",
            "ticket": "123"
        }
        
        result = self.api.filter_clouds(filter_data)
        
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        assert called_url.endswith("/clouds?owner=user1&description=test+cloud&ticket=123") or \
               called_url.endswith("/clouds?ticket=123&owner=user1&description=test+cloud") or \
               called_url.endswith("/clouds?description=test+cloud&ticket=123&owner=user1")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_filter_clouds_empty_params(self, mock_get):
        expected_response = {"clouds": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.filter_clouds({})
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/clouds?")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_filter_clouds_special_chars(self, mock_get):
        expected_response = {"clouds": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        filter_data = {
            "name": "test cloud & more",
            "tag": "special=tag"
        }
        
        result = self.api.filter_clouds(filter_data)
        
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        assert "name=test+cloud+%26+more" in called_url
        assert "tag=special%3Dtag" in called_url
        assert result == expected_response

    @patch('requests.Session.get')
    def test_filter_clouds_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.filter_clouds({"owner": "test"})

    @patch('requests.Session.get')
    def test_filter_clouds_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid filter parameters"}
        mock_get.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Invalid filter parameters"):
            self.api.filter_clouds({"invalid": "parameter"})

    @patch('requests.Session.get')
    def test_filter_assignments(self, mock_get):
        expected_response = {
            "assignments": [
                {"id": 1, "cloud": "cloud1", "host": "host1"},
                {"id": 2, "cloud": "cloud1", "host": "host2"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        filter_data = {
            "cloud": "cloud1",
            "host": "host1",
            "status": "active"
        }
        
        result = self.api.filter_assignments(filter_data)
        
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        assert called_url.endswith("/assignments?cloud=cloud1&host=host1&status=active") or \
               called_url.endswith("/assignments?status=active&cloud=cloud1&host=host1") or \
               called_url.endswith("/assignments?host=host1&status=active&cloud=cloud1")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_filter_assignments_empty_params(self, mock_get):
        expected_response = {"assignments": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.filter_assignments({})
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/assignments?")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_filter_assignments_special_chars(self, mock_get):
        expected_response = {"assignments": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        filter_data = {
            "cloud": "test cloud & more",
            "tag": "special=tag"
        }
        
        result = self.api.filter_assignments(filter_data)
        
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        assert "cloud=test+cloud+%26+more" in called_url
        assert "tag=special%3Dtag" in called_url
        assert result == expected_response

    @patch('requests.Session.get')
    def test_filter_assignments_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.filter_assignments({"cloud": "test"})

    @patch('requests.Session.get')
    def test_filter_assignments_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid filter parameters"}
        mock_get.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Invalid filter parameters"):
            self.api.filter_assignments({"invalid": "parameter"})

    @patch('requests.Session.get')
    def test_get_host(self, mock_get):
        expected_response = {
            "name": "host1",
            "model": "model1",
            "cloud": "cloud1",
            "interfaces": []
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_host("host1")
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/hosts/host1")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_host_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_host("host1")

    @patch('requests.Session.get')
    def test_get_host_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Host not found"}
        mock_get.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Host not found"):
            self.api.get_host("nonexistent")

    @patch('requests.Session.get')
    def test_get_host_special_chars(self, mock_get):
        expected_response = {"name": "host.1", "model": "model1"}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_host("host.1")
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/hosts/host.1")
        assert result == expected_response

    @patch('requests.Session.post')
    def test_create_host(self, mock_post):
        host_data = {
            "name": "new-host",
            "model": "model1",
            "cloud": "cloud1",
            "interfaces": []
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.api.create_host(host_data)
        
        mock_post.assert_called_once()
        assert mock_post.call_args[0][0].endswith("/hosts")
        assert mock_post.call_args[1]["json"] == host_data
        assert result == mock_response

    @patch('requests.Session.post')
    def test_create_host_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.create_host({"name": "new-host"})

    @patch('requests.Session.post')
    def test_create_host_bad_request(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid host data"}
        mock_post.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Invalid host data"):
            self.api.create_host({"invalid": "data"})

    @patch('requests.Session.post')
    def test_create_host_with_all_fields(self, mock_post):
        host_data = {
            "name": "new-host",
            "model": "model1",
            "cloud": "cloud1",
            "interfaces": [{"name": "eth0", "mac_address": "00:11:22:33:44:55"}],
            "disks": [{"name": "sda", "size": "1TB"}],
            "memory": {"total": "64GB"},
            "processors": [{"model": "Intel", "cores": 32}]
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.api.create_host(host_data)
        
        mock_post.assert_called_once()
        assert mock_post.call_args[0][0].endswith("/hosts")
        assert mock_post.call_args[1]["json"] == host_data
        assert result == mock_response

    @patch('requests.Session.patch')
    def test_update_host(self, mock_patch):
        hostname = "existing-host"
        update_data = {
            "model": "updated-model",
            "cloud": "new-cloud"
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response
        
        result = self.api.update_host(hostname, update_data)
        
        mock_patch.assert_called_once()
        assert mock_patch.call_args[0][0].endswith(f"/hosts/{hostname}")
        assert mock_patch.call_args[1]["json"] == update_data
        assert result == mock_response

    @patch('requests.Session.patch')
    def test_update_host_error(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_patch.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.update_host("host1", {"model": "new-model"})

    @patch('requests.Session.patch')
    def test_update_host_bad_request(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Host not found"}
        mock_patch.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Host not found"):
            self.api.update_host("nonexistent", {"model": "new-model"})

    @patch('requests.Session.patch')
    def test_update_host_all_fields(self, mock_patch):
        hostname = "existing-host"
        update_data = {
            "model": "updated-model",
            "cloud": "new-cloud",
            "interfaces": [{"name": "eth0", "mac_address": "00:11:22:33:44:55"}],
            "disks": [{"name": "sda", "size": "2TB"}],
            "memory": {"total": "128GB"},
            "processors": [{"model": "AMD", "cores": 64}]
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response
        
        result = self.api.update_host(hostname, update_data)
        
        mock_patch.assert_called_once()
        assert mock_patch.call_args[0][0].endswith(f"/hosts/{hostname}")
        assert mock_patch.call_args[1]["json"] == update_data
        assert result == mock_response

    @patch('requests.Session.delete')
    def test_remove_host(self, mock_delete):
        hostname = "host-to-remove"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        
        result = self.api.remove_host(hostname)
        
        mock_delete.assert_called_once()
        assert mock_delete.call_args[0][0].endswith(f"/hosts/{hostname}")
        assert result == mock_response

    @patch('requests.Session.delete')
    def test_remove_host_error(self, mock_delete):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_delete.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.remove_host("host1")

    @patch('requests.Session.delete')
    def test_remove_host_bad_request(self, mock_delete):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Host not found"}
        mock_delete.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Host not found"):
            self.api.remove_host("nonexistent")

    @patch('requests.Session.delete')
    def test_remove_host_special_chars(self, mock_delete):
        hostname = "host.with.dots"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        
        result = self.api.remove_host(hostname)
        
        mock_delete.assert_called_once()
        assert mock_delete.call_args[0][0].endswith(f"/hosts/{hostname}")
        assert result == mock_response

    @patch('requests.Session.get')
    def test_is_available_true(self, mock_get):
        hostname = "test-host"
        query_data = {
            "start_date": "2024-03-20",
            "end_date": "2024-03-21"
        }
        mock_response = Mock()
        mock_response.json.return_value = "true"
        mock_get.return_value = mock_response
        
        result = self.api.is_available(hostname, query_data)
        
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        assert called_url.endswith(f"/available/{hostname}?start_date=2024-03-20&end_date=2024-03-21") or \
               called_url.endswith(f"/available/{hostname}?end_date=2024-03-21&start_date=2024-03-20")
        assert result is True

    @patch('requests.Session.get')
    def test_is_available_false(self, mock_get):
        hostname = "test-host"
        query_data = {
            "start_date": "2024-03-20",
            "end_date": "2024-03-21"
        }
        mock_response = Mock()
        mock_response.json.return_value = "false"
        mock_get.return_value = mock_response
        
        result = self.api.is_available(hostname, query_data)
        
        mock_get.assert_called_once()
        assert result is False

    @patch('requests.Session.get')
    def test_is_available_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.is_available("host1", {"start_date": "2024-03-20"})

    @patch('requests.Session.get')
    def test_is_available_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid date format"}
        mock_get.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Invalid date format"):
            self.api.is_available("host1", {"start_date": "invalid-date"})

    @patch('requests.Session.get')
    def test_is_available_empty_params(self, mock_get):
        hostname = "test-host"
        mock_response = Mock()
        mock_response.json.return_value = "true"
        mock_get.return_value = mock_response
        
        result = self.api.is_available(hostname, {})
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith(f"/available/{hostname}?")
        assert result is True

    @patch('requests.Session.get')
    def test_get_clouds(self, mock_get):
        expected_response = {
            "clouds": [
                {"name": "cloud1", "owner": "user1", "ticket": "123"},
                {"name": "cloud2", "owner": "user2", "ticket": "456"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_clouds()
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/clouds")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_clouds_empty(self, mock_get):
        expected_response = {"clouds": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_clouds()
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/clouds")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_clouds_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_clouds()

    @patch('requests.Session.get')
    def test_get_clouds_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid request"}
        mock_get.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Invalid request"):
            self.api.get_clouds()

    @patch('requests.Session.get')
    def test_get_free_clouds(self, mock_get):
        expected_response = {
            "clouds": [
                {"name": "cloud1", "owner": "user1", "status": "free"},
                {"name": "cloud2", "owner": "user2", "status": "free"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_free_clouds()
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/clouds/free/")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_free_clouds_empty(self, mock_get):
        expected_response = {"clouds": []}
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_free_clouds()
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/clouds/free/")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_free_clouds_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_free_clouds()

    @patch('requests.Session.get')
    def test_get_free_clouds_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid request"}
        mock_get.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Invalid request"):
            self.api.get_free_clouds()

    @patch('requests.Session.get')
    def test_get_cloud(self, mock_get):
        cloud_name = "test-cloud"
        expected_response = {
            "name": "test-cloud",
            "owner": "user1",
            "ticket": "123",
            "description": "Test cloud environment"
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_cloud(cloud_name)
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith(f"/clouds?name={cloud_name}")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_cloud_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_cloud("test-cloud")

    @patch('requests.Session.get')
    def test_get_cloud_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Cloud not found"}
        mock_get.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Cloud not found"):
            self.api.get_cloud("nonexistent-cloud")

    @patch('requests.Session.get')
    def test_get_summary(self, mock_get):
        query_data = {
            "start_date": "2024-03-20",
            "end_date": "2024-03-21"
        }
        expected_response = {
            "total_clouds": 10,
            "active_clouds": 5,
            "free_clouds": 5
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_summary(query_data)
        
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        assert called_url.endswith("/clouds/summary?start_date=2024-03-20&end_date=2024-03-21") or \
               called_url.endswith("/clouds/summary?end_date=2024-03-21&start_date=2024-03-20")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_summary_no_params(self, mock_get):
        expected_response = {
            "total_clouds": 10,
            "active_clouds": 5,
            "free_clouds": 5
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_summary({})
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/clouds/summary")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_summary_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_summary({"start_date": "2024-03-20"})

    @patch('requests.Session.get')
    def test_get_summary_bad_request(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid date format"}
        mock_get.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Invalid date format"):
            self.api.get_summary({"start_date": "invalid-date"})

    @patch('requests.Session.post')
    def test_insert_cloud(self, mock_post):
        cloud_data = {
            "name": "new-cloud",
            "owner": "user1",
            "ticket": "123",
            "description": "New test cloud"
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.api.insert_cloud(cloud_data)
        
        mock_post.assert_called_once()
        assert mock_post.call_args[0][0].endswith("/clouds")
        assert mock_post.call_args[1]["json"] == cloud_data
        assert result == mock_response

    @patch('requests.Session.post')
    def test_insert_cloud_minimal(self, mock_post):
        cloud_data = {
            "name": "new-cloud",
            "owner": "user1"
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.api.insert_cloud(cloud_data)
        
        mock_post.assert_called_once()
        assert mock_post.call_args[0][0].endswith("/clouds")
        assert mock_post.call_args[1]["json"] == cloud_data
        assert result == mock_response

    @patch('requests.Session.post')
    def test_insert_cloud_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.insert_cloud({"name": "new-cloud"})

    @patch('requests.Session.post')
    def test_insert_cloud_bad_request(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Cloud name already exists"}
        mock_post.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Cloud name already exists"):
            self.api.insert_cloud({"name": "existing-cloud"})

    @patch('requests.Session.patch')
    def test_update_cloud(self, mock_patch):
        cloud_name = "existing-cloud"
        update_data = {
            "owner": "new-owner",
            "ticket": "456",
            "description": "Updated description"
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response
        
        result = self.api.update_cloud(cloud_name, update_data)
        
        mock_patch.assert_called_once()
        assert mock_patch.call_args[0][0].endswith(f"/clouds/{cloud_name}")
        assert mock_patch.call_args[1]["json"] == update_data
        assert result == mock_response

    @patch('requests.Session.patch')
    def test_update_cloud_error(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_patch.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.update_cloud("cloud1", {"owner": "new-owner"})

    @patch('requests.Session.patch')
    def test_update_cloud_bad_request(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Cloud not found"}
        mock_patch.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Cloud not found"):
            self.api.update_cloud("nonexistent", {"owner": "new-owner"})

    @patch('requests.Session.delete')
    def test_remove_cloud(self, mock_delete):
        cloud_name = "cloud-to-remove"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        
        result = self.api.remove_cloud(cloud_name)
        
        mock_delete.assert_called_once()
        assert mock_delete.call_args[0][0].endswith(f"/clouds/{cloud_name}")
        assert result == mock_response

    @patch('requests.Session.delete')
    def test_remove_cloud_error(self, mock_delete):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_delete.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.remove_cloud("cloud1")

    @patch('requests.Session.delete')
    def test_remove_cloud_bad_request(self, mock_delete):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Cloud not found"}
        mock_delete.return_value = mock_response
        
        with pytest.raises(APIBadRequest, match="Cloud not found"):
            self.api.remove_cloud("nonexistent")

    @patch('requests.Session.get')
    def test_get_schedules(self, mock_get):
        expected_response = {
            "schedules": [
                {"id": 1, "cloud": "cloud1", "start": "2024-03-20", "end": "2024-03-21"},
                {"id": 2, "cloud": "cloud2", "start": "2024-03-22", "end": "2024-03-23"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_schedules()
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/schedules")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_schedules_with_params(self, mock_get):
        query_data = {"cloud": "cloud1", "start": "2024-03-20"}
        expected_response = {
            "schedules": [
                {"id": 1, "cloud": "cloud1", "start": "2024-03-20", "end": "2024-03-21"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_schedules(query_data)
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/schedules?cloud=cloud1&start=2024-03-20") or \
               mock_get.call_args[0][0].endswith("/schedules?start=2024-03-20&cloud=cloud1")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_current_schedules(self, mock_get):
        expected_response = {
            "schedules": [
                {"id": 1, "cloud": "cloud1", "start": "2024-03-20", "end": "2024-03-21"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_current_schedules()
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/schedules/current")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_current_schedules_with_params(self, mock_get):
        query_data = {"cloud": "cloud1"}
        expected_response = {
            "schedules": [
                {"id": 1, "cloud": "cloud1", "start": "2024-03-20", "end": "2024-03-21"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_current_schedules(query_data)
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/schedules/current?cloud=cloud1")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_schedules_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_schedules()

    @patch('requests.Session.get')
    def test_get_current_schedules_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_current_schedules()

    @patch('requests.Session.get')
    def test_get_schedule(self, mock_get):
        schedule_id = 123
        expected_response = {
            "id": 123,
            "cloud": "cloud1",
            "start": "2024-03-20",
            "end": "2024-03-21"
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_schedule(schedule_id)
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith(f"/schedules/{schedule_id}")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_future_schedules(self, mock_get):
        expected_response = {
            "schedules": [
                {"id": 1, "cloud": "cloud1", "start": "2024-03-20", "end": "2024-03-21"},
                {"id": 2, "cloud": "cloud2", "start": "2024-03-22", "end": "2024-03-23"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_future_schedules()
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/schedules/future")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_future_schedules_with_params(self, mock_get):
        query_data = {"cloud": "cloud1"}
        expected_response = {
            "schedules": [
                {"id": 1, "cloud": "cloud1", "start": "2024-03-20", "end": "2024-03-21"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_future_schedules(query_data)
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/schedules/future?cloud=cloud1")
        assert result == expected_response

    @patch('requests.Session.patch')
    def test_update_schedule(self, mock_patch):
        schedule_id = 123
        update_data = {
            "cloud": "new-cloud",
            "end": "2024-03-22"
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response
        
        result = self.api.update_schedule(schedule_id, update_data)
        
        mock_patch.assert_called_once()
        assert mock_patch.call_args[0][0].endswith(f"/schedules/{schedule_id}")
        assert mock_patch.call_args[1]["json"] == update_data
        assert result == mock_response

    @patch('requests.Session.delete')
    def test_remove_schedule(self, mock_delete):
        schedule_id = 123
        mock_response = Mock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        
        result = self.api.remove_schedule(schedule_id)
        
        mock_delete.assert_called_once()
        assert mock_delete.call_args[0][0].endswith(f"/schedules/{schedule_id}")
        assert result == mock_response

    @patch('requests.Session.get')
    def test_get_schedule_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_schedule(123)

    @patch('requests.Session.get')
    def test_get_future_schedules_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_future_schedules()

    @patch('requests.Session.patch')
    def test_update_schedule_error(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_patch.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.update_schedule(123, {"cloud": "new-cloud"})

    @patch('requests.Session.delete')
    def test_remove_schedule_error(self, mock_delete):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_delete.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.remove_schedule(123)

    @patch('requests.Session.post')
    def test_insert_schedule(self, mock_post):
        schedule_data = {
            "cloud": "cloud1",
            "start": "2024-03-20",
            "end": "2024-03-21"
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.api.insert_schedule(schedule_data)
        
        mock_post.assert_called_once()
        assert mock_post.call_args[0][0].endswith("/schedules")
        assert mock_post.call_args[1]["json"] == schedule_data
        assert result == mock_response

    @patch('requests.Session.get')
    def test_get_available(self, mock_get):
        expected_response = {
            "hosts": [
                {"name": "host1", "model": "model1"},
                {"name": "host2", "model": "model2"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_available()
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/available")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_filter_available(self, mock_get):
        filter_data = {
            "start_date": "2024-03-20",
            "end_date": "2024-03-21",
            "model": "model1"
        }
        expected_response = {
            "hosts": [{"name": "host1", "model": "model1"}]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.filter_available(filter_data)
        
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        assert "start_date=2024-03-20" in called_url
        assert "end_date=2024-03-21" in called_url
        assert "model=model1" in called_url
        assert result == expected_response

    @patch('requests.Session.post')
    def test_insert_assignment(self, mock_post):
        assignment_data = {
            "cloud": "cloud1",
            "host": "host1",
            "start": "2024-03-20",
            "end": "2024-03-21"
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.api.insert_assignment(assignment_data)
        
        mock_post.assert_called_once()
        assert mock_post.call_args[0][0].endswith("/assignments")
        assert mock_post.call_args[1]["json"] == assignment_data
        assert result == mock_response

    @patch('requests.Session.patch')
    def test_update_assignment(self, mock_patch):
        assignment_id = 123
        update_data = {
            "end": "2024-03-22",
            "status": "completed"
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response
        
        result = self.api.update_assignment(assignment_id, update_data)
        
        mock_patch.assert_called_once()
        assert mock_patch.call_args[0][0].endswith(f"/assignments/{assignment_id}")
        assert mock_patch.call_args[1]["json"] == update_data
        assert result == mock_response

    @patch('requests.Session.patch')
    def test_update_notification(self, mock_patch):
        notification_id = 456
        update_data = {
            "status": "read",
            "acknowledged": True
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response
        
        result = self.api.update_notification(notification_id, update_data)
        
        mock_patch.assert_called_once()
        assert mock_patch.call_args[0][0].endswith(f"/notifications/{notification_id}")
        assert mock_patch.call_args[1]["json"] == update_data
        assert result == mock_response

    @patch('requests.Session.post')
    def test_insert_schedule_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.insert_schedule({"cloud": "cloud1"})

    @patch('requests.Session.get')
    def test_get_available_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_available()

    @patch('requests.Session.post')
    def test_insert_assignment_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.insert_assignment({"cloud": "cloud1"})

    @patch('requests.Session.patch')
    def test_update_assignment_error(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_patch.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.update_assignment(123, {"status": "completed"})

    @patch('requests.Session.patch')
    def test_update_notification_error(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_patch.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.update_notification(456, {"status": "read"})

    @patch('requests.Session.get')
    def test_get_active_cloud_assignment(self, mock_get):
        cloud_name = "cloud1"
        expected_response = {
            "id": 123,
            "cloud": "cloud1",
            "host": "host1",
            "status": "active"
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_active_cloud_assignment(cloud_name)
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith(f"/assignments/active/{cloud_name}")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_active_assignments(self, mock_get):
        expected_response = {
            "assignments": [
                {"id": 1, "cloud": "cloud1", "host": "host1", "status": "active"},
                {"id": 2, "cloud": "cloud2", "host": "host2", "status": "active"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_active_assignments()
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/assignments/active")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_host_interface(self, mock_get):
        hostname = "host1"
        expected_response = {
            "interfaces": [
                {"name": "eth0", "mac_address": "00:11:22:33:44:55"},
                {"name": "eth1", "mac_address": "00:11:22:33:44:66"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_host_interface(hostname)
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith(f"/hosts/{hostname}/interfaces")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_interfaces(self, mock_get):
        expected_response = {
            "interfaces": [
                {"host": "host1", "name": "eth0", "mac_address": "00:11:22:33:44:55"},
                {"host": "host2", "name": "eth0", "mac_address": "00:11:22:33:44:66"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_interfaces()
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/interfaces")
        assert result == expected_response

    @patch('requests.Session.patch')
    def test_update_interface(self, mock_patch):
        hostname = "host1"
        update_data = {
            "name": "eth0",
            "mac_address": "00:11:22:33:44:77"
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response
        
        result = self.api.update_interface(hostname, update_data)
        
        mock_patch.assert_called_once()
        assert mock_patch.call_args[0][0].endswith(f"/interfaces/{hostname}")
        assert mock_patch.call_args[1]["json"] == update_data
        assert result == mock_response

    @patch('requests.Session.delete')
    def test_remove_interface(self, mock_delete):
        hostname = "host1"
        if_name = "eth0"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        
        result = self.api.remove_interface(hostname, if_name)
        
        mock_delete.assert_called_once()
        assert mock_delete.call_args[0][0].endswith(f"/interfaces/{hostname}/{if_name}")
        assert result == mock_response

    @patch('requests.Session.post')
    def test_create_interface(self, mock_post):
        hostname = "host1"
        interface_data = {
            "name": "eth0",
            "mac_address": "00:11:22:33:44:55",
            "switch_port": "Gi1/0/1"
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.api.create_interface(hostname, interface_data)
        
        mock_post.assert_called_once()
        assert mock_post.call_args[0][0].endswith(f"/interfaces/{hostname}")
        assert mock_post.call_args[1]["json"] == interface_data
        assert result == mock_response

    @patch('requests.Session.post')
    def test_create_memory(self, mock_post):
        hostname = "host1"
        memory_data = {
            "total": "64GB",
            "speed": "3200MHz"
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.api.create_memory(hostname, memory_data)
        
        mock_post.assert_called_once()
        assert mock_post.call_args[0][0].endswith(f"/memory/{hostname}")
        assert mock_post.call_args[1]["json"] == memory_data
        assert result == mock_response

    @patch('requests.Session.get')
    def test_get_active_cloud_assignment_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_active_cloud_assignment("cloud1")

    @patch('requests.Session.get')
    def test_get_host_interface_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_host_interface("host1")

    @patch('requests.Session.patch')
    def test_update_interface_error(self, mock_patch):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_patch.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.update_interface("host1", {"name": "eth0"})

    @patch('requests.Session.post')
    def test_create_interface_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.create_interface("host1", {"name": "eth0"})

    @patch('requests.Session.delete')
    def test_remove_memory(self, mock_delete):
        memory_id = "123"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        
        result = self.api.remove_memory(memory_id)
        
        mock_delete.assert_called_once()
        assert mock_delete.call_args[0][0].endswith(f"/memory/{memory_id}")
        assert result == mock_response

    @patch('requests.Session.post')
    def test_create_disk(self, mock_post):
        hostname = "host1"
        disk_data = {
            "name": "sda",
            "size": "1TB",
            "type": "SSD"
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.api.create_disk(hostname, disk_data)
        
        mock_post.assert_called_once()
        assert mock_post.call_args[0][0].endswith(f"/disks/{hostname}")
        assert mock_post.call_args[1]["json"] == disk_data
        assert result == mock_response

    @patch('requests.Session.patch')
    def test_update_disk(self, mock_patch):
        hostname = "host1"
        disk_data = {
            "name": "sda",
            "size": "2TB"
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response
        
        result = self.api.update_disk(hostname, disk_data)
        
        mock_patch.assert_called_once()
        assert mock_patch.call_args[0][0].endswith(f"/disks/{hostname}")
        assert mock_patch.call_args[1]["json"] == disk_data
        assert result == mock_response

    @patch('requests.Session.delete')
    def test_remove_disk(self, mock_delete):
        hostname = "host1"
        disk_id = "123"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        
        result = self.api.remove_disk(hostname, disk_id)
        
        mock_delete.assert_called_once()
        assert mock_delete.call_args[0][0].endswith(f"/disks/{hostname}/{disk_id}")
        assert result == mock_response

    @patch('requests.Session.post')
    def test_create_processor(self, mock_post):
        hostname = "host1"
        processor_data = {
            "model": "Intel Xeon",
            "cores": 32,
            "threads": 64
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.api.create_processor(hostname, processor_data)
        
        mock_post.assert_called_once()
        assert mock_post.call_args[0][0].endswith(f"/processors/{hostname}")
        assert mock_post.call_args[1]["json"] == processor_data
        assert result == mock_response

    @patch('requests.Session.delete')
    def test_remove_processor(self, mock_delete):
        processor_id = "123"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response
        
        result = self.api.remove_processor(processor_id)
        
        mock_delete.assert_called_once()
        assert mock_delete.call_args[0][0].endswith(f"/processors/{processor_id}")
        assert result == mock_response

    @patch('requests.Session.get')
    def test_get_vlans(self, mock_get):
        expected_response = {
            "vlans": [
                {"id": 100, "name": "prod", "description": "Production network"},
                {"id": 200, "name": "dev", "description": "Development network"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_vlans()
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/vlans")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_vlan(self, mock_get):
        vlan_id = 100
        expected_response = {
            "id": 100,
            "name": "prod",
            "description": "Production network"
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_vlan(vlan_id)
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith(f"/vlans/{vlan_id}")
        assert result == expected_response

    @patch('requests.Session.patch')
    def test_update_vlan(self, mock_patch):
        vlan_id = 100
        update_data = {
            "name": "prod-new",
            "description": "Updated production network"
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response
        
        result = self.api.update_vlan(vlan_id, update_data)
        
        mock_patch.assert_called_once()
        assert mock_patch.call_args[0][0].endswith(f"/vlans/{vlan_id}")
        assert mock_patch.call_args[1]["json"] == update_data
        assert result == mock_response

    @patch('requests.Session.post')
    def test_create_vlan(self, mock_post):
        vlan_data = {
            "id": 300,
            "name": "test",
            "description": "Test network"
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.api.create_vlan(vlan_data)
        
        mock_post.assert_called_once()
        assert mock_post.call_args[0][0].endswith("/vlans")
        assert mock_post.call_args[1]["json"] == vlan_data
        assert result == mock_response

    @patch('requests.Session.get')
    def test_get_moves(self, mock_get):
        expected_response = {
            "moves": [
                {"id": 1, "host": "host1", "from_cloud": "cloud1", "to_cloud": "cloud2"},
                {"id": 2, "host": "host2", "from_cloud": "cloud2", "to_cloud": "cloud3"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_moves()
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/moves")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_moves_with_date(self, mock_get):
        date = "2024-03-20"
        expected_response = {
            "moves": [
                {"id": 1, "host": "host1", "from_cloud": "cloud1", "to_cloud": "cloud2"}
            ]
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_moves(date)
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith(f"/moves?date={date}")
        assert result == expected_response

    @patch('requests.Session.get')
    def test_get_version(self, mock_get):
        expected_response = {
            "version": "1.0.0",
            "api_version": "2.0"
        }
        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_get.return_value = mock_response
        
        result = self.api.get_version()
        
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0].endswith("/version")
        assert result == expected_response

    @patch('requests.Session.delete')
    def test_remove_memory_error(self, mock_delete):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_delete.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.remove_memory("123")

    @patch('requests.Session.post')
    def test_create_disk_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.create_disk("host1", {"name": "sda"})

    @patch('requests.Session.get')
    def test_get_vlans_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_vlans()

    @patch('requests.Session.get')
    def test_get_version_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(APIServerException, match="Check the flask server logs"):
            self.api.get_version()