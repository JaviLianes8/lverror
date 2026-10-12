"""Offline LabVIEW and NI error code lookup.

Turn a numeric LabVIEW or NI error code into a plain-English description without LabVIEW or
any NI driver installed. The descriptions ship inside the package; they are written for this
library and match the meaning of NI's error descriptions (the error files LabVIEW 2026, NI-VISA
and NI-PAL install, the LabVIEW Wiki NI-DAQmx page and NI's 1997 instrument driver table).
Every other code is still classified by the range, or family, it falls in.

Besides the single-code helpers (:func:`explain`, :func:`describe`), the package offers
reverse search (:func:`search`), family queries (:func:`in_family`, :func:`families`),
nearest-known lookup (:func:`nearest`), whole-table iteration (:func:`records`,
:func:`codes`), a dict-like :data:`TABLE`, one-line formatting (:func:`format_line`), and a
``lverror`` command-line tool.

>>> import lverror
>>> lverror.explain(lverror.parse_code("0xBFFF0015"))
'The operation did not finish before the timeout elapsed.'
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
