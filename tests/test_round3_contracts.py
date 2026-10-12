"""Contracts from the third blind mutation round: CLI JSON shapes, exclusive actions, iteration."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from importlib import resources
from pathlib import Path

import pytest
from _cli_command import run_cli

import lverror


def test_list_families_json_is_the_family_list() -> None:
    result = run_cli("--list-families", "--json")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == list(lverror.families())


def test_undocumented_code_has_a_null_message_in_json() -> None:
    result = run_cli("-200300", "--json")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["message"] is None


@pytest.mark.parametrize(
    "args",
    [
        ["--search", "file", "--family", "DDE"],
        ["7", "--family", "DDE"],
        ["--list-families", "--search", "file"],
        ["--list-families", "--family", "DDE"],
        ["7", "--list-families"],
    ],
)
def test_any_two_actions_exit_two(args: list[str]) -> None:
    result = run_cli(*args)
    assert result.returncode == 2
    assert "not allowed with" in result.stderr


def test_nearest_reaches_the_first_and_last_codes() -> None:
    first, last = lverror.codes()[0], lverror.codes()[-1]
    assert lverror.nearest(-(2**31)).code == first
    assert lverror.nearest(first).code == first
    assert lverror.nearest(2**31 - 1).code == last


def test_in_family_is_the_records_filter_for_every_family() -> None:
    for name in lverror.families():
        expected = [rec for rec in lverror.records() if rec.family == name]
        assert lverror.in_family(name) == expected, name
    assert any(rec.code == 1073676294 for rec in lverror.in_family("VISA"))


@pytest.mark.parametrize(("arg", "code"), [("-3", 1), ("bogus", 2), ("7", 0)])
def test_module_form_returns_the_exit_code(arg: str, code: int) -> None:
    env = dict(os.environ)
    package_parent = str(Path(lverror.__file__).resolve().parent.parent)
    env["PYTHONPATH"] = package_parent + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, "-m", "lverror", "--", arg], capture_output=True, text=True, env=env
    )
    assert result.returncode == code, result.stderr


def test_the_error_list_has_no_repeats() -> None:
    raw = resources.files("lverror").joinpath("_messages.json").read_text(encoding="utf-8")
    listed = json.loads(raw)["positive_errors"]
    assert len(listed) == len(set(listed)) and listed == sorted(listed)
