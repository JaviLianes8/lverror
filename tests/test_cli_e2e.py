"""Real end-to-end tests: run the ``lverror`` command of the package under test as a user does.

Each test spawns a fresh process (the console script installed next to the test interpreter,
or ``python -m lverror``) and checks the real stdout, stderr and exit code against NI text read
straight from the captured LabVIEW 2026 and NI-VISA error files. No mocks, nothing installed.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from _cli_command import run_cli

import lverror

_SOURCES = Path(__file__).parent / "fixtures" / "sources"


def _source_text(name: str, code: int) -> str:
    raw = (_SOURCES / f"{name}.xml").read_text(encoding="utf-8")
    body = raw.split(f'<nierror code="{code}">', 1)[1].split("</nierror>", 1)[0]
    return " ".join(body.split()).split(") ", 1)[1]


GOLDEN: list[tuple[str, int, str]] = [
    ("7", 7, _source_text("labview-errors", 7)),
    ("0xBFFF0015", -1073807339, _source_text("visa-errors", -1073807339)),
    ("-1073807339", -1073807339, _source_text("visa-errors", -1073807339)),
    ("14001", 14001, _source_text("labview-errors", 14001)),
    ("1073676294", 1073676294, _source_text("visa-errors", 1073676294)),
]


@pytest.mark.parametrize(("raw", "code", "text"), GOLDEN, ids=[g[0] for g in GOLDEN])
def test_lookup_prints_ni_text_and_exits_zero(raw: str, code: int, text: str) -> None:
    result = run_cli(raw)
    assert result.returncode == 0, result.stderr
    assert result.stdout.endswith(f": {text}\n")
    assert result.stdout.startswith(f"{code} (")


def test_module_form_runs_the_same_tool() -> None:
    env = dict(os.environ)
    package_parent = str(Path(lverror.__file__).resolve().parent.parent)
    env["PYTHONPATH"] = package_parent + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, "-m", "lverror", "7"], capture_output=True, text=True, env=env
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == run_cli("7").stdout


def test_json_output_carries_every_field() -> None:
    result = run_cli("0xBFFF0015", "--json")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "code": -1073807339,
        "message": "Timeout expired before operation completed.",
        "family": "VISA",
        "is_error": True,
        "is_warning": False,
    }


def test_search_finds_the_visa_timeout() -> None:
    result = run_cli("--search", "timeout expired", "--json")
    assert result.returncode == 0, result.stderr
    assert [rec["code"] for rec in json.loads(result.stdout)] == [-1073807339]


def test_family_listing_contains_a_known_dde_code() -> None:
    result = run_cli("--family", "DDE")
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0] == "14001 (error, DDE): Invalid refnum."
    assert len(result.stdout.splitlines()) == len(lverror.in_family("DDE"))


def test_list_families_prints_one_name_per_line() -> None:
    result = run_cli("--list-families")
    assert result.returncode == 0, result.stderr
    assert tuple(result.stdout.splitlines()) == lverror.families()


def test_unknown_code_exits_one() -> None:
    result = run_cli("123456789")
    assert result.returncode == 1
    assert result.stdout == "123456789 (warning, unknown family): no documented information\n"


def test_bad_input_exits_two_with_a_message() -> None:
    result = run_cli("0xZZ")
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == "lverror: not a valid code: '0xZZ'\n"


def test_two_actions_in_one_run_exit_two() -> None:
    result = run_cli("7", "--search", "file")
    assert result.returncode == 2
    assert "not allowed with" in result.stderr


def test_version_matches_the_package() -> None:
    result = run_cli("--version")
    assert result.returncode == 0, result.stderr
    assert result.stdout == f"lverror {lverror.__version__}\n"


def test_help_lists_runnable_examples() -> None:
    result = run_cli("--help")
    assert result.returncode == 0, result.stderr
    assert "Examples:" in result.stdout
    assert "lverror --search" in result.stdout


def test_search_without_a_match_exits_one_and_prints_nothing() -> None:
    result = run_cli("--search", "no such words anywhere")
    assert (result.returncode, result.stdout, result.stderr) == (1, "", "")


def test_undocumented_code_in_a_known_family_exits_zero() -> None:
    result = run_cli("-200300")
    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        "-200300 (error, NI-DAQmx): no documented message, classified by range only\n"
    )


def test_unknown_family_exits_two() -> None:
    result = run_cli("--family", "GPIB")
    assert result.returncode == 2
    assert result.stderr.startswith("lverror: unknown family 'GPIB'; known families are: VISA")
