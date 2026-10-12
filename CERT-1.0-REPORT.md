# lverror 1.0.0 certification report

Progress:
- [x] Branch `release/1.0.0` created from `main` (0.3.0)
- [x] Baseline gates run on 0.3.0
- [x] Ground truth: every message re-derived from real sources (item 7)
- [x] API review and 1.0.0 API changes (item 1)
- [x] Errors, typing, docstrings and doctests (items 2 to 5)
- [x] Contract, fuzz and mutation round (items 6, 9, 18)
- [x] Docs: README, GUIDE, CHANGELOG (items 11, 12)
- [x] Packaging, e2e and upgrade from PyPI 0.3.0 (items 8, 10, 13, 14)
- [x] Version bump to 1.0.0
- [x] Independent reviewer and five QA lenses report PASS (items 16, 19)
- [x] Gates (item 15)
- [x] PR and trace guard (item 17); merge and publish pending
- [x] Owner decision: descriptions rewritten in the library's own words, NI sources test-side only
- [x] Lenses a, b, d re-run as fresh agents on the rewritten descriptions
- [x] Report, CHANGELOG and guard updated after the rewrite
- [x] NI and wiki source copies removed from the repository (local test references only)

## Scorecard (author)

| # | Item | Verdict | Evidence |
| --- | --- | --- | --- |
| 1 | API reviewed for stability | PASS | Same 18 names as 0.3.0; argument validation (`TypeError`/`ValueError`), `SupportsIndex` code parameters, plain-`int` `ErrorInfo.code`, exclusive CLI actions; every change in CHANGELOG 1.0.0 |
| 2 | `__all__` exact | PASS | `test_contract::test_all_lists_exactly_the_public_api`; `test_docs::test_examples_import_only_public_names` |
| 3 | Docstring with runnable example, doctests pass | PASS | `test_docs` (every module doctested, every name has `>>>` and appears in an example); README and GUIDE blocks and `$ lverror` transcripts executed |
| 4 | Typed end to end | PASS | `mypy --strict src tests` exit 0; `py.typed` in the wheel; external strict consumer clean (lens a) |
| 5 | Typed, documented, safe errors | PASS | `test_validation`, `test_round2_contracts`, `test_round4_contracts`: messages bounded for 10 MB strings and 100000-bit integers, failing reprs handled |
| 6 | Contract asserts the full promise | PASS | 386 tests; a promise test per public name plus boundary contracts from five blind rounds |
| 7 | Real ground truth | PASS | Every one of the 888 codes is documented by a captured NI source: the error files LabVIEW 2026, NI-VISA and NI-PAL install on this PC (830), the LabVIEW Wiki DAQmx page (41) and NI's 1997 manual (17, hand-paired and labelled), with size, SHA-256 and date in `MANIFEST.json`; the descriptions are the library's own words, read against NI's meaning for all 888 codes by lens b; families and error/warning classification derived from NI's lists |
| 8 | Real e2e incl. PyPI upgrade | PASS | Wheel in clean venvs, suite from the sdist with `src` removed, a sabotaged installed CLI fails 18 of 20 CLI tests (the other two only check for no traceback), PyPI 0.3.0 upgraded in place matches CHANGELOG (lens d, reviewer) |
| 9 | Seeded fuzz, no crash, hang or blow-up | PASS | `test_fuzz.py` (seed 20261012) against brute-force references; lens c: 780000 random string calls, linear scaling to 10 million characters, 8-thread consistency |
| 10 | Every interpreter on this PC | PASS | 3.10.19, 3.11.5, 3.12.12, 3.13.2, 3.14.2 green against the installed wheel (359 tests at 5af5bb2 by lens d, 372 at 0a4dfc8 by the reviewer) |
| 11 | README | PASS | `twine check --strict` PASSED; absolute links tested; problem, why (PyPI facts checked by downloading the wheels), install, quick start, GUIDE and CHANGELOG links |
| 12 | CHANGELOG dated 1.0.0 | PASS | `## [1.0.0] - 2026-10-12` with the stable surface and every behaviour change |
| 13 | pyproject | PASS | 1.0.0, Production/Stable, 3.10 to 3.14, MIT, Homepage/Source/Issues/Changelog, keywords, `dependencies = []` (contract-tested) |
| 14 | sdist and wheel contents | PASS | Wheel: modules, data file, `py.typed`, LICENSE; sdist adds the tests but not the captured NI sources or the scripts; no NI text ships, so no third-party notice is needed |
| 15 | Gates exit 0 alone | PASS | `ruff format --check .` 0, `ruff check .` 0, `mypy --strict src` 0, `pytest` 0 (386 passed), each run alone |
| 16 | Independent reviewer | PASS | items 1 to 18 PASS at 0a4dfc8, no failures |
| 17 | PR, trace guard | ready | PR #3 from `release/1.0.0`, trace guard CLEAN; merge and PyPI publish are left to the maintainer |
| 18 | Mutation round | PASS | author round: 34 mutations, 4 survivors closed, 1 equivalent; blind lens (e): five rounds, 165 new mutations, every non-equivalent survivor closed |
| 19 | Five QA lenses | PASS | a, b, c, d, e all PASS after their findings were fixed and re-verified |

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
- 34 documented VISA codes, including every positive VISA completion code, reported no
  family because the VISA range stopped at -1073807231.
