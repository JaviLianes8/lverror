import lverror


def test_explain_returns_the_message_for_a_known_general_code() -> None:
    assert lverror.explain(7) == (
        "File not found. The file might be in a different location or deleted. Use the "
        "command prompt or the file explorer to verify that the path is correct."
    )


def test_explain_knows_the_short_common_codes() -> None:
    assert lverror.explain(2) == "Memory is full."
    assert lverror.explain(42) == "Generic error."


def test_explain_knows_a_python_integration_code() -> None:
    assert lverror.explain(1672) == "There was an unknown Python error in the operation."


def test_explain_knows_a_visa_code() -> None:
    assert lverror.explain(-1073807339) == "Timeout expired before operation completed."


def test_explain_knows_a_daqmx_code() -> None:
    assert lverror.explain(-200088) == "The task specified is invalid or does not exist."


def test_explain_knows_an_instrument_driver_code() -> None:
    assert lverror.explain(-1240) == "The instrument timed out."


def test_explain_knows_a_dde_code() -> None:
    assert lverror.explain(14001) == "Invalid refnum."


def test_explain_returns_none_for_an_unknown_code() -> None:
    assert lverror.explain(123456789) is None


def test_explain_returns_none_for_code_zero() -> None:
    assert lverror.explain(0) is None
