"""Deterministic, renderer-agnostic image prompt builder for visual scenes."""

from __future__ import annotations

from dataclasses import dataclass

from figure_agent.ontology.enums import EntityType
from figure_agent.ontology.relationships import OntologyGraph
from figure_agent.renderers.base import RenderConfig
from figure_agent.renderers.gpt_image.exceptions import GPTImagePromptBuildError
from figure_agent.renderers.scene.builder import build_visual_scene
from figure_agent.renderers.scene.exceptions import SceneBuildError
from figure_agent.renderers.scene.models import VisualPanel, VisualPrimitive, VisualScene

PROMPT_VERSION = "1.0"

_PROMPT_PRIMITIVE_BY_ENTITY_TYPE: dict[EntityType, str] = {
    EntityType.LABEL: "text_label",
    EntityType.ARROW: "straight_arrow",
    EntityType.ANNOTATION: "rounded_rectangle",
    EntityType.SHAPE: "rectangle",
    EntityType.IMAGE_ASSET: "image_placeholder",
    EntityType.CELL: "panel_boundary",
    EntityType.MOLECULE: "rectangle",
    EntityType.MACROMOLECULE: "rectangle",
    EntityType.PROTEIN: "rectangle",
    EntityType.NUCLEIC_ACID: "rectangle",
    EntityType.LIGAND: "rectangle",
    EntityType.MEMBRANE: "rectangle",
    EntityType.ORGANELLE: "rectangle",
}


def _prompt_primitive(primitive: VisualPrimitive) -> str:
    if ":panel:" in primitive.id:
        return "panel_boundary"
    if primitive.entity_type is not None:
        return _PROMPT_PRIMITIVE_BY_ENTITY_TYPE.get(
            primitive.entity_type,
            "rectangle",
        )
    return "rectangle"


@dataclass(frozen=True)
class ImagePromptSpec:
    """Structured output from the prompt builder."""

    version: str
    prompt: str
    width: float
    height: float


def _short_id(entity_id: str) -> str:
    return entity_id.split(":")[-1]


def _is_panel(panel: VisualPanel) -> bool:
    return ":panel:" in panel.id


def _panel_children(scene: VisualScene, panel: VisualPanel) -> list[str]:
    primitive_by_id = scene.primitive_by_id()
    child_ids = [member_id for member_id in panel.primitive_ids if member_id != panel.id]
    return sorted(child_ids, key=_short_id)


def _format_panel_section(
    scene: VisualScene,
    panel: VisualPanel,
    *,
    index: int,
) -> list[str]:
    primitive_by_id = scene.primitive_by_id()
    panel_key = _short_id(panel.id)
    lines = [f"PANEL[{index}] id={panel_key} primitive=panel_boundary"]
    for child_index, child_id in enumerate(_panel_children(scene, panel), start=1):
        primitive = primitive_by_id[child_id]
        child_key = _short_id(child_id)
        prompt_primitive = _prompt_primitive(primitive)
        label = primitive.label.text if primitive.label is not None else child_key
        lines.append(
            f"  ELEMENT[{child_index}] id={child_key} primitive={prompt_primitive} label={label!r}"
        )
    return lines


def _format_arrow_section(scene: VisualScene) -> list[str]:
    if not scene.connectors:
        return []
    lines = ["ARROWS:"]
    sorted_connectors = sorted(
        scene.connectors,
        key=lambda connector: (connector.source_id, connector.target_id),
    )
    for index, connector in enumerate(sorted_connectors, start=1):
        source_key = _short_id(connector.source_id)
        target_key = _short_id(connector.target_id)
        lines.append(
            f"  ARROW[{index}] from={source_key!r} to={target_key!r} style=straight"
        )
    return lines


class GPTImagePromptBuilder:
    """Convert visual scenes into deterministic image-generation prompts.

    Output is renderer-agnostic plain text describing structural primitives only.
    No biological semantics, scientific knowledge, or vendor-specific syntax.
    """

    def build(
        self,
        graph: OntologyGraph,
        *,
        config: RenderConfig | None = None,
    ) -> ImagePromptSpec:
        """Build a deterministic prompt from an ontology graph.

        Args:
            graph: Compiled ontology graph.
            config: Optional layout configuration (canvas dimensions).

        Returns:
            ``ImagePromptSpec`` with prompt text and canvas size.

        Raises:
            GPTImagePromptBuildError: If layout validation fails.
        """
        cfg = config or RenderConfig()
        if not graph.entities:
            raise GPTImagePromptBuildError("Cannot layout an empty ontology graph")

        try:
            scene = build_visual_scene(graph, config=cfg)
        except SceneBuildError as exc:
            raise GPTImagePromptBuildError(str(exc)) from exc

        return self.build_from_scene(scene)

    def build_from_scene(self, scene: VisualScene) -> ImagePromptSpec:
        """Build a deterministic prompt from a visual scene."""
        lines: list[str] = [
            f"PROMPT_VERSION: {PROMPT_VERSION}",
            "TASK: structural_schematic_diagram",
            f"CANVAS: width={int(scene.canvas_width)} height={int(scene.canvas_height)}",
            "STYLE: monochrome flat vector schematic; no photorealism; no icons; no gradients",
            f"FIGURE title={scene.title!r} layout_type={scene.layout_type!r}",
            "CONSTRAINTS:",
            "  - structural layout only",
            "  - use labels exactly as given",
            "  - do not invent scientific content",
            "  - do not add biology or chemistry iconography",
        ]

        panel_entities = sorted(
            (panel for panel in scene.panels if _is_panel(panel)),
            key=lambda panel: panel.id,
        )

        lines.append("COMPOSITION:")
        if panel_entities:
            for panel_index, panel in enumerate(panel_entities, start=1):
                lines.extend(_format_panel_section(scene, panel, index=panel_index))
        else:
            lines.append("  ELEMENT[1] id=figure_root primitive=rectangle")

        arrow_lines = _format_arrow_section(scene)
        if arrow_lines:
            lines.extend(arrow_lines)

        if scene.style_references:
            lines.append("STYLE_REFERENCES:")
            for index, style_ref in enumerate(scene.style_references, start=1):
                lines.append(f"  REF[{index}] path={style_ref.path!r}")

        prompt = "\n".join(lines)
        return ImagePromptSpec(
            version=PROMPT_VERSION,
            prompt=prompt,
            width=scene.canvas_width,
            height=scene.canvas_height,
        )