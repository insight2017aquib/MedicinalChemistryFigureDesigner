"""Relationship models connecting ontology entities."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from figure_agent.ontology.entities import Entity
from figure_agent.ontology.enums import RelationshipType


class Relationship(BaseModel):
    """A typed directed relationship between two ontology entities."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(..., min_length=1, description="Unique relationship identifier")
    type: RelationshipType = Field(..., description="Relationship type discriminator")
    source_id: str = Field(
        ...,
        min_length=1,
        description="Identifier of the source entity",
    )
    target_id: str = Field(
        ...,
        min_length=1,
        description="Identifier of the target entity",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="User-supplied relationship metadata",
    )


class OntologyGraph(BaseModel):
    """Container for entities and their relationships."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    ontology_version: str = Field(
        default="0.4.0",
        min_length=1,
        description="Ontology schema version",
    )
    entities: list[Entity] = Field(
        default_factory=list,
        description="Collection of typed ontology entities",
    )
    relationships: list[Relationship] = Field(
        default_factory=list,
        description="Collection of entity relationships",
    )

    @field_validator("entities", mode="before")
    @classmethod
    def _coerce_entities(cls, value: Any) -> list[Any]:
        if value is None:
            return []
        return value
