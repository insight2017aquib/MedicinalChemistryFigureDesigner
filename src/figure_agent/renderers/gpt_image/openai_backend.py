"""OpenAI GPT Image API backend."""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from typing import Any

from figure_agent.renderers.gpt_image.backend import (
    ImageGenerationBackend,
    ImageGenerationRequest,
    ImageGenerationResult,
)
from figure_agent.renderers.gpt_image.exceptions import GPTImageAPIError

OPENAI_IMAGES_URL = "https://api.openai.com/v1/images/generations"
DEFAULT_OPENAI_MODEL = "gpt-image-1"


def resolve_openai_image_size(width: int, height: int) -> str:
    """Map scene dimensions to a supported OpenAI image size token."""
    if width > height * 1.2:
        return "1536x1024"
    if height > width * 1.2:
        return "1024x1536"
    return "1024x1024"


class OpenAIImageBackend(ImageGenerationBackend):
    """Generate images through the OpenAI Images API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = DEFAULT_OPENAI_MODEL,
        timeout_seconds: float = 120.0,
    ) -> None:
        resolved_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not resolved_key:
            raise GPTImageAPIError(
                "OpenAI API key is required. Set OPENAI_API_KEY or pass api_key.",
                retryable=False,
            )
        self._api_key = resolved_key
        self._model = model
        self._timeout_seconds = timeout_seconds

    def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        payload = {
            "model": request.model or self._model,
            "prompt": request.prompt,
            "size": resolve_openai_image_size(request.width, request.height),
        }
        body = json.dumps(payload).encode("utf-8")
        http_request = urllib.request.Request(
            OPENAI_IMAGES_URL,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(
                http_request,
                timeout=self._timeout_seconds,
            ) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise _http_error_to_api_error(exc) from exc
        except urllib.error.URLError as exc:
            raise GPTImageAPIError(
                f"OpenAI image request failed: {exc.reason}",
                retryable=True,
                status_code=None,
            ) from exc
        except TimeoutError as exc:
            raise GPTImageAPIError(
                "OpenAI image request timed out",
                retryable=True,
            ) from exc

        return _parse_openai_response(raw, model=payload["model"])


def _http_error_to_api_error(exc: urllib.error.HTTPError) -> GPTImageAPIError:
    body = exc.read().decode("utf-8", errors="replace")
    message = body or exc.reason
    retryable = exc.code in {408, 409, 429, 500, 502, 503, 504}
    return GPTImageAPIError(
        f"OpenAI image API returned HTTP {exc.code}: {message}",
        retryable=retryable,
        status_code=exc.code,
    )


def _parse_openai_response(
    raw: dict[str, Any],
    *,
    model: str,
) -> ImageGenerationResult:
    data = raw.get("data")
    if not isinstance(data, list) or not data:
        raise GPTImageAPIError(
            "OpenAI image API response did not include image data",
            retryable=False,
        )

    first = data[0]
    if not isinstance(first, dict):
        raise GPTImageAPIError(
            "OpenAI image API response entry has unexpected shape",
            retryable=False,
        )

    revised_prompt = first.get("revised_prompt")
    if isinstance(first.get("b64_json"), str):
        image_bytes = base64.b64decode(first["b64_json"])
        return ImageGenerationResult(
            image_bytes=image_bytes,
            mime_type="image/png",
            model=model,
            revised_prompt=revised_prompt if isinstance(revised_prompt, str) else None,
            raw_response=raw,
        )

    if isinstance(first.get("url"), str):
        return _download_image_url(
            first["url"],
            model=model,
            revised_prompt=revised_prompt if isinstance(revised_prompt, str) else None,
            raw_response=raw,
        )

    raise GPTImageAPIError(
        "OpenAI image API response did not include b64_json or url",
        retryable=False,
    )


def _download_image_url(
    url: str,
    *,
    model: str,
    revised_prompt: str | None,
    raw_response: dict[str, Any],
) -> ImageGenerationResult:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=120.0) as response:
            image_bytes = response.read()
            mime_type = response.headers.get_content_type() or "image/png"
    except urllib.error.URLError as exc:
        raise GPTImageAPIError(
            f"Failed to download generated image: {exc.reason}",
            retryable=True,
        ) from exc

    return ImageGenerationResult(
        image_bytes=image_bytes,
        mime_type=mime_type,
        model=model,
        revised_prompt=revised_prompt,
        raw_response=raw_response,
    )