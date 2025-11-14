#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible_collections.crowdstrike.falcon.plugins.modules import intel_rule_info
from ansible_collections.crowdstrike.falcon.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
)

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestIntelRuleInfoModule:
    def test_get_yara_rules(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "type": "yara-master",
            }
        )

        mock_intel = MagicMock()
        mock_intel.query_rule_ids.return_value = {
            "status_code": 200,
            "body": {"resources": ["1234567890", "0987654321"]},
        }
        mock_intel.get_rule_entities.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": 1234567890,
                        "name": "YARA Rule 1",
                        "type": "yara-master",
                        "created_date": 1745576262,
                    },
                    {
                        "id": 987654321,
                        "name": "YARA Rule 2",
                        "type": "yara-master",
                        "created_date": 1745576263,
                    },
                ]
            },
        }

        with patch.object(intel_rule_info, "HAS_FALCONPY", True):
            with patch.object(
                intel_rule_info, "authenticate", return_value=mock_intel
            ):
                with patch.object(intel_rule_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        intel_rule_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["rules"]) == 2
        assert result.value.args[0]["rules"][0]["name"] == "YARA Rule 1"

    def test_get_rules_with_filter(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "type": "snort-suricata-master",
                "description": ["FANCY BEAR"],
            }
        )

        mock_intel = MagicMock()
        mock_intel.query_rule_ids.return_value = {
            "status_code": 200,
            "body": {"resources": ["1234567890"]},
        }
        mock_intel.get_rule_entities.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": 1234567890,
                        "name": "Snort Rule",
                        "type": "snort-suricata-master",
                        "description": "FANCY BEAR activity",
                    }
                ]
            },
        }

        with patch.object(intel_rule_info, "HAS_FALCONPY", True):
            with patch.object(
                intel_rule_info, "authenticate", return_value=mock_intel
            ):
                with patch.object(intel_rule_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        intel_rule_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["rules"]) == 1

    def test_get_rules_with_sort(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "type": "yara-master",
                "sort": "created_date|desc",
            }
        )

        mock_intel = MagicMock()
        mock_intel.query_rule_ids.return_value = {
            "status_code": 200,
            "body": {"resources": ["1234567890"]},
        }
        mock_intel.get_rule_entities.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": 1234567890,
                        "name": "Latest YARA Rule",
                        "type": "yara-master",
                    }
                ]
            },
        }

        with patch.object(intel_rule_info, "HAS_FALCONPY", True):
            with patch.object(
                intel_rule_info, "authenticate", return_value=mock_intel
            ):
                with patch.object(intel_rule_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        intel_rule_info.main()

        assert result.value.args[0]["changed"] is False

    def test_get_rules_with_limit(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "type": "yara-master",
                "limit": 50,
            }
        )

        mock_intel = MagicMock()
        mock_intel.query_rule_ids.return_value = {
            "status_code": 200,
            "body": {"resources": ["1234567890"]},
        }
        mock_intel.get_rule_entities.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": 1234567890,
                        "name": "YARA Rule",
                        "type": "yara-master",
                    }
                ]
            },
        }

        with patch.object(intel_rule_info, "HAS_FALCONPY", True):
            with patch.object(
                intel_rule_info, "authenticate", return_value=mock_intel
            ):
                with patch.object(intel_rule_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        intel_rule_info.main()

        assert result.value.args[0]["changed"] is False

    def test_missing_falconpy(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "type": "yara-master",
            }
        )

        with patch.object(intel_rule_info, "HAS_FALCONPY", False):
            with pytest.raises(AnsibleFailJson) as result:
                intel_rule_info.main()

        assert "falconpy" in result.value.args[0]["msg"]

    def test_check_mode(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "type": "yara-master",
                "_ansible_check_mode": True,
            }
        )

        mock_intel = MagicMock()
        mock_intel.query_rule_ids.return_value = {
            "status_code": 200,
            "body": {"resources": ["1234567890"]},
        }
        mock_intel.get_rule_entities.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "id": 1234567890,
                        "name": "YARA Rule",
                        "type": "yara-master",
                    }
                ]
            },
        }

        with patch.object(intel_rule_info, "HAS_FALCONPY", True):
            with patch.object(
                intel_rule_info, "authenticate", return_value=mock_intel
            ):
                with patch.object(intel_rule_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        intel_rule_info.main()

        assert result.value.args[0]["changed"] is False

    def test_empty_results(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "type": "yara-master",
            }
        )

        mock_intel = MagicMock()
        mock_intel.query_rule_ids.return_value = {
            "status_code": 200,
            "body": {"resources": []},
        }

        with patch.object(intel_rule_info, "HAS_FALCONPY", True):
            with patch.object(
                intel_rule_info, "authenticate", return_value=mock_intel
            ):
                with patch.object(intel_rule_info, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        intel_rule_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["rules"]) == 0
