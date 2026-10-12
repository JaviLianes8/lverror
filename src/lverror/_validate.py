"""Argument checks shared by every public function, so they all reject bad input the same way."""

from __future__ import annotations

import operator

INT32_MIN = -(1 << 31)
INT32_MAX = (1 << 31) - 1
_SHOWN = 40


def shorten(value: object) -> str:
    """Return a short ``repr`` of user input for an error message, never the whole of it."""
    if isinstance(value, int) and value.bit_length() > 64:
        # A huge integer cannot even be printed cheaply (Python caps int-to-str conversion).
        return f"<int of {value.bit_length()} bits>"
    try:
        text = repr(value)
    except Exception:
        return f"<{type(value).__name__} object>"
    if len(text) <= _SHOWN:
        return text
    return text[: _SHOWN - 3] + "..."


def as_code(value: object) -> int:
    """Return ``value`` as an ``int`` LabVIEW error code, or raise ``TypeError``/``ValueError``.

    A code is any integer, including integer-like objects such as NumPy integers, except
    ``bool``. LabVIEW error codes are signed 32-bit integers, so a value outside that range
    raises ``ValueError``.
    """
    if isinstance(value, bool):
        raise TypeError("an error code must be an integer, not bool")
    try:
        code = operator.index(value)  # type: ignore[arg-type]
    except TypeError:
        name = type(value).__name__
        raise TypeError(f"an error code must be an integer, not {name}") from None
    if not INT32_MIN <= code <= INT32_MAX:
        # The value itself is not echoed: a huge integer cannot even be printed cheaply.
        raise ValueError(f"error code out of the signed 32-bit range ({code.bit_length()} bits)")
    return code


def as_text(value: object, what: str) -> str:
    """Return ``value`` if it is a ``str``, otherwise raise ``TypeError`` naming ``what``."""
    if not isinstance(value, str):
        raise TypeError(f"{what} must be a str, not {type(value).__name__}")
    # A plain copy, so a str subclass cannot override strip or casefold on the way in.
    return str.__str__(value)
