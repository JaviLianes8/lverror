# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
