import pytest

import lverror
from lverror import _data


def test_search_is_case_insensitive_and_matches_the_message() -> None:
    lower = lverror.search("file not found")
    upper = lverror.search("FILE NOT FOUND")
    assert lower == upper
    assert any(rec.code == 7 for rec in lower)


def test_search_respects_the_limit() -> None:
    capped = lverror.search("the", limit=3)
    assert len(capped) == 3


def test_search_sorts_by_code() -> None:
    results = lverror.search("timeout")
    assert [r.code for r in results] == sorted(r.code for r in results)


def test_search_blank_returns_empty() -> None:
    assert lverror.search("   ") == []


def test_in_family_returns_only_that_family() -> None:
    visa = lverror.in_family("VISA")
    assert visa
    assert {rec.family for rec in visa} == {"VISA"}


def test_in_family_is_case_insensitive() -> None:
    assert lverror.in_family("dde") == lverror.in_family("DDE")


def test_in_family_rejects_an_unknown_name() -> None:
    try:
        lverror.in_family("made up")
    except ValueError as exc:
        assert "unknown family" in str(exc)
    else:
        raise AssertionError("expected ValueError for an unknown family")


def test_families_are_unique_and_known() -> None:
    fams = lverror.families()
    assert len(fams) == len(set(fams))
    for expected in ("VISA", "NI-DAQmx", "DDE", "general LabVIEW"):
        assert expected in fams


def test_codes_match_records() -> None:
    assert len(lverror.codes()) == len(list(lverror.records()))


def test_nearest_exact_and_offset() -> None:
    assert lverror.nearest(7).code == 7
    # -200300 is undocumented; the nearest documented NI-DAQmx code is returned.
    near = lverror.nearest(-200300)
    assert near.message is not None
    assert near.code in lverror.codes()


def test_every_record_in_a_family_classifies_to_that_family() -> None:
    for name in lverror.families():
        for rec in lverror.in_family(name):
            assert lverror.family(rec.code) == name


def test_in_family_ignores_surrounding_whitespace() -> None:
    assert lverror.in_family("  DDE \t") == lverror.in_family("DDE")


def test_data_loader_refuses_a_duplicate_code() -> None:
    raw = '{"messages": [[7, "labview-errors", "a"], [7, "labview-errors", "b"]]}'
    with pytest.raises(ValueError, match="duplicate error code"):
        _data._load(raw)


def test_data_loader_marks_only_positive_visa_codes_as_warnings() -> None:
    raw = '{"messages": [[1073676294, "visa-errors", "a"], [7, "labview-errors", "b"]]}'
    messages, visa, listed = _data._load(raw)
    assert messages == {1073676294: "a", 7: "b"} and visa == frozenset({1073676294})
    assert listed == frozenset()
