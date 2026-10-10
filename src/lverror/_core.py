"""The lookup itself: codes to messages, families, and error/warning classification."""

from __future__ import annotations

from dataclasses import dataclass

from ._data import MESSAGES, POSITIVE_ERROR_CODES, RANGES


@dataclass(frozen=True)
class ErrorInfo:
    """What is known about one LabVIEW or NI error code.

    ``message`` is ``None`` when no public source documents the code. ``family`` names the
    documented range the code falls in, or is ``None`` when the code sits outside every
    known range.
    """

    code: int
    message: str | None
    family: str | None
    is_error: bool
    is_warning: bool


def _family_of(code: int) -> str | None:
    for low, high, name in RANGES:
        if low <= code <= high:
            return name
    return None


def explain(code: int) -> str | None:
    """Return the documented description for a code, or ``None`` if the code is not known."""
    return MESSAGES.get(code)


def is_error(code: int) -> bool:
    """Report whether a code denotes an error.

    LabVIEW's authoritative error/warning flag lives in the error cluster's ``status``
    boolean, which a bare code does not carry. Offline, this applies the standard numeric
    convention: negative codes are errors, ``0`` means success, and positive codes are
    warnings, except for the documented positive error codes of the legacy general and
    network families, which are reported as errors.
    """
    if code < 0:
        return True
    return code in POSITIVE_ERROR_CODES


def is_warning(code: int) -> bool:
    """Report whether a code denotes a warning (see :func:`is_error` for the convention)."""
    return code > 0 and code not in POSITIVE_ERROR_CODES


def describe(code: int) -> ErrorInfo:
    """Return everything known about a code: its message, family, and classification."""
    return ErrorInfo(
        code=code,
        message=MESSAGES.get(code),
        family=_family_of(code),
        is_error=is_error(code),
        is_warning=is_warning(code),
    )
