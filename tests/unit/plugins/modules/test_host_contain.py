# Copyright: (c) 2023, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible_collections.crowdstrike.falcon.plugins.modules import host_contain
from ansible_collections.crowdstrike.falcon.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
)

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestHostContainModule:
    def test_contain_single_host_success(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1"],
                "contained": True,
            }
        )

        mock_hosts = MagicMock()
        mock_hosts.perform_action.return_value = {
            "status_code": 200,
            "body": {
                "resources": [{"id": "test_aid_1"}],
                "errors": [],
            },
        }

        with patch.object(host_contain, "HAS_FALCONPY", True):
            with patch.object(host_contain, "authenticate", return_value=mock_hosts):
                with pytest.raises(AnsibleExitJson) as result:
                    host_contain.main()

        assert result.value.args[0]["changed"] is True
        assert "test_aid_1" in result.value.args[0]["hosts"]
        assert len(result.value.args[0]["failed_hosts"]) == 0
        mock_hosts.perform_action.assert_called_once_with(
            action_name="contain", ids=["test_aid_1"]
        )

    def test_lift_containment_success(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1", "test_aid_2"],
                "contained": False,
            }
        )

        mock_hosts = MagicMock()
        mock_hosts.perform_action.return_value = {
            "status_code": 200,
            "body": {
                "resources": [{"id": "test_aid_1"}, {"id": "test_aid_2"}],
                "errors": [],
            },
        }

        with patch.object(host_contain, "HAS_FALCONPY", True):
            with patch.object(host_contain, "authenticate", return_value=mock_hosts):
                with pytest.raises(AnsibleExitJson) as result:
                    host_contain.main()

        assert result.value.args[0]["changed"] is True
        assert "test_aid_1" in result.value.args[0]["hosts"]
        assert "test_aid_2" in result.value.args[0]["hosts"]
        assert len(result.value.args[0]["failed_hosts"]) == 0
        mock_hosts.perform_action.assert_called_once_with(
            action_name="lift_containment", ids=["test_aid_1", "test_aid_2"]
        )

    def test_contain_host_already_contained(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1"],
                "contained": True,
            }
        )

        mock_hosts = MagicMock()
        mock_hosts.perform_action.return_value = {
            "status_code": 200,
            "body": {
                "resources": [],
                "errors": [
                    {
                        "code": 409,
                        "message": "Host test_aid_1 is already contained",
                    }
                ],
            },
        }

        with patch.object(host_contain, "HAS_FALCONPY", True):
            with patch.object(host_contain, "authenticate", return_value=mock_hosts):
                with pytest.raises(AnsibleExitJson) as result:
                    host_contain.main()

        assert result.value.args[0]["changed"] is False
        assert "test_aid_1" in result.value.args[0]["hosts"]
        assert len(result.value.args[0]["failed_hosts"]) == 0

    def test_contain_host_failure(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1"],
                "contained": True,
            }
        )

        mock_hosts = MagicMock()
        mock_hosts.perform_action.return_value = {
            "status_code": 200,
            "body": {
                "resources": [],
                "errors": [
                    {
                        "code": 404,
                        "message": "Host test_aid_1 not found",
                    }
                ],
            },
        }

        with patch.object(host_contain, "HAS_FALCONPY", True):
            with patch.object(host_contain, "authenticate", return_value=mock_hosts):
                with pytest.raises(AnsibleExitJson) as result:
                    host_contain.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["hosts"]) == 0
        assert len(result.value.args[0]["failed_hosts"]) == 1
        assert result.value.args[0]["failed_hosts"][0]["id"] == "test_aid_1"
        assert result.value.args[0]["failed_hosts"][0]["code"] == 404

    def test_contain_multiple_hosts_partial_success(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1", "test_aid_2"],
                "contained": True,
            }
        )

        mock_hosts = MagicMock()
        mock_hosts.perform_action.return_value = {
            "status_code": 200,
            "body": {
                "resources": [{"id": "test_aid_1"}],
                "errors": [
                    {
                        "code": 404,
                        "message": "Host test_aid_2 not found",
                    }
                ],
            },
        }

        with patch.object(host_contain, "HAS_FALCONPY", True):
            with patch.object(host_contain, "authenticate", return_value=mock_hosts):
                with pytest.raises(AnsibleExitJson) as result:
                    host_contain.main()

        assert result.value.args[0]["changed"] is True
        assert "test_aid_1" in result.value.args[0]["hosts"]
        assert len(result.value.args[0]["failed_hosts"]) == 1
        assert result.value.args[0]["failed_hosts"][0]["id"] == "test_aid_2"

    def test_missing_falconpy(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1"],
            }
        )

        with patch.object(host_contain, "HAS_FALCONPY", False):
            with pytest.raises(AnsibleFailJson) as result:
                host_contain.main()

        assert "falconpy" in result.value.args[0]["msg"]

    def test_check_mode(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1"],
                "_ansible_check_mode": True,
            }
        )

        with patch.object(host_contain, "HAS_FALCONPY", True):
            with pytest.raises(AnsibleExitJson) as result:
                host_contain.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["hosts"]) == 0
        assert len(result.value.args[0]["failed_hosts"]) == 0

    def test_no_response_error_handling(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1"],
                "contained": True,
            }
        )

        mock_hosts = MagicMock()
        mock_hosts.perform_action.return_value = {
            "status_code": 500,
            "body": {
                "resources": [],
                "errors": [],
            },
        }

        with patch.object(host_contain, "HAS_FALCONPY", True):
            with patch.object(host_contain, "authenticate", return_value=mock_hosts):
                with patch.object(host_contain, "handle_return_errors") as mock_handle:
                    mock_handle.side_effect = AnsibleFailJson(
                        {"msg": "Internal Server Error"}
                    )
                    with pytest.raises(AnsibleFailJson):
                        host_contain.main()
