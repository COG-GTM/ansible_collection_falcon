# Copyright: (c) 2023, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible_collections.crowdstrike.falcon.plugins.modules import sensor_download
from ansible_collections.crowdstrike.falcon.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
)

try:
    from unittest.mock import MagicMock, patch, mock_open
except ImportError:
    from mock import MagicMock, patch, mock_open


class TestSensorDownloadModule:
    def test_download_sensor_success(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hash": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "dest": "/tmp/test",
            }
        )

        mock_sensor_download = MagicMock()
        mock_sensor_download.get_sensor_installer_entities.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "falcon-sensor.deb",
                        "sha256": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                    }
                ],
            },
        }
        mock_sensor_download.download_sensor_installer.return_value = b"test_binary_data"

        with patch.object(sensor_download, "HAS_FALCONPY", True):
            with patch.object(
                sensor_download, "authenticate", return_value=mock_sensor_download
            ):
                with patch.object(sensor_download, "handle_return_errors"):
                    with patch.object(sensor_download, "check_destination_path"):
                        with patch.object(sensor_download, "lock_file") as mock_lock:
                            with patch.object(sensor_download, "unlock_file"):
                                with patch("builtins.open", mock_open()):
                                    with patch.object(
                                        sensor_download, "update_permissions"
                                    ):
                                        with patch("os.path.isfile", return_value=False):
                                            mock_lock.return_value = MagicMock()
                                            with pytest.raises(AnsibleExitJson) as result:
                                                sensor_download.main()

        assert result.value.args[0]["changed"] is True
        assert "/tmp/test/falcon-sensor.deb" in result.value.args[0]["path"]

    def test_download_sensor_file_exists_same_hash(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hash": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "dest": "/tmp/test",
            }
        )

        mock_sensor_download = MagicMock()
        mock_sensor_download.get_sensor_installer_entities.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "falcon-sensor.deb",
                        "sha256": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                    }
                ],
            },
        }

        mock_module = MagicMock()
        mock_module.sha256.return_value = "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"

        with patch.object(sensor_download, "HAS_FALCONPY", True):
            with patch.object(
                sensor_download, "authenticate", return_value=mock_sensor_download
            ):
                with patch.object(sensor_download, "handle_return_errors"):
                    with patch.object(sensor_download, "check_destination_path"):
                        with patch.object(sensor_download, "lock_file") as mock_lock:
                            with patch.object(sensor_download, "unlock_file"):
                                with patch.object(
                                    sensor_download, "update_permissions", return_value=False
                                ):
                                    with patch("os.path.isfile", return_value=True):
                                        with patch.object(
                                            sensor_download.AnsibleModule, "sha256"
                                        ) as mock_sha:
                                            mock_sha.return_value = "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
                                            mock_lock.return_value = MagicMock()
                                            with pytest.raises(AnsibleExitJson) as result:
                                                sensor_download.main()

        assert result.value.args[0]["changed"] is False

    def test_download_sensor_custom_name(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hash": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "dest": "/tmp/test",
                "name": "custom-sensor.deb",
            }
        )

        mock_sensor_download = MagicMock()
        mock_sensor_download.get_sensor_installer_entities.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "falcon-sensor.deb",
                        "sha256": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                    }
                ],
            },
        }
        mock_sensor_download.download_sensor_installer.return_value = b"test_binary_data"

        with patch.object(sensor_download, "HAS_FALCONPY", True):
            with patch.object(
                sensor_download, "authenticate", return_value=mock_sensor_download
            ):
                with patch.object(sensor_download, "handle_return_errors"):
                    with patch.object(sensor_download, "check_destination_path"):
                        with patch.object(sensor_download, "lock_file") as mock_lock:
                            with patch.object(sensor_download, "unlock_file"):
                                with patch("builtins.open", mock_open()):
                                    with patch.object(
                                        sensor_download, "update_permissions"
                                    ):
                                        with patch("os.path.isfile", return_value=False):
                                            mock_lock.return_value = MagicMock()
                                            with pytest.raises(AnsibleExitJson) as result:
                                                sensor_download.main()

        assert result.value.args[0]["changed"] is True
        assert "custom-sensor.deb" in result.value.args[0]["path"]

    def test_download_sensor_no_dest(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hash": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            }
        )

        mock_sensor_download = MagicMock()
        mock_sensor_download.get_sensor_installer_entities.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "falcon-sensor.deb",
                        "sha256": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                    }
                ],
            },
        }
        mock_sensor_download.download_sensor_installer.return_value = b"test_binary_data"

        with patch.object(sensor_download, "HAS_FALCONPY", True):
            with patch.object(
                sensor_download, "authenticate", return_value=mock_sensor_download
            ):
                with patch.object(sensor_download, "handle_return_errors"):
                    with patch("tempfile.mkdtemp", return_value="/tmp/tmpdir"):
                        with patch("os.chmod"):
                            with patch("os.path.isdir", return_value=True):
                                with patch("os.access", return_value=True):
                                    with patch.object(
                                        sensor_download, "lock_file"
                                    ) as mock_lock:
                                        with patch.object(sensor_download, "unlock_file"):
                                            with patch("builtins.open", mock_open()):
                                                with patch.object(
                                                    sensor_download, "update_permissions"
                                                ):
                                                    with patch(
                                                        "os.path.isfile", return_value=False
                                                    ):
                                                        mock_lock.return_value = MagicMock()
                                                        with pytest.raises(
                                                            AnsibleExitJson
                                                        ) as result:
                                                            sensor_download.main()

        assert result.value.args[0]["changed"] is True

    def test_download_sensor_hash_not_found(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hash": "invalid_hash",
                "dest": "/tmp/test",
            }
        )

        mock_sensor_download = MagicMock()
        mock_sensor_download.get_sensor_installer_entities.return_value = {
            "status_code": 404,
            "body": {
                "errors": [{"message": "Not found"}],
            },
        }

        with patch.object(sensor_download, "HAS_FALCONPY", True):
            with patch.object(
                sensor_download, "authenticate", return_value=mock_sensor_download
            ):
                with patch.object(sensor_download, "handle_return_errors") as mock_handle:
                    with patch.object(sensor_download, "check_destination_path"):
                        mock_handle.side_effect = AnsibleFailJson({"msg": "Not found"})
                        with pytest.raises(AnsibleFailJson):
                            sensor_download.main()

    def test_missing_falconpy(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hash": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            }
        )

        with patch.object(sensor_download, "HAS_FALCONPY", False):
            with pytest.raises(AnsibleFailJson) as result:
                sensor_download.main()

        assert "falconpy" in result.value.args[0]["msg"]

    def test_check_mode(self, monkeypatch):
        set_module_args(
            {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "hash": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "dest": "/tmp/test",
                "_ansible_check_mode": True,
            }
        )

        mock_sensor_download = MagicMock()
        mock_sensor_download.get_sensor_installer_entities.return_value = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "name": "falcon-sensor.deb",
                        "sha256": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                    }
                ],
            },
        }

        with patch.object(sensor_download, "HAS_FALCONPY", True):
            with patch.object(
                sensor_download, "authenticate", return_value=mock_sensor_download
            ):
                with patch.object(sensor_download, "handle_return_errors"):
                    with patch.object(sensor_download, "check_destination_path"):
                        with patch.object(sensor_download, "lock_file") as mock_lock:
                            with patch.object(sensor_download, "unlock_file"):
                                with patch("os.path.isfile", return_value=False):
                                    mock_lock.return_value = MagicMock()
                                    with pytest.raises(AnsibleExitJson) as result:
                                        sensor_download.main()

        assert result.value.args[0]["changed"] is True
