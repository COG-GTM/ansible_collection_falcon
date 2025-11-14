#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible_collections.crowdstrike.falcon.plugins.modules import sensor_download_info
from ansible_collections.crowdstrike.falcon.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
)

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestSensorDownloadInfoModule:
    def test_get_all_installers(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
            }
        )

        mock_sensor_download = MagicMock()
        mock_sensor_download.override.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "falcon-sensor.deb",
                        "platform": "linux",
                        "version": "7.10.0",
                        "sha256": "1234567890abcdef",
                    },
                    {
                        "name": "falcon-sensor.rpm",
                        "platform": "linux",
                        "version": "7.10.0",
                        "sha256": "abcdef1234567890",
                    },
                ],
            },
        }

        with patch.object(sensor_download_info, "HAS_FALCONPY", True):
            with patch.object(
                sensor_download_info, "authenticate", return_value=mock_sensor_download
            ):
                with patch.object(sensor_download_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        sensor_download_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["installers"]) == 2
        assert result.value.args[0]["installers"][0]["name"] == "falcon-sensor.deb"
        assert result.value.args[0]["installers"][1]["name"] == "falcon-sensor.rpm"

    def test_get_installers_with_filter(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "filter": "platform:'linux'",
            }
        )

        mock_sensor_download = MagicMock()
        mock_sensor_download.override.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "falcon-sensor.deb",
                        "platform": "linux",
                        "version": "7.10.0",
                    }
                ],
            },
        }

        with patch.object(sensor_download_info, "HAS_FALCONPY", True):
            with patch.object(
                sensor_download_info, "authenticate", return_value=mock_sensor_download
            ):
                with patch.object(sensor_download_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        sensor_download_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["installers"]) == 1
        assert result.value.args[0]["installers"][0]["platform"] == "linux"
        mock_sensor_download.override.assert_called_once()

    def test_get_installers_with_sort(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "sort": "version|desc",
            }
        )

        mock_sensor_download = MagicMock()
        mock_sensor_download.override.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "falcon-sensor-new.deb",
                        "version": "7.11.0",
                    },
                    {
                        "name": "falcon-sensor-old.deb",
                        "version": "7.10.0",
                    },
                ],
            },
        }

        with patch.object(sensor_download_info, "HAS_FALCONPY", True):
            with patch.object(
                sensor_download_info, "authenticate", return_value=mock_sensor_download
            ):
                with patch.object(sensor_download_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        sensor_download_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["installers"]) == 2

    def test_get_installers_with_filter_and_sort(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "filter": "platform:'windows'",
                "sort": "version|desc",
            }
        )

        mock_sensor_download = MagicMock()
        mock_sensor_download.override.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "falcon-sensor.exe",
                        "platform": "windows",
                        "version": "7.11.0",
                    }
                ],
            },
        }

        with patch.object(sensor_download_info, "HAS_FALCONPY", True):
            with patch.object(
                sensor_download_info, "authenticate", return_value=mock_sensor_download
            ):
                with patch.object(sensor_download_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        sensor_download_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["installers"]) == 1
        assert result.value.args[0]["installers"][0]["platform"] == "windows"

    def test_missing_falconpy(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
            }
        )

        with patch.object(sensor_download_info, "HAS_FALCONPY", False):
            with pytest.raises(AnsibleFailJson) as result:
                sensor_download_info.main()

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
        mock_sensor_download.override.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "falcon-sensor.deb",
                        "platform": "linux",
                    }
                ],
            },
        }

        with patch.object(sensor_download_info, "HAS_FALCONPY", True):
            with patch.object(
                sensor_download_info, "authenticate", return_value=mock_sensor_download
            ):
                with patch.object(sensor_download_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        sensor_download_info.main()

        assert result.value.args[0]["changed"] is False

    def test_api_error(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
            }
        )

        mock_sensor_download = MagicMock()
        mock_sensor_download.override.return_value = {
            "status_code": 403,
            "body": {
                "errors": [{"message": "Forbidden"}],
            },
        }

        with patch.object(sensor_download_info, "HAS_FALCONPY", True):
            with patch.object(
                sensor_download_info, "authenticate", return_value=mock_sensor_download
            ):
                with patch.object(
                    sensor_download_info, "handle_return_errors"
                ) as mock_handle:
                    mock_handle.side_effect = AnsibleFailJson({"msg": "Forbidden"})
                    with pytest.raises(AnsibleFailJson):
                        sensor_download_info.main()
