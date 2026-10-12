"""Refresh src/lverror/_messages.json from the captured NI sources in tests/fixtures/sources.

    python scripts/refresh_data.py

The messages themselves are written for this library and are kept as they are. For each code
this script records which captured source documents it (the NI-VISA error file for VISA codes,
then the LabVIEW 2026 error file, the NI-PAL error file, the LabVIEW Wiki NI-DAQmx page and the
1997 instrument driver table), refuses a message that repeats the source's wording (the same
words after normalisation, or six or more consecutive words in common), and rewrites the list
of positive codes NI's LabVIEW file lists as errors. It never adds a code.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "tests" / "fixtures" / "sources"
TARGET = ROOT / "src" / "lverror" / "_messages.json"
ENTRY = re.compile(r'<nierror code="(-?\d+)">(.*?)</nierror>', re.S)
PREFIX = re.compile(r"^[A-Za-z][\w .-]*: \(Hex 0x[0-9A-Fa-f]+\) ")
ROW = re.compile(r"^\| (-?\d+)[ \t]*\n\| (.*?)(?=^\|[-}]|\Z)", re.S | re.M)
ENTITIES = {"&lt;": "<", "&gt;": ">", "&quot;": '"', "&apos;": "'", "&amp;": "&"}
VISA_HIGH_WORDS = (0xBFFF, 0x3FFF)
DESCRIPTIONS = {
    "visa-errors": "NI-VISA error file installed with LabVIEW 2026",
    "labview-errors": "LabVIEW 2026 error file (resource/errors/English/LabVIEW-errors.txt)",
    "nipal-errors": "NI-PAL error file installed with LabVIEW 2026",
    "daqmx-wiki": "LabVIEW Wiki, NI-DAQmx Error Code Family page",
    "instrument-driver-1997": "NI LabVIEW Error Codes manual, May 1997, Table 5",
}


def _clean(text: str) -> str:
    # NI marks control and menu names in bold; the tags are presentation, not text.
    text = re.sub(r"</?[bB]>", "", text)
    for entity, char in ENTITIES.items():
        text = text.replace(entity, char)
    text = " ".join(text.split())
    return PREFIX.sub("", text, count=1)


def _xml(name: str) -> dict[int, list[str]]:
    found: dict[int, list[str]] = {}
    text = (SOURCES / f"{name}.xml").read_text(encoding="utf-8")
    for code, body in ENTRY.findall(text):
        found.setdefault(int(code), []).append(_clean(body))
    return found


def _wiki() -> dict[int, list[str]]:
    text = (SOURCES / "daqmx-wiki.txt").read_text(encoding="utf-8")
    found = {int(code): [" ".join(body.split())] for code, body in ROW.findall(text)}
    for code, texts in found.items():
        if re.search(r"[\[\]{}<>]|''", texts[0]):
            raise ValueError(f"wiki markup left in the text of {code}")
    return found


def _manual() -> dict[int, list[str]]:
    pairs = json.loads((SOURCES / "instrument-driver-1997-pairs.json").read_text("utf-8"))
    return {int(code): [text] for code, text in pairs["pairs"]}


def _positive_errors() -> list[int]:
    # Positive codes NI's LabVIEW file lists as errors, shipped as numbers only, so that
    # is_error is right for them even when their text is not shipped.
    text = (SOURCES / "labview-positive-codes.txt").read_text(encoding="utf-8")
    pairs = [line.split() for line in text.splitlines()]
    return [int(code) for code, kind in pairs if kind == "error"]


def _is_visa(code: int) -> bool:
    return ((code & 0xFFFFFFFF) >> 16) in VISA_HIGH_WORDS


def build(codes: list[int]) -> list[list[object]]:
    tables = {
        "visa-errors": _xml("visa-errors"),
        "labview-errors": _xml("labview-errors"),
        "nipal-errors": _xml("nipal-errors"),
        "daqmx-wiki": _wiki(),
        "instrument-driver-1997": _manual(),
    }
    order = list(tables)
    entries: list[list[object]] = []
    for code in codes:
        names = order if _is_visa(code) else order[1:]
        source = next((name for name in names if code in tables[name]), None)
        if source is None:
            raise ValueError(f"no captured source carries code {code}")
        entries.append([code, source, " Also: ".join(tables[source][code])])
    return entries


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


def main() -> int:
    current = json.loads(TARGET.read_text(encoding="utf-8"))
    ours = {int(entry[0]): str(entry[2]) for entry in current["messages"]}
    entries: list[list[object]] = []
    for code, source, theirs in build(sorted(ours)):
        text = ours[code]
        if (
            _words(text) == _words(str(theirs))
            or _shared_run(_words(text), _words(str(theirs))) >= 6
        ):
            raise ValueError(f"the message for {code} repeats the wording of {source}")
        entries.append([code, source, text])
    lines = [json.dumps(entry, ensure_ascii=False) for entry in entries]
    head = json.dumps(DESCRIPTIONS, indent=1, ensure_ascii=False)
    errors = json.dumps(_positive_errors())
    body = (
        '{\n"sources": '
        + head
        + ',\n"positive_errors": '
        + errors
        + ',\n"messages": [\n'
        + ",\n".join(lines)
        + "\n]\n}\n"
    )
    TARGET.write_text(body, encoding="utf-8", newline="\n")
    print(f"refreshed {len(entries)} messages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