- The NI-DAQmx range stopped at 209999 while NI-DAQmx codes run to 239999.

## Author mutation round (item 18)

Each mutation was applied alone to a scratch copy of the repository, the full suite run with
`-x`, and the copy restored. "Caught by" is the first failing test. 34 mutations: 29 killed
at once, 4 survived and were killed by new contracts on re-application, 1 equivalent.

| Mutation | File | Result | Caught by |
| --- | --- | --- | --- |
| zero counted as an error | `_core.py` | killed | `test_classify.py::test_zero_is_neither_error_nor_warning` |
| zero counted as a warning | `_core.py` | killed | `test_classify.py::test_zero_is_neither_error_nor_warning` |
| range low bound exclusive | `_core.py` | killed | `test_classify.py::test_general_labview_family_covers_its_range` |
| VISA range back to the old narrow end | `_data.py` | killed | `test_ranges_truth.py::test_every_installed_visa_code_falls_in_the_visa_ranges` |
| NI-DAQmx negative range back to 209999 | `_data.py` | killed | `test_ranges_truth.py::test_ni_daqmx_ranges_hold_every_daqmx_family_span` |
| network range one short | `_data.py` | killed | `test_ranges_truth.py::test_quoted_ranges_match_the_1997_table` |
| general LabVIEW range back to 16000 | `_data.py` | killed | `test_ranges_truth.py::test_positive_labview_codes_below_17000_all_have_a_family` |
| warning set taken from the wrong source | `_data.py` | killed | `test_classify.py::test_positive_documented_codes_are_errors_not_warnings` |
| duplicate guard dropped | `_data.py` | survived, then killed | new `test_query::test_data_loader_refuses_a_duplicate_code` |
| bool accepted as a code | `_validate.py` | killed | `test_docs.py::test_document_examples_run[GUIDE.md]` |
| INT32_MAX off by one | `_validate.py` | killed | `test_validation.py::test_code_functions_refuse_values_outside_int32[above-explain]` |
| INT32_MIN excluded | `_validate.py` | killed | `test_validation.py::test_code_functions_accept_the_int32_limits[-2147483648-explain]` |
| error messages echo huge input | `_validate.py` | killed | `test_validation.py::test_unknown_family_message_stays_short` |
| two's complement upper bound inclusive | `_format.py` | killed | `test_docs.py::test_document_examples_run[GUIDE.md]` |
| two's complement off by one | `_format.py` | killed | `test_cli_e2e.py::test_lookup_prints_ni_text_and_exits_zero[0xBFFF0015]` |
| underscores accepted in decimal | `_format.py` | killed | `test_docs.py::test_document_examples_run[GUIDE.md]` |
| negative hex refused | `_format.py` | killed | `test_fuzz.py::test_parse_code_round_trips_decimal_and_hex` |
| severity words swapped | `_format.py` | killed | `test_cli_e2e.py::test_family_listing_contains_a_known_dde_code` |
| no-information wording changed | `_format.py` | killed | `test_cli_e2e.py::test_unknown_code_exits_one` |
| search case-sensitive on the message | `_query.py` | killed | `test_cli_e2e.py::test_search_finds_the_visa_timeout` |
| search limit off by one | `_query.py` | killed | `test_docs.py::test_module_doctests_pass[lverror._query]` |
| nearest tie goes to the higher code | `_query.py` | killed | `test_fuzz.py::test_nearest_agrees_with_a_brute_force_reference` |
| family name not stripped | `_query.py` | survived, then killed | new `test_query::test_in_family_ignores_surrounding_whitespace` |
| families sorted instead of table order | `_query.py` | killed | `test_docs.py::test_module_doctests_pass[lverror._query]` |
| codes not sorted | `_query.py` | equivalent | the data file is written in code order, so `sorted()` is a no-op today |
| TABLE accepts bool keys | `_table.py` | killed | `test_validation.py::test_table_treats_non_codes_as_missing[True]` |
| UnknownCodeError carries the key as text | `_table.py` | killed | `test_docs.py::test_module_doctests_pass[lverror._table]` |
| CLI search always exits 0 | `_cli.py` | survived, then killed | new `test_cli_e2e::test_search_without_a_match_exits_one_and_prints_nothing` |
| CLI code exit ignores the family | `_cli.py` | survived, then killed | new `test_cli_e2e::test_undocumented_code_in_a_known_family_exits_zero` |
| CLI actions not exclusive | `_cli.py` | killed | `test_cli_e2e.py::test_two_actions_in_one_run_exit_two` |
| CLI catches the wrong error | `_cli.py` | killed | `test_cli_e2e.py::test_bad_input_exits_two_with_a_message` |
| describe swaps error and warning | `_core.py` | killed | `test_cli_e2e.py::test_json_output_carries_every_field` |
| one message loses its full stop | `_messages.json` | killed | `test_cli_e2e.py::test_lookup_prints_ni_text_and_exits_zero[14001]` |
| CLI JSON drops is_warning | `_cli.py` | killed | `test_cli_e2e.py::test_json_output_carries_every_field` |

