"""Tests for the FSL semantic validator."""

from __future__ import annotations

import pytest

from figure_agent.fsl.exceptions import FSLValidationError
from figure_agent.fsl.parser import parse, validate_schema
from figure_agent.fsl.validator import FSLValidator
from helpers import valid_document


def test_duplicate_panel_id_raises_validation_error() -> None:
    """Duplicate panel identifiers should fail semantic validation."""
    document = valid_document()
    document["layout"]["panels"].append(
        {
            "id": "panel-a",
            "zones": ["secondary"],
            "object_refs": [],
        }
    )

    figure = validate_schema(document)

    with pytest.raises(FSLValidationError) as exc_info:
        FSLValidator().validate(figure)

    assert "duplicate panel id 'panel-a'" in str(exc_info.value)


def test_duplicate_slot_id_raises_validation_error() -> None:
    """Duplicate content slot identifiers should fail semantic validation."""
    document = valid_document()
    document["content_slots"].append(
        {
            "id": "slot-1",
            "label": "Duplicate slot",
            "type": "placeholder",
            "value": None,
        }
    )

    figure = validate_schema(document)

    with pytest.raises(FSLValidationError) as exc_info:
        FSLValidator().validate(figure)

    assert "duplicate content slot id 'slot-1'" in str(exc_info.value)


def test_invalid_layout_panel_count_raises_validation_error() -> None:
    """Layout types with incorrect panel counts should fail validation."""
    document = valid_document()
    document["layout"]["type"] = "single-panel"
    document["layout"]["panels"].append(
        {
            "id": "panel-b",
            "zones": ["secondary"],
            "object_refs": [],
        }
    )

    with pytest.raises(FSLValidationError) as exc_info:
        parse(document)

    assert "allows at most 1 panel" in str(exc_info.value)


def test_unknown_panel_object_reference_raises_validation_error() -> None:
    """Panel object references must point to defined content slots."""
    document = valid_document()
    document["layout"]["panels"][0]["object_refs"] = ["missing-slot"]

    with pytest.raises(FSLValidationError) as exc_info:
        parse(document)

    assert "references unknown object 'missing-slot'" in str(exc_info.value)


def test_unknown_template_reference_raises_validation_error() -> None:
    """Template references must match known repository templates."""
    document = valid_document()
    document["template"]["ref"] = "templates/unknown-template.md"

    with pytest.raises(FSLValidationError) as exc_info:
        parse(document)

    assert "template.ref 'templates/unknown-template.md' is unknown" in str(
        exc_info.value
    )
