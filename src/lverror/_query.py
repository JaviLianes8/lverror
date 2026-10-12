"""Query helpers over the documented codes: search, families, nearest, and iteration.

These read the same baked-in data as :func:`explain` and :func:`describe`, so they work
offline and never invent a message. ``search`` and ``in_family`` return records sorted by
code; ``nearest`` finds the documented code closest in numeric value.
"""

from __future__ import annotations

import operator
from collections.abc import Iterator
from typing import SupportsIndex

from ._core import ErrorInfo, describe
from ._data import MESSAGES, RANGES
from ._validate import as_code, as_text, shorten

_SORTED: tuple[int, ...] = tuple(sorted(MESSAGES))


def families() -> tuple[str, ...]:
    """Return the known family names, in the order the range table lists them, without repeats.

    >>> families()[:3]
    ('VISA', 'NI-DAQmx', 'analysis VI')
    >>> families()[-1]
    'general LabVIEW'
    """
    seen: dict[str, None] = {}
    for _low, _high, name in RANGES:
        seen.setdefault(name, None)
    return tuple(seen)


def codes() -> tuple[int, ...]:
    """Return every documented code (a code that carries a message), in ascending order.

    >>> codes()[0] < 0 < codes()[-1]
    True
    >>> 7 in codes(), -200300 in codes()
    (True, False)
    """
    return _SORTED


def records() -> Iterator[ErrorInfo]:
    """Yield the full :class:`ErrorInfo` for every documented code, in ascending code order.

    >>> first = next(records())
    >>> first.code == codes()[0] and first.message is not None
    True
    """
    for code in _SORTED:
        yield describe(code)


def search(text: str, *, limit: SupportsIndex | None = None) -> list[ErrorInfo]:
    """Return documented records whose message contains ``text``, case-insensitively.

    Results are sorted by code. Pass ``limit`` (zero or more) to cap the number returned. An
    empty or whitespace-only query returns an empty list rather than every record. A
    non-``str`` query or a non-integer ``limit`` raises ``TypeError``; a negative ``limit``
    raises ``ValueError``.

    >>> [rec.code for rec in search("timeout expired")]
    [-1073807339]
    >>> len(search("visa", limit=2))
    2
    """
    needle = as_text(text, "the search text").strip().casefold()
    cap = _limit(limit)
    if not needle:
        return []
    found: list[ErrorInfo] = []
    for code in _SORTED:
        if cap is not None and len(found) >= cap:
            break
        if needle in MESSAGES[code].casefold():
            found.append(describe(code))
    return found


def _limit(limit: object) -> int | None:
    if limit is None:
        return None
    if isinstance(limit, bool):
        raise TypeError("limit must be an integer or None, not bool")
    try:
        cap = operator.index(limit)  # type: ignore[arg-type]
    except TypeError:
        raise TypeError(f"limit must be an integer or None, not {type(limit).__name__}") from None
    if cap < 0:
        raise ValueError("limit must be zero or more")
    return cap


def in_family(name: str) -> list[ErrorInfo]:
    """Return every documented record whose family is ``name``, sorted by code.

    The name is matched case-insensitively against the known family names. A name that is
    not a known family raises ``ValueError`` listing the valid names; a non-``str`` name
    raises ``TypeError``.

    >>> [rec.code for rec in in_family("dde")][:3]
    [14001, 14002, 14003]
    """
    known = {fam.casefold(): fam for fam in families()}
    key = as_text(name, "the family name").strip().casefold()
    if key not in known:
        valid = ", ".join(families())
        raise ValueError(f"unknown family {shorten(name)}; known families are: {valid}")
    canonical = known[key]
    return [rec for rec in records() if rec.family == canonical]


def nearest(code: SupportsIndex) -> ErrorInfo:
    """Return the documented record whose code is numerically nearest ``code``.

    An exact match returns that record. On a tie the lower code wins. The table always holds
    at least one code, so a record is always returned. ``code`` is checked as in
    :func:`explain`.

    >>> nearest(7).code
    7
    >>> nearest(-200300).family
    'NI-DAQmx'
    """
    target = as_code(code)
    best = min(_SORTED, key=lambda known: (abs(known - target), known))
    return describe(best)
