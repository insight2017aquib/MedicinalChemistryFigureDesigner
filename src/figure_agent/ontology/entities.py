"""Typed entity models for the scientific figure ontology."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from figure_agent.ontology.enums import EntityType


class BaseEntity(BaseModel):
    """Base model shared by all ontology entities."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(..., min_length=1, description="Unique entity identifier")
    entity_type: EntityType = Field(..., description="Entity type discriminator")
    label: str | None = Field(default=None, description="Optional display label")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="User-supplied metadata slots",
    )


class StructuralEntity(BaseEntity):
    """Base class for structural figure components."""

    pass


class GraphicalEntity(BaseEntity):
    """Base class for graphical annotation components."""

    pass


class Molecule(StructuralEntity):
    """Generic small-molecule entity placeholder."""

    entity_type: Literal[EntityType.MOLECULE] = EntityType.MOLECULE


class Macromolecule(StructuralEntity):
    """Generic macromolecule entity placeholder."""

    entity_type: Literal[EntityType.MACROMOLECULE] = EntityType.MACROMOLECULE


class Protein(Macromolecule):
    """Generic protein entity placeholder."""

    entity_type: Literal[EntityType.PROTEIN] = EntityType.PROTEIN


class NucleicAcid(Macromolecule):
    """Generic nucleic acid entity placeholder."""

    entity_type: Literal[EntityType.NUCLEIC_ACID] = EntityType.NUCLEIC_ACID


class Ligand(Molecule):
    """Generic ligand entity placeholder."""

    entity_type: Literal[EntityType.LIGAND] = EntityType.LIGAND


class Membrane(StructuralEntity):
    """Generic membrane entity placeholder."""

    entity_type: Literal[EntityType.MEMBRANE] = EntityType.MEMBRANE


class Organelle(StructuralEntity):
    """Generic organelle entity placeholder."""

    entity_type: Literal[EntityType.ORGANELLE] = EntityType.ORGANELLE


class Cell(StructuralEntity):
    """Generic cell entity placeholder."""

    entity_type: Literal[EntityType.CELL] = EntityType.CELL


class Label(GraphicalEntity):
    """Text label entity."""

    entity_type: Literal[EntityType.LABEL] = EntityType.LABEL
    text: str | None = Field(default=None, description="Label text placeholder")


class Arrow(GraphicalEntity):
    """Directional arrow entity."""

    entity_type: Literal[EntityType.ARROW] = EntityType.ARROW


class Annotation(GraphicalEntity):
    """Annotation callout entity."""

    entity_type: Literal[EntityType.ANNOTATION] = EntityType.ANNOTATION


class Shape(GraphicalEntity):
    """Generic geometric shape entity."""

    entity_type: Literal[EntityType.SHAPE] = EntityType.SHAPE
    shape_kind: str | None = Field(
        default=None,
        description="Shape category identifier (user-supplied)",
    )


class ImageAsset(GraphicalEntity):
    """External image asset reference entity."""

    entity_type: Literal[EntityType.IMAGE_ASSET] = EntityType.IMAGE_ASSET
    asset_ref: str | None = Field(
        default=None,
        description="Path or URI to an image asset",
    )


Entity = Annotated[
    Molecule
    | Macromolecule
    | Protein
    | NucleicAcid
    | Ligand
    | Membrane
    | Organelle
    | Cell
    | Label
    | Arrow
    | Annotation
    | Shape
    | ImageAsset,
    Field(discriminator="entity_type"),
]

ENTITY_MODEL_BY_TYPE: dict[EntityType, type[BaseEntity]] = {
    EntityType.MOLECULE: Molecule,
    EntityType.MACROMOLECULE: Macromolecule,
    EntityType.PROTEIN: Protein,
    EntityType.NUCLEIC_ACID: NucleicAcid,
    EntityType.LIGAND: Ligand,
    EntityType.MEMBRANE: Membrane,
    EntityType.ORGANELLE: Organelle,
    EntityType.CELL: Cell,
    EntityType.LABEL: Label,
    EntityType.ARROW: Arrow,
    EntityType.ANNOTATION: Annotation,
    EntityType.SHAPE: Shape,
    EntityType.IMAGE_ASSET: ImageAsset,
}
