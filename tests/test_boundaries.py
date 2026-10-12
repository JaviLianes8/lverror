"""Boundary contracts from the blind mutation round: edges every mutation of them must break."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from _cli_command import run_cli

import lverror

_DATA = Path(lverror.__file__).parent / "_messages.json"


def test_short_input_is_shown_whole_and_longer_input_is_cut() -> None:
    whole = "a" * 38  # its repr is exactly 40 characters
    with pytest.raises(ValueError) as caught:
        lverror.in_family(whole)
    assert repr(whole) in str(caught.value)
    with pytest.raises(ValueError) as caught:
        lverror.in_family("a" * 39)
    assert f"'{'a' * 36}..." in str(caught.value) and repr("a" * 39) not in str(caught.value)


def test_uppercase_hex_prefix_is_accepted() -> None:
    assert lverror.parse_code("0XBFFF0015") == -1073807339
    assert lverror.parse_code("-0X10") == -16


def test_input_up_to_64_characters_is_read() -> None:
    assert lverror.parse_code("0x" + "0" * 54 + "BFFF0015") == -1073807339
    assert lverror.parse_code("0" * 63 + "7") == 7
    with pytest.raises(ValueError):
        lverror.parse_code("0" * 64 + "7")


@pytest.mark.parametrize(
    ("code", "family"),
    [
        (-200000, "NI-DAQmx"),
        (-239999, "NI-DAQmx"),
        (-199999, None),
        (-240000, None),
        (200000, "NI-DAQmx"),
        (239999, "NI-DAQmx"),
        (240000, None),
        (16999, "general LabVIEW"),
        (17000, None),
        (14020, "DDE"),
        (14021, "general LabVIEW"),
        (-1073741825, "VISA"),
        (-1073741824, None),
        (1073676288, "VISA"),
        (1073741823, "VISA"),
        (1073741824, None),
    ],
)
def test_range_edges(code: int, family: str | None) -> None:
    assert lverror.family(code) == family


def test_visa_completion_codes_are_warnings() -> None:
    completions = [c for c in lverror.codes() if c > 0 and c >> 16 == 0x3FFF]
    assert len(completions) == 19
    for code in completions:
        assert lverror.is_warning(code) and not lverror.is_error(code), code


def test_every_entry_is_tagged_with_the_source_its_code_belongs_to() -> None:
    for code, source, _text in json.loads(_DATA.read_text(encoding="utf-8"))["messages"]:
        if (code & 0xFFFFFFFF) >> 16 in (0xBFFF, 0x3FFF):
            assert source == "visa-errors", code
        elif -239999 <= code <= -200000:
            assert source == "daqmx-wiki", code
        elif code in (-50103, -50251):
            assert source == "nipal-errors", code
        else:
            assert source in ("labview-errors", "instrument-driver-1997"), code


def test_search_query_is_stripped() -> None:
    assert lverror.search(" ") == []
    assert lverror.search("  timeout expired  ") == lverror.search("timeout expired")


def test_limit_is_checked_even_for_an_empty_query() -> None:
    with pytest.raises(ValueError):
        lverror.search("", limit=-1)
    with pytest.raises(TypeError):
        lverror.search("", limit="3")  # type: ignore[arg-type]


def test_no_action_exits_two_with_usage() -> None:
    result = run_cli()
    assert result.returncode == 2
    assert result.stdout == "" and result.stderr.startswith("usage: lverror")


@pytest.mark.parametrize("name", ["analysis VI", "data acquisition VI", "user-defined"])
def test_family_without_documented_codes_exits_one(name: str) -> None:
    result = run_cli("--family", name)
    assert (result.returncode, result.stdout) == (1, "")
    result = run_cli("--family", name, "--json")
    assert result.returncode == 1 and json.loads(result.stdout) == []
