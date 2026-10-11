"""Query helpers over the documented codes: search, families, nearest, and iteration.

These read the same baked-in data as :func:`explain` and :func:`describe`, so they work
offline and never invent a message. ``search`` and ``in_family`` return records sorted by
code; ``nearest`` finds the documented code closest in numeric value.
"""

from __future__ import annotations

from collections.abc import Iterator

from ._core import ErrorInfo, describe
from ._data import MESSAGES, RANGES


def families() -> tuple[str, ...]:
    """Return the known family names, in the order the range table lists them, without repeats."""
    seen: dict[str, None] = {}
    for _low, _high, name in RANGES:
        seen.setdefault(name, None)
    return tuple(seen)


def codes() -> tuple[int, ...]:
    """Return every documented code (a code that carries a message), in ascending order."""
    return tuple(sorted(MESSAGES))


def records() -> Iterator[ErrorInfo]:
    """Yield the full :class:`ErrorInfo` for every documented code, in ascending code order."""
    for code in sorted(MESSAGES):
        yield describe(code)


def search(text: str, *, limit: int | None = None) -> list[ErrorInfo]:
    """Return documented records whose message contains ``text``, case-insensitively.

    Results are sorted by code. Pass ``limit`` to cap the number returned. An empty or
    whitespace-only query returns an empty list rather than every record.
    """
    needle = text.strip().lower()
    if not needle:
        return []
    found = [describe(code) for code in sorted(MESSAGES) if needle in MESSAGES[code].lower()]
    if limit is not None:
        return found[:limit]
    return found


def in_family(name: str) -> list[ErrorInfo]:
    """Return every documented record whose family is ``name``, sorted by code.

    The name is matched case-insensitively against the known family names. A name that is
    not a known family raises :class:`ValueError` listing the valid names.
    """
    known = {fam.lower(): fam for fam in families()}
    key = name.strip().lower()
    if key not in known:
        valid = ", ".join(families())
        raise ValueError(f"unknown family {name!r}; known families are: {valid}")
    canonical = known[key]
    return [rec for rec in records() if rec.family == canonical]


def nearest(code: int) -> ErrorInfo:
    """Return the documented record whose code is numerically nearest ``code``.

    An exact match returns that record. On a tie the lower code wins. The table always holds
    at least one code, so a record is always returned.
    """
    best = min(MESSAGES, key=lambda known: (abs(known - code), known))
    return describe(best)
