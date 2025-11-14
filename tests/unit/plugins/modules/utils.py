#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, CrowdStrike Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import sys

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


class AnsibleExitJson(Exception):
    pass


class AnsibleFailJson(Exception):
    pass


def set_module_args(args):
    if "_ansible_remote_tmp" not in args:
        args["_ansible_remote_tmp"] = "/tmp"
    if "_ansible_keep_remote_files" not in args:
        args["_ansible_keep_remote_files"] = False

    args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args)


def exit_json(*args, **kwargs):
    if "changed" not in kwargs:
        kwargs["changed"] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


def get_bin_path(self, arg, required=False, opt_dirs=None):
    if arg.endswith("falconctl"):
        return "/opt/CrowdStrike/falconctl"
    return arg


def mock_run_command(self, cmd, use_unsafe_shell=False):
    return (0, "", "")
