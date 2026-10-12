# lverror guide

This guide covers every public name in `lverror` 1.0. All Python blocks and command
transcripts below are run by the test suite, so they stay correct.

## 1. Looking up one code

`explain(code)` returns NI's text for a code, or `None` when the shipped sources do not
document it. `describe(code)` returns an `ErrorInfo` with everything known.

```python
import lverror

assert lverror.explain(7).startswith("File not found.")
assert lverror.explain(-200300) is None

info = lverror.describe(-1073807339)
assert info == lverror.ErrorInfo(
    code=-1073807339,
    message="Timeout expired before operation completed.",
    family="VISA",
    is_error=True,
    is_warning=False,
)
```

`ErrorInfo` is a frozen dataclass: its five fields (`code`, `message`, `family`, `is_error`,
`is_warning`) are stable, it compares by value and it is hashable. `is_known(code)` tells
whether a message ships, and `family(code)` returns the range name alone.

```python
import lverror

assert lverror.is_known(7) and not lverror.is_known(-200300)
assert lverror.family(65) == "network"
assert lverror.family(-3) is None  # outside every known range
```

Some codes mean different things in different LabVIEW subsystems. Where NI's file lists one
code twice, both meanings are kept, joined by `Also:`:

```python
import lverror

assert lverror.explain(65) == (
    "Serial port timeout; bytes not received at serial port. "
    "Also: The network connection is already established."
)
```

## 2. What a code may be

Every function that takes a code accepts an `int`, or any integer-like object (an
`IntEnum` member, a NumPy integer: anything with `__index__`). It refuses `bool`, floats and
strings with `TypeError`, and a value outside the signed 32-bit range that every LabVIEW
error code fits in with `ValueError`. An exception raised by the argument's own `__index__`
propagates unchanged, as it does for `int()` and list indexing. Use `parse_code` for text.

```python
import enum

import lverror


class Code(enum.IntEnum):
    FILE_NOT_FOUND = 7


assert lverror.describe(Code.FILE_NOT_FOUND).code == 7
for bad in (True, 7.0, "7"):
    try:
        lverror.explain(bad)
    except TypeError:
        pass
    else:
        raise AssertionError(bad)
try:
    lverror.explain(2**31)
except ValueError as exc:
    assert "signed 32-bit range" in str(exc)
```

## 3. Errors, warnings and success

A bare code does not carry LabVIEW's `status` flag, so `is_error` and `is_warning` apply the
usual numeric convention: negative codes are errors, `0` is success, positive codes are
warnings, except the positive codes NI's LabVIEW 2026 error file lists, which are errors
unless NI's text calls them a warning (only 40624 does). That list ships as numbers only, so
1612 is an error although its text is not shipped. The VISA completion codes (`0x3FFF....`)
are warnings. Exactly one of the two is true for every code except `0`.

```python
import lverror

assert lverror.is_error(-1073807339) and not lverror.is_warning(-1073807339)
assert lverror.is_error(7)  # a documented positive LabVIEW error
assert lverror.is_error(1612) and lverror.explain(1612) is None  # listed by NI, text not shipped
assert lverror.is_warning(1073676294)  # a VISA completion code
assert lverror.is_warning(200010)  # positive and undocumented: a warning by convention
assert not lverror.is_error(0) and not lverror.is_warning(0)
```

## 4. Families and the range table

`families()` lists the family names in table order; `in_family(name)` returns the documented
records of one family, matching the name case-insensitively, and raises `ValueError` for an
unknown name. A code shared by two families reports the more specific one: the network
range wins over general LabVIEW for 53 to 66. Three families (analysis VI, data acquisition
VI and user-defined) classify codes but ship no messages, so `in_family` returns `[]` for them.
Codes outside every range, such as the COM codes (`-2147467259`) or NI-PAL's `-50251`, have
no family even when their message ships.

```python
import lverror

assert lverror.families() == (
    "VISA",
    "NI-DAQmx",
    "analysis VI",
    "data acquisition VI",
    "user-defined",
    "AppleEvent",
    "instrument driver",
    "PPC",
    "network",
    "DDE",
    "general LabVIEW",
)
assert [rec.code for rec in lverror.in_family("dde")][:2] == [14001, 14002]
try:
    lverror.in_family("GPIB")
except ValueError as exc:
    assert "known families are" in str(exc)
```

