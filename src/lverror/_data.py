"""Baked-in LabVIEW and NI error data, compiled from public sources.

Messages are compiled from public National Instruments documentation (the NI "LabVIEW Error
Codes", "General LabVIEW Error Codes" and NI-VISA references, and the NI-DAQmx knowledge
base) and the community LabVIEW Wiki error-code pages. No message is invented: a code absent
from those sources carries no message and is classified only by the range it falls in. The
same integer can mean different things in different LabVIEW subsystems; the general LabVIEW
meaning is used as the default for small positive codes.
"""

from __future__ import annotations

from ._daqmx import DAQMX
from ._families import FAMILIES
from ._general_adv_a import GENERAL_ADV_A
from ._general_adv_b import GENERAL_ADV_B
from ._general_adv_c import GENERAL_ADV_C
from ._general_low import GENERAL_LOW
from ._general_vi_a import GENERAL_VI_A
from ._general_vi_b import GENERAL_VI_B
from ._visa import VISA, VISA_WARNING_CODES

_PARTS: tuple[dict[int, str], ...] = (
    GENERAL_LOW,
    GENERAL_VI_A,
    GENERAL_VI_B,
    GENERAL_ADV_A,
    GENERAL_ADV_B,
    GENERAL_ADV_C,
    VISA,
    DAQMX,
    FAMILIES,
)


def _merge(parts: tuple[dict[int, str], ...]) -> dict[int, str]:
    merged: dict[int, str] = {}
    for part in parts:
        for code, message in part.items():
            if code in merged:
                raise ValueError(f"duplicate error code across data modules: {code}")
            merged[code] = message
    return merged


# code -> human description, compiled from the public sources named above.
MESSAGES: dict[int, str] = _merge(_PARTS)

# Positive codes that are warnings or completions, not errors (the VISA completion family).
WARNING_CODES: frozenset[int] = VISA_WARNING_CODES

# Positive codes that denote errors, not warnings. LabVIEW's legacy general, network and DDE
# families number some errors with positive values, against the usual "positive means warning"
# convention; the VISA completion codes above are the positive values that are not errors.
POSITIVE_ERROR_CODES: frozenset[int] = frozenset(c for c in MESSAGES if c > 0) - WARNING_CODES

# Documented numeric ranges, most specific first. Each tuple is (low, high, family).
# Sources: NI "Ranges of LabVIEW Error Codes" (families and the custom-code ranges) and the
# NI "LabVIEW Error Codes" manual. Some codes belong to more than one family (NI notes, for
# example, that 65 is both a serial and a network code); the first match wins, so the more
# specific family is the one reported.
RANGES: tuple[tuple[int, int, str], ...] = (
    (-1073807360, -1073807231, "VISA"),
    (-209999, -200000, "NI-DAQmx"),
    (-20065, -20001, "analysis VI"),
    (-10943, -10001, "data acquisition VI"),
    (-8999, -8000, "user-defined"),
    (-1719, -1700, "AppleEvent"),
    (-1399, -1200, "instrument driver"),
    (-932, -900, "PPC"),
    (53, 66, "network"),
    (5000, 9999, "user-defined"),
    (14001, 14020, "DDE"),
    (200000, 209999, "NI-DAQmx"),
    (500000, 599999, "user-defined"),
    (1, 16000, "general LabVIEW"),
)
