"""Capture the raw NI source text for every shipped code into tests/fixtures/sources.

Run on a Windows machine with LabVIEW 2026 and NI-VISA installed and with network access:

    python scripts/capture_sources.py

It copies, byte for byte, the ``<nierror>`` entries of the shipped codes from the error files
that LabVIEW and NI-VISA install, the matching rows of the LabVIEW Wiki NI-DAQmx error page,
and the instrument driver table of NI's 1997 "LabVIEW Error Codes" manual, and records the
origin of each (path or URL, size, SHA-256, retrieval date) in MANIFEST.json. The code list is
read from the shipped data file, so the capture never adds a code on its own.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "fixtures" / "sources"
NI = Path("C:/Program Files/National Instruments")
INSTALLED = {
    "labview-errors": NI / "LabVIEW 2026/resource/errors/English/LabVIEW-errors.txt",
    "visa-errors": NI / "Shared/Errors/English/VISA-errors.txt",
    "nipal-errors": NI / "Shared/Errors/English/nipal-errors.txt",
}
DAQMX_URL = "https://labviewwiki.org/w/index.php?title=NI-DAQmx_Error_Code_Family&action=raw"
FAMILIES_URL = "https://labviewwiki.org/w/index.php?title=List_of_errors&action=raw"
FAMILY_ROWS = ("LabVIEW", "NI-DAQmx", "VISA")
MANUAL_URL = "https://www.apexwaves.com/pdf/manuals/SC-2040/archived--labview-error-codes.pdf"
RANGES_URL = (
    "https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/"
    "ranges-of-labview-error-codes.html"
)
# NI's documentation site only renders its text server side for crawlers.
CRAWLER = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
ENTRY = re.compile(rb'<nierror code="(-?\d+)">.*?</nierror>', re.S)
ROW = re.compile(r"^\| (-?\d+)[ \t]*\n\| (.*?)(?=^\|[-}])", re.S | re.M)


def _fetch(url: str, agent: str = "Mozilla/5.0") -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": agent})
    with urllib.request.urlopen(request, timeout=60) as response:
        return bytes(response.read())


def _record(source_id: str, origin: str, data: bytes, note: str) -> dict[str, object]:
    return {
        "id": source_id,
        "origin": origin,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "retrieved": datetime.date.today().isoformat(),
        "note": note,
    }


def _installed(codes: set[int], manifest: list[dict[str, object]]) -> None:
    for source_id, path in INSTALLED.items():
        data = path.read_bytes()
        blocks = [m.group(0) for m in ENTRY.finditer(data) if int(m.group(1)) in codes]
        body = b"<nidocument>\n" + b"\n".join(blocks) + b"\n</nidocument>\n"
        (OUT / f"{source_id}.xml").write_bytes(body)
        note = "excerpt: the <nierror> entries of the shipped codes, copied byte for byte"
        manifest.append(_record(source_id, str(path), data, note))


def _daqmx(codes: set[int], manifest: list[dict[str, object]]) -> None:
    data = _fetch(DAQMX_URL)
    rows = [m.group(0) for m in ROW.finditer(data.decode("utf-8")) if int(m.group(1)) in codes]
    table = "|-\n" + "|-\n".join(rows) + "|}\n"
    (OUT / "daqmx-wiki.txt").write_text(table, encoding="utf-8", newline="\n")
    note = "excerpt: the wikitext rows of the shipped NI-DAQmx codes, copied verbatim"
    manifest.append(_record("daqmx-wiki", DAQMX_URL, data, note))


def _families(manifest: list[dict[str, object]]) -> None:
    data = _fetch(FAMILIES_URL)
    text = data.decode("utf-8")
    rows = []
    for name in FAMILY_ROWS:
        pattern = r"^\| \[\[" + re.escape(name) + r" Error Code Family\|.*\n\| .*\n"
        found = re.search(pattern, text, re.M)
        if found is None:
            raise ValueError(f"family row not found: {name}")
        rows.append(found.group(0))
    table = "|-\n" + "|-\n".join(rows) + "|}\n"
    (OUT / "wiki-families.txt").write_text(table, encoding="utf-8", newline="\n")
    note = "excerpt: the LabVIEW, NI-DAQmx and VISA rows of the family range table"
    manifest.append(_record("wiki-families", FAMILIES_URL, data, note))


def _manual(manifest: list[dict[str, object]]) -> None:
    data = _fetch(MANUAL_URL)
    with tempfile.TemporaryDirectory() as tmp:
        pdf = Path(tmp) / "manual.pdf"
        pdf.write_bytes(data)
        text = subprocess.run(
            ["pdftotext", "-layout", str(pdf), "-"], capture_output=True, check=True
        ).stdout.decode("latin-1")
    start = text.index("Table 5. Instrument Driver Error Codes")
    end = text.index("Instrument-specific error", start) + len("Instrument-specific error")
    # pdftotext writes the minus signs of this PDF as soft hyphens.
    excerpt = text[start:end].replace("\xad", "-").replace("\r", "")
    (OUT / "instrument-driver-1997.txt").write_text(excerpt + "\n", encoding="utf-8")
    note = "excerpt: Table 5 as extracted by pdftotext -layout (part number 321551A-01)"
    manifest.append(_record("instrument-driver-1997", MANUAL_URL, data, note))


def _ranges(manifest: list[dict[str, object]]) -> None:
    data = _fetch(RANGES_URL, CRAWLER)
    page = re.sub(r"<script.*?</script>|<style.*?</style>", "", data.decode("utf-8"), flags=re.S)
    text = " ".join(re.sub(r"<[^>]+>", " ", page).split())
    start = text.index("You can define custom error codes")
    end = text.index("already established.", start) + len("already established.")
    (OUT / "ni-ranges.txt").write_text(text[start:end] + "\n", encoding="utf-8")
    note = "excerpt: the custom-range and shared-code sentences of the page text"
    manifest.append(_record("ni-ranges", RANGES_URL, data, note))


def main() -> int:
    shipped = json.loads((ROOT / "src" / "lverror" / "_messages.json").read_text("utf-8"))
    codes = {int(entry[0]) for entry in shipped["messages"]}
    OUT.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, object]] = []
    _installed(codes, manifest)
    _daqmx(codes, manifest)
    _families(manifest)
    _manual(manifest)
    _ranges(manifest)
    text = json.dumps({"sources": manifest}, indent=2) + "\n"
    (OUT / "MANIFEST.json").write_text(text, encoding="utf-8")
    print(f"captured {len(manifest)} sources for {len(codes)} codes", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
