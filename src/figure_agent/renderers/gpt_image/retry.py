"""Retry helpers for transient image generation failures."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

from figure_agent.renderers.gpt_image.exceptions import GPTImageRetryExhaustedError

T = TypeVar("T")


def call_with_retries(
    operation: Callable[[], T],
    *,
    max_attempts: int = 3,
    initial_backoff_seconds: float = 0.5,
    max_backoff_seconds: float = 8.0,
    is_retryable: Callable[[BaseException], bool] | None = None,
) -> T:
    """Execute ``operation`` with exponential backoff on retryable errors."""
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    retryable = is_retryable or _default_retryable
    last_error: BaseException | None = None
    backoff = initial_backoff_seconds

    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except BaseException as exc:
            if not retryable(exc) or attempt >= max_attempts:
                if attempt >= max_attempts and retryable(exc):
                    raise GPTImageRetryExhaustedError(
                        f"Image generation failed after {max_attempts} attempts: {exc}"
                    ) from exc
                raise
            last_error = exc
            time.sleep(min(backoff, max_backoff_seconds))
            backoff *= 2

    raise GPTImageRetryExhaustedError(
        f"Image generation failed after {max_attempts} attempts: {last_error}"
    )


def _default_retryable(exc: BaseException) -> bool:
    from figure_agent.renderers.gpt_image.exceptions import GPTImageAPIError

    if isinstance(exc, GPTImageAPIError):
        return exc.retryable
    return isinstance(
        exc,
        (
            TimeoutError,
            ConnectionError,
            OSError,
            RuntimeError,
        ),
    )