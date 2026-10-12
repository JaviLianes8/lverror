import lverror


def test_describe_assembles_a_full_record_for_a_known_code() -> None:
    info = lverror.describe(7)
    assert info.code == 7
    assert info.message is not None
    assert info.message.startswith("The file could not be found")
    assert info.family == "general LabVIEW"
    assert info.is_error is True
    assert info.is_warning is False


def test_describe_classifies_an_unknown_code_by_range_only() -> None:
    info = lverror.describe(-200300)
    assert info.code == -200300
    assert info.message is None
    assert info.family == "NI-DAQmx"
    assert info.is_error is True


def test_describe_of_a_fully_unknown_code_has_no_message_and_no_family() -> None:
    info = lverror.describe(123456789)
    assert info.message is None
    assert info.family is None
    assert info.is_warning is True


def test_describe_of_zero_is_success() -> None:
    info = lverror.describe(0)
    assert info.message is None
    assert info.is_error is False
    assert info.is_warning is False


def test_error_info_is_immutable() -> None:
    info = lverror.describe(2)
    try:
        info.code = 3  # type: ignore[misc]
    except AttributeError:
        return
    raise AssertionError("ErrorInfo should be frozen")
