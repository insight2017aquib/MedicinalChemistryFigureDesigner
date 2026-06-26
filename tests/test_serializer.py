"""Tests for FSL serialization and round-trip consistency."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from figure_agent.fsl.parser import load_yaml, parse
from figure_agent.fsl.serializer import to_dict, to_json, to_yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
MINIMAL_FIGURE = REPO_ROOT / "examples" / "minimal_figure.yaml"


def test_to_yaml_produces_mapping() -> None:
    """Serialized YAML should remain a parseable mapping."""
    figure = parse(load_yaml(MINIMAL_FIGURE))
    yaml_text = to_yaml(figure)
    loaded = yaml.safe_load(yaml_text)

    assert isinstance(loaded, dict)
    assert loaded["metadata"]["id"] == "fig-001"


def test_to_json_produces_object() -> None:
    """Serialized JSON should remain a parseable object."""
    figure = parse(load_yaml(MINIMAL_FIGURE))
    json_text = to_json(figure)
    loaded = json.loads(json_text)

    assert loaded["fsl_version"] == "0.3.0"
    assert loaded["layout"]["type"] == "single-panel"


def test_yaml_round_trip_consistency() -> None:
    """YAML serialization round-trip should preserve semantic content."""
    original = parse(load_yaml(MINIMAL_FIGURE))
    round_tripped = parse(yaml.safe_load(to_yaml(original)))

    assert to_dict(original) == to_dict(round_tripped)


def test_json_round_trip_consistency() -> None:
    """JSON serialization round-trip should preserve semantic content."""
    original = parse(load_yaml(MINIMAL_FIGURE))
    round_tripped = parse(json.loads(to_json(original)))

    assert to_dict(original) == to_dict(round_tripped)
