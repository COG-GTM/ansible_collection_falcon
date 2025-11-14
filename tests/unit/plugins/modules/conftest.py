# Copyright: (c) 2023, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
import pytest

try:
    from unittest.mock import MagicMock, Mock
except ImportError:
    from mock import MagicMock, Mock

mock_falconpy = MagicMock()
mock_falconpy._version = Mock()
mock_falconpy._version.__version__ = "1.4.3"
mock_falconpy.OAuth2 = MagicMock
mock_falconpy.Hosts = MagicMock
mock_falconpy.SensorDownload = MagicMock
mock_falconpy.SensorUpdatePolicy = MagicMock
mock_falconpy.Intel = MagicMock
mock_falconpy.KernelCompatibility = MagicMock

sys.modules['falconpy'] = mock_falconpy
sys.modules['falconpy._version'] = mock_falconpy._version

from ansible.module_utils import basic
from ansible_collections.crowdstrike.falcon.tests.unit.plugins.modules import utils


@pytest.fixture(autouse=True)
def patch_ansible_module(monkeypatch):
    """Automatically patch AnsibleModule methods for all tests."""
    monkeypatch.setattr(basic.AnsibleModule, "exit_json", utils.exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", utils.fail_json)
    monkeypatch.setattr(basic.AnsibleModule, "get_bin_path", utils.get_bin_path)
    monkeypatch.setattr(basic.AnsibleModule, "run_command", utils.mock_run_command)
