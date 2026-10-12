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
  CHANGELOG, LICENSE, pyproject, plus the `.gitignore` hatchling always adds.
- The wheel installed into a fresh venv on each of 3.10.19, 3.11.5, 3.12.12, 3.13.2 and
  3.14.2; the suite from the extracted sdist, with `src` removed so it imports the installed
  wheel and drives its console script, gave 315 passed on every one.
- PyPI 0.3.0 installed, then upgraded in place to the 1.0.0 wheel: `explain(-200088)` changes
  to NI's exact text, `family(1073676294)` from `None` to `VISA`, `explain(True)` from a
  message to `TypeError`, as CHANGELOG 1.0.0 lists.
