"""Error versus warning follows NI's LabVIEW file for every positive code it lists.

``labview-positive-codes.txt`` is derived (numbers only) from the LabVIEW 2026 error file:
each positive code it lists, marked ``warning`` when NI's text contains the word "warning".
On a machine with LabVIEW 2026 installed the derivation is re-run against the real file.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import lverror

SOURCES = Path(__file__).parent / "fixtures" / "sources"
if not (SOURCES / "labview-positive-codes.txt").is_file():
    # The NI texts are kept on the maintainer's machine only (scripts/capture_sources.py).
    pytest.skip("the captured NI sources are not present", allow_module_level=True)
LABVIEW = Path(
    "C:/Program Files/National Instruments/LabVIEW 2026/resource/errors/English/LabVIEW-errors.txt"
)


def _listed() -> dict[int, str]:
    text = (SOURCES / "labview-positive-codes.txt").read_text(encoding="utf-8")
    return {int(code): kind for code, kind in (line.split() for line in text.splitlines())}


def test_every_listed_positive_code_is_classified_as_nis_text_says() -> None:
    listed = _listed()
    assert len(listed) == 1027
    wrong = [
        code
        for code, kind in listed.items()
        if (lverror.is_error(code), lverror.is_warning(code))
        != (kind == "error", kind == "warning")
    ]
    assert wrong == []


def test_known_cases() -> None:
    assert lverror.is_error(1612) and lverror.explain(1612) is None
    assert lverror.is_error(14021) and lverror.is_error(14022)
    assert lverror.is_warning(40624)
    assert lverror.is_warning(200010)  # not in the LabVIEW file: a warning by convention


def test_every_shipped_labview_message_marks_the_same_kind() -> None:
    listed = _listed()
    for info in lverror.records():
        if info.code in listed:
            assert info.is_error == (listed[info.code] == "error"), info.code


def test_the_list_matches_the_installed_file() -> None:
    if not LABVIEW.is_file():
        pytest.skip("LabVIEW 2026 is not installed here")
    text = LABVIEW.read_text(encoding="utf-8")
    live: dict[int, str] = {}
    for code, body in re.findall(r'<nierror code="(\d+)">(.*?)</nierror>', text, re.S):
        if int(code) > 0:
            said = re.search(r"\bwarning\b", body, re.I) is not None
            warned = said or live.get(int(code)) == "warning"
            live[int(code)] = "warning" if warned else "error"
    assert live == _listed()
