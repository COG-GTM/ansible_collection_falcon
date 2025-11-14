# Copyright: (c) 2023, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible_collections.crowdstrike.falcon.plugins.modules import intel_rule_download
from ansible_collections.crowdstrike.falcon.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
)

try:
    from unittest.mock import MagicMock, patch, mock_open
except ImportError:
    from mock import MagicMock, patch, mock_open


class TestIntelRuleDownloadModule:
    def test_download_latest_yara_rule(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "type": "yara-master",
                "dest": "/tmp/rules",
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
                        "name": "YARA Master Rule",
                        "type": "yara-master",
                    }
                ]
            },
        }
        mock_intel.get_latest_rule_file.return_value = b"rule content"

        with patch.object(intel_rule_download, "HAS_FALCONPY", True):
            with patch.object(
                intel_rule_download, "authenticate", return_value=mock_intel
            ):
                with patch.object(intel_rule_download, "handle_return_errors"):
                    with patch.object(intel_rule_download, "lock_file") as mock_lock:
                        with patch.object(intel_rule_download, "unlock_file"):
                            with patch.object(
                                intel_rule_download, "check_destination_path"
                            ):
                                with patch.object(
                                    intel_rule_download, "update_permissions"
                                ):
                                    with patch("builtins.open", mock_open()):
                                        with patch.object(
                                            intel_rule_download.os.path, "isfile", return_value=False
                                        ):
                                            mock_lock.return_value = MagicMock()
                                            with pytest.raises(AnsibleExitJson) as result:
                                                intel_rule_download.main()

        assert result.value.args[0]["changed"] is True
        assert "path" in result.value.args[0]
        assert result.value.args[0]["rule_id"] == "1234567890"

    def test_download_specific_rule_by_id(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "rule_id": "9876543210",
                "dest": "/tmp/rules",
            }
        )

        mock_intel = MagicMock()
        mock_intel.get_rule_entities.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "Specific Rule",
                        "type": "yara-master",
                    }
                ]
            },
        }
        mock_intel.get_rule_file.return_value = b"specific rule content"

        with patch.object(intel_rule_download, "HAS_FALCONPY", True):
            with patch.object(
                intel_rule_download, "authenticate", return_value=mock_intel
            ):
                with patch.object(intel_rule_download, "handle_return_errors"):
                    with patch.object(intel_rule_download, "lock_file") as mock_lock:
                        with patch.object(intel_rule_download, "unlock_file"):
                            with patch.object(
                                intel_rule_download, "check_destination_path"
                            ):
                                with patch.object(
                                    intel_rule_download, "update_permissions"
                                ):
                                    with patch("builtins.open", mock_open()):
                                        with patch.object(
                                            intel_rule_download.os.path, "isfile", return_value=False
                                        ):
                                            mock_lock.return_value = MagicMock()
                                            with pytest.raises(AnsibleExitJson) as result:
                                                intel_rule_download.main()

        assert result.value.args[0]["changed"] is True
        assert result.value.args[0]["rule_id"] == "9876543210"

    def test_missing_falconpy(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "type": "yara-master",
            }
        )

        with patch.object(intel_rule_download, "HAS_FALCONPY", False):
            with pytest.raises(AnsibleFailJson) as result:
                intel_rule_download.main()

        assert "falconpy" in result.value.args[0]["msg"]

    def test_check_mode(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "type": "yara-master",
                "dest": "/tmp/rules",
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
                        "name": "YARA Master Rule",
                        "type": "yara-master",
                    }
                ]
            },
        }

        with patch.object(intel_rule_download, "HAS_FALCONPY", True):
            with patch.object(
                intel_rule_download, "authenticate", return_value=mock_intel
            ):
                with patch.object(intel_rule_download, "handle_return_errors"):
                    with patch.object(intel_rule_download, "lock_file") as mock_lock:
                        with patch.object(intel_rule_download, "unlock_file"):
                            with patch.object(
                                intel_rule_download, "check_destination_path"
                            ):
                                with patch.object(
                                    intel_rule_download.os.path, "isfile", return_value=False
                                ):
                                    mock_lock.return_value = MagicMock()
                                    with pytest.raises(AnsibleExitJson) as result:
                                        intel_rule_download.main()

        assert result.value.args[0]["changed"] is True

    def test_file_already_exists(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "type": "yara-master",
                "dest": "/tmp/rules",
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
                        "name": "YARA Master Rule",
                        "type": "yara-master",
                    }
                ]
            },
        }

        with patch.object(intel_rule_download, "HAS_FALCONPY", True):
            with patch.object(
                intel_rule_download, "authenticate", return_value=mock_intel
            ):
                with patch.object(intel_rule_download, "handle_return_errors"):
                    with patch.object(intel_rule_download, "lock_file") as mock_lock:
                        with patch.object(intel_rule_download, "unlock_file"):
                            with patch.object(
                                intel_rule_download, "check_destination_path"
                            ):
                                with patch.object(
                                    intel_rule_download, "update_permissions", return_value=False
                                ):
                                    with patch.object(
                                        intel_rule_download.os.path, "isfile", return_value=True
                                    ):
                                        mock_lock.return_value = MagicMock()
                                        with pytest.raises(AnsibleExitJson) as result:
                                            intel_rule_download.main()

        assert result.value.args[0]["changed"] is False
