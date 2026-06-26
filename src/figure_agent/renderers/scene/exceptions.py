"""Exceptions for visual scene construction."""

from __future__ import annotations

from figure_agent.renderers.exceptions import RenderError


class SceneBuildError(RenderError):
    """Raised when an ontology graph cannot be converted to a visual scene."""

    def __init__(self, message: str) -> None:
        super().__init__(message)