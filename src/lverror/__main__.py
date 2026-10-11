"""Entry point so the tool runs as ``python -m lverror``."""

from __future__ import annotations

from ._cli import main

if __name__ == "__main__":
    raise SystemExit(main())
