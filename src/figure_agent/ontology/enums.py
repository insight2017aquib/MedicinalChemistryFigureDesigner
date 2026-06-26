"""Enumerations for the scientific figure ontology layer."""

from __future__ import annotations

from enum import StrEnum


class EntityType(StrEnum):
    """Supported entity type identifiers in the ontology registry."""

    MOLECULE = "molecule"
    MACROMOLECULE = "macromolecule"
    PROTEIN = "protein"
    NUCLEIC_ACID = "nucleic_acid"
    LIGAND = "ligand"
    MEMBRANE = "membrane"
    ORGANELLE = "organelle"
    CELL = "cell"
    LABEL = "label"
    ARROW = "arrow"
    ANNOTATION = "annotation"
    SHAPE = "shape"
    IMAGE_ASSET = "image_asset"


class RelationshipType(StrEnum):
    """Typed relationship identifiers between ontology entities."""

    CONTAINS = "contains"
    CONNECTED_TO = "connected_to"
    LOCATED_IN = "located_in"
    ANNOTATES = "annotates"
    REFERENCES = "references"
    INTERACTS_WITH = "interacts_with"


HIERARCHICAL_RELATIONSHIPS: frozenset[RelationshipType] = frozenset(
    {
        RelationshipType.CONTAINS,
        RelationshipType.LOCATED_IN,
    }
)
