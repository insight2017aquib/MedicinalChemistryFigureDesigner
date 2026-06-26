"""Serialize FSL figure objects to YAML and JSON."""

from __future__ import annotations

import json
from typing import Any

import yaml

from figure_agent.fsl.models import Figure


def to_dict(figure: Figure) -> dict[str, Any]:
    """Convert a ``Figure`` instance to a plain dictionary.

    Args:
        figure: Parsed figure specification.

    Returns:
        JSON-compatible dictionary representation.
    """
    return figure.model_dump(mode="json", exclude_none=False)


def to_json(figure: Figure, *, indent: int = 2) -> str:
    """Serialize a ``Figure`` instance to a JSON string.

    Args:
        figure: Parsed figure specification.
        indent: JSON indentation level.

    Returns:
        JSON document string.
    """
    return json.dumps(to_dict(figure), indent=indent, sort_keys=False)


def to_yaml(figure: Figure) -> str:
    """Serialize a ``Figure`` instance to a YAML string.

    Args:
        figure: Parsed figure specification.

    Returns:
        YAML document string.
    """
    return yaml.safe_dump(
        to_dict(figure),
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )
