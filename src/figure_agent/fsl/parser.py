"""Parse raw FSL documents into typed Python objects."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from figure_agent.fsl.exceptions import FSLParseError, FSLSchemaError
from figure_agent.fsl.models import Figure
from figure_agent.fsl.validator import FSLValidator

PathLike = str | Path


def load_yaml(source: PathLike) -> dict[str, Any]:
    """Load a YAML FSL document from a file path.

    Args:
        source: Filesystem path to a YAML file.

    Returns:
        Parsed document as a dictionary.

    Raises:
        FSLParseError: If the file cannot be read or parsed.
    """
    path = Path(source)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise FSLParseError(
            f"Unable to read YAML file: {exc}", source=str(path)
        ) from exc

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise FSLParseError(f"Invalid YAML syntax: {exc}", source=str(path)) from exc

    if not isinstance(data, dict):
        raise FSLParseError(
            "YAML root must be a mapping/object",
            source=str(path),
        )

    return data


def load_json(source: PathLike) -> dict[str, Any]:
    """Load a JSON FSL document from a file path.

    Args:
        source: Filesystem path to a JSON file.

    Returns:
        Parsed document as a dictionary.

    Raises:
        FSLParseError: If the file cannot be read or parsed.
    """
    path = Path(source)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise FSLParseError(
            f"Unable to read JSON file: {exc}", source=str(path)
        ) from exc

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise FSLParseError(f"Invalid JSON syntax: {exc}", source=str(path)) from exc

    if not isinstance(data, dict):
        raise FSLParseError(
            "JSON root must be an object",
            source=str(path),
        )

    return data


def validate_schema(data: dict[str, Any]) -> Figure:
    """Validate raw data against the FSL Pydantic schema.

    Args:
        data: Parsed FSL document dictionary.

    Returns:
        A validated ``Figure`` instance.

    Raises:
        FSLSchemaError: If required fields are missing or types are invalid.
    """
    try:
        return Figure.model_validate(data)
    except ValidationError as exc:
        errors = [_format_validation_error(error) for error in exc.errors()]
        raise FSLSchemaError("FSL schema validation failed", errors=errors) from exc


def parse(
    data: dict[str, Any],
    *,
    run_semantic_validation: bool = True,
) -> Figure:
    """Parse and optionally semantically validate an FSL document.

    Args:
        data: Parsed FSL document dictionary.
        run_semantic_validation: When ``True``, run semantic checks after schema
            validation.

    Returns:
        A validated ``Figure`` instance.

    Raises:
        FSLSchemaError: If schema validation fails.
        FSLValidationError: If semantic validation fails.
    """
    figure = validate_schema(data)
    if run_semantic_validation:
        FSLValidator().validate(figure)
    return figure


def _format_validation_error(error: dict[str, Any]) -> str:
    """Format a Pydantic validation error entry as a readable string."""
    location = ".".join(str(part) for part in error.get("loc", ()))
    message = error.get("msg", "invalid value")
    if location:
        return f"{location}: {message}"
    return message
