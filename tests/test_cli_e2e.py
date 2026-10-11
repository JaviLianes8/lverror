"""Real end-to-end tests: run the shipped ``lverror`` command as a user does.

No mocks and no importing the functions under test. Each test spawns a fresh process and
checks the real stdout, stderr, and exit code against golden fixtures of actual NI/LabVIEW
codes and their documented text. Both the installed console script (when present on PATH) and
``python -m lverror`` are exercised, so the packaged entry point is covered.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys

import pytest

# Golden fixtures: real NI/LabVIEW codes paired with a stable fragment of their documented
# text. These come from the baked-in dataset, which is compiled from public NI sources.
GOLDEN: list[tuple[str, str]] = [
    ("7", "File not found"),
    ("0xBFFF0015", "Timeout expired before operation completed."),
    ("-1073807339", "Timeout expired before operation completed."),
    ("14001", "Invalid refnum."),
    ("-200088", "The task specified is invalid or does not exist."),
]


def _module_is_importable() -> bool:
    probe = subprocess.run(
        [sys.executable, "-c", "import lverror"],
        capture_output=True,
        timeout=60,
        check=False,
    )
    return probe.returncode == 0


def _commands() -> list[tuple[str, list[str]]]:
    commands: list[tuple[str, list[str]]] = []
    script = shutil.which("lverror")
    if script is not None:
        commands.append(("console-script", [script]))
    # The module form is only exercised where the package is importable under the test
    # interpreter, so a multi-interpreter machine does not report a false failure.
    if _module_is_importable():
        commands.append(("module", [sys.executable, "-m", "lverror"]))
    return commands


COMMANDS = _commands()
IDS = [name for name, _ in COMMANDS]
PREFIXES = [argv for _, argv in COMMANDS]


def _run(prefix: list[str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*prefix, *args],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


def test_a_console_script_is_installed() -> None:
    # The e2e suite is only meaningful if the packaged command exists. This asserts the
    # project did install its console script, so the suite cannot silently cover nothing.
    assert shutil.which("lverror") is not None, "install the package (pip install -e .) first"


@pytest.mark.parametrize("prefix", PREFIXES, ids=IDS)
@pytest.mark.parametrize(("code", "fragment"), GOLDEN)
def test_lookup_prints_real_text_and_exits_zero(
    prefix: list[str], code: str, fragment: str
) -> None:
    result = _run(prefix, code)
    assert result.returncode == 0, result.stderr
    assert fragment in result.stdout


@pytest.mark.parametrize("prefix", PREFIXES, ids=IDS)
def test_json_output_is_valid_and_round_trips(prefix: list[str]) -> None:
    result = _run(prefix, "0xBFFF0015", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["code"] == -1073807339
    assert payload["message"] == "Timeout expired before operation completed."
    assert payload["family"] == "VISA"
    assert payload["is_error"] is True


@pytest.mark.parametrize("prefix", PREFIXES, ids=IDS)
def test_search_finds_the_visa_timeout(prefix: list[str]) -> None:
    result = _run(prefix, "--search", "timeout", "--json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert any(rec["code"] == -1073807339 for rec in payload)


@pytest.mark.parametrize("prefix", PREFIXES, ids=IDS)
def test_family_listing_contains_a_known_dde_code(prefix: list[str]) -> None:
    result = _run(prefix, "--family", "DDE")
    assert result.returncode == 0, result.stderr
    assert "14001" in result.stdout
    assert "Invalid refnum." in result.stdout


@pytest.mark.parametrize("prefix", PREFIXES, ids=IDS)
def test_unknown_code_exits_one(prefix: list[str]) -> None:
    result = _run(prefix, "123456789")
    assert result.returncode == 1
    assert "no documented information" in result.stdout


@pytest.mark.parametrize("prefix", PREFIXES, ids=IDS)
def test_bad_input_exits_two_with_a_message(prefix: list[str]) -> None:
    result = _run(prefix, "0xZZ")
    assert result.returncode == 2
    assert "not a valid code" in result.stderr


@pytest.mark.parametrize("prefix", PREFIXES, ids=IDS)
def test_version_matches_the_package(prefix: list[str]) -> None:
    result = _run(prefix, "--version")
    assert result.returncode == 0, result.stderr
    assert "0.3.0" in result.stdout


@pytest.mark.parametrize("prefix", PREFIXES, ids=IDS)
def test_help_lists_runnable_examples(prefix: list[str]) -> None:
    result = _run(prefix, "--help")
    assert result.returncode == 0, result.stderr
    assert "Examples:" in result.stdout
    assert "lverror --search" in result.stdout
