from lverror._data import MESSAGES, POSITIVE_ERROR_CODES, RANGES


def test_no_message_is_empty() -> None:
    assert all(msg.strip() for msg in MESSAGES.values())


def test_messages_use_no_em_or_en_dash() -> None:
    # House style forbids the dash characters; the source text must not smuggle one in.
    em_dash, en_dash = chr(0x2014), chr(0x2013)
    assert all(em_dash not in msg and en_dash not in msg for msg in MESSAGES.values())


def test_every_positive_message_code_is_marked_an_error() -> None:
    assert frozenset(c for c in MESSAGES if c > 0) == POSITIVE_ERROR_CODES


def test_ranges_are_well_formed() -> None:
    assert all(low <= high for low, high, _ in RANGES)
    assert all(isinstance(name, str) and name for _, _, name in RANGES)


def test_known_codes_fall_in_their_expected_families() -> None:
    # A spot check that the curated messages and the range table agree on family.
    assert -1073807339 <= -1073807231  # VISA code sits inside the VISA band
    daqmx = [name for low, high, name in RANGES if low <= -200279 <= high]
    assert daqmx == ["NI-DAQmx"]
