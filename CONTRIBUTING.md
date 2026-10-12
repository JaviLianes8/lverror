# Contributing

Thanks for taking the time. This project keeps a small, predictable shape.

## Setup

```
pip install -r requirements-dev.txt
```

## Before you open a pull request

- Keep public API in `src/lverror/__init__.py`; internals live in `_`-prefixed modules.
- Add a test for the behaviour you change. Tests inject time, disk and network; they
  never touch the real thing.
- Run `scripts/check.ps1` (format, lint, types, tests) and make sure it passes.
- One logical change per commit, imperative subject line.

Open an issue first if the change is large or shifts the public API.

## The NI source copies

The ground-truth tests compare every description with National Instruments' own error text,
but that text is not kept in this repository. `tests/fixtures/sources/MANIFEST.json` records
where each source came from, with its size and SHA-256, and
`tests/fixtures/sources/labview-positive-codes.txt` lists only code numbers. Without the rest
of the folder, the tests that need it are skipped and everything else runs.

To re-create the folder (maintainers), on a Windows machine with LabVIEW 2026 and NI-VISA
installed, network access and `pdftotext` (Poppler) on `PATH`:

```
python scripts/capture_sources.py
```

It copies the entries of the shipped codes from the installed error files (paths in
`MANIFEST.json`), fetches the LabVIEW Wiki pages and NI's 1997 error-codes manual from the
recorded URLs, and rewrites `MANIFEST.json`. Compare the new checksums with the recorded ones:
an installed file that differs means a newer LabVIEW, and a web page may change between
fetches. The folder is ignored by git; never commit its contents. After changing a description,
`python scripts/refresh_data.py` re-checks every message against the copies and refreshes the
list of positive error codes.
