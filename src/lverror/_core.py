"""The lookup itself: codes to messages, families, and error/warning classification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import SupportsIndex

from ._data import MESSAGES, POSITIVE_ERROR_CODES, RANGES
from ._validate import as_code


@dataclass(frozen=True)
class ErrorInfo:
    """What is known about one LabVIEW or NI error code.

    ``message`` is NI's text for the code, or ``None`` when no captured NI source documents
    it. ``family`` names the range the code falls in, or is ``None`` when the code sits
    outside every known range. ``is_error`` and ``is_warning`` follow :func:`is_error`.
    Instances are immutable, compare by value and are hashable.

    >>> info = describe(-1073807339)
    >>> info.message
    'Timeout expired before operation completed.'
    >>> (info.code, info.family, info.is_error, info.is_warning)
    (-1073807339, 'VISA', True, False)
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


def explain(code: SupportsIndex) -> str | None:
    """Return NI's description of a code, or ``None`` if no captured source documents it.

    Raises ``TypeError`` if ``code`` is not an integer (``bool`` included) and ``ValueError``
    if it is outside the signed 32-bit range every LabVIEW error code fits in.

    >>> explain(-200088)
    'Task specified is invalid or does not exist.'
    >>> explain(-200300) is None
    True
    """
    return MESSAGES.get(as_code(code))


def is_known(code: SupportsIndex) -> bool:
    """Report whether the package ships NI's message for the code.

    >>> is_known(7), is_known(-200300)
    (True, False)
    """
    return as_code(code) in MESSAGES


def family(code: SupportsIndex) -> str | None:
    """Return the range, or family, the code falls in, or ``None`` if it is outside all.

    >>> family(-200300), family(65), family(1073676294), family(-3)
    ('NI-DAQmx', 'network', 'VISA', None)
    """
    return _family_of(as_code(code))


def is_error(code: SupportsIndex) -> bool:
    """Report whether a code denotes an error.

    LabVIEW's authoritative error/warning flag lives in the error cluster's ``status``
    boolean, which a bare code does not carry. Offline, this applies the standard numeric
    convention: negative codes are errors, ``0`` means success, and positive codes are
    warnings, except for the documented positive error codes of the legacy general, network,
    and DDE families, which are reported as errors.

    >>> is_error(-1073807339), is_error(7), is_error(1073676294), is_error(0)
    (True, True, False, False)
    """
    checked = as_code(code)
    if checked < 0:
        return True
    return checked in POSITIVE_ERROR_CODES


def is_warning(code: SupportsIndex) -> bool:
    """Report whether a code denotes a warning (see :func:`is_error` for the convention).

    >>> is_warning(1073676294), is_warning(200010), is_warning(7), is_warning(0)
    (True, True, False, False)
    """
    checked = as_code(code)
    return checked > 0 and checked not in POSITIVE_ERROR_CODES


def describe(code: SupportsIndex) -> ErrorInfo:
    """Return everything known about a code: its message, family, and classification.

    >>> info = describe(-200300)
    >>> info.message is None, info.family, info.is_error
    (True, 'NI-DAQmx', True)
    """
    checked = as_code(code)
    return ErrorInfo(
        code=checked,
        message=MESSAGES.get(checked),
        family=_family_of(checked),
        is_error=is_error(checked),
        is_warning=is_warning(checked),
    )
