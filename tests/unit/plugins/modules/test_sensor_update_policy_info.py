# Copyright: (c) 2023, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible_collections.crowdstrike.falcon.plugins.modules import sensor_update_policy_info
from ansible_collections.crowdstrike.falcon.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
)

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestSensorUpdatePolicyInfoModule:
    def test_get_all_policies(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
            }
        )

        mock_result = {
            "changed": False,
            "policies": [
                {
                    "id": "d78cd791785442a98ec75249d8c385dd",
                    "name": "Windows 10 Sensor Policy",
                    "platform_name": "Windows",
                    "enabled": True,
                },
                {
                    "id": "e89de802896553b09fd86350e9d496ee",
                    "name": "Linux Sensor Policy",
                    "platform_name": "Linux",
                    "enabled": True,
                },
            ],
        }

        with patch.object(sensor_update_policy_info, "HAS_FALCONPY", True):
            with patch.object(sensor_update_policy_info, "authenticate"):
                with patch.object(
                    sensor_update_policy_info, "get_paginated_results_info", return_value=mock_result
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        sensor_update_policy_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["policies"]) == 2
        assert result.value.args[0]["policies"][0]["name"] == "Windows 10 Sensor Policy"

    def test_get_policies_with_filter(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "filter": "platform_name:'Windows'+enabled:'true'",
            }
        )

        mock_result = {
            "changed": False,
            "policies": [
                {
                    "id": "d78cd791785442a98ec75249d8c385dd",
                    "name": "Windows 10 Sensor Policy",
                    "platform_name": "Windows",
                    "enabled": True,
                }
            ],
        }

        with patch.object(sensor_update_policy_info, "HAS_FALCONPY", True):
            with patch.object(sensor_update_policy_info, "authenticate"):
                with patch.object(
                    sensor_update_policy_info, "get_paginated_results_info", return_value=mock_result
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        sensor_update_policy_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["policies"]) == 1
        assert result.value.args[0]["policies"][0]["platform_name"] == "Windows"

    def test_get_policies_with_sort(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "sort": "platform_name.asc",
            }
        )

        mock_result = {
            "changed": False,
            "policies": [
                {
                    "id": "e89de802896553b09fd86350e9d496ee",
                    "name": "Linux Sensor Policy",
                    "platform_name": "Linux",
                },
                {
                    "id": "d78cd791785442a98ec75249d8c385dd",
                    "name": "Windows 10 Sensor Policy",
                    "platform_name": "Windows",
                },
            ],
        }

        with patch.object(sensor_update_policy_info, "HAS_FALCONPY", True):
            with patch.object(sensor_update_policy_info, "authenticate"):
                with patch.object(
                    sensor_update_policy_info, "get_paginated_results_info", return_value=mock_result
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        sensor_update_policy_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["policies"]) == 2

    def test_missing_falconpy(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
            }
        )

        with patch.object(sensor_update_policy_info, "HAS_FALCONPY", False):
            with pytest.raises(AnsibleFailJson) as result:
                sensor_update_policy_info.main()

        assert "falconpy" in result.value.args[0]["msg"]

    def test_check_mode(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "_ansible_check_mode": True,
            }
        )

        mock_result = {
            "changed": False,
            "policies": [
                {
                    "id": "d78cd791785442a98ec75249d8c385dd",
                    "name": "Windows 10 Sensor Policy",
                }
            ],
        }

        with patch.object(sensor_update_policy_info, "HAS_FALCONPY", True):
            with patch.object(sensor_update_policy_info, "authenticate"):
                with patch.object(
                    sensor_update_policy_info, "get_paginated_results_info", return_value=mock_result
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        sensor_update_policy_info.main()

        assert result.value.args[0]["changed"] is False

    def test_empty_results(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "filter": "platform_name:'NonExistent'",
            }
        )

        mock_result = {
            "changed": False,
            "policies": [],
        }

        with patch.object(sensor_update_policy_info, "HAS_FALCONPY", True):
            with patch.object(sensor_update_policy_info, "authenticate"):
                with patch.object(
                    sensor_update_policy_info, "get_paginated_results_info", return_value=mock_result
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        sensor_update_policy_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["policies"]) == 0
