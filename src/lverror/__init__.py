"""Offline LabVIEW and NI error code lookup.

Turn a numeric LabVIEW or NI error code into NI's own description without LabVIEW or any NI
driver installed. The text ships inside the package, copied word for word from the error
files LabVIEW 2026 and NI-VISA install, the LabVIEW Wiki NI-DAQmx page and NI's 1997
instrument driver table. Every other code is still classified by the range, or family, it
falls in. No description is written by hand.

Besides the single-code helpers (:func:`explain`, :func:`describe`), the package offers
reverse search (:func:`search`), family queries (:func:`in_family`, :func:`families`),
nearest-known lookup (:func:`nearest`), whole-table iteration (:func:`records`,
:func:`codes`), a dict-like :data:`TABLE`, one-line formatting (:func:`format_line`), and a
``lverror`` command-line tool.

>>> import lverror
>>> lverror.explain(lverror.parse_code("0xBFFF0015"))
'Timeout expired before operation completed.'
"""

from __future__ import annotations

from ._core import ErrorInfo, describe, explain, family, is_error, is_known, is_warning
from ._format import format_line, parse_code
from ._query import codes, families, in_family, nearest, records, search
from ._table import TABLE, ErrorTable, UnknownCodeError

__version__ = "1.0.0"

__all__ = [
    "TABLE",
    "ErrorInfo",
    "ErrorTable",
    "UnknownCodeError",
    "codes",
    "describe",
    "explain",
    "families",
    "family",
    "format_line",
    "in_family",
    "is_error",
    "is_known",
    "is_warning",
    "nearest",
    "parse_code",
    "records",
    "search",
]
