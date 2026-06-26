"""Abstract renderer interface for ontology graphs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from figure_agent.ontology.relationships import OntologyGraph


@dataclass(frozen=True)
class RenderConfig:
    """Configuration shared by renderer implementations."""

    width: float = 800.0
    height: float = 600.0
    margin: float = 24.0
    panel_gap: float = 32.0
    item_spacing: float = 16.0
    item_width: float = 180.0
    item_height: float = 48.0
    panel_padding: float = 20.0


@dataclass(frozen=True)
class RenderResult:
    """Output produced by a renderer."""

    content: str
    width: float
    height: float
    mime_type: str


class Renderer(ABC):
    """Abstract base class for ontology graph renderers.

    Future implementations (BioRender, GPT Image, PowerPoint, Mermaid,
    Illustrator) should inherit from this interface.
    """

    @abstractmethod
    def render(
        self, graph: OntologyGraph, *, config: RenderConfig | None = None
    ) -> RenderResult:
        """Render an ontology graph.

        Args:
            graph: Compiled ontology graph.
            config: Optional render configuration.

        Returns:
            A ``RenderResult`` containing rendered output.
        """
