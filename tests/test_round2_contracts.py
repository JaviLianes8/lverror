"""Contracts from the second blind mutation round: the shipped error list and short messages."""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path

import lverror

_FIXTURE = Path(__file__).parent / "fixtures" / "sources" / "labview-positive-codes.txt"


def _fixture_errors() -> set[int]:
    pairs = (line.split() for line in _FIXTURE.read_text(encoding="utf-8").splitlines())
    return {int(code) for code, kind in pairs if kind == "error"}


def test_shipped_error_list_is_exactly_the_fixture_list() -> None:
    raw = resources.files("lverror").joinpath("_messages.json").read_text(encoding="utf-8")
    assert set(json.loads(raw)["positive_errors"]) == _fixture_errors()


def test_unlisted_positive_codes_are_warnings() -> None:
    errors, shipped = _fixture_errors(), set(lverror.codes())
    for code in range(1, 17000):
        if code not in errors and code not in shipped:
            assert lverror.is_warning(code) and not lverror.is_error(code), code


class _Sub(int):
    pass


class _BadRepr:
    def __repr__(self) -> str:
        raise RuntimeError("no repr")


def _message(key: object) -> str:
    return str(lverror.UnknownCodeError(key))


def test_unknown_code_error_without_arguments_is_empty() -> None:
    assert str(lverror.UnknownCodeError()) == ""


def test_integers_up_to_64_bits_are_shown_and_larger_ones_summarised() -> None:
    assert _message(2**64 - 1) == "18446744073709551615"
    assert _message(2**64) == "<int of 65 bits>"
    assert _message(-(2**65)) == "<int of 66 bits>"
    assert _message(_Sub(2**65)) == "<int of 66 bits>"
    assert _message(10**5000) == "<int of 16610 bits>"


def test_a_key_whose_repr_fails_is_named_by_its_type() -> None:
    assert _message(_BadRepr()) == "<_BadRepr object>"
    try:
        lverror.TABLE[_BadRepr()]  # type: ignore[index]
    except lverror.UnknownCodeError as exc:
        assert str(exc) == "<_BadRepr object>"
    else:
        raise AssertionError("a non-code key must be missing")


def test_search_casefolds_as_documented() -> None:
    assert lverror.search(chr(0xDF)) == lverror.search("ss") != []
