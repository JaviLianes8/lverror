"""A read-only mapping view over the documented codes.

``ErrorTable`` turns the baked-in data into a standard :class:`collections.abc.Mapping`
from a code to its :class:`ErrorInfo`, so the table drops into any code that expects a
mapping. Only documented codes (the ones that carry a message) are members; looking up an
undocumented code raises :class:`UnknownCodeError`. Use :func:`describe` instead when you
want the range classification of an undocumented code without an exception.
"""

from __future__ import annotations

import operator
from collections.abc import Iterator, Mapping

from ._core import ErrorInfo, describe
from ._data import MESSAGES


class UnknownCodeError(KeyError):
    """Raised when a key that is not a documented code is looked up in an ``ErrorTable``.

    It is a ``KeyError``, so ``TABLE.get(code)`` and ``code in TABLE`` work as with a dict.
    ``args[0]`` is the key that was looked up.

    >>> try:
    ...     TABLE[-200300]
    ... except UnknownCodeError as exc:
    ...     exc.args[0]
    -200300
    """


def _member(key: object) -> int | None:
    if isinstance(key, bool):
        return None
    try:
        code = operator.index(key)  # type: ignore[arg-type]
    except TypeError:
        return None
    return code if code in MESSAGES else None


class ErrorTable(Mapping[int, ErrorInfo]):
    """A read-only mapping from a documented code to its :class:`ErrorInfo`.

    Membership is exactly the set of codes that carry a message. ``table[code]`` returns the
    full record for a documented code and raises :class:`UnknownCodeError` for any other key,
    including ``bool`` and non-integer keys. Iteration yields the documented codes in
    ascending order. Use the shared :data:`TABLE` instance.

    >>> TABLE[14001].message
    'Invalid refnum.'
    >>> 7 in TABLE, -200300 in TABLE, TABLE.get(-200300)
    (True, False, None)
    """

    __slots__ = ("_codes",)

    def __init__(self) -> None:
        self._codes: tuple[int, ...] = tuple(sorted(MESSAGES))

    def __getitem__(self, code: int) -> ErrorInfo:
        member = _member(code)
        if member is None:
            raise UnknownCodeError(code)
        return describe(member)

    def __iter__(self) -> Iterator[int]:
        return iter(self._codes)

    def __len__(self) -> int:
        return len(self._codes)

    def __contains__(self, code: object) -> bool:
        return _member(code) is not None

    def __repr__(self) -> str:
        return f"ErrorTable({len(self._codes)} documented codes)"


# The shared, read-only table of every documented code.
TABLE: ErrorTable = ErrorTable()
