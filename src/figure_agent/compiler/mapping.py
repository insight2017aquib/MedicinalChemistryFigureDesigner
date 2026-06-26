"""Mapping rules from FSL constructs to ontology entities."""

from __future__ import annotations

from typing import Any

from figure_agent.compiler.context import CompilationContext
from figure_agent.fsl.models import ContentSlot, Figure, Panel, StyleReference
from figure_agent.ontology.entities import (
    Annotation,
    Arrow,
    BaseEntity,
    Cell,
    ImageAsset,
    Label,
    Shape,
)
from figure_agent.ontology.enums import EntityType, RelationshipType
from figure_agent.ontology.relationships import Relationship

DEFAULT_SLOT_ENTITY_TYPE = EntityType.SHAPE

SLOT_TYPE_TO_ENTITY_TYPE: dict[str, EntityType] = {
    "placeholder": EntityType.LABEL,
    "text": EntityType.LABEL,
    "label": EntityType.LABEL,
    "image": EntityType.IMAGE_ASSET,
    "asset": EntityType.IMAGE_ASSET,
    "structure": EntityType.SHAPE,
    "shape": EntityType.SHAPE,
    "arrow": EntityType.ARROW,
    "annotation": EntityType.ANNOTATION,
    "molecule": EntityType.MOLECULE,
    "macromolecule": EntityType.MACROMOLECULE,
    "protein": EntityType.PROTEIN,
    "nucleic_acid": EntityType.NUCLEIC_ACID,
    "ligand": EntityType.LIGAND,
    "membrane": EntityType.MEMBRANE,
    "organelle": EntityType.ORGANELLE,
    "cell": EntityType.CELL,
}


def resolve_slot_entity_type(slot: ContentSlot) -> EntityType:
    """Map a content slot type string to an ontology entity type."""
    if slot.type is None:
        return DEFAULT_SLOT_ENTITY_TYPE
    normalized = slot.type.strip().lower()
    return SLOT_TYPE_TO_ENTITY_TYPE.get(normalized, DEFAULT_SLOT_ENTITY_TYPE)


def map_figure_root(figure: Figure, context: CompilationContext) -> Cell:
    """Create the root ontology container for an FSL figure."""
    entity_id = context.make_entity_id("figure", figure.metadata.id)
    context.register_mapping("figure", figure.metadata.id, entity_id)

    return Cell(
        id=entity_id,
        label=figure.metadata.title,
        metadata={
            "fsl_version": figure.fsl_version,
            "layout_type": figure.layout.type,
            "template_ref": figure.template.ref,
            "template_params": figure.template.params,
            "author": figure.metadata.author,
            "export_formats": figure.export.formats,
            "export_naming": figure.export.naming,
        },
    )


def map_panel(panel: Panel, figure: Figure, context: CompilationContext) -> Cell:
    """Create an ontology panel container from an FSL panel."""
    entity_id = context.make_entity_id("panel", panel.id)
    context.register_mapping("panel", panel.id, entity_id)
    context.record_panel(panel)

    return Cell(
        id=entity_id,
        label=panel.id,
        metadata={
            "layout_type": figure.layout.type,
            "zones": panel.zones,
            "object_refs": panel.object_refs,
        },
    )


def map_content_slot(slot: ContentSlot, context: CompilationContext) -> BaseEntity:
    """Create an ontology entity from an FSL content slot."""
    entity_id = context.make_entity_id("slot", slot.id)
    context.register_mapping("slot", slot.id, entity_id)
    context.record_slot(slot)

    entity_type = resolve_slot_entity_type(slot)
    metadata: dict[str, Any] = {
        "fsl_slot_type": slot.type,
        "value": slot.value,
    }

    if entity_type == EntityType.LABEL:
        return Label(id=entity_id, label=slot.label, text=slot.label, metadata=metadata)
    if entity_type == EntityType.IMAGE_ASSET:
        asset_ref = slot.value if isinstance(slot.value, str) else None
        return ImageAsset(
            id=entity_id,
            label=slot.label,
            asset_ref=asset_ref,
            metadata=metadata,
        )
    if entity_type == EntityType.ARROW:
        return Arrow(id=entity_id, label=slot.label, metadata=metadata)
    if entity_type == EntityType.ANNOTATION:
        return Annotation(id=entity_id, label=slot.label, metadata=metadata)
    if entity_type == EntityType.SHAPE:
        return Shape(
            id=entity_id,
            label=slot.label,
            shape_kind=slot.type,
            metadata=metadata,
        )

    from figure_agent.ontology.registry import create_entity

    return create_entity(entity_type, entity_id, label=slot.label, metadata=metadata)


def map_style_reference(
    style_ref: StyleReference,
    index: int,
    context: CompilationContext,
) -> Annotation:
    """Create an ontology annotation entity for a style reference."""
    fsl_id = f"style-{index}"
    entity_id = context.make_entity_id("style", fsl_id)
    context.register_mapping("style", fsl_id, entity_id)

    return Annotation(
        id=entity_id,
        label=style_ref.ref,
        metadata={
            "style_ref": style_ref.ref,
            "kind": "style_reference",
        },
    )


def build_panel_contains_relationship(
    panel_entity_id: str,
    slot_entity_id: str,
    *,
    relationship_id: str,
) -> Relationship:
    """Create a contains relationship from panel to slot."""
    return Relationship(
        id=relationship_id,
        type=RelationshipType.CONTAINS,
        source_id=panel_entity_id,
        target_id=slot_entity_id,
    )


def build_figure_contains_panel_relationship(
    figure_entity_id: str,
    panel_entity_id: str,
    *,
    relationship_id: str,
) -> Relationship:
    """Create a contains relationship from figure root to panel."""
    return Relationship(
        id=relationship_id,
        type=RelationshipType.CONTAINS,
        source_id=figure_entity_id,
        target_id=panel_entity_id,
    )


def build_style_reference_relationship(
    figure_entity_id: str,
    style_entity_id: str,
    *,
    relationship_id: str,
) -> Relationship:
    """Create a references relationship from figure root to style annotation."""
    return Relationship(
        id=relationship_id,
        type=RelationshipType.REFERENCES,
        source_id=figure_entity_id,
        target_id=style_entity_id,
    )
