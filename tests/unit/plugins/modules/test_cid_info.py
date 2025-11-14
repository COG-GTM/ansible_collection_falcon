#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible_collections.crowdstrike.falcon.plugins.modules import cid_info
from ansible_collections.crowdstrike.falcon.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
)

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestCidInfoModule:
    def test_get_cid_success(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
            }
        )

        mock_sensor_download = MagicMock()
        mock_sensor_download.get_sensor_installer_ccid.return_value = {
            "status_code": 200,
            "body": {"resources": ["1234567890ABCDEF1234567890ABCDEF-12"]},
        }

        with patch.object(cid_info, "HAS_FALCONPY", True):
            with patch.object(
                cid_info, "authenticate", return_value=mock_sensor_download
            ):
                with patch.object(cid_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        cid_info.main()

        assert result.value.args[0]["changed"] is False
        assert result.value.args[0]["cid"] == "1234567890ABCDEF1234567890ABCDEF-12"
        mock_sensor_download.get_sensor_installer_ccid.assert_called_once()

    def test_get_cid_failure(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
            }
        )

        mock_sensor_download = MagicMock()
        mock_sensor_download.get_sensor_installer_ccid.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "Forbidden"}]},
        }

        with patch.object(cid_info, "HAS_FALCONPY", True):
            with patch.object(
                cid_info, "authenticate", return_value=mock_sensor_download
            ):
                with patch.object(cid_info, "handle_return_errors") as mock_handle:
                    mock_handle.side_effect = AnsibleFailJson({"msg": "Forbidden"})
                    with pytest.raises(AnsibleFailJson):
                        cid_info.main()

    def test_missing_falconpy(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
            }
        )

        with patch.object(cid_info, "HAS_FALCONPY", False):
            with pytest.raises(AnsibleFailJson) as result:
                cid_info.main()

        assert "falconpy" in result.value.args[0]["msg"]

    def test_check_mode(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "_ansible_check_mode": True,
            }
        )

        mock_sensor_download = MagicMock()

        with patch.object(cid_info, "HAS_FALCONPY", True):
            with patch.object(
                cid_info, "authenticate", return_value=mock_sensor_download
            ):
                with pytest.raises(AnsibleExitJson) as result:
                    cid_info.main()

        assert result.value.args[0]["changed"] is False
        mock_sensor_download.get_sensor_installer_ccid.assert_called_once()