| Family | Range | Source |
| --- | --- | --- |
| VISA | `0xBFFF0000` to `0xBFFFFFFF` and `0x3FFF0000` to `0x3FFFFFFF` | derived from the NI-VISA error file |
| NI-DAQmx | -239999 to -200000 and 200000 to 239999 | derived from the NI-DAQmx family table |
| analysis VI | -20065 to -20001 | NI 1997 manual |
| data acquisition VI | -10943 to -10001 | NI 1997 manual |
| user-defined | -8999 to -8000, 5000 to 9999, 500000 to 599999 | NI "Ranges of LabVIEW Error Codes" |
| AppleEvent | -1719 to -1700 | NI 1997 manual |
| instrument driver | -1399 to -1200 | NI 1997 manual ("-1200 to -13xx") |
| PPC | -932 to -900 | NI 1997 manual |
| network | 53 to 66 | NI 1997 manual |
| DDE | 14001 to 14020 | NI 1997 manual |
| general LabVIEW | 1 to 16999 | derived from the LabVIEW family table |

The family names and their order are part of the stable API; ranges may widen in a minor
release when NI documents more codes.

## 5. Searching and walking the table

`search(text, *, limit=None)` returns the records whose message contains `text`,
case-insensitively, sorted by code; an empty query returns `[]`. `codes()` is the sorted
tuple of documented codes and `records()` yields their `ErrorInfo` in the same order.
`nearest(code)` returns the documented record closest to a code (the lower code on a tie).

```python
import lverror

assert [rec.code for rec in lverror.search("TIMEOUT EXPIRED")] == [-1073807339]
assert len(lverror.search("timed out", limit=3)) == 3
assert lverror.search("   ") == []
assert len(lverror.codes()) == 888
assert next(lverror.records()).code == lverror.codes()[0]
assert lverror.nearest(-200300).code == -200284
```

## 6. A mapping view

`TABLE` is the shared `ErrorTable`, a read-only `collections.abc.Mapping` from a documented
code to its `ErrorInfo`. Any other key, including `bool` and strings, is missing: indexing
raises `UnknownCodeError`, a `KeyError`, so `get` and `in` behave as with a dict.

```python
from collections.abc import Mapping

import lverror

assert isinstance(lverror.TABLE, Mapping) and isinstance(lverror.TABLE, lverror.ErrorTable)
assert lverror.TABLE[14001].message == "Invalid refnum."
assert -200300 not in lverror.TABLE and lverror.TABLE.get(-200300) is None
try:
    lverror.TABLE[-200300]
except lverror.UnknownCodeError as exc:
    assert isinstance(exc, KeyError) and exc.args == (-200300,)
assert len(lverror.TABLE) == len(lverror.codes())
```

## 7. Text in and text out

`parse_code(text)` reads a decimal or `0x` hexadecimal code, with an optional sign and
surrounding whitespace. Hex values from `0x80000000` to `0xFFFFFFFF` are read as 32-bit two's
complement, as NI dialogs print VISA codes. Anything else raises `ValueError` with a short
message that never repeats long input. `format_line(code)` renders one line.

```python
import lverror

assert lverror.parse_code("0xBFFF0015") == -1073807339
assert lverror.parse_code(" +7 ") == 7
for bad in ("7.0", "1_000", "0x100000000", ""):
    try:
        lverror.parse_code(bad)
    except ValueError:
        pass
    else:
        raise AssertionError(bad)
assert lverror.format_line(0) == "0 (success, unknown family): no documented information"
```

## 8. The command line

The `lverror` command (also `python -m lverror`) runs one action per call: a code, `--search
TEXT`, `--family NAME` or `--list-families`; add `--json` for machine output. It exits `0`
when it finds information, `1` when a code, a search or a known family finds none, and `2`
on bad input, including an unknown family name and two actions at once.

```
$ lverror 14001
14001 (error, DDE): Invalid refnum.
$ lverror 0x3FFF0006 --json
{
  "code": 1073676294,
  "message": "The number of bytes transferred is equal to the requested input count. More data might be available.",
  "family": "VISA",
  "is_error": false,
  "is_warning": true
}
$ lverror --list-families
VISA
NI-DAQmx
analysis VI
data acquisition VI
user-defined
AppleEvent
instrument driver
PPC
network
DDE
general LabVIEW
```

Older Python versions (3.13 and earlier) take a negative hex code for an option; put it
after `--`: `lverror -- -0x10`.
