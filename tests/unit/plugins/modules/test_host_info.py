#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible_collections.crowdstrike.falcon.plugins.modules import host_info
from ansible_collections.crowdstrike.falcon.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
)

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestHostInfoModule:
    def test_get_single_host_info(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1"],
            }
        )

        mock_hosts = MagicMock()
        mock_hosts.get_device_details.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "device_id": "test_aid_1",
                        "hostname": "test-host-1",
                        "platform_name": "Linux",
                        "os_version": "Ubuntu 22.04",
                    }
                ],
            },
        }

        with patch.object(host_info, "HAS_FALCONPY", True):
            with patch.object(host_info, "authenticate", return_value=mock_hosts):
                with patch.object(host_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        host_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["hosts"]) == 1
        assert result.value.args[0]["hosts"][0]["device_id"] == "test_aid_1"
        assert result.value.args[0]["hosts"][0]["hostname"] == "test-host-1"
        mock_hosts.get_device_details.assert_called_once_with(ids=["test_aid_1"])

    def test_get_multiple_hosts_info(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1", "test_aid_2"],
            }
        )

        mock_hosts = MagicMock()
        mock_hosts.get_device_details.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "device_id": "test_aid_1",
                        "hostname": "test-host-1",
                        "platform_name": "Linux",
                    },
                    {
                        "device_id": "test_aid_2",
                        "hostname": "test-host-2",
                        "platform_name": "Windows",
                    },
                ],
            },
        }

        with patch.object(host_info, "HAS_FALCONPY", True):
            with patch.object(host_info, "authenticate", return_value=mock_hosts):
                with patch.object(host_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        host_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["hosts"]) == 2
        assert result.value.args[0]["hosts"][0]["device_id"] == "test_aid_1"
        assert result.value.args[0]["hosts"][1]["device_id"] == "test_aid_2"

    def test_get_hosts_batch_processing(self, monkeypatch):
        hosts_list = [f"test_aid_{i}" for i in range(6000)]
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": hosts_list,
            }
        )

        mock_hosts = MagicMock()
        mock_hosts.get_device_details.return_value = {
            "status_code": 200,
            "body": {
                "resources": [{"device_id": aid} for aid in hosts_list[:5000]],
            },
        }

        with patch.object(host_info, "HAS_FALCONPY", True):
            with patch.object(host_info, "authenticate", return_value=mock_hosts):
                with patch.object(host_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        host_info.main()

        assert result.value.args[0]["changed"] is False
        assert mock_hosts.get_device_details.call_count == 2

    def test_missing_falconpy(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1"],
            }
        )

        with patch.object(host_info, "HAS_FALCONPY", False):
            with pytest.raises(AnsibleFailJson) as result:
                host_info.main()

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

        mock_hosts = MagicMock()
        mock_hosts.get_device_details.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "device_id": "test_aid_1",
                        "hostname": "test-host-1",
                    }
                ],
            },
        }

        with patch.object(host_info, "HAS_FALCONPY", True):
            with patch.object(host_info, "authenticate", return_value=mock_hosts):
                with patch.object(host_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        host_info.main()

        assert result.value.args[0]["changed"] is False

    def test_api_error(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1"],
            }
        )

        mock_hosts = MagicMock()
        mock_hosts.get_device_details.return_value = {
            "status_code": 403,
            "body": {
                "errors": [{"message": "Forbidden"}],
            },
        }

        with patch.object(host_info, "HAS_FALCONPY", True):
            with patch.object(host_info, "authenticate", return_value=mock_hosts):
                with patch.object(host_info, "handle_return_errors") as mock_handle:
                    mock_handle.side_effect = AnsibleFailJson({"msg": "Forbidden"})
                    with pytest.raises(AnsibleFailJson):
                        host_info.main()
