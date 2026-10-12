# lverror 1.0.0 certification report

Progress:
- [x] Branch `release/1.0.0` created from `main` (0.3.0)
- [x] Baseline gates run on 0.3.0
- [ ] Ground truth: every message re-derived from real sources (item 7)
- [ ] API review and 1.0.0 API changes (item 1)
- [ ] Errors, typing, docstrings and doctests (items 2 to 5)
- [ ] Contract, fuzz and mutation round (items 6, 9, 18)
- [ ] Docs: README, GUIDE, CHANGELOG (items 11, 12)
- [ ] Packaging, e2e and upgrade from PyPI 0.3.0 (items 8, 10, 13, 14)
- [ ] Version bump to 1.0.0
- [ ] Independent reviewer and five QA lenses report PASS (items 16, 19)
- [ ] Gates (item 15)
- [ ] PR and trace guard (item 17); merge and publish pending

## Baseline on 0.3.0 (before any change)

| Command | Result |
| --- | --- |
| `ruff format --check .`, `ruff check .`, `mypy --strict src tests` | exit 0 |
| `pytest` | 108 passed |
| `pytest --doctest-modules src` | no doctests at all |

Defects found in 0.3.0 at the start of this round, by comparing the shipped table with the
error files that LabVIEW 2026 and NI-VISA install on this PC:

- Only 224 of the 888 shipped messages matched NI's text word for word. 589 were rewritten or
  shortened, some with a changed meaning (for example VISA -1073807239 described an invalid
  protocol, while NI's text is about secure connections).
- 58 codes were not in any installed file: 41 NI-DAQmx codes and 17 instrument driver codes.
- 45 documented codes had no family because the range table was too narrow: 34 VISA codes,
  including every positive VISA completion code, fell outside the VISA range.
- The NI-DAQmx range stopped at 209999 while NI-DAQmx codes run to 239999.
