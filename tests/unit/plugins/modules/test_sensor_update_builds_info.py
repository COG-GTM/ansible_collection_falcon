#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible_collections.crowdstrike.falcon.plugins.modules import sensor_update_builds_info
from ansible_collections.crowdstrike.falcon.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
)

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestSensorUpdateBuildsInfoModule:
    def test_get_all_builds(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
            }
        )

        mock_sensor_update_policy = MagicMock()
        mock_sensor_update_policy.query_combined_builds.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "build": "16410|n|tagged|11",
                        "platform": "Windows",
                        "sensor_version": "6.49.16303",
                        "stage": "prod",
                    },
                    {
                        "build": "16411|n|tagged|12",
                        "platform": "Linux",
                        "sensor_version": "6.49.16304",
                        "stage": "prod",
                    },
                ]
            },
        }

        with patch.object(sensor_update_builds_info, "HAS_FALCONPY", True):
            with patch.object(
                sensor_update_builds_info, "authenticate", return_value=mock_sensor_update_policy
            ):
                with patch.object(sensor_update_builds_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        sensor_update_builds_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["builds"]) == 2
        assert result.value.args[0]["builds"][0]["platform"] == "Windows"

    def test_get_builds_for_platform(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "platform": "windows",
            }
        )

        mock_sensor_update_policy = MagicMock()
        mock_sensor_update_policy.query_combined_builds.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "build": "16410|n|tagged|11",
                        "platform": "Windows",
                        "sensor_version": "6.49.16303",
                        "stage": "prod",
                    }
                ]
            },
        }

        with patch.object(sensor_update_builds_info, "HAS_FALCONPY", True):
            with patch.object(
                sensor_update_builds_info, "authenticate", return_value=mock_sensor_update_policy
            ):
                with patch.object(sensor_update_builds_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        sensor_update_builds_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["builds"]) == 1
        assert result.value.args[0]["builds"][0]["platform"] == "Windows"

    def test_get_builds_for_stage(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "stage": "early_adopter",
            }
        )

        mock_sensor_update_policy = MagicMock()
        mock_sensor_update_policy.query_combined_builds.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "build": "16412|n|tagged|13",
                        "platform": "Linux",
                        "sensor_version": "6.50.16305",
                        "stage": "early_adopter",
                    }
                ]
            },
        }

        with patch.object(sensor_update_builds_info, "HAS_FALCONPY", True):
            with patch.object(
                sensor_update_builds_info, "authenticate", return_value=mock_sensor_update_policy
            ):
                with patch.object(sensor_update_builds_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        sensor_update_builds_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["builds"]) == 1
        assert result.value.args[0]["builds"][0]["stage"] == "early_adopter"

    def test_missing_falconpy(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
            }
        )

        with patch.object(sensor_update_builds_info, "HAS_FALCONPY", False):
            with pytest.raises(AnsibleFailJson) as result:
                sensor_update_builds_info.main()

        assert "falconpy" in result.value.args[0]["msg"]

    def test_check_mode(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "_ansible_check_mode": True,
            }
        )

        mock_sensor_update_policy = MagicMock()
        mock_sensor_update_policy.query_combined_builds.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "build": "16410|n|tagged|11",
                        "platform": "Windows",
                    }
                ]
            },
        }

        with patch.object(sensor_update_builds_info, "HAS_FALCONPY", True):
            with patch.object(
                sensor_update_builds_info, "authenticate", return_value=mock_sensor_update_policy
            ):
                with patch.object(sensor_update_builds_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        sensor_update_builds_info.main()

        assert result.value.args[0]["changed"] is False

    def test_api_error(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
            }
        )

        mock_sensor_update_policy = MagicMock()
        mock_sensor_update_policy.query_combined_builds.return_value = {
            "status_code": 403,
            "body": {
                "errors": [{"message": "Forbidden"}],
            },
        }

        with patch.object(sensor_update_builds_info, "HAS_FALCONPY", True):
            with patch.object(
                sensor_update_builds_info, "authenticate", return_value=mock_sensor_update_policy
            ):
                with patch.object(
                    sensor_update_builds_info, "handle_return_errors"
                ) as mock_handle:
                    mock_handle.side_effect = AnsibleFailJson({"msg": "Forbidden"})
                    with pytest.raises(AnsibleFailJson):
                        sensor_update_builds_info.main()
