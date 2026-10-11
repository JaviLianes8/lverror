from collections.abc import Mapping

import lverror


def test_table_is_a_mapping() -> None:
    assert isinstance(lverror.TABLE, Mapping)


def test_table_lookup_returns_full_record() -> None:
    info = lverror.TABLE[7]
    assert info.code == 7
    assert info.message is not None
    assert info.family == "general LabVIEW"


def test_table_membership() -> None:
    assert 7 in lverror.TABLE
    assert -1073807339 in lverror.TABLE
    assert 123456789 not in lverror.TABLE


def test_table_len_matches_documented_codes() -> None:
    assert len(lverror.TABLE) == len(lverror.codes())


def test_table_iterates_in_ascending_order() -> None:
    keys = list(lverror.TABLE)
    assert keys == sorted(keys)
    assert keys == list(lverror.codes())


def test_table_get_returns_default_for_unknown() -> None:
    assert lverror.TABLE.get(123456789) is None
    assert lverror.TABLE.get(7) is not None


def test_table_getitem_raises_for_unknown() -> None:
    try:
        lverror.TABLE[123456789]
    except lverror.UnknownCodeError as exc:
        assert isinstance(exc, KeyError)
    else:
        raise AssertionError("expected UnknownCodeError")


def test_table_values_are_error_info() -> None:
    sample = lverror.TABLE[14001]
    assert isinstance(sample, lverror.ErrorInfo)


def test_error_table_repr_is_informative() -> None:
    assert "documented codes" in repr(lverror.TABLE)
