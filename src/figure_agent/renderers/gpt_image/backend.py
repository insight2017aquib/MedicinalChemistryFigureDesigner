"""Pluggable image generation backends for GPT Image rendering."""

from __future__ import annotations

import base64
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ImageGenerationRequest:
    """Input passed to an image generation backend."""

    prompt: str
    width: int
    height: int
    model: str = "gpt-image-1"


@dataclass(frozen=True)
class ImageGenerationResult:
    """Output from a successful image generation call."""

    image_bytes: bytes
    mime_type: str
    model: str
    revised_prompt: str | None = None
    raw_response: dict[str, Any] | None = None


class ImageGenerationBackend(ABC):
    """Abstract backend for raster image generation APIs."""

    @abstractmethod
    def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """Generate an image from a text prompt."""


# Minimal 1x1 transparent PNG for stub backends and tests.
MINIMAL_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


class StubImageBackend(ImageGenerationBackend):
    """Deterministic in-memory backend for tests and offline development."""

    def __init__(
        self,
        *,
        image_bytes: bytes | None = None,
        mime_type: str = "image/png",
        model: str = "stub-gpt-image",
        revised_prompt: str | None = None,
        fail_until_attempt: int = 0,
        failure_message: str = "transient backend failure",
    ) -> None:
        self._image_bytes = image_bytes or MINIMAL_PNG_BYTES
        self._mime_type = mime_type
        self._model = model
        self._revised_prompt = revised_prompt
        self._fail_until_attempt = fail_until_attempt
        self._failure_message = failure_message
        self.attempts = 0
        self.requests: list[ImageGenerationRequest] = []

    def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        self.attempts += 1
        self.requests.append(request)
        if self.attempts <= self._fail_until_attempt:
            raise RuntimeError(self._failure_message)
        return ImageGenerationResult(
            image_bytes=self._image_bytes,
            mime_type=self._mime_type,
            model=self._model,
            revised_prompt=self._revised_prompt or request.prompt,
            raw_response={"backend": "stub", "attempt": self.attempts},
        )