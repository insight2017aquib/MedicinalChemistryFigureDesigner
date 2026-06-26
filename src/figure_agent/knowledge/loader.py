"""Load knowledge pack manifests from disk."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from figure_agent.knowledge.exceptions import (
    KnowledgePackParseError,
    KnowledgePackSchemaError,
)
from figure_agent.knowledge.models import KnowledgePackManifest
from figure_agent.knowledge.schema import PACK_MANIFEST_FILENAME

PathLike = str | Path


def load_pack_yaml(source: PathLike) -> dict[str, Any]:
    """Load a YAML manifest into a dictionary."""
    path = Path(source)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise KnowledgePackParseError(
            f"Unable to read pack manifest: {exc}",
            source=str(path),
        ) from exc

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise KnowledgePackParseError(
            f"Invalid YAML syntax: {exc}",
            source=str(path),
        ) from exc

    if not isinstance(data, dict):
        raise KnowledgePackParseError(
            "Pack manifest root must be a mapping/object",
            source=str(path),
        )
    return data


def load_pack_json(source: PathLike) -> dict[str, Any]:
    """Load a JSON manifest into a dictionary."""
    path = Path(source)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise KnowledgePackParseError(
            f"Unable to read pack manifest: {exc}",
            source=str(path),
        ) from exc

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise KnowledgePackParseError(
            f"Invalid JSON syntax: {exc}",
            source=str(path),
        ) from exc

    if not isinstance(data, dict):
        raise KnowledgePackParseError(
            "Pack manifest root must be a mapping/object",
            source=str(path),
        )
    return data


def parse_pack_manifest(data: dict[str, Any]) -> KnowledgePackManifest:
    """Validate raw manifest data against the pack schema."""
    try:
        return KnowledgePackManifest.model_validate(data)
    except ValidationError as exc:
        errors = [
            f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        ]
        raise KnowledgePackSchemaError(
            "Knowledge pack manifest failed schema validation",
            errors=errors,
        ) from exc


def load_pack_manifest(source: PathLike) -> KnowledgePackManifest:
    """Load and validate a pack manifest file."""
    path = Path(source)
    if path.suffix.lower() == ".json":
        data = load_pack_json(path)
    else:
        data = load_pack_yaml(path)
    return parse_pack_manifest(data)


def load_pack_directory(directory: PathLike) -> KnowledgePackManifest:
    """Load ``pack.yaml`` from a knowledge pack directory."""
    root = Path(directory)
    manifest_path = root / PACK_MANIFEST_FILENAME
    if not manifest_path.exists():
        raise KnowledgePackParseError(
            f"Missing {PACK_MANIFEST_FILENAME} in pack directory",
            source=str(root),
        )
    return load_pack_manifest(manifest_path)


def discover_pack_directories(root: PathLike) -> list[Path]:
    """Discover pack directories containing ``pack.yaml`` under ``root``."""
    base = Path(root)
    if not base.exists():
        return []

    discovered: list[Path] = []
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        if (child / PACK_MANIFEST_FILENAME).exists():
            discovered.append(child)
    return discovered