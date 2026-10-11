import lverror


def test_general_labview_family_covers_its_range() -> None:
    assert lverror.describe(1).family == "general LabVIEW"
    assert lverror.describe(16000).family == "general LabVIEW"


def test_above_the_general_range_has_no_family() -> None:
    assert lverror.describe(16001).family is None


def test_visa_range_boundaries() -> None:
    assert lverror.describe(-1073807360).family == "VISA"
    assert lverror.describe(-1073807231).family == "VISA"
    assert lverror.describe(-1073807361).family is None


def test_daqmx_range_classifies_an_undocumented_code() -> None:
    info = lverror.describe(-200300)
    assert info.family == "NI-DAQmx"
    assert info.message is None


def test_network_family_wins_over_general_inside_its_band() -> None:
    assert lverror.describe(55).family == "network"
    assert lverror.describe(52).family == "general LabVIEW"
    assert lverror.describe(67).family == "general LabVIEW"


def test_user_defined_ranges_are_recognised() -> None:
    assert lverror.describe(5000).family == "user-defined"
    assert lverror.describe(-8000).family == "user-defined"
    assert lverror.describe(500000).family == "user-defined"


def test_negative_codes_are_errors() -> None:
    assert lverror.is_error(-1073807339) is True
    assert lverror.is_warning(-1073807339) is False


def test_positive_documented_codes_are_errors_not_warnings() -> None:
    assert lverror.is_error(7) is True
    assert lverror.is_warning(7) is False


def test_undocumented_positive_codes_are_warnings_by_convention() -> None:
    assert lverror.is_warning(200010) is True
    assert lverror.is_error(200010) is False


def test_zero_is_neither_error_nor_warning() -> None:
    assert lverror.is_error(0) is False
    assert lverror.is_warning(0) is False


def test_visa_completion_code_is_a_warning_not_an_error() -> None:
    # 1073676294 is VISA's "bytes read equals the input count" completion, a warning.
    assert lverror.is_warning(1073676294) is True
    assert lverror.is_error(1073676294) is False


def test_is_known_reports_documented_codes() -> None:
    assert lverror.is_known(7) is True
    assert lverror.is_known(-1073807339) is True
    assert lverror.is_known(123456789) is False
    assert lverror.is_known(0) is False


def test_family_returns_the_range_name() -> None:
    assert lverror.family(-1073807339) == "VISA"
    assert lverror.family(-200279) == "NI-DAQmx"
    assert lverror.family(-1700) == "AppleEvent"
    assert lverror.family(123456789) is None
