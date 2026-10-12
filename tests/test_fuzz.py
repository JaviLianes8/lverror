"""Seeded fuzz and property tests: random codes and text never crash and stay consistent.

Each property is checked against a brute-force reference written here, not against the
library's own helpers, over thousands of seeded random inputs.
"""

from __future__ import annotations

import random
import string
import time

import lverror
from lverror._data import MESSAGES, POSITIVE_ERROR_CODES, RANGES

SEED = 20261012
INT32 = (-(2**31), 2**31 - 1)


def _codes(count: int) -> list[int]:
    rng = random.Random(SEED)
    documented = sorted(MESSAGES)
    picks = [rng.randint(*INT32) for _ in range(count)]
    picks += [rng.choice(documented) + rng.randint(-3, 3) for _ in range(count)]
    picks += [low for low, _, _ in RANGES] + [high for _, high, _ in RANGES]
    picks += [low - 1 for low, _, _ in RANGES] + [high + 1 for _, high, _ in RANGES]
    return [c for c in picks if INT32[0] <= c <= INT32[1]]


def _family(code: int) -> str | None:
    return next((name for low, high, name in RANGES if low <= code <= high), None)


def test_describe_agrees_with_a_brute_force_reference() -> None:
    for code in _codes(4000):
        info = lverror.describe(code)
        assert info.code == code
        assert info.message == MESSAGES.get(code)
        assert info.family == _family(code)
        assert info.is_error == (code < 0 or code in POSITIVE_ERROR_CODES)
        assert info.is_warning == (code > 0 and code not in POSITIVE_ERROR_CODES)
        assert not (info.is_error and info.is_warning)
        assert (info.is_error or info.is_warning) == (code != 0)


def test_nearest_agrees_with_a_brute_force_reference() -> None:
    documented = sorted(MESSAGES)
    for code in _codes(500):
        best = min(documented, key=lambda known: (abs(known - code), known))
        assert lverror.nearest(code).code == best


def test_format_line_is_one_line_that_parses_back() -> None:
    for code in _codes(2000):
        line = lverror.format_line(code)
        assert "\n" not in line and "\r" not in line
        assert lverror.parse_code(line.split(" ", 1)[0]) == code


def test_parse_code_round_trips_decimal_and_hex() -> None:
    for code in _codes(3000):
        assert lverror.parse_code(str(code)) == code
        assert lverror.parse_code(f"  {code}\t") == code
        assert lverror.parse_code(hex(code & 0xFFFFFFFF)) == code
        assert lverror.parse_code(hex(code & 0xFFFFFFFF).upper().replace("0X", "0x")) == code
        if code >= 0:
            assert lverror.parse_code(f"+{code}") == code
            assert lverror.parse_code(hex(code)) == code
        else:
            assert lverror.parse_code("-" + hex(-code)) == code


def test_parse_code_random_text_raises_only_value_error() -> None:
    rng = random.Random(SEED)
    alphabet = string.printable + "٣ −﻿"
    for _ in range(20000):
        text = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 14)))
        try:
            value = lverror.parse_code(text)
        except ValueError:
            continue
        assert INT32[0] <= value <= INT32[1]
        assert text.strip().lstrip("+-")[:1].isdigit()


def test_search_matches_a_brute_force_reference() -> None:
    rng = random.Random(SEED)
    words = [w for text in MESSAGES.values() for w in text.split()]
    for _ in range(300):
        needle = rng.choice(words)[: rng.randint(1, 6)]
        if rng.random() < 0.3:
            needle = needle.upper()
        expected = sorted(c for c, m in MESSAGES.items() if needle.lower() in m.lower())
        assert [rec.code for rec in lverror.search(needle)] == expected


def test_search_on_random_text_never_crashes() -> None:
    rng = random.Random(SEED)
    for _ in range(2000):
        text = "".join(rng.choice(string.printable) for _ in range(rng.randint(0, 8)))
        for rec in lverror.search(text, limit=rng.randint(0, 5)):
            assert text.strip().casefold() in (rec.message or "").casefold()


def test_lookups_stay_fast_on_hostile_input() -> None:
    start = time.perf_counter()
    lverror.search("q" * 1_000_000)
    for text in ("9" * 1_000_000, "0x" + "f" * 1_000_000, " " * 1_000_000 + "7"):
        try:
            lverror.parse_code(text)
        except ValueError:
            pass
    assert time.perf_counter() - start < 5
