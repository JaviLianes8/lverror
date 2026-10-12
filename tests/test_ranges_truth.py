"""The range table agrees with the captured sources it cites.

Quoted ranges come from NI's "Ranges of LabVIEW Error Codes" page (user-defined codes) and
the range table of NI's 1997 "LabVIEW Error Codes" manual. The VISA, NI-DAQmx and general
LabVIEW ranges are derived, not quoted; the tests check the derivation against the LabVIEW
Wiki family table and the installed NI-VISA error file excerpt.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import lverror
from lverror._data import RANGES

SOURCES = Path(__file__).parent / "fixtures" / "sources"
if not (SOURCES / "wiki-families.txt").is_file():
    # The NI texts are kept on the maintainer's machine only (scripts/capture_sources.py).
    pytest.skip("the captured NI sources are not present", allow_module_level=True)


def _ranges_named(name: str) -> list[tuple[int, int]]:
    return [(low, high) for low, high, family in RANGES if family == name]


def _covered(name: str, low: int, high: int) -> bool:
    return any(a <= low and high <= b for a, b in _ranges_named(name))


def _wiki_row(family: str) -> list[tuple[int, int]]:
    text = (SOURCES / "wiki-families.txt").read_text(encoding="utf-8")
    line = re.search(rf"\|{re.escape(family)}\]\]\n\| (.*)\n", text)
    assert line is not None, family
    spans = []
    for part in line.group(1).split(","):
        bounds = [int(value) for value in part.split(" to ")]
        spans.append((bounds[0], bounds[-1]))
    return spans


def test_user_defined_ranges_are_the_ones_ni_documents() -> None:
    text = (SOURCES / "ni-ranges.txt").read_text(encoding="utf-8").replace(chr(0x2013), "-")
    found = re.findall(r"(-?[\d,]+) through (-?[\d,]+)", text)
    quoted = sorted((int(a.replace(",", "")), int(b.replace(",", ""))) for a, b in found)
    ours = sorted((min(low, high), max(low, high)) for low, high in _ranges_named("user-defined"))
    assert sorted((min(a, b), max(a, b)) for a, b in quoted) == ours


def test_quoted_ranges_match_the_1997_table() -> None:
    text = (SOURCES / "ranges-1997.txt").read_text(encoding="utf-8")
    rows = {
        name.strip(): (int(low), high)
        for low, high, name in re.findall(r"(-?\d+)\s+to\s+(-?\w+)\s+(.+?) Error Codes", text)
    }
    expected = {
        "Analysis VI": "analysis VI",
        "Data Acquisition VI": "data acquisition VI",
        "AppleEvent": "AppleEvent",
        "PPC": "PPC",
        "TCP/IP and UDP": "network",
        "DDE": "DDE",
    }
    for title, family in expected.items():
        low, high = rows[title]
        assert sorted((low, int(high))) in [sorted(span) for span in _ranges_named(family)]
    low, high = rows["Instrument Driver"]
    assert (low, high) == (-1200, "-13xx")
    assert _ranges_named("instrument driver") == [(-1399, -1200)]


def test_every_installed_visa_code_falls_in_the_visa_ranges() -> None:
    excerpt = (SOURCES / "visa-errors.xml").read_text(encoding="utf-8")
    visa = [int(code) for code in re.findall(r'<nierror code="(-?\d+)">', excerpt)]
    assert visa and all(lverror.family(code) == "VISA" for code in visa)
    for low, high in [span for span in _wiki_row("VISA") if span != (0, 0)]:
        assert _covered("VISA", low, high), (low, high)


def test_visa_ranges_are_the_two_visa_high_words() -> None:
    assert sorted(_ranges_named("VISA")) == [
        (0xBFFF0000 - (1 << 32), 0xBFFFFFFF - (1 << 32)),
        (0x3FFF0000, 0x3FFFFFFF),
    ]


def test_ni_daqmx_ranges_hold_every_daqmx_family_span() -> None:
    spans = _wiki_row("NI-DAQmx")
    assert min(low for low, _ in spans) == -239999
    assert max(high for _, high in spans) == 215501
    for low, high in spans:
        assert _covered("NI-DAQmx", low, high), (low, high)


def test_positive_labview_codes_below_17000_all_have_a_family() -> None:
    spans = [(low, high) for low, high in _wiki_row("LabVIEW") if low > 0 and high < 17000]
    assert max(high for _, high in spans) == 16554
    for low, high in spans:
        assert all(lverror.family(code) is not None for code in range(low, high + 1))
    assert lverror.family(17000) is None
