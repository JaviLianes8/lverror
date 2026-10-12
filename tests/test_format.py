import lverror


def test_format_line_for_a_documented_error() -> None:
    line = lverror.format_line(7)
    assert line.startswith("7 (error, general LabVIEW): ")
    assert "file could not be found" in line


def test_format_line_for_a_warning() -> None:
    line = lverror.format_line(1073676294)
    assert "warning" in line
    assert line.startswith("1073676294 ")


def test_format_line_for_an_undocumented_but_classified_code() -> None:
    line = lverror.format_line(-200300)
    assert "NI-DAQmx" in line
    assert "classified by range only" in line


def test_format_line_for_a_fully_unknown_code() -> None:
    line = lverror.format_line(123456789)
    assert "unknown family" in line
    assert "no documented information" in line


def test_parse_code_decimal() -> None:
    assert lverror.parse_code("0") == 0
    assert lverror.parse_code("42") == 42
    assert lverror.parse_code("-200088") == -200088
    assert lverror.parse_code("  7  ") == 7


def test_parse_code_hex_small_stays_positive() -> None:
    assert lverror.parse_code("0x7") == 7
    assert lverror.parse_code("0x7FFFFFFF") == 0x7FFFFFFF


def test_parse_code_hex_wraps_to_signed_32bit() -> None:
    assert lverror.parse_code("0xBFFF0015") == -1073807339
    assert lverror.parse_code("0xFFFFFFFF") == -1


def test_parse_code_rejects_garbage() -> None:
    for bad in ("", "   ", "0xZZ", "seven", "4.2"):
        try:
            lverror.parse_code(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {bad!r}")


def test_parse_code_round_trips_a_real_visa_code_into_explain() -> None:
    code = lverror.parse_code("0xBFFF0015")
    assert lverror.explain(code) == "The operation did not finish before the timeout elapsed."
