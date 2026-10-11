"""The ``lverror`` command-line tool: look up a code, search, or list a family, offline.

Exit codes: ``0`` when the lookup or search yields information, ``1`` when a code or a search
has no result, and ``2`` on bad input. Pass ``--json`` for machine-readable output.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from . import __version__
from ._core import ErrorInfo, describe
from ._format import format_line, parse_code
from ._query import families, in_family, search

_EXAMPLES = """\
Examples:
  lverror 7                 look up a single code
  lverror 0xBFFF0015        hex is accepted (a VISA timeout, -1073807339)
  lverror --search timeout  find codes whose message mentions a word
  lverror --family VISA     list every documented code in a family
  lverror --list-families   show the known family names
  lverror 7 --json          machine-readable output
"""


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lverror",
        description="Offline lookup of a LabVIEW or NI error code, with no NI software installed.",
        epilog=_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("code", nargs="?", help="a code in decimal (7) or hex (0xBFFF0015)")
    parser.add_argument("--search", metavar="TEXT", help="list codes whose message contains TEXT")
    parser.add_argument("--family", metavar="NAME", help="list documented codes in a family")
    parser.add_argument(
        "--list-families", action="store_true", help="list the known family names and exit"
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    parser.add_argument("--version", action="version", version=f"lverror {__version__}")
    return parser


def _as_dict(info: ErrorInfo) -> dict[str, object]:
    return {
        "code": info.code,
        "message": info.message,
        "family": info.family,
        "is_error": info.is_error,
        "is_warning": info.is_warning,
    }


def _emit_records(records: list[ErrorInfo], as_json: bool) -> None:
    if as_json:
        print(json.dumps([_as_dict(rec) for rec in records], indent=2))
        return
    for rec in records:
        print(format_line(rec.code))


def _run_search(text: str, as_json: bool) -> int:
    results = search(text)
    _emit_records(results, as_json)
    return 0 if results else 1


def _run_family(name: str, as_json: bool) -> int:
    results = in_family(name)
    _emit_records(results, as_json)
    return 0 if results else 1


def _run_list_families(as_json: bool) -> int:
    names = list(families())
    if as_json:
        print(json.dumps(names, indent=2))
    else:
        for name in names:
            print(name)
    return 0


def _run_code(raw: str, as_json: bool) -> int:
    code = parse_code(raw)
    info = describe(code)
    if as_json:
        print(json.dumps(_as_dict(info), indent=2))
    else:
        print(format_line(code))
    return 0 if (info.message is not None or info.family is not None) else 1


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line tool. Returns the process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.list_families:
            return _run_list_families(args.json)
        if args.search is not None:
            return _run_search(args.search, args.json)
        if args.family is not None:
            return _run_family(args.family, args.json)
        if args.code is not None:
            return _run_code(args.code, args.json)
    except ValueError as exc:
        print(f"lverror: {exc}", file=sys.stderr)
        return 2
    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
