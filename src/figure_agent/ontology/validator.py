"""Structural validation for ontology graphs."""

from __future__ import annotations

from figure_agent.ontology.entities import BaseEntity
from figure_agent.ontology.enums import HIERARCHICAL_RELATIONSHIPS, RelationshipType
from figure_agent.ontology.exceptions import OntologyValidationError
from figure_agent.ontology.registry import EntityRegistry
from figure_agent.ontology.relationships import OntologyGraph, Relationship


class OntologyValidator:
    """Validate structural integrity of an ontology graph.

    Performs reference and relationship checks only. Does not validate
    scientific content.
    """

    def __init__(
        self,
        *,
        known_relationship_types: set[RelationshipType] | None = None,
    ) -> None:
        self._known_relationship_types = known_relationship_types or set(
            RelationshipType
        )

    def validate(self, graph: OntologyGraph) -> None:
        """Validate an ontology graph.

        Args:
            graph: Ontology graph to validate.

        Raises:
            OntologyValidationError: If one or more checks fail.
        """
        entity_ids = self._entity_id_set(graph)
        errors: list[str] = []
        errors.extend(self._check_duplicate_entity_ids(graph))
        errors.extend(self._check_duplicate_relationship_ids(graph.relationships))
        errors.extend(self._check_relationship_types(graph.relationships))
        errors.extend(self._check_missing_references(graph.relationships, entity_ids))
        errors.extend(
            self._check_cyclic_hierarchical_relationships(graph.relationships)
        )

        if errors:
            raise OntologyValidationError("Ontology validation failed", errors=errors)

    def validate_registry(self, registry: EntityRegistry) -> None:
        """Validate the graph currently stored in a registry."""
        self.validate(registry.build_graph())

    def _entity_id_set(self, graph: OntologyGraph) -> set[str]:
        ids: set[str] = set()
        for entity in graph.entities:
            if isinstance(entity, BaseEntity):
                ids.add(entity.id)
            elif isinstance(entity, dict) and isinstance(entity.get("id"), str):
                ids.add(entity["id"])
        return ids

    def _check_duplicate_entity_ids(self, graph: OntologyGraph) -> list[str]:
        seen: set[str] = set()
        errors: list[str] = []
        for entity in graph.entities:
            if isinstance(entity, BaseEntity):
                entity_id = entity.id
            elif isinstance(entity, dict):
                entity_id = entity.get("id")
            else:
                errors.append("entity entry has unsupported type")
                continue

            if not isinstance(entity_id, str):
                errors.append("entity is missing a valid string id")
                continue
            if entity_id in seen:
                errors.append(f"duplicate entity id '{entity_id}'")
            seen.add(entity_id)
        return errors

    def _check_duplicate_relationship_ids(
        self,
        relationships: list[Relationship],
    ) -> list[str]:
        seen: set[str] = set()
        errors: list[str] = []
        for relationship in relationships:
            if relationship.id in seen:
                errors.append(f"duplicate relationship id '{relationship.id}'")
            seen.add(relationship.id)
        return errors

    def _check_relationship_types(self, relationships: list[Relationship]) -> list[str]:
        errors: list[str] = []
        for relationship in relationships:
            if relationship.type not in self._known_relationship_types:
                known = ", ".join(
                    sorted(item.value for item in self._known_relationship_types)
                )
                errors.append(
                    f"relationship '{relationship.id}' has invalid type "
                    f"'{relationship.type}'; expected one of: {known}"
                )
        return errors

    def _check_missing_references(
        self,
        relationships: list[Relationship],
        entity_ids: set[str],
    ) -> list[str]:
        errors: list[str] = []
        for relationship in relationships:
            if relationship.source_id not in entity_ids:
                errors.append(
                    f"relationship '{relationship.id}' references unknown source "
                    f"entity '{relationship.source_id}'"
                )
            if relationship.target_id not in entity_ids:
                errors.append(
                    f"relationship '{relationship.id}' references unknown target "
                    f"entity '{relationship.target_id}'"
                )
        return errors

    def _check_cyclic_hierarchical_relationships(
        self,
        relationships: list[Relationship],
    ) -> list[str]:
        """Detect cycles in hierarchical relationship types."""
        parent_edges: dict[str, set[str]] = {}

        for relationship in relationships:
            if relationship.type not in HIERARCHICAL_RELATIONSHIPS:
                continue
            parent_edges.setdefault(relationship.target_id, set()).add(
                relationship.source_id
            )

        visited: set[str] = set()
        stack: set[str] = set()
        errors: list[str] = []

        def visit(node: str) -> None:
            if node in stack:
                errors.append(
                    f"cyclic parent relationship detected involving entity '{node}'"
                )
                return
            if node in visited:
                return
            stack.add(node)
            for parent in parent_edges.get(node, set()):
                visit(parent)
            stack.remove(node)
            visited.add(node)

        for node in parent_edges:
            visit(node)

        return errors
