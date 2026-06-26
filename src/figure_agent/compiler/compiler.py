"""Compile FSL figure specifications into ontology graphs."""

from __future__ import annotations

from figure_agent.compiler.context import CompilationContext
from figure_agent.compiler.exceptions import CompilationMappingError
from figure_agent.compiler.mapping import (
    build_figure_contains_panel_relationship,
    build_panel_contains_relationship,
    build_style_reference_relationship,
    map_content_slot,
    map_figure_root,
    map_panel,
    map_style_reference,
)
from figure_agent.compiler.validator import CompilerValidator
from figure_agent.fsl.models import Figure
from figure_agent.ontology.entities import BaseEntity
from figure_agent.ontology.relationships import OntologyGraph, Relationship


class FigureCompiler:
    """Transform a validated FSL ``Figure`` into an ``OntologyGraph``.

    The compiler instantiates ontology entities, assigns namespaced identifiers,
    constructs relationships, and validates the resulting graph. It does not
    perform rendering or scientific validation.
    """

    def __init__(self, *, validate_output: bool = True) -> None:
        self._validate_output = validate_output
        self._compiler_validator = CompilerValidator()

    def compile(self, figure: Figure) -> OntologyGraph:
        """Compile an FSL figure into an ontology graph.

        Args:
            figure: Parsed and validated FSL figure specification.

        Returns:
            Compiled ``OntologyGraph``.

        Raises:
            CompilationMappingError: If entity instantiation fails.
            CompilationValidationError: If mapping or graph validation fails.
        """
        context = CompilationContext(figure=figure)
        entities: list[BaseEntity] = []
        relationships: list[Relationship] = []

        try:
            root = map_figure_root(figure, context)
            entities.append(root)

            slot_entities = self._compile_content_slots(figure, context)
            entities.extend(slot_entities)

            panel_entities, panel_relationships = self._compile_panels(
                figure, context, root.id
            )
            entities.extend(panel_entities)
            relationships.extend(panel_relationships)

            style_entities, style_relationships = self._compile_style_references(
                figure, context, root.id
            )
            entities.extend(style_entities)
            relationships.extend(style_relationships)

            self._compiler_validator.validate_context(context)

            graph = OntologyGraph(
                ontology_version="0.4.0",
                entities=entities,
                relationships=relationships,
            )

            if self._validate_output:
                self._compiler_validator.validate_graph(graph)

            return graph
        except Exception as exc:
            if exc.__class__.__module__.startswith("figure_agent.compiler"):
                raise
            raise CompilationMappingError(
                f"Failed to compile figure '{figure.metadata.id}': {exc}"
            ) from exc

    def _compile_content_slots(
        self,
        figure: Figure,
        context: CompilationContext,
    ) -> list[BaseEntity]:
        return [map_content_slot(slot, context) for slot in figure.content_slots]

    def _compile_panels(
        self,
        figure: Figure,
        context: CompilationContext,
        root_entity_id: str,
    ) -> tuple[list[BaseEntity], list[Relationship]]:
        panel_entities: list[BaseEntity] = []
        relationships: list[Relationship] = []

        for panel in figure.layout.panels:
            panel_entity = map_panel(panel, figure, context)
            panel_entities.append(panel_entity)

            relationships.append(
                build_figure_contains_panel_relationship(
                    root_entity_id,
                    panel_entity.id,
                    relationship_id=context.make_entity_id(
                        "rel", f"figure-contains-{panel.id}"
                    ),
                )
            )

            for slot_ref in panel.object_refs:
                slot_entity_id = context.get_entity_id("slot", slot_ref)
                if slot_entity_id is None:
                    continue
                context.record_slot_reference(slot_ref)
                relationships.append(
                    build_panel_contains_relationship(
                        panel_entity.id,
                        slot_entity_id,
                        relationship_id=context.make_entity_id(
                            "rel", f"panel-contains-{panel.id}-{slot_ref}"
                        ),
                    )
                )

        return panel_entities, relationships

    def _compile_style_references(
        self,
        figure: Figure,
        context: CompilationContext,
        root_entity_id: str,
    ) -> tuple[list[BaseEntity], list[Relationship]]:
        style_entities: list[BaseEntity] = []
        relationships: list[Relationship] = []

        for index, style_ref in enumerate(figure.styles.refs):
            style_entity = map_style_reference(style_ref, index, context)
            style_entities.append(style_entity)
            relationships.append(
                build_style_reference_relationship(
                    root_entity_id,
                    style_entity.id,
                    relationship_id=context.make_entity_id(
                        "rel", f"figure-references-style-{index}"
                    ),
                )
            )

        return style_entities, relationships


def compile_figure(figure: Figure, *, validate_output: bool = True) -> OntologyGraph:
    """Compile an FSL figure into an ontology graph.

    Convenience wrapper around ``FigureCompiler``.
    """
    return FigureCompiler(validate_output=validate_output).compile(figure)
