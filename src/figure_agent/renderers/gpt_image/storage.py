"""Persist GPT Image render outputs and metadata."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from figure_agent.renderers.gpt_image.exceptions import GPTImageStorageError

_IMAGE_EXTENSIONS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}


def resolve_image_extension(mime_type: str) -> str:
    """Return a file extension for a supported image mime type."""
    return _IMAGE_EXTENSIONS.get(mime_type, ".png")


def save_render_artifacts(
    output_dir: Path,
    *,
    stem: str,
    image_bytes: bytes,
    mime_type: str,
    metadata: dict[str, Any],
) -> tuple[Path, Path]:
    """Write image bytes and sidecar metadata JSON to ``output_dir``.

    Returns:
        Tuple of ``(image_path, metadata_path)``.
    """
    if not stem.strip():
        raise GPTImageStorageError("Output filename stem must not be empty")

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        image_path = output_dir / f"{stem}{resolve_image_extension(mime_type)}"
        metadata_path = output_dir / f"{stem}.metadata.json"
        image_path.write_bytes(image_bytes)
        metadata_with_paths = {
            **metadata,
            "image_path": str(image_path),
            "metadata_path": str(metadata_path),
        }
        metadata_path.write_text(
            json.dumps(metadata_with_paths, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    except OSError as exc:
        raise GPTImageStorageError(f"Failed to save render artifacts: {exc}") from exc

    return image_path, metadata_path


def build_metadata_payload(
    *,
    figure_id: str,
    prompt: str,
    prompt_version: str,
    width: float,
    height: float,
    mime_type: str,
    model: str,
    backend: str,
    revised_prompt: str | None = None,
    image_path: str | None = None,
    attempts: int = 1,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a JSON-serializable metadata document for a render."""
    payload: dict[str, Any] = {
        "figure_id": figure_id,
        "prompt_version": prompt_version,
        "prompt": prompt,
        "revised_prompt": revised_prompt,
        "width": width,
        "height": height,
        "mime_type": mime_type,
        "model": model,
        "backend": backend,
        "attempts": attempts,
        "rendered_at": datetime.now(UTC).isoformat(),
    }
    if image_path is not None:
        payload["image_path"] = image_path
    if extra:
        payload.update(_json_safe(extra))
    return payload


def _json_safe(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value