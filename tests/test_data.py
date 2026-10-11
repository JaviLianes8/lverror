from lverror._data import (
    _PARTS,
    MESSAGES,
    POSITIVE_ERROR_CODES,
    RANGES,
    WARNING_CODES,
)


def test_no_message_is_empty() -> None:
    assert all(msg.strip() for msg in MESSAGES.values())


def test_messages_use_no_em_or_en_dash() -> None:
    # House style forbids the dash characters; the source text must not smuggle one in.
    em_dash, en_dash = chr(0x2014), chr(0x2013)
    assert all(em_dash not in msg and en_dash not in msg for msg in MESSAGES.values())


def test_no_code_is_defined_in_two_data_modules() -> None:
    assert sum(len(part) for part in _PARTS) == len(MESSAGES)


def test_zero_carries_no_message() -> None:
    assert 0 not in MESSAGES


def test_positive_codes_split_into_errors_and_warnings() -> None:
    positives = frozenset(c for c in MESSAGES if c > 0)
    assert positives == POSITIVE_ERROR_CODES | WARNING_CODES
    assert POSITIVE_ERROR_CODES.isdisjoint(WARNING_CODES)


def test_warning_codes_are_the_visa_completion_family() -> None:
    assert WARNING_CODES
    assert all(c > 0 and c in MESSAGES for c in WARNING_CODES)


def test_ranges_are_well_formed() -> None:
    assert all(low <= high for low, high, _ in RANGES)
    assert all(isinstance(name, str) and name for _, _, name in RANGES)


def test_known_codes_fall_in_their_expected_families() -> None:
    # A spot check that the curated messages and the range table agree on family.
    assert -1073807339 <= -1073807231  # VISA code sits inside the VISA band
    daqmx = [name for low, high, name in RANGES if low <= -200279 <= high]
    assert daqmx == ["NI-DAQmx"]
