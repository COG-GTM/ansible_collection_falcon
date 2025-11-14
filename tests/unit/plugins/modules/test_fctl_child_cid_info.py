# Copyright: (c) 2024, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible_collections.crowdstrike.falcon.plugins.modules import fctl_child_cid_info
from ansible_collections.crowdstrike.falcon.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
)

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestFctlChildCidInfoModule:
    def test_get_single_child_cid(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "cids": ["12345678901234567890"],
            }
        )

        mock_flight_control = MagicMock()
        mock_flight_control.override.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "child_cid": "12345678901234567890",
                        "child_gcid": "g12345678901234567890",
                        "child_of": "09876543210987654321",
                        "name": "Flight Control Child 1",
                        "checksum": "xy",
                        "domains": ["example.com"],
                        "status": "active",
                    }
                ],
            },
        }

        with patch.object(fctl_child_cid_info, "HAS_FALCONPY", True):
            with patch.object(
                fctl_child_cid_info, "authenticate", return_value=mock_flight_control
            ):
                with patch.object(fctl_child_cid_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        fctl_child_cid_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["child_cids"]) == 1
        assert result.value.args[0]["child_cids"][0]["child_cid"] == "12345678901234567890"
        assert result.value.args[0]["child_cids"][0]["name"] == "Flight Control Child 1"

    def test_get_multiple_child_cids(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "cids": ["12345678901234567890", "09876543210987654321"],
            }
        )

        mock_flight_control = MagicMock()
        mock_flight_control.override.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "child_cid": "12345678901234567890",
                        "name": "Flight Control Child 1",
                        "status": "active",
                    },
                    {
                        "child_cid": "09876543210987654321",
                        "name": "Flight Control Child 2",
                        "status": "active",
                    },
                ],
            },
        }

        with patch.object(fctl_child_cid_info, "HAS_FALCONPY", True):
            with patch.object(
                fctl_child_cid_info, "authenticate", return_value=mock_flight_control
            ):
                with patch.object(fctl_child_cid_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        fctl_child_cid_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["child_cids"]) == 2

    def test_missing_falconpy(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "cids": ["12345678901234567890"],
            }
        )

        with patch.object(fctl_child_cid_info, "HAS_FALCONPY", False):
            with pytest.raises(AnsibleFailJson) as result:
                fctl_child_cid_info.main()

        assert "falconpy" in result.value.args[0]["msg"]

    def test_check_mode(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "cids": ["12345678901234567890"],
                "_ansible_check_mode": True,
            }
        )

        mock_flight_control = MagicMock()
        mock_flight_control.override.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "child_cid": "12345678901234567890",
                        "name": "Flight Control Child 1",
                    }
                ],
            },
        }

        with patch.object(fctl_child_cid_info, "HAS_FALCONPY", True):
            with patch.object(
                fctl_child_cid_info, "authenticate", return_value=mock_flight_control
            ):
                with patch.object(fctl_child_cid_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        fctl_child_cid_info.main()

        assert result.value.args[0]["changed"] is False

    def test_api_error(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "cids": ["12345678901234567890"],
            }
        )

        mock_flight_control = MagicMock()
        mock_flight_control.override.return_value = {
            "status_code": 403,
            "body": {
                "errors": [{"message": "Forbidden"}],
            },
        }

        with patch.object(fctl_child_cid_info, "HAS_FALCONPY", True):
            with patch.object(
                fctl_child_cid_info, "authenticate", return_value=mock_flight_control
            ):
                with patch.object(
                    fctl_child_cid_info, "handle_return_errors"
                ) as mock_handle:
                    mock_handle.side_effect = AnsibleFailJson({"msg": "Forbidden"})
                    with pytest.raises(AnsibleFailJson):
                        fctl_child_cid_info.main()

    def test_empty_resources(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "cids": ["nonexistent"],
            }
        )

        mock_flight_control = MagicMock()
        mock_flight_control.override.return_value = {
            "status_code": 200,
            "body": {
                "resources": [],
            },
        }

        with patch.object(fctl_child_cid_info, "HAS_FALCONPY", True):
            with patch.object(
                fctl_child_cid_info, "authenticate", return_value=mock_flight_control
            ):
                with patch.object(fctl_child_cid_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        fctl_child_cid_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["child_cids"]) == 0
