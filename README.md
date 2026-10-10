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

lverror.explain(999999)      # not a documented code
# None

info = lverror.describe(-200279)
info.code                    # -200279
info.message                 # None  (no public message for this specific code)
info.family                  # 'NI-DAQmx'  (classified by its range)
info.is_error                # True

lverror.is_error(-1073807339)   # True  (a VISA timeout)
lverror.is_warning(200010)      # True  (positive, undocumented: a warning by convention)
lverror.is_error(0)             # False (zero means success)
```

`explain(code)` returns the documented description or `None`. `describe(code)` returns an
`ErrorInfo` with the `code`, the `message` (if known), the `family` it falls in, and the
`is_error` / `is_warning` flags. `is_error(code)` and `is_warning(code)` are also available
on their own.

## Coverage

The data is baked into the package, so lookups work offline and need no NI software.

- 53 common, well-documented codes carry a verbatim message: the general LabVIEW codes
  (file I/O, memory, references, .NET and Python integration), the common network codes,
  and the common VISA codes.
- Every other code is classified by the numeric range, or family, it falls in: general
  LabVIEW, NI-DAQmx, VISA, network, analysis VI, data acquisition VI, instrument driver,
  AppleEvent, PPC, DDE, and the user-defined ranges. For those codes `explain` returns
  `None` while `describe` still reports the family.

No description is invented. A code whose message is not in a public source has no message;
it is only classified by range. This is a deliberate limit: the complete code set lives in
NI's installed XML and runs to tens of thousands of entries, most of them driver-specific.

### A note on errors versus warnings

LabVIEW's authoritative error/warning indicator is the `status` boolean in the error
cluster, which a bare numeric code does not carry. Offline, `is_error` / `is_warning` apply
the standard numeric convention (negative is an error, zero is success, positive is a
warning), with the documented positive error codes of the legacy general and network
families reported as errors.

## Why

When a LabVIEW or NI function fails from a Python side (a TCP or TDMS reader, a test rig
log parser, a tool that shells out to LabVIEW), you get a bare integer such as `-1073807339`
or `7`. Mapping it to a description normally means opening LabVIEW's Explain Error dialog or
digging through NI's installed `errors` XML files, neither of which exists on a plain Python
machine or a CI runner.

No maintained PyPI package does this lookup. The NI driver bindings (`nidaqmx`, the NI-RFmx
family) can describe a code, but only by calling back into the installed NI driver runtime,
so they are useless without that runtime. Generic packages such as `error-manager` manage
codes you define yourself and ship none of NI's. The VI and source parsers (`pylabview`,
`pylavi`, `lvkit`) read `.vi` files, not error codes. So the codes themselves have no
standalone, offline, dependency-free home on PyPI.

`lverror` fills that gap. The messages are quoted verbatim from National Instruments public
documentation (the NI "LabVIEW Error Codes" manual) and the community
[LabVIEW Wiki error-code family pages](https://labviewwiki.org/wiki/LabVIEW_Error_Code_Family),
and the ranges from NI's
["Ranges of LabVIEW Error Codes"](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/ranges-of-labview-error-codes.html).
It is pure standard library, fully typed, and ships `py.typed`.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
