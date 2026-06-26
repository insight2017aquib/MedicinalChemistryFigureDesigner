"""Entity type registry and ontology graph management."""

from __future__ import annotations

import json
from typing import Any

import yaml
from pydantic import TypeAdapter

from figure_agent.ontology.entities import ENTITY_MODEL_BY_TYPE, BaseEntity, Entity
from figure_agent.ontology.enums import EntityType
from figure_agent.ontology.exceptions import (
    OntologyRegistryError,
    OntologySerializationError,
)
from figure_agent.ontology.relationships import OntologyGraph, Relationship

_ENTITY_ADAPTER: TypeAdapter[Entity] = TypeAdapter(Entity)


class EntityRegistry:
    """Register entity types, store instances, and resolve entity definitions."""

    def __init__(self) -> None:
        self._entity_types: dict[EntityType, type[BaseEntity]] = dict(
            ENTITY_MODEL_BY_TYPE
        )
        self._entities: dict[str, BaseEntity] = {}
        self._relationships: dict[str, Relationship] = {}

    def register_entity_type(
        self,
        entity_type: EntityType,
        model_class: type[BaseEntity],
    ) -> None:
        """Register or override an entity type definition.

        Args:
            entity_type: Entity type identifier.
            model_class: Pydantic model class for the entity type.

        Raises:
            OntologyRegistryError: If the model class is not a ``BaseEntity`` subclass.
        """
        if not issubclass(model_class, BaseEntity):
            raise OntologyRegistryError(
                f"Entity model '{model_class.__name__}' must subclass BaseEntity"
            )
        self._entity_types[entity_type] = model_class

    def get_entity_type(self, entity_type: EntityType) -> type[BaseEntity]:
        """Retrieve the model class for an entity type.

        Args:
            entity_type: Entity type identifier.

        Returns:
            Registered Pydantic model class.

        Raises:
            OntologyRegistryError: If the entity type is not registered.
        """
        try:
            return self._entity_types[entity_type]
        except KeyError as exc:
            raise OntologyRegistryError(f"Unknown entity type '{entity_type}'") from exc

    def list_entity_types(self) -> list[EntityType]:
        """Return all registered entity type identifiers."""
        return sorted(self._entity_types, key=lambda item: item.value)

    def add_entity(self, entity: BaseEntity) -> None:
        """Add an entity instance to the registry.

        Args:
            entity: Typed entity instance.

        Raises:
            OntologyRegistryError: If the entity type is unknown or ID already exists.
        """
        if entity.entity_type not in self._entity_types:
            raise OntologyRegistryError(
                f"Cannot add entity with unknown type '{entity.entity_type}'"
            )
        if entity.id in self._entities:
            raise OntologyRegistryError(
                f"Entity id '{entity.id}' is already registered"
            )
        self._entities[entity.id] = entity

    def get_entity(self, entity_id: str) -> BaseEntity:
        """Retrieve an entity instance by identifier.

        Args:
            entity_id: Entity identifier.

        Returns:
            Registered entity instance.

        Raises:
            OntologyRegistryError: If the entity is not found.
        """
        try:
            return self._entities[entity_id]
        except KeyError as exc:
            raise OntologyRegistryError(f"Unknown entity id '{entity_id}'") from exc

    def has_entity(self, entity_id: str) -> bool:
        """Return whether an entity identifier is registered."""
        return entity_id in self._entities

    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship to the registry.

        Args:
            relationship: Typed relationship instance.

        Raises:
            OntologyRegistryError: If the relationship ID already exists.
        """
        if relationship.id in self._relationships:
            raise OntologyRegistryError(
                f"Relationship id '{relationship.id}' is already registered"
            )
        self._relationships[relationship.id] = relationship

    def get_relationship(self, relationship_id: str) -> Relationship:
        """Retrieve a relationship by identifier."""
        try:
            return self._relationships[relationship_id]
        except KeyError as exc:
            raise OntologyRegistryError(
                f"Unknown relationship id '{relationship_id}'"
            ) from exc

    def build_graph(self, *, ontology_version: str = "0.4.0") -> OntologyGraph:
        """Build an ``OntologyGraph`` from registered entities and relationships."""
        return OntologyGraph(
            ontology_version=ontology_version,
            entities=list(self._entities.values()),
            relationships=list(self._relationships.values()),
        )

    def load_graph(self, graph: OntologyGraph) -> None:
        """Populate the registry from an ontology graph."""
        self._entities.clear()
        self._relationships.clear()
        for raw_entity in graph.entities:
            entity = (
                raw_entity
                if isinstance(raw_entity, BaseEntity)
                else _ENTITY_ADAPTER.validate_python(raw_entity)
            )
            self.add_entity(entity)
        for relationship in graph.relationships:
            self.add_relationship(relationship)

    def validate_entity_reference(self, entity_id: str) -> None:
        """Validate that an entity reference exists in the registry.

        Args:
            entity_id: Entity identifier to resolve.

        Raises:
            OntologyRegistryError: If the entity is not registered.
        """
        if entity_id not in self._entities:
            raise OntologyRegistryError(f"Invalid entity reference '{entity_id}'")


def create_entity(entity_type: EntityType, entity_id: str, **kwargs: Any) -> BaseEntity:
    """Factory helper for creating a typed entity instance.

    Args:
        entity_type: Entity type identifier.
        entity_id: Unique entity identifier.
        **kwargs: Additional fields passed to the entity model.

    Returns:
        Instantiated entity model.
    """
    model_class = ENTITY_MODEL_BY_TYPE[entity_type]
    return model_class(id=entity_id, **kwargs)


def graph_to_dict(graph: OntologyGraph) -> dict[str, Any]:
    """Serialize an ontology graph to a plain dictionary."""
    return graph.model_dump(mode="json")


def graph_to_json(graph: OntologyGraph, *, indent: int = 2) -> str:
    """Serialize an ontology graph to a JSON string."""
    return json.dumps(graph_to_dict(graph), indent=indent, sort_keys=False)


def graph_to_yaml(graph: OntologyGraph) -> str:
    """Serialize an ontology graph to a YAML string."""
    return yaml.safe_dump(
        graph_to_dict(graph),
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )


def graph_from_dict(data: dict[str, Any]) -> OntologyGraph:
    """Deserialize an ontology graph from a dictionary.

    Args:
        data: Parsed ontology document.

    Returns:
        Validated ``OntologyGraph`` instance.

    Raises:
        OntologySerializationError: If deserialization fails.
    """
    try:
        entities = [
            _ENTITY_ADAPTER.validate_python(item) for item in data.get("entities", [])
        ]
        graph = OntologyGraph(
            ontology_version=data.get("ontology_version", "0.4.0"),
            entities=entities,
            relationships=data.get("relationships", []),
        )
        return graph
    except Exception as exc:
        raise OntologySerializationError(
            f"Failed to deserialize ontology graph: {exc}"
        ) from exc
