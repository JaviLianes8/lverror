"""Offline LabVIEW and NI error code lookup.

Turn a numeric LabVIEW or NI error code into a human description without LabVIEW or any NI
driver installed. The data is baked into the package and compiled from public National
Instruments documentation and the LabVIEW Wiki. Well-documented common codes carry a
verbatim message; every other code is still classified by the range, or family, it falls
in. No description is invented.
"""

from __future__ import annotations

from ._core import ErrorInfo, describe, explain, family, is_error, is_known, is_warning

__version__ = "0.2.0"

__all__ = [
    "ErrorInfo",
    "describe",
    "explain",
    "family",
    "is_error",
    "is_known",
    "is_warning",
]
