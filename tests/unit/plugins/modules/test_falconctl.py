#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible_collections.crowdstrike.falcon.plugins.modules import falconctl
from ansible_collections.crowdstrike.falcon.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
    get_bin_path,
    mock_run_command,
)

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestFalconCtlModule:
    def test_set_cid_present(self, monkeypatch):
        set_module_args(
            {
                "state": "present",
                "cid": "1234567890ABCDEF1234567890ABCDEF-12",
            }
        )

        with patch.object(falconctl.AnsibleModule, "get_bin_path", get_bin_path):
            with patch.object(
                falconctl.AnsibleModule, "run_command", mock_run_command
            ):
                with patch(
                    "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                    return_value={"cid": None},
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        falconctl.main()

        assert result.value.args[0]["changed"] is True

    def test_set_cid_with_provisioning_token(self, monkeypatch):
        set_module_args(
            {
                "state": "present",
                "cid": "1234567890ABCDEF1234567890ABCDEF-12",
                "provisioning_token": "12345678",
            }
        )

        with patch.object(falconctl.AnsibleModule, "get_bin_path", get_bin_path):
            with patch.object(
                falconctl.AnsibleModule, "run_command", mock_run_command
            ):
                with patch(
                    "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                    return_value={"cid": None, "provisioning_token": None},
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        falconctl.main()

        assert result.value.args[0]["changed"] is True

    def test_set_cid_with_cloud(self, monkeypatch):
        set_module_args(
            {
                "state": "present",
                "cid": "1234567890ABCDEF1234567890ABCDEF-12",
                "cloud": "us-2",
            }
        )

        with patch.object(falconctl.AnsibleModule, "get_bin_path", get_bin_path):
            with patch.object(
                falconctl.AnsibleModule, "run_command", mock_run_command
            ):
                with patch(
                    "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                    return_value={"cid": None, "cloud": None},
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        falconctl.main()

        assert result.value.args[0]["changed"] is True

    def test_delete_cid_absent(self, monkeypatch):
        set_module_args(
            {
                "state": "absent",
                "cid": "",
            }
        )

        with patch.object(falconctl.AnsibleModule, "get_bin_path", get_bin_path):
            with patch.object(
                falconctl.AnsibleModule, "run_command", mock_run_command
            ):
                with patch(
                    "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                    return_value={"cid": "1234567890abcdef1234567890abcdef"},
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        falconctl.main()

        assert result.value.args[0]["changed"] is True

    def test_delete_aid_absent(self, monkeypatch):
        set_module_args(
            {
                "state": "absent",
                "aid": True,
            }
        )

        with patch.object(falconctl.AnsibleModule, "get_bin_path", get_bin_path):
            with patch.object(
                falconctl.AnsibleModule, "run_command", mock_run_command
            ):
                with patch(
                    "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                    return_value={"aid": "test_aid"},
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        falconctl.main()

        assert result.value.args[0]["changed"] is True

    def test_set_proxy_settings(self, monkeypatch):
        set_module_args(
            {
                "state": "present",
                "apd": "false",
                "aph": "proxy.example.com",
                "app": "8080",
            }
        )

        with patch.object(falconctl.AnsibleModule, "get_bin_path", get_bin_path):
            with patch.object(
                falconctl.AnsibleModule, "run_command", mock_run_command
            ):
                with patch(
                    "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                    return_value={"apd": "TRUE", "aph": None, "app": None},
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        falconctl.main()

        assert result.value.args[0]["changed"] is True

    def test_set_tags(self, monkeypatch):
        set_module_args(
            {
                "state": "present",
                "tags": "tag1,tag2,tag3",
            }
        )

        with patch.object(falconctl.AnsibleModule, "get_bin_path", get_bin_path):
            with patch.object(
                falconctl.AnsibleModule, "run_command", mock_run_command
            ):
                with patch(
                    "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                    return_value={"tags": None},
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        falconctl.main()

        assert result.value.args[0]["changed"] is True

    def test_invalid_cid_format(self, monkeypatch):
        set_module_args(
            {
                "state": "present",
                "cid": "invalid_cid",
            }
        )

        with patch.object(falconctl.AnsibleModule, "get_bin_path", get_bin_path):
            with pytest.raises(AnsibleFailJson) as result:
                falconctl.main()

        assert "Invalid CrowdStrike CID" in result.value.args[0]["msg"]

    def test_invalid_provisioning_token_format(self, monkeypatch):
        set_module_args(
            {
                "state": "present",
                "cid": "1234567890ABCDEF1234567890ABCDEF-12",
                "provisioning_token": "invalid",
            }
        )

        with patch.object(falconctl.AnsibleModule, "get_bin_path", get_bin_path):
            with pytest.raises(AnsibleFailJson) as result:
                falconctl.main()

        assert "Invalid provisioning token" in result.value.args[0]["msg"]

    def test_provisioning_token_without_cid(self, monkeypatch):
        set_module_args(
            {
                "state": "present",
                "provisioning_token": "12345678",
            }
        )

        with patch.object(falconctl.AnsibleModule, "get_bin_path", get_bin_path):
            with pytest.raises(AnsibleFailJson) as result:
                falconctl.main()

        assert "provisioning_token requires cid" in result.value.args[0]["msg"]

    def test_invalid_tags_format(self, monkeypatch):
        set_module_args(
            {
                "state": "present",
                "tags": "invalid@tags!",
            }
        )

        with patch.object(falconctl.AnsibleModule, "get_bin_path", get_bin_path):
            with pytest.raises(AnsibleFailJson) as result:
                falconctl.main()

        assert "Value of tags must be one of" in result.value.args[0]["msg"]

    def test_check_mode(self, monkeypatch):
        set_module_args(
            {
                "state": "present",
                "cid": "1234567890ABCDEF1234567890ABCDEF-12",
                "_ansible_check_mode": True,
            }
        )

        with patch.object(falconctl.AnsibleModule, "get_bin_path", get_bin_path):
            with patch(
                "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                return_value={"cid": None},
            ):
                with pytest.raises(AnsibleExitJson) as result:
                    falconctl.main()

        assert result.value.args[0]["changed"] is True

    def test_no_change_when_already_set(self, monkeypatch):
        set_module_args(
            {
                "state": "present",
                "cid": "1234567890ABCDEF1234567890ABCDEF-12",
            }
        )

        with patch.object(falconctl.AnsibleModule, "get_bin_path", get_bin_path):
            with patch.object(
                falconctl.AnsibleModule, "run_command", mock_run_command
            ):
                with patch(
                    "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                    return_value={"cid": "1234567890abcdef1234567890abcdef"},
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        falconctl.main()

        assert result.value.args[0]["changed"] is False

    def test_set_backend(self, monkeypatch):
        set_module_args(
            {
                "state": "present",
                "backend": "bpf",
            }
        )

        with patch.object(falconctl.AnsibleModule, "get_bin_path", get_bin_path):
            with patch.object(
                falconctl.AnsibleModule, "run_command", mock_run_command
            ):
                with patch(
                    "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                    return_value={"backend": None},
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        falconctl.main()

        assert result.value.args[0]["changed"] is True

    def test_set_billing(self, monkeypatch):
        set_module_args(
            {
                "state": "present",
                "billing": "metered",
            }
        )

        with patch.object(falconctl.AnsibleModule, "get_bin_path", get_bin_path):
            with patch.object(
                falconctl.AnsibleModule, "run_command", mock_run_command
            ):
                with patch(
                    "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                    return_value={"billing": None},
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        falconctl.main()

        assert result.value.args[0]["changed"] is True

    def test_set_trace(self, monkeypatch):
        set_module_args(
            {
                "state": "present",
                "trace": "debug",
            }
        )

        with patch.object(falconctl.AnsibleModule, "get_bin_path", get_bin_path):
            with patch.object(
                falconctl.AnsibleModule, "run_command", mock_run_command
            ):
                with patch(
                    "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                    return_value={"trace": None},
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        falconctl.main()

        assert result.value.args[0]["changed"] is True

    def test_set_feature_list(self, monkeypatch):
        set_module_args(
            {
                "state": "present",
                "feature": ["enableLog", "disableLogBuffer"],
            }
        )

        with patch.object(falconctl.AnsibleModule, "get_bin_path", get_bin_path):
            with patch.object(
                falconctl.AnsibleModule, "run_command", mock_run_command
            ):
                with patch(
                    "ansible_collections.crowdstrike.falcon.plugins.module_utils.falconctl_utils.get_options",
                    return_value={"feature": None},
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        falconctl.main()

        assert result.value.args[0]["changed"] is True
