#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible_collections.crowdstrike.falcon.plugins.modules import host_hide
from ansible_collections.crowdstrike.falcon.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
)

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestHostHideModule:
    def test_hide_single_host_success(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1"],
                "hidden": True,
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

        with patch.object(host_hide, "HAS_FALCONPY", True):
            with patch.object(host_hide, "authenticate", return_value=mock_hosts):
                with pytest.raises(AnsibleExitJson) as result:
                    host_hide.main()

        assert result.value.args[0]["changed"] is True
        assert "test_aid_1" in result.value.args[0]["hosts"]
        assert len(result.value.args[0]["failed_hosts"]) == 0
        mock_hosts.perform_action.assert_called_once_with(
            action_name="hide_host", ids=["test_aid_1"]
        )

    def test_unhide_hosts_success(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1", "test_aid_2"],
                "hidden": False,
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

        with patch.object(host_hide, "HAS_FALCONPY", True):
            with patch.object(host_hide, "authenticate", return_value=mock_hosts):
                with pytest.raises(AnsibleExitJson) as result:
                    host_hide.main()

        assert result.value.args[0]["changed"] is True
        assert "test_aid_1" in result.value.args[0]["hosts"]
        assert "test_aid_2" in result.value.args[0]["hosts"]
        assert len(result.value.args[0]["failed_hosts"]) == 0
        mock_hosts.perform_action.assert_called_once_with(
            action_name="unhide_host", ids=["test_aid_1", "test_aid_2"]
        )

    def test_hide_host_already_hidden(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1"],
                "hidden": True,
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
                        "message": "Host test_aid_1 is already hidden",
                    }
                ],
            },
        }

        with patch.object(host_hide, "HAS_FALCONPY", True):
            with patch.object(host_hide, "authenticate", return_value=mock_hosts):
                with pytest.raises(AnsibleExitJson) as result:
                    host_hide.main()

        assert result.value.args[0]["changed"] is False
        assert "test_aid_1" in result.value.args[0]["hosts"]
        assert len(result.value.args[0]["failed_hosts"]) == 0

    def test_hide_host_failure(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1"],
                "hidden": True,
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

        with patch.object(host_hide, "HAS_FALCONPY", True):
            with patch.object(host_hide, "authenticate", return_value=mock_hosts):
                with pytest.raises(AnsibleExitJson) as result:
                    host_hide.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["hosts"]) == 0
        assert len(result.value.args[0]["failed_hosts"]) == 1
        assert result.value.args[0]["failed_hosts"][0]["id"] == "test_aid_1"
        assert result.value.args[0]["failed_hosts"][0]["code"] == 404

    def test_hide_multiple_hosts_partial_success(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1", "test_aid_2"],
                "hidden": True,
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

        with patch.object(host_hide, "HAS_FALCONPY", True):
            with patch.object(host_hide, "authenticate", return_value=mock_hosts):
                with pytest.raises(AnsibleExitJson) as result:
                    host_hide.main()

        assert result.value.args[0]["changed"] is True
        assert "test_aid_1" in result.value.args[0]["hosts"]
        assert len(result.value.args[0]["failed_hosts"]) == 1
        assert result.value.args[0]["failed_hosts"][0]["id"] == "test_aid_2"

    def test_hide_hosts_batch_processing(self, monkeypatch):
        hosts_list = [f"test_aid_{i}" for i in range(150)]
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": hosts_list,
                "hidden": True,
            }
        )

        mock_hosts = MagicMock()
        mock_hosts.perform_action.return_value = {
            "status_code": 200,
            "body": {
                "resources": [{"id": aid} for aid in hosts_list[:100]],
                "errors": [],
            },
        }

        with patch.object(host_hide, "HAS_FALCONPY", True):
            with patch.object(host_hide, "authenticate", return_value=mock_hosts):
                with pytest.raises(AnsibleExitJson) as result:
                    host_hide.main()

        assert result.value.args[0]["changed"] is True
        assert mock_hosts.perform_action.call_count == 2

    def test_hide_host_403_error(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1"],
                "hidden": True,
            }
        )

        mock_hosts = MagicMock()
        mock_hosts.perform_action.return_value = {
            "status_code": 403,
            "body": {
                "errors": [{"message": "Forbidden"}],
            },
        }

        with patch.object(host_hide, "HAS_FALCONPY", True):
            with patch.object(host_hide, "authenticate", return_value=mock_hosts):
                with pytest.raises(AnsibleFailJson) as result:
                    host_hide.main()

        assert "Unable to hide/unhide hosts" in result.value.args[0]["msg"]

    def test_missing_falconpy(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hosts": ["test_aid_1"],
            }
        )

        with patch.object(host_hide, "HAS_FALCONPY", False):
            with pytest.raises(AnsibleFailJson) as result:
                host_hide.main()

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

        with patch.object(host_hide, "HAS_FALCONPY", True):
            with pytest.raises(AnsibleExitJson) as result:
                host_hide.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["hosts"]) == 0
        assert len(result.value.args[0]["failed_hosts"]) == 0
