import lverror


def test_explain_returns_the_message_for_a_known_general_code() -> None:
    assert lverror.explain(7) == (
        "The file could not be found. It may have been moved or removed. Check that the path is "
        "right using a file explorer or the command prompt."
    )


def test_explain_knows_the_short_common_codes() -> None:
    assert (
        lverror.explain(2) == "There is no free memory left. Also: A file could not be found "
        "(status ERROR_FILE_NOT_FOUND)."
    )
    assert lverror.explain(42) == "An unspecified error occurred."


def test_explain_knows_a_python_integration_code() -> None:
    assert lverror.explain(1672) == "The operation hit a Python error of unknown kind."


def test_explain_knows_a_visa_code() -> None:
    assert (
        lverror.explain(-1073807339) == "The operation did not finish before the timeout elapsed."
    )


def test_explain_knows_a_daqmx_code() -> None:
    assert (
        lverror.explain(-200088)
        == "Either the requested task cannot be found or it is not a valid task."
    )


def test_explain_knows_an_instrument_driver_code() -> None:
    assert lverror.explain(-1240) == "The instrument did not respond within the time limit."


def test_explain_knows_a_dde_code() -> None:
    assert lverror.explain(14001) == "The refnum is not valid."


def test_explain_returns_none_for_an_unknown_code() -> None:
    assert lverror.explain(123456789) is None


def test_explain_returns_none_for_code_zero() -> None:
    assert lverror.explain(0) is None
