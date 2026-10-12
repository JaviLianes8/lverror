# lverror

Offline lookup that turns a LabVIEW or NI error code into NI's own description, with no
LabVIEW and no NI driver installed.

## The problem

When a LabVIEW program, an NI driver or a test rig fails, what reaches the Python side (a TCP
reader, a log parser, a tool that shells out to LabVIEW) is a bare integer such as
`-1073807339` or `7`. Turning it into words normally means opening LabVIEW's Explain Error
dialog or reading the `errors` files that NI software installs, and neither exists on a plain
Python machine or a CI runner.

`lverror` carries NI's text for 888 common codes inside the package, word for word, and
classifies every other code by the numeric range it falls in.

## Install

```
pip install lverror
```

Pure standard library, no runtime dependencies, Python 3.10 or newer, fully typed.

## Quick start

```python
import lverror

assert lverror.explain(-1073807339) == "Timeout expired before operation completed."
assert lverror.explain(-200300) is None  # not in the shipped sources

info = lverror.describe(-200300)
assert (info.family, info.is_error) == ("NI-DAQmx", True)  # still classified by range

assert lverror.parse_code("0xBFFF0015") == -1073807339  # the hex form NI dialogs show
assert lverror.format_line(56) == (
    "56 (error, network): The network operation exceeded the user-specified or system time limit."
)
assert [rec.code for rec in lverror.search("timeout expired")] == [-1073807339]
assert lverror.is_warning(1073676294)  # a VISA completion code, not an error
assert lverror.TABLE[14001].message == "Invalid refnum."
```

The same lookups work from a shell:

```
$ lverror 0xBFFF0015
-1073807339 (error, VISA): Timeout expired before operation completed.
$ lverror --search "synchronous poke"
14014 (error, DDE): A request for a synchronous poke transaction has timed out.
$ lverror -200300
-200300 (error, NI-DAQmx): no documented message, classified by range only
```

Every function, the range table, the error rules and the command-line tool are covered in
the [guide](https://github.com/JaviLianes8/lverror/blob/main/GUIDE.md). Changes are listed in
the [changelog](https://github.com/JaviLianes8/lverror/blob/main/CHANGELOG.md).

## Where the text comes from

Every message is NI's text, copied verbatim (the NI-DAQmx text through the LabVIEW Wiki,
which reproduces it) and checked by the test suite against captured
sources whose origin, size and SHA-256 are recorded in `tests/fixtures/sources/MANIFEST.json`:

- 729 codes from the error file LabVIEW 2026 installs (`LabVIEW-errors.txt`), 99 VISA codes
  from the NI-VISA error file and 2 from the NI-PAL error file, read on a machine with
  LabVIEW 2026 installed.
- 41 NI-DAQmx codes from the
  [LabVIEW Wiki NI-DAQmx error page](https://labviewwiki.org/wiki/NI-DAQmx_Error_Code_Family),
  which reproduces NI's DAQmx error text.
- 17 instrument driver codes that LabVIEW 2026 no longer lists, from Table 5 of NI's 1997
  "LabVIEW Error Codes" manual (part number 321551A-01).

Only the `LabVIEW: (Hex 0x7)` style prefix and NI's bold tags are removed, and line breaks
and runs of spaces become single spaces. Where NI lists one
code twice with two meanings (serial and network codes 61 to 65, for example), both are kept,
joined by `Also:`. A code outside these sources has no message: `explain` returns `None`,
while `describe` still reports its family. The full NI code set runs to tens of thousands of
mostly driver-specific entries; this package ships the general LabVIEW, VISA, common NI-DAQmx,
instrument driver, AppleEvent, PPC, DDE and networking codes a Python caller usually meets.

## Why lverror

- The NI driver bindings can describe a code only by calling the installed driver: the
  `nidaqmx` package ships the DAQmx code names (`nidaqmx.error_codes`), not their text.
- [PyVISA](https://pypi.org/project/PyVISA/) ships offline descriptions of the VISA status
  codes, and only those: no general LabVIEW, NI-DAQmx or networking codes.
- [lvkit](https://pypi.org/project/lvkit/), a toolkit for converting LabVIEW VIs to Python
  (alpha, with runtime dependencies such as pydantic, networkx and pylabview), includes a
  table of about 1300 LabVIEW error messages. It has no NI-DAQmx codes and no family or
  error/warning classification.
- [error-manager](https://pypi.org/project/error-manager/) manages codes you define yourself
  and ships none of NI's. The LabVIEW file parsers
  [pylabview](https://pypi.org/project/pylabview/) and
  [pylavi](https://pypi.org/project/pylavi/) read `.vi` files, not error codes.

`lverror` runs wherever Python runs, with nothing else installed, which suits CI runners, log
and data pipelines, and test-rig tooling that never has LabVIEW.

## Errors versus warnings

LabVIEW's authoritative error flag is the `status` boolean of the error cluster, which a bare
code does not carry. Offline, `is_error` and `is_warning` apply the usual convention: negative
codes are errors, `0` is success and positive codes are warnings, except the positive codes
NI's LabVIEW error file lists, unless NI's text calls them a warning (1026 of them, from the
general, network and DDE families among others), which are errors even when their text is
not shipped.

## License

MIT. See [LICENSE](https://github.com/JaviLianes8/lverror/blob/main/LICENSE). The messages
are NI's text, quoted to identify the codes they describe.

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
