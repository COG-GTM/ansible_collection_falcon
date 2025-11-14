#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible_collections.crowdstrike.falcon.plugins.modules import auth
from ansible_collections.crowdstrike.falcon.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
)

try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch


class TestAuthModule:
    def test_generate_token_success(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "action": "generate",
            }
        )

        mock_oauth2 = MagicMock()
        mock_oauth2.login.return_value = {"status_code": 201}
        mock_oauth2.token_value = "test_access_token"
        mock_oauth2.base_url = "https://api.crowdstrike.com"

        with patch.object(auth, "OAuth2", return_value=mock_oauth2):
            with patch.object(auth, "HAS_FALCONPY", True):
                with patch.object(
                    auth, "get_cloud_from_url", return_value="us-1"
                ) as mock_get_cloud:
                    with pytest.raises(AnsibleExitJson) as result:
                        auth.main()

        assert result.value.args[0]["changed"] is False
        assert result.value.args[0]["auth"]["access_token"] == "test_access_token"
        assert result.value.args[0]["auth"]["cloud"] == "us-1"
        mock_oauth2.login.assert_called_once()
        mock_get_cloud.assert_called_once()

    def test_generate_token_failure(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "action": "generate",
            }
        )

        mock_oauth2 = MagicMock()
        mock_oauth2.login.return_value = {
            "status_code": 401,
            "body": {"errors": [{"message": "Invalid credentials"}]},
        }

        with patch.object(auth, "OAuth2", return_value=mock_oauth2):
            with patch.object(auth, "HAS_FALCONPY", True):
                with patch.object(
                    auth, "handle_return_errors"
                ) as mock_handle_errors:
                    mock_handle_errors.side_effect = AnsibleFailJson(
                        {"msg": "Invalid credentials"}
                    )
                    with pytest.raises(AnsibleFailJson):
                        auth.main()

    def test_revoke_token_success(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "action": "revoke",
                "access_token": "test_token_to_revoke",
            }
        )

        mock_oauth2 = MagicMock()
        mock_oauth2.login.return_value = {"status_code": 201}
        mock_oauth2.revoke.return_value = {"status_code": 200}
        mock_oauth2.logout.return_value = {"status_code": 200}

        with patch.object(auth, "OAuth2", return_value=mock_oauth2):
            with patch.object(auth, "HAS_FALCONPY", True):
                with patch.object(auth, "handle_return_errors"):
                    with pytest.raises(AnsibleExitJson) as result:
                        auth.main()

        assert result.value.args[0]["changed"] is False
        mock_oauth2.login.assert_called_once()
        mock_oauth2.revoke.assert_called_once_with(token="test_token_to_revoke")
        mock_oauth2.logout.assert_called_once()

    def test_missing_falconpy(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "action": "generate",
            }
        )

        with patch.object(auth, "HAS_FALCONPY", False):
            with pytest.raises(AnsibleFailJson) as result:
                auth.main()

        assert "falconpy" in result.value.args[0]["msg"]

    def test_revoke_without_access_token(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "action": "revoke",
            }
        )

        with patch.object(auth, "HAS_FALCONPY", True):
            with pytest.raises(AnsibleFailJson) as result:
                auth.main()

        assert "access_token" in str(result.value.args[0])

    def test_argspec(self):
        spec = auth.argspec()
        assert "action" in spec
        assert "access_token" in spec
        assert "client_id" in spec
        assert "client_secret" in spec
        assert "auth" not in spec

    def test_generate_function(self):
        mock_falcon = MagicMock()
        mock_falcon.login.return_value = {"status_code": 201}
        result = auth.generate(mock_falcon)
        assert result["status_code"] == 201
        mock_falcon.login.assert_called_once()

    def test_revoke_function(self):
        mock_falcon = MagicMock()
        mock_falcon.login.return_value = {"status_code": 201}
        mock_falcon.revoke.return_value = {"status_code": 200}
        mock_falcon.logout.return_value = {"status_code": 200}

        result = auth.revoke(mock_falcon, "test_token")

        assert result["status_code"] == 200
        mock_falcon.login.assert_called_once()
        mock_falcon.revoke.assert_called_once_with(token="test_token")
        mock_falcon.logout.assert_called_once()
