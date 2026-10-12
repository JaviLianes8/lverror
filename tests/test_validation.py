"""Every public function rejects bad arguments the same way, with short, typed errors."""

from __future__ import annotations

import enum
from collections.abc import Callable

import pytest

import lverror

CODE_FUNCTIONS: list[Callable[[int], object]] = [
    lverror.explain,
    lverror.describe,
    lverror.is_known,
    lverror.family,
    lverror.is_error,
    lverror.is_warning,
    lverror.nearest,
    lverror.format_line,
]
NAMES = [f.__name__ for f in CODE_FUNCTIONS]


class Index:
    """An integer-like object, as NumPy integers are: it only offers ``__index__``."""

    def __init__(self, value: int) -> None:
        self.value = value

    def __index__(self) -> int:
        return self.value


class Code(enum.IntEnum):
    FILE_NOT_FOUND = 7


@pytest.mark.parametrize("function", CODE_FUNCTIONS, ids=NAMES)
@pytest.mark.parametrize("bad", [True, False, 7.0, "7", None, b"7", [7]])
def test_code_functions_refuse_non_integers(
    function: Callable[[object], object], bad: object
) -> None:
    with pytest.raises(TypeError, match="must be an integer"):
        function(bad)


@pytest.mark.parametrize("function", CODE_FUNCTIONS, ids=NAMES)
@pytest.mark.parametrize(
    "bad", [2**31, -(2**31) - 1, 10**5000, -(10**5000)], ids=["above", "below", "huge", "-huge"]
)
def test_code_functions_refuse_values_outside_int32(
    function: Callable[[int], object], bad: int
) -> None:
    with pytest.raises(ValueError, match="signed 32-bit range") as caught:
        function(bad)
    assert len(str(caught.value)) < 80


@pytest.mark.parametrize("function", CODE_FUNCTIONS, ids=NAMES)
@pytest.mark.parametrize("edge", [2**31 - 1, -(2**31)])
def test_code_functions_accept_the_int32_limits(
    function: Callable[[int], object], edge: int
) -> None:
    function(edge)


@pytest.mark.parametrize("function", CODE_FUNCTIONS, ids=NAMES)
def test_integer_like_codes_behave_like_ints(function: Callable[[object], object]) -> None:
    assert function(Index(7)) == function(7)
    assert function(Code.FILE_NOT_FOUND) == function(7)


def test_describe_stores_a_plain_int() -> None:
    assert type(lverror.describe(Index(7)).code) is int
    assert type(lverror.describe(Code.FILE_NOT_FOUND).code) is int
    assert lverror.format_line(Code.FILE_NOT_FOUND).startswith("7 (error")


@pytest.mark.parametrize("bad", [7, None, b"timeout"])
def test_search_refuses_non_text(bad: object) -> None:
    with pytest.raises(TypeError, match="search text must be a str"):
        lverror.search(bad)  # type: ignore[arg-type]


@pytest.mark.parametrize("bad", [True, 1.5, "3"])
def test_search_refuses_a_non_integer_limit(bad: object) -> None:
    with pytest.raises(TypeError, match="limit must be an integer"):
        lverror.search("file", limit=bad)  # type: ignore[arg-type]


def test_search_refuses_a_negative_limit() -> None:
    with pytest.raises(ValueError, match="zero or more"):
        lverror.search("file", limit=-1)


def test_search_limit_edges() -> None:
    assert lverror.search("file", limit=0) == []
    assert lverror.search("file", limit=Index(1)) == lverror.search("file")[:1]
    assert lverror.search("", limit=-0) == []


@pytest.mark.parametrize("bad", [7, None, b"DDE"])
def test_in_family_refuses_non_text(bad: object) -> None:
    with pytest.raises(TypeError, match="family name must be a str"):
        lverror.in_family(bad)  # type: ignore[arg-type]


def test_unknown_family_message_stays_short() -> None:
    with pytest.raises(ValueError, match="unknown family") as caught:
        lverror.in_family("x" * 100_000)
    assert len(str(caught.value)) < 400


@pytest.mark.parametrize("bad", [7, None, b"7"])
def test_parse_code_refuses_non_text(bad: object) -> None:
    with pytest.raises(TypeError, match="code text must be a str"):
        lverror.parse_code(bad)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "bad",
    ["", "  ", "7.0", "1_000", "0x", "x7", "7 8", "--7", "0b101", "٣", "0x٣", "1e3"],
)
def test_parse_code_refuses_malformed_text(bad: str) -> None:
    with pytest.raises(ValueError):
        lverror.parse_code(bad)


@pytest.mark.parametrize("bad", ["2147483648", "-2147483649", "0x100000000", "-0xBFFF0015"])
def test_parse_code_refuses_values_outside_int32(bad: str) -> None:
    with pytest.raises(ValueError, match="signed 32-bit range"):
        lverror.parse_code(bad)


def test_parse_code_messages_never_echo_huge_input() -> None:
    for text in ("9" * 100_000, "0x" + "F" * 100_000, "z" * 100_000):
        with pytest.raises(ValueError) as caught:
            lverror.parse_code(text)
        assert len(str(caught.value)) < 100


@pytest.mark.parametrize("key", [True, False, "7", 7.0, None, 2**40, Index(-200300)])
def test_table_treats_non_codes_as_missing(key: object) -> None:
    assert key not in lverror.TABLE
    assert lverror.TABLE.get(key) is None  # type: ignore[call-overload]
    with pytest.raises(lverror.UnknownCodeError):
        lverror.TABLE[key]  # type: ignore[index]


def test_table_accepts_integer_like_keys() -> None:
    assert Index(7) in lverror.TABLE  # type: ignore[comparison-overlap]
    assert lverror.TABLE[Index(7)] == lverror.TABLE[7]


def test_unknown_code_error_message_stays_short() -> None:
    for key in (10**5000, "x" * 1_000_000, -200300):
        with pytest.raises(lverror.UnknownCodeError) as caught:
            lverror.TABLE[key]  # type: ignore[index]
        assert len(str(caught.value)) < 60
        assert caught.value.args == (key,)
    assert str(lverror.UnknownCodeError(-200300)) == "-200300"


def test_table_index_type_accepts_integer_like_keys_statically() -> None:
    assert lverror.TABLE[Index(14001)].message == "The refnum is not valid."
