"""Exception hierarchy for GPT Image prompt generation."""

from __future__ import annotations

from figure_agent.renderers.exceptions import GPTImagePromptError


class GPTImagePromptBuildError(GPTImagePromptError):
    """Raised when an ontology graph cannot be converted to a prompt."""