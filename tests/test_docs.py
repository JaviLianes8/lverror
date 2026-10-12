"""The documentation is executable: doctests, README and GUIDE examples and transcripts run."""

from __future__ import annotations

import doctest
import importlib
import pkgutil
import re
import shlex
from pathlib import Path

import pytest
from _cli_command import run_cli

import lverror

_ROOT = Path(__file__).resolve().parent.parent
_MODULES = ["lverror"] + [f"lverror.{m.name}" for m in pkgutil.iter_modules(lverror.__path__)]
_PYTHON = re.compile(r"```python\n(.*?)```", re.DOTALL)
_SHELL = re.compile(r"```\n(\$ lverror.*?)```", re.DOTALL)
_DOCS = ["README.md", "GUIDE.md"]


@pytest.mark.parametrize("name", _MODULES)
def test_module_doctests_pass(name: str) -> None:
    result = doctest.testmod(importlib.import_module(name), optionflags=doctest.ELLIPSIS)
    assert result.failed == 0


@pytest.mark.parametrize("name", lverror.__all__)
def test_every_public_name_has_a_docstring_with_an_example(name: str) -> None:
    doc = getattr(lverror, name).__doc__ or ""
    assert ">>>" in doc, name


def test_the_doctests_cover_every_public_name() -> None:
    finder = doctest.DocTestFinder()
    examples = "".join(
        example.source
        for module in _MODULES
        for test in finder.find(importlib.import_module(module))
        for example in test.examples
    )
    for name in lverror.__all__:
        assert re.search(rf"\b{name}\b", examples), name


@pytest.mark.parametrize("document", _DOCS)
def test_document_examples_run(document: str) -> None:
    blocks = _PYTHON.findall((_ROOT / document).read_text(encoding="utf-8"))
    assert blocks, document
    for block in blocks:
        exec(compile(block, document, "exec"), {})


def _transcripts(document: str) -> list[tuple[list[str], str]]:
    runs: list[tuple[list[str], str]] = []
    for block in _SHELL.findall((_ROOT / document).read_text(encoding="utf-8")):
        for chunk in block.split("$ lverror")[1:]:
            command, _, output = chunk.partition("\n")
            runs.append((shlex.split(command), output))
    return runs


@pytest.mark.parametrize("document", _DOCS)
def test_document_transcripts_match_the_real_command(document: str) -> None:
    runs = _transcripts(document)
    assert runs, document
    for args, output in runs:
        result = run_cli(*args)
        assert result.returncode in (0, 1), (args, result.stderr)
        assert result.stdout == output, args


def test_guide_covers_every_public_name() -> None:
    text = (_ROOT / "GUIDE.md").read_text(encoding="utf-8")
    for name in lverror.__all__:
        assert re.search(rf"\b{name}\b", text), name


@pytest.mark.parametrize("document", [*_DOCS, "CHANGELOG.md"])
def test_documents_use_absolute_links(document: str) -> None:
    text = (_ROOT / document).read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        assert target.startswith(("https://", "#")), f"{document}: {target}"


def test_examples_import_only_public_names() -> None:
    for document in _DOCS:
        text = (_ROOT / document).read_text(encoding="utf-8")
        assert not re.search(r"lverror\._[a-z]", text), document


def test_guide_range_table_matches_the_code() -> None:
    text = (_ROOT / "GUIDE.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| ([a-zA-Z][\w -]*?) \| ", text, re.MULTILINE)
    assert [row for row in rows if row != "Family"] == list(lverror.families())
