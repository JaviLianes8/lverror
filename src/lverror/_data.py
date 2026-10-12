"""Baked-in LabVIEW and NI error data: NI's own message text and the documented code ranges.

Every message is NI's text for the code, word for word, read from ``_messages.json``. That file
is built by ``scripts/build_messages.py`` from sources captured in ``tests/fixtures/sources``:
the error files that LabVIEW 2026 and NI-VISA install, the LabVIEW Wiki NI-DAQmx error page,
and NI's 1997 instrument driver table. No message is written by hand; a code absent from
those sources carries no message and is classified only by the range it falls in.
"""

from __future__ import annotations

import json
from importlib import resources


def _load() -> tuple[dict[int, str], frozenset[int]]:
    raw = resources.files(__package__).joinpath("_messages.json").read_text(encoding="utf-8")
    messages: dict[int, str] = {}
    visa: set[int] = set()
    for code, source, text in json.loads(raw)["messages"]:
        if code in messages:
            raise ValueError(f"duplicate error code in the data file: {code}")
        messages[code] = text
        if source == "visa-errors":
            visa.add(code)
    return messages, frozenset(visa)


# code -> NI's description, from the sources named above.
MESSAGES: dict[int, str]
_VISA_CODES: frozenset[int]
MESSAGES, _VISA_CODES = _load()

# Positive codes that are warnings or completions, not errors (the VISA completion family).
WARNING_CODES: frozenset[int] = frozenset(c for c in _VISA_CODES if c > 0)

# Positive codes that denote errors, not warnings. LabVIEW's legacy general, network and DDE
# families number some errors with positive values, against the usual "positive means warning"
# convention; the VISA completion codes above are the positive values that are not errors.
POSITIVE_ERROR_CODES: frozenset[int] = frozenset(c for c in MESSAGES if c > 0) - WARNING_CODES

# Numeric ranges, most specific first. Each tuple is (low, high, family); the first match wins,
# so a code shared by two families (NI notes that 65 is both a serial and a network code)
# reports the more specific one. Sources, all captured in tests/fixtures/sources:
# - user-defined: NI "Ranges of LabVIEW Error Codes" (ni-ranges.txt).
# - analysis VI, data acquisition VI, AppleEvent, instrument driver ("-1200 to -13xx"), PPC,
#   network ("TCP/IP and UDP", 53 to 66) and DDE: the range table of NI's 1997 "LabVIEW Error
#   Codes" manual.
# - Derived, not quoted: VISA is every code whose high 16 bits are 0xBFFF (errors) or 0x3FFF
#   (completions), which holds for every code in the installed NI-VISA error file (VISA's
#   success code 0 aside); NI-DAQmx covers the NI-DAQmx row of the LabVIEW Wiki family range
#   table, which runs from -239999 to 215501; general LabVIEW covers the positive codes of the
#   LabVIEW row of that table up to its SMTP block ending at 16554.
RANGES: tuple[tuple[int, int, str], ...] = (
    (-1073807360, -1073741825, "VISA"),
    (-239999, -200000, "NI-DAQmx"),
    (-20065, -20001, "analysis VI"),
    (-10943, -10001, "data acquisition VI"),
    (-8999, -8000, "user-defined"),
    (-1719, -1700, "AppleEvent"),
    (-1399, -1200, "instrument driver"),
    (-932, -900, "PPC"),
    (53, 66, "network"),
    (5000, 9999, "user-defined"),
    (14001, 14020, "DDE"),
    (200000, 239999, "NI-DAQmx"),
    (500000, 599999, "user-defined"),
    (1073676288, 1073741823, "VISA"),
    (1, 16999, "general LabVIEW"),
)