## Packaging and end-to-end (items 8, 10, 14), author run

- `python -m build` and `twine check --strict`: both artifacts PASSED.
- Wheel: the nine package modules, `_messages.json`, `py.typed`, LICENSE and metadata, nothing
  else. Sdist: `src`, `tests` with the source fixtures, the two data scripts, README, GUIDE,
  CHANGELOG, LICENSE, pyproject, plus the `.gitignore` hatchling always adds. NOTICE was
  added later, after lens d (it ships in both artifacts).
- The wheel installed into a fresh venv on each of 3.10.19, 3.11.5, 3.12.12, 3.13.2 and
  3.14.2; the suite from the extracted sdist, with `src` removed so it imports the installed
  wheel and drives its console script, gave 315 passed on every one.
- PyPI 0.3.0 installed, then upgraded in place to the 1.0.0 wheel: `explain(-200088)` changes
  to NI's exact text, `family(1073676294)` from `None` to `VISA`, `explain(True)` from a
  message to `TypeError`, as CHANGELOG 1.0.0 lists.

## Blind mutation rounds by QA lens (e) (items 18 and 19e)

Each round was designed from the source alone, without the author's table, applied one
mutation at a time to the lens's own clone, and run against the full suite with `-x`. Every
round first re-applied the previous round's survivors and confirmed them killed.

| Round | State | Mutations | Killed | Equivalent or text only | Survived, then contract added | New contracts |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | c50e91d | 73 | 62 | 1 | 10 | `tests/test_boundaries.py` |
| 2 | 18c77cb | 30 | 18 | 3 | 9 | `tests/test_round2_contracts.py` |
| 3 | 60546d2 | 27 | 19 | 2 | 6 | `tests/test_round3_contracts.py` |
| 4 | 0a4dfc8 | 21 | 11 | 3 | 7 | `tests/test_round4_contracts.py` |
| 5 | 762acbf | 14 | 10 | 3 | 1 | `test_round4_contracts::test_module_form_usage_names_the_program_lverror` |
| total | | 165 | 120 | 12 | 33, all closed | |

Equivalent mutations, with the reason: the warning set built from every source except the
LabVIEW file (no positive code comes from the other sources); the union with the listed
errors taken before or after removing VISA completions (no listed code is a VISA completion);
shipped positives dropped from the error set (all of them are listed); `codes()` in file order
(the data file is sorted); a repeated code in `positive_errors` (read into a set); JSON
written without ASCII escaping (all text is ASCII); two disjoint range rows swapped; NOTICE
dropped from the sdist include list (hatchling ships license files anyway, and a contract pins
the license-files entry); two text-only changes, later pinned anyway (the range message and
the NOTICE sentence). Gaps the rounds closed: range edges on both sides of every family, entry
source tags, the shipped error list against its fixture, `0X` prefixes and the 64-character
cap, query stripping and limit checks on empty queries, CLI exit codes for no action, empty
families, every pair of actions and the module form, JSON shapes, `nearest` at both ends,
closed-pipe exit code and quiet stderr, runnable help examples, and short error forms.

