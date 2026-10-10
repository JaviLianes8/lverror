# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
