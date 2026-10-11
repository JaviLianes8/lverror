# lverror round 2: ranked improvements

This round builds on v0.2.0, where the dataset was already deepened from 53 to 888
verified codes compiled from public National Instruments documentation and the LabVIEW
Wiki. Because the data is already broad and every message is sourced (no message is
invented), round 2 concentrates on making that depth usable: query the table, search it
by text, drive it from a shell, and treat it as a first-class Python mapping. Every item
below is additive. No existing public name changes.

## Why not just add more codes

The honest limit stated in the README still holds: the complete NI code set lives in NI's
installed XML and runs to tens of thousands of mostly driver-specific entries. Round 1
captured the codes a Python-side caller actually hits and sourced each one. Rather than pad
the table with text that cannot be verified from a public source, round 2 invests in the
API and the CLI so the existing, trustworthy data goes further. This keeps the "no message
is invented" guarantee intact.

## Ranked improvements

1. Reverse search by text. `search(text)` scans every documented message for a
   case-insensitive substring and returns the matching records, sorted by code. This is the
   most requested direction for a lookup tool: "which code was the timeout one again?"

2. A command-line tool. A `lverror` console script (entry point in `[project.scripts]`)
   with: a bare code lookup (`lverror 7`), hex input (`lverror 0xBFFF0015`), reverse search
   (`--search timeout`), family listing (`--family VISA`), `--list-families`, machine output
   (`--json`), `--version`, and a `--help` that carries runnable examples. Runs offline.

3. Hex code parsing. NI's Explain Error dialog shows VISA codes in hex (for example
   `0xBFFF0015`). `parse_code` accepts decimal and hex, applying the 32-bit two's-complement
   convention so `0xBFFF0015` resolves to `-1073807339`, the signed code the table stores.

4. Family and range queries. `in_family(name)` returns every documented record in a named
   family; `families()` lists the known family names. This turns the range table, which was
   internal, into something a caller can enumerate.

5. A dict-like mapping. `ErrorTable` is a read-only `collections.abc.Mapping` from code to
   `ErrorInfo`, exposed as the singleton `TABLE`. `TABLE[7]`, `7 in TABLE`, `len(TABLE)`,
   iteration and `.get` all work, so the data drops into code that expects a mapping.

6. Nearest-known lookup. `nearest(code)` returns the documented record closest in numeric
   value, so an undocumented code still points the user at the nearest entry they can read.

7. Whole-table iteration. `records()` yields every documented `ErrorInfo` in code order and
   `codes()` returns the sorted code tuple, for callers that want to export or scan the set.

8. Human one-line formatting. `format_line(code)` renders a single line such as
   `7 (error, general LabVIEW): File not found. ...`, suited to logs and the CLI.

9. A clear exception. `UnknownCodeError` (a `KeyError`) is raised by `TABLE[code]` for an
   undocumented code, so mapping access fails loudly while `explain`/`describe` stay
   non-raising for the common path.

10. A complete-promise contract test. The `-claims` contract test asserts the behaviour of
    every public name, not merely that it is exported, so the contract fails if any promise
    regresses.

11. Real end-to-end tests. The installed `lverror` console script is invoked through
    `subprocess.run` and its real stdout and exit codes are checked against golden fixtures
    of actual NI/LabVIEW codes (`7`, `-1073807339`, `14001`, `-200088`). No mocks, no
    importing the function under test: the shipped command is exercised as a user runs it.

12. `python -m lverror`. A `__main__` entry so the tool also runs as a module, which the
    e2e tests rely on when the console script is not on `PATH`.
