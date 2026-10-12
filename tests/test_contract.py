"""The contract: every public name is exported and keeps its promise.

This asserts behaviour, not just presence. Add every exported name to ``PUBLIC_API`` and give
it a real behavioural check below as the library grows; the test fails if the module and this
list disagree, or if any promised behaviour regresses.
"""

import dataclasses
import importlib.resources
import re
from collections.abc import Mapping
from pathlib import Path

import lverror

PUBLIC_API: list[str] = [
    "TABLE",
    "ErrorInfo",
    "ErrorTable",
    "UnknownCodeError",
    "codes",
    "describe",
    "explain",
    "families",
    "family",
    "format_line",
    "in_family",
    "is_error",
    "is_known",
    "is_warning",
    "nearest",
    "parse_code",
    "records",
    "search",
]


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(lverror.__all__) == sorted(PUBLIC_API)


def test_every_exported_name_resolves() -> None:
    for name in lverror.__all__:
        assert hasattr(lverror, name)


def test_version_is_a_three_part_string() -> None:
    parts = lverror.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("lverror").joinpath("py.typed").is_file()


def test_explain_promise() -> None:
    assert lverror.explain(7) is not None
    assert lverror.explain(123456789) is None


def test_describe_promise() -> None:
    info = lverror.describe(7)
    assert isinstance(info, lverror.ErrorInfo)
    assert info.code == 7
    assert info.message is not None
    assert info.family == "general LabVIEW"
    assert info.is_error is True and info.is_warning is False


def test_error_info_is_a_frozen_record() -> None:
    info = lverror.describe(2)
    try:
        info.code = 3  # type: ignore[misc]
    except AttributeError:
        pass
    else:
        raise AssertionError("ErrorInfo should be frozen")


def test_is_known_promise() -> None:
    assert lverror.is_known(7) is True
    assert lverror.is_known(123456789) is False


def test_family_promise() -> None:
    assert lverror.family(-1073807339) == "VISA"
    assert lverror.family(123456789) is None


def test_is_error_and_is_warning_promise() -> None:
    assert lverror.is_error(-1073807339) is True
    assert lverror.is_warning(-1073807339) is False
    assert lverror.is_warning(200010) is True
    assert lverror.is_error(0) is False and lverror.is_warning(0) is False


def test_search_promise() -> None:
    results = lverror.search("timeout")
    assert results
    assert all("timeout" in rec.message.lower() for rec in results if rec.message)
    assert any(rec.code == -1073807339 for rec in results)
    assert lverror.search("", limit=5) == []


def test_in_family_promise() -> None:
    dde = lverror.in_family("DDE")
    assert dde
    assert all(rec.family == "DDE" for rec in dde)
    assert any(rec.code == 14001 for rec in dde)


def test_families_promise() -> None:
    fams = lverror.families()
    assert isinstance(fams, tuple)
    assert "VISA" in fams and "DDE" in fams
    assert len(fams) == len(set(fams))


def test_codes_and_records_promise() -> None:
    all_codes = lverror.codes()
    recs = list(lverror.records())
    assert len(all_codes) == len(recs)
    assert list(all_codes) == sorted(all_codes)
    assert all(rec.code in all_codes for rec in recs)


def test_nearest_promise() -> None:
    assert lverror.nearest(7).code == 7
    near = lverror.nearest(-200300)
    assert near.code in lverror.codes()


def test_format_line_promise() -> None:
    line = lverror.format_line(7)
    assert line.startswith("7 ")
    assert "File not found" in line


def test_parse_code_promise() -> None:
    assert lverror.parse_code("42") == 42
    assert lverror.parse_code("-7") == -7
    assert lverror.parse_code("0xBFFF0015") == -1073807339


def test_table_promise() -> None:
    assert isinstance(lverror.TABLE, Mapping)
    assert isinstance(lverror.TABLE, lverror.ErrorTable)
    assert lverror.TABLE[7].message is not None
    assert 7 in lverror.TABLE
    assert len(lverror.TABLE) == len(lverror.codes())


def test_unknown_code_error_promise() -> None:
    assert issubclass(lverror.UnknownCodeError, KeyError)
    try:
        lverror.TABLE[123456789]
    except lverror.UnknownCodeError:
        pass
    else:
        raise AssertionError("TABLE should raise UnknownCodeError for an undocumented code")


def test_version_matches_pyproject() -> None:
    text = (Path(__file__).resolve().parent.parent / "pyproject.toml").read_text("utf-8")
    match = re.search(r'^version = "([^"]+)"$', text, re.MULTILINE)
    assert match is not None
    assert match.group(1) == lverror.__version__


def test_package_has_no_runtime_dependencies_and_is_stable() -> None:
    text = (Path(__file__).resolve().parent.parent / "pyproject.toml").read_text("utf-8")
    assert re.search(r"^dependencies = \[\]$", text, re.MULTILINE)
    assert "Development Status :: 5 - Production/Stable" in text
    for minor in range(10, 15):
        assert f"Programming Language :: Python :: 3.{minor}" in text


def test_the_data_file_ships_inside_the_package() -> None:
    assert importlib.resources.files("lverror").joinpath("_messages.json").is_file()


def test_error_info_has_exactly_the_five_stable_fields() -> None:
    names = [field.name for field in dataclasses.fields(lverror.ErrorInfo)]
    assert names == ["code", "message", "family", "is_error", "is_warning"]
    info = lverror.describe(7)
    assert hash(info) == hash(lverror.describe(7)) and info == lverror.describe(7)


def test_every_documented_record_is_consistent() -> None:
    for info in lverror.records():
        assert info.message is not None and info.message == info.message.strip()
        assert "\n" not in info.message and "  " not in info.message
        assert chr(0x2014) not in info.message
        assert info.is_error != info.is_warning
        assert lverror.TABLE[info.code] == info == lverror.describe(info.code)
    assert lverror.explain(0) is None and 0 not in lverror.TABLE
