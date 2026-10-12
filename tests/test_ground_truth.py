"""Every shipped message matches a code NI documents, in this library's own words.

The NI sources live in ``tests/fixtures/sources`` with their origin in ``MANIFEST.json``:
excerpts of the error files LabVIEW 2026, NI-VISA and NI-PAL install (real program data), the
LabVIEW Wiki NI-DAQmx page and NI's 1997 instrument driver table (fetched from the URLs recorded
there). They are test-side references only and are not distributed. Each shipped code must be
documented by one of them, and no shipped message may repeat the source's wording: not the same
words after normalising case and punctuation, and no run of six or more consecutive words in
common. The parser locates each entry by the ``(Hex 0x...)`` tag computed from the code itself.
"""

from __future__ import annotations

import difflib
import json
import re
from pathlib import Path

import pytest

import lverror
from lverror._data import MESSAGES

SOURCES = Path(__file__).parent / "fixtures" / "sources"
if not SOURCES.is_dir():
    pytest.skip("the captured NI sources are not distributed", allow_module_level=True)
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


def _words(text: str) -> list[str]:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).split()


def _shared_run(ours: list[str], theirs: list[str]) -> int:
    best, prev = 0, [0] * (len(theirs) + 1)
    for word in ours:
        cur = [0] * (len(theirs) + 1)
        for j, other in enumerate(theirs, 1):
            if word == other:
                cur[j] = prev[j - 1] + 1
                best = max(best, cur[j])
        prev = cur
    return best


def test_every_shipped_code_is_documented_by_a_captured_source() -> None:
    expected = _expected()
    assert sorted(expected) == sorted(MESSAGES)
    assert len(MESSAGES) == 888


def _similarity(ours: str, theirs: str) -> float:
    return difflib.SequenceMatcher(None, " ".join(_words(ours)), " ".join(_words(theirs))).ratio()


def test_no_message_repeats_the_wording_of_its_source() -> None:
    expected = _expected()
    same = [c for c, text in MESSAGES.items() if _words(text) == _words(expected[c])]
    assert same == []
    long_runs = [
        c for c, text in MESSAGES.items() if _shared_run(_words(text), _words(expected[c])) >= 6
    ]
    assert long_runs == []
    close = [c for c, text in MESSAGES.items() if _similarity(text, expected[c]) >= 0.75]
    assert close == []


def test_no_message_repeats_a_sentence_of_any_captured_entry() -> None:
    # Across codes, short stock phrases ("does not match the data type") are fine; eight
    # consecutive words would be a copied sentence.
    grams: set[tuple[str, ...]] = set()
    for text in _expected().values():
        words = _words(text)
        grams.update(tuple(words[i : i + 8]) for i in range(len(words) - 7))
    hits = []
    for code, text in MESSAGES.items():
        words = _words(text)
        if any(tuple(words[i : i + 8]) in grams for i in range(len(words) - 7)):
            hits.append(code)
    assert hits == []


def test_the_overlap_check_bites() -> None:
    theirs = _words("Timeout expired before operation completed.")
    assert _words("timeout EXPIRED, before operation completed") == theirs
    assert _shared_run(_words("a b c d e f g"), _words("x b c d e f g y")) == 6
    assert _similarity("The pen does not exist.", "Pen does not exist.") >= 0.75


def test_every_entry_is_tagged_with_the_source_that_documents_it() -> None:
    raw = (Path(lverror.__file__).parent / "_messages.json").read_text(encoding="utf-8")
    visa, labview, nipal = (
        _entries("visa-errors"),
        _entries("labview-errors"),
        _entries("nipal-errors"),
    )
    wiki, manual = _wiki_rows(), _manual_pairs()
    for code, source, _text in json.loads(raw)["messages"]:
        is_visa = (code & 0xFFFFFFFF) >> 16 in (0xBFFF, 0x3FFF)
        found = next(
            name
            for name, table in (
                ("visa-errors", visa if is_visa else {}),
                ("labview-errors", labview),
                ("nipal-errors", nipal),
                ("daqmx-wiki", wiki),
                ("instrument-driver-1997", manual),
            )
            if code in table
        )
        assert source == found, code


def test_codes_listed_twice_keep_both_meanings() -> None:
    labview = _entries("labview-errors")
    for code in (2, 61, 62, 63, 64, 65):
        assert len(labview[code]) == 2
        assert " Also: " in (lverror.explain(code) or "")


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
