# Copyright: (c) 2023, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible.module_utils import basic
from ansible_collections.crowdstrike.falcon.tests.unit.plugins.modules import utils


@pytest.fixture(autouse=True)
def patch_ansible_module(monkeypatch):
    """Automatically patch AnsibleModule methods for all tests."""
    monkeypatch.setattr(basic.AnsibleModule, "exit_json", utils.exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", utils.fail_json)
    monkeypatch.setattr(basic.AnsibleModule, "get_bin_path", utils.get_bin_path)
    monkeypatch.setattr(basic.AnsibleModule, "run_command", utils.mock_run_command)