## Independent reviews (items 16 and 19)

Every reviewer was a fresh agent that read the factory rules and CERT-1.0.md first, worked in
its own clone, ran things rather than reading, and reported back privately. Lenses c and d and
the first item 16 reviewer were cut by a usage limit and relaunched fresh.

| Lens | First verdict | Findings | Final verdict |
| --- | --- | --- | --- |
| a. API and docs | FAIL (1 high, 1 medium, 4 low) | README said lvkit ships no error table (it has about 1300 messages); empty-family exit code undocumented; `TABLE[...]` typed `int` only; CHANGELOG incomplete against 0.3.0; unbounded `UnknownCodeError` message; search normalisation undocumented | PASS at 18c77cb: all fixed; examples, transcripts, strict consumer and `get_type_hints` on 3.10 and 3.14 re-run |
| b. Correctness and ground truth | FAIL (1 medium, 4 low, 2 info) | 888 of 888 messages verified, but 369 positive codes NI lists were reported as warnings because their text is not shipped; provenance wording; manifest silent on two excerpt edits; case of bold tags | PASS at 18c77cb: the 1026-code error list equals its own derivation from the installed file, 0 mismatches in 43077 classification cases, 888 of 888 messages |
| c. Adversarial and robustness | FAIL (2 medium, 3 low, 3 info) | traceback when the reader closes the pipe; deadline traceback lost under capture; long `UnknownCodeError` repr; lying `str` subclasses; negative-hex hint | PASS at d586272: closed pipes quiet in 12 runs, deadline traceback visible without `-s`, fuzz regression clean; accepted: a stdlib-named file in the current directory shadows imports (ordinary Python path behaviour), exceptions from a caller's own `__index__` propagate (documented) |
| d. Packaging and real e2e | FAIL (1 medium, 1 low, 3 info) | no notice for the NI text and the CC BY 3.0 wiki data; unknown-family exit code wording | PASS at 5af5bb2: NOTICE in both artifacts, 359 passed from the sdist on 3.10 to 3.14 against the installed wheel, sdist install, 0.3.0 upgrade matches CHANGELOG |
| e. Contract strength | FAIL (10 survivors) | five blind rounds, see above | PASS at 3e32a41: R12 re-applied and killed, every non-equivalent mutation of all five rounds killed; the lens judged the surface exhausted |
| Item 16 reviewer | PASS | items 1 to 18 PASS at 0a4dfc8 (17 pending), no failures | PASS |

## Decisions for the maintainer

- The messages are NI's text, verbatim, and the NI-DAQmx text comes through the LabVIEW Wiki
  under CC BY 3.0. NOTICE says the NI text is not covered by the MIT license and attributes the
  wiki. Shipping NI's wording is the premise of the package since 0.1.0; 1.0.0 makes it exact
  and sourced.
- The 888-code set is unchanged. The installed LabVIEW 2026 file holds 2523 codes and the wiki
  8507 DAQmx codes; adding them is possible in a minor release but was kept out of the
  certification to avoid shipping more third-party text without a decision.
- `is_error` now trusts NI's LabVIEW file for every positive code it lists (1026 errors; only
  40624 is a warning), shipped as numbers only. Positive codes outside that file, such as the
  NI-PAL 50000 block and DAQmx positives, stay warnings by convention.
- Ranges marked "derived" in `_data.py` and GUIDE (VISA, NI-DAQmx, general LabVIEW) are not
  quoted from NI; they cover every code NI lists for those families. Negative LabVIEW codes
  outside every range (COM codes, for example) have no family, documented as a limit.
- Code arguments are now validated (`bool`, floats and strings raise `TypeError`, values
  outside int32 raise `ValueError`); 0.3.0 silently looked up `True` as code 1.
- The README links to GUIDE.md and NOTICE on `main`, so publish after the merge.

## Owner decision: descriptions in the library's own words

