"""Tests for the FSL parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from figure_agent.fsl.exceptions import FSLParseError, FSLSchemaError
from figure_agent.fsl.parser import load_yaml, parse, validate_schema
from helpers import valid_document

REPO_ROOT = Path(__file__).resolve().parents[1]
MINIMAL_FIGURE = REPO_ROOT / "examples" / "minimal_figure.yaml"


def test_parse_valid_document() -> None:
    """A valid document should parse into a typed Figure object."""
    figure = parse(valid_document())

    assert figure.metadata.id == "fig-001"
    assert figure.layout.type == "single-panel"
    assert figure.layout.panels[0].object_refs == ["slot-1"]
    assert figure.content_slots[0].id == "slot-1"


def test_load_yaml_example_file() -> None:
    """The repository example YAML should load and parse successfully."""
    data = load_yaml(MINIMAL_FIGURE)
    figure = parse(data)

    assert figure.metadata.title == "Placeholder Figure"
    assert figure.template.ref == "templates/single-panel.md"


def test_missing_required_field_raises_schema_error() -> None:
    """Missing required fields should raise FSLSchemaError."""
    document = valid_document()
    del document["metadata"]["id"]

    with pytest.raises(FSLSchemaError) as exc_info:
        validate_schema(document)

    assert "metadata.id" in str(exc_info.value)


def test_invalid_yaml_file_raises_parse_error(tmp_path: Path) -> None:
    """Malformed YAML should raise FSLParseError."""
    bad_file = tmp_path / "bad.yaml"
    bad_file.write_text("fsl_version: [unclosed", encoding="utf-8")

    with pytest.raises(FSLParseError):
        load_yaml(bad_file)
