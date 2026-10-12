"""Rebuild src/lverror/_messages.json from the captured NI sources in tests/fixtures/sources.

    python scripts/build_messages.py

Every message is NI's own text, taken from the first source that carries the code: the
NI-VISA error file for VISA codes, then the LabVIEW 2026 error file, the NI-PAL error file,
the LabVIEW Wiki NI-DAQmx page and the 1997 instrument driver table. Only the source prefix
(such as ``LabVIEW: (Hex 0x7)``) and NI's ``<b>`` bold tags are removed, and runs of
whitespace become one space. When a file lists one code twice, both texts are kept, joined
by ``Also:``, as NI documents two meanings for it. The code set is the one already shipped;
this script never adds a code.
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
    text = text.replace("<b>", "").replace("</b>", "")
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


def main() -> int:
    current = json.loads(TARGET.read_text(encoding="utf-8"))
    codes = sorted(int(entry[0]) for entry in current["messages"])
    entries = build(codes)
    lines = [json.dumps(entry, ensure_ascii=False) for entry in entries]
    head = json.dumps(DESCRIPTIONS, indent=1, ensure_ascii=False)
    body = '{\n"sources": ' + head + ',\n"messages": [\n' + ",\n".join(lines) + "\n]\n}\n"
    TARGET.write_text(body, encoding="utf-8", newline="\n")
    print(f"wrote {len(entries)} messages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
