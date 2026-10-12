"""Every shipped message is NI's own text, checked against the captured sources.

The sources live in ``tests/fixtures/sources`` with their origin in ``MANIFEST.json``: excerpts
of the error files LabVIEW 2026 and NI-VISA install (real program data), the LabVIEW Wiki
NI-DAQmx page and NI's 1997 instrument driver table (fetched from the URLs recorded there).
This parser is written independently of ``scripts/build_messages.py``: it locates each entry
by the ``(Hex 0x...)`` tag computed from the code itself, so a wrong code would not match.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import lverror
from lverror._data import MESSAGES

SOURCES = Path(__file__).parent / "fixtures" / "sources"
INSTALLED = {
    "labview-errors": Path(
        "C:/Program Files/National Instruments/LabVIEW 2026/resource/errors/English/"
        "LabVIEW-errors.txt"
    ),
    "visa-errors": Path(
        "C:/Program Files/National Instruments/Shared/Errors/English/VISA-errors.txt"
    ),
    "nipal-errors": Path(
        "C:/Program Files/National Instruments/Shared/Errors/English/nipal-errors.txt"
    ),
}


def _entries(name: str) -> dict[int, list[str]]:
    text = (SOURCES / f"{name}.xml").read_text(encoding="utf-8")
    found: dict[int, list[str]] = {}
    for chunk in text.split("</nierror>")[:-1]:
        head, _, body = chunk.partition('<nierror code="')[2].partition('">')
        code = int(head)
        flat = " ".join(body.replace("<b>", "").replace("</b>", "").split())
        tag = f"(Hex 0x{code & 0xFFFFFFFF:X}) "
        # NI-PAL entries carry no "<family>: (Hex ...)" prefix; the others must tag the code.
        assert tag in flat or (name == "nipal-errors" and "(Hex" not in flat), (name, code)
        found.setdefault(code, []).append(flat.split(tag, 1)[-1])
    return found


def _wiki_rows() -> dict[int, str]:
    text = (SOURCES / "daqmx-wiki.txt").read_text(encoding="utf-8")
    rows: dict[int, str] = {}
    for row in text.split("|-\n")[1:]:
        code_line, _, body = row.partition("\n")
        rows[int(code_line.lstrip("| "))] = " ".join(body.removesuffix("|}\n")[2:].split())
    return rows


def _manual_pairs() -> dict[int, str]:
    pairs = json.loads((SOURCES / "instrument-driver-1997-pairs.json").read_text("utf-8"))
    return {int(code): str(text) for code, text in pairs["pairs"]}


def _expected() -> dict[int, str]:
    visa, labview, nipal = (
        _entries("visa-errors"),
        _entries("labview-errors"),
        _entries("nipal-errors"),
    )
    wiki, manual = _wiki_rows(), _manual_pairs()
    expected: dict[int, str] = {}
    for code in MESSAGES:
        is_visa = (code & 0xFFFFFFFF) >> 16 in (0xBFFF, 0x3FFF)
        for table in ([visa] if is_visa else []) + [labview, nipal]:
            if code in table:
                expected[code] = " Also: ".join(table[code])
                break
        else:
            expected[code] = wiki[code] if code in wiki else manual[code]
    return expected


def test_every_message_is_the_text_of_its_source() -> None:
    expected = _expected()
    wrong = [code for code, text in MESSAGES.items() if text != expected[code]]
    assert wrong == []
    assert len(MESSAGES) == 888


def test_spot_checks_read_straight_from_the_sources() -> None:
    assert lverror.explain(7) == _entries("labview-errors")[7][0]
    assert lverror.explain(-1073807339) == _entries("visa-errors")[-1073807339][0]
    assert lverror.explain(-200279) == _wiki_rows()[-200279]
    assert lverror.explain(-1240) == "Instrument timed out"


def test_codes_listed_twice_keep_both_meanings() -> None:
    labview = _entries("labview-errors")
    for code in (2, 61, 62, 63, 64, 65):
        assert len(labview[code]) == 2
        assert lverror.explain(code) == f"{labview[code][0]} Also: {labview[code][1]}"


def test_the_manual_pairs_come_from_the_captured_table() -> None:
    table = " ".join((SOURCES / "instrument-driver-1997.txt").read_text("utf-8").split())
    lines = (SOURCES / "instrument-driver-1997.txt").read_text("utf-8").splitlines()
    listed = [int(line.split()[0]) for line in lines if re.match(r"-1[23]\d\d\b", line)]
    pairs = _manual_pairs()
    assert list(pairs) == listed
    for text in pairs.values():
        # One description wraps onto a second line, after the "Set By" column of its first.
        head, _, last = text.rpartition(" ")
        assert text in table or (f"{head} VISA Transition Library -1215 {last}" in table), text


def test_four_manual_pairs_agree_with_labview_2026() -> None:
    labview = _entries("labview-errors")
    for code, text in _manual_pairs().items():
        if code in labview:
            assert labview[code][0].rstrip(".").casefold() == text.casefold(), code
    assert sorted(set(_manual_pairs()) & set(labview)) == [-1300, -1236, -1223, -1210]


def test_manifest_records_the_origin_of_every_fixture() -> None:
    manifest = json.loads((SOURCES / "MANIFEST.json").read_text("utf-8"))["sources"]
    ids = {entry["id"] for entry in manifest}
    stems = {path.stem for path in SOURCES.iterdir() if path.suffix in (".xml", ".txt")}
    assert stems <= ids
    for entry in manifest:
        assert re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])
        assert entry["retrieved"] == "2026-10-12"
        assert entry["origin"].startswith(("https://", "C:\\Program Files\\National Instruments"))


@pytest.mark.parametrize("name", sorted(INSTALLED))
def test_excerpts_match_the_files_installed_on_this_machine(name: str) -> None:
    path = INSTALLED[name]
    if not path.is_file():
        pytest.skip(f"{path} is not installed here")
    live = path.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
    excerpt = (SOURCES / f"{name}.xml").read_text(encoding="utf-8")
    blocks = re.findall(r'<nierror code="-?\d+">.*?</nierror>', excerpt, re.S)
    assert blocks
    assert [block for block in blocks if block not in live] == []
