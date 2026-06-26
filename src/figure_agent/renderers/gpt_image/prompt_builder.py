"""Deterministic, renderer-agnostic image prompt builder for ontology graphs."""

from __future__ import annotations

from dataclasses import dataclass

from figure_agent.ontology.entities import BaseEntity
from figure_agent.ontology.enums import EntityType, RelationshipType
from figure_agent.ontology.relationships import OntologyGraph
from figure_agent.renderers.base import RenderConfig
from figure_agent.renderers.exceptions import LayoutError
from figure_agent.renderers.gpt_image.exceptions import GPTImagePromptBuildError
from figure_agent.renderers.layout import GraphLayout, compute_layout, validate_layout

PROMPT_VERSION = "1.0"

_PRIMITIVE_BY_ENTITY_TYPE: dict[EntityType, str] = {
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


@dataclass(frozen=True)
class ImagePromptSpec:
    """Structured output from the prompt builder."""

    version: str
    prompt: str
    width: float
    height: float


def _display_label(entity: BaseEntity) -> str:
    if entity.label:
        return entity.label
    text = getattr(entity, "text", None)
    if isinstance(text, str) and text:
        return text
    return entity.id.split(":")[-1]


def _is_panel(entity: BaseEntity) -> bool:
    return ":panel:" in entity.id


def _is_figure_root(entity: BaseEntity) -> bool:
    return ":figure:" in entity.id


def _is_style_annotation(entity: BaseEntity) -> bool:
    return entity.entity_type == EntityType.ANNOTATION and ":style:" in entity.id


def _primitive_name(entity: BaseEntity) -> str:
    if _is_panel(entity):
        return "panel_boundary"
    return _PRIMITIVE_BY_ENTITY_TYPE.get(entity.entity_type, "rectangle")


def _contains_children(graph: OntologyGraph, parent_id: str) -> list[str]:
    return [
        rel.target_id
        for rel in graph.relationships
        if rel.type == RelationshipType.CONTAINS and rel.source_id == parent_id
    ]


def _entity_by_id(graph: OntologyGraph) -> dict[str, BaseEntity]:
    return {entity.id: entity for entity in graph.entities}


def _sorted_contains_children(
    graph: OntologyGraph,
    parent_id: str,
    entities: dict[str, BaseEntity],
) -> list[BaseEntity]:
    child_ids = sorted(
        cid
        for cid in _contains_children(graph, parent_id)
        if cid in entities and not _is_panel(entities[cid])
    )
    return [entities[cid] for cid in child_ids]


def _style_reference_paths(graph: OntologyGraph, entities: dict[str, BaseEntity]) -> list[str]:
    paths: list[str] = []
    for rel in graph.relationships:
        if rel.type != RelationshipType.REFERENCES:
            continue
        target = entities.get(rel.target_id)
        if target is None or not _is_style_annotation(target):
            continue
        style_ref = target.metadata.get("style_ref")
        if isinstance(style_ref, str) and style_ref:
            paths.append(style_ref)
        elif target.label:
            paths.append(target.label)
    return sorted(set(paths))


def _format_panel_section(
    panel: BaseEntity,
    children: list[BaseEntity],
    *,
    index: int,
) -> list[str]:
    panel_key = panel.id.split(":")[-1]
    lines = [f"PANEL[{index}] id={panel_key} primitive=panel_boundary"]
    for child_index, child in enumerate(children, start=1):
        child_key = child.id.split(":")[-1]
        primitive = _primitive_name(child)
        label = _display_label(child)
        lines.append(
            f"  ELEMENT[{child_index}] id={child_key} primitive={primitive} label={label!r}"
        )
    return lines


def _format_arrow_section(layout: GraphLayout) -> list[str]:
    if not layout.arrows:
        return []
    lines = ["ARROWS:"]
    for index, (source_id, target_id) in enumerate(
        sorted(layout.arrows, key=lambda pair: (pair[0], pair[1])),
        start=1,
    ):
        source_key = source_id.split(":")[-1]
        target_key = target_id.split(":")[-1]
        lines.append(
            f"  ARROW[{index}] from={source_key!r} to={target_key!r} style=straight"
        )
    return lines


class GPTImagePromptBuilder:
    """Convert ontology graphs into deterministic image-generation prompts.

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
        try:
            layout = compute_layout(graph, cfg)
            validate_layout(layout)
        except LayoutError as exc:
            raise GPTImagePromptBuildError(str(exc)) from exc

        entities = _entity_by_id(graph)
        root = layout.root
        if root is None:
            raise GPTImagePromptBuildError("Ontology graph has no layout root")

        figure_title = _display_label(root)
        layout_type = root.metadata.get("layout_type", "unknown")
        style_refs = _style_reference_paths(graph, entities)

        lines: list[str] = [
            f"PROMPT_VERSION: {PROMPT_VERSION}",
            "TASK: structural_schematic_diagram",
            f"CANVAS: width={int(layout.canvas_size.width)} height={int(layout.canvas_size.height)}",
            "STYLE: monochrome flat vector schematic; no photorealism; no icons; no gradients",
            f"FIGURE title={figure_title!r} layout_type={layout_type!r}",
            "CONSTRAINTS:",
            "  - structural layout only",
            "  - use labels exactly as given",
            "  - do not invent scientific content",
            "  - do not add biology or chemistry iconography",
        ]

        panel_entities = sorted(
            (
                panel_layout.entity
                for panel_layout in layout.panels
                if _is_panel(panel_layout.entity)
            ),
            key=lambda entity: entity.id,
        )

        if panel_entities:
            lines.append("COMPOSITION:")
            for panel_index, panel in enumerate(panel_entities, start=1):
                children = _sorted_contains_children(graph, panel.id, entities)
                lines.extend(
                    _format_panel_section(panel, children, index=panel_index)
                )
        else:
            lines.append("COMPOSITION:")
            lines.append("  ELEMENT[1] id=figure_root primitive=rectangle")

        arrow_lines = _format_arrow_section(layout)
        if arrow_lines:
            lines.extend(arrow_lines)

        if style_refs:
            lines.append("STYLE_REFERENCES:")
            for index, path in enumerate(style_refs, start=1):
                lines.append(f"  REF[{index}] path={path!r}")

        prompt = "\n".join(lines)
        return ImagePromptSpec(
            version=PROMPT_VERSION,
            prompt=prompt,
            width=layout.canvas_size.width,
            height=layout.canvas_size.height,
        )