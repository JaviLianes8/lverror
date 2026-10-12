"""Contracts from the fourth blind mutation round: closed pipes, help examples, short errors."""

from __future__ import annotations

import errno
import os
import re
import shlex
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from _cli_command import cli_command, run_cli

import lverror
from lverror._cli import main


class _ClosedStdout:
    """A stdout whose flush fails the way a closed pipe does."""

    def __init__(self, err: int, fd: int) -> None:
        self.err = err
        self.fd = fd

    def write(self, text: str) -> int:
        return len(text)

    def flush(self) -> None:
        raise OSError(self.err, os.strerror(self.err))

    def fileno(self) -> int:
        return self.fd


@pytest.fixture
def scratch_fd() -> Iterator[int]:
    fd, path = tempfile.mkstemp()
    try:
        yield fd
    finally:
        os.close(fd)
        os.unlink(path)


@pytest.mark.parametrize("err", [errno.EPIPE, errno.EINVAL])
def test_a_closed_pipe_exits_one(
    monkeypatch: pytest.MonkeyPatch, scratch_fd: int, err: int
) -> None:
    monkeypatch.setattr(sys, "stdout", _ClosedStdout(err, scratch_fd))
    assert main(["7"]) == 1


def test_other_output_errors_propagate(monkeypatch: pytest.MonkeyPatch, scratch_fd: int) -> None:
    monkeypatch.setattr(sys, "stdout", _ClosedStdout(errno.ENOSPC, scratch_fd))
    with pytest.raises(OSError):
        main(["7"])


def test_output_closed_before_any_write_leaves_stderr_empty() -> None:
    env = dict(os.environ)
    package_parent = str(Path(lverror.__file__).resolve().parent.parent)
    env["PYTHONPATH"] = package_parent + os.pathsep + env.get("PYTHONPATH", "")
    with subprocess.Popen(
        [*cli_command(), "7"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
    ) as proc:
        assert proc.stdout is not None and proc.stderr is not None
        proc.stdout.close()
        err = proc.stderr.read().decode("utf-8", "replace")
        code = proc.wait(timeout=60)
    assert (err, code in (0, 1)) == ("", True)


def test_every_help_example_runs() -> None:
    help_text = run_cli("--help").stdout.split("Examples:", 1)[1]
    examples = [m.group(1) for m in re.finditer(r"^\s+lverror (.*?)\s{2,}", help_text, re.M)]
    assert len(examples) >= 6
    for example in examples:
        result = run_cli(*shlex.split(example))
        assert result.returncode in (0, 1), (example, result.stderr)


@pytest.mark.parametrize("bad", ["x" * 100_000, ["x"] * 100_000], ids=["str", "list"])
def test_type_errors_never_echo_the_input(bad: object) -> None:
    with pytest.raises(TypeError) as caught:
        lverror.explain(bad)  # type: ignore[arg-type]
    assert len(str(caught.value)) < 100


def test_the_table_takes_no_attributes() -> None:
    with pytest.raises(AttributeError):
        lverror.TABLE.extra = 1  # type: ignore[attr-defined]


def test_range_message_names_the_bits_needed() -> None:
    with pytest.raises(ValueError, match=r"\(the value needs 32 bits\)$"):
        lverror.explain(2**31)


def test_notice_keeps_the_ni_text_outside_the_mit_grant() -> None:
    notice = (Path(__file__).resolve().parent.parent / "NOTICE").read_text(encoding="utf-8")
    assert "which is not covered by that license" in " ".join(notice.split())
