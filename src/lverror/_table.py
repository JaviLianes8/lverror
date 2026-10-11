"""A read-only mapping view over the documented codes.

``ErrorTable`` turns the baked-in data into a standard :class:`collections.abc.Mapping`
from a code to its :class:`ErrorInfo`, so the table drops into any code that expects a
mapping. Only documented codes (the ones that carry a message) are members; looking up an
undocumented code raises :class:`UnknownCodeError`. Use :func:`describe` instead when you
want the range classification of an undocumented code without an exception.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping

from ._core import ErrorInfo, describe
from ._data import MESSAGES


class UnknownCodeError(KeyError):
    """Raised when a code that carries no documented message is looked up in an ``ErrorTable``."""


class ErrorTable(Mapping[int, ErrorInfo]):
    """A read-only mapping from a documented code to its :class:`ErrorInfo`.

    Membership is exactly the set of codes that carry a message. ``table[code]`` returns the
    full record for a documented code and raises :class:`UnknownCodeError` otherwise.
    Iteration yields the documented codes in ascending order.
    """

    __slots__ = ("_codes",)

    def __init__(self) -> None:
        self._codes: tuple[int, ...] = tuple(sorted(MESSAGES))

    def __getitem__(self, code: int) -> ErrorInfo:
        if code not in MESSAGES:
            raise UnknownCodeError(code)
        return describe(code)

    def __iter__(self) -> Iterator[int]:
        return iter(self._codes)

    def __len__(self) -> int:
        return len(self._codes)

    def __contains__(self, code: object) -> bool:
        return code in MESSAGES

    def __repr__(self) -> str:
        return f"ErrorTable({len(self._codes)} documented codes)"


# The shared, read-only table of every documented code.
TABLE: ErrorTable = ErrorTable()
