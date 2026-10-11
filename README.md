# lverror

Offline lookup that turns a LabVIEW or NI error code into a human description, with no
LabVIEW and no NI driver installed.

## Install

```
pip install lverror
```

## Usage

```python
import lverror

lverror.explain(7)
# 'File not found. The file might be in a different location or deleted. ...'

lverror.explain(1672)
# 'There was an unknown Python error in the operation.'

lverror.explain(999999)  # not a documented code
# None

info = lverror.describe(-200300)
info.code  # -200300
info.message  # None (no public message for this specific code)
info.family  # 'NI-DAQmx' (classified by its range)
info.is_error  # True

lverror.is_error(-1073807339)  # True (a VISA timeout)
lverror.is_warning(1073676294)  # True (a VISA completion code, not an error)
lverror.is_warning(200010)  # True (positive, undocumented: a warning by convention)
lverror.is_error(0)  # False (zero means success)

lverror.is_known(7)  # True
lverror.family(-1073807339)  # 'VISA'
```

### Search, families, and iteration

```python
import lverror

# Reverse search: which code was the timeout one again?
[rec.code for rec in lverror.search("timeout")]
# [-1073807339, -200284, 65, 123]

# Every documented code in one family.
[rec.code for rec in lverror.in_family("DDE")][:3]
# [14001, 14002, 14003]

lverror.families()
# ('VISA', 'NI-DAQmx', 'analysis VI', ... , 'general LabVIEW')

# The nearest documented code to an undocumented one.
lverror.nearest(-200300).code  # a real NI-DAQmx code near -200300

# Parse the hex spelling NI's Explain Error dialog shows.
lverror.parse_code("0xBFFF0015")  # -1073807339

# One human line, for a log.
lverror.format_line(7)
# '7 (error, general LabVIEW): File not found. ...'

# A dict-like view of every documented code.
lverror.TABLE[7].message  # 'File not found. ...'
len(lverror.TABLE)  # count of documented codes
7 in lverror.TABLE  # True
```

`search(text)` returns the records whose message contains `text`, case-insensitively.
`in_family(name)` and `families()` query the range table. `nearest(code)` returns the
closest documented record. `codes()` and `records()` iterate the whole table. `parse_code`
reads decimal or hex. `format_line` renders one line. `TABLE` is a read-only mapping from
code to `ErrorInfo`; looking up an undocumented code on it raises `UnknownCodeError`, while
`explain` and `describe` stay non-raising.

## Command line

The package installs a `lverror` command for the same lookups from a shell, offline.

```
$ lverror 7
7 (error, general LabVIEW): File not found. ...

$ lverror 0xBFFF0015
-1073807339 (error, VISA): Timeout expired before operation completed.

$ lverror --search timeout
-1073807339 (error, VISA): Timeout expired before operation completed.
...

$ lverror --family DDE
14001 (error, DDE): Invalid refnum.
...

$ lverror --list-families
VISA
NI-DAQmx
...

$ lverror 7 --json
{
  "code": 7,
  "message": "File not found. ...",
  "family": "general LabVIEW",
  "is_error": true,
  "is_warning": false
}
```

It exits `0` when a lookup or search yields information, `1` when a code or search has no
result, and `2` on bad input. Run `lverror --help` for the full list with examples. The tool
also runs as `python -m lverror`.

## Coverage

The data is baked into the package, so lookups work offline and need no NI software.

- 888 well-documented codes carry a message: the general LabVIEW codes (file I/O, memory,
  references, VI Server, .NET, Python integration, classes, 3D scenes, and LabVIEW targets),
  the full NI-VISA completion and error set, common NI-DAQmx codes, and the instrument driver,
  AppleEvent, PPC, DDE, network, and modern networking codes.
- Every other code is classified by the numeric range, or family, it falls in: general
  LabVIEW, NI-DAQmx, VISA, network, analysis VI, data acquisition VI, instrument driver,
  AppleEvent, PPC, DDE, and the user-defined ranges. For those codes `explain` returns
  `None` while `describe` still reports the family.

No description is invented. A code whose message is not in a public source has no message;
it is only classified by range. This is a deliberate limit: the complete code set lives in
NI's installed XML and runs to tens of thousands of entries, most of them driver-specific.

The same integer can mean different things in different LabVIEW subsystems (for example a
small positive code may be a general LabVIEW error, a GPIB code, or a serial-port code). The
lookup uses the general LabVIEW meaning as the default for small positive codes, because that
is the interpretation most callers hit, and notes the alternative meaning where one exists.

### A note on errors versus warnings

LabVIEW's authoritative error/warning indicator is the `status` boolean in the error
cluster, which a bare numeric code does not carry. Offline, `is_error` / `is_warning` apply
the standard numeric convention (negative is an error, zero is success, positive is a
warning), with the documented positive error codes of the legacy general, network, and DDE
families reported as errors.

## Why

When a LabVIEW or NI function fails from a Python side (a TCP or TDMS reader, a test rig
log parser, a tool that shells out to LabVIEW), you get a bare integer such as `-1073807339`
or `7`. Mapping it to a description normally means opening LabVIEW's Explain Error dialog or
digging through NI's installed `errors` XML files, neither of which exists on a plain Python
machine or a CI runner.

No maintained PyPI package does this lookup. The NI driver bindings (`nidaqmx`, the NI-RFmx
family) can describe a code, but only by calling back into the installed NI driver runtime,
so they are useless without that runtime. The NI error text itself lives in NI's installed
`errors` XML files, so reading it the usual way means NI software is present. The community
tools that do handle error text, such as OpenG's error utilities, are LabVIEW-side: they run
inside LabVIEW, on a block diagram, not in a plain Python process. Generic packages such as
`error-manager` manage codes you define yourself and ship none of NI's. The VI and source
parsers (`pylabview`, `pylavi`, `lvkit`) read `.vi` files, not error codes. So the codes
themselves have no standalone, offline, dependency-free home on PyPI.

`lverror` is that home: it runs anywhere Python runs, with nothing installed, which makes it
suited to CI runners, log and data pipelines, and test-rig tooling that never has LabVIEW.

The messages are compiled from National Instruments public documentation (the NI "LabVIEW
Error Codes" and "General LabVIEW Error Codes" references, the NI-VISA reference, and the
NI-DAQmx knowledge base) and the community
[LabVIEW Wiki error-code pages](https://labviewwiki.org/wiki/LabVIEW_Error_Code_Family), and
the ranges from NI's
["Ranges of LabVIEW Error Codes"](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/ranges-of-labview-error-codes.html).
It is pure standard library, fully typed, and ships `py.typed`.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
