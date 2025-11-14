#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible_collections.crowdstrike.falcon.plugins.modules import falconctl_info
from ansible_collections.crowdstrike.falcon.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    set_module_args,
    get_bin_path,
)

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestFalconCtlInfoModule:
    def test_get_all_options(self, monkeypatch):
        set_module_args({})

        mock_get_options = {
            "cid": "1234567890abcdef1234567890abcdef",
            "aid": "test_aid",
            "tags": "tag1,tag2",
            "version": "7.10.0",
        }

        with patch.object(falconctl_info.AnsibleModule, "get_bin_path", get_bin_path):
            with patch(
                "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                return_value=mock_get_options,
            ):
                with pytest.raises(AnsibleExitJson) as result:
                    falconctl_info.main()

        assert result.value.args[0]["changed"] is False
        assert result.value.args[0]["falconctl_info"]["cid"] == "1234567890abcdef1234567890abcdef"
        assert result.value.args[0]["falconctl_info"]["aid"] == "test_aid"
        assert result.value.args[0]["falconctl_info"]["tags"] == "tag1,tag2"
        assert result.value.args[0]["falconctl_info"]["version"] == "7.10.0"

    def test_get_specific_options(self, monkeypatch):
        set_module_args(
            {
                "name": ["cid", "aid"],
            }
        )

        mock_get_options = {
            "cid": "1234567890abcdef1234567890abcdef",
            "aid": "test_aid",
        }

        with patch.object(falconctl_info.AnsibleModule, "get_bin_path", get_bin_path):
            with patch(
                "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                return_value=mock_get_options,
            ):
                with pytest.raises(AnsibleExitJson) as result:
                    falconctl_info.main()

        assert result.value.args[0]["changed"] is False
        assert result.value.args[0]["falconctl_info"]["cid"] == "1234567890abcdef1234567890abcdef"
        assert result.value.args[0]["falconctl_info"]["aid"] == "test_aid"
        assert "tags" not in result.value.args[0]["falconctl_info"]

    def test_get_version_info(self, monkeypatch):
        set_module_args(
            {
                "name": ["version"],
            }
        )

        mock_get_options = {
            "version": "7.10.0",
        }

        with patch.object(falconctl_info.AnsibleModule, "get_bin_path", get_bin_path):
            with patch(
                "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                return_value=mock_get_options,
            ):
                with pytest.raises(AnsibleExitJson) as result:
                    falconctl_info.main()

        assert result.value.args[0]["changed"] is False
        assert result.value.args[0]["falconctl_info"]["version"] == "7.10.0"

    def test_get_rfm_state(self, monkeypatch):
        set_module_args(
            {
                "name": ["rfm_state", "rfm_reason"],
            }
        )

        mock_get_options = {
            "rfm_state": "true",
            "rfm_reason": "Missing kernel symbols",
        }

        with patch.object(falconctl_info.AnsibleModule, "get_bin_path", get_bin_path):
            with patch(
                "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                return_value=mock_get_options,
            ):
                with pytest.raises(AnsibleExitJson) as result:
                    falconctl_info.main()

        assert result.value.args[0]["changed"] is False
        assert result.value.args[0]["falconctl_info"]["rfm_state"] == "true"
        assert result.value.args[0]["falconctl_info"]["rfm_reason"] == "Missing kernel symbols"

    def test_get_proxy_settings(self, monkeypatch):
        set_module_args(
            {
                "name": ["apd", "aph", "app"],
            }
        )

        mock_get_options = {
            "apd": "FALSE",
            "aph": "proxy.example.com",
            "app": "8080",
        }

        with patch.object(falconctl_info.AnsibleModule, "get_bin_path", get_bin_path):
            with patch(
                "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                return_value=mock_get_options,
            ):
                with pytest.raises(AnsibleExitJson) as result:
                    falconctl_info.main()

        assert result.value.args[0]["changed"] is False
        assert result.value.args[0]["falconctl_info"]["apd"] == "FALSE"
        assert result.value.args[0]["falconctl_info"]["aph"] == "proxy.example.com"
        assert result.value.args[0]["falconctl_info"]["app"] == "8080"

    def test_get_backend_info(self, monkeypatch):
        set_module_args(
            {
                "name": ["backend"],
            }
        )

        mock_get_options = {
            "backend": "bpf",
        }

        with patch.object(falconctl_info.AnsibleModule, "get_bin_path", get_bin_path):
            with patch(
                "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                return_value=mock_get_options,
            ):
                with pytest.raises(AnsibleExitJson) as result:
                    falconctl_info.main()

        assert result.value.args[0]["changed"] is False
        assert result.value.args[0]["falconctl_info"]["backend"] == "bpf"

    def test_get_cloud_info(self, monkeypatch):
        set_module_args(
            {
                "name": ["cloud"],
            }
        )

        mock_get_options = {
            "cloud": "us-2",
        }

        with patch.object(falconctl_info.AnsibleModule, "get_bin_path", get_bin_path):
            with patch(
                "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                return_value=mock_get_options,
            ):
                with pytest.raises(AnsibleExitJson) as result:
                    falconctl_info.main()

        assert result.value.args[0]["changed"] is False
        assert result.value.args[0]["falconctl_info"]["cloud"] == "us-2"

    def test_check_mode(self, monkeypatch):
        set_module_args(
            {
                "_ansible_check_mode": True,
            }
        )

        with patch.object(falconctl_info.AnsibleModule, "get_bin_path", get_bin_path):
            with pytest.raises(AnsibleExitJson) as result:
                falconctl_info.main()

        assert result.value.args[0]["changed"] is False

    def test_null_values(self, monkeypatch):
        set_module_args(
            {
                "name": ["tags", "billing"],
            }
        )

        mock_get_options = {
            "tags": None,
            "billing": None,
        }

        with patch.object(falconctl_info.AnsibleModule, "get_bin_path", get_bin_path):
            with patch(
                "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                return_value=mock_get_options,
            ):
                with pytest.raises(AnsibleExitJson) as result:
                    falconctl_info.main()

        assert result.value.args[0]["changed"] is False
        assert result.value.args[0]["falconctl_info"]["tags"] is None
        assert result.value.args[0]["falconctl_info"]["billing"] is None
