# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-10-12

The public API is now stable: the names in `lverror.__all__`, their signatures, the five
`ErrorInfo` fields, the family names and their order, the error types listed below, and the
command-line options and exit codes. Message text follows NI's sources and may change when
NI changes it.

### Changed

- Every message is now NI's own text, word for word. 0.3.0 shipped 888 messages of which
  only 224 matched NI exactly; the rest were shortened or reworded, some from older NI
  wording (VISA -1073807239, for example, now reads as the installed NI-VISA file has it).
  The text now comes from the error files LabVIEW 2026, NI-VISA and NI-PAL install, the LabVIEW Wiki NI-DAQmx page and NI's 1997 instrument
  driver table, captured with their origin and checksum in `tests/fixtures/sources`. The set
  of 888 codes is unchanged.
- Codes NI lists twice keep both meanings, joined by `Also:` (2 and 61 to 65).
- `is_error` reports every positive code NI's LabVIEW 2026 error file lists as an error
  (unless NI's text calls it a warning) even when its text is not shipped; 0.3.0 reported 369
  of them, such as 1612, as warnings. The list ships as code numbers only.
- The VISA family now covers every VISA code (`0xBFFF0000` to `0xBFFFFFFF` and the
  completion codes `0x3FFF0000` to `0x3FFFFFFF`); 34 documented VISA codes, including all the
  completion codes, used to report no family.
- The NI-DAQmx family now spans -239999 to -200000 and 200000 to 239999 (was -209999 to
  -200000 and 200000 to 209999), and the general LabVIEW family 1 to 16999 (was 16000),
  matching the codes NI documents.
- Functions that take a code refuse `bool`, floats and strings with `TypeError` and values
  outside the signed 32-bit range with `ValueError`. In 0.3.0 `True` and `7.0` were looked up
  as codes 1 and 7, strings and `None` failed with an unrelated comparison `TypeError` in most
  functions, and out-of-range integers were classified (`is_warning(2**31)` was `True`).
  Integer-like values (an `IntEnum`, a NumPy integer) are accepted, the code parameters are
  annotated `SupportsIndex`, and `ErrorInfo.code` is always a plain `int` (0.3.0 stored the
  argument as given).
- `parse_code` accepts only ASCII decimal or `0x` hexadecimal text with an optional sign,
  and refuses values outside the signed 32-bit range; underscores, other Unicode digits and
  out-of-range values used to slip through. Error messages never repeat long input.
- `search` refuses a non-`str` query and a negative or non-integer `limit` (`limit=True` used
  to mean 1), and matches with `str.casefold`. `in_family` refuses a non-`str` name.
- `TABLE` treats `bool` and non-integer keys as missing (`True in TABLE` was `True`), accepts
  integer-like keys, and `UnknownCodeError` shows a short form of a long or huge key.
- The command line refuses two actions in one call (a code with `--search`, for example)
  with exit code 2 instead of silently running one of them, and out-of-range or malformed
  codes such as `1_000` exit 2 (they used to exit 0 or 1).

### Added

- Doctested examples on every public name, a guide (`GUIDE.md`), and contract, ground
  truth, fuzz and end-to-end tests that drive the installed command.

## [0.3.0]

### Added

- `search(text)`: reverse lookup that returns the documented records whose message contains a
  case-insensitive substring, sorted by code, with an optional `limit`.
- `in_family(name)` and `families()`: enumerate the documented codes in a named family and
  list the known family names.
- `nearest(code)`: return the documented record numerically closest to a code.
- `codes()` and `records()`: iterate every documented code, or its full `ErrorInfo`, in order.
- `parse_code(text)`: parse a code in decimal or hex, applying the 32-bit two's-complement
  convention so `0xBFFF0015` resolves to `-1073807339` as NI's Explain Error dialog shows it.
- `format_line(code)`: render one record as a single human-readable line.
- `TABLE`, an `ErrorTable` read-only `Mapping` from code to `ErrorInfo`, and `UnknownCodeError`
  raised when an undocumented code is looked up on it.
- A `lverror` command-line tool (console script and `python -m lverror`): single-code lookup
  with hex input, `--search`, `--family`, `--list-families`, `--json`, and `--version`, with a
  `--help` that carries runnable examples.

### Changed

- The contract test now asserts the behaviour of every public name, not only that it is
  exported. Real end-to-end tests invoke the installed command through a subprocess and check
  stdout and exit codes against golden fixtures of actual NI/LabVIEW codes.

## [0.2.0]

### Added

- `is_known(code)`: report whether the package ships a documented message for a code.
- `family(code)`: return the documented range, or family, a code falls in, or `None`.
- VISA completion and warning codes (the positive `0x3FFF` family), classified as warnings
  rather than errors through a dedicated warning set so `is_warning` is accurate for them.
- Error families that were not covered before: instrument driver, AppleEvent, PPC, DDE, and
  the modern networking codes.

### Changed

- The baked-in dataset grows from 53 codes to 888 codes with verbatim or closely paraphrased
  messages, covering the general LabVIEW codes (file I/O, memory, VI Server, .NET, Python,
  classes, 3D, targets), the full NI-VISA completion and error set, common NI-DAQmx codes, and
  the families listed above. No message is invented; codes absent from public sources are still
  classified by range only.
- Data is split across several range-scoped modules so each file stays small, and a merge guard
  rejects any code defined in two modules.

## [0.1.0]

### Added

- `explain(code)`: return the documented description for a LabVIEW or NI error code, or
  `None` when the code is not known.
- `describe(code)`: return an `ErrorInfo` with the code, its message (if known), the family
  it falls in, and the `is_error` / `is_warning` flags.
- `is_error(code)` and `is_warning(code)` helpers.
- Baked-in offline data: 53 common codes with verbatim messages (general LabVIEW, network
  and VISA), plus range-based family classification for every other code. No message is
  invented; a code absent from the public sources is classified by range only.
