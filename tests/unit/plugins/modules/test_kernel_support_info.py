#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible_collections.crowdstrike.falcon.plugins.modules import kernel_support_info
from ansible_collections.crowdstrike.falcon.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
)

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class TestKernelSupportInfoModule:
    def test_get_kernel_support_info(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
            }
        )

        mock_result = {
            "changed": False,
            "info": [
                {
                    "architecture": "x86_64",
                    "release": "5.4.0-1040-gcp",
                    "vendor": "ubuntu",
                    "distro": "ubuntu20",
                    "flavor": "generic",
                }
            ],
        }

        with patch.object(kernel_support_info, "HAS_FALCONPY", True):
            with patch.object(kernel_support_info, "authenticate"):
                with patch.object(
                    kernel_support_info, "get_paginated_results_info", return_value=mock_result
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        kernel_support_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["info"]) == 1
        assert result.value.args[0]["info"][0]["architecture"] == "x86_64"

    def test_get_kernel_support_with_filter(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "filter": "vendor:'ubuntu'+distro:'ubuntu20'+release:*'5.8.*'",
            }
        )

        mock_result = {
            "changed": False,
            "info": [
                {
                    "architecture": "x86_64",
                    "release": "5.8.0-1040-gcp",
                    "vendor": "ubuntu",
                    "distro": "ubuntu20",
                }
            ],
        }

        with patch.object(kernel_support_info, "HAS_FALCONPY", True):
            with patch.object(kernel_support_info, "authenticate"):
                with patch.object(
                    kernel_support_info, "get_paginated_results_info", return_value=mock_result
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        kernel_support_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["info"]) == 1

    def test_missing_falconpy(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
            }
        )

        with patch.object(kernel_support_info, "HAS_FALCONPY", False):
            with pytest.raises(AnsibleFailJson) as result:
                kernel_support_info.main()

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
            "info": [
                {
                    "architecture": "x86_64",
                    "release": "5.4.0-1040-gcp",
                }
            ],
        }

        with patch.object(kernel_support_info, "HAS_FALCONPY", True):
            with patch.object(kernel_support_info, "authenticate"):
                with patch.object(
                    kernel_support_info, "get_paginated_results_info", return_value=mock_result
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        kernel_support_info.main()

        assert result.value.args[0]["changed"] is False

    def test_empty_results(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "filter": "vendor:'nonexistent'",
            }
        )

        mock_result = {
            "changed": False,
            "info": [],
        }

        with patch.object(kernel_support_info, "HAS_FALCONPY", True):
            with patch.object(kernel_support_info, "authenticate"):
                with patch.object(
                    kernel_support_info, "get_paginated_results_info", return_value=mock_result
                ):
                    with pytest.raises(AnsibleExitJson) as result:
                        kernel_support_info.main()

        assert result.value.args[0]["changed"] is False
        assert len(result.value.args[0]["info"]) == 0
