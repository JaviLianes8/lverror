"""Human formatting and input parsing for codes.

``format_line`` renders one record as a single line for logs or a terminal. ``parse_code``
accepts the decimal and hexadecimal spellings a user is likely to paste, including the hex
form NI's Explain Error dialog shows for VISA codes.
"""

from __future__ import annotations

from ._core import describe

_UINT32 = 1 << 32
_INT32_MAX = (1 << 31) - 1


def _severity(code: int) -> str:
    info = describe(code)
    if info.is_error:
        return "error"
    if info.is_warning:
        return "warning"
    return "success"


def format_line(code: int) -> str:
    """Return a one-line summary of a code, such as ``7 (error, general LabVIEW): File not ...``.

    An undocumented code still reports its severity and family; when no message and no family
    are known the line ends with ``no documented information``.
    """
    info = describe(code)
    family = info.family if info.family is not None else "unknown family"
    head = f"{code} ({_severity(code)}, {family})"
    if info.message is not None:
        return f"{head}: {info.message}"
    if info.family is not None:
        return f"{head}: no documented message, classified by range only"
    return f"{head}: no documented information"


def parse_code(text: str) -> int:
    """Parse a user-supplied code in decimal or hexadecimal into the signed integer code.

    Decimal values are read as written. Hexadecimal values (a ``0x`` prefix, optionally
    signed) that fall in the unsigned 32-bit range above :data:`0x7FFFFFFF` are read with the
    32-bit two's-complement convention, so ``0xBFFF0015`` becomes ``-1073807339``, matching
    how NI displays VISA codes. A value that is neither raises :class:`ValueError`.
    """
    token = text.strip()
    if not token:
        raise ValueError("empty code")
    lowered = token.lower()
    is_hex = lowered.startswith("0x") or lowered.startswith("-0x") or lowered.startswith("+0x")
    try:
        value = int(token, 16) if is_hex else int(token, 10)
    except ValueError:
        raise ValueError(f"not a valid code: {text!r}") from None
    if is_hex and _INT32_MAX < value < _UINT32:
        return value - _UINT32
    return value
