"""Human formatting and input parsing for codes.

``format_line`` renders one record as a single line for logs or a terminal. ``parse_code``
accepts the decimal and hexadecimal spellings a user is likely to paste, including the hex
form NI's Explain Error dialog shows for VISA codes.
"""

from __future__ import annotations

import re
from typing import SupportsIndex

from ._core import describe
from ._validate import INT32_MAX, INT32_MIN, as_text, shorten

_UINT32 = 1 << 32
_DECIMAL = re.compile(r"[+-]?[0-9]+")
_HEX = re.compile(r"[+-]?0[xX][0-9A-Fa-f]+")
_LONGEST = 64


def format_line(code: SupportsIndex) -> str:
    """Return a one-line summary of a code: ``<code> (<severity>, <family>): <message>``.

    The severity is ``error``, ``warning`` or ``success``. An undocumented code still reports
    its severity and family; when no message and no family are known the line ends with
    ``no documented information``. ``code`` is checked as in :func:`explain`.

    >>> format_line(-1073807339)
    '-1073807339 (error, VISA): The operation did not finish before the timeout elapsed.'
    >>> format_line(-200300)
    '-200300 (error, NI-DAQmx): no documented message, classified by range only'
    >>> format_line(0)
    '0 (success, unknown family): no documented information'
    """
    info = describe(code)
    severity = "error" if info.is_error else "warning" if info.is_warning else "success"
    family = info.family if info.family is not None else "unknown family"
    head = f"{info.code} ({severity}, {family})"
    if info.message is not None:
        return f"{head}: {info.message}"
    if info.family is not None:
        return f"{head}: no documented message, classified by range only"
    return f"{head}: no documented information"


def parse_code(text: str) -> int:
    """Parse a user-supplied code in decimal or hexadecimal into the signed integer code.

    Decimal values are read as written, with an optional sign. Hexadecimal values take a
    ``0x`` or ``0X`` prefix, optionally signed; one in the unsigned 32-bit range above
    ``0x7FFFFFFF`` is read with the 32-bit two's-complement convention, so ``0xBFFF0015``
    becomes ``-1073807339``, matching how NI displays VISA codes. Surrounding whitespace is
    ignored, and the code itself may be up to 64 characters long (leading zeros included).
    Anything else, or a value outside the signed 32-bit range, raises ``ValueError``; a
    non-``str`` argument raises ``TypeError``.

    >>> parse_code("0xBFFF0015")
    -1073807339
    >>> parse_code(" -200088 ")
    -200088
    """
    token = as_text(text, "the code text").strip()
    if not token:
        raise ValueError("empty code")
    is_hex = len(token) <= _LONGEST and _HEX.fullmatch(token) is not None
    if not is_hex and (len(token) > _LONGEST or _DECIMAL.fullmatch(token) is None):
        raise ValueError(f"not a valid code: {shorten(text)}")
    value = int(token, 16 if is_hex else 10)
    if is_hex and INT32_MAX < value < _UINT32:
        value -= _UINT32
    if not INT32_MIN <= value <= INT32_MAX:
        raise ValueError(f"code out of the signed 32-bit range: {shorten(text)}")
    return value