After the first certification pass the owner decided the package must not ship NI's wording.
What changed:

- All 888 descriptions were rewritten to match the meaning of NI's error descriptions in new
  wording, then a second pass rewrote the 214 that stayed close to NI's sentences. 885 differ
  from 0.3.0; three (1042, 1421, 1504) were already in the library's own words.
- New contracts in `tests/test_ground_truth.py`, enforced also by `scripts/refresh_data.py`: no
  description equals its NI source after normalising case and punctuation, shares a run of six
  or more consecutive words with it, or reaches a character similarity of 0.75 (difflib ratio on
  normalised text, autojunk off); and no description shares eight consecutive words with any
  captured NI entry. Highest similarity now 0.706 (code 14016); longest shared run 4 words.
- Codes, families, ranges and the error/warning classification are unchanged: they are bare
  facts derived from NI's lists (61,750 codes compared with the earlier certified state).
- The captured NI sources stay in `tests/fixtures/sources` as test-side references only; the
  sdist excludes them and the data scripts, and the tests that need them skip when absent
  (23 tests in an extracted sdist). NOTICE was removed: no NI or wiki text ships.
- README, GUIDE, docstrings, the PyPI summary and CHANGELOG say the messages are written for
  this library, matching the meaning of NI's error descriptions.

Re-run as fresh agents on the rewritten descriptions:

| Lens | First verdict | Findings | Final verdict |
| --- | --- | --- | --- |
| a. API and docs | FAIL | PyPI summary and two docstrings still claimed NI text; CHANGELOG counts; code 2 and `%s` placeholders; later, some second-pass rewrites read worse ("is wrong", chatty openings) | PASS at 7cc4c3f: docs, transcripts, doctests, strict consumer, CHANGELOG against PyPI 0.3.0 (885 changed, 3 unchanged), clarity of every changed description |
| b. Correctness and ground truth | FAIL | 28 near-verbatim short descriptions, three meaning errors (1128, 1319, 1353), one sentence equal to another code's NI text; then the similarity check missed long texts (difflib autojunk) and 1761 was over the limit | PASS at 7cc4c3f: all 888 descriptions read against NI's meaning, similarity rules re-implemented independently, planted copies (short, long, cross-code) all caught, derived facts unchanged, no NI sentence in either archive |
| d. Packaging and real e2e | FAIL | PyPI summary still claimed NI text | PASS at 96aad22: no NI sources, scripts or NOTICE in either archive, 362 passed and 5 skipped from the sdist on 3.10 to 3.14 against the installed wheel, sabotaged CLI caught, 0.3.0 upgrade matches CHANGELOG |

Lenses c and e and the item 16 reviewer were not re-run: the rewrite changed data text and
documentation only, not code paths, and the gates, the mutation contracts and the full suite
(386 tests) stay green.

## Decisions for the maintainer after the rewrite

- The earlier "NI text verbatim" and NOTICE decisions above are superseded by this section.
- Branch history still contains the NI text from the first pass (commits before 321c4eb). A
  squash merge keeps it out of `main`'s history; a merge commit would bring it in.
- Message wording is now ours to improve; the tests only guard the distance from NI's wording
  and the code set, not the exact sentences (apart from the few quoted in docs and tests).

## NI source copies kept out of the repository

Owner decision before the merge: NI's and the LabVIEW Wiki's texts must not be in the public
repository either. The captured copies in `tests/fixtures/sources` are no longer tracked and
the folder is ignored by git, except `MANIFEST.json` (origins, sizes, SHA-256, no NI text) and
`labview-positive-codes.txt` (code numbers only). `scripts/capture_sources.py` re-creates the
rest on a machine with LabVIEW 2026 and NI-VISA, network access and `pdftotext`; it now also
writes the 1997 instrument driver pairs itself, parsed from `pdftotext -raw` (identical to the
earlier hand pairing). CONTRIBUTING explains the steps.

- Without the copies, `tests/test_ground_truth.py` and `tests/test_ranges_truth.py` skip as
  modules (18 tests); a fresh clone of the branch from GitHub gives 368 passed, 2 skipped. With
  the copies present, 386 passed.
- No tracked file shares eight consecutive words with any NI or wiki entry of the captured
  copies.
- The squash merge planned by the coordinator keeps the earlier commits that carried NI text
  out of `main`.

